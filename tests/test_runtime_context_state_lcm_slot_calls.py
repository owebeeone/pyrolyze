from __future__ import annotations

from contextlib import nullcontext
from typing import Any

import pytest

from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted
from pyrolyze.runtime.slot_call_semantics import (
    ExternalStoreRef,
    UseEffectAsyncRequest,
    UseEffectRequest,
    SlotValueBinding,
)
from pyrolyze.api import PyrolyzeMountAdvertisementRequest


def _root_and_slot() -> tuple[Any, Any]:
    root = runtime.RenderContext()
    with root.pass_scope():
        slot = root._ensure_slot(_slot_id(), runtime.SlotCallSlotContext)
        slot.evaluate(lambda value: value, (1,), {})
    return root, slot


def _slot_id() -> Any:
    return runtime.SlotId(runtime.ModuleId("tests.slot_call_faults"), 1)




@pytest.mark.parametrize("parent_fails", (False, True))
def test_private_binding_uses_the_handler_approved_by_admission(
    parent_fails: bool,
) -> None:
    root, slot = _root_and_slot()
    accepted = slot.binding
    events: list[str] = []

    class Result:
        identity = object()
        class_reads = 0

        @property
        def __class__(self) -> type[Any]:
            self.class_reads += 1
            # One handler-selection pass sees a plain value; a second sees a
            # subscription. Binding must not repeat admission's recognition.
            return type(self) if self.class_reads <= 8 else ExternalStoreRef

        def subscribe(self, callback: Any) -> Any:
            events.append("subscribe")
            return lambda: events.append("unsubscribe")

        def get(self) -> int:
            events.append("get")
            return 42

    value = Result()
    expectation = (
        pytest.raises(ValueError, match="parent failed")
        if parent_fails
        else nullcontext()
    )
    with expectation:
        with root.pass_scope():
            root._ensure_slot(_slot_id(), runtime.SlotCallSlotContext)
            slot.evaluate(lambda: value, (), {})
            if parent_fails:
                raise ValueError("parent failed")
    assert events == []
    assert type(slot.binding) is SlotValueBinding
    if parent_fails:
        assert slot.binding is accepted
        assert slot.binding.exposed_value() == 1
    else:
        assert slot.binding.exposed_value() is value
    assert root._field_only_completion.last.reuse_ready


@pytest.mark.parametrize(
    "attack", ("preparation", "equality", "callable", "projection")
)
def test_slot_call_reentry_cannot_write_into_replacement_transaction(
    attack: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, slot = _root_and_slot()
    state = slot
    manager = state._transaction_manager
    replacement: Any = None
    accepted = slot.binding
    entered: list[str] = []

    def replace_token() -> None:
        nonlocal replacement
        manager.rollback(PASS_TX_KEY)
        replacement = manager.begin(PASS_TX_KEY)

    class Payload:
        def __eq__(self, other: object) -> bool:
            replace_token()
            return False

    class Keywords(dict[str, Any]):
        def items(self) -> Any:
            replace_token()
            return super().items()

    def source(value: Any) -> int:
        entered.append("call")
        if attack == "callable":
            replace_token()
        return 2

    if attack == "equality":
        with root.pass_scope():
            root._ensure_slot(_slot_id(), runtime.SlotCallSlotContext)
            slot.evaluate(source, (1,), {})
        # The same callable and argument shape force argument equality next.
    if attack == "projection":

        def project(self: Any, dirty: bool, shape: object | None) -> bool:
            replace_token()
            return dirty

        monkeypatch.setattr(type(state), "project_dirty_state", project)
    prior = state.current._invocation
    with pytest.raises(RuntimeError, match="missing or replaced"):
        with root.pass_scope():
            root._ensure_slot(_slot_id(), runtime.SlotCallSlotContext)
            slot.evaluate(
                source,
                (Payload(),) if attack == "equality" else (2,),
                Keywords() if attack == "preparation" else {},
            )
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    assert state.current._invocation is prior
    assert state._invocation is prior
    assert not root._field_only_completion.last.reuse_ready
    if attack == "preparation":
        assert entered == []
    if attack == "equality":
        assert entered == ["call"]
    else:
        assert accepted.exposed_value() == 1
    manager.rollback(PASS_TX_KEY)


def test_caught_keyword_failure_aborts_original_slot_call_attempt() -> None:
    root, slot = _root_and_slot()
    accepted = slot.binding
    failure = ValueError("slot-call keyword preparation failed")

    class Keywords(dict[str, Any]):
        def items(self) -> Any:
            raise failure

    with pytest.raises(RenderAttemptAborted) as caught:
        with root.pass_scope():
            root._ensure_slot(_slot_id(), runtime.SlotCallSlotContext)
            with pytest.raises(ValueError) as inner:
                slot.evaluate(lambda: 2, (), Keywords())
            assert inner.value is failure
    assert caught.value.__cause__ is failure
    assert slot.binding is accepted
    assert root._field_only_completion.last.reuse_ready
