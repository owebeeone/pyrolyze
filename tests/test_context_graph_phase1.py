from __future__ import annotations

import pytest

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime.context import (
    ModuleRegistry,
    RenderContext,
    SlotId,
    SlotOwnershipError,
    dirtyof,
)
from pyrolyze_testsupport import pyrolize_test_wrap


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.context_graph_phase1")


def _make_compiled_welcome_program(log: list[tuple[object, ...]], *, conditional: bool = False):
    def _format_title(name: str) -> str:
        log.append(("format_title", name))
        return f"Hello {name}"

    namespace = load_transformed_namespace(
        '''
from pyrolyze.api import UIElement, call_native, component, pyrolyze, slotted
from pyrolyze.runtime.context import ContextBase

def section(ctx: ContextBase, title, *, accent):
    LOG.append(("section", title, accent))
    ctx.call_native(UIElement, kind="section", props={"title": title, "accent": accent})

@pyrolyze
def badge(text, *, tone):
    LOG.append(("badge", text, tone))
    call_native(UIElement)(kind="badge", props={"text": text, "tone": tone})

@pyrolyze
def welcome(name):
    title = slotted(format_title, name)
    with component(section, "Greeting", accent="blue"):
        badge(title, tone="info")

@pyrolyze
def welcome_conditional(name, show_badge):
    title = slotted(format_title, name)
    with component(section, "Greeting", accent="blue"):
        if show_badge:
            badge(title, tone="info")
''',
        module_name="tests.context_graph_phase1.compiled_welcome",
        globals_dict={"LOG": log, "format_title": _format_title},
    )
    return namespace["welcome_conditional" if conditional else "welcome"]._pyrolyze_meta._func




def test_first_pass_executes_and_stable_second_pass_retains_subtree() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    pyr_welcome = _make_compiled_welcome_program(log)

    pyr_welcome(ctx, dirtyof(name=True), "Ada")

    assert log == [
        ("format_title", "Ada"),
        ("section", "Greeting", "blue"),
        ("badge", "Hello Ada", "info"),
    ]
    children = ctx.debug_children_of()
    assert len(children) == 2
    section_slot = children[1]
    section_children = ctx.debug_children_of(section_slot)
    assert section_children
    published = ctx.committed_ui()
    assert len(published) == 1
    assert published[0].kind == "section"

    pyr_welcome(ctx, dirtyof(name=False), "Ada")

    assert log == [
        ("format_title", "Ada"),
        ("section", "Greeting", "blue"),
        ("badge", "Hello Ada", "info"),
    ]
    assert ctx.debug_children_of() == children
    assert ctx.debug_children_of(section_slot) == section_children
    assert ctx.committed_ui()[0] is published[0]


def test_parent_rerun_deactivates_previously_active_child_when_branch_is_omitted() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    pyr_welcome_conditional = _make_compiled_welcome_program(log, conditional=True)

    pyr_welcome_conditional(
        ctx,
        dirtyof(name=True, show_badge=True),
        "Ada",
        True,
    )
    section_slot = ctx.debug_children_of()[1]
    assert ctx.committed_ui()[0].children[0].kind == "badge"

    pyr_welcome_conditional(
        ctx,
        dirtyof(name=True, show_badge=True),
        "Bea",
        False,
    )

    assert ("badge", "Hello Bea", "info") not in log
    assert ctx.committed_ui()[0].children == ()
    assert ctx.debug_children_of()[1] == section_slot


def test_first_visit_is_dirty_and_later_stable_visit_is_clean() -> None:
    ctx = RenderContext()
    slot = SlotId(_MODULE_ID, 99, line_no=99)

    with ctx.pass_scope():
        assert ctx.visit_slot_and_dirty(slot) is True

    with ctx.pass_scope():
        assert ctx.visit_slot_and_dirty(slot) is False


def test_pass_scope_rolls_back_when_body_raises() -> None:
    ctx = RenderContext()
    slot = SlotId(_MODULE_ID, 100, line_no=100)

    with pytest.raises(RuntimeError, match="boom"):
        with ctx.pass_scope():
            assert ctx.visit_slot_and_dirty(slot) is True
            raise RuntimeError("boom")

    with ctx.pass_scope():
        assert ctx.visit_slot_and_dirty(slot) is True


def test_child_visitation_must_use_the_owning_container_context() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    pyr_welcome = _make_compiled_welcome_program(log)

    pyr_welcome(ctx, dirtyof(name=True), "Ada")
    section_slot = ctx.debug_children_of()[1]
    badge_slot = ctx.debug_children_of(section_slot)[0]

    with pytest.raises(SlotOwnershipError):
        with ctx.pass_scope():
            ctx.component_call(badge_slot, pyrolize_test_wrap(lambda: None), dirty_state=dirtyof())


def test_skipped_clean_subtree_preserves_event_handler_slots() -> None:
    ctx = RenderContext()
    events: list[str] = []
    captured_dispatch: dict[str, object] = {}

    namespace = load_transformed_namespace(
        '''
from pyrolyze.api import UIElement, call_native, component, pyrolyze
from pyrolyze.runtime.context import ContextBase

def panel_scope(ctx: ContextBase):
    ctx.call_native(UIElement, kind="panel", props={})

@pyrolyze
def button(*, on_clicked):
    CAPTURED["value"] = on_clicked
    call_native(UIElement)(kind="button", props={"on_clicked": on_clicked})

@pyrolyze
def counter_ui(value):
    call_native(UIElement)(kind="counter", props={"value": value})

@pyrolyze
def panel(counter):
    with component(panel_scope):
        counter_ui(counter)
        button(on_clicked=lambda: EVENTS.append("clicked"))
''',
        module_name="tests.context_graph_phase1.compiled_events",
        globals_dict={"EVENTS": events, "CAPTURED": captured_dispatch},
    )
    render = namespace["panel"]._pyrolyze_meta._func
    render(ctx, dirtyof(counter=True), 1)
    dispatch = captured_dispatch["value"]
    assert callable(dispatch)
    dispatch()
    assert events == ["clicked"]

    render(ctx, dirtyof(counter=True), 2)

    assert captured_dispatch["value"] is dispatch
    dispatch = captured_dispatch["value"]
    assert callable(dispatch)
    dispatch()
    assert events == ["clicked", "clicked"]
