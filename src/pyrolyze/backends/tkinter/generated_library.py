"""Generated UI interface stubs for discovered widgets."""

from __future__ import annotations

from typing import Any, ClassVar

from frozendict import frozendict

from pyrolyze.api import MISSING, MissingType, UIElement, call_native, pyrolyse, ui_interface
from pyrolyze.backends.model import (
    AccessorKind,
    ChildPolicy,
    FillPolicy,
    MethodMode,
    PropMode,
    TypeRef,
    UiInterface,
    UiInterfaceEntry,
    UiMethodSpec,
    UiParamSpec,
    UiPropSpec,
    UiWidgetSpec,
)


@ui_interface
class TkinterUiLibrary:
    ROOT_MODULE: ClassVar[str] = "tkinter"

    UI_INTERFACE: ClassVar[UiInterface] = UiInterface(
        name="TkinterUiLibrary",
        owner=None,
        entries=frozendict({
            "CBalloon": UiInterfaceEntry(public_name="CBalloon", kind="Balloon"),
            "CButton": UiInterfaceEntry(public_name="CButton", kind="Button"),
            "CTtkButton": UiInterfaceEntry(public_name="CTtkButton", kind="Button"),
            "CButtonBox": UiInterfaceEntry(public_name="CButtonBox", kind="ButtonBox"),
            "CCObjView": UiInterfaceEntry(public_name="CCObjView", kind="CObjView"),
            "CCanvas": UiInterfaceEntry(public_name="CCanvas", kind="Canvas"),
            "CCheckList": UiInterfaceEntry(public_name="CCheckList", kind="CheckList"),
            "CCheckbutton": UiInterfaceEntry(public_name="CCheckbutton", kind="Checkbutton"),
            "CTtkCheckbutton": UiInterfaceEntry(public_name="CTtkCheckbutton", kind="Checkbutton"),
            "CComboBox": UiInterfaceEntry(public_name="CComboBox", kind="ComboBox"),
            "CCombobox": UiInterfaceEntry(public_name="CCombobox", kind="Combobox"),
            "CControl": UiInterfaceEntry(public_name="CControl", kind="Control"),
            "CDialog": UiInterfaceEntry(public_name="CDialog", kind="Dialog"),
            "CDialogShell": UiInterfaceEntry(public_name="CDialogShell", kind="DialogShell"),
            "CDirList": UiInterfaceEntry(public_name="CDirList", kind="DirList"),
            "CDirSelectBox": UiInterfaceEntry(public_name="CDirSelectBox", kind="DirSelectBox"),
            "CDirSelectDialog": UiInterfaceEntry(public_name="CDirSelectDialog", kind="DirSelectDialog"),
            "CDirTree": UiInterfaceEntry(public_name="CDirTree", kind="DirTree"),
            "CEntry": UiInterfaceEntry(public_name="CEntry", kind="Entry"),
            "CTtkEntry": UiInterfaceEntry(public_name="CTtkEntry", kind="Entry"),
            "CExFileSelectBox": UiInterfaceEntry(public_name="CExFileSelectBox", kind="ExFileSelectBox"),
            "CExFileSelectDialog": UiInterfaceEntry(public_name="CExFileSelectDialog", kind="ExFileSelectDialog"),
            "CFileEntry": UiInterfaceEntry(public_name="CFileEntry", kind="FileEntry"),
            "CFileSelectBox": UiInterfaceEntry(public_name="CFileSelectBox", kind="FileSelectBox"),
            "CFileSelectDialog": UiInterfaceEntry(public_name="CFileSelectDialog", kind="FileSelectDialog"),
            "CFrame": UiInterfaceEntry(public_name="CFrame", kind="Frame"),
            "CTtkFrame": UiInterfaceEntry(public_name="CTtkFrame", kind="Frame"),
            "CGrid": UiInterfaceEntry(public_name="CGrid", kind="Grid"),
            "CHList": UiInterfaceEntry(public_name="CHList", kind="HList"),
            "CInputOnly": UiInterfaceEntry(public_name="CInputOnly", kind="InputOnly"),
            "CLabel": UiInterfaceEntry(public_name="CLabel", kind="Label"),
            "CTtkLabel": UiInterfaceEntry(public_name="CTtkLabel", kind="Label"),
            "CLabelEntry": UiInterfaceEntry(public_name="CLabelEntry", kind="LabelEntry"),
            "CLabelFrame": UiInterfaceEntry(public_name="CLabelFrame", kind="LabelFrame"),
            "CTixLabelFrame": UiInterfaceEntry(public_name="CTixLabelFrame", kind="LabelFrame"),
            "CLabeledScale": UiInterfaceEntry(public_name="CLabeledScale", kind="LabeledScale"),
            "CLabelframe": UiInterfaceEntry(public_name="CLabelframe", kind="Labelframe"),
            "CListNoteBook": UiInterfaceEntry(public_name="CListNoteBook", kind="ListNoteBook"),
            "CListbox": UiInterfaceEntry(public_name="CListbox", kind="Listbox"),
            "CMenu": UiInterfaceEntry(public_name="CMenu", kind="Menu"),
            "CMenubutton": UiInterfaceEntry(public_name="CMenubutton", kind="Menubutton"),
            "CTtkMenubutton": UiInterfaceEntry(public_name="CTtkMenubutton", kind="Menubutton"),
            "CMessage": UiInterfaceEntry(public_name="CMessage", kind="Message"),
            "CMeter": UiInterfaceEntry(public_name="CMeter", kind="Meter"),
            "CNoteBook": UiInterfaceEntry(public_name="CNoteBook", kind="NoteBook"),
            "CNoteBookFrame": UiInterfaceEntry(public_name="CNoteBookFrame", kind="NoteBookFrame"),
            "CNotebook": UiInterfaceEntry(public_name="CNotebook", kind="Notebook"),
            "COptionMenu": UiInterfaceEntry(public_name="COptionMenu", kind="OptionMenu"),
            "CTixOptionMenu": UiInterfaceEntry(public_name="CTixOptionMenu", kind="OptionMenu"),
            "CTtkOptionMenu": UiInterfaceEntry(public_name="CTtkOptionMenu", kind="OptionMenu"),
            "CPanedWindow": UiInterfaceEntry(public_name="CPanedWindow", kind="PanedWindow"),
            "CTixPanedWindow": UiInterfaceEntry(public_name="CTixPanedWindow", kind="PanedWindow"),
            "CPanedwindow": UiInterfaceEntry(public_name="CPanedwindow", kind="Panedwindow"),
            "CPopupMenu": UiInterfaceEntry(public_name="CPopupMenu", kind="PopupMenu"),
            "CProgressbar": UiInterfaceEntry(public_name="CProgressbar", kind="Progressbar"),
            "CRadiobutton": UiInterfaceEntry(public_name="CRadiobutton", kind="Radiobutton"),
            "CTtkRadiobutton": UiInterfaceEntry(public_name="CTtkRadiobutton", kind="Radiobutton"),
            "CResizeHandle": UiInterfaceEntry(public_name="CResizeHandle", kind="ResizeHandle"),
            "CScale": UiInterfaceEntry(public_name="CScale", kind="Scale"),
            "CTtkScale": UiInterfaceEntry(public_name="CTtkScale", kind="Scale"),
            "CScrollbar": UiInterfaceEntry(public_name="CScrollbar", kind="Scrollbar"),
            "CTtkScrollbar": UiInterfaceEntry(public_name="CTtkScrollbar", kind="Scrollbar"),
            "CScrolledGrid": UiInterfaceEntry(public_name="CScrolledGrid", kind="ScrolledGrid"),
            "CScrolledHList": UiInterfaceEntry(public_name="CScrolledHList", kind="ScrolledHList"),
            "CScrolledListBox": UiInterfaceEntry(public_name="CScrolledListBox", kind="ScrolledListBox"),
            "CScrolledTList": UiInterfaceEntry(public_name="CScrolledTList", kind="ScrolledTList"),
            "CScrolledtextScrolledText": UiInterfaceEntry(public_name="CScrolledtextScrolledText", kind="ScrolledText"),
            "CTixScrolledText": UiInterfaceEntry(public_name="CTixScrolledText", kind="ScrolledText"),
            "CScrolledWindow": UiInterfaceEntry(public_name="CScrolledWindow", kind="ScrolledWindow"),
            "CSelect": UiInterfaceEntry(public_name="CSelect", kind="Select"),
            "CSeparator": UiInterfaceEntry(public_name="CSeparator", kind="Separator"),
            "CShell": UiInterfaceEntry(public_name="CShell", kind="Shell"),
            "CSizegrip": UiInterfaceEntry(public_name="CSizegrip", kind="Sizegrip"),
            "CSpinbox": UiInterfaceEntry(public_name="CSpinbox", kind="Spinbox"),
            "CTtkSpinbox": UiInterfaceEntry(public_name="CTtkSpinbox", kind="Spinbox"),
            "CStdButtonBox": UiInterfaceEntry(public_name="CStdButtonBox", kind="StdButtonBox"),
            "CTList": UiInterfaceEntry(public_name="CTList", kind="TList"),
            "CText": UiInterfaceEntry(public_name="CText", kind="Text"),
            "CTixSubWidget": UiInterfaceEntry(public_name="CTixSubWidget", kind="TixSubWidget"),
            "CTixWidget": UiInterfaceEntry(public_name="CTixWidget", kind="TixWidget"),
            "CTree": UiInterfaceEntry(public_name="CTree", kind="Tree"),
            "CTreeview": UiInterfaceEntry(public_name="CTreeview", kind="Treeview"),
            "C_dummyButton": UiInterfaceEntry(public_name="C_dummyButton", kind="_dummyButton"),
            "C_dummyCheckbutton": UiInterfaceEntry(public_name="C_dummyCheckbutton", kind="_dummyCheckbutton"),
            "C_dummyComboBox": UiInterfaceEntry(public_name="C_dummyComboBox", kind="_dummyComboBox"),
            "C_dummyDirList": UiInterfaceEntry(public_name="C_dummyDirList", kind="_dummyDirList"),
            "C_dummyDirSelectBox": UiInterfaceEntry(public_name="C_dummyDirSelectBox", kind="_dummyDirSelectBox"),
            "C_dummyEntry": UiInterfaceEntry(public_name="C_dummyEntry", kind="_dummyEntry"),
            "C_dummyExFileSelectBox": UiInterfaceEntry(public_name="C_dummyExFileSelectBox", kind="_dummyExFileSelectBox"),
            "C_dummyFileComboBox": UiInterfaceEntry(public_name="C_dummyFileComboBox", kind="_dummyFileComboBox"),
            "C_dummyFileSelectBox": UiInterfaceEntry(public_name="C_dummyFileSelectBox", kind="_dummyFileSelectBox"),
            "C_dummyFrame": UiInterfaceEntry(public_name="C_dummyFrame", kind="_dummyFrame"),
            "C_dummyHList": UiInterfaceEntry(public_name="C_dummyHList", kind="_dummyHList"),
            "C_dummyLabel": UiInterfaceEntry(public_name="C_dummyLabel", kind="_dummyLabel"),
            "C_dummyListbox": UiInterfaceEntry(public_name="C_dummyListbox", kind="_dummyListbox"),
            "C_dummyMenu": UiInterfaceEntry(public_name="C_dummyMenu", kind="_dummyMenu"),
            "C_dummyMenubutton": UiInterfaceEntry(public_name="C_dummyMenubutton", kind="_dummyMenubutton"),
            "C_dummyNoteBookFrame": UiInterfaceEntry(public_name="C_dummyNoteBookFrame", kind="_dummyNoteBookFrame"),
            "C_dummyPanedWindow": UiInterfaceEntry(public_name="C_dummyPanedWindow", kind="_dummyPanedWindow"),
            "C_dummyScrollbar": UiInterfaceEntry(public_name="C_dummyScrollbar", kind="_dummyScrollbar"),
            "C_dummyScrolledHList": UiInterfaceEntry(public_name="C_dummyScrolledHList", kind="_dummyScrolledHList"),
            "C_dummyScrolledListBox": UiInterfaceEntry(public_name="C_dummyScrolledListBox", kind="_dummyScrolledListBox"),
            "C_dummyStdButtonBox": UiInterfaceEntry(public_name="C_dummyStdButtonBox", kind="_dummyStdButtonBox"),
            "C_dummyTList": UiInterfaceEntry(public_name="C_dummyTList", kind="_dummyTList"),
            "C_dummyText": UiInterfaceEntry(public_name="C_dummyText", kind="_dummyText"),
        }),
    )

    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({
        "Balloon": UiWidgetSpec(
            kind="Balloon",
            mounted_type_name="tkinter.tix.Balloon",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Button": UiWidgetSpec(
            kind="Button",
            mounted_type_name="tkinter.Button",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Button": UiWidgetSpec(
            kind="Button",
            mounted_type_name="tkinter.ttk.Button",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "ButtonBox": UiWidgetSpec(
            kind="ButtonBox",
            mounted_type_name="tkinter.tix.ButtonBox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "CObjView": UiWidgetSpec(
            kind="CObjView",
            mounted_type_name="tkinter.tix.CObjView",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "widgetName": UiParamSpec(name="widgetName", annotation=None, default_repr='None'),
                "static_options": UiParamSpec(name="static_options", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
                "kw": UiParamSpec(name="kw", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "widgetName": UiPropSpec(name="widgetName", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='widgetName', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "static_options": UiPropSpec(name="static_options", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='static_options', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "kw": UiPropSpec(name="kw", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='kw', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Canvas": UiWidgetSpec(
            kind="Canvas",
            mounted_type_name="tkinter.Canvas",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "CheckList": UiWidgetSpec(
            kind="CheckList",
            mounted_type_name="tkinter.tix.CheckList",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
                "setstatus": UiMethodSpec(
                    name="setstatus",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="entrypath", annotation=None, default_repr=None),
                        UiParamSpec(name="mode", annotation=None, default_repr="'on'"),
                    ),
                    source_props=("entrypath", "mode"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Checkbutton": UiWidgetSpec(
            kind="Checkbutton",
            mounted_type_name="tkinter.Checkbutton",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Checkbutton": UiWidgetSpec(
            kind="Checkbutton",
            mounted_type_name="tkinter.ttk.Checkbutton",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "ComboBox": UiWidgetSpec(
            kind="ComboBox",
            mounted_type_name="tkinter.tix.ComboBox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Combobox": UiWidgetSpec(
            kind="Combobox",
            mounted_type_name="tkinter.ttk.Combobox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Control": UiWidgetSpec(
            kind="Control",
            mounted_type_name="tkinter.tix.Control",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Dialog": UiWidgetSpec(
            kind="Dialog",
            mounted_type_name="tkinter.dialog.Dialog",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "DialogShell": UiWidgetSpec(
            kind="DialogShell",
            mounted_type_name="tkinter.tix.DialogShell",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "DirList": UiWidgetSpec(
            kind="DirList",
            mounted_type_name="tkinter.tix.DirList",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "DirSelectBox": UiWidgetSpec(
            kind="DirSelectBox",
            mounted_type_name="tkinter.tix.DirSelectBox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "DirSelectDialog": UiWidgetSpec(
            kind="DirSelectDialog",
            mounted_type_name="tkinter.tix.DirSelectDialog",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "DirTree": UiWidgetSpec(
            kind="DirTree",
            mounted_type_name="tkinter.tix.DirTree",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Entry": UiWidgetSpec(
            kind="Entry",
            mounted_type_name="tkinter.Entry",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Entry": UiWidgetSpec(
            kind="Entry",
            mounted_type_name="tkinter.ttk.Entry",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "widget": UiParamSpec(name="widget", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "widget": UiPropSpec(name="widget", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='widget', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "ExFileSelectBox": UiWidgetSpec(
            kind="ExFileSelectBox",
            mounted_type_name="tkinter.tix.ExFileSelectBox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "ExFileSelectDialog": UiWidgetSpec(
            kind="ExFileSelectDialog",
            mounted_type_name="tkinter.tix.ExFileSelectDialog",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "FileEntry": UiWidgetSpec(
            kind="FileEntry",
            mounted_type_name="tkinter.tix.FileEntry",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "FileSelectBox": UiWidgetSpec(
            kind="FileSelectBox",
            mounted_type_name="tkinter.tix.FileSelectBox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "FileSelectDialog": UiWidgetSpec(
            kind="FileSelectDialog",
            mounted_type_name="tkinter.tix.FileSelectDialog",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Frame": UiWidgetSpec(
            kind="Frame",
            mounted_type_name="tkinter.Frame",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Frame": UiWidgetSpec(
            kind="Frame",
            mounted_type_name="tkinter.ttk.Frame",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Grid": UiWidgetSpec(
            kind="Grid",
            mounted_type_name="tkinter.tix.Grid",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
                "set": UiMethodSpec(
                    name="set",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="x", annotation=None, default_repr=None),
                        UiParamSpec(name="y", annotation=None, default_repr=None),
                        UiParamSpec(name="itemtype", annotation=None, default_repr='None'),
                    ),
                    source_props=("x", "y", "itemtype"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "HList": UiWidgetSpec(
            kind="HList",
            mounted_type_name="tkinter.tix.HList",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "InputOnly": UiWidgetSpec(
            kind="InputOnly",
            mounted_type_name="tkinter.tix.InputOnly",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Label": UiWidgetSpec(
            kind="Label",
            mounted_type_name="tkinter.Label",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Label": UiWidgetSpec(
            kind="Label",
            mounted_type_name="tkinter.ttk.Label",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "LabelEntry": UiWidgetSpec(
            kind="LabelEntry",
            mounted_type_name="tkinter.tix.LabelEntry",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "LabelFrame": UiWidgetSpec(
            kind="LabelFrame",
            mounted_type_name="tkinter.LabelFrame",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "LabelFrame": UiWidgetSpec(
            kind="LabelFrame",
            mounted_type_name="tkinter.tix.LabelFrame",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "LabeledScale": UiWidgetSpec(
            kind="LabeledScale",
            mounted_type_name="tkinter.ttk.LabeledScale",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "variable": UiParamSpec(name="variable", annotation=None, default_repr='None'),
                "from_": UiParamSpec(name="from_", annotation=None, default_repr='0'),
                "to": UiParamSpec(name="to", annotation=None, default_repr='10'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "variable": UiPropSpec(name="variable", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='variable', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "from_": UiPropSpec(name="from_", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='from_', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "to": UiPropSpec(name="to", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='to', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Labelframe": UiWidgetSpec(
            kind="Labelframe",
            mounted_type_name="tkinter.ttk.Labelframe",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "ListNoteBook": UiWidgetSpec(
            kind="ListNoteBook",
            mounted_type_name="tkinter.tix.ListNoteBook",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Listbox": UiWidgetSpec(
            kind="Listbox",
            mounted_type_name="tkinter.Listbox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Menu": UiWidgetSpec(
            kind="Menu",
            mounted_type_name="tkinter.Menu",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Menubutton": UiWidgetSpec(
            kind="Menubutton",
            mounted_type_name="tkinter.Menubutton",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Menubutton": UiWidgetSpec(
            kind="Menubutton",
            mounted_type_name="tkinter.ttk.Menubutton",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Message": UiWidgetSpec(
            kind="Message",
            mounted_type_name="tkinter.Message",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Meter": UiWidgetSpec(
            kind="Meter",
            mounted_type_name="tkinter.tix.Meter",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "NoteBook": UiWidgetSpec(
            kind="NoteBook",
            mounted_type_name="tkinter.tix.NoteBook",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "NoteBookFrame": UiWidgetSpec(
            kind="NoteBookFrame",
            mounted_type_name="tkinter.tix.NoteBookFrame",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "widgetName": UiParamSpec(name="widgetName", annotation=None, default_repr='None'),
                "static_options": UiParamSpec(name="static_options", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
                "kw": UiParamSpec(name="kw", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "widgetName": UiPropSpec(name="widgetName", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='widgetName', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "static_options": UiPropSpec(name="static_options", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='static_options', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "kw": UiPropSpec(name="kw", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='kw', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Notebook": UiWidgetSpec(
            kind="Notebook",
            mounted_type_name="tkinter.ttk.Notebook",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "OptionMenu": UiWidgetSpec(
            kind="OptionMenu",
            mounted_type_name="tkinter.OptionMenu",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "variable": UiParamSpec(name="variable", annotation=None, default_repr=None),
                "value": UiParamSpec(name="value", annotation=None, default_repr=None),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "variable": UiPropSpec(name="variable", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='variable', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "value": UiPropSpec(name="value", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='value', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "OptionMenu": UiWidgetSpec(
            kind="OptionMenu",
            mounted_type_name="tkinter.tix.OptionMenu",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "OptionMenu": UiWidgetSpec(
            kind="OptionMenu",
            mounted_type_name="tkinter.ttk.OptionMenu",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "variable": UiParamSpec(name="variable", annotation=None, default_repr=None),
                "default": UiParamSpec(name="default", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "variable": UiPropSpec(name="variable", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='variable', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "default": UiPropSpec(name="default", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='default', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "PanedWindow": UiWidgetSpec(
            kind="PanedWindow",
            mounted_type_name="tkinter.PanedWindow",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "PanedWindow": UiWidgetSpec(
            kind="PanedWindow",
            mounted_type_name="tkinter.tix.PanedWindow",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Panedwindow": UiWidgetSpec(
            kind="Panedwindow",
            mounted_type_name="tkinter.ttk.Panedwindow",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "PopupMenu": UiWidgetSpec(
            kind="PopupMenu",
            mounted_type_name="tkinter.tix.PopupMenu",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Progressbar": UiWidgetSpec(
            kind="Progressbar",
            mounted_type_name="tkinter.ttk.Progressbar",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Radiobutton": UiWidgetSpec(
            kind="Radiobutton",
            mounted_type_name="tkinter.Radiobutton",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Radiobutton": UiWidgetSpec(
            kind="Radiobutton",
            mounted_type_name="tkinter.ttk.Radiobutton",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "ResizeHandle": UiWidgetSpec(
            kind="ResizeHandle",
            mounted_type_name="tkinter.tix.ResizeHandle",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Scale": UiWidgetSpec(
            kind="Scale",
            mounted_type_name="tkinter.Scale",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Scale": UiWidgetSpec(
            kind="Scale",
            mounted_type_name="tkinter.ttk.Scale",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Scrollbar": UiWidgetSpec(
            kind="Scrollbar",
            mounted_type_name="tkinter.Scrollbar",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
                "set": UiMethodSpec(
                    name="set",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="first", annotation=None, default_repr=None),
                        UiParamSpec(name="last", annotation=None, default_repr=None),
                    ),
                    source_props=("first", "last"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Scrollbar": UiWidgetSpec(
            kind="Scrollbar",
            mounted_type_name="tkinter.ttk.Scrollbar",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
                "set": UiMethodSpec(
                    name="set",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="first", annotation=None, default_repr=None),
                        UiParamSpec(name="last", annotation=None, default_repr=None),
                    ),
                    source_props=("first", "last"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "ScrolledGrid": UiWidgetSpec(
            kind="ScrolledGrid",
            mounted_type_name="tkinter.tix.ScrolledGrid",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
                "set": UiMethodSpec(
                    name="set",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="x", annotation=None, default_repr=None),
                        UiParamSpec(name="y", annotation=None, default_repr=None),
                        UiParamSpec(name="itemtype", annotation=None, default_repr='None'),
                    ),
                    source_props=("x", "y", "itemtype"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "ScrolledHList": UiWidgetSpec(
            kind="ScrolledHList",
            mounted_type_name="tkinter.tix.ScrolledHList",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "ScrolledListBox": UiWidgetSpec(
            kind="ScrolledListBox",
            mounted_type_name="tkinter.tix.ScrolledListBox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "ScrolledTList": UiWidgetSpec(
            kind="ScrolledTList",
            mounted_type_name="tkinter.tix.ScrolledTList",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "ScrolledText": UiWidgetSpec(
            kind="ScrolledText",
            mounted_type_name="tkinter.scrolledtext.ScrolledText",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "ScrolledText": UiWidgetSpec(
            kind="ScrolledText",
            mounted_type_name="tkinter.tix.ScrolledText",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "ScrolledWindow": UiWidgetSpec(
            kind="ScrolledWindow",
            mounted_type_name="tkinter.tix.ScrolledWindow",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Select": UiWidgetSpec(
            kind="Select",
            mounted_type_name="tkinter.tix.Select",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Separator": UiWidgetSpec(
            kind="Separator",
            mounted_type_name="tkinter.ttk.Separator",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Shell": UiWidgetSpec(
            kind="Shell",
            mounted_type_name="tkinter.tix.Shell",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Sizegrip": UiWidgetSpec(
            kind="Sizegrip",
            mounted_type_name="tkinter.ttk.Sizegrip",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Spinbox": UiWidgetSpec(
            kind="Spinbox",
            mounted_type_name="tkinter.Spinbox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Spinbox": UiWidgetSpec(
            kind="Spinbox",
            mounted_type_name="tkinter.ttk.Spinbox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "StdButtonBox": UiWidgetSpec(
            kind="StdButtonBox",
            mounted_type_name="tkinter.tix.StdButtonBox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "TList": UiWidgetSpec(
            kind="TList",
            mounted_type_name="tkinter.tix.TList",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Text": UiWidgetSpec(
            kind="Text",
            mounted_type_name="tkinter.Text",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "TixSubWidget": UiWidgetSpec(
            kind="TixSubWidget",
            mounted_type_name="tkinter.tix.TixSubWidget",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
                "check_intermediate": UiParamSpec(name="check_intermediate", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "check_intermediate": UiPropSpec(name="check_intermediate", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='check_intermediate', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "TixWidget": UiWidgetSpec(
            kind="TixWidget",
            mounted_type_name="tkinter.tix.TixWidget",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "widgetName": UiParamSpec(name="widgetName", annotation=None, default_repr='None'),
                "static_options": UiParamSpec(name="static_options", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
                "kw": UiParamSpec(name="kw", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "widgetName": UiPropSpec(name="widgetName", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='widgetName', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "static_options": UiPropSpec(name="static_options", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='static_options', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "kw": UiPropSpec(name="kw", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='kw', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Tree": UiWidgetSpec(
            kind="Tree",
            mounted_type_name="tkinter.tix.Tree",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
                "setmode": UiMethodSpec(
                    name="setmode",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="entrypath", annotation=None, default_repr=None),
                        UiParamSpec(name="mode", annotation=None, default_repr="'none'"),
                    ),
                    source_props=("entrypath", "mode"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "Treeview": UiWidgetSpec(
            kind="Treeview",
            mounted_type_name="tkinter.ttk.Treeview",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
                "set": UiMethodSpec(
                    name="set",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="item", annotation=None, default_repr=None),
                        UiParamSpec(name="column", annotation=None, default_repr='None'),
                        UiParamSpec(name="value", annotation=None, default_repr='None'),
                    ),
                    source_props=("item", "column", "value"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyButton": UiWidgetSpec(
            kind="_dummyButton",
            mounted_type_name="tkinter.tix._dummyButton",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyCheckbutton": UiWidgetSpec(
            kind="_dummyCheckbutton",
            mounted_type_name="tkinter.tix._dummyCheckbutton",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyComboBox": UiWidgetSpec(
            kind="_dummyComboBox",
            mounted_type_name="tkinter.tix._dummyComboBox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyDirList": UiWidgetSpec(
            kind="_dummyDirList",
            mounted_type_name="tkinter.tix._dummyDirList",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyDirSelectBox": UiWidgetSpec(
            kind="_dummyDirSelectBox",
            mounted_type_name="tkinter.tix._dummyDirSelectBox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyEntry": UiWidgetSpec(
            kind="_dummyEntry",
            mounted_type_name="tkinter.tix._dummyEntry",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyExFileSelectBox": UiWidgetSpec(
            kind="_dummyExFileSelectBox",
            mounted_type_name="tkinter.tix._dummyExFileSelectBox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyFileComboBox": UiWidgetSpec(
            kind="_dummyFileComboBox",
            mounted_type_name="tkinter.tix._dummyFileComboBox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyFileSelectBox": UiWidgetSpec(
            kind="_dummyFileSelectBox",
            mounted_type_name="tkinter.tix._dummyFileSelectBox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyFrame": UiWidgetSpec(
            kind="_dummyFrame",
            mounted_type_name="tkinter.tix._dummyFrame",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyHList": UiWidgetSpec(
            kind="_dummyHList",
            mounted_type_name="tkinter.tix._dummyHList",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyLabel": UiWidgetSpec(
            kind="_dummyLabel",
            mounted_type_name="tkinter.tix._dummyLabel",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyListbox": UiWidgetSpec(
            kind="_dummyListbox",
            mounted_type_name="tkinter.tix._dummyListbox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyMenu": UiWidgetSpec(
            kind="_dummyMenu",
            mounted_type_name="tkinter.tix._dummyMenu",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyMenubutton": UiWidgetSpec(
            kind="_dummyMenubutton",
            mounted_type_name="tkinter.tix._dummyMenubutton",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyNoteBookFrame": UiWidgetSpec(
            kind="_dummyNoteBookFrame",
            mounted_type_name="tkinter.tix._dummyNoteBookFrame",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='0'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyPanedWindow": UiWidgetSpec(
            kind="_dummyPanedWindow",
            mounted_type_name="tkinter.tix._dummyPanedWindow",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyScrollbar": UiWidgetSpec(
            kind="_dummyScrollbar",
            mounted_type_name="tkinter.tix._dummyScrollbar",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
                "set": UiMethodSpec(
                    name="set",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="first", annotation=None, default_repr=None),
                        UiParamSpec(name="last", annotation=None, default_repr=None),
                    ),
                    source_props=("first", "last"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyScrolledHList": UiWidgetSpec(
            kind="_dummyScrolledHList",
            mounted_type_name="tkinter.tix._dummyScrolledHList",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyScrolledListBox": UiWidgetSpec(
            kind="_dummyScrolledListBox",
            mounted_type_name="tkinter.tix._dummyScrolledListBox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyStdButtonBox": UiWidgetSpec(
            kind="_dummyStdButtonBox",
            mounted_type_name="tkinter.tix._dummyStdButtonBox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyTList": UiWidgetSpec(
            kind="_dummyTList",
            mounted_type_name="tkinter.tix._dummyTList",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
        "_dummyText": UiWidgetSpec(
            kind="_dummyText",
            mounted_type_name="tkinter.tix._dummyText",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
            }),
            child_policy=ChildPolicy.NONE,
        ),
    })

    @classmethod
    # NOTE: a trailing `kwds` parameter enables PyRolyze's tail kwds optimization.
    # The compiler lowers matching wrappers so only actually passed arguments
    # are forwarded into `UIElement.props`. See
    # docs/design/Packed_Kwds_UI_Interface_Optimization.md.
    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
        return UIElement(kind=kind, props=dict(kwds))

    @classmethod
    @pyrolyse
    # NOTE: original signature for Balloon includes omitted variadic arguments
    def CBalloon(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Balloon",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Button includes omitted variadic arguments
    def CButton(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Button",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Button includes omitted variadic arguments
    def CTtkButton(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Button",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for ButtonBox includes omitted variadic arguments
    def CButtonBox(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="ButtonBox",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    def CCObjView(
        cls,
        master = None,
        widgetName = None,
        static_options = None,
        cnf = {},
        kw = {},
    ) -> None:
        call_native(cls.__element)(
            kind="CObjView",
            master=master,
            widgetName=widgetName,
            static_options=static_options,
            cnf=cnf,
            kw=kw,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Canvas includes omitted variadic arguments
    def CCanvas(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Canvas",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for CheckList includes omitted variadic arguments
    def CCheckList(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="CheckList",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Checkbutton includes omitted variadic arguments
    def CCheckbutton(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Checkbutton",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Checkbutton includes omitted variadic arguments
    def CTtkCheckbutton(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Checkbutton",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for ComboBox includes omitted variadic arguments
    def CComboBox(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="ComboBox",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Combobox includes omitted variadic arguments
    def CCombobox(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Combobox",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Control includes omitted variadic arguments
    def CControl(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Control",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Dialog includes omitted variadic arguments
    def CDialog(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Dialog",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for DialogShell includes omitted variadic arguments
    def CDialogShell(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="DialogShell",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for DirList includes omitted variadic arguments
    def CDirList(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="DirList",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for DirSelectBox includes omitted variadic arguments
    def CDirSelectBox(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="DirSelectBox",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for DirSelectDialog includes omitted variadic arguments
    def CDirSelectDialog(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="DirSelectDialog",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for DirTree includes omitted variadic arguments
    def CDirTree(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="DirTree",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Entry includes omitted variadic arguments
    def CEntry(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Entry",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Entry includes omitted variadic arguments
    def CTtkEntry(
        cls,
        master = None,
        widget = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Entry",
            master=master,
            widget=widget,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for ExFileSelectBox includes omitted variadic arguments
    def CExFileSelectBox(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="ExFileSelectBox",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for ExFileSelectDialog includes omitted variadic arguments
    def CExFileSelectDialog(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="ExFileSelectDialog",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for FileEntry includes omitted variadic arguments
    def CFileEntry(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="FileEntry",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for FileSelectBox includes omitted variadic arguments
    def CFileSelectBox(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="FileSelectBox",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for FileSelectDialog includes omitted variadic arguments
    def CFileSelectDialog(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="FileSelectDialog",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Frame includes omitted variadic arguments
    def CFrame(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Frame",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Frame includes omitted variadic arguments
    def CTtkFrame(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Frame",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Grid includes omitted variadic arguments
    def CGrid(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Grid",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for HList includes omitted variadic arguments
    def CHList(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="HList",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for InputOnly includes omitted variadic arguments
    def CInputOnly(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="InputOnly",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Label includes omitted variadic arguments
    def CLabel(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Label",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Label includes omitted variadic arguments
    def CTtkLabel(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Label",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for LabelEntry includes omitted variadic arguments
    def CLabelEntry(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="LabelEntry",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for LabelFrame includes omitted variadic arguments
    def CLabelFrame(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="LabelFrame",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for LabelFrame includes omitted variadic arguments
    def CTixLabelFrame(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="LabelFrame",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for LabeledScale includes omitted variadic arguments
    def CLabeledScale(
        cls,
        master = None,
        variable = None,
        from_ = 0,
        to = 10,
    ) -> None:
        call_native(cls.__element)(
            kind="LabeledScale",
            master=master,
            variable=variable,
            from_=from_,
            to=to,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Labelframe includes omitted variadic arguments
    def CLabelframe(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Labelframe",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for ListNoteBook includes omitted variadic arguments
    def CListNoteBook(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="ListNoteBook",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Listbox includes omitted variadic arguments
    def CListbox(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Listbox",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Menu includes omitted variadic arguments
    def CMenu(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Menu",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Menubutton includes omitted variadic arguments
    def CMenubutton(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Menubutton",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Menubutton includes omitted variadic arguments
    def CTtkMenubutton(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Menubutton",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Message includes omitted variadic arguments
    def CMessage(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Message",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Meter includes omitted variadic arguments
    def CMeter(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Meter",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for NoteBook includes omitted variadic arguments
    def CNoteBook(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="NoteBook",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    def CNoteBookFrame(
        cls,
        master = None,
        widgetName = None,
        static_options = None,
        cnf = {},
        kw = {},
    ) -> None:
        call_native(cls.__element)(
            kind="NoteBookFrame",
            master=master,
            widgetName=widgetName,
            static_options=static_options,
            cnf=cnf,
            kw=kw,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Notebook includes omitted variadic arguments
    def CNotebook(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Notebook",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for OptionMenu includes omitted variadic arguments
    def COptionMenu(
        cls,
        master,
        variable,
        value,
    ) -> None:
        call_native(cls.__element)(
            kind="OptionMenu",
            master=master,
            variable=variable,
            value=value,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for OptionMenu includes omitted variadic arguments
    def CTixOptionMenu(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="OptionMenu",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for OptionMenu includes omitted variadic arguments
    def CTtkOptionMenu(
        cls,
        master,
        variable,
        default = None,
    ) -> None:
        call_native(cls.__element)(
            kind="OptionMenu",
            master=master,
            variable=variable,
            default=default,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for PanedWindow includes omitted variadic arguments
    def CPanedWindow(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="PanedWindow",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for PanedWindow includes omitted variadic arguments
    def CTixPanedWindow(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="PanedWindow",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Panedwindow includes omitted variadic arguments
    def CPanedwindow(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Panedwindow",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for PopupMenu includes omitted variadic arguments
    def CPopupMenu(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="PopupMenu",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Progressbar includes omitted variadic arguments
    def CProgressbar(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Progressbar",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Radiobutton includes omitted variadic arguments
    def CRadiobutton(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Radiobutton",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Radiobutton includes omitted variadic arguments
    def CTtkRadiobutton(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Radiobutton",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for ResizeHandle includes omitted variadic arguments
    def CResizeHandle(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="ResizeHandle",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Scale includes omitted variadic arguments
    def CScale(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Scale",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Scale includes omitted variadic arguments
    def CTtkScale(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Scale",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Scrollbar includes omitted variadic arguments
    def CScrollbar(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Scrollbar",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Scrollbar includes omitted variadic arguments
    def CTtkScrollbar(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Scrollbar",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for ScrolledGrid includes omitted variadic arguments
    def CScrolledGrid(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="ScrolledGrid",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for ScrolledHList includes omitted variadic arguments
    def CScrolledHList(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="ScrolledHList",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for ScrolledListBox includes omitted variadic arguments
    def CScrolledListBox(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="ScrolledListBox",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for ScrolledTList includes omitted variadic arguments
    def CScrolledTList(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="ScrolledTList",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for ScrolledText includes omitted variadic arguments
    def CScrolledtextScrolledText(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="ScrolledText",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for ScrolledText includes omitted variadic arguments
    def CTixScrolledText(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="ScrolledText",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for ScrolledWindow includes omitted variadic arguments
    def CScrolledWindow(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="ScrolledWindow",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Select includes omitted variadic arguments
    def CSelect(
        cls,
        master,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Select",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Separator includes omitted variadic arguments
    def CSeparator(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Separator",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Shell includes omitted variadic arguments
    def CShell(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Shell",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Sizegrip includes omitted variadic arguments
    def CSizegrip(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Sizegrip",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Spinbox includes omitted variadic arguments
    def CSpinbox(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Spinbox",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Spinbox includes omitted variadic arguments
    def CTtkSpinbox(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Spinbox",
            master=master,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for StdButtonBox includes omitted variadic arguments
    def CStdButtonBox(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="StdButtonBox",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for TList includes omitted variadic arguments
    def CTList(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="TList",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Text includes omitted variadic arguments
    def CText(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Text",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    def CTixSubWidget(
        cls,
        master,
        name,
        destroy_physically = 1,
        check_intermediate = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="TixSubWidget",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
            check_intermediate=check_intermediate,
        )

    @classmethod
    @pyrolyse
    def CTixWidget(
        cls,
        master = None,
        widgetName = None,
        static_options = None,
        cnf = {},
        kw = {},
    ) -> None:
        call_native(cls.__element)(
            kind="TixWidget",
            master=master,
            widgetName=widgetName,
            static_options=static_options,
            cnf=cnf,
            kw=kw,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Tree includes omitted variadic arguments
    def CTree(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        call_native(cls.__element)(
            kind="Tree",
            master=master,
            cnf=cnf,
        )

    @classmethod
    @pyrolyse
    # NOTE: original signature for Treeview includes omitted variadic arguments
    def CTreeview(
        cls,
        master = None,
    ) -> None:
        call_native(cls.__element)(
            kind="Treeview",
            master=master,
        )

    @classmethod
    @pyrolyse
    def C_dummyButton(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyButton",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyCheckbutton(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyCheckbutton",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyComboBox(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyComboBox",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyDirList(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyDirList",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyDirSelectBox(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyDirSelectBox",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyEntry(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyEntry",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyExFileSelectBox(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyExFileSelectBox",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyFileComboBox(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyFileComboBox",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyFileSelectBox(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyFileSelectBox",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyFrame(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyFrame",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyHList(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyHList",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyLabel(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyLabel",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyListbox(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyListbox",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyMenu(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyMenu",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyMenubutton(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyMenubutton",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyNoteBookFrame(
        cls,
        master,
        name,
        destroy_physically = 0,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyNoteBookFrame",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyPanedWindow(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyPanedWindow",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyScrollbar(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyScrollbar",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyScrolledHList(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyScrolledHList",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyScrolledListBox(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyScrolledListBox",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyStdButtonBox(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyStdButtonBox",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyTList(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyTList",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )

    @classmethod
    @pyrolyse
    def C_dummyText(
        cls,
        master,
        name,
        destroy_physically = 1,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyText",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
        )
