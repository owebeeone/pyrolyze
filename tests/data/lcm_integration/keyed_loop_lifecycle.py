"""Keyed selection and nested resource retirement share outer publication."""

from __future__ import annotations

import json
from typing import Any

from pyrolyze.api import UIElement
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.keyed_loop_render import (
    _enable_keyed_loop_render,
)
from pyrolyze.runtime.slot_call_semantics import ExternalStoreRef


def characterize() -> dict[str, Any]:
    root = runtime.RenderContext()
    _enable_keyed_loop_render(root._state_mgr)
    module = runtime.ModuleId("loop-proof")
    loop_id = runtime.SlotId(module, 1)
    result: dict[str, Any] = {}
    resources = []
    identities = {}

    def render(values):
        dirty = []
        items = []
        for item in root.keyed_loop(loop_id, values, key_fn=lambda value: value[0]):
            with item.pass_scope():
                changed, value = item.current_value()
                dirty.append(list(changed))
                items.append(item)
                item.call_native(UIElement, kind="text", props={"value": value[1]})
                slot = item._ensure_slot(
                    runtime.SlotId(module, 2), runtime.SlotCallSlotContext
                )
                name = value[0]

                def subscribe(callback, name=name):
                    resources.append("subscribe:" + name)
                    return lambda: resources.append("unsubscribe:" + name)

                slot.evaluate(
                    lambda: ExternalStoreRef(name, subscribe, lambda: name), (), {}
                )
        return items, dirty

    def values():
        return [node.props["value"] for node in root.debug_ui()]

    with root.pass_scope():
        items, dirty = render([("a", 1), ("b", 2)])
        identities.update(zip(("a", "b"), items))
    result["initial"] = [values(), dirty, list(resources)]
    with root.pass_scope():
        items, dirty = render([("b", 2), ("a", 3)])
    result["reorder"] = [
        values(),
        dirty,
        [items[0] is identities["b"], items[1] is identities["a"]],
    ]
    try:
        with root.pass_scope():
            render([("a", 99), ("c", 4)])
            raise ValueError("discard")
    except ValueError:
        pass
    result["rollback"] = [
        values(),
        identities["a"]._state_mgr.current._selection.value,
        list(resources),
    ]
    with root.pass_scope():
        items, dirty = render([("a", 5)])
    result["remove_and_retry"] = [
        values(),
        dirty,
        items[0] is identities["a"],
        list(resources),
    ]
    with root.pass_scope():
        for outer in root.keyed_loop(
            loop_id, [("a", 5)], key_fn=lambda value: value[0]
        ):
            with outer.pass_scope():
                for inner in outer.keyed_loop(
                    runtime.SlotId(module, 3), [7], key_fn=lambda value: value
                ):
                    with inner.pass_scope():
                        result["nested_key"] = list(inner.current_slot_id().key_path)
    with root.pass_scope():
        pass
    result["omit"] = [values(), list(resources)]
    namespace = load_transformed_namespace(
        """
from pyrolyze.api import UIElement, call_native, keyed, pyrolyze

@pyrolyze
def panel(values, stop=False):
    for value in keyed(values, key=lambda value: value[0]):
        call_native(UIElement)(kind="text", props={"value": value[1]})
        if stop:
            break
""",
        module_name="keyed_lifecycle_authored",
    )
    compiled_root = runtime.RenderContext()
    _enable_keyed_loop_render(compiled_root._state_mgr)
    component_id = runtime.SlotId(module, 4)
    for rows in ([("a", 1), ("b", 2)], [("b", 3), ("a", 1)]):
        with compiled_root.pass_scope():
            compiled_root.component_call(component_id, namespace["panel"], rows)
    result["compiled"] = [node.props["value"] for node in compiled_root.debug_ui()]
    with compiled_root.pass_scope():
        compiled_root.component_call(
            component_id, namespace["panel"], [("a", 8), ("b", 9)], stop=True
        )
    result["compiled_break"] = [
        node.props["value"] for node in compiled_root.debug_ui()
    ]
    try:
        with compiled_root.pass_scope():
            compiled_root.component_call(
                component_id, namespace["panel"], [("a", 99), ("b", 9)], stop=True
            )
            raise ValueError("discard prefix")
    except ValueError:
        pass
    result["compiled_break_rollback"] = [
        node.props["value"] for node in compiled_root.debug_ui()
    ]
    return result


if __name__ == "__main__":
    print(json.dumps(characterize(), sort_keys=True))
