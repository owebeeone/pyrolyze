from __future__ import annotations

from contextlib import contextmanager

import pytest

from pyrolyze.api import (
    CallFromNonPyrolyzeContext,
    ComponentMetadata,
    ComponentRef,
    UIElement,
    pyrolyze_component_ref,
)
from pyrolyze.runtime.context import DirtyStateContext, ModuleRegistry, RenderContext, SlotId, dirtyof
from tests.slot_expr_test_utils import eval_single_slot_expr


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
_DIRECT_CONTAINER_SLOT = SlotId(_MODULE_ID, 9, line_no=41)
_DIRECT_CONTAINER_HANDLER_SLOT = SlotId(_MODULE_ID, 10, line_no=42)
_DIRECT_CONTAINER_INNER_LEAF_SLOT = SlotId(_MODULE_ID, 11, line_no=43)


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

    def __pyr_neutral_badge(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
        text: str,
    ) -> None:
        log.append(("render", "neutral", text, __pyr_dirty_state.text))
        with ctx.pass_scope():
            if __pyr_dirty_state.text or ctx.visit_slot_and_dirty(_NEUTRAL_BADGE_LEAF_SLOT):
                ctx.leaf_call(
                    _NEUTRAL_BADGE_LEAF_SLOT,
                    _badge,
                    text,
                    tone="neutral",
                )

    @pyrolyze_component_ref(
        ComponentMetadata("neutral_badge", __pyr_neutral_badge)
    )
    def neutral_badge(text: str) -> None:
        raise CallFromNonPyrolyzeContext("neutral_badge")

    def __pyr_info_badge(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
        text: str,
    ) -> None:
        log.append(("render", "info", text, __pyr_dirty_state.text))
        with ctx.pass_scope():
            if __pyr_dirty_state.text or ctx.visit_slot_and_dirty(_INFO_BADGE_LEAF_SLOT):
                ctx.leaf_call(
                    _INFO_BADGE_LEAF_SLOT,
                    _badge,
                    text,
                    tone="info",
                )

    @pyrolyze_component_ref(
        ComponentMetadata("info_badge", __pyr_info_badge)
    )
    def info_badge(text: str) -> None:
        raise CallFromNonPyrolyzeContext("info_badge")

    def pick_badge(kind: str) -> ComponentRef[[str]]:
        return info_badge if kind == "info" else neutral_badge

    def __pyr_badge_panel(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
        kind: str,
        text: str,
    ) -> None:
        with ctx.pass_scope():
            __pyr_chosen_dirty, chosen = eval_single_slot_expr(
                ctx,
                __pyr_dirty_state,
                _PICK_BADGE_SLOT,
                pick_badge,
                kind,
                args_dirty=(__pyr_dirty_state.kind,),
                result_name="chosen",
            )

            if __pyr_chosen_dirty or __pyr_dirty_state.text or ctx.visit_slot_and_dirty(_SECTION_SLOT):
                with ctx.container_call(
                    _SECTION_SLOT,
                    _section,
                    "Badges",
                    accent="slate",
                ) as section_ctx:
                    if (
                        __pyr_chosen_dirty
                        or __pyr_dirty_state.text
                        or section_ctx.visit_slot_and_dirty(_CHOSEN_COMPONENT_SLOT)
                    ):
                        section_ctx.component_call(
                            _CHOSEN_COMPONENT_SLOT,
                            chosen,
                            text,
                            dirty_state=dirtyof(text=__pyr_dirty_state.text),
                        )

                    __pyr_fallback_dirty, fallback = eval_single_slot_expr(
                        section_ctx,
                        dirtyof(),
                        _FALLBACK_PICK_SLOT,
                        pick_badge,
                        "neutral",
                        result_name="fallback",
                    )

                    if __pyr_fallback_dirty or section_ctx.visit_slot_and_dirty(_FALLBACK_COMPONENT_SLOT):
                        section_ctx.component_call(
                            _FALLBACK_COMPONENT_SLOT,
                            fallback,
                            "fallback",
                            dirty_state=dirtyof(text=True),
                        )

    def __pyr_direct_component(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
        component: ComponentRef[[str]],
        text: str,
        refresh: int,
    ) -> None:
        _ = refresh
        with ctx.pass_scope():
            if (
                __pyr_dirty_state.refresh
                or __pyr_dirty_state.component
                or __pyr_dirty_state.text
                or ctx.visit_slot_and_dirty(_DIRECT_COMPONENT_SLOT)
            ):
                ctx.component_call(
                    _DIRECT_COMPONENT_SLOT,
                    component,
                    text,
                    dirty_state=dirtyof(text=__pyr_dirty_state.text),
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
        dirtyof(kind=True, text=True),
        "info",
        "Hello",
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
        dirtyof(kind=False, text=False),
        "info",
        "Hello",
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
        dirtyof(component=True, text=True, refresh=True),
        program["neutral_badge"],
        "Hello",
        1,
    )
    log.clear()

    program["direct_component"](
        ctx,
        dirtyof(component=False, text=False, refresh=True),
        program["neutral_badge"],
        "Hello",
        1,
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
        dirtyof(component=True, text=True, refresh=True),
        program["neutral_badge"],
        "Hello",
        1,
    )
    log.clear()

    program["direct_component"](
        ctx,
        dirtyof(component=True, text=False, refresh=True),
        program["info_badge"],
        "Hello",
        2,
    )

    assert log == [
        ("render", "info", "Hello", False),
        ("badge", "Hello", "info"),
    ]

    log.clear()
    program["direct_component"](
        ctx,
        dirtyof(component=True, text=False, refresh=True),
        program["neutral_badge"],
        "Hello",
        3,
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
            dirtyof(component=True, text=True, refresh=True),
            not_a_component,
            "Hello",
            1,
        )


def _make_container_component_program(log: list[tuple[object, ...]]):
    def _body(text: str) -> None:
        log.append(("body", text))

    def __pyr_neutral_box(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
        title: str,
    ) -> None:
        log.append(("render-container", "neutral", title, __pyr_dirty_state.title))
        with ctx.pass_scope():
            ctx.call_native(
                UIElement,
                kind="box",
                props={"title": title, "tone": "neutral"},
            )

    @pyrolyze_component_ref(ComponentMetadata("neutral_box", __pyr_neutral_box))
    def neutral_box(title: str) -> None:
        raise CallFromNonPyrolyzeContext("neutral_box")

    def __pyr_info_box(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
        title: str,
    ) -> None:
        log.append(("render-container", "info", title, __pyr_dirty_state.title))
        with ctx.pass_scope():
            ctx.call_native(
                UIElement,
                kind="box",
                props={"title": title, "tone": "info"},
            )

    @pyrolyze_component_ref(ComponentMetadata("info_box", __pyr_info_box))
    def info_box(title: str) -> None:
        raise CallFromNonPyrolyzeContext("info_box")

    def __pyr_button_box(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
        label: str,
    ) -> None:
        with ctx.pass_scope():
            dispatch = ctx.event_handler(
                _DIRECT_CONTAINER_HANDLER_SLOT,
                dirty=__pyr_dirty_state.label,
                callback=lambda: log.append(("press", label)),
            )
            ctx.call_native(
                UIElement,
                kind="button",
                props={"label": label, "on_press": dispatch},
            )

    @pyrolyze_component_ref(ComponentMetadata("button_box", __pyr_button_box))
    def button_box(label: str) -> None:
        raise CallFromNonPyrolyzeContext("button_box")

    def render_container(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
        component: ComponentRef[[str]],
        title: str,
        refresh: int,
    ) -> None:
        _ = refresh
        with ctx.pass_scope():
            if (
                __pyr_dirty_state.refresh
                or __pyr_dirty_state.component
                or __pyr_dirty_state.title
                or ctx.visit_slot_and_dirty(_DIRECT_CONTAINER_SLOT)
            ):
                with ctx.container_call(
                    _DIRECT_CONTAINER_SLOT,
                    component,
                    title,
                    dirty_state=dirtyof(title=__pyr_dirty_state.title),
                ):
                    _body(title)

    return {
        "render_container": render_container,
        "neutral_box": neutral_box,
        "info_box": info_box,
        "button_box": button_box,
    }


def test_container_component_ref_rerenders_with_stable_identity() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    program = _make_container_component_program(log)

    program["render_container"](
        ctx,
        dirtyof(component=True, title=True, refresh=True),
        program["neutral_box"],
        "Hello",
        1,
    )
    log.clear()

    program["render_container"](
        ctx,
        dirtyof(component=False, title=False, refresh=True),
        program["neutral_box"],
        "Hello",
        2,
    )

    assert log == [
        ("render-container", "neutral", "Hello", False),
        ("body", "Hello"),
    ]


def test_container_component_ref_replaces_runtime_when_identity_changes() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    program = _make_container_component_program(log)

    program["render_container"](
        ctx,
        dirtyof(component=True, title=True, refresh=True),
        program["neutral_box"],
        "Hello",
        1,
    )
    log.clear()

    program["render_container"](
        ctx,
        dirtyof(component=True, title=False, refresh=True),
        program["info_box"],
        "Hello",
        2,
    )

    assert log == [
        ("render-container", "info", "Hello", False),
        ("body", "Hello"),
    ]


def test_container_component_ref_rolls_back_failed_pass() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []

    def __pyr_ok_box(
        child_ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
        title: str,
    ) -> None:
        del __pyr_dirty_state
        with child_ctx.pass_scope():
            child_ctx.call_native(UIElement, kind="box", props={"title": title})

    @pyrolyze_component_ref(ComponentMetadata("ok_box", __pyr_ok_box))
    def ok_box(title: str) -> None:
        raise CallFromNonPyrolyzeContext("ok_box")

    def __pyr_fail_box(
        child_ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
        title: str,
    ) -> None:
        del title
        with child_ctx.pass_scope():
            child_ctx.call_native(UIElement, kind="box", props={"title": "bad"})
            log.append(("fail", __pyr_dirty_state.title))
            raise RuntimeError("boom")

    @pyrolyze_component_ref(ComponentMetadata("fail_box", __pyr_fail_box))
    def fail_box(title: str) -> None:
        raise CallFromNonPyrolyzeContext("fail_box")

    def render(component: ComponentRef[[str]], title: str, state: DirtyStateContext) -> None:
        with ctx.pass_scope():
            if state.component or state.title or ctx.visit_slot_and_dirty(_DIRECT_CONTAINER_SLOT):
                with ctx.container_call(
                    _DIRECT_CONTAINER_SLOT,
                    component,
                    title,
                    dirty_state=dirtyof(title=state.title),
                ):
                    pass

    render(ok_box, "good", dirtyof(component=True, title=True))
    committed = ctx.committed_ui()

    with pytest.raises(RuntimeError, match="boom"):
        render(fail_box, "bad", dirtyof(component=True, title=True))

    assert ctx.committed_ui() == committed
    assert log == [("fail", True)]


def test_container_component_ref_retains_event_handler_callback_identity() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    program = _make_container_component_program(log)

    program["render_container"](
        ctx,
        dirtyof(component=True, title=True, refresh=True),
        program["button_box"],
        "Alpha",
        1,
    )
    (button_node,) = ctx.committed_ui()
    dispatch = button_node.props["on_press"]
    assert callable(dispatch)

    dispatch()
    assert log == [("body", "Alpha"), ("press", "Alpha")]

    log.clear()
    program["render_container"](
        ctx,
        dirtyof(component=False, title=True, refresh=True),
        program["button_box"],
        "Beta",
        2,
    )
    (updated_button_node,) = ctx.committed_ui()
    updated_dispatch = updated_button_node.props["on_press"]

    assert updated_dispatch is dispatch
    dispatch()
    assert log == [("body", "Beta"), ("press", "Beta")]
