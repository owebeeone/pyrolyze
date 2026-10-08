from __future__ import annotations

import gc
from typing import Any, Callable
import weakref

import pytest

from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.async_effect_render import (
    _enable_async_effect_render,
)
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.slot_call_semantics import (
    AsyncEffectHandle,
    UseEffectAsyncRequest,
)


def _root() -> Any:
    root = runtime.RenderContext()
    _enable_async_effect_render(root._state_mgr)
    return root


def _evaluate(root: Any, request: UseEffectAsyncRequest, index: int = 1) -> Any:
    slot = root._ensure_slot(
        runtime.SlotId(runtime.ModuleId("tests.async_effect_faults"), index),
        runtime.SlotCallSlotContext,
    )
    slot.evaluate(lambda: request, (), {})
    return slot


def test_start_failures_drain_without_undoing_publication() -> None:
    root = _root()
    events: list[str] = []
    cause = SystemExit("start failed")
    callbacks: list[Callable[[], None]] = []
    posted: list[Callable[[], None]] = []
    root.set_flush_poster(posted.append)

    def fail(done: Callable[[], None]) -> None:
        callbacks.append(done)
        raise cause

    with pytest.raises(SystemExit) as caught:
        with root.pass_scope():
            _evaluate(root, UseEffectAsyncRequest(fail))
            _evaluate(
                root, UseEffectAsyncRequest(lambda done: events.append("later")), 2
            )
    assert caught.value is cause
    assert events == ["later"]
    assert root._state_mgr._field_only_completion.last.published is True
    callbacks[0]()
    assert posted == []
    with pytest.raises(RuntimeError, match="not ready"):
        with root.pass_scope():
            pass


def test_cancel_failure_does_not_suppress_cleanup_or_other_slots() -> None:
    root = _root()
    events: list[str] = []
    cancel_error = ValueError("cancel failed")
    cleanup_error = SystemExit("cleanup failed")

    class Handle(AsyncEffectHandle):
        def cancel(self) -> None:
            events.append("cancel")
            raise cancel_error

    def cleanup() -> None:
        events.append("cleanup")
        raise cleanup_error

    with root.pass_scope():
        _evaluate(root, UseEffectAsyncRequest(lambda done: Handle(), (1,), cleanup))
    with pytest.raises(BaseExceptionGroup) as caught:
        with root.pass_scope():
            _evaluate(
                root, UseEffectAsyncRequest(lambda done: events.append("replacement"))
            )
            _evaluate(
                root,
                UseEffectAsyncRequest(lambda done: events.append("independent")),
                2,
            )
    assert caught.value.exceptions == (cancel_error, cleanup_error)
    assert events == ["cancel", "cleanup", "independent"]
    assert root._state_mgr._field_only_completion.last.published is True


def test_synchronous_completion_does_not_leave_a_finished_handle_to_cancel() -> None:
    root = _root()
    posted: list[Callable[[], None]] = []
    root.set_flush_poster(posted.append)
    events: list[str] = []

    class Handle(AsyncEffectHandle):
        def cancel(self) -> None:
            events.append("cancel")

    def start(done: Callable[[], None]) -> AsyncEffectHandle:
        done()
        return Handle()

    with root.pass_scope():
        slot = _evaluate(
            root, UseEffectAsyncRequest(start, cleanup=lambda: events.append("cleanup"))
        )
    assert len(posted) == 1
    assert slot.binding.resource.handle is None
    with root.pass_scope():
        slot.deactivate()
    assert events == ["cleanup"]


def test_retained_completion_callback_does_not_keep_graph_alive() -> None:
    root = _root()
    callbacks: list[Callable[[], None]] = []
    events: list[str] = []

    class Handle(AsyncEffectHandle):
        def cancel(self) -> None:
            events.append("cancel")

    def start(done: Callable[[], None]) -> AsyncEffectHandle:
        callbacks.append(done)
        return Handle()

    with root.pass_scope():
        slot = _evaluate(root, UseEffectAsyncRequest(start))
    reference = weakref.ref(root)
    del slot, root
    gc.collect()
    assert reference() is None
    assert events == ["cancel"]
    callbacks[0]()
    assert events == ["cancel"]


def test_start_reentry_is_rejected_and_independent_start_still_runs() -> None:
    root = _root()
    events: list[str] = []

    def start(done: Callable[[], None]) -> None:
        with root.pass_scope():
            events.append("reentered")

    with pytest.raises(RuntimeError, match="completion is in progress"):
        with root.pass_scope():
            _evaluate(root, UseEffectAsyncRequest(start))
            _evaluate(
                root, UseEffectAsyncRequest(lambda done: events.append("later")), 2
            )
    assert events == ["later"]
    assert root._state_mgr._field_only_completion.last.published is True


def test_dependency_comparison_cannot_select_on_replacement_transaction() -> None:
    root = _root()
    manager = root._state_mgr._transaction_manager
    events: list[str] = []
    replacement: Any = None
    with root.pass_scope():
        slot = _evaluate(
            root, UseEffectAsyncRequest(lambda done: events.append("old"), (1,))
        )

    class Dependency:
        def __eq__(self, other: object) -> bool:
            nonlocal replacement
            manager.rollback(PASS_TX_KEY)
            replacement = manager.begin(PASS_TX_KEY)
            return False

    with pytest.raises(BaseException):
        with root.pass_scope():
            _evaluate(
                root,
                UseEffectAsyncRequest(
                    lambda done: events.append("new"), (Dependency(),)
                ),
            )
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    assert events == ["old"]
    assert not slot.binding.resource.is_closed
    manager.rollback(PASS_TX_KEY)
