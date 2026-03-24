"""Phase 5.2: mount unified emitters through each backend ``MountableEngine`` (one path each).

These are structural smokes: native instances exist under the host; no GUI event loop.
Known gaps (e.g. Tk ``tool_bar`` title ignored) stay documented on ``UnifiedNativeLibrary`` methods.
"""

from __future__ import annotations

import pytest

from pyrolyze.backends.dearpygui.generated_library import DearPyGuiUiLibrary
from pyrolyze.backends.mountable_engine import MountableEngine
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary
from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary
from pyrolyze.unified import (
    DpgUnifiedNativeLibrary,
    QtUnifiedNativeLibrary,
    TkUnifiedNativeLibrary,
)


@pytest.mark.parametrize(
    "backend,specs_type,lib_factory,setup_fixture",
    [
        ("qt", PySide6UiLibrary, QtUnifiedNativeLibrary, "qapplication"),
        ("tk", TkinterUiLibrary, TkUnifiedNativeLibrary, "tk_root"),
        ("dpg", DearPyGuiUiLibrary, DpgUnifiedNativeLibrary, "recording_dpg_host"),
    ],
)
def test_phase5_unified_push_button_mounts_under_engine(
    request: pytest.FixtureRequest,
    backend: str,
    specs_type: type,
    lib_factory: type,
    setup_fixture: str,
) -> None:
    _ = request.getfixturevalue(setup_fixture)
    eng = MountableEngine(specs_type.WIDGET_SPECS)
    lib = lib_factory()
    el = lib.push_button(text="Phase5")
    node = eng.mount(el, slot_id=("phase5", "smoke", backend), call_site_id=800)
    assert node.element.kind == el.kind
    assert node.mountable is not None
