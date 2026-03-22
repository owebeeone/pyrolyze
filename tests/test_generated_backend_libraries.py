from __future__ import annotations

import importlib
import inspect

from frozendict import frozendict

from pyrolyze.api import MISSING
from pyrolyze.backends.model import UiInterface, UiMethodSpec, UiWidgetSpec


def test_generated_backend_libraries_import() -> None:
    pyside6_module = importlib.import_module("pyrolyze.backends.pyside6.generated_library")
    tkinter_module = importlib.import_module("pyrolyze.backends.tkinter.generated_library")

    assert hasattr(pyside6_module, "PySide6UiLibrary")
    assert hasattr(tkinter_module, "TkinterUiLibrary")

    assert isinstance(pyside6_module.PySide6UiLibrary.UI_INTERFACE, UiInterface)
    assert isinstance(tkinter_module.TkinterUiLibrary.UI_INTERFACE, UiInterface)
    assert isinstance(pyside6_module.PySide6UiLibrary.WIDGET_SPECS, frozendict)
    assert isinstance(tkinter_module.TkinterUiLibrary.WIDGET_SPECS, frozendict)
    assert all(isinstance(spec, UiWidgetSpec) for spec in pyside6_module.PySide6UiLibrary.WIDGET_SPECS.values())
    assert all(isinstance(spec, UiWidgetSpec) for spec in tkinter_module.TkinterUiLibrary.WIDGET_SPECS.values())

    qlabel_signature = inspect.signature(pyside6_module.PySide6UiLibrary.CQLabel)
    assert "enabled" in qlabel_signature.parameters
    assert qlabel_signature.parameters["enabled"].default is MISSING

    qpush_signature = inspect.signature(pyside6_module.PySide6UiLibrary.CQPushButton)
    assert "geometry_x" in qpush_signature.parameters
    assert "geometry_height" in qpush_signature.parameters

    qpush_button_spec = pyside6_module.PySide6UiLibrary.WIDGET_SPECS["QPushButton"]
    assert "setGeometry" in qpush_button_spec.methods
    assert isinstance(qpush_button_spec.methods["setGeometry"], UiMethodSpec)
    assert qpush_button_spec.methods["setGeometry"].source_props == (
        "geometry_x",
        "geometry_y",
        "geometry_width",
        "geometry_height",
    )

    qspin_box_spec = pyside6_module.PySide6UiLibrary.WIDGET_SPECS["QSpinBox"]
    assert qspin_box_spec.methods["setRange"].source_props == ("minimum", "maximum")
    assert qspin_box_spec.methods["setRange"].constructor_equivalent is True
