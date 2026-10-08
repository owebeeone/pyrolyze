"""Expression mount advertisements follow the shared render decision."""

from __future__ import annotations

import json
from typing import Any

from mount_selection_lifecycle import native_section
from pyrolyze.api import advertise_mount
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.mount_expr_render import (
    _enable_mount_expr_render,
)
from pyrolyze.runtime.dirt import DM
from pyrolyze.runtime.slot_expr import (
    LiteralFunctionProvider,
    slot_params,
    slot_params_dirt,
)


def characterize() -> dict[str, Any]:
    root = runtime.RenderContext()
    _enable_mount_expr_render(root._state_mgr)
    module = runtime.ModuleId("tests.expression_mount")
    container_id = runtime.SlotId(module, 1)
    call_id = runtime.SlotId(module, 9)
    manager: Any = None

    def evaluate(container: Any, key: str, index: int = 2) -> None:
        nonlocal manager
        expression = container.slot_expr(
            runtime.SlotId(module, index), lambda e: e.eval(), lambda e: e.dirty()
        )
        expression.slot_call(
            "e",
            LiteralFunctionProvider(advertise_mount),
            lambda: slot_params(key),
            lambda: slot_params_dirt(False),
            slot_id=call_id,
        )
        manager = expression.call_site_context_manager
        expression.apply_dirt_sink(DM()).evaluate()

    def accepted() -> list[Any]:
        return [item.key for item in root.debug_mount_advertisements()]

    result: dict[str, Any] = {}
    with root.pass_scope():
        with root.container_call(container_id, native_section) as container:
            evaluate(container, "a")
        result["provisional"] = accepted()
    retained = manager.iter_current()[0].binding.binding
    result["initial"] = accepted()
    result["ui_anchor"] = root.debug_ui()[0].children[0].key
    advert = root.debug_mount_advertisements()[0]
    result["provenance"] = [
        advert.source_slot_id == call_id,
        advert.surface_owner_id == container_id,
        advert.mount_owner_id == container_id,
    ]
    try:
        with root.pass_scope():
            with root.container_call(container_id, native_section) as container:
                evaluate(container, "discard")
            result["pending"] = accepted()
            raise ValueError("parent failed")
    except ValueError:
        pass
    result["discarded"] = accepted()
    with root.pass_scope():
        with root.container_call(container_id, native_section) as container:
            evaluate(container, "superseded")
            evaluate(container, "latest")
    result["latest"] = accepted()
    result["retained_snapshot"] = retained.retained_advertisement().key
    with root.pass_scope():
        with root.container_call(container_id, native_section) as container:
            evaluate(container, "one", 2)
            evaluate(container, "two", 3)
    result["scoped_call_sites"] = accepted()
    result["scoped_anchors"] = [child.key for child in root.debug_ui()[0].children]
    with root.pass_scope():
        with root.container_call(container_id, native_section):
            pass
    result["expressions_omitted"] = [accepted(), list(root.debug_ui()[0].children)]
    with root.pass_scope():
        pass
    result["container_omitted"] = [accepted(), list(root.debug_ui())]
    return result


if __name__ == "__main__":
    print(json.dumps(characterize(), sort_keys=True, indent=2))
