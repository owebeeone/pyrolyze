from __future__ import annotations

from contextlib import contextmanager

import pytest

from pyrolyze.runtime.context import (
    DirtyStateContext,
    ModuleRegistry,
    RenderContext,
    SlotId,
    SlotOwnershipError,
    dirtyof,
)


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.context_graph_phase1")

_TITLE_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_SECTION_SLOT = SlotId(_MODULE_ID, 2, line_no=11)
_BADGE_SLOT = SlotId(_MODULE_ID, 3, line_no=12)
_PANEL_SLOT = SlotId(_MODULE_ID, 4, line_no=13)
_COUNTER_SLOT = SlotId(_MODULE_ID, 5, line_no=14)
_BUTTON_SLOT = SlotId(_MODULE_ID, 6, line_no=15)
_BUTTON_EVENT_SLOT = SlotId(_MODULE_ID, 7, line_no=16)


def _make_welcome_program(log: list[tuple[object, ...]]):
    @contextmanager
    def _section(title: str, *, accent: str):
        log.append(("section.enter", title, accent))
        try:
            yield
        finally:
            log.append(("section.exit", title, accent))

    def _format_title(name: str) -> str:
        log.append(("format_title", name))
        return f"Hello {name}"

    def _badge(text: str, *, tone: str) -> None:
        log.append(("badge", text, tone))

    def _pyr_welcome(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
        name: str,
    ) -> None:
        with ctx.pass_scope():
            __pyr_title_dirty, title = ctx.call_plain(
                _TITLE_SLOT,
                _format_title,
                name,
            )

            if __pyr_title_dirty or ctx.visit_slot_and_dirty(_SECTION_SLOT):
                with ctx.container_call(
                    _SECTION_SLOT,
                    _section,
                    "Greeting",
                    accent="blue",
                ) as section_ctx:
                    if __pyr_title_dirty or section_ctx.visit_slot_and_dirty(_BADGE_SLOT):
                        section_ctx.leaf_call(
                            _BADGE_SLOT,
                            _badge,
                            title,
                            tone="info",
                        )

    return _pyr_welcome


def _make_welcome_conditional_program(log: list[tuple[object, ...]]):
    @contextmanager
    def _section(title: str, *, accent: str):
        log.append(("section.enter", title, accent))
        try:
            yield
        finally:
            log.append(("section.exit", title, accent))

    def _format_title(name: str) -> str:
        log.append(("format_title", name))
        return f"Hello {name}"

    def _badge(text: str, *, tone: str) -> None:
        log.append(("badge", text, tone))

    def _pyr_welcome_conditional(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
        name: str,
        show_badge: bool,
    ) -> None:
        with ctx.pass_scope():
            __pyr_title_dirty, title = ctx.call_plain(
                _TITLE_SLOT,
                _format_title,
                name,
            )

            if (
                __pyr_title_dirty
                or __pyr_dirty_state.show_badge
                or ctx.visit_slot_and_dirty(_SECTION_SLOT)
            ):
                with ctx.container_call(
                    _SECTION_SLOT,
                    _section,
                    "Greeting",
                    accent="blue",
                ) as section_ctx:
                    if show_badge:
                        if (
                            __pyr_title_dirty
                            or __pyr_dirty_state.show_badge
                            or section_ctx.visit_slot_and_dirty(_BADGE_SLOT)
                        ):
                            section_ctx.leaf_call(
                                _BADGE_SLOT,
                                _badge,
                                title,
                                tone="info",
                            )

    return _pyr_welcome_conditional


def _make_wrong_child_owner_program(log: list[tuple[object, ...]]):
    @contextmanager
    def _section(title: str, *, accent: str):
        log.append(("section.enter", title, accent))
        try:
            yield
        finally:
            log.append(("section.exit", title, accent))

    def _format_title(name: str) -> str:
        log.append(("format_title", name))
        return f"Hello {name}"

    def _badge(text: str, *, tone: str) -> None:
        log.append(("badge", text, tone))

    def _pyr_wrong_child_owner(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
        name: str,
        accent: str,
    ) -> None:
        with ctx.pass_scope():
            __pyr_title_dirty, title = ctx.call_plain(
                _TITLE_SLOT,
                _format_title,
                name,
            )

            if (
                __pyr_title_dirty
                or __pyr_dirty_state.accent
                or ctx.visit_slot_and_dirty(_SECTION_SLOT)
            ):
                with ctx.container_call(
                    _SECTION_SLOT,
                    _section,
                    "Greeting",
                    accent=accent,
                ) as section_ctx:
                    if __pyr_title_dirty or ctx.visit_slot_and_dirty(_BADGE_SLOT):
                        section_ctx.leaf_call(
                            _BADGE_SLOT,
                            _badge,
                            title,
                            tone="info",
                        )

    return _pyr_wrong_child_owner


def test_first_pass_executes_and_stable_second_pass_retains_subtree() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    pyr_welcome = _make_welcome_program(log)

    pyr_welcome(ctx, dirtyof(name=True), "Ada")

    assert log == [
        ("format_title", "Ada"),
        ("section.enter", "Greeting", "blue"),
        ("badge", "Hello Ada", "info"),
        ("section.exit", "Greeting", "blue"),
    ]
    assert ctx.debug_children_of() == (_TITLE_SLOT, _SECTION_SLOT)
    assert ctx.debug_children_of(_SECTION_SLOT) == (_BADGE_SLOT,)

    pyr_welcome(ctx, dirtyof(name=False), "Ada")

    assert log == [
        ("format_title", "Ada"),
        ("section.enter", "Greeting", "blue"),
        ("badge", "Hello Ada", "info"),
        ("section.exit", "Greeting", "blue"),
    ]
    assert ctx.debug_children_of() == (_TITLE_SLOT, _SECTION_SLOT)
    assert ctx.debug_children_of(_SECTION_SLOT) == (_BADGE_SLOT,)


def test_parent_rerun_deactivates_previously_active_child_when_branch_is_omitted() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    pyr_welcome_conditional = _make_welcome_conditional_program(log)

    pyr_welcome_conditional(
        ctx,
        dirtyof(name=True, show_badge=True),
        "Ada",
        True,
    )
    assert ctx.debug_children_of(_SECTION_SLOT) == (_BADGE_SLOT,)

    pyr_welcome_conditional(
        ctx,
        dirtyof(name=True, show_badge=True),
        "Bea",
        False,
    )

    assert ("badge", "Hello Bea", "info") not in log
    assert ctx.debug_children_of(_SECTION_SLOT) == ()


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
    pyr_welcome = _make_welcome_program(log)
    pyr_wrong_child_owner = _make_wrong_child_owner_program(log)

    pyr_welcome(ctx, dirtyof(name=True), "Ada")

    with pytest.raises(SlotOwnershipError):
        pyr_wrong_child_owner(
            ctx,
            dirtyof(name=False, accent=True),
            "Ada",
            "violet",
        )


def test_skipped_clean_subtree_preserves_event_handler_slots() -> None:
    ctx = RenderContext()
    events: list[str] = []
    captured_dispatch: dict[str, object] = {}

    @contextmanager
    def _panel():
        yield

    @contextmanager
    def _button():
        yield

    def _render(counter_dirty: bool, button_dirty: bool) -> None:
        with ctx.pass_scope():
            if counter_dirty or button_dirty or ctx.visit_slot_and_dirty(_PANEL_SLOT):
                with ctx.container_call(_PANEL_SLOT, _panel) as panel_ctx:
                    if counter_dirty or panel_ctx.visit_slot_and_dirty(_COUNTER_SLOT):
                        panel_ctx.leaf_call(_COUNTER_SLOT, lambda: None)
                    if button_dirty or panel_ctx.visit_slot_and_dirty(_BUTTON_SLOT):
                        with panel_ctx.container_call(_BUTTON_SLOT, _button) as button_ctx:
                            captured_dispatch["value"] = button_ctx.event_handler(
                                _BUTTON_EVENT_SLOT,
                                dirty=button_dirty,
                                callback=lambda: events.append("clicked"),
                            )

    _render(counter_dirty=True, button_dirty=True)
    dispatch = captured_dispatch["value"]
    assert callable(dispatch)
    dispatch()
    assert events == ["clicked"]

    _render(counter_dirty=True, button_dirty=False)

    dispatch = captured_dispatch["value"]
    assert callable(dispatch)
    dispatch()
    assert events == ["clicked", "clicked"]
