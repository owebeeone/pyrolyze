from __future__ import annotations

from typing import Any
import gc
import weakref

import pytest

from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.subscription_expr_render import (
    _enable_subscription_expr_render,
)
from pyrolyze.runtime.slot_call_semantics import ExternalStoreRef, UseEffectRequest
from tests.test_runtime_context_state_lcm_expression_render import _expr
from tests.slot_expr_test_utils import eval_single_slot_expr


def _root() -> Any:
    root = runtime.RenderContext()
    _enable_subscription_expr_render(root._state_mgr)
    return root


@pytest.mark.parametrize("change", ("argument", "keyword", "callable"))
def test_pending_refresh_does_not_mask_changed_invocation(change: str) -> None:
    root = _root()
    notifications: list[Any] = []
    events: list[tuple[str, int]] = []
    slot_id = runtime.SlotId(runtime.ModuleId("refresh-input-collision"), 1)

    def first(value: int = 1) -> ExternalStoreRef[int]:
        events.append(("first", value))

        def subscribe(callback: Any) -> Any:
            notifications.append(callback)
            return lambda: notifications.remove(callback)

        return ExternalStoreRef(("first", value), subscribe, lambda: value)

    def second(value: int = 1) -> ExternalStoreRef[int]:
        events.append(("second", value))
        return ExternalStoreRef("second", lambda callback: lambda: None, lambda: 9)

    with root.pass_scope():
        if change == "argument":
            _, value = eval_single_slot_expr(root, runtime.dirtyof(), slot_id, first, 1)
        elif change == "keyword":
            _, value = eval_single_slot_expr(root, runtime.dirtyof(), slot_id, first, value=1)
        else:
            _, value = eval_single_slot_expr(root, runtime.dirtyof(), slot_id, first)
        assert value == 1
    notifications[0]()
    with root.pass_scope():
        if change == "argument":
            _, value = eval_single_slot_expr(
                root, runtime.dirtyof(), slot_id, first, 2, args_dirty=(True,)
            )
        elif change == "keyword":
            _, value = eval_single_slot_expr(
                root, runtime.dirtyof(), slot_id, first,
                value=2, kwargs_dirty={"value": True},
            )
        else:
            _, value = eval_single_slot_expr(root, runtime.dirtyof(), slot_id, second)
        assert value == (9 if change == "callable" else 2)
    assert events == [("first", 1), ("second", 1) if change == "callable" else ("first", 2)]
    assert len(notifications) == (0 if change == "callable" else 1)


def test_failed_store_read_unsubscribes_with_retained_traceback_and_allows_retry() -> (
    None
):
    root = _root()
    events: list[str] = []
    error = ValueError("read")

    def subscribe(callback: Any) -> Any:
        events.append("subscribe")
        return lambda: events.append("unsubscribe")

    def get() -> int:
        raise error

    with pytest.raises(ValueError) as caught:
        with root.pass_scope():
            _expr(root, lambda: ExternalStoreRef("bad", subscribe, get)).evaluate()
    assert caught.value is error
    assert events == ["subscribe", "unsubscribe"]
    with root.pass_scope():
        assert _expr(root, lambda: 9).evaluate() == 9


def test_store_read_replacing_token_cannot_stage_into_replacement() -> None:
    root = _root()
    manager = root._state_mgr._transaction_manager
    events: list[str] = []
    replacement: Any = None

    def get() -> int:
        nonlocal replacement
        manager.rollback(PASS_TX_KEY)
        replacement = manager.begin(PASS_TX_KEY)
        return 7

    with pytest.raises((RuntimeError, BaseExceptionGroup)):
        with root.pass_scope():
            expression = _expr(
                root,
                lambda: ExternalStoreRef(
                    "stale", lambda callback: lambda: events.append("unsubscribe"), get
                ),
            )
            expression.evaluate()
    assert events == ["unsubscribe"]
    assert expression.call_site_context_manager.iter_current() == ()
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    manager.rollback(PASS_TX_KEY)


def test_effect_expressions_remain_rejected_before_setup() -> None:
    root = _root()
    events: list[str] = []
    with pytest.raises(RuntimeError, match="resource expression results"):
        with root.pass_scope():
            _expr(
                root, lambda: UseEffectRequest(lambda: events.append("setup"), ())
            ).evaluate()
    assert events == []


def test_unsubscribe_failure_preserves_publication_and_quarantines_reuse() -> None:
    root = _root()
    error = ValueError("unsubscribe")

    def cleanup() -> None:
        raise error

    with root.pass_scope():
        expression = _expr(
            root, lambda: ExternalStoreRef("old", lambda callback: cleanup, lambda: 1)
        )
        expression.evaluate()
    with pytest.raises(ValueError) as caught:
        with root.pass_scope():
            pass
    assert caught.value is error
    assert expression.call_site_context_manager.iter_current() == ()
    completion = root._state_mgr._field_only_completion
    assert completion.last.published is True
    assert completion._cleanup_failure is error


def test_live_store_notification_does_not_retain_render_graph() -> None:
    callbacks: list[Any] = []

    def subscribe(callback: Any) -> Any:
        callbacks.append(callback)
        return lambda: callbacks.remove(callback)

    def render() -> Any:
        root = _root()
        with root.pass_scope():
            _expr(
                root, lambda: ExternalStoreRef("weak", subscribe, lambda: 1)
            ).evaluate()
        return weakref.ref(root)

    root_ref = render()
    gc.collect()
    assert root_ref() is None
    assert callbacks == []


def test_cleanup_reentry_is_rejected_before_new_expression_selection() -> None:
    root = _root()
    errors: list[BaseException] = []

    def cleanup() -> None:
        try:
            _expr(root, lambda: 8).evaluate()
        except RuntimeError as error:
            errors.append(error)

    with root.pass_scope():
        _expr(
            root,
            lambda: ExternalStoreRef("reentry", lambda callback: cleanup, lambda: 1),
        ).evaluate()
    with root.pass_scope():
        pass
    assert len(errors) == 1
