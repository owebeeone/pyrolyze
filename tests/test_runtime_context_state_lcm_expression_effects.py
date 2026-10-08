from __future__ import annotations

from typing import Any, Callable

import pytest

from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.effect_expr_render import (
    _enable_effect_expr_render,
)
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted
from pyrolyze.runtime.dirt import DM
from pyrolyze.runtime.slot_call_semantics import UseEffectAsyncRequest, UseEffectRequest
from pyrolyze.runtime.slot_expr import (
    LiteralFunctionProvider,
    slot_params,
    slot_params_dirt,
)


def _root() -> Any:
    root = runtime.RenderContext()
    _enable_effect_expr_render(root._state_mgr)
    return root


def _evaluate(root: Any, request: Any, index: int = 1) -> Any:
    module = runtime.ModuleId("tests.expression_effect_faults")
    expr = root.slot_expr(
        runtime.SlotId(module, index), lambda e: e.eval(), lambda e: e.dirty()
    )
    expr.slot_call(
        "e",
        LiteralFunctionProvider(lambda: request),
        lambda: slot_params(),
        lambda: slot_params_dirt(),
        slot_id=runtime.SlotId(module, index + 10),
    )
    expr.apply_dirt_sink(DM()).evaluate()
    return expr.call_site_context_manager


def test_setup_failures_drain_and_preserve_published_values() -> None:
    root = _root()
    events: list[int] = []
    failures = (ValueError("first"), SystemExit("second"))

    def setup(index: int) -> Callable[[], None]:
        def effect() -> None:
            events.append(index)
            if index < 3:
                raise failures[index - 1]

        return effect

    with pytest.raises(BaseExceptionGroup) as caught:
        with root.pass_scope():
            managers = [
                _evaluate(root, UseEffectRequest(setup(index)), index)
                for index in (1, 2, 3)
            ]
    assert caught.value.exceptions == failures
    assert events == [1, 2, 3]
    assert all(
        manager.iter_current()[0].binding.binding.resource.started
        for manager in managers
    )
    assert root._state_mgr._field_only_completion.last.published is True
    with pytest.raises(RuntimeError, match="not ready"):
        with root.pass_scope():
            pass


def test_failed_cleanup_blocks_only_its_replacement() -> None:
    root = _root()
    events: list[str] = []
    error = ValueError("cleanup")

    def initial() -> Callable[[], None]:
        def cleanup() -> None:
            events.append("cleanup")
            raise error

        return cleanup

    with root.pass_scope():
        manager = _evaluate(root, UseEffectRequest(initial, (1,)))
    with pytest.raises(ValueError) as caught:
        with root.pass_scope():
            _evaluate(
                root, UseEffectRequest(lambda: events.append("replacement"), (2,))
            )
            _evaluate(root, UseEffectRequest(lambda: events.append("independent")), 2)
    assert caught.value is error
    assert events == ["cleanup", "independent"]
    assert manager.iter_current()[0].binding.binding.resource.started is False
    assert root._state_mgr._field_only_completion.last.published is True


def test_invalid_cleanup_is_reported_after_publication() -> None:
    root = _root()
    with pytest.raises(TypeError, match="cleanup callable"):
        with root.pass_scope():
            manager = _evaluate(root, UseEffectRequest(lambda: 1))
    assert manager.iter_current()[0].binding.binding.resource.started
    assert root._state_mgr._field_only_completion.last.published is True


def test_setup_reentry_does_not_suppress_later_effects() -> None:
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


def test_dependency_comparison_cannot_stage_into_replacement_transaction() -> None:
    root = _root()
    manager = root._state_mgr._transaction_manager
    events: list[str] = []
    replacement: Any = None
    with root.pass_scope():
        collection = _evaluate(
            root, UseEffectRequest(lambda: events.append("old"), (1,))
        )
    accepted = collection.iter_current()[0]

    class Dependency:
        def __eq__(self, other: object) -> bool:
            nonlocal replacement
            manager.rollback(PASS_TX_KEY)
            replacement = manager.begin(PASS_TX_KEY)
            return False

    with pytest.raises((RuntimeError, BaseExceptionGroup)):
        with root.pass_scope():
            _evaluate(
                root, UseEffectRequest(lambda: events.append("new"), (Dependency(),))
            )
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    assert collection.iter_current()[0] is accepted
    assert events == ["old"]
    manager.rollback(PASS_TX_KEY)


def test_caught_expression_failure_prevents_candidate_setup() -> None:
    root = _root()
    events: list[str] = []
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            _evaluate(root, UseEffectRequest(lambda: events.append("setup")))
            try:
                _evaluate(
                    root, UseEffectAsyncRequest(lambda done: events.append("async")), 2
                )
            except RuntimeError:
                pass
    assert events == []
