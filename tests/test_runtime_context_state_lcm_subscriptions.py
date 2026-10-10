from __future__ import annotations

from typing import Any, Callable
import weakref

import pytest

from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted
from pyrolyze.runtime.context_state_lcm import subscription_binding
from pyrolyze.runtime.context_state_lcm.resource_ownership import _ResourceOwner
from pyrolyze.runtime.slot_call_semantics import ExternalStoreRef, UseEffectRequest


def _root() -> Any:
    root = runtime.RenderContext()
    return root


def _evaluate(root: Any, result: Any, index: int = 1) -> Any:
    slot_id = runtime.SlotId(runtime.ModuleId("tests.subscription_faults"), index)
    slot = root._ensure_slot(slot_id, runtime.SlotCallSlotContext)
    slot.evaluate(lambda: result, (), {})
    return slot


def test_private_owners_release_explicit_references_once() -> None:
    root = _root()
    completion = root._field_only_completion
    resource = subscription_binding._StoreSubscription(
        "shared", weakref.ref(root), weakref.ref(completion)
    )
    events: list[str] = []
    resource.unsubscribe = lambda: events.append("unsubscribe")
    first = _ResourceOwner(resource)
    second = _ResourceOwner.retain(resource)
    assert resource.ref_count == 2
    first.release()
    first.release()
    assert resource.ref_count == 1
    assert not resource.is_closed
    second.release()
    assert resource.is_closed
    assert events == ["unsubscribe"]
    assert resource.ref_count == 0


def test_caught_get_failure_discards_subscription_and_allows_retry() -> None:
    root = _root()
    events: list[str] = []
    cause = ValueError("get failed")

    def subscribe(callback: Callable[[], None]) -> Callable[[], None]:
        events.append("subscribe")
        return lambda: events.append("unsubscribe")

    def get() -> int:
        raise cause

    with pytest.raises(RenderAttemptAborted) as caught:
        with root.pass_scope():
            with pytest.raises(ValueError) as inner:
                _evaluate(root, ExternalStoreRef("bad", subscribe, get))
            assert inner.value is cause
    assert caught.value.__cause__ is cause
    assert events == ["subscribe", "unsubscribe"]
    with root.pass_scope():
        slot = _evaluate(root, ExternalStoreRef("good", subscribe, lambda: 2))
    assert slot.binding.exposed_value() == 2


@pytest.mark.parametrize("step", ("subscribe", "get"))
def test_subscription_reentry_cannot_stage_on_replacement_token(step: str) -> None:
    root = _root()
    manager = root._transaction_manager
    events: list[str] = []
    replacement: Any = None

    def replace() -> None:
        nonlocal replacement
        manager.rollback(PASS_TX_KEY)
        replacement = manager.begin(PASS_TX_KEY)

    def subscribe(callback: Callable[[], None]) -> Callable[[], None]:
        events.append("subscribe")
        if step == "subscribe":
            replace()
        return lambda: events.append("unsubscribe")

    def get() -> int:
        events.append("get")
        if step == "get":
            replace()
        return 2

    with pytest.raises(BaseException):
        with root.pass_scope():
            _evaluate(root, ExternalStoreRef("replace", subscribe, get))
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    assert events == (
        ["subscribe", "unsubscribe"]
        if step == "subscribe"
        else ["subscribe", "get", "unsubscribe"]
    )
    assert root.current.children_state == {}
    with pytest.raises(RuntimeError, match="not ready"):
        with root.pass_scope():
            pass
    manager.rollback(PASS_TX_KEY)


@pytest.mark.parametrize("publish", (False, True))
def test_subscription_cleanup_failures_drain_and_quarantine(publish: bool) -> None:
    root = _root()
    events: list[int] = []
    failures = (ValueError("first cleanup"), RuntimeError("second cleanup"))
    slots: list[Any] = []

    def ref(index: int) -> ExternalStoreRef[int]:
        def subscribe(callback: Callable[[], None]) -> Callable[[], None]:
            def unsubscribe() -> None:
                events.append(index)
                raise failures[index - 1]

            return unsubscribe

        return ExternalStoreRef(index, subscribe, lambda: index)

    if publish:
        with root.pass_scope():
            slots = [_evaluate(root, ref(index), index) for index in (1, 2)]
    cause = LookupError("parent failed")
    with pytest.raises(BaseExceptionGroup) as caught:
        with root.pass_scope():
            if publish:
                for index in (1, 2):
                    _evaluate(root, index + 10, index)
            else:
                slots = [_evaluate(root, ref(index), index) for index in (1, 2)]
                raise cause
    errors = caught.value.exceptions
    assert all(error in errors for error in failures)
    if not publish:
        assert cause in errors
    assert events == [1, 2]
    assert root._field_only_completion.last.published is publish
    assert [
        slot.binding.exposed_value() if slot.binding is not None else None
        for slot in slots
    ] == ([11, 12] if publish else [None, None])
    with pytest.raises(RuntimeError, match="not ready"):
        with root.pass_scope():
            pass




def test_failed_cleanup_cannot_reenter_completion() -> None:
    root = _root()
    events: list[str] = []

    def subscribe(callback: Callable[[], None]) -> Callable[[], None]:
        def unsubscribe() -> None:
            events.append("unsubscribe")
            with root.pass_scope():
                events.append("reentered")

        return unsubscribe

    with pytest.raises(BaseExceptionGroup):
        with root.pass_scope():
            _evaluate(root, ExternalStoreRef("reenter", subscribe, lambda: 1))
            raise ValueError("parent failed")
    assert events == ["unsubscribe"]
    assert root.current.children_state == {}


def test_get_and_cleanup_failures_preserve_both_original_errors() -> None:
    root = _root()
    cause = ValueError("get failed")
    cleanup = SystemExit("cleanup failed")

    def subscribe(callback: Callable[[], None]) -> Callable[[], None]:
        def unsubscribe() -> None:
            raise cleanup

        return unsubscribe

    def get() -> int:
        raise cause

    with pytest.raises(BaseExceptionGroup) as caught:
        with root.pass_scope():
            _evaluate(root, ExternalStoreRef("both", subscribe, get))
    assert caught.value.exceptions == (cause, cleanup)


def test_identity_comparison_reentry_prevents_new_subscription() -> None:
    root = _root()
    manager = root._transaction_manager
    events: list[str] = []
    replacement: Any = None
    with root.pass_scope():
        slot = _evaluate(
            root, ExternalStoreRef("old", lambda callback: lambda: None, lambda: 1)
        )

    class Identity:
        def __eq__(self, other: object) -> bool:
            nonlocal replacement
            manager.rollback(PASS_TX_KEY)
            replacement = manager.begin(PASS_TX_KEY)
            return False

    with pytest.raises(BaseException):
        with root.pass_scope():
            _evaluate(
                root,
                ExternalStoreRef(
                    Identity(), lambda callback: events.append("subscribe"), lambda: 2
                ),
            )
    assert events == []
    assert slot.binding.exposed_value() == 1
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    manager.rollback(PASS_TX_KEY)


def test_value_comparison_reentry_discards_unstaged_subscription() -> None:
    root = _root()
    manager = root._transaction_manager
    events: list[str] = []
    replacement: Any = None
    with root.pass_scope():
        slot = _evaluate(root, 1)

    class Value:
        def __eq__(self, other: object) -> bool:
            nonlocal replacement
            manager.rollback(PASS_TX_KEY)
            replacement = manager.begin(PASS_TX_KEY)
            return False

    def subscribe(callback: Callable[[], None]) -> Callable[[], None]:
        events.append("subscribe")
        return lambda: events.append("unsubscribe")

    with pytest.raises(BaseException):
        with root.pass_scope():
            _evaluate(root, ExternalStoreRef("value-reentry", subscribe, Value))
    assert events == ["subscribe", "unsubscribe"]
    assert slot.binding.exposed_value() == 1
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    manager.rollback(PASS_TX_KEY)
