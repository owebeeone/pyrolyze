"""Selected override reads acknowledge only their own accepted publication."""

from __future__ import annotations

import json
from typing import Any

from pyrolyze.api import use_app_context
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.app_context import AppContextKey
from pyrolyze.runtime.context_state_lcm.pass_state_render import _enable_pass_state_render
from pyrolyze.runtime.dirt import DM
from pyrolyze.runtime.slot_expr import LiteralFunctionProvider, slot_params, slot_params_dirt


def read(scope: Any, slot_id: Any, key: Any, expression: bool) -> Any:
    if expression:
        expr = scope.slot_expr(slot_id, lambda v: v.eval(), lambda v: v.dirty())
        expr.slot_call(
            "v", LiteralFunctionProvider(use_app_context),
            lambda: slot_params(key), lambda: slot_params_dirt(True), slot_id=slot_id,
        )
        expr.apply_dirt_sink(DM()).evaluate()
        context = expr.call_site_context_manager.get_visible(slot_id)
        return context.binding.binding
    slot = scope._ensure_slot(slot_id, runtime.SlotCallSlotContext)
    slot.invoke_dirty = True
    slot.evaluate(use_app_context, (key,), {})
    return slot._state_mgr._invocation.binding


def characterize() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for expression in (False, True):
        root = runtime.RenderContext()
        _enable_pass_state_render(root._state_mgr)
        key = AppContextKey("theme", lambda host: "unused")
        module = runtime.ModuleId("override-read-proof")
        outer_id, middle_id, inner_id, first_id, second_id = (
            runtime.SlotId(module, index) for index in range(1, 6)
        )
        with root.pass_scope():
            with root.open_app_context_override(outer_id, (key,), "old") as outer:
                with (
                    outer.open_app_context_override(middle_id, (key,), None) as middle,
                    middle.open_app_context_override(inner_id, (key,), None) as inner,
                ):
                    first = read(inner, first_id, key, expression)
                    second = read(inner, second_id, key, expression)
                    source = inner.authored_app_context_ref(key).identity
        initial = [first.resource.revision, second.resource.revision]
        assert initial == [0, 0]
        with root.pass_scope():
            with root.open_app_context_override(outer_id, (key,), "new") as outer:
                with (
                    outer.open_app_context_override(middle_id, (key,), None) as middle,
                    middle.open_app_context_override(inner_id, (key,), None) as inner,
                ):
                    selected = read(inner, first_id, key, expression)
                    inner.retain_slot(second_id)
        selective = [selected.resource.revision, second.resource.revision]
        assert selective == [0, 1]
        source.next("independent")
        independent = [selected.resource.revision, second.resource.revision]
        assert independent == [1, 2]
        with root.pass_scope():
            for value in ("intermediate", "latest"):
                with root.open_app_context_override(outer_id, (key,), value) as outer:
                    with (
                        outer.open_app_context_override(middle_id, (key,), None) as middle,
                        middle.open_app_context_override(inner_id, (key,), None) as inner,
                    ):
                        latest = read(inner, first_id, key, expression)
                        inner.retain_slot(second_id)
        latest_revisions = [latest.resource.revision, second.resource.revision]
        assert latest_revisions == [1, 3]
        result["expression" if expression else "slot_call"] = {
            "initial": initial,
            "selected_value": selected.value,
            "resource_reused": selected.resource is first.resource,
            "selective": selective,
            "independent": independent,
            "latest_value": latest.value,
            "latest_revisions": latest_revisions,
        }
    return result


if __name__ == "__main__":
    print(json.dumps(characterize(), sort_keys=True))
