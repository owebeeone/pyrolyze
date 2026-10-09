"""Observe common slot construction and post-construction graph registration."""

from __future__ import annotations

import json
from typing import Any

from pyrolyze.runtime.context_state_lcm.component_call_slot_context import ComponentCallSlotContextStateMgr
from pyrolyze.runtime.context_state_lcm.container_slot_context import ContainerSlotContextStateMgr
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.event_handler_slot_context import EventHandlerSlotContextStateMgr
from pyrolyze.runtime.context_state_lcm.leaf_slot_context import LeafSlotContextStateMgr
from pyrolyze.runtime.context_state_lcm.lifecycle_adapter import TransactionManager
from pyrolyze.runtime.context_state_lcm.rerunnable_slot_context import RerunnableSlotContextStateMgr
from pyrolyze.runtime.context_state_lcm.slot_context import SlotContextStateMgr
from pyrolyze.runtime.context_state_lcm.slot_expr_slot_context import SlotExprSlotContextStateMgr
from pyrolyze.runtime.slot_kinds import ContextKind


class Owner:
    _context_kind = ContextKind.SLOT
    _generation_tracker_key_const = object()
    _pass_scope_handle_cls = object


class Graph:
    def __init__(self, ready_field: str) -> None:
        self._transaction_manager = TransactionManager(tx_keys=(PASS_TX_KEY,))
        self.ready_field = ready_field
        self.events: list[str] = []
        self.slots: dict[str, Any] = {}
        self.children: dict[str, Any] = {}
        self.complete_at_registration = False

    def register_slot_state_mgr(self, state: Any) -> None:
        self.complete_at_registration = hasattr(state, self.ready_field)
        self.events.append("root")
        self.slots[state.current_slot_id()] = state

    def register_child_state_mgr(self, slot_id: str, state: Any) -> None:
        self.events.append("parent")
        self.children[slot_id] = state


def characterize() -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    cases = (
        (SlotContextStateMgr, "_site_metadata"),
        (RerunnableSlotContextStateMgr, "children_state"),
        (EventHandlerSlotContextStateMgr, "_dispatch"),
        (LeafSlotContextStateMgr, "_last_kwargs"),
        (ContainerSlotContextStateMgr, "_expects_native_root"),
        (SlotExprSlotContextStateMgr, "_call_site_context_manager"),
        (ComponentCallSlotContextStateMgr, "_call_state"),
    )
    common_names = ("_parent_state_mgr", "_slot_id", "_legacy_invoke_dirty", "_legacy_seen_in_pass", "_site_metadata")
    input_names = ("parent_state_mgr", "slot_id", "invoke_dirty", "seen_in_pass")
    for state_type, ready_field in cases:
        graph = Graph(ready_field)
        owner = Owner()
        state = state_type.create(
            owner=owner,
            render_context_state_mgr=graph,
            parent_state_mgr=graph,
            slot_id="slot",
            invoke_dirty=False,
            seen_in_pass=True,
        )
        field_names = state.__yidl_lifecycle_definition__["class"]["lifecycle_field_names"]
        field_counts = {
            name: sum(fact["field_name"] == name for fact in state.__yidl_lifecycle_definition__["fields"])
            for name in common_names
        }
        detached_graph = Graph(ready_field)
        detached = state_type(
            owner=Owner(),
            render_context_state_mgr=detached_graph,
            parent_state_mgr=detached_graph,
            slot_id="detached",
            invoke_dirty=True,
            seen_in_pass=False,
            transaction_manager=detached_graph._transaction_manager,
        )
        identity_writes: dict[str, bool] = {}
        for name in ("_parent_state_mgr", "_slot_id", "_render_context_state_mgr"):
            try:
                setattr(detached, name, getattr(detached, name))
            except AttributeError:
                identity_writes[name] = False
            else:
                identity_writes[name] = True
        result.append({
            "type": state_type.__name__,
            "registration_order": graph.events,
            "complete_at_registration": graph.complete_at_registration,
            "shared_manager": state._y_get_transaction_manager() is graph._transaction_manager,
            "registered_identity": graph.slots["slot"] is graph.children["slot"] is state,
            "owner_and_inputs": state.owner is owner and state._parent_state_mgr is graph and state._slot_id == "slot",
            "flags": [state._invoke_dirty, state._seen_in_pass],
            "common_field_counts": field_counts,
            "inputs_not_stored": all(name not in field_names for name in input_names),
            "identity_writes": identity_writes,
            "direct_constructor_detached": not detached_graph.events and detached._slot_id == "detached",
        })
    return result


if __name__ == "__main__":
    print(json.dumps(characterize(), indent=2, sort_keys=True))
