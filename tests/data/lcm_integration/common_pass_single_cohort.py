"""SC2 target observations through the privately activated real context graph."""

from __future__ import annotations

import json
from collections.abc import Hashable
from dataclasses import dataclass, field
from typing import Any

from pyrolyze.api import UIElement
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.field_only_render import (
    _enable_field_only_render,
)
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted
from yidl_lifecycle.transaction_yidl import DEFAULT_TRANSACTION
from yidl_lifecycle.lifecycle import lifecycle, managed


def _root() -> Any:
    root = runtime.RenderContext()
    _enable_field_only_render(root._state_mgr)
    return root


def _slot_id(index: int) -> Any:
    return runtime.SlotId(runtime.ModuleId("tests.single_cohort"), index)


def _ui(context: Any) -> list[str]:
    return [item.props["value"] for item in context._state_mgr.committed_ui()]


def _emit(context: Any, value: str, fail: bool = False) -> None:
    context.call_native(UIElement, kind="text", props={"value": value}, children=())
    if fail:
        raise ValueError("leaf failed after emission")


def _leaf(context: Any, value: str, fail: bool = False, index: int = 1) -> Any:
    leaf = context._ensure_slot(_slot_id(index), runtime.LeafSlotContext)
    leaf.invoke_native(_emit, (value, fail), {}, context_param="context")
    return leaf


def _nested(context: Any, value: str) -> None:
    with context.pass_scope():
        _leaf(context, value)


def _component(root: Any, value: str, index: int = 2) -> Any:
    component = root._ensure_slot(_slot_id(index), runtime.ComponentCallSlotContext)
    component.invoke(_nested, (value,), {})
    return component


def _tracker(root: Any) -> Any:
    state = root._state_mgr
    return state.get_app_context(state._generation_tracker_key)


def _clean_and_failures() -> dict[str, Any]:
    root = _root()
    with root.pass_scope():
        leaf = _leaf(root, "old")
        component = _component(root, "nested-old")
    nested = component.child_context
    manager = root._state_mgr._transaction_manager
    result: dict[str, Any] = {}
    result["participant_audit"] = all(
        not state.__yidl_lifecycle_definition__["transaction_methods"]
        and all(
            not fact["has_freeze"] and not fact["has_thaw"]
            for fact in state.__yidl_lifecycle_definition__["fields"]
        )
        for state in (
            root._state_mgr,
            leaf._state_mgr,
            component._state_mgr,
            nested._state_mgr,
        )
    )
    with root.pass_scope():
        token = manager.active_transaction_for(PASS_TX_KEY)
        _leaf(root, "new")
        _component(root, "nested-new")
        result["clean_inside"] = {
            "shared_manager": leaf._state_mgr._transaction_manager is manager
            and nested._state_mgr._transaction_manager is manager,
            "current": _ui(root),
            "leaf_current": _ui(leaf),
            "nested_current": _ui(nested),
            "candidate": [
                item.props["value"] for item in root._state_mgr.build_committed_ui()
            ],
            "local_released": not leaf._state_mgr.is_scope_active()
            and not nested._state_mgr.is_scope_active(),
            "same_token": manager.active_transaction_for(PASS_TX_KEY) is token,
            "generation": _tracker(root).committed_generation_id,
        }
    result["clean_after"] = {
        "ui": _ui(root),
        "generation": _tracker(root).committed_generation_id,
    }
    try:
        with root.pass_scope():
            try:
                _leaf(root, "failed", True)
            except ValueError as error:
                result["caught"] = str(error)
            _component(root, "sibling-after-failure")
            result["caught_current"] = _ui(root)
    except RenderAttemptAborted as error:
        result["outer_abort"] = {
            "type": type(error).__name__,
            "cause": str(error.__cause__),
        }
    result["caught_after"] = {
        "ui": _ui(root),
        "generation": _tracker(root).committed_generation_id,
    }
    try:
        with root.pass_scope():
            _leaf(root, "parent-candidate")
            _component(root, "child-succeeded")
            _leaf(root, "new-membership", index=3)
            raise ValueError("parent failed after child")
    except ValueError as error:
        result["parent_error"] = str(error)
    result["parent_after"] = {
        "ui": _ui(root),
        "nested_ui": _ui(nested),
        "new_slot_registered": root.debug_is_active(_slot_id(3)),
        "children": [slot.slot_index for slot in root.debug_children_of()],
        "generation": _tracker(root).committed_generation_id,
    }
    with root.pass_scope():
        fresh_token = manager.active_transaction_for(PASS_TX_KEY)
        _leaf(root, "retry")
        _component(root, "nested-retry")
    result["retry"] = {
        "ui": _ui(root),
        "new_token": fresh_token is not token,
        "inactive": manager.active_transaction_for(PASS_TX_KEY) is None,
        "no_local_scope": not root._state_mgr.is_scope_active(),
        "generation": _tracker(root).committed_generation_id,
    }
    return result


@lifecycle
class OtherKeyValues:
    value: int = managed(default=1)


@dataclass
class _RejectingValidator:
    events: list[str] = field(default_factory=list)

    def commit_order_key_for(self, tx_key: Hashable) -> tuple[object, ...]:
        return ()

    def requires_validation_for(self, tx_key: Hashable) -> bool:
        return True

    def validate_commit_for(self, tx_key: Hashable) -> bool:
        self.events.append("validate")
        raise ValueError("validation failed")

    def _prepare_commit_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self.events.append("prepare")

    def _apply_prepared_commit_tx_by_key(
        self, tx_key: Hashable, tx_token: int | None
    ) -> None:
        self.events.append("apply")

    def _after_commit_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self.events.append("after")

    def _rollback_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self.events.append("rollback")

    def _after_rollback_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self.events.append("after rollback")


def _validation_and_permissions() -> dict[str, Any]:
    root = _root()
    manager = root._state_mgr._transaction_manager
    other = OtherKeyValues(transaction_manager=manager)
    validator = _RejectingValidator()
    result: dict[str, Any] = {}
    try:
        with root.pass_scope():
            _emit(root, "candidate")
            try:
                other.value = 2
            except RuntimeError:
                result["other_key_rejected"] = True
            manager.enlist(validator, PASS_TX_KEY)
    except ExceptionGroup as error:
        result["validation_error"] = str(error.exceptions[0])
    result["after_validation"] = {
        "events": validator.events,
        "ui": _ui(root),
        "generation": _tracker(root).committed_generation_id,
        "inactive": manager.active_transaction_for(PASS_TX_KEY) is None,
    }
    other_token = manager.begin(DEFAULT_TRANSACTION)
    other.value = 3
    with root.pass_scope():
        _emit(root, "retry")
    result["retry"] = {
        "ui": _ui(root),
        "generation": _tracker(root).committed_generation_id,
        "other_current": other.current.value,
        "other_candidate": other.value,
        "other_token_preserved": manager.active_transaction_for(DEFAULT_TRANSACTION)
        is other_token,
    }
    manager.rollback(DEFAULT_TRANSACTION)
    return result


def _entry_and_isolation() -> dict[str, Any]:
    root = _root()
    other = _root()
    manager = root._state_mgr._transaction_manager
    other_manager = other._state_mgr._transaction_manager
    result: dict[str, Any] = {"different_managers": manager is not other_manager}
    external = manager.begin(PASS_TX_KEY)
    result["external_not_local"] = not root._state_mgr.is_scope_active()
    try:
        with root.pass_scope():
            raise AssertionError("externally owned key was admitted")
    except RuntimeError as error:
        result["external_rejected"] = str(error)
    result["external_preserved"] = (
        manager.active_transaction_for(PASS_TX_KEY) is external
    )
    manager.rollback(PASS_TX_KEY)
    default_token = manager.begin(DEFAULT_TRANSACTION)
    with other.pass_scope():
        other_token = other_manager.active_transaction_for(PASS_TX_KEY)
        with root.pass_scope():
            _emit(root, "one-reset")
            with root.pass_scope():
                result["reentry_ui"] = [
                    item.props["value"] for item in root._state_mgr.own_ui_state
                ]
        result["other_preserved"] = (
            other_manager.active_transaction_for(PASS_TX_KEY) is other_token
        )
        _emit(other, "independent")
    result["default_preserved"] = (
        manager.active_transaction_for(DEFAULT_TRANSACTION) is default_token
    )
    manager.rollback(DEFAULT_TRANSACTION)
    try:
        with root.pass_scope():
            root.begin_pass()
    except RuntimeError as error:
        result["duplicate_rejected"] = str(error)
    result["duplicate_ui"] = _ui(root)
    return result


def _standalone_and_boundaries() -> dict[str, Any]:
    root = _root()
    values = ["mounted"]

    def render() -> None:
        with root.pass_scope():
            _leaf(root, values[-1])
            _component(root, values[-1] + "-nested")
            _component(root, values[-1] + "-other", index=4)

    root.mount(render)
    leaf = root._slots_by_id[_slot_id(1)]
    leaf.invoke_native(_emit, ("standalone",), {}, context_param="context")
    with root._state_mgr.publish_write_scope():
        root._state_mgr.refresh_committed_ui_from_children()
    nested = root._slots_by_id[_slot_id(2)].child_context
    sibling = root._slots_by_id[_slot_id(4)].child_context
    root._state_mgr._scheduler.request(nested)
    root._state_mgr._scheduler.request(sibling)
    root.run_pending_invalidations()
    return {
        "ui": _ui(root),
        "generation": _tracker(root).committed_generation_id,
        "pending": len(root.debug_pending_boundaries()),
        "active": root._state_mgr._transaction_manager.active_transaction_for(
            PASS_TX_KEY
        )
        is not None,
    }


def _membership_and_order() -> dict[str, Any]:
    root = _root()
    result: dict[str, Any] = {}
    with root.pass_scope():
        root._ensure_slot(_slot_id(9), runtime.SlotContext)
    result["structural_slot"] = {
        "ui": _ui(root),
        "children": [slot.slot_index for slot in root.debug_children_of()],
    }
    orders = ((1, 2), (2, 1), (3,), (1, 2, 3), (3, 2, 1), (3, 2, 1))
    observations = []
    for order in orders:
        with root.pass_scope():
            for index in order:
                _leaf(root, str(index), index=index)
        observations.append(
            {
                "children": [slot.slot_index for slot in root.debug_children_of()],
                "ui": _ui(root),
            }
        )
    result["orders"] = observations
    return result


def _published_membership() -> dict[str, Any]:
    root = _root()
    result: dict[str, Any] = {}

    def observe() -> dict[str, Any]:
        return {
            "children": [slot.slot_index for slot in root.debug_children_of()],
            "active": root.debug_is_active(_slot_id(10)),
            "slot_children": [
                slot.slot_index for slot in root.debug_children_of(_slot_id(10))
            ],
            "slot_ui": [item.props["value"] for item in root.debug_ui(_slot_id(10))],
        }

    def add() -> None:
        parent = root._ensure_slot(_slot_id(10), runtime.LeafSlotContext)
        with parent.pass_scope():
            _leaf(parent, "published-child", index=11)

    try:
        with root.pass_scope():
            add()
            result["addition_inside"] = observe()
            raise ValueError("discard addition")
    except ValueError:
        pass
    result["addition_discarded"] = observe()
    with root.pass_scope():
        add()
        result["addition_retry_inside"] = observe()
    result["addition_committed"] = observe()
    try:
        with root.pass_scope():
            result["removal_inside"] = observe()
            raise ValueError("discard removal")
    except ValueError:
        pass
    result["removal_discarded"] = observe()
    with root.pass_scope():
        result["removal_retry_inside"] = observe()
    result["removal_committed"] = observe()
    return result


def characterize() -> dict[str, Any]:
    return {
        "clean_and_failures": _clean_and_failures(),
        "entry_and_isolation": _entry_and_isolation(),
        "standalone_and_boundaries": _standalone_and_boundaries(),
        "validation_and_permissions": _validation_and_permissions(),
        "membership_and_order": _membership_and_order(),
        "published_membership": _published_membership(),
    }


if __name__ == "__main__":
    print(json.dumps(characterize(), indent=2, sort_keys=True))
