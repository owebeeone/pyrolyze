from __future__ import annotations

from contextlib import contextmanager

import pytest

from pyrolyze.runtime.context import (
    CompValue,
    ModuleRegistry,
    RenderContext,
    SlotId,
    SlotOwnershipError,
)


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.context_graph_phase1")

_TITLE_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_SECTION_SLOT = SlotId(_MODULE_ID, 2, line_no=11)
_BADGE_SLOT = SlotId(_MODULE_ID, 3, line_no=12)


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

    def _pyr_welcome(ctx: RenderContext, name: CompValue[str]) -> None:
        with ctx.pass_scope():
            title = ctx.call_plain(
                _TITLE_SLOT,
                ctx.literal(_format_title),
                name,
            )

            if title.dirty or ctx.visit_slot_and_dirty(_SECTION_SLOT):
                with ctx.container_call(
                    _SECTION_SLOT,
                    _section,
                    ctx.literal("Greeting"),
                    accent=ctx.literal("blue"),
                ) as section_ctx:
                    if title.dirty or section_ctx.visit_slot_and_dirty(_BADGE_SLOT):
                        section_ctx.leaf_call(
                            _BADGE_SLOT,
                            _badge,
                            title,
                            tone=ctx.literal("info"),
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
        name: CompValue[str],
        show_badge: CompValue[bool],
    ) -> None:
        with ctx.pass_scope():
            title = ctx.call_plain(
                _TITLE_SLOT,
                ctx.literal(_format_title),
                name,
            )

            if title.dirty or show_badge.dirty or ctx.visit_slot_and_dirty(_SECTION_SLOT):
                with ctx.container_call(
                    _SECTION_SLOT,
                    _section,
                    ctx.literal("Greeting"),
                    accent=ctx.literal("blue"),
                ) as section_ctx:
                    if show_badge.value:
                        if title.dirty or show_badge.dirty or section_ctx.visit_slot_and_dirty(_BADGE_SLOT):
                            section_ctx.leaf_call(
                                _BADGE_SLOT,
                                _badge,
                                title,
                                tone=ctx.literal("info"),
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
        name: CompValue[str],
        accent: CompValue[str],
    ) -> None:
        with ctx.pass_scope():
            title = ctx.call_plain(
                _TITLE_SLOT,
                ctx.literal(_format_title),
                name,
            )

            if title.dirty or accent.dirty or ctx.visit_slot_and_dirty(_SECTION_SLOT):
                with ctx.container_call(
                    _SECTION_SLOT,
                    _section,
                    ctx.literal("Greeting"),
                    accent=accent,
                ) as section_ctx:
                    if title.dirty or ctx.visit_slot_and_dirty(_BADGE_SLOT):
                        section_ctx.leaf_call(
                            _BADGE_SLOT,
                            _badge,
                            title,
                            tone=ctx.literal("info"),
                        )

    return _pyr_wrong_child_owner

def test_first_pass_executes_and_stable_second_pass_retains_subtree() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    pyr_welcome = _make_welcome_program(log)

    pyr_welcome(ctx, CompValue("Ada", dirty=True))

    assert log == [
        ("format_title", "Ada"),
        ("section.enter", "Greeting", "blue"),
        ("badge", "Hello Ada", "info"),
        ("section.exit", "Greeting", "blue"),
    ]
    assert ctx.debug_children_of() == (_TITLE_SLOT, _SECTION_SLOT)
    assert ctx.debug_children_of(_SECTION_SLOT) == (_BADGE_SLOT,)

    pyr_welcome(ctx, CompValue("Ada", dirty=False))

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
        CompValue("Ada", dirty=True),
        CompValue(True, dirty=True),
    )
    assert ctx.debug_children_of(_SECTION_SLOT) == (_BADGE_SLOT,)

    pyr_welcome_conditional(
        ctx,
        CompValue("Bea", dirty=True),
        CompValue(False, dirty=True),
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


def test_pass_scope_commits_cleanup_when_body_raises() -> None:
    ctx = RenderContext()
    slot = SlotId(_MODULE_ID, 100, line_no=100)

    with pytest.raises(RuntimeError, match="boom"):
        with ctx.pass_scope():
            assert ctx.visit_slot_and_dirty(slot) is True
            raise RuntimeError("boom")

    with ctx.pass_scope():
        assert ctx.visit_slot_and_dirty(slot) is False


def test_child_visitation_must_use_the_owning_container_context() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    pyr_welcome = _make_welcome_program(log)
    pyr_wrong_child_owner = _make_wrong_child_owner_program(log)

    pyr_welcome(ctx, CompValue("Ada", dirty=True))

    with pytest.raises(SlotOwnershipError):
        pyr_wrong_child_owner(
            ctx,
            CompValue("Ada", dirty=False),
            CompValue("violet", dirty=True),
        )
