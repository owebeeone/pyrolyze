from __future__ import annotations

from typing import Any

import pytest

from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.lifecycle_adapter import TransactionManager, const, managed_context
from pyrolyze.runtime.context_state_lcm.rerunnable_slot_context import RerunnableSlotContextStateMgr
from pyrolyze.runtime.context_state_lcm.slot_context import SlotContextStateMgr
from pyrolyze.runtime.context_state_lcm.slot_expr_slot_context import SlotExprSlotContextStateMgr
from pyrolyze.runtime.slot_kinds import ContextKind


class Owner:
    _context_kind = ContextKind.SLOT
    _generation_tracker_key_const = object()
    _pass_scope_handle_cls = object


class Graph:
    def __init__(self) -> None:
        self._transaction_manager = TransactionManager(tx_keys=(PASS_TX_KEY,))
        self.registered: list[Any] = []

    def register_slot_state_mgr(self, state: Any) -> None:
        self.registered.append(state)

    def register_child_state_mgr(self, slot_id: object, state: Any) -> None:
        self.registered.append(state)


class FailingOrdinarySlot(SlotContextStateMgr):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        raise ValueError("derived initialization failed")


class FailingRerunnableSlot(RerunnableSlotContextStateMgr):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        raise ValueError("derived initialization failed")


def _fail_factory(self: SlotExprSlotContextStateMgr) -> None:
    del self
    raise ValueError("derived initialization failed")


@managed_context
class FailingDecoratedSlot(SlotExprSlotContextStateMgr):
    _late_failure: None = const(init=False, default_factory=_fail_factory, allow_self_factory=True)


@pytest.mark.parametrize("state_type", (FailingOrdinarySlot, FailingRerunnableSlot, FailingDecoratedSlot))
def test_failed_derived_initialization_never_registers(state_type: type[Any]) -> None:
    graph = Graph()
    with pytest.raises(ValueError, match="derived initialization failed"):
        state_type.create(
            owner=Owner(),
            render_context_state_mgr=graph,
            parent_state_mgr=graph,
            slot_id="failed",
            invoke_dirty=False,
            seen_in_pass=False,
        )
    assert graph.registered == []
