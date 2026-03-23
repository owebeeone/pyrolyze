from __future__ import annotations

import importlib
import inspect

from frozendict import frozendict

from pyrolyze.api import MISSING
from pyrolyze.backends.model import MountReplayKind, UiEventSpec, UiInterface, UiMethodSpec, UiWidgetSpec


def test_generated_backend_libraries_import() -> None:
    common_module = importlib.import_module("pyrolyze.backends.common.generated_library")
    pyside6_module = importlib.import_module("pyrolyze.backends.pyside6.generated_library")
    tkinter_module = importlib.import_module("pyrolyze.backends.tkinter.generated_library")

    assert hasattr(common_module, "CoreUiLibrary")
    assert hasattr(pyside6_module, "PySide6UiLibrary")
    assert hasattr(tkinter_module, "TkinterUiLibrary")

    assert isinstance(common_module.CoreUiLibrary.UI_INTERFACE, UiInterface)
    assert isinstance(pyside6_module.PySide6UiLibrary.UI_INTERFACE, UiInterface)
    assert isinstance(tkinter_module.TkinterUiLibrary.UI_INTERFACE, UiInterface)
    assert common_module.CoreUiLibrary.UI_INTERFACE.name == "CoreUiLibrary"
    assert common_module.CoreUiLibrary.UI_INTERFACE.build_element(
        "section",
        title="Root",
        accent="blue",
    ).kind == "section"
    assert hasattr(common_module.CoreUiLibrary.section, "_pyrolyze_meta")
    assert hasattr(common_module.CoreUiLibrary.button, "_pyrolyze_meta")
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

    qaction_signature = inspect.signature(pyside6_module.PySide6UiLibrary.CQAction)
    assert "separator" in qaction_signature.parameters
    assert "on_triggered" in qaction_signature.parameters

    qhbox_signature = inspect.signature(pyside6_module.PySide6UiLibrary.CQHBoxLayout)
    assert qhbox_signature.parameters["parent"].default is Ellipsis

    qvbox_signature = inspect.signature(pyside6_module.PySide6UiLibrary.CQVBoxLayout)
    assert qvbox_signature.parameters["parent"].default is Ellipsis

    tk_combobox_signature = inspect.signature(tkinter_module.TkinterUiLibrary.CCombobox)
    assert "value" in tk_combobox_signature.parameters
    tk_button_signature = inspect.signature(tkinter_module.TkinterUiLibrary.CButton)
    assert "text" in tk_button_signature.parameters
    assert "on_command" in tk_button_signature.parameters
    tk_entry_signature = inspect.signature(tkinter_module.TkinterUiLibrary.CEntry)
    assert "show" in tk_entry_signature.parameters
    assert "on_key_release" in tk_entry_signature.parameters
    tk_frame_signature = inspect.signature(tkinter_module.TkinterUiLibrary.CFrame)
    assert "width" in tk_frame_signature.parameters

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

    qgrid_layout_spec = pyside6_module.PySide6UiLibrary.WIDGET_SPECS["QGridLayout"]
    assert "widget" in qgrid_layout_spec.mount_points
    assert qgrid_layout_spec.mount_points["widget"].apply_method_name == "addWidget"
    assert qgrid_layout_spec.mount_points["widget"].detach_method_name == "removeWidget"
    assert "layout" in qgrid_layout_spec.mount_points
    assert qgrid_layout_spec.mount_points["layout"].apply_method_name == "addLayout"
    assert qgrid_layout_spec.mount_points["layout"].detach_method_name == "removeItem"

    qmenu_bar_spec = pyside6_module.PySide6UiLibrary.WIDGET_SPECS["QMenuBar"]
    assert "action" in qmenu_bar_spec.mount_points
    assert qmenu_bar_spec.mount_points["action"].params == ()

    qaction_spec = pyside6_module.PySide6UiLibrary.WIDGET_SPECS["QAction"]
    assert "setSeparator" in qaction_spec.methods
    assert "on_triggered" in qaction_spec.events
    assert qaction_spec.events["on_triggered"].signal_name == "triggered"
    assert "menu" in qaction_spec.mount_points
    assert qaction_spec.mount_points["menu"].apply_method_name == "setMenu"
    qwidget_spec = pyside6_module.PySide6UiLibrary.WIDGET_SPECS["QWidget"]
    assert "setHidden" not in qwidget_spec.methods
    assert "setContextMenuPolicy" not in qwidget_spec.methods

    tk_combobox_spec = tkinter_module.TkinterUiLibrary.WIDGET_SPECS["Combobox"]
    assert "set" in tk_combobox_spec.methods
    tk_button_spec = tkinter_module.TkinterUiLibrary.WIDGET_SPECS["tkinter_Button"]
    assert "text" in tk_button_spec.props
    assert "command" not in tk_button_spec.props
    assert "on_command" in tk_button_spec.events
    assert tk_button_spec.events["on_command"].signal_name == "command"
    ttk_button_spec = tkinter_module.TkinterUiLibrary.WIDGET_SPECS["ttk_Button"]
    assert "text" in ttk_button_spec.props
    assert "on_command" in ttk_button_spec.events
    tk_entry_spec = tkinter_module.TkinterUiLibrary.WIDGET_SPECS["tkinter_Entry"]
    assert "show" in tk_entry_spec.props
    assert "on_key_release" in tk_entry_spec.events
    assert tk_entry_spec.events["on_key_release"].signal_name == "bind:<KeyRelease>"
    tk_frame_spec = tkinter_module.TkinterUiLibrary.WIDGET_SPECS["tkinter_Frame"]
    assert "pack" in tk_frame_spec.mount_points
    assert tk_frame_spec.mount_points["pack"].append_method_name == "pack"
    assert tk_frame_spec.default_child_mount_point_name == "pack"
    assert tk_frame_spec.default_attach_mount_point_names == ("pack",)
    assert "grid" in tk_frame_spec.mount_points
    assert tk_frame_spec.mount_points["grid"].apply_method_name == "grid"
    assert tk_frame_spec.mount_points["grid"].detach_method_name == "grid_forget"

    notebook_spec = tkinter_module.TkinterUiLibrary.WIDGET_SPECS["Notebook"]
    panedwindow_spec = tkinter_module.TkinterUiLibrary.WIDGET_SPECS["Panedwindow"]
    raw_panedwindow_kind = tkinter_module.TkinterUiLibrary.UI_INTERFACE.entries["CPanedWindow"].kind
    tix_panedwindow_kind = tkinter_module.TkinterUiLibrary.UI_INTERFACE.entries["CTixPanedWindow"].kind
    raw_panedwindow_spec = tkinter_module.TkinterUiLibrary.WIDGET_SPECS[raw_panedwindow_kind]
    assert isinstance(notebook_spec, UiWidgetSpec)
    assert isinstance(panedwindow_spec, UiWidgetSpec)
    assert "tab" in notebook_spec.mount_points
    assert notebook_spec.mount_points["tab"].place_method_name == "insert"
    assert notebook_spec.mount_points["tab"].append_method_name == "add"
    assert notebook_spec.mount_points["tab"].detach_method_name == "forget"
    assert notebook_spec.mount_points["tab"].replay_kind is MountReplayKind.INDEX
    assert notebook_spec.default_child_mount_point_name == "tab"
    assert notebook_spec.default_attach_mount_point_names == ("tab",)

    assert "pane" in panedwindow_spec.mount_points
    assert panedwindow_spec.mount_points["pane"].place_method_name == "insert"
    assert panedwindow_spec.mount_points["pane"].append_method_name == "add"
    assert panedwindow_spec.mount_points["pane"].detach_method_name == "forget"
    assert panedwindow_spec.mount_points["pane"].replay_kind is MountReplayKind.INDEX
    assert panedwindow_spec.default_child_mount_point_name == "pane"
    assert panedwindow_spec.default_attach_mount_point_names == ("pane",)

    assert raw_panedwindow_kind != tix_panedwindow_kind
    assert tkinter_module.TkinterUiLibrary.UI_INTERFACE.entries["CButton"].kind != tkinter_module.TkinterUiLibrary.UI_INTERFACE.entries["CTtkButton"].kind
    assert "pane" in raw_panedwindow_spec.mount_points
    assert raw_panedwindow_spec.mount_points["pane"].place_method_name is None
    assert raw_panedwindow_spec.mount_points["pane"].append_method_name == "add"
    assert raw_panedwindow_spec.mount_points["pane"].detach_method_name == "remove"
    assert raw_panedwindow_spec.default_child_mount_point_name == "pane"
    assert raw_panedwindow_spec.default_attach_mount_point_names == ("pane",)

    assert tkinter_module.TkinterUiLibrary.mounts.tab.name == "tab"
    assert tkinter_module.TkinterUiLibrary.mounts.pane.name == "pane"
