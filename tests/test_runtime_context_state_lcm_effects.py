from __future__ import annotations

from typing import Any, Callable

import pytest

from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.effect_render import _enable_effect_render
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted
from pyrolyze.runtime.slot_call_semantics import UseEffectAsyncRequest, UseEffectRequest


def _root() -> Any:
    root = runtime.RenderContext()
    _enable_effect_render(root._state_mgr)
    return root


def _evaluate(root: Any, request: Any, index: int = 1) -> Any:
    slot = root._ensure_slot(
        runtime.SlotId(runtime.ModuleId("tests.effect_faults"), index),
        runtime.SlotCallSlotContext,
    )
    slot.evaluate(lambda: request, (), {})
    return slot


def test_setup_failures_drain_and_keep_actual_publication() -> None:
    root = _root()
    events: list[int] = []
    failures = (ValueError("first"), SystemExit("second"))

    def effect(index: int) -> Callable[[], None]:
        def setup() -> None:
            events.append(index)
            if index < 3:
                raise failures[index - 1]

        return setup

    with pytest.raises(BaseExceptionGroup) as caught:
        with root.pass_scope():
            slots = [
                _evaluate(root, UseEffectRequest(effect(index)), index)
                for index in (1, 2, 3)
            ]
    assert caught.value.exceptions == failures
    assert events == [1, 2, 3]
    assert all(slot.binding.resource.started for slot in slots)
    assert root._state_mgr._field_only_completion.last.published is True
    with pytest.raises(RuntimeError, match="not ready"):
        with root.pass_scope():
            pass


def test_failed_cleanup_skips_its_replacement_but_not_independent_effects() -> None:
    root = _root()
    events: list[str] = []
    failure = ValueError("cleanup failed")

    def initial() -> Callable[[], None]:
        def cleanup() -> None:
            events.append("cleanup")
            raise failure

        return cleanup

    with root.pass_scope():
        old = _evaluate(root, UseEffectRequest(initial, ("old",)))
    with pytest.raises(ValueError) as caught:
        with root.pass_scope():
            _evaluate(root, UseEffectRequest(lambda: events.append("replacement")))
            _evaluate(root, UseEffectRequest(lambda: events.append("independent")), 2)
    assert caught.value is failure
    assert events == ["cleanup", "independent"]
    assert old.binding.resource.started is False
    assert root._state_mgr._field_only_completion.last.published is True


def test_invalid_cleanup_result_is_reported_after_publication() -> None:
    root = _root()
    with pytest.raises(TypeError, match="cleanup callable"):
        with root.pass_scope():
            slot = _evaluate(root, UseEffectRequest(lambda: 1))
    assert slot.binding.resource.started
    assert root._state_mgr._field_only_completion.last.published is True


def test_dependency_comparison_cannot_write_to_replacement_transaction() -> None:
    root = _root()
    manager = root._state_mgr._transaction_manager
    events: list[str] = []
    replacement: Any = None
    with root.pass_scope():
        slot = _evaluate(root, UseEffectRequest(lambda: events.append("old"), (1,)))

    class Dependency:
        def __eq__(self, other: object) -> bool:
            nonlocal replacement
            manager.rollback(PASS_TX_KEY)
            replacement = manager.begin(PASS_TX_KEY)
            return False

    with pytest.raises(BaseException):
        with root.pass_scope():
            _evaluate(
                root, UseEffectRequest(lambda: events.append("new"), (Dependency(),))
            )
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    assert events == ["old"]
    assert slot.binding.resource.started
    manager.rollback(PASS_TX_KEY)


def test_setup_reentry_is_rejected_without_suppressing_later_effects() -> None:
    root = _root()
    events: list[str] = []

    def reenter() -> None:
        with root.pass_scope():
            events.append("reentered")

    with pytest.raises(RuntimeError, match="completion is in progress"):
        with root.pass_scope():
            _evaluate(root, UseEffectRequest(reenter))
            _evaluate(root, UseEffectRequest(lambda: events.append("later")), 2)
    assert events == ["later"]
    assert root._state_mgr._field_only_completion.last.published is True


def test_caught_child_failure_does_not_deliver_provisional_effect() -> None:
    root = _root()
    events: list[str] = []
    cause = ValueError("child failed")
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            slot = _evaluate(root, UseEffectRequest(lambda: events.append("setup")))
            try:
                with slot.pass_scope():
                    raise cause
            except ValueError:
                pass
    assert events == []
    assert slot.binding is None


def test_effect_gate_still_rejects_async_before_start() -> None:
    root = _root()
    events: list[str] = []
    with pytest.raises(RuntimeError, match="not admitted"):
        with root.pass_scope():
            _evaluate(root, UseEffectAsyncRequest(lambda done: events.append("async")))
    assert events == []
