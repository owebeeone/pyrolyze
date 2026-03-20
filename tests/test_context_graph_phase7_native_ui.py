from __future__ import annotations

import pytest

from pyrolyze.api import UIElement
from pyrolyze.runtime.context import (
    ContextBase,
    ModuleRegistry,
    RenderContext,
    SlotId,
    dirtyof,
)


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.context_graph_phase7_native_ui")

_SECTION_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_BADGE_SLOT = SlotId(_MODULE_ID, 2, line_no=11)
_BUTTON_SLOT = SlotId(_MODULE_ID, 3, line_no=12)
_NONE_SLOT = SlotId(_MODULE_ID, 4, line_no=13)
_BAD_SLOT = SlotId(_MODULE_ID, 5, line_no=14)
_DOUBLE_SECTION_SLOT = SlotId(_MODULE_ID, 6, line_no=15)
_BUILTIN_LEAF_SLOT = SlotId(_MODULE_ID, 7, line_no=16)
_BUILTIN_CONTAINER_SLOT = SlotId(_MODULE_ID, 8, line_no=17)


def _pyr_badge(ctx: ContextBase, text: str, *, tone: str) -> None:
    ctx.call_native(
        UIElement,
        kind="badge",
        props={"text": text, "tone": tone},
    )


def _pyr_button(
    ctx: ContextBase,
    label: str,
    *,
    enabled: bool,
    meta: dict[str, object],
) -> None:
    ctx.call_native(
        UIElement,
        kind="button",
        props={
            "label": label,
            "enabled": enabled,
            "meta": meta,
        },
    )


def _pyr_section(
    ctx: ContextBase,
    title: str,
    *,
    accent: str,
) -> None:
    ctx.call_native(
        UIElement,
        kind="section",
        props={"title": title, "accent": accent},
    )


def _pyr_none(ctx: ContextBase) -> None:
    ctx.call_native(lambda: None)


def _pyr_invalid(ctx: ContextBase) -> None:
    ctx.call_native(lambda: "not-a-ui-element")


def _pyr_double_root(ctx: ContextBase) -> None:
    ctx.call_native(UIElement, kind="section", props={"title": "One"})
    ctx.call_native(UIElement, kind="section", props={"title": "Two"})


def _make_toolbar_program() -> callable:
    def _pyr_toolbar(ctx: RenderContext, __pyr_dirty_state, active: bool) -> None:
        with ctx.pass_scope():
            if __pyr_dirty_state.active or ctx.visit_slot_and_dirty(_SECTION_SLOT):
                with ctx.container_call(
                    _SECTION_SLOT,
                    _pyr_section,
                    "Toolbar",
                    accent="cyan",
                ) as section_ctx:
                    if __pyr_dirty_state.active or section_ctx.visit_slot_and_dirty(_BADGE_SLOT):
                        section_ctx.leaf_call(
                            _BADGE_SLOT,
                            _pyr_badge,
                            "Ready" if active else "Paused",
                            tone="info",
                        )

                    if __pyr_dirty_state.active or section_ctx.visit_slot_and_dirty(_BUTTON_SLOT):
                        section_ctx.leaf_call(
                            _BUTTON_SLOT,
                            _pyr_button,
                            "Run",
                            enabled=not active,
                            meta={
                                "tags": ["primary", "toolbar"],
                                "status": {"active": active},
                            },
                        )

    return _pyr_toolbar


def test_native_ui_helpers_build_committed_tree_and_retain_on_stable_pass() -> None:
    ctx = RenderContext()
    pyr_toolbar = _make_toolbar_program()

    pyr_toolbar(ctx, dirtyof(active=True), True)

    assert ctx.debug_ui() == (
        UIElement(
            kind="section",
            props={"title": "Toolbar", "accent": "cyan"},
            children=(
                UIElement(kind="badge", props={"text": "Ready", "tone": "info"}),
                UIElement(
                    kind="button",
                    props={
                        "label": "Run",
                        "enabled": False,
                        "meta": {
                            "tags": ["primary", "toolbar"],
                            "status": {"active": True},
                        },
                    },
                ),
            ),
        ),
    )

    pyr_toolbar(ctx, dirtyof(active=False), True)

    assert ctx.debug_ui() == (
        UIElement(
            kind="section",
            props={"title": "Toolbar", "accent": "cyan"},
            children=(
                UIElement(kind="badge", props={"text": "Ready", "tone": "info"}),
                UIElement(
                    kind="button",
                    props={
                        "label": "Run",
                        "enabled": False,
                        "meta": {
                            "tags": ["primary", "toolbar"],
                            "status": {"active": True},
                        },
                    },
                ),
            ),
        ),
    )


def test_call_native_none_is_ignored_and_invalid_result_raises() -> None:
    ctx = RenderContext()

    with ctx.pass_scope():
        assert ctx.visit_slot_and_dirty(_NONE_SLOT) is True
        ctx.leaf_call(_NONE_SLOT, _pyr_none)

    assert ctx.debug_ui() == ()

    with pytest.raises(TypeError, match="UIElement or None"):
        with ctx.pass_scope():
            assert ctx.visit_slot_and_dirty(_BAD_SLOT) is True
            ctx.leaf_call(_BAD_SLOT, _pyr_invalid)

    assert ctx.debug_ui() == ()


def test_container_native_helper_requires_exactly_one_root_element() -> None:
    ctx = RenderContext()

    with pytest.raises(RuntimeError, match="exactly one root UIElement"):
        with ctx.pass_scope():
            assert ctx.visit_slot_and_dirty(_DOUBLE_SECTION_SLOT) is True
            with ctx.container_call(
                _DOUBLE_SECTION_SLOT,
                _pyr_double_root,
            ):
                pass

    assert ctx.debug_ui() == ()


def test_failed_native_rerun_rolls_back_to_last_committed_ui() -> None:
    ctx = RenderContext()

    with ctx.pass_scope():
        assert ctx.visit_slot_and_dirty(_BADGE_SLOT) is True
        ctx.leaf_call(
            _BADGE_SLOT,
            _pyr_badge,
            "Ready",
            tone="info",
        )

    assert ctx.debug_ui() == (
        UIElement(kind="badge", props={"text": "Ready", "tone": "info"}),
    )

    with pytest.raises(TypeError, match="UIElement or None"):
        with ctx.pass_scope():
            assert ctx.visit_slot_and_dirty(_BADGE_SLOT) is False
            ctx.leaf_call(_BADGE_SLOT, _pyr_invalid)

    assert ctx.debug_ui() == (
        UIElement(kind="badge", props={"text": "Ready", "tone": "info"}),
    )


def test_leaf_call_accepts_builtin_function_without_attribute_cache_support() -> None:
    ctx = RenderContext()

    with ctx.pass_scope():
        assert ctx.visit_slot_and_dirty(_BUILTIN_LEAF_SLOT) is True
        result = ctx.leaf_call(_BUILTIN_LEAF_SLOT, len, [1, 2, 3])

    assert result == 3
    assert ctx.debug_ui() == ()


def test_container_call_accepts_builtin_function_without_attribute_cache_support() -> None:
    ctx = RenderContext()

    with ctx.pass_scope():
        assert ctx.visit_slot_and_dirty(_BUILTIN_CONTAINER_SLOT) is True
        with ctx.container_call(_BUILTIN_CONTAINER_SLOT, len, [1, 2, 3]) as slot:
            slot.call_native(
                UIElement,
                kind="badge",
                props={"text": "Builtins supported", "tone": "info"},
            )

    assert ctx.debug_ui() == (
        UIElement(kind="badge", props={"text": "Builtins supported", "tone": "info"}),
    )


def test_leaf_call_tolerates_callable_with_invalid_signature_metadata() -> None:
    ctx = RenderContext()

    class _NoAttrBadSignatureLeaf:
        __slots__ = ()
        __signature__ = "invalid"

        def __call__(self, values: list[int]) -> int:
            return len(values)

    with ctx.pass_scope():
        assert ctx.visit_slot_and_dirty(_BUILTIN_LEAF_SLOT) is True
        result = ctx.leaf_call(_BUILTIN_LEAF_SLOT, _NoAttrBadSignatureLeaf(), [1, 2, 3])

    assert result == 3
    assert ctx.debug_ui() == ()
