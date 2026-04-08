from __future__ import annotations

from pyrolyze.runtime import context_lcm as runtime


module_registry = runtime.ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.test_runtime_context_lcm_phase6")

_OVERRIDE_SLOT = runtime.SlotId(_MODULE_ID, 1, line_no=200)
_THEME_KEY = runtime.AppContextKey("theme", factory=lambda _host: "factory-theme")


def _root() -> runtime.RenderContext:
    root = runtime.RenderContext()
    root.begin_pass()
    return root


def test_context_lcm_exports_app_context_override_slot_context_override() -> None:
    assert runtime.AppContextOverrideSlotContext.__module__ == "pyrolyze.runtime.context_lcm"


def test_app_context_override_slot_context_direct_stage_commit_and_rollback() -> None:
    root = _root()
    slot = runtime.AppContextOverrideSlotContext(
        render_context=root,
        parent=root,
        slot_id=_OVERRIDE_SLOT,
    )

    slot._begin_scope_pass()
    slot.stage_override((_THEME_KEY,), ("dark",))
    slot._commit_scope_pass()

    assert slot.declared_keys == (_THEME_KEY,)
    assert slot.committed_values == ("dark",)
    assert slot.get_authored_app_context(_THEME_KEY) == "dark"

    slot._begin_scope_pass()
    slot.stage_override((_THEME_KEY,), ("light",))
    slot._rollback_scope_pass()

    assert slot.committed_values == ("dark",)
    assert slot.get_authored_app_context(_THEME_KEY) == "dark"
