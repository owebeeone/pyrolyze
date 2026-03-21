from __future__ import annotations

from pathlib import Path
import sys

import pytest


from pyrolyze_tools.generate_semantic_library import (
    DiscoveredProperty,
    DiscoveredWidgetClass,
    _extract_multiarg_setter_methods,
    _extract_pyside6_parameters,
    _extract_qt_properties,
    discover_modules,
    discover_widget_classes,
    generate_library_source,
    main,
    write_generated_library,
)


def _write_fake_widget_package(root: Path) -> None:
    package_dir = root / "fakewidgets"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("from .widgets import AlphaWidget, VariadicWidget\n")
    (package_dir / "__main__.py").write_text("raise RuntimeError('should not import __main__')\n")
    (package_dir / "base.py").write_text(
        "class WidgetBase:\n"
        "    pass\n"
    )
    (package_dir / "widgets.py").write_text(
        "from __future__ import annotations\n"
        "from .base import WidgetBase\n"
        "\n"
        "class AlphaWidget(WidgetBase):\n"
        "    def __init__(self, title: str, *, visible: bool = True, count: int = 0) -> None:\n"
        "        self.title = title\n"
        "        self.visible = visible\n"
        "        self.count = count\n"
        "\n"
        "class VariadicWidget(WidgetBase):\n"
        "    def __init__(self, parent=None, **kw) -> None:\n"
        "        self.parent = parent\n"
        "        self.kw = kw\n"
    )
    (package_dir / "extras.py").write_text(
        "class NotAWidget:\n"
        "    pass\n"
    )


def test_discover_modules_recurses_package(tmp_path: Path, monkeypatch) -> None:
    _write_fake_widget_package(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    modules = discover_modules("fakewidgets")

    assert "fakewidgets" in modules
    assert "fakewidgets.base" in modules
    assert "fakewidgets.widgets" in modules
    assert "fakewidgets.extras" in modules
    assert "fakewidgets.__main__" not in modules


def test_discover_widget_classes_filters_by_base_class(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_fake_widget_package(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    widgets = discover_widget_classes(
        "fakewidgets",
        widget_base_specs=("fakewidgets.base:WidgetBase",),
    )

    assert [widget.class_name for widget in widgets] == ["AlphaWidget", "VariadicWidget"]
    assert widgets[0].callable_name == "alpha_widget"
    assert widgets[1].callable_name == "variadic_widget"


def test_generate_library_source_renders_explicit_parameters_and_coercions(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_fake_widget_package(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    widgets = discover_widget_classes(
        "fakewidgets",
        widget_base_specs=("fakewidgets.base:WidgetBase",),
    )
    source = generate_library_source("fakewidgets", widgets)

    assert "class FakewidgetsSemanticLibrary:" in source
    assert 'LIBRARY_ID: ClassVar[str] = "generated.fakewidgets"' in source
    assert "def alpha_widget(" in source
    assert "title: str" in source
    assert "visible: bool = True" in source
    assert "count: int = 0" in source
    assert "visible=bool(visible)" in source
    assert "count=int(count)" in source
    assert "# NOTE: original signature for VariadicWidget includes omitted variadic arguments" in source


def test_generate_library_source_renders_qt_property_metadata() -> None:
    source = generate_library_source(
        "PySide6",
        [
            DiscoveredWidgetClass(
                module_name="PySide6.QtWidgets",
                class_name="QPushButton",
                callable_name="q_push_button",
                parameters=(),
                properties=(
                    DiscoveredProperty(
                        name="text",
                        type_name="QString",
                        readable=True,
                        writable=True,
                    ),
                ),
            )
        ],
    )

    assert 'QT_PROPERTY_GETTER: ClassVar[str] = "property"' in source
    assert 'QT_PROPERTY_SETTER: ClassVar[str] = "setProperty"' in source
    assert '"QPushButton": {' in source
    assert '"text": ("QString", True, True),' in source


def test_write_generated_library_uses_package_name_for_output(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_fake_widget_package(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    widgets = discover_widget_classes(
        "fakewidgets",
        widget_base_specs=("fakewidgets.base:WidgetBase",),
    )

    out_file = write_generated_library(
        "fakewidgets",
        widgets,
        output_dir=tmp_path / "out",
    )

    assert out_file.name == "fakewidgets.py"
    assert out_file.exists()
    assert "class FakewidgetsSemanticLibrary:" in out_file.read_text()


def test_main_generates_file_from_module_name(tmp_path: Path, monkeypatch) -> None:
    _write_fake_widget_package(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    out_dir = tmp_path / "generated"
    exit_code = main(
        [
            "fakewidgets",
            "--widget-base",
            "fakewidgets.base:WidgetBase",
            "--output-dir",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    assert (out_dir / "fakewidgets.py").exists()


def test_extract_pyside6_parameters_prefers_stub_signatures() -> None:
    pytest.importorskip("PySide6.QtWidgets")
    from PySide6.QtWidgets import QPushButton

    parameters = _extract_pyside6_parameters(QPushButton)
    names = [parameter.name for parameter in parameters]

    assert "text" in names
    assert "parent" in names
    assert "autoDefault" in names
    assert "default" in names
    assert "flat" in names


def test_extract_qt_properties_uses_metaobject() -> None:
    pytest.importorskip("PySide6.QtWidgets")
    from PySide6.QtWidgets import QPushButton

    properties = {prop.name: prop for prop in _extract_qt_properties(QPushButton)}

    assert properties["text"].type_name == "QString"
    assert properties["text"].readable is True
    assert properties["text"].writable is True
    assert properties["enabled"].type_name == "bool"


def test_extract_pyside6_multiarg_setters_ignores_single_value_property_setters() -> None:
    pytest.importorskip("PySide6.QtWidgets")
    from PySide6.QtWidgets import QPushButton

    methods = {method.name for method in _extract_multiarg_setter_methods("PySide6", QPushButton)}

    assert "setGeometry" in methods
    assert "setText" not in methods


def test_extract_tkinter_multiarg_setters_filters_generic_setvar() -> None:
    pytest.importorskip("tkinter")
    from tkinter import Scrollbar

    methods = {method.name for method in _extract_multiarg_setter_methods("tkinter", Scrollbar)}

    assert "set" in methods
    assert "setvar" not in methods
