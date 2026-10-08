"""Subscription ownership follows the enclosing expression render decision."""

from __future__ import annotations

import json
from typing import Any

from subscription_selection_lifecycle import Store
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.subscription_expr_render import (
    _enable_subscription_expr_render,
)
from pyrolyze.runtime.dirt import DM
from pyrolyze.runtime.slot_expr import (
    LiteralFunctionProvider,
    slot_params,
    slot_params_dirt,
)


def characterize() -> dict[str, Any]:
    events: list[list[Any]] = []
    a, b = Store("a", 1, events), Store("b", 2, events)
    root = runtime.RenderContext()
    _enable_subscription_expr_render(root._state_mgr)
    module = runtime.ModuleId("tests.expression_subscription")
    manager: Any = None

    def source(ref: Any) -> Any:
        return ref

    def evaluate(store: Store, *, force: bool = False) -> int:
        nonlocal manager
        expr = root.slot_expr(
            runtime.SlotId(module, 1), lambda v: v.eval(), lambda v: v.dirty()
        )
        expr.slot_call(
            "v",
            LiteralFunctionProvider(source),
            lambda: slot_params(store.ref()),
            lambda: slot_params_dirt(force),
            slot_id=runtime.SlotId(module, 2),
        )
        manager = expr.call_site_context_manager
        return expr.apply_dirt_sink(DM()).evaluate()

    result: dict[str, Any] = {}
    with root.pass_scope():
        result["initial"] = evaluate(a)
    retained = manager.iter_current()[0]
    with root.pass_scope():
        result["same_identity"] = evaluate(a, force=True)
    a.notify(3)
    with root.pass_scope():
        result["refresh"] = evaluate(a)
        result["accepted_during_refresh"] = retained.binding.exposed_value()
    try:
        with root.pass_scope():
            result["candidate"] = evaluate(b)
            raise ValueError("discard")
    except ValueError:
        pass
    result["after_discard"] = [
        len(a.callbacks),
        len(b.callbacks),
        manager.iter_current()[0].binding.exposed_value(),
    ]
    with root.pass_scope():
        result["replacement"] = evaluate(b)
    result["after_replace"] = [len(a.callbacks), len(b.callbacks), retained.is_closed]
    with root.pass_scope():
        pass
    result["after_remove"] = [len(a.callbacks), len(b.callbacks)]
    result["events"] = events
    return result


if __name__ == "__main__":
    print(json.dumps(characterize(), sort_keys=True, indent=2))
