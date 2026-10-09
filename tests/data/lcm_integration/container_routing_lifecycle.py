"""Authored scope containers share one publication and resource decision."""

from __future__ import annotations

import json
from typing import Any

from pyrolyze.api import MountDirective
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.container_render import _enable_container_render


def characterize() -> dict[str, Any]:
    namespace = load_transformed_namespace(
        """
from pyrolyze.api import ComponentRef, MountSelector, UIElement, call_native, mount, pyrolyze, pyrolyze_slotted
from pyrolyze.runtime.context_bare_refactor_lcm import ContextBase
from pyrolyze.runtime.slot_call_semantics import ExternalStoreRef

calls = []

def native_frame(ctx: ContextBase):
    ctx.call_native(UIElement, kind="native", props={})

@pyrolyze
def frame(label):
    call_native(UIElement)(kind="frame", props={"label": label})

@pyrolyze_slotted
def observe(label):
    def subscribe(callback):
        calls.append("subscribe:" + label)
        return lambda: calls.append("unsubscribe:" + label)
    return ExternalStoreRef(label, subscribe, lambda: label)

@pyrolyze
def panel(label, target, native: ComponentRef):
    with frame(label):
        with native():
            with mount(MountSelector.named(target)):
                call_native(UIElement)(kind="text", props={"label": label})
                observe(label)
""",
        module_name="container_routing_authored",
    )
    root = runtime.RenderContext()
    _enable_container_render(root._state_mgr)
    slot_id = runtime.SlotId(runtime.ModuleId("container-routing"), 1)

    def projection(node):
        if isinstance(node, MountDirective):
            return [
                "mount",
                [selector.name for selector in node.selectors],
                [projection(child) for child in node.children],
            ]
        return [
            node.kind,
            dict(node.props),
            [projection(child) for child in node.children],
        ]

    def ui():
        return [projection(node) for node in root.debug_ui()]

    def render(label, target):
        root.component_call(
            slot_id, namespace["panel"], label, target, namespace["native_frame"]
        )

    result: dict[str, Any] = {}
    with root.pass_scope():
        render("old", "menu")
        result["provisional"] = ui()
    result["accepted"] = [ui(), list(namespace["calls"])]
    try:
        with root.pass_scope():
            render("discard", "temporary")
            raise ValueError("discard")
    except ValueError:
        pass
    result["rollback"] = [ui(), list(namespace["calls"])]
    with root.pass_scope():
        render("new", "corner")
    result["replacement"] = [ui(), list(namespace["calls"])]
    with root.pass_scope():
        pass
    result["omitted"] = [ui(), list(namespace["calls"])]
    return result


if __name__ == "__main__":
    print(json.dumps(characterize(), sort_keys=True))
