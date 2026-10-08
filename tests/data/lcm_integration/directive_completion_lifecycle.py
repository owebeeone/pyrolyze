"""Directive publication, registries, and outer completion delivery timeline."""

from __future__ import annotations

import json
from typing import Any

from pyrolyze.api import MountSelector, UIElement, validate_mount_selectors
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.completion_render import (
    _enable_completion_render,
)


def characterize() -> dict[str, Any]:
    root = runtime.RenderContext()
    _enable_completion_render(root._state_mgr)
    slot_id = runtime.SlotId(runtime.ModuleId("completion-proof"), 1)
    tracker = root._state_mgr.get_app_context(root._state_mgr._generation_tracker_key)
    calls = []
    result: dict[str, Any] = {}

    def observation():
        directive = root.debug_ui()[0]
        calls.append(
            [
                directive.selectors[0].name,
                directive.children[0].props["value"],
                root.debug_is_active(slot_id),
                tracker.committed_generation_id,
                tracker.active_generation_id is None,
            ]
        )

    def render(name, value):
        with root.open_directive(
            slot_id, validate_mount_selectors, MountSelector.named(name)
        ) as scope:
            scope.call_native(UIElement, kind="text", props={"value": value})
            with scope.open_directive(
                runtime.SlotId(slot_id.module_id, 2),
                validate_mount_selectors,
                MountSelector.named("nested"),
            ) as nested:
                nested.call_native(UIElement, kind="text", props={"value": value + 1})
        root._enqueue_post_commit(observation)
        return scope

    with root.pass_scope():
        scope = render("old", 1)
        result["before_outer_exit"] = [list(calls), root.debug_is_active(slot_id)]
    result["accepted"] = list(calls)
    nested = root.debug_ui()[0].children[1]
    result["nested"] = [nested.selectors[0].name, nested.children[0].props["value"]]
    try:
        with root.pass_scope():
            render("discard", 2)
            raise ValueError("discard")
    except ValueError:
        pass
    result["discard"] = [scope.committed_selectors[0].name, list(calls)]
    with root.pass_scope():
        render("new", 3)
    result["retry"] = list(calls)
    with root.pass_scope():
        pass
    result["removed"] = [root.debug_is_active(slot_id), list(root.debug_ui())]
    expressions = []
    with root.pass_scope():
        slot = root._ensure_slot(slot_id, runtime.SlotExprSlotContext)
        with slot.pass_scope():
            slot.append_slot_expr_post_commit_callback(
                lambda: expressions.append("expression")
            )
            root._state_mgr.queue_invalidation_from(slot)
        result["expression_before_exit"] = list(expressions)
    result["expression_after_exit"] = expressions
    result["independent_invalidation"] = [
        root._state_mgr._scheduler.has_pending_work(),
        slot._state_mgr._invoke_dirty,
    ]
    return result


if __name__ == "__main__":
    print(json.dumps(characterize(), sort_keys=True))
