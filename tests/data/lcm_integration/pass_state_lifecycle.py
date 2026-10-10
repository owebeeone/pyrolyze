"""Render consumption rolls back; independently arriving requests do not."""

from __future__ import annotations

import json
from typing import Any

from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY


def _root() -> Any:
    root = runtime.RenderContext()
    return root


def characterize() -> dict[str, Any]:
    root = _root()
    completion = root._field_only_completion
    slot_id = runtime.SlotId(runtime.ModuleId("pass-state"), 1)
    calls: list[int] = []
    notify_during_call = False
    slot: Any = None

    def source(value: int) -> int:
        nonlocal notify_during_call
        calls.append(value)
        if notify_during_call:
            notify_during_call = False
            root.queue_invalidation_from(slot)
        return value

    def visit(value: int = 1) -> None:
        nonlocal slot
        slot = root._ensure_slot(slot_id, runtime.SlotCallSlotContext)
        slot.evaluate(source, (value,), {})

    def state() -> list[Any]:
        backing = slot
        return [
            backing._requested_revision,
            backing.current._handled_revision,
            slot.invoke_dirty,
            slot.seen_in_pass,
            len(calls),
        ]

    result: dict[str, Any] = {}
    with root.pass_scope():
        visit()
    fields = {
        row["field_name"]: row
        for row in slot.__yidl_lifecycle_definition__["fields"]
    }
    result["declarations"] = [
        fields["_requested_revision"]["field_kind"],
        fields["_handled_revision"]["field_kind"],
        fields["_handled_revision"]["tx_key_key"] == PASS_TX_KEY,
        fields["_pass_seen_in_pass"]["field_kind"],
        fields["_pass_requested_revision"]["field_kind"],
    ]
    result["initial"] = state()
    with root.pass_scope():
        visit()
    result["unchanged"] = state()

    root.queue_invalidation_from(slot)
    notify_during_call = True
    with completion.attempt_scope():
        with root.pass_scope():
            visit()
        result["later_request_provisional"] = [
            slot._handled_revision,
            slot.invoke_dirty,
        ]
    result["later_request_committed"] = state()
    with root.pass_scope():
        visit()
    result["later_request_consumed"] = state()

    root.queue_invalidation_from(slot)
    try:
        with completion.attempt_scope():
            with root.pass_scope():
                visit()
            result["failure_provisional"] = [
                slot._handled_revision,
                slot.current._handled_revision,
            ]
            raise ValueError("outer failure")
    except ValueError:
        pass
    result["failure_discarded"] = state()
    with root.pass_scope():
        visit()
    result["failure_retry"] = state()

    with completion.attempt_scope():
        with root.pass_scope():
            visit(2)
        root.queue_invalidation_from(slot)
        with root.pass_scope():
            visit(2)
    result["repeated_passes"] = state()

    with completion.attempt_scope():
        with root.pass_scope():
            visit(2)
        root.queue_invalidation_from(slot)
    result["notification_after_local_exit"] = state()
    with root.pass_scope():
        visit(2)
    result["notification_retry"] = state()

    try:
        with completion.attempt_scope():
            with root.pass_scope():
                pass
            result["removal_provisional"] = [
                bool(root.children_state),
                slot.seen_in_pass,
                slot.current._pass_seen_in_pass,
            ]
            raise ValueError("discard removal")
    except ValueError:
        pass
    result["removal_discarded"] = [
        bool(root.children_state),
        slot.seen_in_pass,
    ]
    other = _root()
    with other.pass_scope():
        other_slot = other._ensure_slot(slot_id, runtime.SlotCallSlotContext)
        other_slot.evaluate(source, (3,), {})
    root.queue_invalidation_from(slot)
    result["independent_root"] = [
        slot.invoke_dirty,
        other_slot.invoke_dirty,
        root._transaction_manager
        is not other._transaction_manager,
    ]
    result["bookkeeping_unused"] = [
        not hasattr(root, "_pass_child_dirty"),
        not getattr(root, "_field_only_has_snapshot", False),
        completion._invalidated_states == {},
    ]
    slot.invoke_dirty = False
    cancelled = not slot.invoke_dirty
    root.queue_invalidation_from(slot)
    result["explicit_cancel"] = [cancelled, slot.invoke_dirty]
    with root.pass_scope():
        pass
    result["removal_committed"] = root.current.children_state == {}
    result["partial_rerender"] = _partial_rerender()
    result["owned_handlers"] = _owned_handlers()
    return result


def _partial_rerender() -> dict[str, Any]:
    calls: list[str] = []
    module = runtime.ModuleId("partial-pass")

    def observe(label: str) -> str:
        calls.append(label)
        return label

    def child(context: Any) -> None:
        with context.pass_scope():
            slot = context._ensure_slot(
                runtime.SlotId(module, 3), runtime.SlotCallSlotContext
            )
            slot.evaluate(observe, ("child",), {})

    def panel(context: Any) -> None:
        with context.pass_scope():
            component = context._ensure_slot(
                runtime.SlotId(module, 2), runtime.ComponentCallSlotContext
            )
            component.invoke(child, (), {})
            slot = context._ensure_slot(
                runtime.SlotId(module, 4), runtime.SlotCallSlotContext
            )
            slot.evaluate(observe, ("sibling",), {})

    root = _root()
    with root.pass_scope():
        component = root._ensure_slot(
            runtime.SlotId(module, 1), runtime.ComponentCallSlotContext
        )
        component.invoke(panel, (), {})
    # Locate via the accepted graph, not the scheduler's registration cache.
    panel = next(iter(root.children_state.values()))
    render = panel._child_context_state_mgr
    child = next(
        state
        for state in render.children_state.values()
        if isinstance(state.owner, runtime.ComponentCallSlotContext)
    )
    child_render = child._child_context_state_mgr
    observed = next(iter(child_render.children_state.values()))
    sibling = next(
        state
        for state in render.children_state.values()
        if isinstance(state.owner, runtime.SlotCallSlotContext)
    )
    accepted_sibling = sibling.current._invocation
    root.queue_invalidation_from(observed)
    root.run_pending_invalidations()
    return {
        "calls": calls,
        "consumed": [not observed._invoke_dirty, not child._invoke_dirty],
        "sibling_retained": sibling.current._invocation is accepted_sibling,
        "scheduled_work_drained": not root._scheduler.has_pending_work(),
    }


def _owned_handlers() -> dict[str, Any]:
    root = _root()
    module = runtime.ModuleId("pass-state-handlers")
    calls: list[str] = []
    held: list[Any] = []

    def child(context: Any, handler: Any) -> None:
        with context.pass_scope():
            if handler is not None:
                held.append(handler)

    def invoke(label: str | None) -> None:
        binding = (
            None
            if label is None
            else root.event_handler_binding(
                runtime.SlotId(module, 1),
                callback=lambda: calls.append(label),
                dirty=True,
            )
        )
        component = root._ensure_slot(
            runtime.SlotId(module, 2), runtime.ComponentCallSlotContext
        )
        component.invoke(child, (binding,), {})

    with root.pass_scope():
        invoke("old")
    dispatch = held[-1]
    dispatch()
    handler = root._slots_by_id[runtime.SlotId(module, 1)]
    try:
        with root.pass_scope():
            invoke(None)
            raise ValueError("discard handler omission")
    except ValueError:
        pass
    retained = handler._seen_in_pass
    dispatch()
    with root.pass_scope():
        invoke("new")
    dispatch()
    with root.pass_scope():
        invoke(None)
    try:
        dispatch()
    except RuntimeError as error:
        inactive = str(error)
    else:
        raise AssertionError("omitted handler must be inactive")
    return {"calls": calls, "rollback_retained": retained, "omitted": inactive}


if __name__ == "__main__":
    print(json.dumps(characterize(), indent=2, sort_keys=True))
