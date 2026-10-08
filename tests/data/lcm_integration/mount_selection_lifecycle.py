"""Detached mount advertisements and committed native-container surfaces."""

from __future__ import annotations

import json
from typing import Any

from pyrolyze.api import UIElement, advertise_mount
from pyrolyze.runtime.context_bare_refactor_lcm import ContextBase
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.mount_render import _enable_mount_render


def native_section(ctx: ContextBase) -> None:
    ctx._state_mgr.own_ui_state = (UIElement(kind="section", props={}),)


def characterize() -> dict[str, Any]:
    root = runtime.RenderContext()
    _enable_mount_render(root._state_mgr)
    module = runtime.ModuleId("tests.mount_selection")
    container_id = runtime.SlotId(module, 1)
    advert_id = runtime.SlotId(module, 2)
    result: dict[str, Any] = {}
    slot: Any = None
    container: Any = None

    def accepted() -> list[Any]:
        return [item.key for item in root.debug_mount_advertisements()]

    def select(section: Any, key: str) -> None:
        nonlocal slot
        slot = section._ensure_slot(advert_id, runtime.SlotCallSlotContext)
        slot.evaluate(advertise_mount, (key,), {})

    try:
        with root.pass_scope():
            with root.container_call(container_id, native_section) as container:
                select(container, "never_published")
            raise ValueError("initial render failed")
    except ValueError:
        pass
    result["failed_initial"] = [
        accepted(),
        container._state_mgr.current._committed_native_root,
        list(root.debug_ui()),
    ]

    with root.pass_scope():
        with root.container_call(container_id, native_section) as container:
            select(container, "a")
        result["provisional"] = accepted()
        result["provisional_native_root"] = (
            container._state_mgr.current._committed_native_root
        )
    retained = slot.binding
    result["initial"] = accepted()
    result["native_root"] = container._state_mgr.current._committed_native_root
    result["ui_anchor"] = root.debug_ui()[0].children[0].key
    advert = root.debug_mount_advertisements()[0]
    result["provenance"] = [
        advert.source_slot_id == slot.slot_id,
        advert.surface_owner_id == container.slot_id,
        advert.mount_owner_id == container.slot_id,
    ]
    try:
        with root.pass_scope():
            with root.container_call(container_id, native_section) as container:
                select(container, "failed")
            result["pending_replacement"] = accepted()
            raise ValueError("parent failed")
    except ValueError:
        pass
    result["failed_replacement"] = accepted()
    with root.pass_scope():
        with root.container_call(container_id, native_section) as container:
            select(container, "b")
    result["replacement"] = accepted()
    result["retained_snapshot"] = retained.retained_advertisement().key
    try:
        with root.pass_scope():
            with root.container_call(container_id, native_section) as container:
                slot.deactivate()
            raise ValueError("removal failed")
    except ValueError:
        pass
    result["failed_removal"] = accepted()
    with root.pass_scope():
        with root.container_call(container_id, native_section) as container:
            slot.deactivate()
    result["removed"] = accepted()
    with root.pass_scope():
        with root.container_call(container_id, native_section) as container:
            select(container, "superseded")
            select(container, "latest")
    result["latest"] = accepted()
    with root.pass_scope():
        pass
    result["container_omitted"] = [accepted(), list(root.debug_ui())]
    result["ready"] = root._state_mgr._field_only_completion.last.reuse_ready
    return result


if __name__ == "__main__":
    print(json.dumps(characterize(), indent=2, sort_keys=True))
