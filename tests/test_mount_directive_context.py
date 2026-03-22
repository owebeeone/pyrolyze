from __future__ import annotations

import pytest

from pyrolyze.api import MountDirective, MountSelector, UIElement, no_emit, validate_mount_selectors
from pyrolyze.runtime.context import ModuleRegistry, RenderContext, SlotId


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.mount_directive_context")

_DIRECTIVE_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_OUTER_DIRECTIVE_SLOT = SlotId(_MODULE_ID, 2, line_no=11)
_INNER_DIRECTIVE_SLOT = SlotId(_MODULE_ID, 3, line_no=12)
def test_open_directive_commits_retained_mount_directive() -> None:
    ctx = RenderContext()
    menu = MountSelector.named("menu")

    with ctx.pass_scope():
        assert ctx.visit_slot_and_dirty(_DIRECTIVE_SLOT) is True
        with ctx.open_directive(_DIRECTIVE_SLOT, validate_mount_selectors, menu) as mount_ctx:
            mount_ctx.call_native(UIElement, kind="badge", props={"text": "File"})

    assert ctx.debug_ui() == (
        MountDirective(
            selectors=(menu,),
            children=(UIElement(kind="badge", props={"text": "File"}),),
        ),
    )
    directive = ctx.debug_ui()[0]
    assert isinstance(directive, MountDirective)
    assert directive.slot_id == _DIRECTIVE_SLOT


def test_open_directive_preserves_nested_lexical_structure() -> None:
    ctx = RenderContext()
    outer = MountSelector.named("menu")
    inner = MountSelector.named("corner_widget")(corner="top_left")

    with ctx.pass_scope():
        assert ctx.visit_slot_and_dirty(_OUTER_DIRECTIVE_SLOT) is True
        with ctx.open_directive(
            _OUTER_DIRECTIVE_SLOT,
            validate_mount_selectors,
            outer,
        ) as outer_ctx:
            outer_ctx.call_native(UIElement, kind="badge", props={"text": "File"})
            with outer_ctx.open_directive(
                _INNER_DIRECTIVE_SLOT,
                validate_mount_selectors,
                inner,
            ) as inner_ctx:
                inner_ctx.call_native(UIElement, kind="badge", props={"text": "Edit"})

    assert ctx.debug_ui() == (
        MountDirective(
            selectors=(outer,),
            children=(
                UIElement(kind="badge", props={"text": "File"}),
                MountDirective(
                    selectors=(inner,),
                    children=(UIElement(kind="badge", props={"text": "Edit"}),),
                ),
            ),
        ),
    )


def test_open_directive_rollback_restores_prior_committed_tree() -> None:
    ctx = RenderContext()
    menu = MountSelector.named("menu")
    widget = MountSelector.named("widget")

    with ctx.pass_scope():
        with ctx.open_directive(_DIRECTIVE_SLOT, validate_mount_selectors, menu) as mount_ctx:
            mount_ctx.call_native(UIElement, kind="badge", props={"text": "File"})

    assert ctx.debug_ui() == (
        MountDirective(
            selectors=(menu,),
            children=(UIElement(kind="badge", props={"text": "File"}),),
        ),
    )

    with pytest.raises(RuntimeError, match="boom"):
        with ctx.pass_scope():
            with ctx.open_directive(_DIRECTIVE_SLOT, validate_mount_selectors, widget) as mount_ctx:
                mount_ctx.call_native(UIElement, kind="badge", props={"text": "View"})
                raise RuntimeError("boom")

    assert ctx.debug_ui() == (
        MountDirective(
            selectors=(menu,),
            children=(UIElement(kind="badge", props={"text": "File"}),),
        ),
    )


def test_open_directive_rejects_no_emit_when_children_are_emitted() -> None:
    ctx = RenderContext()

    with pytest.raises(RuntimeError, match="no_emit"):
        with ctx.pass_scope():
            with ctx.open_directive(_DIRECTIVE_SLOT, validate_mount_selectors, no_emit) as mount_ctx:
                mount_ctx.call_native(UIElement, kind="badge", props={"text": "Hidden"})

    assert ctx.debug_ui() == ()
