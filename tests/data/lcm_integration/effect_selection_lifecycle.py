"""Synchronous effect selection under one outer render decision."""

from __future__ import annotations

import json
from typing import Any, Callable

from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.effect_render import _enable_effect_render
from pyrolyze.runtime.slot_call_semantics import UseEffectRequest


def _source(request: UseEffectRequest) -> UseEffectRequest:
    return request


def characterize() -> dict[str, Any]:
    root = runtime.RenderContext()
    _enable_effect_render(root._state_mgr)
    slot_id = runtime.SlotId(runtime.ModuleId("tests.effect_selection"), 1)
    events: list[list[Any]] = []
    slot: Any = None

    def evaluate(label: str, deps: tuple[str, ...] | None) -> None:
        nonlocal slot
        slot = root._ensure_slot(slot_id, runtime.SlotCallSlotContext)

        def effect() -> Callable[[], None]:
            completion = root._state_mgr._field_only_completion
            events.append(["setup", label, completion.last.published])
            return lambda: events.append(["cleanup", label])

        slot.evaluate(_source, (UseEffectRequest(effect, deps),), {})

    result: dict[str, Any] = {}
    with root.pass_scope():
        slot = root._ensure_slot(slot_id, runtime.SlotCallSlotContext)
        with slot.pass_scope():
            evaluate("a", ("first",))
        result["provisional"] = list(events)
    result["initial"] = list(events)
    retained = slot.binding
    with root.pass_scope():
        evaluate("stable", ("first",))
    result["stable_dependencies"] = list(events)
    try:
        with root.pass_scope():
            evaluate("failed", ("failed",))
            raise ValueError("parent failed")
    except ValueError:
        pass
    result["failed_replacement"] = [list(events), retained.resource.is_closed]
    with root.pass_scope():
        evaluate("c", ("changed",))
    result["retained_snapshot_closed"] = retained.resource.is_closed
    with root.pass_scope():
        evaluate("unused", ("unused",))
        evaluate("final", ("final",))
    try:
        with root.pass_scope():
            slot.deactivate()
            raise ValueError("removal failed")
    except ValueError:
        pass
    result["failed_removal_active"] = not slot.binding.resource.is_closed
    with root.pass_scope():
        pass
    result["omitted"] = slot.binding is None
    with root.pass_scope():
        evaluate("always1", None)
    with root.pass_scope():
        evaluate("always2", None)
    with root.pass_scope():
        evaluate("once", ())
    with root.pass_scope():
        evaluate("skipped", ())
    with root.pass_scope():
        slot.deactivate()
    result["explicit_removal"] = slot.binding is None
    with root.pass_scope():
        evaluate("superseded", ("pending",))
        evaluate("latest", ("pending",))
    with root.pass_scope():
        slot.deactivate()
    result["ready"] = root._state_mgr._field_only_completion.last.reuse_ready
    result["events"] = events
    return result


if __name__ == "__main__":
    print(json.dumps(characterize(), indent=2, sort_keys=True))
