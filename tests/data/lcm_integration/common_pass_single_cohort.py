"""SC2 target observations through the privately activated real context graph."""

from __future__ import annotations

import json
from collections.abc import Hashable
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import patch

from pyrolyze.api import UIElement
from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted
from yidl_lifecycle.transaction_yidl import DEFAULT_TRANSACTION
from yidl_lifecycle.lifecycle import lifecycle, managed


def _root() -> Any:
    root = runtime.RenderContext()
    return root


def _slot_id(index: int) -> Any:
    return runtime.SlotId(runtime.ModuleId("tests.single_cohort"), index)


def _ui(context: Any) -> list[str]:
    return [item.props["value"] for item in context.committed_ui()]


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
    state = root
    return state.get_app_context(state._generation_tracker_key)


def _clean_and_failures() -> dict[str, Any]:
    root = _root()
    with root.pass_scope():
        leaf = _leaf(root, "old")
        component = _component(root, "nested-old")
    nested = component.child_context
    manager = root._transaction_manager
    result: dict[str, Any] = {}
    result["participant_audit"] = all(
        not state.__yidl_lifecycle_definition__["transaction_methods"]
        and all(
            not fact["has_freeze"] and not fact["has_thaw"]
            for fact in state.__yidl_lifecycle_definition__["fields"]
        )
        for state in (
            root,
            leaf,
            component,
            nested,
        )
    )
    with root.pass_scope():
        token = manager.active_transaction_for(PASS_TX_KEY)
        _leaf(root, "new")
        _component(root, "nested-new")
        result["clean_inside"] = {
            "shared_manager": leaf._transaction_manager is manager
            and nested._transaction_manager is manager,
            "current": _ui(root),
            "leaf_current": _ui(leaf),
            "nested_current": _ui(nested),
            "candidate": [
                item.props["value"] for item in root.build_committed_ui()
            ],
            "local_released": not leaf.is_scope_active()
            and not nested.is_scope_active(),
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
        "no_local_scope": not root.is_scope_active(),
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
    manager = root._transaction_manager
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
    manager = root._transaction_manager
    other_manager = other._transaction_manager
    result: dict[str, Any] = {"different_managers": manager is not other_manager}
    external = manager.begin(PASS_TX_KEY)
    result["external_not_local"] = not root.is_scope_active()
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
                    item.props["value"] for item in root.own_ui_state
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
    with root.publish_write_scope():
        root.refresh_committed_ui_from_children()
    nested = root._slots_by_id[_slot_id(2)].child_context
    sibling = root._slots_by_id[_slot_id(4)].child_context
    root._scheduler.request(nested)
    root._scheduler.request(sibling)
    root.run_pending_invalidations()
    return {
        "ui": _ui(root),
        "generation": _tracker(root).committed_generation_id,
        "pending": len(root.debug_pending_boundaries()),
        "active": root._transaction_manager.active_transaction_for(
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


def _candidate_retirement() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for slot_type in (runtime.LeafSlotContext, runtime.SlotContext):
        root = _root()
        with root.pass_scope():
            old = root._ensure_slot(_slot_id(1), slot_type)
        with root.pass_scope():
            root._ensure_slot(_slot_id(1), slot_type)
            _leaf(root, "keep", index=3)
            old.deactivate()
            inside = {
                "candidate": [
                    slot.slot_index for slot in root.children_state
                ],
                "published": [slot.slot_index for slot in root.debug_children_of()],
            }
        result[slot_type.__name__] = {
            "inside": inside,
            "after": [slot.slot_index for slot in root.debug_children_of()],
            "ui": _ui(root),
        }
    root = _root()

    def render() -> None:
        with root.pass_scope():
            first = _component(root, "first")
        with root.pass_scope():
            second = _component(root, "second")
        result["same_component"] = first is second

    root.mount(render)
    result["repeat_ui"] = _ui(root)
    result["repeat_generation"] = _tracker(root).committed_generation_id
    return result


@dataclass
class _CompletionFault(_RejectingValidator):
    failure_phase: str | None = None

    def requires_validation_for(self, tx_key: Hashable) -> bool:
        return self.failure_phase == "validate"

    def _visit(self, phase: str) -> None:
        self.events.append(phase)
        if phase == self.failure_phase:
            raise ValueError(f"{phase} failed")

    def validate_commit_for(self, tx_key: Hashable) -> bool:
        self._visit("validate")
        return True

    def _prepare_commit_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self._visit("prepare")

    def _apply_prepared_commit_tx_by_key(
        self, tx_key: Hashable, tx_token: int | None
    ) -> None:
        self._visit("apply")

    def _after_commit_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self._visit("after commit")

    def _rollback_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self._visit("rollback")

    def _after_rollback_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self._visit("after rollback")


def _completion_evidence() -> dict[str, Any]:
    results: dict[str, Any] = {}
    cases = (
        "empty commit",
        "empty rollback",
        "empty abort",
        "validate",
        "prepare",
        "apply",
        "after commit",
        "rollback",
        "after rollback",
    )
    for case in cases:
        root = _root()
        completion = root._field_only_completion
        tracker = _tracker(root)
        manager = root._transaction_manager
        decisions = []
        commit, rollback = tracker.commit, tracker.rollback

        def record_commit(self: Any) -> int:
            decisions.append("commit")
            return commit()

        def record_rollback(self: Any) -> int:
            decisions.append("rollback")
            return rollback()

        fault = _CompletionFault(failure_phase=case)
        error = None
        try:
            # Direct owner entry leaves the empty cases genuinely participant-free.
            with (
                patch.object(type(tracker), "commit", record_commit),
                patch.object(type(tracker), "rollback", record_rollback),
                completion.attempt_scope(),
            ):
                owner = completion.active
                if not case.startswith("empty"):
                    with root.pass_scope():
                        _leaf(root, "candidate")
                        manager.enlist(fault, PASS_TX_KEY)
                        if case in ("rollback", "after rollback"):
                            raise ValueError("body failed")
                elif case == "empty rollback":
                    owner.fail(ValueError("caught body failure"))
                elif case == "empty abort":
                    raise ValueError("body failed")
        except BaseException as exc:
            error = type(exc).__name__
        owner = completion.last
        record = owner.transaction.completion
        assert record is not None
        published = case in ("empty commit", "after commit")
        uncertain = case == "apply"
        reusable = case in (
            "empty commit",
            "empty rollback",
            "empty abort",
            "validate",
            "prepare",
        )
        assert owner.publication_uncertain is uncertain, case
        assert owner.reuse_ready is reusable, case
        assert decisions == (
            [] if uncertain else ["commit" if published else "rollback"]
        ), case
        assert tracker.committed_generation_id == int(published), case
        assert (tracker.active_generation_id is not None) is uncertain, case
        assert _ui(root) == (
            ["candidate"] if case in ("apply", "after commit") else []
        ), case
        results[case] = {
            "publication_started": record.publication_started,
            "publication_complete": record.publication_complete,
            "discard_complete": record.discard_complete,
            "after_actions_complete": record.after_actions_complete,
            "generation_decisions": list(decisions),
            "generation": tracker.committed_generation_id,
            "generation_pending": tracker.active_generation_id is not None,
            "reuse_ready": owner.reuse_ready,
            "publication_uncertain": owner.publication_uncertain,
            "ui": _ui(root),
            "error": error,
            "events": fault.events,
            "registered": root.debug_is_active(_slot_id(1)),
        }
        if not reusable:
            try:
                with root.pass_scope():
                    raise AssertionError("quarantined graph admitted retry")
            except RuntimeError as exc:
                assert "reuse" in str(exc), case
        assert decisions == results[case]["generation_decisions"], case
    return results


def characterize() -> dict[str, Any]:
    return {
        "clean_and_failures": _clean_and_failures(),
        "entry_and_isolation": _entry_and_isolation(),
        "standalone_and_boundaries": _standalone_and_boundaries(),
        "validation_and_permissions": _validation_and_permissions(),
        "membership_and_order": _membership_and_order(),
        "published_membership": _published_membership(),
        "candidate_retirement": _candidate_retirement(),
        "completion_evidence": _completion_evidence(),
    }


if __name__ == "__main__":
    print(json.dumps(characterize(), indent=2, sort_keys=True))
