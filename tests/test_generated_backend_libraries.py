from __future__ import annotations

import importlib
import inspect

from frozendict import frozendict

from pyrolyze.api import MISSING
from pyrolyze.backends.model import UiEventSpec, UiInterface, UiMethodSpec, UiWidgetSpec


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
    assert "icon" not in qpush_signature.parameters
    assert "text" in qpush_signature.parameters
    assert "geometry_x" in qpush_signature.parameters
    assert "geometry_height" in qpush_signature.parameters

    qhbox_signature = inspect.signature(pyside6_module.PySide6UiLibrary.CQHBoxLayout)
    assert qhbox_signature.parameters["parent"].default is Ellipsis

    qvbox_signature = inspect.signature(pyside6_module.PySide6UiLibrary.CQVBoxLayout)
    assert qvbox_signature.parameters["parent"].default is Ellipsis

    qpush_button_spec = pyside6_module.PySide6UiLibrary.WIDGET_SPECS["QPushButton"]
    assert "setGeometry" in qpush_button_spec.methods
    assert isinstance(qpush_button_spec.methods["setGeometry"], UiMethodSpec)
    assert qpush_button_spec.methods["setGeometry"].source_props == (
        "geometry_x",
        "geometry_y",
        "geometry_width",
        "geometry_height",
    )
    assert "on_clicked" in qpush_button_spec.events
    assert isinstance(qpush_button_spec.events["on_clicked"], UiEventSpec)
    assert qpush_button_spec.events["on_clicked"].signal_name == "clicked"

    qspin_box_spec = pyside6_module.PySide6UiLibrary.WIDGET_SPECS["QSpinBox"]
    assert qspin_box_spec.methods["setRange"].source_props == ("minimum", "maximum")
    assert qspin_box_spec.methods["setRange"].constructor_equivalent is True

    assert "QWidget" in pyside6_module.PySide6UiLibrary.WIDGET_SPECS
    assert "QLayout" in pyside6_module.PySide6UiLibrary.WIDGET_SPECS
    assert "QAction" in pyside6_module.PySide6UiLibrary.WIDGET_SPECS

    qwidget_spec = pyside6_module.PySide6UiLibrary.WIDGET_SPECS["QWidget"]
    assert "layout" in qwidget_spec.mount_points
    assert qwidget_spec.mount_points["layout"].apply_method_name == "setLayout"

    qmain_window_spec = pyside6_module.PySide6UiLibrary.WIDGET_SPECS["QMainWindow"]
    assert "central_widget" in qmain_window_spec.mount_points
    assert qmain_window_spec.mount_points["central_widget"].apply_method_name == "setCentralWidget"

    qbox_layout_spec = pyside6_module.PySide6UiLibrary.WIDGET_SPECS["QBoxLayout"]
    assert "widget" in qbox_layout_spec.mount_points
    assert qbox_layout_spec.mount_points["widget"].place_method_name == "insertWidget"
    assert qbox_layout_spec.mount_points["widget"].detach_method_name == "removeWidget"

    qaction_spec = pyside6_module.PySide6UiLibrary.WIDGET_SPECS["QAction"]
    assert "menu" in qaction_spec.mount_points
    assert qaction_spec.mount_points["menu"].apply_method_name == "setMenu"
