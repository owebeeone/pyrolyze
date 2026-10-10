"""Async expression requests share the outer render's completion decision."""

from __future__ import annotations

import json
from typing import Any, Callable

from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.dirt import DM
from pyrolyze.runtime.slot_call_semantics import (
    AsyncEffectHandle,
    UseEffectAsyncRequest,
)
from pyrolyze.runtime.slot_expr import (
    LiteralFunctionProvider,
    slot_params,
    slot_params_dirt,
)


def characterize() -> dict[str, Any]:
    root = runtime.RenderContext()
    module = runtime.ModuleId("tests.expression_async_effect")
    events: list[list[Any]] = []
    callbacks: dict[str, Callable[[], None]] = {}
    posted: list[Callable[[], None]] = []
    root.set_flush_poster(posted.append)
    manager: Any = None

    class Handle(AsyncEffectHandle):
        def __init__(self, label: str) -> None:
            self.label = label

        def cancel(self) -> None:
            events.append(["cancel", self.label])
            callbacks[self.label]()

    def source(request: Any) -> Any:
        return request

    def evaluate(label: str, deps: tuple[str, ...]) -> None:
        nonlocal manager

        def start(done: Callable[[], None]) -> AsyncEffectHandle:
            events.append(
                ["start", label, root._field_only_completion.last.published]
            )
            callbacks[label] = done
            return Handle(label)

        request = UseEffectAsyncRequest(
            start, deps, lambda: events.append(["cleanup", label])
        )
        expr = root.slot_expr(
            runtime.SlotId(module, 1), lambda e: e.eval(), lambda e: e.dirty()
        )
        expr.slot_call(
            "e",
            LiteralFunctionProvider(source),
            lambda: slot_params(request),
            lambda: slot_params_dirt(False),
            slot_id=runtime.SlotId(module, 2),
        )
        manager = expr.call_site_context_manager
        expr.apply_dirt_sink(DM()).evaluate()

    result: dict[str, Any] = {}
    with root.pass_scope():
        evaluate("a", ("a",))
        result["provisional"] = list(events)
    retained = manager.iter_current()[0].binding.binding
    with root.pass_scope():
        evaluate("stable", ("a",))
    result["stable"] = list(events)
    try:
        with root.pass_scope():
            evaluate("discard", ("discard",))
            raise ValueError("parent failed")
    except ValueError:
        pass
    result["after_discard"] = [list(events), retained.resource.is_closed]
    with root.pass_scope():
        evaluate("superseded", ("pending",))
        evaluate("latest", ("pending",))
    result["retained_closed"] = retained.resource.is_closed
    result["cancel_callback_ignored"] = len(posted)
    callbacks["a"]()
    result["stale_callback_ignored"] = len(posted)
    callbacks["latest"]()
    result["completion"] = [
        len(posted),
        manager.iter_current()[0].binding.binding.resource.completed,
    ]
    posted.clear()
    with root.pass_scope():
        evaluate("completed_stable", ("pending",))
    with root.pass_scope():
        pass
    result["removed"] = manager.iter_current() == ()
    result["events"] = events
    return result


if __name__ == "__main__":
    print(json.dumps(characterize(), sort_keys=True, indent=2))
