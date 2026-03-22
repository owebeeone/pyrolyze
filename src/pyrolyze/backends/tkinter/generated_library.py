"""Generated UI interface stubs for discovered widgets."""
from __future__ import annotations
from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
import tkinter
from typing import Any, ClassVar
from frozendict import frozendict
from pyrolyze.api import MISSING, MissingType, PyrolyzeHandler, UIElement, call_native, pyrolyse, ui_interface
from pyrolyze.backends.model import AccessorKind, ChildPolicy, EventPayloadPolicy, FillPolicy, MethodMode, MountParamSpec, MountPointSpec, PropMode, TypeRef, UiEventSpec, UiInterface, UiInterfaceEntry, UiMethodSpec, UiParamSpec, UiPropSpec, UiWidgetSpec

@ui_interface
class TkinterUiLibrary:
    ROOT_MODULE: ClassVar[str] = 'tkinter'
    UI_INTERFACE: ClassVar[UiInterface] = UiInterface(name='TkinterUiLibrary', owner=None, entries=frozendict({'CBalloon': UiInterfaceEntry(public_name='CBalloon', kind='Balloon'), 'CButton': UiInterfaceEntry(public_name='CButton', kind='Button'), 'CTtkButton': UiInterfaceEntry(public_name='CTtkButton', kind='Button'), 'CButtonBox': UiInterfaceEntry(public_name='CButtonBox', kind='ButtonBox'), 'CCObjView': UiInterfaceEntry(public_name='CCObjView', kind='CObjView'), 'CCanvas': UiInterfaceEntry(public_name='CCanvas', kind='Canvas'), 'CCheckList': UiInterfaceEntry(public_name='CCheckList', kind='CheckList'), 'CCheckbutton': UiInterfaceEntry(public_name='CCheckbutton', kind='Checkbutton'), 'CTtkCheckbutton': UiInterfaceEntry(public_name='CTtkCheckbutton', kind='Checkbutton'), 'CComboBox': UiInterfaceEntry(public_name='CComboBox', kind='ComboBox'), 'CCombobox': UiInterfaceEntry(public_name='CCombobox', kind='Combobox'), 'CControl': UiInterfaceEntry(public_name='CControl', kind='Control'), 'CDialog': UiInterfaceEntry(public_name='CDialog', kind='Dialog'), 'CDialogShell': UiInterfaceEntry(public_name='CDialogShell', kind='DialogShell'), 'CDirList': UiInterfaceEntry(public_name='CDirList', kind='DirList'), 'CDirSelectBox': UiInterfaceEntry(public_name='CDirSelectBox', kind='DirSelectBox'), 'CDirSelectDialog': UiInterfaceEntry(public_name='CDirSelectDialog', kind='DirSelectDialog'), 'CDirTree': UiInterfaceEntry(public_name='CDirTree', kind='DirTree'), 'CEntry': UiInterfaceEntry(public_name='CEntry', kind='Entry'), 'CTtkEntry': UiInterfaceEntry(public_name='CTtkEntry', kind='Entry'), 'CExFileSelectBox': UiInterfaceEntry(public_name='CExFileSelectBox', kind='ExFileSelectBox'), 'CExFileSelectDialog': UiInterfaceEntry(public_name='CExFileSelectDialog', kind='ExFileSelectDialog'), 'CFileEntry': UiInterfaceEntry(public_name='CFileEntry', kind='FileEntry'), 'CFileSelectBox': UiInterfaceEntry(public_name='CFileSelectBox', kind='FileSelectBox'), 'CFileSelectDialog': UiInterfaceEntry(public_name='CFileSelectDialog', kind='FileSelectDialog'), 'CFrame': UiInterfaceEntry(public_name='CFrame', kind='Frame'), 'CTtkFrame': UiInterfaceEntry(public_name='CTtkFrame', kind='Frame'), 'CGrid': UiInterfaceEntry(public_name='CGrid', kind='Grid'), 'CHList': UiInterfaceEntry(public_name='CHList', kind='HList'), 'CInputOnly': UiInterfaceEntry(public_name='CInputOnly', kind='InputOnly'), 'CLabel': UiInterfaceEntry(public_name='CLabel', kind='Label'), 'CTtkLabel': UiInterfaceEntry(public_name='CTtkLabel', kind='Label'), 'CLabelEntry': UiInterfaceEntry(public_name='CLabelEntry', kind='LabelEntry'), 'CLabelFrame': UiInterfaceEntry(public_name='CLabelFrame', kind='LabelFrame'), 'CTixLabelFrame': UiInterfaceEntry(public_name='CTixLabelFrame', kind='LabelFrame'), 'CLabeledScale': UiInterfaceEntry(public_name='CLabeledScale', kind='LabeledScale'), 'CLabelframe': UiInterfaceEntry(public_name='CLabelframe', kind='Labelframe'), 'CListNoteBook': UiInterfaceEntry(public_name='CListNoteBook', kind='ListNoteBook'), 'CListbox': UiInterfaceEntry(public_name='CListbox', kind='Listbox'), 'CMenu': UiInterfaceEntry(public_name='CMenu', kind='Menu'), 'CMenubutton': UiInterfaceEntry(public_name='CMenubutton', kind='Menubutton'), 'CTtkMenubutton': UiInterfaceEntry(public_name='CTtkMenubutton', kind='Menubutton'), 'CMessage': UiInterfaceEntry(public_name='CMessage', kind='Message'), 'CMeter': UiInterfaceEntry(public_name='CMeter', kind='Meter'), 'CNoteBook': UiInterfaceEntry(public_name='CNoteBook', kind='NoteBook'), 'CNoteBookFrame': UiInterfaceEntry(public_name='CNoteBookFrame', kind='NoteBookFrame'), 'CNotebook': UiInterfaceEntry(public_name='CNotebook', kind='Notebook'), 'COptionMenu': UiInterfaceEntry(public_name='COptionMenu', kind='OptionMenu'), 'CTixOptionMenu': UiInterfaceEntry(public_name='CTixOptionMenu', kind='OptionMenu'), 'CTtkOptionMenu': UiInterfaceEntry(public_name='CTtkOptionMenu', kind='OptionMenu'), 'CPanedWindow': UiInterfaceEntry(public_name='CPanedWindow', kind='PanedWindow'), 'CTixPanedWindow': UiInterfaceEntry(public_name='CTixPanedWindow', kind='PanedWindow'), 'CPanedwindow': UiInterfaceEntry(public_name='CPanedwindow', kind='Panedwindow'), 'CPopupMenu': UiInterfaceEntry(public_name='CPopupMenu', kind='PopupMenu'), 'CProgressbar': UiInterfaceEntry(public_name='CProgressbar', kind='Progressbar'), 'CRadiobutton': UiInterfaceEntry(public_name='CRadiobutton', kind='Radiobutton'), 'CTtkRadiobutton': UiInterfaceEntry(public_name='CTtkRadiobutton', kind='Radiobutton'), 'CResizeHandle': UiInterfaceEntry(public_name='CResizeHandle', kind='ResizeHandle'), 'CScale': UiInterfaceEntry(public_name='CScale', kind='Scale'), 'CTtkScale': UiInterfaceEntry(public_name='CTtkScale', kind='Scale'), 'CScrollbar': UiInterfaceEntry(public_name='CScrollbar', kind='Scrollbar'), 'CTtkScrollbar': UiInterfaceEntry(public_name='CTtkScrollbar', kind='Scrollbar'), 'CScrolledGrid': UiInterfaceEntry(public_name='CScrolledGrid', kind='ScrolledGrid'), 'CScrolledHList': UiInterfaceEntry(public_name='CScrolledHList', kind='ScrolledHList'), 'CScrolledListBox': UiInterfaceEntry(public_name='CScrolledListBox', kind='ScrolledListBox'), 'CScrolledTList': UiInterfaceEntry(public_name='CScrolledTList', kind='ScrolledTList'), 'CScrolledtextScrolledText': UiInterfaceEntry(public_name='CScrolledtextScrolledText', kind='ScrolledText'), 'CTixScrolledText': UiInterfaceEntry(public_name='CTixScrolledText', kind='ScrolledText'), 'CScrolledWindow': UiInterfaceEntry(public_name='CScrolledWindow', kind='ScrolledWindow'), 'CSelect': UiInterfaceEntry(public_name='CSelect', kind='Select'), 'CSeparator': UiInterfaceEntry(public_name='CSeparator', kind='Separator'), 'CShell': UiInterfaceEntry(public_name='CShell', kind='Shell'), 'CSizegrip': UiInterfaceEntry(public_name='CSizegrip', kind='Sizegrip'), 'CSpinbox': UiInterfaceEntry(public_name='CSpinbox', kind='Spinbox'), 'CTtkSpinbox': UiInterfaceEntry(public_name='CTtkSpinbox', kind='Spinbox'), 'CStdButtonBox': UiInterfaceEntry(public_name='CStdButtonBox', kind='StdButtonBox'), 'CTList': UiInterfaceEntry(public_name='CTList', kind='TList'), 'CText': UiInterfaceEntry(public_name='CText', kind='Text'), 'CTixSubWidget': UiInterfaceEntry(public_name='CTixSubWidget', kind='TixSubWidget'), 'CTixWidget': UiInterfaceEntry(public_name='CTixWidget', kind='TixWidget'), 'CTree': UiInterfaceEntry(public_name='CTree', kind='Tree'), 'CTreeview': UiInterfaceEntry(public_name='CTreeview', kind='Treeview'), 'C_dummyButton': UiInterfaceEntry(public_name='C_dummyButton', kind='_dummyButton'), 'C_dummyCheckbutton': UiInterfaceEntry(public_name='C_dummyCheckbutton', kind='_dummyCheckbutton'), 'C_dummyComboBox': UiInterfaceEntry(public_name='C_dummyComboBox', kind='_dummyComboBox'), 'C_dummyDirList': UiInterfaceEntry(public_name='C_dummyDirList', kind='_dummyDirList'), 'C_dummyDirSelectBox': UiInterfaceEntry(public_name='C_dummyDirSelectBox', kind='_dummyDirSelectBox'), 'C_dummyEntry': UiInterfaceEntry(public_name='C_dummyEntry', kind='_dummyEntry'), 'C_dummyExFileSelectBox': UiInterfaceEntry(public_name='C_dummyExFileSelectBox', kind='_dummyExFileSelectBox'), 'C_dummyFileComboBox': UiInterfaceEntry(public_name='C_dummyFileComboBox', kind='_dummyFileComboBox'), 'C_dummyFileSelectBox': UiInterfaceEntry(public_name='C_dummyFileSelectBox', kind='_dummyFileSelectBox'), 'C_dummyFrame': UiInterfaceEntry(public_name='C_dummyFrame', kind='_dummyFrame'), 'C_dummyHList': UiInterfaceEntry(public_name='C_dummyHList', kind='_dummyHList'), 'C_dummyLabel': UiInterfaceEntry(public_name='C_dummyLabel', kind='_dummyLabel'), 'C_dummyListbox': UiInterfaceEntry(public_name='C_dummyListbox', kind='_dummyListbox'), 'C_dummyMenu': UiInterfaceEntry(public_name='C_dummyMenu', kind='_dummyMenu'), 'C_dummyMenubutton': UiInterfaceEntry(public_name='C_dummyMenubutton', kind='_dummyMenubutton'), 'C_dummyNoteBookFrame': UiInterfaceEntry(public_name='C_dummyNoteBookFrame', kind='_dummyNoteBookFrame'), 'C_dummyPanedWindow': UiInterfaceEntry(public_name='C_dummyPanedWindow', kind='_dummyPanedWindow'), 'C_dummyScrollbar': UiInterfaceEntry(public_name='C_dummyScrollbar', kind='_dummyScrollbar'), 'C_dummyScrolledHList': UiInterfaceEntry(public_name='C_dummyScrolledHList', kind='_dummyScrolledHList'), 'C_dummyScrolledListBox': UiInterfaceEntry(public_name='C_dummyScrolledListBox', kind='_dummyScrolledListBox'), 'C_dummyStdButtonBox': UiInterfaceEntry(public_name='C_dummyStdButtonBox', kind='_dummyStdButtonBox'), 'C_dummyTList': UiInterfaceEntry(public_name='C_dummyTList', kind='_dummyTList'), 'C_dummyText': UiInterfaceEntry(public_name='C_dummyText', kind='_dummyText')}))
    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({'Balloon': UiWidgetSpec(kind='Balloon', mounted_type_name='tkinter.tix.Balloon', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Button': UiWidgetSpec(kind='Button', mounted_type_name='tkinter.Button', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Button': UiWidgetSpec(kind='Button', mounted_type_name='tkinter.ttk.Button', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'ButtonBox': UiWidgetSpec(kind='ButtonBox', mounted_type_name='tkinter.tix.ButtonBox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'CObjView': UiWidgetSpec(kind='CObjView', mounted_type_name='tkinter.tix.CObjView', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'widgetName': UiParamSpec(name='widgetName', annotation=None, default_repr='None'), 'static_options': UiParamSpec(name='static_options', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}'), 'kw': UiParamSpec(name='kw', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'widgetName': UiPropSpec(name='widgetName', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='widgetName', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'static_options': UiPropSpec(name='static_options', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='static_options', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'kw': UiPropSpec(name='kw', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='kw', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Canvas': UiWidgetSpec(kind='Canvas', mounted_type_name='tkinter.Canvas', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'CheckList': UiWidgetSpec(kind='CheckList', mounted_type_name='tkinter.tix.CheckList', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({'setstatus': UiMethodSpec(name='setstatus', mode=MethodMode.CREATE_UPDATE, params=(UiParamSpec(name='entrypath', annotation=None, default_repr=None), UiParamSpec(name='mode', annotation=None, default_repr="'on'")), source_props=('entrypath', 'mode'), fill_policy=FillPolicy.RETAIN_EFFECTIVE, constructor_equivalent=False)}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Checkbutton': UiWidgetSpec(kind='Checkbutton', mounted_type_name='tkinter.Checkbutton', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Checkbutton': UiWidgetSpec(kind='Checkbutton', mounted_type_name='tkinter.ttk.Checkbutton', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'ComboBox': UiWidgetSpec(kind='ComboBox', mounted_type_name='tkinter.tix.ComboBox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Combobox': UiWidgetSpec(kind='Combobox', mounted_type_name='tkinter.ttk.Combobox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Control': UiWidgetSpec(kind='Control', mounted_type_name='tkinter.tix.Control', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Dialog': UiWidgetSpec(kind='Dialog', mounted_type_name='tkinter.dialog.Dialog', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'DialogShell': UiWidgetSpec(kind='DialogShell', mounted_type_name='tkinter.tix.DialogShell', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'DirList': UiWidgetSpec(kind='DirList', mounted_type_name='tkinter.tix.DirList', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'DirSelectBox': UiWidgetSpec(kind='DirSelectBox', mounted_type_name='tkinter.tix.DirSelectBox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'DirSelectDialog': UiWidgetSpec(kind='DirSelectDialog', mounted_type_name='tkinter.tix.DirSelectDialog', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'DirTree': UiWidgetSpec(kind='DirTree', mounted_type_name='tkinter.tix.DirTree', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Entry': UiWidgetSpec(kind='Entry', mounted_type_name='tkinter.Entry', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Entry': UiWidgetSpec(kind='Entry', mounted_type_name='tkinter.ttk.Entry', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'widget': UiParamSpec(name='widget', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'widget': UiPropSpec(name='widget', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='widget', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'ExFileSelectBox': UiWidgetSpec(kind='ExFileSelectBox', mounted_type_name='tkinter.tix.ExFileSelectBox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'ExFileSelectDialog': UiWidgetSpec(kind='ExFileSelectDialog', mounted_type_name='tkinter.tix.ExFileSelectDialog', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'FileEntry': UiWidgetSpec(kind='FileEntry', mounted_type_name='tkinter.tix.FileEntry', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'FileSelectBox': UiWidgetSpec(kind='FileSelectBox', mounted_type_name='tkinter.tix.FileSelectBox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'FileSelectDialog': UiWidgetSpec(kind='FileSelectDialog', mounted_type_name='tkinter.tix.FileSelectDialog', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Frame': UiWidgetSpec(kind='Frame', mounted_type_name='tkinter.Frame', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Frame': UiWidgetSpec(kind='Frame', mounted_type_name='tkinter.ttk.Frame', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Grid': UiWidgetSpec(kind='Grid', mounted_type_name='tkinter.tix.Grid', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({'set': UiMethodSpec(name='set', mode=MethodMode.CREATE_UPDATE, params=(UiParamSpec(name='x', annotation=None, default_repr=None), UiParamSpec(name='y', annotation=None, default_repr=None), UiParamSpec(name='itemtype', annotation=None, default_repr='None')), source_props=('x', 'y', 'itemtype'), fill_policy=FillPolicy.RETAIN_EFFECTIVE, constructor_equivalent=False)}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'HList': UiWidgetSpec(kind='HList', mounted_type_name='tkinter.tix.HList', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'InputOnly': UiWidgetSpec(kind='InputOnly', mounted_type_name='tkinter.tix.InputOnly', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Label': UiWidgetSpec(kind='Label', mounted_type_name='tkinter.Label', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Label': UiWidgetSpec(kind='Label', mounted_type_name='tkinter.ttk.Label', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'LabelEntry': UiWidgetSpec(kind='LabelEntry', mounted_type_name='tkinter.tix.LabelEntry', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'LabelFrame': UiWidgetSpec(kind='LabelFrame', mounted_type_name='tkinter.LabelFrame', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'LabelFrame': UiWidgetSpec(kind='LabelFrame', mounted_type_name='tkinter.tix.LabelFrame', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'LabeledScale': UiWidgetSpec(kind='LabeledScale', mounted_type_name='tkinter.ttk.LabeledScale', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'variable': UiParamSpec(name='variable', annotation=None, default_repr='None'), 'from_': UiParamSpec(name='from_', annotation=None, default_repr='0'), 'to': UiParamSpec(name='to', annotation=None, default_repr='10')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'variable': UiPropSpec(name='variable', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='variable', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'from_': UiPropSpec(name='from_', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='from_', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'to': UiPropSpec(name='to', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='to', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Labelframe': UiWidgetSpec(kind='Labelframe', mounted_type_name='tkinter.ttk.Labelframe', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'ListNoteBook': UiWidgetSpec(kind='ListNoteBook', mounted_type_name='tkinter.tix.ListNoteBook', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Listbox': UiWidgetSpec(kind='Listbox', mounted_type_name='tkinter.Listbox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Menu': UiWidgetSpec(kind='Menu', mounted_type_name='tkinter.Menu', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Menubutton': UiWidgetSpec(kind='Menubutton', mounted_type_name='tkinter.Menubutton', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Menubutton': UiWidgetSpec(kind='Menubutton', mounted_type_name='tkinter.ttk.Menubutton', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Message': UiWidgetSpec(kind='Message', mounted_type_name='tkinter.Message', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Meter': UiWidgetSpec(kind='Meter', mounted_type_name='tkinter.tix.Meter', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'NoteBook': UiWidgetSpec(kind='NoteBook', mounted_type_name='tkinter.tix.NoteBook', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'NoteBookFrame': UiWidgetSpec(kind='NoteBookFrame', mounted_type_name='tkinter.tix.NoteBookFrame', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'widgetName': UiParamSpec(name='widgetName', annotation=None, default_repr='None'), 'static_options': UiParamSpec(name='static_options', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}'), 'kw': UiParamSpec(name='kw', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'widgetName': UiPropSpec(name='widgetName', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='widgetName', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'static_options': UiPropSpec(name='static_options', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='static_options', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'kw': UiPropSpec(name='kw', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='kw', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Notebook': UiWidgetSpec(kind='Notebook', mounted_type_name='tkinter.ttk.Notebook', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'OptionMenu': UiWidgetSpec(kind='OptionMenu', mounted_type_name='tkinter.OptionMenu', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'variable': UiParamSpec(name='variable', annotation=None, default_repr=None), 'value': UiParamSpec(name='value', annotation=None, default_repr=None)}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'variable': UiPropSpec(name='variable', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='variable', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'value': UiPropSpec(name='value', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='value', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'OptionMenu': UiWidgetSpec(kind='OptionMenu', mounted_type_name='tkinter.tix.OptionMenu', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'OptionMenu': UiWidgetSpec(kind='OptionMenu', mounted_type_name='tkinter.ttk.OptionMenu', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'variable': UiParamSpec(name='variable', annotation=None, default_repr=None), 'default': UiParamSpec(name='default', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'variable': UiPropSpec(name='variable', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='variable', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'default': UiPropSpec(name='default', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='default', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'PanedWindow': UiWidgetSpec(kind='PanedWindow', mounted_type_name='tkinter.PanedWindow', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'PanedWindow': UiWidgetSpec(kind='PanedWindow', mounted_type_name='tkinter.tix.PanedWindow', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Panedwindow': UiWidgetSpec(kind='Panedwindow', mounted_type_name='tkinter.ttk.Panedwindow', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'PopupMenu': UiWidgetSpec(kind='PopupMenu', mounted_type_name='tkinter.tix.PopupMenu', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Progressbar': UiWidgetSpec(kind='Progressbar', mounted_type_name='tkinter.ttk.Progressbar', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Radiobutton': UiWidgetSpec(kind='Radiobutton', mounted_type_name='tkinter.Radiobutton', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Radiobutton': UiWidgetSpec(kind='Radiobutton', mounted_type_name='tkinter.ttk.Radiobutton', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'ResizeHandle': UiWidgetSpec(kind='ResizeHandle', mounted_type_name='tkinter.tix.ResizeHandle', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Scale': UiWidgetSpec(kind='Scale', mounted_type_name='tkinter.Scale', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Scale': UiWidgetSpec(kind='Scale', mounted_type_name='tkinter.ttk.Scale', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Scrollbar': UiWidgetSpec(kind='Scrollbar', mounted_type_name='tkinter.Scrollbar', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({'set': UiMethodSpec(name='set', mode=MethodMode.CREATE_UPDATE, params=(UiParamSpec(name='first', annotation=None, default_repr=None), UiParamSpec(name='last', annotation=None, default_repr=None)), source_props=('first', 'last'), fill_policy=FillPolicy.RETAIN_EFFECTIVE, constructor_equivalent=False)}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Scrollbar': UiWidgetSpec(kind='Scrollbar', mounted_type_name='tkinter.ttk.Scrollbar', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({'set': UiMethodSpec(name='set', mode=MethodMode.CREATE_UPDATE, params=(UiParamSpec(name='first', annotation=None, default_repr=None), UiParamSpec(name='last', annotation=None, default_repr=None)), source_props=('first', 'last'), fill_policy=FillPolicy.RETAIN_EFFECTIVE, constructor_equivalent=False)}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'ScrolledGrid': UiWidgetSpec(kind='ScrolledGrid', mounted_type_name='tkinter.tix.ScrolledGrid', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({'set': UiMethodSpec(name='set', mode=MethodMode.CREATE_UPDATE, params=(UiParamSpec(name='x', annotation=None, default_repr=None), UiParamSpec(name='y', annotation=None, default_repr=None), UiParamSpec(name='itemtype', annotation=None, default_repr='None')), source_props=('x', 'y', 'itemtype'), fill_policy=FillPolicy.RETAIN_EFFECTIVE, constructor_equivalent=False)}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'ScrolledHList': UiWidgetSpec(kind='ScrolledHList', mounted_type_name='tkinter.tix.ScrolledHList', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'ScrolledListBox': UiWidgetSpec(kind='ScrolledListBox', mounted_type_name='tkinter.tix.ScrolledListBox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'ScrolledTList': UiWidgetSpec(kind='ScrolledTList', mounted_type_name='tkinter.tix.ScrolledTList', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'ScrolledText': UiWidgetSpec(kind='ScrolledText', mounted_type_name='tkinter.scrolledtext.ScrolledText', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'ScrolledText': UiWidgetSpec(kind='ScrolledText', mounted_type_name='tkinter.tix.ScrolledText', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'ScrolledWindow': UiWidgetSpec(kind='ScrolledWindow', mounted_type_name='tkinter.tix.ScrolledWindow', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Select': UiWidgetSpec(kind='Select', mounted_type_name='tkinter.tix.Select', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Separator': UiWidgetSpec(kind='Separator', mounted_type_name='tkinter.ttk.Separator', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Shell': UiWidgetSpec(kind='Shell', mounted_type_name='tkinter.tix.Shell', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Sizegrip': UiWidgetSpec(kind='Sizegrip', mounted_type_name='tkinter.ttk.Sizegrip', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Spinbox': UiWidgetSpec(kind='Spinbox', mounted_type_name='tkinter.Spinbox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Spinbox': UiWidgetSpec(kind='Spinbox', mounted_type_name='tkinter.ttk.Spinbox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'StdButtonBox': UiWidgetSpec(kind='StdButtonBox', mounted_type_name='tkinter.tix.StdButtonBox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'TList': UiWidgetSpec(kind='TList', mounted_type_name='tkinter.tix.TList', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Text': UiWidgetSpec(kind='Text', mounted_type_name='tkinter.Text', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'TixSubWidget': UiWidgetSpec(kind='TixSubWidget', mounted_type_name='tkinter.tix.TixSubWidget', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1'), 'check_intermediate': UiParamSpec(name='check_intermediate', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'check_intermediate': UiPropSpec(name='check_intermediate', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='check_intermediate', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'TixWidget': UiWidgetSpec(kind='TixWidget', mounted_type_name='tkinter.tix.TixWidget', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'widgetName': UiParamSpec(name='widgetName', annotation=None, default_repr='None'), 'static_options': UiParamSpec(name='static_options', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}'), 'kw': UiParamSpec(name='kw', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'widgetName': UiPropSpec(name='widgetName', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='widgetName', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'static_options': UiPropSpec(name='static_options', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='static_options', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'kw': UiPropSpec(name='kw', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='kw', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Tree': UiWidgetSpec(kind='Tree', mounted_type_name='tkinter.tix.Tree', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None'), 'cnf': UiParamSpec(name='cnf', annotation=None, default_repr='{}')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'cnf': UiPropSpec(name='cnf', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({'setmode': UiMethodSpec(name='setmode', mode=MethodMode.CREATE_UPDATE, params=(UiParamSpec(name='entrypath', annotation=None, default_repr=None), UiParamSpec(name='mode', annotation=None, default_repr="'none'")), source_props=('entrypath', 'mode'), fill_policy=FillPolicy.RETAIN_EFFECTIVE, constructor_equivalent=False)}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), 'Treeview': UiWidgetSpec(kind='Treeview', mounted_type_name='tkinter.ttk.Treeview', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr='None')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({'set': UiMethodSpec(name='set', mode=MethodMode.CREATE_UPDATE, params=(UiParamSpec(name='item', annotation=None, default_repr=None), UiParamSpec(name='column', annotation=None, default_repr='None'), UiParamSpec(name='value', annotation=None, default_repr='None')), source_props=('item', 'column', 'value'), fill_policy=FillPolicy.RETAIN_EFFECTIVE, constructor_equivalent=False)}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyButton': UiWidgetSpec(kind='_dummyButton', mounted_type_name='tkinter.tix._dummyButton', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyCheckbutton': UiWidgetSpec(kind='_dummyCheckbutton', mounted_type_name='tkinter.tix._dummyCheckbutton', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyComboBox': UiWidgetSpec(kind='_dummyComboBox', mounted_type_name='tkinter.tix._dummyComboBox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyDirList': UiWidgetSpec(kind='_dummyDirList', mounted_type_name='tkinter.tix._dummyDirList', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyDirSelectBox': UiWidgetSpec(kind='_dummyDirSelectBox', mounted_type_name='tkinter.tix._dummyDirSelectBox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyEntry': UiWidgetSpec(kind='_dummyEntry', mounted_type_name='tkinter.tix._dummyEntry', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyExFileSelectBox': UiWidgetSpec(kind='_dummyExFileSelectBox', mounted_type_name='tkinter.tix._dummyExFileSelectBox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyFileComboBox': UiWidgetSpec(kind='_dummyFileComboBox', mounted_type_name='tkinter.tix._dummyFileComboBox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyFileSelectBox': UiWidgetSpec(kind='_dummyFileSelectBox', mounted_type_name='tkinter.tix._dummyFileSelectBox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyFrame': UiWidgetSpec(kind='_dummyFrame', mounted_type_name='tkinter.tix._dummyFrame', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyHList': UiWidgetSpec(kind='_dummyHList', mounted_type_name='tkinter.tix._dummyHList', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyLabel': UiWidgetSpec(kind='_dummyLabel', mounted_type_name='tkinter.tix._dummyLabel', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyListbox': UiWidgetSpec(kind='_dummyListbox', mounted_type_name='tkinter.tix._dummyListbox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyMenu': UiWidgetSpec(kind='_dummyMenu', mounted_type_name='tkinter.tix._dummyMenu', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyMenubutton': UiWidgetSpec(kind='_dummyMenubutton', mounted_type_name='tkinter.tix._dummyMenubutton', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyNoteBookFrame': UiWidgetSpec(kind='_dummyNoteBookFrame', mounted_type_name='tkinter.tix._dummyNoteBookFrame', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='0')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyPanedWindow': UiWidgetSpec(kind='_dummyPanedWindow', mounted_type_name='tkinter.tix._dummyPanedWindow', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyScrollbar': UiWidgetSpec(kind='_dummyScrollbar', mounted_type_name='tkinter.tix._dummyScrollbar', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({'set': UiMethodSpec(name='set', mode=MethodMode.CREATE_UPDATE, params=(UiParamSpec(name='first', annotation=None, default_repr=None), UiParamSpec(name='last', annotation=None, default_repr=None)), source_props=('first', 'last'), fill_policy=FillPolicy.RETAIN_EFFECTIVE, constructor_equivalent=False)}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyScrolledHList': UiWidgetSpec(kind='_dummyScrolledHList', mounted_type_name='tkinter.tix._dummyScrolledHList', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyScrolledListBox': UiWidgetSpec(kind='_dummyScrolledListBox', mounted_type_name='tkinter.tix._dummyScrolledListBox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyStdButtonBox': UiWidgetSpec(kind='_dummyStdButtonBox', mounted_type_name='tkinter.tix._dummyStdButtonBox', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyTList': UiWidgetSpec(kind='_dummyTList', mounted_type_name='tkinter.tix._dummyTList', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE), '_dummyText': UiWidgetSpec(kind='_dummyText', mounted_type_name='tkinter.tix._dummyText', constructor_params=frozendict({'master': UiParamSpec(name='master', annotation=None, default_repr=None), 'name': UiParamSpec(name='name', annotation=None, default_repr=None), 'destroy_physically': UiParamSpec(name='destroy_physically', annotation=None, default_repr='1')}), props=frozendict({'master': UiPropSpec(name='master', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'name': UiPropSpec(name='name', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True), 'destroy_physically': UiPropSpec(name='destroy_physically', annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True)}), methods=frozendict({}), events=frozendict({}), mount_points=frozendict({}), default_child_mount_point_name=None, default_attach_mount_point_names=(), child_policy=ChildPolicy.NONE)})

    @classmethod
    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
        return UIElement(kind=kind, props=dict(kwds))

    def __pyr_TkinterUiLibrary__CBalloon(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Balloon', kwds=kwds, __pyr_call_site_id=1)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CBalloon', __pyr_TkinterUiLibrary__CBalloon, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CBalloon(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CBalloon')

    def __pyr_TkinterUiLibrary__CButton(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Button', kwds=kwds, __pyr_call_site_id=2)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CButton', __pyr_TkinterUiLibrary__CButton, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CButton(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CButton')

    def __pyr_TkinterUiLibrary__CTtkButton(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Button', kwds=kwds, __pyr_call_site_id=3)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTtkButton', __pyr_TkinterUiLibrary__CTtkButton, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CTtkButton(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTtkButton')

    def __pyr_TkinterUiLibrary__CButtonBox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='ButtonBox', kwds=kwds, __pyr_call_site_id=4)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CButtonBox', __pyr_TkinterUiLibrary__CButtonBox, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CButtonBox(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CButtonBox')

    def __pyr_TkinterUiLibrary__CCObjView(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='CObjView', kwds=kwds, __pyr_call_site_id=5)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CCObjView', __pyr_TkinterUiLibrary__CCObjView, packed_kwargs=True, packed_kwarg_param_names=('master', 'widgetName', 'static_options', 'cnf', 'kw')))
    def CCObjView(cls, master=None, widgetName=None, static_options=None, cnf={}, kw={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CCObjView')

    def __pyr_TkinterUiLibrary__CCanvas(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Canvas', kwds=kwds, __pyr_call_site_id=6)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CCanvas', __pyr_TkinterUiLibrary__CCanvas, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CCanvas(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CCanvas')

    def __pyr_TkinterUiLibrary__CCheckList(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='CheckList', kwds=kwds, __pyr_call_site_id=7)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CCheckList', __pyr_TkinterUiLibrary__CCheckList, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CCheckList(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CCheckList')

    def __pyr_TkinterUiLibrary__CCheckbutton(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Checkbutton', kwds=kwds, __pyr_call_site_id=8)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CCheckbutton', __pyr_TkinterUiLibrary__CCheckbutton, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CCheckbutton(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CCheckbutton')

    def __pyr_TkinterUiLibrary__CTtkCheckbutton(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Checkbutton', kwds=kwds, __pyr_call_site_id=9)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTtkCheckbutton', __pyr_TkinterUiLibrary__CTtkCheckbutton, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CTtkCheckbutton(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTtkCheckbutton')

    def __pyr_TkinterUiLibrary__CComboBox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='ComboBox', kwds=kwds, __pyr_call_site_id=10)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CComboBox', __pyr_TkinterUiLibrary__CComboBox, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CComboBox(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CComboBox')

    def __pyr_TkinterUiLibrary__CCombobox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Combobox', kwds=kwds, __pyr_call_site_id=11)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CCombobox', __pyr_TkinterUiLibrary__CCombobox, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CCombobox(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CCombobox')

    def __pyr_TkinterUiLibrary__CControl(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Control', kwds=kwds, __pyr_call_site_id=12)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CControl', __pyr_TkinterUiLibrary__CControl, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CControl(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CControl')

    def __pyr_TkinterUiLibrary__CDialog(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Dialog', kwds=kwds, __pyr_call_site_id=13)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CDialog', __pyr_TkinterUiLibrary__CDialog, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CDialog(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CDialog')

    def __pyr_TkinterUiLibrary__CDialogShell(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='DialogShell', kwds=kwds, __pyr_call_site_id=14)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CDialogShell', __pyr_TkinterUiLibrary__CDialogShell, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CDialogShell(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CDialogShell')

    def __pyr_TkinterUiLibrary__CDirList(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='DirList', kwds=kwds, __pyr_call_site_id=15)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CDirList', __pyr_TkinterUiLibrary__CDirList, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CDirList(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CDirList')

    def __pyr_TkinterUiLibrary__CDirSelectBox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='DirSelectBox', kwds=kwds, __pyr_call_site_id=16)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CDirSelectBox', __pyr_TkinterUiLibrary__CDirSelectBox, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CDirSelectBox(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CDirSelectBox')

    def __pyr_TkinterUiLibrary__CDirSelectDialog(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='DirSelectDialog', kwds=kwds, __pyr_call_site_id=17)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CDirSelectDialog', __pyr_TkinterUiLibrary__CDirSelectDialog, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CDirSelectDialog(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CDirSelectDialog')

    def __pyr_TkinterUiLibrary__CDirTree(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='DirTree', kwds=kwds, __pyr_call_site_id=18)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CDirTree', __pyr_TkinterUiLibrary__CDirTree, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CDirTree(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CDirTree')

    def __pyr_TkinterUiLibrary__CEntry(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Entry', kwds=kwds, __pyr_call_site_id=19)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CEntry', __pyr_TkinterUiLibrary__CEntry, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CEntry(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CEntry')

    def __pyr_TkinterUiLibrary__CTtkEntry(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Entry', kwds=kwds, __pyr_call_site_id=20)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTtkEntry', __pyr_TkinterUiLibrary__CTtkEntry, packed_kwargs=True, packed_kwarg_param_names=('master', 'widget')))
    def CTtkEntry(cls, master=None, widget=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTtkEntry')

    def __pyr_TkinterUiLibrary__CExFileSelectBox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='ExFileSelectBox', kwds=kwds, __pyr_call_site_id=21)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CExFileSelectBox', __pyr_TkinterUiLibrary__CExFileSelectBox, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CExFileSelectBox(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CExFileSelectBox')

    def __pyr_TkinterUiLibrary__CExFileSelectDialog(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='ExFileSelectDialog', kwds=kwds, __pyr_call_site_id=22)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CExFileSelectDialog', __pyr_TkinterUiLibrary__CExFileSelectDialog, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CExFileSelectDialog(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CExFileSelectDialog')

    def __pyr_TkinterUiLibrary__CFileEntry(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='FileEntry', kwds=kwds, __pyr_call_site_id=23)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CFileEntry', __pyr_TkinterUiLibrary__CFileEntry, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CFileEntry(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CFileEntry')

    def __pyr_TkinterUiLibrary__CFileSelectBox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='FileSelectBox', kwds=kwds, __pyr_call_site_id=24)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CFileSelectBox', __pyr_TkinterUiLibrary__CFileSelectBox, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CFileSelectBox(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CFileSelectBox')

    def __pyr_TkinterUiLibrary__CFileSelectDialog(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='FileSelectDialog', kwds=kwds, __pyr_call_site_id=25)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CFileSelectDialog', __pyr_TkinterUiLibrary__CFileSelectDialog, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CFileSelectDialog(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CFileSelectDialog')

    def __pyr_TkinterUiLibrary__CFrame(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Frame', kwds=kwds, __pyr_call_site_id=26)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CFrame', __pyr_TkinterUiLibrary__CFrame, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CFrame(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CFrame')

    def __pyr_TkinterUiLibrary__CTtkFrame(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Frame', kwds=kwds, __pyr_call_site_id=27)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTtkFrame', __pyr_TkinterUiLibrary__CTtkFrame, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CTtkFrame(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTtkFrame')

    def __pyr_TkinterUiLibrary__CGrid(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Grid', kwds=kwds, __pyr_call_site_id=28)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CGrid', __pyr_TkinterUiLibrary__CGrid, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CGrid(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CGrid')

    def __pyr_TkinterUiLibrary__CHList(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='HList', kwds=kwds, __pyr_call_site_id=29)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CHList', __pyr_TkinterUiLibrary__CHList, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CHList(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CHList')

    def __pyr_TkinterUiLibrary__CInputOnly(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='InputOnly', kwds=kwds, __pyr_call_site_id=30)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CInputOnly', __pyr_TkinterUiLibrary__CInputOnly, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CInputOnly(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CInputOnly')

    def __pyr_TkinterUiLibrary__CLabel(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Label', kwds=kwds, __pyr_call_site_id=31)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CLabel', __pyr_TkinterUiLibrary__CLabel, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CLabel(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CLabel')

    def __pyr_TkinterUiLibrary__CTtkLabel(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Label', kwds=kwds, __pyr_call_site_id=32)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTtkLabel', __pyr_TkinterUiLibrary__CTtkLabel, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CTtkLabel(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTtkLabel')

    def __pyr_TkinterUiLibrary__CLabelEntry(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='LabelEntry', kwds=kwds, __pyr_call_site_id=33)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CLabelEntry', __pyr_TkinterUiLibrary__CLabelEntry, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CLabelEntry(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CLabelEntry')

    def __pyr_TkinterUiLibrary__CLabelFrame(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='LabelFrame', kwds=kwds, __pyr_call_site_id=34)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CLabelFrame', __pyr_TkinterUiLibrary__CLabelFrame, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CLabelFrame(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CLabelFrame')

    def __pyr_TkinterUiLibrary__CTixLabelFrame(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='LabelFrame', kwds=kwds, __pyr_call_site_id=35)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTixLabelFrame', __pyr_TkinterUiLibrary__CTixLabelFrame, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CTixLabelFrame(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTixLabelFrame')

    def __pyr_TkinterUiLibrary__CLabeledScale(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='LabeledScale', kwds=kwds, __pyr_call_site_id=36)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CLabeledScale', __pyr_TkinterUiLibrary__CLabeledScale, packed_kwargs=True, packed_kwarg_param_names=('master', 'variable', 'from_', 'to')))
    def CLabeledScale(cls, master=None, variable=None, from_=0, to=10) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CLabeledScale')

    def __pyr_TkinterUiLibrary__CLabelframe(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Labelframe', kwds=kwds, __pyr_call_site_id=37)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CLabelframe', __pyr_TkinterUiLibrary__CLabelframe, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CLabelframe(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CLabelframe')

    def __pyr_TkinterUiLibrary__CListNoteBook(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='ListNoteBook', kwds=kwds, __pyr_call_site_id=38)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CListNoteBook', __pyr_TkinterUiLibrary__CListNoteBook, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CListNoteBook(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CListNoteBook')

    def __pyr_TkinterUiLibrary__CListbox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Listbox', kwds=kwds, __pyr_call_site_id=39)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CListbox', __pyr_TkinterUiLibrary__CListbox, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CListbox(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CListbox')

    def __pyr_TkinterUiLibrary__CMenu(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Menu', kwds=kwds, __pyr_call_site_id=40)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CMenu', __pyr_TkinterUiLibrary__CMenu, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CMenu(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CMenu')

    def __pyr_TkinterUiLibrary__CMenubutton(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Menubutton', kwds=kwds, __pyr_call_site_id=41)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CMenubutton', __pyr_TkinterUiLibrary__CMenubutton, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CMenubutton(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CMenubutton')

    def __pyr_TkinterUiLibrary__CTtkMenubutton(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Menubutton', kwds=kwds, __pyr_call_site_id=42)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTtkMenubutton', __pyr_TkinterUiLibrary__CTtkMenubutton, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CTtkMenubutton(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTtkMenubutton')

    def __pyr_TkinterUiLibrary__CMessage(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Message', kwds=kwds, __pyr_call_site_id=43)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CMessage', __pyr_TkinterUiLibrary__CMessage, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CMessage(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CMessage')

    def __pyr_TkinterUiLibrary__CMeter(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Meter', kwds=kwds, __pyr_call_site_id=44)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CMeter', __pyr_TkinterUiLibrary__CMeter, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CMeter(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CMeter')

    def __pyr_TkinterUiLibrary__CNoteBook(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='NoteBook', kwds=kwds, __pyr_call_site_id=45)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CNoteBook', __pyr_TkinterUiLibrary__CNoteBook, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CNoteBook(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CNoteBook')

    def __pyr_TkinterUiLibrary__CNoteBookFrame(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='NoteBookFrame', kwds=kwds, __pyr_call_site_id=46)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CNoteBookFrame', __pyr_TkinterUiLibrary__CNoteBookFrame, packed_kwargs=True, packed_kwarg_param_names=('master', 'widgetName', 'static_options', 'cnf', 'kw')))
    def CNoteBookFrame(cls, master=None, widgetName=None, static_options=None, cnf={}, kw={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CNoteBookFrame')

    def __pyr_TkinterUiLibrary__CNotebook(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Notebook', kwds=kwds, __pyr_call_site_id=47)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CNotebook', __pyr_TkinterUiLibrary__CNotebook, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CNotebook(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CNotebook')

    def __pyr_TkinterUiLibrary__COptionMenu(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='OptionMenu', kwds=kwds, __pyr_call_site_id=48)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.COptionMenu', __pyr_TkinterUiLibrary__COptionMenu, packed_kwargs=True, packed_kwarg_param_names=('master', 'variable', 'value')))
    def COptionMenu(cls, master, variable, value) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.COptionMenu')

    def __pyr_TkinterUiLibrary__CTixOptionMenu(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='OptionMenu', kwds=kwds, __pyr_call_site_id=49)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTixOptionMenu', __pyr_TkinterUiLibrary__CTixOptionMenu, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CTixOptionMenu(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTixOptionMenu')

    def __pyr_TkinterUiLibrary__CTtkOptionMenu(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='OptionMenu', kwds=kwds, __pyr_call_site_id=50)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTtkOptionMenu', __pyr_TkinterUiLibrary__CTtkOptionMenu, packed_kwargs=True, packed_kwarg_param_names=('master', 'variable', 'default')))
    def CTtkOptionMenu(cls, master, variable, default=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTtkOptionMenu')

    def __pyr_TkinterUiLibrary__CPanedWindow(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='PanedWindow', kwds=kwds, __pyr_call_site_id=51)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CPanedWindow', __pyr_TkinterUiLibrary__CPanedWindow, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CPanedWindow(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CPanedWindow')

    def __pyr_TkinterUiLibrary__CTixPanedWindow(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='PanedWindow', kwds=kwds, __pyr_call_site_id=52)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTixPanedWindow', __pyr_TkinterUiLibrary__CTixPanedWindow, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CTixPanedWindow(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTixPanedWindow')

    def __pyr_TkinterUiLibrary__CPanedwindow(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Panedwindow', kwds=kwds, __pyr_call_site_id=53)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CPanedwindow', __pyr_TkinterUiLibrary__CPanedwindow, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CPanedwindow(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CPanedwindow')

    def __pyr_TkinterUiLibrary__CPopupMenu(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='PopupMenu', kwds=kwds, __pyr_call_site_id=54)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CPopupMenu', __pyr_TkinterUiLibrary__CPopupMenu, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CPopupMenu(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CPopupMenu')

    def __pyr_TkinterUiLibrary__CProgressbar(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Progressbar', kwds=kwds, __pyr_call_site_id=55)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CProgressbar', __pyr_TkinterUiLibrary__CProgressbar, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CProgressbar(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CProgressbar')

    def __pyr_TkinterUiLibrary__CRadiobutton(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Radiobutton', kwds=kwds, __pyr_call_site_id=56)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CRadiobutton', __pyr_TkinterUiLibrary__CRadiobutton, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CRadiobutton(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CRadiobutton')

    def __pyr_TkinterUiLibrary__CTtkRadiobutton(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Radiobutton', kwds=kwds, __pyr_call_site_id=57)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTtkRadiobutton', __pyr_TkinterUiLibrary__CTtkRadiobutton, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CTtkRadiobutton(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTtkRadiobutton')

    def __pyr_TkinterUiLibrary__CResizeHandle(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='ResizeHandle', kwds=kwds, __pyr_call_site_id=58)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CResizeHandle', __pyr_TkinterUiLibrary__CResizeHandle, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CResizeHandle(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CResizeHandle')

    def __pyr_TkinterUiLibrary__CScale(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Scale', kwds=kwds, __pyr_call_site_id=59)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CScale', __pyr_TkinterUiLibrary__CScale, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CScale(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CScale')

    def __pyr_TkinterUiLibrary__CTtkScale(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Scale', kwds=kwds, __pyr_call_site_id=60)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTtkScale', __pyr_TkinterUiLibrary__CTtkScale, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CTtkScale(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTtkScale')

    def __pyr_TkinterUiLibrary__CScrollbar(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Scrollbar', kwds=kwds, __pyr_call_site_id=61)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CScrollbar', __pyr_TkinterUiLibrary__CScrollbar, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CScrollbar(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CScrollbar')

    def __pyr_TkinterUiLibrary__CTtkScrollbar(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Scrollbar', kwds=kwds, __pyr_call_site_id=62)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTtkScrollbar', __pyr_TkinterUiLibrary__CTtkScrollbar, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CTtkScrollbar(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTtkScrollbar')

    def __pyr_TkinterUiLibrary__CScrolledGrid(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='ScrolledGrid', kwds=kwds, __pyr_call_site_id=63)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CScrolledGrid', __pyr_TkinterUiLibrary__CScrolledGrid, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CScrolledGrid(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CScrolledGrid')

    def __pyr_TkinterUiLibrary__CScrolledHList(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='ScrolledHList', kwds=kwds, __pyr_call_site_id=64)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CScrolledHList', __pyr_TkinterUiLibrary__CScrolledHList, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CScrolledHList(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CScrolledHList')

    def __pyr_TkinterUiLibrary__CScrolledListBox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='ScrolledListBox', kwds=kwds, __pyr_call_site_id=65)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CScrolledListBox', __pyr_TkinterUiLibrary__CScrolledListBox, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CScrolledListBox(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CScrolledListBox')

    def __pyr_TkinterUiLibrary__CScrolledTList(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='ScrolledTList', kwds=kwds, __pyr_call_site_id=66)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CScrolledTList', __pyr_TkinterUiLibrary__CScrolledTList, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CScrolledTList(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CScrolledTList')

    def __pyr_TkinterUiLibrary__CScrolledtextScrolledText(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='ScrolledText', kwds=kwds, __pyr_call_site_id=67)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CScrolledtextScrolledText', __pyr_TkinterUiLibrary__CScrolledtextScrolledText, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CScrolledtextScrolledText(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CScrolledtextScrolledText')

    def __pyr_TkinterUiLibrary__CTixScrolledText(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='ScrolledText', kwds=kwds, __pyr_call_site_id=68)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTixScrolledText', __pyr_TkinterUiLibrary__CTixScrolledText, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CTixScrolledText(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTixScrolledText')

    def __pyr_TkinterUiLibrary__CScrolledWindow(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='ScrolledWindow', kwds=kwds, __pyr_call_site_id=69)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CScrolledWindow', __pyr_TkinterUiLibrary__CScrolledWindow, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CScrolledWindow(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CScrolledWindow')

    def __pyr_TkinterUiLibrary__CSelect(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Select', kwds=kwds, __pyr_call_site_id=70)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CSelect', __pyr_TkinterUiLibrary__CSelect, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CSelect(cls, master, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CSelect')

    def __pyr_TkinterUiLibrary__CSeparator(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Separator', kwds=kwds, __pyr_call_site_id=71)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CSeparator', __pyr_TkinterUiLibrary__CSeparator, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CSeparator(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CSeparator')

    def __pyr_TkinterUiLibrary__CShell(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Shell', kwds=kwds, __pyr_call_site_id=72)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CShell', __pyr_TkinterUiLibrary__CShell, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CShell(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CShell')

    def __pyr_TkinterUiLibrary__CSizegrip(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Sizegrip', kwds=kwds, __pyr_call_site_id=73)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CSizegrip', __pyr_TkinterUiLibrary__CSizegrip, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CSizegrip(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CSizegrip')

    def __pyr_TkinterUiLibrary__CSpinbox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Spinbox', kwds=kwds, __pyr_call_site_id=74)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CSpinbox', __pyr_TkinterUiLibrary__CSpinbox, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CSpinbox(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CSpinbox')

    def __pyr_TkinterUiLibrary__CTtkSpinbox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Spinbox', kwds=kwds, __pyr_call_site_id=75)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTtkSpinbox', __pyr_TkinterUiLibrary__CTtkSpinbox, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CTtkSpinbox(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTtkSpinbox')

    def __pyr_TkinterUiLibrary__CStdButtonBox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='StdButtonBox', kwds=kwds, __pyr_call_site_id=76)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CStdButtonBox', __pyr_TkinterUiLibrary__CStdButtonBox, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CStdButtonBox(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CStdButtonBox')

    def __pyr_TkinterUiLibrary__CTList(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='TList', kwds=kwds, __pyr_call_site_id=77)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTList', __pyr_TkinterUiLibrary__CTList, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CTList(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTList')

    def __pyr_TkinterUiLibrary__CText(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Text', kwds=kwds, __pyr_call_site_id=78)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CText', __pyr_TkinterUiLibrary__CText, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CText(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CText')

    def __pyr_TkinterUiLibrary__CTixSubWidget(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='TixSubWidget', kwds=kwds, __pyr_call_site_id=79)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTixSubWidget', __pyr_TkinterUiLibrary__CTixSubWidget, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically', 'check_intermediate')))
    def CTixSubWidget(cls, master, name, destroy_physically=1, check_intermediate=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTixSubWidget')

    def __pyr_TkinterUiLibrary__CTixWidget(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='TixWidget', kwds=kwds, __pyr_call_site_id=80)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTixWidget', __pyr_TkinterUiLibrary__CTixWidget, packed_kwargs=True, packed_kwarg_param_names=('master', 'widgetName', 'static_options', 'cnf', 'kw')))
    def CTixWidget(cls, master=None, widgetName=None, static_options=None, cnf={}, kw={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTixWidget')

    def __pyr_TkinterUiLibrary__CTree(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Tree', kwds=kwds, __pyr_call_site_id=81)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTree', __pyr_TkinterUiLibrary__CTree, packed_kwargs=True, packed_kwarg_param_names=('master', 'cnf')))
    def CTree(cls, master=None, cnf={}) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTree')

    def __pyr_TkinterUiLibrary__CTreeview(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='Treeview', kwds=kwds, __pyr_call_site_id=82)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.CTreeview', __pyr_TkinterUiLibrary__CTreeview, packed_kwargs=True, packed_kwarg_param_names=('master',)))
    def CTreeview(cls, master=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.CTreeview')

    def __pyr_TkinterUiLibrary__C_dummyButton(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyButton', kwds=kwds, __pyr_call_site_id=83)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyButton', __pyr_TkinterUiLibrary__C_dummyButton, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyButton(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyButton')

    def __pyr_TkinterUiLibrary__C_dummyCheckbutton(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyCheckbutton', kwds=kwds, __pyr_call_site_id=84)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyCheckbutton', __pyr_TkinterUiLibrary__C_dummyCheckbutton, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyCheckbutton(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyCheckbutton')

    def __pyr_TkinterUiLibrary__C_dummyComboBox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyComboBox', kwds=kwds, __pyr_call_site_id=85)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyComboBox', __pyr_TkinterUiLibrary__C_dummyComboBox, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyComboBox(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyComboBox')

    def __pyr_TkinterUiLibrary__C_dummyDirList(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyDirList', kwds=kwds, __pyr_call_site_id=86)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyDirList', __pyr_TkinterUiLibrary__C_dummyDirList, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyDirList(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyDirList')

    def __pyr_TkinterUiLibrary__C_dummyDirSelectBox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyDirSelectBox', kwds=kwds, __pyr_call_site_id=87)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyDirSelectBox', __pyr_TkinterUiLibrary__C_dummyDirSelectBox, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyDirSelectBox(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyDirSelectBox')

    def __pyr_TkinterUiLibrary__C_dummyEntry(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyEntry', kwds=kwds, __pyr_call_site_id=88)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyEntry', __pyr_TkinterUiLibrary__C_dummyEntry, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyEntry(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyEntry')

    def __pyr_TkinterUiLibrary__C_dummyExFileSelectBox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyExFileSelectBox', kwds=kwds, __pyr_call_site_id=89)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyExFileSelectBox', __pyr_TkinterUiLibrary__C_dummyExFileSelectBox, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyExFileSelectBox(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyExFileSelectBox')

    def __pyr_TkinterUiLibrary__C_dummyFileComboBox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyFileComboBox', kwds=kwds, __pyr_call_site_id=90)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyFileComboBox', __pyr_TkinterUiLibrary__C_dummyFileComboBox, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyFileComboBox(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyFileComboBox')

    def __pyr_TkinterUiLibrary__C_dummyFileSelectBox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyFileSelectBox', kwds=kwds, __pyr_call_site_id=91)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyFileSelectBox', __pyr_TkinterUiLibrary__C_dummyFileSelectBox, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyFileSelectBox(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyFileSelectBox')

    def __pyr_TkinterUiLibrary__C_dummyFrame(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyFrame', kwds=kwds, __pyr_call_site_id=92)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyFrame', __pyr_TkinterUiLibrary__C_dummyFrame, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyFrame(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyFrame')

    def __pyr_TkinterUiLibrary__C_dummyHList(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyHList', kwds=kwds, __pyr_call_site_id=93)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyHList', __pyr_TkinterUiLibrary__C_dummyHList, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyHList(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyHList')

    def __pyr_TkinterUiLibrary__C_dummyLabel(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyLabel', kwds=kwds, __pyr_call_site_id=94)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyLabel', __pyr_TkinterUiLibrary__C_dummyLabel, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyLabel(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyLabel')

    def __pyr_TkinterUiLibrary__C_dummyListbox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyListbox', kwds=kwds, __pyr_call_site_id=95)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyListbox', __pyr_TkinterUiLibrary__C_dummyListbox, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyListbox(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyListbox')

    def __pyr_TkinterUiLibrary__C_dummyMenu(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyMenu', kwds=kwds, __pyr_call_site_id=96)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyMenu', __pyr_TkinterUiLibrary__C_dummyMenu, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyMenu(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyMenu')

    def __pyr_TkinterUiLibrary__C_dummyMenubutton(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyMenubutton', kwds=kwds, __pyr_call_site_id=97)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyMenubutton', __pyr_TkinterUiLibrary__C_dummyMenubutton, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyMenubutton(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyMenubutton')

    def __pyr_TkinterUiLibrary__C_dummyNoteBookFrame(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyNoteBookFrame', kwds=kwds, __pyr_call_site_id=98)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyNoteBookFrame', __pyr_TkinterUiLibrary__C_dummyNoteBookFrame, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyNoteBookFrame(cls, master, name, destroy_physically=0) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyNoteBookFrame')

    def __pyr_TkinterUiLibrary__C_dummyPanedWindow(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyPanedWindow', kwds=kwds, __pyr_call_site_id=99)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyPanedWindow', __pyr_TkinterUiLibrary__C_dummyPanedWindow, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyPanedWindow(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyPanedWindow')

    def __pyr_TkinterUiLibrary__C_dummyScrollbar(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyScrollbar', kwds=kwds, __pyr_call_site_id=100)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyScrollbar', __pyr_TkinterUiLibrary__C_dummyScrollbar, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyScrollbar(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyScrollbar')

    def __pyr_TkinterUiLibrary__C_dummyScrolledHList(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyScrolledHList', kwds=kwds, __pyr_call_site_id=101)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyScrolledHList', __pyr_TkinterUiLibrary__C_dummyScrolledHList, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyScrolledHList(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyScrolledHList')

    def __pyr_TkinterUiLibrary__C_dummyScrolledListBox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyScrolledListBox', kwds=kwds, __pyr_call_site_id=102)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyScrolledListBox', __pyr_TkinterUiLibrary__C_dummyScrolledListBox, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyScrolledListBox(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyScrolledListBox')

    def __pyr_TkinterUiLibrary__C_dummyStdButtonBox(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyStdButtonBox', kwds=kwds, __pyr_call_site_id=103)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyStdButtonBox', __pyr_TkinterUiLibrary__C_dummyStdButtonBox, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyStdButtonBox(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyStdButtonBox')

    def __pyr_TkinterUiLibrary__C_dummyTList(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyTList', kwds=kwds, __pyr_call_site_id=104)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyTList', __pyr_TkinterUiLibrary__C_dummyTList, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyTList(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyTList')

    def __pyr_TkinterUiLibrary__C_dummyText(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='_dummyText', kwds=kwds, __pyr_call_site_id=105)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('TkinterUiLibrary.C_dummyText', __pyr_TkinterUiLibrary__C_dummyText, packed_kwargs=True, packed_kwarg_param_names=('master', 'name', 'destroy_physically')))
    def C_dummyText(cls, master, name, destroy_physically=1) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('TkinterUiLibrary.C_dummyText')