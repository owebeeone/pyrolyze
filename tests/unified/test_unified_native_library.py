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
