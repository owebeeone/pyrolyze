"""Phase 6.1: unified context keys + subtree override feeding unified emitters (per backend).

``RenderContext.open_app_context_override`` supplies values read via
``get_authored_app_context``; those values are passed into
``UnifiedNativeLibrary`` emitters and mounted with each backend's
``MountableEngine``. Tk mount tests skip on macOS (see ``conftest.py``).
"""

from __future__ import annotations

from pyrolyze.backends.dearpygui.generated_library import DearPyGuiUiLibrary
from pyrolyze.backends.mountable_engine import MountableEngine
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary
from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary
from pyrolyze.runtime import ModuleRegistry, RenderContext, SlotId
from pyrolyze.unified.context_keys import UNIFIED_DENSITY, UNIFIED_THEME, UNIFIED_TYPOGRAPHY
from pyrolyze.unified.dpg import DpgUnifiedNativeLibrary
from pyrolyze.unified.qt import QtUnifiedNativeLibrary
from pyrolyze.unified.tk import TkUnifiedNativeLibrary

_module_registry = ModuleRegistry()
_MOD = _module_registry.module_id("tests.unified.phase6_app_context")
_SLOT_THEME = SlotId(_MOD, 1, line_no=1)
_SLOT_DENSITY = SlotId(_MOD, 2, line_no=2)
_SLOT_TYPO = SlotId(_MOD, 3, line_no=3)


def test_phase6_context_keys_are_stable_app_context_keys() -> None:
    assert UNIFIED_THEME.debug_name == "unified.theme"
    assert UNIFIED_DENSITY.debug_name == "unified.density"
    assert UNIFIED_TYPOGRAPHY.debug_name == "unified.typography"


def test_phase6_qt_unified_emitter_sees_subtree_theme(qapplication: object) -> None:
    _ = qapplication
    ctx = RenderContext()
    with ctx.pass_scope():
        with ctx.open_app_context_override(_SLOT_THEME, (UNIFIED_THEME,), "dark") as scope:
            theme = scope.get_authored_app_context(UNIFIED_THEME)
            el = QtUnifiedNativeLibrary().push_button(text=f"t={theme}")
    eng = MountableEngine(PySide6UiLibrary.WIDGET_SPECS)
    node = eng.mount(el, slot_id=("phase6", "qt"), call_site_id=601)
    assert node.element.props["text"] == "t=dark"


def test_phase6_tk_unified_emitter_sees_subtree_density(tk_root: object) -> None:
    _ = tk_root
    ctx = RenderContext()
    with ctx.pass_scope():
        with ctx.open_app_context_override(_SLOT_DENSITY, (UNIFIED_DENSITY,), "compact") as scope:
            density = scope.get_authored_app_context(UNIFIED_DENSITY)
            el = TkUnifiedNativeLibrary().push_button(text=f"d={density}")
    eng = MountableEngine(TkinterUiLibrary.WIDGET_SPECS)
    node = eng.mount(el, slot_id=("phase6", "tk"), call_site_id=602)
    assert node.element.props["text"] == "d=compact"


def test_phase6_dpg_unified_emitter_sees_subtree_typography(recording_dpg_host: object) -> None:
    _ = recording_dpg_host
    ctx = RenderContext()
    with ctx.pass_scope():
        with ctx.open_app_context_override(_SLOT_TYPO, (UNIFIED_TYPOGRAPHY,), "large") as scope:
            typo = scope.get_authored_app_context(UNIFIED_TYPOGRAPHY)
            el = DpgUnifiedNativeLibrary().push_button(text=f"y={typo}")
    eng = MountableEngine(DearPyGuiUiLibrary.WIDGET_SPECS)
    node = eng.mount(el, slot_id=("phase6", "dpg"), call_site_id=603)
    assert node.element.props["label"] == "y=large"
