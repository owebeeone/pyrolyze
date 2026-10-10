from __future__ import annotations

import ast
import sys
from types import ModuleType, SimpleNamespace

import pytest

from pyrolyze.compiler.kernels.v3_14.rewrite import _collect_imported_annotated_symbols


@pytest.fixture
def lazy_ui_library(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    resolved: list[str] = []

    def widget(*, text: str = "") -> None:
        pass

    class LazyLibrary(type):
        def __getattr__(cls, name: str) -> object:
            if name == "CBroken":
                raise RuntimeError("invalid widget group")
            if name in cls.UI_INTERFACE.entries:
                resolved.append(name)
                return widget
            raise AttributeError(name)

    class Library(metaclass=LazyLibrary):
        UI_INTERFACE = SimpleNamespace(entries={"CLabel": None, "CButton": None, "CBroken": None})

    module = ModuleType("selective_ui_fixture")
    module.Library = Library
    monkeypatch.setitem(sys.modules, module.__name__, module)
    return resolved


@pytest.mark.parametrize("body", (
    "Qt.CLabel(text='hello')",
    "with Qt.CLabel():\n    pass",
    "label = Qt.CLabel\nlabel(text='hello')",
    "def nested():\n    Qt.CLabel(text='hello')",
))
def test_only_referenced_ui_members_are_inspected(
    lazy_ui_library: list[str], body: str
) -> None:
    tree = ast.parse("from selective_ui_fixture import Library as Qt\n" + body)
    _, components, parameters, _, _ = _collect_imported_annotated_symbols(tree)
    assert lazy_ui_library == ["CLabel"]
    assert components == {"Qt.CLabel"}
    assert parameters["Qt.CLabel"] == ("text",)


def test_unused_import_does_not_resolve_ui_members(lazy_ui_library: list[str]) -> None:
    _collect_imported_annotated_symbols(ast.parse("from selective_ui_fixture import Library as Qt"))
    assert lazy_ui_library == []


def test_repeated_references_are_inspected_once(lazy_ui_library: list[str]) -> None:
    _collect_imported_annotated_symbols(ast.parse(
        "from selective_ui_fixture import Library as Qt\nQt.CLabel()\nQt.CLabel()"
    ))
    assert lazy_ui_library == ["CLabel"]


def test_unknown_member_does_not_trigger_catalog_fallback(lazy_ui_library: list[str]) -> None:
    _, components, _, _, _ = _collect_imported_annotated_symbols(ast.parse(
        "from selective_ui_fixture import Library as Qt\nQt.CUnknown()"
    ))
    assert not components
    assert lazy_ui_library == []


def test_known_broken_member_failure_is_not_swallowed(lazy_ui_library: list[str]) -> None:
    with pytest.raises(RuntimeError, match="invalid widget group"):
        _collect_imported_annotated_symbols(ast.parse(
            "from selective_ui_fixture import Library as Qt\nQt.CBroken()"
        ))


def test_dynamic_access_does_not_trigger_catalog_fallback(lazy_ui_library: list[str]) -> None:
    _collect_imported_annotated_symbols(ast.parse(
        "from selective_ui_fixture import Library as Qt\ngetattr(Qt, selected)()"
    ))
    assert lazy_ui_library == []
