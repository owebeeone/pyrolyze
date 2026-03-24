"""Phase 5.1: every unified emitter returns a kind the backend ``MountableEngine`` accepts.

Complements explicit equality tests in ``test_unified_native_library.py`` by mounting
each surface once per backend (structural acceptance).
"""

from __future__ import annotations

from typing import Any

from pyrolyze.backends.dearpygui.generated_library import DearPyGuiUiLibrary
from pyrolyze.backends.mountable_engine import MountableEngine
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary
from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary
from pyrolyze.unified import (
    DpgUnifiedNativeLibrary,
    QtUnifiedNativeLibrary,
    TkUnifiedNativeLibrary,
)

# (method, kwargs) — minimal valid calls for ``UnifiedNativeLibrary`` surface.
_EMITTER_CALLS: tuple[tuple[str, dict[str, Any]], ...] = (
    ("push_button", {"text": "m"}),
    ("toggle", {"checked": False, "text": ""}),
    ("text_field", {"text": ""}),
    ("int_field", {"value": 0}),
    ("float_field", {"value": 0.0}),
    ("combo_box", {}),
    ("slider", {}),
    ("progress", {"value": 0.0}),
    ("tab_stack", {}),
    ("radio_button", {"text": "r", "checked": False}),
    ("text_area", {"text": "", "read_only": False}),
    ("static_text", {"text": "s"}),
    ("menu_bar", {}),
    ("tool_bar", {"title": ""}),
    ("separator", {"horizontal": True}),
    ("scroll_panel", {}),
    ("spacer", {"width": 0, "height": 0}),
    ("label", {"text": "L"}),
)


def test_phase5_emitter_matrix_mounts_on_all_backends(
    qapplication: object,
    tk_root: object,
    recording_dpg_host: object,
) -> None:
    _ = (qapplication, tk_root, recording_dpg_host)
    scenarios: tuple[tuple[str, type, type, Any], ...] = (
        ("qt", PySide6UiLibrary, QtUnifiedNativeLibrary, qapplication),
        ("tk", TkinterUiLibrary, TkUnifiedNativeLibrary, tk_root),
        ("dpg", DearPyGuiUiLibrary, DpgUnifiedNativeLibrary, recording_dpg_host),
    )
    call_site = 5000
    for sid, spec_t, lib_t, _ctx in scenarios:
        eng = MountableEngine(spec_t.WIDGET_SPECS)
        lib = lib_t()
        for method, kw in _EMITTER_CALLS:
            el = getattr(lib, method)(**kw)
            node = eng.mount(
                el,
                slot_id=("matrix", sid, method),
                call_site_id=call_site,
            )
            call_site += 1
            assert node.element.kind == el.kind, f"{sid}.{method}"
            assert node.mountable is not None
