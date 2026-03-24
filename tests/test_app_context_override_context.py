from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pytest

from pyrolyze.api import (
    CallFromNonPyrolyzeContext,
    ComponentMetadata,
    UIElement,
    pyrolyze_component_ref,
)
from pyrolyze.runtime import (
    AppContextKey,
    AppContextStore,
    ContextBase,
    DirtyStateContext,
    ModuleRegistry,
    RenderContext,
    SlotId,
    dirtyof,
)


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.app_context_override_context")

_OVERRIDE_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_OUTER_OVERRIDE_SLOT = SlotId(_MODULE_ID, 2, line_no=11)
_INNER_OVERRIDE_SLOT = SlotId(_MODULE_ID, 3, line_no=12)
_COMPONENT_SLOT = SlotId(_MODULE_ID, 4, line_no=13)

_THEME_KEY = AppContextKey("theme", factory=lambda _host: "factory-theme")
_LOCALE_KEY = AppContextKey("locale", factory=lambda _host: "factory-locale")
_SHARED_KEY = AppContextKey("shared", factory=lambda host: SharedState(values=[f"host:{host}"]))


@dataclass(slots=True)
class SharedState:
    values: list[str] = field(default_factory=list)


def _watch_ref(ref: object) -> tuple[list[object], Callable[[], None]]:
    events: list[object] = []
    subscribe = getattr(ref, "subscribe")
    get = getattr(ref, "get")

    def on_change() -> None:
        events.append(get())

    unsubscribe = subscribe(on_change)
    return events, unsubscribe


def test_authored_app_context_root_is_empty() -> None:
    ctx = RenderContext()

    with pytest.raises(LookupError, match="theme"):
        ctx.get_authored_app_context(_THEME_KEY)


def test_open_app_context_override_is_lexical_and_does_not_emit_wrapper_ui() -> None:
    ctx = RenderContext()
    seen: list[str] = []

    with ctx.pass_scope():
        with ctx.open_app_context_override(_OVERRIDE_SLOT, (_THEME_KEY,), "dark") as scope:
            seen.append(scope.get_authored_app_context(_THEME_KEY))
            scope.call_native(UIElement, kind="label", props={"text": "body"})

    assert seen == ["dark"]
    assert ctx.debug_ui() == (UIElement(kind="label", props={"text": "body"}),)


def test_none_override_falls_through_to_parent_value() -> None:
    ctx = RenderContext()
    seen: list[str] = []

    with ctx.pass_scope():
        with ctx.open_app_context_override(_OUTER_OVERRIDE_SLOT, (_THEME_KEY,), "dark") as outer:
            with outer.open_app_context_override(_INNER_OVERRIDE_SLOT, (_THEME_KEY,), None) as inner:
                seen.append(inner.get_authored_app_context(_THEME_KEY))

    assert seen == ["dark"]


def test_component_child_context_inherits_authored_override() -> None:
    seen: list[str] = []

    def __pyr_child(child_ctx: RenderContext, __pyr_dirty_state: DirtyStateContext) -> None:
        _ = __pyr_dirty_state
        with child_ctx.pass_scope():
            seen.append(child_ctx.get_authored_app_context(_THEME_KEY))

    @pyrolyze_component_ref(ComponentMetadata("child", __pyr_child))
    def child() -> None:
        raise CallFromNonPyrolyzeContext("child")

    ctx = RenderContext()

    with ctx.pass_scope():
        with ctx.open_app_context_override(_OVERRIDE_SLOT, (_THEME_KEY,), "dark") as scope:
            scope.component_call(_COMPONENT_SLOT, child, dirty_state=dirtyof())

    assert seen == ["dark"]


def test_internal_app_context_store_remains_separate_from_authored_overrides() -> None:
    ctx = RenderContext(app_context_store=AppContextStore(host_app="APP"))

    with ctx.pass_scope():
        with ctx.open_app_context_override(_OVERRIDE_SLOT, (_THEME_KEY,), "dark") as scope:
            assert scope.get_authored_app_context(_THEME_KEY) == "dark"
            assert scope.get_app_context(_SHARED_KEY).values == ["host:APP"]


def test_open_app_context_override_validates_value_arity() -> None:
    ctx = RenderContext()

    with ctx.pass_scope():
        with pytest.raises(RuntimeError, match="arity"):
            with ctx.open_app_context_override(
                _OVERRIDE_SLOT,
                (_THEME_KEY, _LOCALE_KEY),
                "dark",
            ):
                pass


def test_open_app_context_override_rejects_key_tuple_changes_at_same_slot() -> None:
    ctx = RenderContext()

    with ctx.pass_scope():
        with ctx.open_app_context_override(_OVERRIDE_SLOT, (_THEME_KEY,), "dark"):
            pass

    with ctx.pass_scope():
        with pytest.raises(RuntimeError, match="fixed"):
            with ctx.open_app_context_override(_OVERRIDE_SLOT, (_LOCALE_KEY,), "en_AU"):
                pass


def test_authored_app_context_ref_notifies_only_changed_key() -> None:
    ctx = RenderContext()

    with ctx.pass_scope():
        with ctx.open_app_context_override(
            _OVERRIDE_SLOT,
            (_THEME_KEY, _LOCALE_KEY),
            "dark",
            "en_AU",
        ) as scope:
            theme_ref = scope.authored_app_context_ref(_THEME_KEY)
            locale_ref = scope.authored_app_context_ref(_LOCALE_KEY)

    theme_events, unsubscribe_theme = _watch_ref(theme_ref)
    locale_events, unsubscribe_locale = _watch_ref(locale_ref)

    try:
        with ctx.pass_scope():
            with ctx.open_app_context_override(
                _OVERRIDE_SLOT,
                (_THEME_KEY, _LOCALE_KEY),
                "dark",
                "fr_FR",
            ):
                pass
    finally:
        unsubscribe_theme()
        unsubscribe_locale()

    assert theme_events == ["dark"]
    assert locale_events == ["en_AU", "fr_FR"]


def test_none_override_forwards_parent_notifications_through_proxy_drip() -> None:
    ctx = RenderContext()

    with ctx.pass_scope():
        with ctx.open_app_context_override(_OUTER_OVERRIDE_SLOT, (_THEME_KEY,), "dark") as outer:
            outer_ref = outer.authored_app_context_ref(_THEME_KEY)
            with outer.open_app_context_override(_INNER_OVERRIDE_SLOT, (_THEME_KEY,), None) as inner:
                inner_ref = inner.authored_app_context_ref(_THEME_KEY)

    inner_events, unsubscribe_inner = _watch_ref(inner_ref)
    try:
        with ctx.pass_scope():
            with ctx.open_app_context_override(_OUTER_OVERRIDE_SLOT, (_THEME_KEY,), "light") as outer:
                with outer.open_app_context_override(_INNER_OVERRIDE_SLOT, (_THEME_KEY,), None):
                    pass
    finally:
        unsubscribe_inner()

    assert inner_events == ["dark", "light"]
    assert inner_ref.identity is not outer_ref.identity


def test_concrete_override_blocks_parent_notifications() -> None:
    ctx = RenderContext()

    with ctx.pass_scope():
        with ctx.open_app_context_override(_OUTER_OVERRIDE_SLOT, (_THEME_KEY,), "dark") as outer:
            with outer.open_app_context_override(_INNER_OVERRIDE_SLOT, (_THEME_KEY,), "blue") as inner:
                inner_ref = inner.authored_app_context_ref(_THEME_KEY)

    inner_events, unsubscribe_inner = _watch_ref(inner_ref)
    try:
        with ctx.pass_scope():
            with ctx.open_app_context_override(_OUTER_OVERRIDE_SLOT, (_THEME_KEY,), "light") as outer:
                with outer.open_app_context_override(_INNER_OVERRIDE_SLOT, (_THEME_KEY,), "blue"):
                    pass
    finally:
        unsubscribe_inner()

    assert inner_events == ["blue"]


def test_transparent_override_unsubscribes_from_parent_when_becoming_concrete() -> None:
    ctx = RenderContext()

    with ctx.pass_scope():
        with ctx.open_app_context_override(_OUTER_OVERRIDE_SLOT, (_THEME_KEY,), "dark") as outer:
            outer_drip = outer.authored_app_context_ref(_THEME_KEY).identity
            with outer.open_app_context_override(_INNER_OVERRIDE_SLOT, (_THEME_KEY,), None):
                pass

    assert outer_drip.has_subscribers() is True

    with ctx.pass_scope():
        with ctx.open_app_context_override(_OUTER_OVERRIDE_SLOT, (_THEME_KEY,), "dark") as outer:
            with outer.open_app_context_override(_INNER_OVERRIDE_SLOT, (_THEME_KEY,), "blue"):
                pass

    assert outer_drip.has_subscribers() is False


def test_transparent_override_unsubscribes_from_parent_on_deactivate() -> None:
    ctx = RenderContext()

    with ctx.pass_scope():
        with ctx.open_app_context_override(_OUTER_OVERRIDE_SLOT, (_THEME_KEY,), "dark") as outer:
            outer_drip = outer.authored_app_context_ref(_THEME_KEY).identity
            with outer.open_app_context_override(_INNER_OVERRIDE_SLOT, (_THEME_KEY,), None):
                pass

    assert outer_drip.has_subscribers() is True

    with ctx.pass_scope():
        with ctx.open_app_context_override(_OUTER_OVERRIDE_SLOT, (_THEME_KEY,), "dark"):
            pass

    assert outer_drip.has_subscribers() is False
