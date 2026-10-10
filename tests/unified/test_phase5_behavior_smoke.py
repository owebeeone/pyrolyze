"""Phase 5.2: mount unified emitters through each backend ``MountableEngine`` (one path each).

These are structural smokes: native instances exist under the host; no GUI event loop.
Known gaps (e.g. Tk ``tool_bar`` title ignored) stay documented on ``UnifiedNativeLibrary`` methods.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from pyrolyze.api import UIElement
from pyrolyze.backends.dearpygui.host import RecordingDpgHost
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


@pytest.mark.parametrize(
    "emit,property_name",
    [
        (DpgUnifiedNativeLibrary.push_button, "label"),
        (DpgUnifiedNativeLibrary.toggle, "label"),
        (DpgUnifiedNativeLibrary.text_field, "value"),
    ],
    ids=["button", "toggle", "text-field"],
)
def test_dpg_unified_text_updates_preserve_retained_item(
    recording_dpg_host: RecordingDpgHost,
    emit: Callable[..., UIElement],
    property_name: str,
) -> None:
    engine = MountableEngine(DearPyGuiUiLibrary.WIDGET_SPECS)
    library = DpgUnifiedNativeLibrary()
    node = engine.mount(
        emit(library, **{property_name: "native"}),
        slot_id=("unified", property_name),
    )
    mountable = node.mountable
    tag = int(mountable.tag)

    def read_text() -> str:
        if property_name == "value":
            return recording_dpg_host.get_item_value(tag)
        return recording_dpg_host.get_config_value(tag, property_name)

    assert read_text() == "native"
    for text in ("populated", None, "", "repopulated"):
        engine.update(node, emit(library, text=text))
        assert read_text() == ("populated" if text is None else text)
        assert node.mountable is mountable
        assert int(node.mountable.tag) == tag
    engine.update(node, emit(library))
    assert read_text() == "repopulated"
