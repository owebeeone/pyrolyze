"""Unified native library: factory, backend selection, and wave-1 emitters."""

from __future__ import annotations

import pytest

from pyrolyze.api import UIElement
from pyrolyze.unified import (
    PYROLYZE_UNIFIED_BACKEND_ENV,
    DpgUnifiedNativeLibrary,
    QtUnifiedNativeLibrary,
    TkUnifiedNativeLibrary,
    UnifiedNativeLibrary,
    get_unified_native_library,
)
from pyrolyze.unified.factory import _normalize_backend_key


def test_normalize_backend_key_strips_and_lowercases() -> None:
    assert _normalize_backend_key("  QT  ") == "qt"


def test_get_unified_native_library_unknown_backend_raises() -> None:
    with pytest.raises(ValueError, match="unknown unified backend"):
        get_unified_native_library(backend="wasm")


def test_get_unified_native_library_explicit_qt() -> None:
    lib = get_unified_native_library(backend="qt")
    assert isinstance(lib, QtUnifiedNativeLibrary)
    assert lib.backend_id == "qt"


def test_get_unified_native_library_respects_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(PYROLYZE_UNIFIED_BACKEND_ENV, "tk")
    lib = get_unified_native_library()
    assert isinstance(lib, TkUnifiedNativeLibrary)
    assert lib.backend_id == "tk"


def test_get_unified_native_library_explicit_overrides_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(PYROLYZE_UNIFIED_BACKEND_ENV, "tk")
    lib = get_unified_native_library(backend="dpg")
    assert isinstance(lib, DpgUnifiedNativeLibrary)


def test_default_backend_is_qt_when_env_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(PYROLYZE_UNIFIED_BACKEND_ENV, raising=False)
    lib = get_unified_native_library()
    assert isinstance(lib, QtUnifiedNativeLibrary)


def test_qt_native_library_type() -> None:
    from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary

    lib = QtUnifiedNativeLibrary()
    assert lib.native_library_type is PySide6UiLibrary


def test_qt_mounts_delegates_to_ui_library() -> None:
    from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary

    lib = QtUnifiedNativeLibrary()
    assert lib.mounts is PySide6UiLibrary.mounts


def test_qt_ux_alias_exposes_generated_structural_component_refs() -> None:
    from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary
    from pyrolyze.unified.qt import QtUx

    assert QtUx is QtUnifiedNativeLibrary
    assert QtUnifiedNativeLibrary.CQMainWindow == PySide6UiLibrary.CQMainWindow
    assert QtUnifiedNativeLibrary.mounts is PySide6UiLibrary.mounts
    assert QtUnifiedNativeLibrary.UI_INTERFACE.owner is QtUnifiedNativeLibrary


def test_tk_mounts_delegates_to_ui_library() -> None:
    from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary

    lib = TkUnifiedNativeLibrary()
    assert lib.mounts is TkinterUiLibrary.mounts


def test_dpg_mounts_is_none() -> None:
    lib = DpgUnifiedNativeLibrary()
    assert lib.mounts is None


def test_qt_push_button_kind() -> None:
    lib = QtUnifiedNativeLibrary()
    el = lib.push_button(text="OK")
    assert el == UIElement(kind="QPushButton", props={"text": "OK"})


def test_tk_push_button_kind() -> None:
    lib = TkUnifiedNativeLibrary()
    el = lib.push_button(text="OK")
    assert el == UIElement(kind="ttk_Button", props={"text": "OK"})


def test_dpg_push_button_kind() -> None:
    lib = DpgUnifiedNativeLibrary()
    el = lib.push_button(text="OK")
    assert el == UIElement(kind="DpgButton", props={"label": "OK"})


def test_label_shared_across_backends() -> None:
    for factory in (QtUnifiedNativeLibrary, TkUnifiedNativeLibrary, DpgUnifiedNativeLibrary):
        lib = factory()
        el = lib.label(text="Hi")
        assert el.kind == "Label"
        assert el.props == {"text": "Hi"}


def test_qt_toggle_and_text_field() -> None:
    lib = QtUnifiedNativeLibrary()
    assert lib.toggle(checked=True, text="On") == UIElement(
        kind="QCheckBox",
        props={"text": "On", "checked": True},
    )
    assert lib.text_field(text="x") == UIElement(kind="QLineEdit", props={"text": "x"})


def test_tk_toggle_and_text_field() -> None:
    lib = TkUnifiedNativeLibrary()
    assert lib.toggle(text="x", checked=False) == UIElement(
        kind="ttk_Checkbutton",
        props={"text": "x", "checked": False},
    )
    assert lib.text_field(text="ab") == UIElement(kind="ttk_Entry", props={"text": "ab"})


def test_dpg_toggle_and_text_field() -> None:
    lib = DpgUnifiedNativeLibrary()
    assert lib.toggle(checked=True, text="L") == UIElement(
        kind="DpgCheckbox",
        props={"label": "L", "value": True},
    )
    assert lib.text_field(text="hi") == UIElement(kind="DpgInputText", props={"value": "hi"})


def test_qt_wave_a_emitters() -> None:
    lib = QtUnifiedNativeLibrary()
    assert lib.int_field(value=3, min_value=0, max_value=9, step=2) == UIElement(
        kind="QSpinBox",
        props={"value": 3, "singleStep": 2, "minimum": 0, "maximum": 9},
    )
    assert lib.float_field(value=1.5, min_value=0.0, max_value=10.0, step=0.5) == UIElement(
        kind="QDoubleSpinBox",
        props={"value": 1.5, "singleStep": 0.5, "minimum": 0.0, "maximum": 10.0},
    )
    assert lib.combo_box(items=("a", "b"), current_index=1) == UIElement(
        kind="QComboBox",
        props={"items": ["a", "b"], "currentIndex": 1},
    )
    assert lib.slider(value=25, min_value=0, max_value=50) == UIElement(
        kind="QSlider",
        props={"minimum": 0, "maximum": 50, "value": 25, "orientation": "Horizontal"},
    )
    assert lib.progress(value=0.5) == UIElement(
        kind="QProgressBar",
        props={"maximum": 100, "value": 50},
    )
    assert lib.tab_stack() == UIElement(kind="QTabWidget", props={})
    assert lib.radio_button(text="Opt", checked=True) == UIElement(
        kind="QRadioButton",
        props={"text": "Opt", "checked": True},
    )


def test_tk_wave_a_emitters() -> None:
    lib = TkUnifiedNativeLibrary()
    assert lib.int_field(value=3, min_value=0, max_value=9, step=2) == UIElement(
        kind="tkinter_Spinbox",
        props={"from_": 0, "to": 9, "increment": 2, "text": "3"},
    )
    assert lib.float_field(value=1.5, min_value=0.0, max_value=10.0) == UIElement(
        kind="tkinter_Spinbox",
        props={
            "from_": 0.0,
            "to": 10.0,
            "increment": 0.1,
            "format": "%.6g",
            "text": "1.5",
        },
    )
    assert lib.combo_box(items=("x", "y"), current_index=0) == UIElement(
        kind="Combobox",
        props={"values": ["x", "y"], "text": "x"},
    )
    assert lib.slider(value=25, min_value=0, max_value=50) == UIElement(
        kind="ttk_Scale",
        props={"from_": 0.0, "to": 50.0, "value": 25.0},
    )
    assert lib.progress(value=0.25) == UIElement(
        kind="Progressbar",
        props={"maximum": 100, "value": 25},
    )
    assert lib.tab_stack() == UIElement(kind="Notebook", props={})
    assert lib.radio_button(text="A", checked=True) == UIElement(
        kind="ttk_Radiobutton",
        props={"text": "A", "value": "A", "state": "selected"},
    )


def test_dpg_wave_a_emitters() -> None:
    lib = DpgUnifiedNativeLibrary()
    assert lib.int_field(value=7, min_value=0, max_value=10, step=1) == UIElement(
        kind="DpgInputInt",
        props={"value": 7, "min_value": 0, "max_value": 10},
    )
    assert lib.float_field(value=2.5, min_value=0.0, max_value=5.0) == UIElement(
        kind="DpgInputFloat",
        props={"value": 2.5, "min_value": 0.0, "max_value": 5.0},
    )
    assert lib.combo_box(items=("p", "q"), current_index=1) == UIElement(
        kind="DpgCombo",
        props={"items": ["p", "q"], "value": "q"},
    )
    assert lib.slider(value=3, min_value=0, max_value=10) == UIElement(
        kind="DpgSliderInt",
        props={"min_value": 0, "max_value": 10, "value": 3},
    )
    assert lib.progress(value=0.4) == UIElement(
        kind="DpgProgressBar",
        props={"value": 0.4},
    )
    assert lib.tab_stack() == UIElement(kind="DpgTabBar", props={})
    assert lib.radio_button(text="R", checked=True) == UIElement(
        kind="DpgRadioButton",
        props={"label": "R", "items": ("R",), "value": "R"},
    )


def test_qt_waves_bcd_emitters() -> None:
    lib = QtUnifiedNativeLibrary()
    assert lib.text_area(text="a\nb", read_only=True) == UIElement(
        kind="QPlainTextEdit",
        props={"plainText": "a\nb", "readOnly": True},
    )
    assert lib.static_text(text="Hi") == UIElement(kind="QLabel", props={"text": "Hi"})
    assert lib.menu_bar() == UIElement(kind="QMenuBar", props={})
    assert lib.tool_bar(title="T") == UIElement(kind="QToolBar", props={"title": "T"})
    assert lib.separator(horizontal=True) == UIElement(
        kind="QFrame",
        props={"frameShape": "HLine", "frameShadow": "Sunken"},
    )
    assert lib.scroll_panel() == UIElement(
        kind="QScrollArea",
        props={"widgetResizable": True},
    )
    assert lib.spacer(width=8, height=0) == UIElement(
        kind="QWidget",
        props={"minimumWidth": 8, "maximumWidth": 8},
    )


def test_tk_waves_bcd_emitters() -> None:
    lib = TkUnifiedNativeLibrary()
    assert lib.text_area(text="x", read_only=False) == UIElement(
        kind="Text",
        props={
            "text": "x",
            "height": 6,
            "width": 48,
            "wrap": "word",
            "state": "normal",
        },
    )
    assert lib.static_text(text="Hi") == UIElement(kind="ttk_Label", props={"text": "Hi"})
    assert lib.menu_bar() == UIElement(kind="Menu", props={"tearoff": 0})
    assert lib.tool_bar(title="ignored") == UIElement(
        kind="ttk_Frame",
        props={"padding": 2},
    )
    assert lib.separator(horizontal=False) == UIElement(
        kind="Separator",
        props={"orient": "vertical"},
    )
    assert lib.scroll_panel() == UIElement(
        kind="Canvas",
        props={"width": 240, "height": 160, "background": "white"},
    )
    assert lib.spacer(height=12) == UIElement(kind="ttk_Frame", props={"height": 12})


def test_dpg_waves_bcd_emitters() -> None:
    lib = DpgUnifiedNativeLibrary()
    assert lib.text_area(text="m", read_only=True) == UIElement(
        kind="DpgInputText",
        props={"value": "m", "multiline": True, "readonly": True},
    )
    assert lib.static_text(text="Hi") == UIElement(kind="DpgText", props={"default_value": "Hi"})
    assert lib.menu_bar() == UIElement(kind="DpgMenuBar", props={})
    assert lib.tool_bar(title="Bar") == UIElement(
        kind="DpgGroup",
        props={"horizontal": True, "label": "Bar"},
    )
    assert lib.separator() == UIElement(kind="DpgSeparator", props={})
    assert lib.scroll_panel() == UIElement(
        kind="DpgChildWindow",
        props={
            "width": 240,
            "height": 180,
            "horizontal_scrollbar": True,
            "no_scrollbar": False,
        },
    )
    assert lib.spacer(width=4, height=6) == UIElement(
        kind="DpgSpacer",
        props={"width": 4, "height": 6},
    )
