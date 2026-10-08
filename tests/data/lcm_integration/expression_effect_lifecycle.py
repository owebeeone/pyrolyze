"""Expression effects are delivered only after outer publication."""

from __future__ import annotations

import json
from typing import Any, Callable

from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.effect_expr_render import (
    _enable_effect_expr_render,
)
from pyrolyze.runtime.dirt import DM
from pyrolyze.runtime.slot_call_semantics import UseEffectRequest
from pyrolyze.runtime.slot_expr import (
    LiteralFunctionProvider,
    slot_params,
    slot_params_dirt,
)


def characterize() -> dict[str, Any]:
    root = runtime.RenderContext()
    _enable_effect_expr_render(root._state_mgr)
    module = runtime.ModuleId("tests.expression_effect")
    events: list[list[Any]] = []
    manager: Any = None

    def source(request: UseEffectRequest) -> UseEffectRequest:
        return request

    def evaluate(label: str, deps: tuple[str, ...] | None) -> None:
        nonlocal manager

        def effect() -> Callable[[], None]:
            events.append(
                ["setup", label, root._state_mgr._field_only_completion.last.published]
            )
            return lambda: events.append(["cleanup", label])

        expr = root.slot_expr(
            runtime.SlotId(module, 1), lambda e: e.eval(), lambda e: e.dirty()
        )
        expr.slot_call(
            "e",
            LiteralFunctionProvider(source),
            lambda: slot_params(UseEffectRequest(effect, deps)),
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
            raise ValueError("parent failure")
    except ValueError:
        pass
    result["after_discard"] = [list(events), retained.resource.is_closed]
    with root.pass_scope():
        evaluate("b", ("b",))
    result["retained_closed"] = retained.resource.is_closed
    with root.pass_scope():
        evaluate("superseded", ("pending",))
        evaluate("latest", ("pending",))
    with root.pass_scope():
        pass
    with root.pass_scope():
        evaluate("always1", None)
    with root.pass_scope():
        evaluate("always2", None)
    with root.pass_scope():
        evaluate("once", ())
    with root.pass_scope():
        evaluate("skipped", ())
    with root.pass_scope():
        pass
    result["removed"] = manager.iter_current() == ()
    result["events"] = events
    return result


if __name__ == "__main__":
    print(json.dumps(characterize(), sort_keys=True, indent=2))
