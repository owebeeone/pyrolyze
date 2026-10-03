"""Observe I3a migration gates, not acceptance of the existing behavior."""

from __future__ import annotations

import json
import os
from typing import Any

from pyrolyze.api import UIElement
from pyrolyze.runtime import context as runtime


def _emit(context: Any, value: str, fail: bool = False) -> None:
    context.call_native(UIElement, kind="text", props={"value": value}, children=())
    if fail:
        raise ValueError("leaf failed after emission")


def _ui(root: Any, slot_id: Any = None) -> list[str]:
    return [element.props["value"] for element in root.debug_ui(slot_id)]


def _root_and_leaf() -> tuple[Any, Any, Any]:
    root = runtime.RenderContext()
    slot_id = runtime.SlotId(runtime.ModuleId("tests.i3a_preflight"), 1)
    with root.pass_scope():
        leaf = root._ensure_slot(slot_id, runtime.LeafSlotContext)
        leaf.invoke_native(_emit, ("old",), {}, context_param="context")
    return root, leaf, slot_id


def _caught_leaf_failure() -> dict[str, Any]:
    root, leaf, slot_id = _root_and_leaf()
    result: dict[str, Any] = {
        "before": {"root": _ui(root), "leaf": _ui(root, slot_id)},
    }
    with root.pass_scope():
        leaf = root._ensure_slot(slot_id, runtime.LeafSlotContext)
        _emit(root, "parent-candidate")
        try:
            leaf.invoke_native(_emit, ("failed", True), {}, context_param="context")
        except ValueError as exc:
            result["caught"] = str(exc)
        result["after_catch"] = {"root": _ui(root), "leaf": _ui(root, slot_id)}
        if hasattr(leaf, "_state_mgr"):
            from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY

            state = leaf._state_mgr
            manager = root._state_mgr._transaction_manager
            result["lifecycle_after_catch"] = {
                "leaf_current": [item.props["value"] for item in state.current.ui_state],
                "root_current": [
                    item.props["value"] for item in root._state_mgr.current.ui_state
                ],
                "same_manager": state._transaction_manager is manager,
                "transaction_active": (
                    manager.active_transaction_for(PASS_TX_KEY) is not None
                ),
                "leaf_started_transaction": state._pass_started_tx,
            }
    result["after_parent_success"] = {"root": _ui(root), "leaf": _ui(root, slot_id)}
    return result


def _outside_pass_invalidation() -> dict[str, Any]:
    root, leaf, _ = _root_and_leaf()
    result: dict[str, Any] = {"initial_dirty": leaf.invoke_dirty}
    leaf.invoke_dirty = True
    result["after_owner_setter"] = leaf.invoke_dirty
    leaf.invoke_dirty = False
    root._queue_invalidation_from(leaf)
    result["after_queue_invalidation"] = leaf.invoke_dirty
    result["queued_boundaries"] = len(root.debug_pending_boundaries())
    if hasattr(leaf, "_state_mgr"):
        from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY

        leaf.site_metadata = ("outside-pass",)
        result["metadata_after_outside_setter"] = list(leaf.site_metadata)
        result["transaction_active"] = (
            root._state_mgr._transaction_manager.active_transaction_for(PASS_TX_KEY)
            is not None
        )
    return result


def _borrowed_scope_entry() -> dict[str, Any]:
    from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY

    root = runtime.RenderContext()
    state = root._state_mgr
    manager = state._transaction_manager
    manager.begin(PASS_TX_KEY)
    result: dict[str, Any] = {"reports_active_before_local_entry": state.is_scope_active()}
    state.own_ui_state = (UIElement(kind="text", props={"value": "stale"}, children=()),)
    with root.pass_scope():
        result["own_ui_inside_scope"] = [item.props["value"] for item in state.own_ui_state]
    result["transaction_active_after_scope"] = (
        manager.active_transaction_for(PASS_TX_KEY) is not None
    )
    manager.rollback(PASS_TX_KEY)
    return result


def _managed_write_permissions() -> dict[str, Any]:
    from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
    from yidl_lifecycle.lifecycle import lifecycle, managed
    from yidl_lifecycle.transaction_yidl import TransactionManager

    @lifecycle
    class CandidateFields:
        _invoke_dirty: bool = managed(default=False, tx_key=PASS_TX_KEY)
        _site_metadata: tuple[str, ...] = managed(default_factory=tuple, tx_key=PASS_TX_KEY)

    manager = TransactionManager(tx_keys=(PASS_TX_KEY,))
    candidate = CandidateFields(transaction_manager=manager)
    result: dict[str, Any] = {}
    for name, value in (("_invoke_dirty", True), ("_site_metadata", ("outside-pass",))):
        try:
            setattr(candidate, name, value)
        except RuntimeError as exc:
            result[name] = {"error_type": type(exc).__name__, "message": str(exc)}
        else:
            result[name] = {"error_type": None}
    result["current_after_rejected_writes"] = {
        "dirty": candidate.current._invoke_dirty,
        "metadata": list(candidate.current._site_metadata),
    }
    return result


def characterize() -> dict[str, Any]:
    result = {
        "selector": os.environ["PYROLYZE_CONTEXT_IMPL"],
        "caught_leaf_failure": _caught_leaf_failure(),
        "outside_pass_invalidation": _outside_pass_invalidation(),
    }
    if os.environ["PYROLYZE_CONTEXT_IMPL"] == "bare_refactor_lcm":
        result["borrowed_scope_entry"] = _borrowed_scope_entry()
        result["managed_write_permissions"] = _managed_write_permissions()
    return result


if __name__ == "__main__":
    print(json.dumps(characterize(), indent=2, sort_keys=True))
