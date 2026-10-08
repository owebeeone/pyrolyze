"""Async-effect ownership and callback fencing at outer completion."""

from __future__ import annotations

import json
from typing import Any, Callable

from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.async_effect_render import (
    _enable_async_effect_render,
)
from pyrolyze.runtime.slot_call_semantics import (
    AsyncEffectHandle,
    UseEffectAsyncRequest,
)


def characterize() -> dict[str, Any]:
    root = runtime.RenderContext()
    _enable_async_effect_render(root._state_mgr)
    posted: list[Callable[[], None]] = []
    root.set_flush_poster(posted.append)
    events: list[list[Any]] = []
    callbacks: dict[str, Callable[[], None]] = {}
    slot_id = runtime.SlotId(runtime.ModuleId("tests.async_effect_selection"), 1)
    slot: Any = None

    class Handle:
        def __init__(self, label: str) -> None:
            self.label = label

        def cancel(self) -> None:
            events.append(["cancel", self.label])
            callbacks[self.label]()

    def evaluate(label: str, deps: tuple[str, ...] | None) -> None:
        nonlocal slot
        slot = root._ensure_slot(slot_id, runtime.SlotCallSlotContext)

        def start(done: Callable[[], None]) -> AsyncEffectHandle:
            events.append(
                ["start", label, root._state_mgr._field_only_completion.last.published]
            )
            callbacks[label] = done
            return Handle(label)

        request = UseEffectAsyncRequest(
            start, deps, lambda: events.append(["cleanup", label])
        )
        slot.evaluate(lambda value: value, (request,), {})

    result: dict[str, Any] = {}
    with root.pass_scope():
        slot = root._ensure_slot(slot_id, runtime.SlotCallSlotContext)
        with slot.pass_scope():
            evaluate("a", ("a",))
        result["provisional"] = list(events)
    retained = slot.binding
    with root.pass_scope():
        evaluate("stable", ("a",))
    try:
        with root.pass_scope():
            evaluate("failed", ("failed",))
            raise ValueError("parent failed")
    except ValueError:
        pass
    result["failed_replacement"] = list(events)
    with root.pass_scope():
        evaluate("b", ("b",))
    result["retained_snapshot_closed"] = retained.resource.is_closed
    callbacks["a"]()
    result["stale_callback_posts"] = len(posted)
    callbacks["b"]()
    result["completion_posts"] = len(posted)
    with root.pass_scope():
        evaluate("after_completion", ("b",))
    with root.pass_scope():
        evaluate("superseded", ("pending",))
        evaluate("latest", ("pending",))
    try:
        with root.pass_scope():
            slot.deactivate()
            raise ValueError("remove failed")
    except ValueError:
        pass
    result["failed_removal_active"] = not slot.binding.resource.is_closed
    with root.pass_scope():
        pass
    callbacks["latest"]()
    result["removed_callback_posts"] = len(posted)
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
    result["events"] = events
    result["ready"] = root._state_mgr._field_only_completion.last.reuse_ready
    result["scheduler"] = _scheduler_trace()
    return result


def _scheduler_trace() -> list[Any]:
    root = runtime.RenderContext()
    _enable_async_effect_render(root._state_mgr)
    events: list[Any] = []
    callbacks: list[Callable[[], None]] = []
    posted: list[Callable[[], None]] = []
    root.set_flush_poster(posted.append)

    def start(done: Callable[[], None]) -> None:
        events.append("start")
        callbacks.append(done)

    def render() -> None:
        events.append("render")
        with root.pass_scope():
            slot = root._ensure_slot(
                runtime.SlotId(runtime.ModuleId("tests.async_effect_scheduler"), 1),
                runtime.SlotCallSlotContext,
            )
            slot.evaluate(
                lambda: UseEffectAsyncRequest(
                    start, (), lambda: events.append("cleanup")
                ),
                (),
                {},
            )

    root.mount(render)
    callbacks[0]()
    events.append(["posted", len(posted)])
    posted.pop()()
    with root.pass_scope():
        pass
    return events


if __name__ == "__main__":
    print(json.dumps(characterize(), indent=2, sort_keys=True))
