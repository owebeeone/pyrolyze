from __future__ import annotations

import pytest

from pyrolyze.api import use_app_context
from pyrolyze.runtime import AppContextKey, ModuleRegistry, RenderContext, SlotId, dirtyof
from tests.slot_expr_test_utils import eval_single_slot_expr


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.use_app_context_runtime")

_OVERRIDE_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_OUTER_OVERRIDE_SLOT = SlotId(_MODULE_ID, 2, line_no=11)
_INNER_OVERRIDE_SLOT = SlotId(_MODULE_ID, 3, line_no=12)
_READ_SLOT = SlotId(_MODULE_ID, 4, line_no=13)

_THEME_KEY = AppContextKey("theme", factory=lambda _host: "factory-theme")
_LOCALE_KEY = AppContextKey("locale", factory=lambda _host: "factory-locale")


def test_use_app_context_reads_current_override_value() -> None:
    ctx = RenderContext()

    with ctx.pass_scope():
        with ctx.open_app_context_override(_OVERRIDE_SLOT, (_THEME_KEY,), "dark") as scope:
            _, value = eval_single_slot_expr(scope, dirtyof(), _READ_SLOT, use_app_context, _THEME_KEY)

    assert value == "dark"


def test_use_app_context_rejects_non_key_arguments() -> None:
    ctx = RenderContext()

    with ctx.pass_scope():
        with pytest.raises(TypeError, match="AppContextKey"):
            eval_single_slot_expr(ctx, dirtyof(), _READ_SLOT, use_app_context, "theme")


def test_use_app_context_raises_when_no_provider_exists() -> None:
    ctx = RenderContext()

    with ctx.pass_scope():
        with pytest.raises(LookupError, match="theme"):
            eval_single_slot_expr(ctx, dirtyof(), _READ_SLOT, use_app_context, _THEME_KEY)


def test_use_app_context_rebinds_when_requested_key_changes() -> None:
    ctx = RenderContext()
    requested_key = _THEME_KEY
    requested_key_dirty = True
    theme_value = "dark"
    locale_value = "en_AU"
    values: list[str] = []
    drips: dict[str, object] = {}

    def render() -> None:
        nonlocal requested_key_dirty
        with ctx.pass_scope():
            with ctx.open_app_context_override(
                _OVERRIDE_SLOT,
                (_THEME_KEY, _LOCALE_KEY),
                theme_value,
                locale_value,
            ) as scope:
                drips["theme"] = scope.authored_app_context_ref(_THEME_KEY).identity
                drips["locale"] = scope.authored_app_context_ref(_LOCALE_KEY).identity
                _, value = eval_single_slot_expr(
                    scope,
                    dirtyof(),
                    _READ_SLOT,
                    use_app_context,
                    requested_key,
                    args_dirty=(requested_key_dirty,),
                )
                values.append(value)
                requested_key_dirty = False

    ctx.mount(render)

    assert values == ["dark"]

    requested_key = _LOCALE_KEY
    requested_key_dirty = True
    ctx._run_boundary()

    assert values == ["dark", "en_AU"]

    theme_value = "light"
    drips["theme"].next("light")
    ctx.run_pending_invalidations()

    assert values == ["dark", "en_AU"]

    locale_value = "fr_FR"
    drips["locale"].next("fr_FR")
    ctx.run_pending_invalidations()

    assert values == ["dark", "en_AU", "fr_FR"]


def test_use_app_context_reads_parent_value_through_none_override() -> None:
    ctx = RenderContext()
    theme_value = "dark"
    values: list[str] = []
    drips: dict[str, object] = {}

    def render() -> None:
        with ctx.pass_scope():
            with ctx.open_app_context_override(_OUTER_OVERRIDE_SLOT, (_THEME_KEY,), theme_value) as outer:
                drips["outer"] = outer.authored_app_context_ref(_THEME_KEY).identity
                with outer.open_app_context_override(_INNER_OVERRIDE_SLOT, (_THEME_KEY,), None) as inner:
                    _, value = eval_single_slot_expr(inner, dirtyof(), _READ_SLOT, use_app_context, _THEME_KEY)
                    values.append(value)

    ctx.mount(render)

    assert values == ["dark"]

    theme_value = "light"
    drips["outer"].next("light")
    ctx.run_pending_invalidations()

    assert values == ["dark", "light"]
