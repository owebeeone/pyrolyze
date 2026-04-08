from __future__ import annotations

from pyrolyze.runtime import context_lcm as runtime


module_registry = runtime.ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.test_runtime_context_lcm_phase5")


def _slot(index: int) -> runtime.SlotId:
    return runtime.SlotId(_MODULE_ID, index, line_no=100 + index)


def _root() -> runtime.RenderContext:
    root = runtime.RenderContext()
    root.begin_pass()
    return root


def test_context_lcm_exports_component_call_slot_context_override() -> None:
    assert runtime.ComponentCallSlotContext.__module__ == "pyrolyze.runtime.context_lcm"


def test_component_call_slot_context_commit_owned_event_handlers_commits_seen_children() -> None:
    root = _root()
    slot = runtime.ComponentCallSlotContext(render_context=root, parent=root, slot_id=_slot(1))
    child_slot_id = _slot(2)
    child = runtime.EventHandlerSlotContext(render_context=root, parent=slot, slot_id=child_slot_id)
    slot._children[child_slot_id] = child

    calls: list[str] = []
    child.stage_callback(callback=lambda: calls.append("pressed"), dirty=True)
    child.seen_in_pass = True
    slot._pass_owned_event_handler_order = ()

    slot.commit_owned_event_handlers()
    dispatch = child._dispatch_callable()
    dispatch()

    assert calls == ["pressed"]
    assert slot._pass_owned_event_handler_order == ()

    root.rollback_pass()


def test_component_call_slot_context_dispose_child_context_clears_owned_runtime() -> None:
    root = _root()
    slot = runtime.ComponentCallSlotContext(render_context=root, parent=root, slot_id=_slot(3))
    child = runtime.RenderContext(
        owner_slot=slot,
        scheduler_root=root._scheduler_root,
        authored_app_context_lookup=root._authored_app_context_lookup,
    )
    slot.child_context = child
    slot.pending_dirty_state = runtime.dirtyof(value=True)
    slot._committed_ui = (runtime.UIElement(kind="div", props={}, children=(), call_site_id=None, slot_id=None),)

    slot._dispose_child_context()

    assert slot.child_context is None
    assert slot.pending_dirty_state is None
    assert slot._committed_ui == ()
