from __future__ import annotations

from contextlib import contextmanager
from typing import Callable

import pytest

from pyrolyze.api import (
    CallFromNonPyrolyzeContext,
    ComponentMetadata,
    ComponentRef,
    pyrolyze_component_ref,
)
from pyrolyze.runtime.context import CompValue, ModuleRegistry, RenderContext, SlotId


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.context_graph_phase5_component_call")

_NEUTRAL_BADGE_LEAF_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_INFO_BADGE_LEAF_SLOT = SlotId(_MODULE_ID, 2, line_no=20)
_PICK_BADGE_SLOT = SlotId(_MODULE_ID, 3, line_no=30)
_SECTION_SLOT = SlotId(_MODULE_ID, 4, line_no=31)
_CHOSEN_COMPONENT_SLOT = SlotId(_MODULE_ID, 5, line_no=32)
_FALLBACK_PICK_SLOT = SlotId(_MODULE_ID, 6, line_no=33)
_FALLBACK_COMPONENT_SLOT = SlotId(_MODULE_ID, 7, line_no=34)
_DIRECT_COMPONENT_SLOT = SlotId(_MODULE_ID, 8, line_no=40)


def _make_component_program(log: list[tuple[object, ...]]):
    @contextmanager
    def _section(title: str, *, accent: str):
        log.append(("section.enter", title, accent))
        try:
            yield
        finally:
            log.append(("section.exit", title, accent))

    def _badge(text: str, *, tone: str) -> None:
        log.append(("badge", text, tone))

    def __pyr_neutral_badge(ctx: RenderContext, text: CompValue[str]) -> None:
        log.append(("render", "neutral", text.value, text.dirty))
        with ctx.pass_scope():
            if text.dirty or ctx.visit_slot_and_dirty(_NEUTRAL_BADGE_LEAF_SLOT):
                ctx.leaf_call(
                    _NEUTRAL_BADGE_LEAF_SLOT,
                    ctx.literal(_badge),
                    text,
                    tone=ctx.literal("neutral"),
                )

    @pyrolyze_component_ref(
        ComponentMetadata("neutral_badge", __pyr_neutral_badge)
    )
    def neutral_badge(text: str) -> None:
        raise CallFromNonPyrolyzeContext("neutral_badge")

    def __pyr_info_badge(ctx: RenderContext, text: CompValue[str]) -> None:
        log.append(("render", "info", text.value, text.dirty))
        with ctx.pass_scope():
            if text.dirty or ctx.visit_slot_and_dirty(_INFO_BADGE_LEAF_SLOT):
                ctx.leaf_call(
                    _INFO_BADGE_LEAF_SLOT,
                    ctx.literal(_badge),
                    text,
                    tone=ctx.literal("info"),
                )

    @pyrolyze_component_ref(
        ComponentMetadata("info_badge", __pyr_info_badge)
    )
    def info_badge(text: str) -> None:
        raise CallFromNonPyrolyzeContext("info_badge")

    def pick_badge(kind: str) -> ComponentRef[[str]]:
        return info_badge if kind == "info" else neutral_badge

    def __pyr_badge_panel(ctx: RenderContext, kind: CompValue[str], text: CompValue[str]) -> None:
        with ctx.pass_scope():
            chosen = ctx.call_plain(
                _PICK_BADGE_SLOT,
                pick_badge,
                kind,
            )

            if chosen.dirty or text.dirty or ctx.visit_slot_and_dirty(_SECTION_SLOT):
                with ctx.container_call(
                    _SECTION_SLOT,
                    _section,
                    ctx.literal("Badges"),
                    accent=ctx.literal("slate"),
                ) as section_ctx:
                    if chosen.dirty or text.dirty or section_ctx.visit_slot_and_dirty(_CHOSEN_COMPONENT_SLOT):
                        section_ctx.component_call(
                            _CHOSEN_COMPONENT_SLOT,
                            chosen,
                            text,
                        )

                    fallback = section_ctx.call_plain(
                        _FALLBACK_PICK_SLOT,
                        pick_badge,
                        ctx.literal("neutral"),
                    )

                    if fallback.dirty or section_ctx.visit_slot_and_dirty(_FALLBACK_COMPONENT_SLOT):
                        section_ctx.component_call(
                            _FALLBACK_COMPONENT_SLOT,
                            fallback,
                            ctx.literal("fallback"),
                        )

    def __pyr_direct_component(
        ctx: RenderContext,
        component: CompValue[ComponentRef[[str]]],
        text: CompValue[str],
        refresh: CompValue[int],
    ) -> None:
        with ctx.pass_scope():
            if refresh.dirty or component.dirty or text.dirty or ctx.visit_slot_and_dirty(_DIRECT_COMPONENT_SLOT):
                ctx.component_call(
                    _DIRECT_COMPONENT_SLOT,
                    component,
                    text,
                )

    return {
        "badge_panel": __pyr_badge_panel,
        "direct_component": __pyr_direct_component,
        "neutral_badge": neutral_badge,
        "info_badge": info_badge,
    }


def test_component_call_mounts_child_component_from_helper_returned_component_ref() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    program = _make_component_program(log)

    program["badge_panel"](
        ctx,
        CompValue("info", dirty=True),
        CompValue("Hello", dirty=True),
    )

    assert log == [
        ("section.enter", "Badges", "slate"),
        ("render", "info", "Hello", True),
        ("badge", "Hello", "info"),
        ("render", "neutral", "fallback", True),
        ("badge", "fallback", "neutral"),
        ("section.exit", "Badges", "slate"),
    ]

    program["badge_panel"](
        ctx,
        CompValue("info", dirty=False),
        CompValue("Hello", dirty=False),
    )

    assert log == [
        ("section.enter", "Badges", "slate"),
        ("render", "info", "Hello", True),
        ("badge", "Hello", "info"),
        ("render", "neutral", "fallback", True),
        ("badge", "fallback", "neutral"),
        ("section.exit", "Badges", "slate"),
    ]


def test_component_call_rerenders_existing_child_context_when_identity_is_stable() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    program = _make_component_program(log)

    program["direct_component"](
        ctx,
        CompValue(program["neutral_badge"], dirty=True),
        CompValue("Hello", dirty=True),
        CompValue(1, dirty=True),
    )
    log.clear()

    program["direct_component"](
        ctx,
        CompValue(program["neutral_badge"], dirty=False),
        CompValue("Hello", dirty=False),
        CompValue(1, dirty=True),
    )

    assert log == [
        ("render", "neutral", "Hello", False),
    ]


def test_component_call_replaces_child_context_when_component_identity_changes() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    program = _make_component_program(log)

    program["direct_component"](
        ctx,
        CompValue(program["neutral_badge"], dirty=True),
        CompValue("Hello", dirty=True),
        CompValue(1, dirty=True),
    )
    log.clear()

    program["direct_component"](
        ctx,
        CompValue(program["info_badge"], dirty=True),
        CompValue("Hello", dirty=False),
        CompValue(2, dirty=True),
    )

    assert log == [
        ("render", "info", "Hello", False),
        ("badge", "Hello", "info"),
    ]

    log.clear()
    program["direct_component"](
        ctx,
        CompValue(program["neutral_badge"], dirty=True),
        CompValue("Hello", dirty=False),
        CompValue(3, dirty=True),
    )

    assert log == [
        ("render", "neutral", "Hello", False),
        ("badge", "Hello", "neutral"),
    ]


def test_component_call_rejects_undecorated_callable() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    program = _make_component_program(log)

    def not_a_component(text: str) -> None:
        log.append(("plain", text))

    with pytest.raises(TypeError, match="ComponentRef"):
        program["direct_component"](
            ctx,
            CompValue(not_a_component, dirty=True),
            CompValue("Hello", dirty=True),
            CompValue(1, dirty=True),
        )
