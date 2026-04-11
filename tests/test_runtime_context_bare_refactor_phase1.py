from __future__ import annotations

import pytest
from pyrolyze.api import MountSelector, PyrolyzeMountAdvertisementRequest, SlotSelector, UIElement

from pyrolyze.runtime.context_bare_refactor import (
    AppContextKey,
    AppContextOverrideSlotContext,
    AppContextOverrideStructureError,
    ComponentCallSlotContext,
    ContainerSlotContext,
    DirectiveSlotContext,
    EventHandlerSlotContext,
    LeafSlotContext,
    MountAdvertisementContextError,
    ModuleId,
    RenderContext,
    SlotRuntimeContext,
    SlotCallSlotContext,
    SlotContext,
    SlotExprSlotContext,
    SlotId,
    dirtyof,
)


def _slot(index: int) -> SlotId:
    return SlotId(ModuleId("tests.bare_refactor"), index)


_THEME_KEY = AppContextKey("theme", factory=lambda _host: "default-theme")
_LOCALE_KEY = AppContextKey("locale", factory=lambda _host: "en-AU")


def test_slot_context_registers_with_parent_and_render_context() -> None:
    root = RenderContext()
    slot = SlotContext(render_context=root, parent=root, slot_id=_slot(1))

    assert root._slots_by_id[slot.slot_id] is slot
    assert root.debug_children_of() == (slot.slot_id,)
    assert slot.current_slot_id() == slot.slot_id


def test_slot_context_visit_self_and_dirty_requires_active_scope() -> None:
    root = RenderContext()
    slot = LeafSlotContext(render_context=root, parent=root, slot_id=_slot(2))

    with pytest.raises(RuntimeError, match="scope is not active"):
        slot.visit_self_and_dirty()

    slot._begin_scope_pass()
    assert slot.visit_self_and_dirty() is True


def test_slot_context_deactivate_unlinks_from_parent_and_root() -> None:
    root = RenderContext()
    slot = SlotContext(render_context=root, parent=root, slot_id=_slot(3))

    slot.deactivate()

    assert slot.slot_id not in root._slots_by_id
    assert slot.slot_id not in root.debug_children_of()


def test_event_handler_slot_context_stages_commits_and_dispatches() -> None:
    root = RenderContext()
    slot = EventHandlerSlotContext(render_context=root, parent=root, slot_id=_slot(4))
    seen: list[str] = []

    dispatch = slot.stage_callback(callback=lambda: seen.append("called"), dirty=True)
    slot.commit_handler()
    dispatch()

    assert seen == ["called"]
    assert slot.staged_callback is None
    assert slot.committed_callback is not None


def test_event_handler_slot_context_rollback_clears_staged_callback() -> None:
    root = RenderContext()
    slot = EventHandlerSlotContext(render_context=root, parent=root, slot_id=_slot(5))

    slot.stage_callback(callback=lambda: None, dirty=True)
    slot.rollback_handler()

    assert slot.staged_callback is None
    assert slot.staged_key is None


def test_leaf_slot_context_invoke_tracks_arguments() -> None:
    root = RenderContext()
    slot = LeafSlotContext(render_context=root, parent=root, slot_id=_slot(6))

    result = slot.invoke(lambda a, *, b: (a, b), (1,), {"b": 2})

    assert result == (1, 2)
    assert slot.last_args == (1,)
    assert slot.last_kwargs == (("b", 2),)


def test_leaf_slot_context_invoke_native_commits_scope_on_success() -> None:
    root = RenderContext()
    slot = LeafSlotContext(render_context=root, parent=root, slot_id=_slot(7))

    result = slot.invoke_native(lambda ctx, value: None, (1,), {}, context_param="ctx")

    assert result is None
    assert slot._state_mgr.is_scope_active() is False


def test_leaf_slot_context_invoke_native_rolls_back_scope_on_error() -> None:
    root = RenderContext()
    slot = LeafSlotContext(render_context=root, parent=root, slot_id=_slot(8))

    def boom(_ctx: object) -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        slot.invoke_native(boom, (), {}, context_param="ctx")

    assert slot._state_mgr.is_scope_active() is False


def test_context_base_pass_scope_commits_on_clean_exit() -> None:
    root = RenderContext()

    with root.pass_scope():
        assert root._state_mgr.is_scope_active() is True

    assert root._state_mgr.is_scope_active() is False


def test_context_base_pass_scope_rolls_back_on_exception() -> None:
    root = RenderContext()

    with pytest.raises(ValueError, match="boom"):
        with root.pass_scope():
            raise ValueError("boom")

    assert root._state_mgr.is_scope_active() is False


def test_render_context_mount_runs_callback_and_debug_helpers_work() -> None:
    root = RenderContext()
    child = SlotContext(render_context=root, parent=root, slot_id=_slot(9))
    seen: list[str] = []

    root.mount(lambda: seen.append("mounted"))

    assert seen == ["mounted"]
    assert root.debug_is_active(child.slot_id) is True
    assert root.debug_children_of() == (child.slot_id,)
    assert root.debug_pending_boundaries() == ()
    assert root.debug_mount_advertisements() == ()
    assert root.committed_ui() == ()
    assert root.debug_ui() == ()


def test_slot_expr_runtime_locals_and_stage_merge() -> None:
    root = RenderContext()
    slot = SlotExprSlotContext(render_context=root, parent=root, slot_id=_slot(10))

    first = slot.runtime_locals("a")
    second = slot.runtime_locals("a")
    slot.stage_slot_expr_pass(
        visited_call_site_ids=("one", "two"),
        post_commit_callbacks=(lambda: None,),
    )
    slot.stage_slot_expr_pass(
        visited_call_site_ids=("two", "three"),
        post_commit_callbacks=(),
    )

    assert first is second
    assert slot._runtime_locals_by_slot_id["a"] is first
    assert slot._staged_call_site_ids == ("one", "two", "three")
    assert len(slot._staged_post_commit_callbacks) == 1


def test_slot_expr_append_commit_and_rollback_reset_staging() -> None:
    root = RenderContext()
    slot = SlotExprSlotContext(render_context=root, parent=root, slot_id=_slot(11))
    seen: list[str] = []

    slot.append_slot_expr_post_commit_callback(lambda: seen.append("done"))
    slot.stage_slot_expr_pass(visited_call_site_ids=("one",), post_commit_callbacks=())
    slot.commit_binding()
    assert seen == ["done"]
    assert slot._staged_call_site_ids == ()
    assert slot._staged_post_commit_callbacks == ()

    slot.stage_slot_expr_pass(visited_call_site_ids=("two",), post_commit_callbacks=())
    slot.append_slot_expr_post_commit_callback(lambda: seen.append("nope"))
    slot.rollback_binding()
    assert slot._staged_call_site_ids == ()
    assert slot._staged_post_commit_callbacks == ()
    assert seen == ["done"]


def test_slot_call_evaluate_injects_runtime_context_and_caches() -> None:
    root = RenderContext()
    slot = SlotCallSlotContext(render_context=root, parent=root, slot_id=_slot(12))

    def source(value: int, *, runtime: SlotRuntimeContext) -> int:
        _ = runtime
        return value + 1

    result = slot.evaluate(source, (2,), {})
    dirty, value = tuple(result)
    assert dirty is True
    assert value == 3

    second = slot.evaluate(source, (2,), {})
    dirty2, value2 = tuple(second)
    assert dirty2 is False
    assert value2 == 3


def test_slot_call_runtime_locals_invalidation_and_post_commit_queue() -> None:
    root = RenderContext()
    slot = SlotCallSlotContext(render_context=root, parent=root, slot_id=_slot(13))

    def source(*, runtime: SlotRuntimeContext) -> SlotRuntimeContext:
        return runtime

    runtime = slot._call_with_optional_runtime_context(slot._prepare_slot_call(source, (), {}))
    runtime.set_local("x", 1)
    runtime.invalidate()
    slot.enqueue_slot_call_post_commit(lambda: None)

    assert runtime.get_local("x") == 1
    assert root._queued_invalidations == [slot]
    assert len(root._post_commit_callbacks) == 1


def test_slot_call_publish_and_withdraw_mount_advertisement() -> None:
    root = RenderContext()
    slot = SlotCallSlotContext(render_context=root, parent=root, slot_id=_slot(14))

    request = PyrolyzeMountAdvertisementRequest(key="sel")
    with pytest.raises(MountAdvertisementContextError, match="native container owner"):
        slot.publish_slot_call_mount_advertisement(request)


def test_directive_slot_context_evaluate_and_pending_selectors() -> None:
    root = RenderContext()
    slot = DirectiveSlotContext(render_context=root, parent=root, slot_id=_slot(15))

    selectors = (MountSelector.named("x"),)
    result = slot.evaluate_directive(lambda: selectors, (), {})

    assert result == selectors
    assert slot.pending_selectors() == selectors


def test_directive_slot_context_tracks_pending_children() -> None:
    root = RenderContext()
    slot = DirectiveSlotContext(render_context=root, parent=root, slot_id=_slot(16))
    child = ContainerSlotContext(render_context=root, parent=slot, slot_id=_slot(17))
    child._state_mgr._committed_ui = (UIElement(kind="text", props={}, children=()),)

    assert slot.has_pending_emitted_children() is True


def test_component_call_slot_context_creates_child_context_and_commits_handlers() -> None:
    root = RenderContext()
    slot = ComponentCallSlotContext(render_context=root, parent=root, slot_id=_slot(18))
    event = EventHandlerSlotContext(render_context=root, parent=slot, slot_id=_slot(19))
    seen: list[str] = []

    event.stage_callback(callback=lambda: seen.append("called"), dirty=True)
    event.seen_in_pass = True

    def component(child_ctx: RenderContext, value: int) -> None:
        child_ctx._committed_ui = (UIElement(kind="text", props={"value": value}, children=()),)

    slot.invoke(component, (7,), {})
    event.seen_in_pass = True
    slot.commit_owned_event_handlers()
    event.dispatch()

    assert slot.child_context is not None
    assert slot._state_mgr._committed_ui == slot.child_context._state_mgr._committed_ui
    assert seen == ["called"]


def test_component_call_slot_context_rollback_owned_handlers_and_deactivate() -> None:
    root = RenderContext()
    slot = ComponentCallSlotContext(render_context=root, parent=root, slot_id=_slot(20))
    kept = EventHandlerSlotContext(render_context=root, parent=slot, slot_id=_slot(21))
    added = EventHandlerSlotContext(render_context=root, parent=slot, slot_id=_slot(22))

    slot._pass_owned_event_handler_order = (kept.slot_id,)
    kept.stage_callback(callback=lambda: None, dirty=True)
    added.stage_callback(callback=lambda: None, dirty=True)
    kept.seen_in_pass = True
    added.seen_in_pass = False

    slot.rollback_owned_event_handlers()
    assert added.slot_id not in slot._state_mgr._children
    assert kept.staged_callback is None

    def component(child_ctx: RenderContext) -> None:
        child_ctx._committed_ui = ()

    slot.invoke(component, (), {})
    assert slot.child_context is not None
    slot.deactivate()
    assert slot.child_context is None


def test_app_context_override_stage_commit_and_lookup() -> None:
    root = RenderContext()
    slot = AppContextOverrideSlotContext(render_context=root, parent=root, slot_id=_slot(23))

    slot.stage_override((_THEME_KEY,), ("dark",))
    slot._begin_scope_pass()

    assert slot.get_authored_app_context(_THEME_KEY) == "dark"
    slot._commit_scope_pass()

    assert slot.committed_values == ("dark",)
    assert slot.get_authored_app_context(_THEME_KEY) == "dark"


def test_app_context_override_none_value_tracks_parent_drip() -> None:
    root = RenderContext()
    parent = AppContextOverrideSlotContext(render_context=root, parent=root, slot_id=_slot(24))
    child = AppContextOverrideSlotContext(render_context=root, parent=parent, slot_id=_slot(25))

    parent.stage_override((_THEME_KEY,), ("parent-theme",))
    parent._begin_scope_pass()
    parent._commit_scope_pass()

    child.stage_override((_THEME_KEY,), (None,))
    child._begin_scope_pass()
    assert child.get_authored_app_context(_THEME_KEY) == "parent-theme"
    child._commit_scope_pass()
    assert child.get_authored_app_context(_THEME_KEY) == "parent-theme"


def test_app_context_override_rollback_restores_committed_values() -> None:
    root = RenderContext()
    slot = AppContextOverrideSlotContext(render_context=root, parent=root, slot_id=_slot(26))

    slot.stage_override((_THEME_KEY,), ("first",))
    slot._begin_scope_pass()
    slot._commit_scope_pass()

    slot.stage_override((_THEME_KEY,), ("second",))
    slot._begin_scope_pass()
    assert slot.get_authored_app_context(_THEME_KEY) == "second"
    slot._rollback_scope_pass()

    assert slot.committed_values == ("first",)
    assert slot.get_authored_app_context(_THEME_KEY) == "first"


def test_app_context_override_validates_structure() -> None:
    root = RenderContext()
    slot = AppContextOverrideSlotContext(render_context=root, parent=root, slot_id=_slot(27))

    with pytest.raises(AppContextOverrideStructureError, match="requires at least one key"):
        slot.stage_override((), ())

    with pytest.raises(AppContextOverrideStructureError, match="arity must match"):
        slot.stage_override((_THEME_KEY,), ())

    with pytest.raises(AppContextOverrideStructureError, match="duplicate key"):
        slot.stage_override((_THEME_KEY, _THEME_KEY), ("a", "b"))


def test_app_context_override_fixed_keys_cannot_change() -> None:
    root = RenderContext()
    slot = AppContextOverrideSlotContext(render_context=root, parent=root, slot_id=_slot(28))

    slot.stage_override((_THEME_KEY,), ("dark",))
    with pytest.raises(AppContextOverrideStructureError, match="fixed keys cannot change"):
        slot.stage_override((_LOCALE_KEY,), ("en",))


def test_app_context_override_authored_app_context_ref_tracks_committed_drip() -> None:
    root = RenderContext()
    slot = AppContextOverrideSlotContext(render_context=root, parent=root, slot_id=_slot(29))

    slot.stage_override((_THEME_KEY,), ("dark",))
    slot._begin_scope_pass()
    slot._commit_scope_pass()

    ref = slot.authored_app_context_ref(_THEME_KEY)
    assert ref.get() == "dark"
    assert ref.identity is slot._committed_key_states[_THEME_KEY].drip


def test_app_context_override_deactivate_clears_pending_and_key_state() -> None:
    root = RenderContext()
    slot = AppContextOverrideSlotContext(render_context=root, parent=root, slot_id=_slot(30))

    slot.stage_override((_THEME_KEY,), ("dark",))
    assert slot._committed_key_states
    slot.deactivate()

    assert slot._committed_key_states == {}
    assert slot._pending_values == ()
    assert slot._pending_initialized is False
