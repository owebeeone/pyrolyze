from __future__ import annotations

import gc
from typing import Any, Callable
import weakref

import pytest

from pyrolyze.api import advertise_mount
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.async_effect_expr_render import (
    _enable_async_effect_expr_render,
)
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.slot_call_semantics import (
    AsyncEffectHandle,
    UseEffectAsyncRequest,
)
from tests.test_runtime_context_state_lcm_expression_effects import _evaluate


def _root() -> Any:
    root = runtime.RenderContext()
    _enable_async_effect_expr_render(root._state_mgr)
    return root


def test_start_failure_fences_callback_and_drains_independent_start() -> None:
    root = _root()
    error = SystemExit("start")
    events: list[str] = []
    callbacks: list[Callable[[], None]] = []
    posted: list[Callable[[], None]] = []
    root.set_flush_poster(posted.append)

    def start(done: Callable[[], None]) -> None:
        callbacks.append(done)
        raise error

    with pytest.raises(SystemExit) as caught:
        with root.pass_scope():
            _evaluate(root, UseEffectAsyncRequest(start))
            _evaluate(
                root, UseEffectAsyncRequest(lambda done: events.append("later")), 2
            )
    assert caught.value is error
    assert events == ["later"]
    assert root._state_mgr._field_only_completion.last.published is True
    callbacks[0]()
    assert posted == []
    with pytest.raises(RuntimeError, match="not ready"):
        with root.pass_scope():
            pass


def test_cancel_failure_drains_cleanup_and_other_expression_delivery() -> None:
    root = _root()
    events: list[str] = []
    cancel_error, cleanup_error = ValueError("cancel"), SystemExit("cleanup")

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
                root,
                UseEffectAsyncRequest(lambda done: events.append("replacement"), (2,)),
            )
            _evaluate(
                root,
                UseEffectAsyncRequest(lambda done: events.append("independent")),
                2,
            )
    assert caught.value.exceptions == (cancel_error, cleanup_error)
    assert events == ["cancel", "cleanup", "independent"]
    assert root._state_mgr._field_only_completion.last.published is True


def test_completion_during_start_does_not_resurrect_finished_handle() -> None:
    root = _root()
    events: list[str] = []

    class Handle(AsyncEffectHandle):
        def cancel(self) -> None:
            events.append("cancel")

    def start(done: Callable[[], None]) -> AsyncEffectHandle:
        done()
        return Handle()

    with root.pass_scope():
        manager = _evaluate(
            root, UseEffectAsyncRequest(start, cleanup=lambda: events.append("cleanup"))
        )
    assert manager.iter_current()[0].binding.binding.resource.handle is None
    with root.pass_scope():
        pass
    assert events == ["cleanup"]


def test_retained_callback_does_not_retain_expression_graph() -> None:
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
        _evaluate(root, UseEffectAsyncRequest(start))
    reference = weakref.ref(root)
    del root
    gc.collect()
    assert reference() is None
    assert events == ["cancel"]
    callbacks[0]()
    assert events == ["cancel"]


def test_start_reentry_does_not_suppress_independent_operation() -> None:
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


def test_dependency_comparison_cannot_stage_into_replacement() -> None:
    root = _root()
    manager = root._state_mgr._transaction_manager
    events: list[str] = []
    replacement: Any = None
    with root.pass_scope():
        collection = _evaluate(
            root, UseEffectAsyncRequest(lambda done: events.append("old"), (1,))
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
                root,
                UseEffectAsyncRequest(
                    lambda done: events.append("new"), (Dependency(),)
                ),
            )
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    assert collection.iter_current()[0] is accepted
    assert events == ["old"]
    manager.rollback(PASS_TX_KEY)


def test_mount_expression_is_rejected_before_advertisement_publication() -> None:
    root = _root()
    with pytest.raises(RuntimeError, match="resource expression results"):
        with root.pass_scope():
            _evaluate(root, advertise_mount("not-admitted"))
    assert root.debug_mount_advertisements() == ()
