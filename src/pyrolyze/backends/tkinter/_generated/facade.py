"""Generated lazy native facade; definitions load by indexed group."""
from __future__ import annotations
from typing import Any, ClassVar
from collections.abc import Mapping
from frozendict import frozendict
from pyrolyze.api import MountSelector, UIElement, ui_interface
from pyrolyze.backends.model import UiInterface, UiInterfaceEntry, UiWidgetSpec
from pyrolyze.backends.lazy_library import LazyLibraryCatalog, LazyUiLibraryMeta
from .index import ENTRIES, GENERATION
from pyrolyze.backends.generated_package import admit_generated_package
admit_generated_package(__file__, GENERATION)

@ui_interface
class TkinterUiLibrary(metaclass=LazyUiLibraryMeta):
    ROOT_MODULE: ClassVar[str] = 'tkinter'
    _lazy_catalog = LazyLibraryCatalog(__package__, GENERATION, ENTRIES)
    def __getattr__(self, name: str) -> Any:
        return getattr(type(self), name)
    WIDGET_SPECS: ClassVar[Mapping[str, UiWidgetSpec]] = _lazy_catalog
    UI_INTERFACE = UiInterface(name='TkinterUiLibrary', owner=None, entries=frozendict({
            "CBalloon": UiInterfaceEntry(public_name="CBalloon", kind="Balloon"),
            "CButtonBox": UiInterfaceEntry(public_name="CButtonBox", kind="ButtonBox"),
            "CCObjView": UiInterfaceEntry(public_name="CCObjView", kind="CObjView"),
            "CCanvas": UiInterfaceEntry(public_name="CCanvas", kind="Canvas"),
            "CCheckList": UiInterfaceEntry(public_name="CCheckList", kind="CheckList"),
            "CComboBox": UiInterfaceEntry(public_name="CComboBox", kind="ComboBox"),
            "CCombobox": UiInterfaceEntry(public_name="CCombobox", kind="Combobox"),
            "CControl": UiInterfaceEntry(public_name="CControl", kind="Control"),
            "CDialog": UiInterfaceEntry(public_name="CDialog", kind="Dialog"),
            "CDialogShell": UiInterfaceEntry(public_name="CDialogShell", kind="DialogShell"),
            "CDirList": UiInterfaceEntry(public_name="CDirList", kind="DirList"),
            "CDirSelectBox": UiInterfaceEntry(public_name="CDirSelectBox", kind="DirSelectBox"),
            "CDirSelectDialog": UiInterfaceEntry(public_name="CDirSelectDialog", kind="DirSelectDialog"),
            "CDirTree": UiInterfaceEntry(public_name="CDirTree", kind="DirTree"),
            "CExFileSelectBox": UiInterfaceEntry(public_name="CExFileSelectBox", kind="ExFileSelectBox"),
            "CExFileSelectDialog": UiInterfaceEntry(public_name="CExFileSelectDialog", kind="ExFileSelectDialog"),
            "CFileEntry": UiInterfaceEntry(public_name="CFileEntry", kind="FileEntry"),
            "CFileSelectBox": UiInterfaceEntry(public_name="CFileSelectBox", kind="FileSelectBox"),
            "CFileSelectDialog": UiInterfaceEntry(public_name="CFileSelectDialog", kind="FileSelectDialog"),
            "CGrid": UiInterfaceEntry(public_name="CGrid", kind="Grid"),
            "CHList": UiInterfaceEntry(public_name="CHList", kind="HList"),
            "CInputOnly": UiInterfaceEntry(public_name="CInputOnly", kind="InputOnly"),
            "CLabelEntry": UiInterfaceEntry(public_name="CLabelEntry", kind="LabelEntry"),
            "CLabeledScale": UiInterfaceEntry(public_name="CLabeledScale", kind="LabeledScale"),
            "CLabelframe": UiInterfaceEntry(public_name="CLabelframe", kind="Labelframe"),
            "CListNoteBook": UiInterfaceEntry(public_name="CListNoteBook", kind="ListNoteBook"),
            "CListbox": UiInterfaceEntry(public_name="CListbox", kind="Listbox"),
            "CMenu": UiInterfaceEntry(public_name="CMenu", kind="Menu"),
            "CMessage": UiInterfaceEntry(public_name="CMessage", kind="Message"),
            "CMeter": UiInterfaceEntry(public_name="CMeter", kind="Meter"),
            "CNoteBook": UiInterfaceEntry(public_name="CNoteBook", kind="NoteBook"),
            "CNoteBookFrame": UiInterfaceEntry(public_name="CNoteBookFrame", kind="NoteBookFrame"),
            "CNotebook": UiInterfaceEntry(public_name="CNotebook", kind="Notebook"),
            "CPanedwindow": UiInterfaceEntry(public_name="CPanedwindow", kind="Panedwindow"),
            "CPopupMenu": UiInterfaceEntry(public_name="CPopupMenu", kind="PopupMenu"),
            "CProgressbar": UiInterfaceEntry(public_name="CProgressbar", kind="Progressbar"),
            "CResizeHandle": UiInterfaceEntry(public_name="CResizeHandle", kind="ResizeHandle"),
            "CScrolledGrid": UiInterfaceEntry(public_name="CScrolledGrid", kind="ScrolledGrid"),
            "CScrolledHList": UiInterfaceEntry(public_name="CScrolledHList", kind="ScrolledHList"),
            "CScrolledListBox": UiInterfaceEntry(public_name="CScrolledListBox", kind="ScrolledListBox"),
            "CScrolledTList": UiInterfaceEntry(public_name="CScrolledTList", kind="ScrolledTList"),
            "CScrolledWindow": UiInterfaceEntry(public_name="CScrolledWindow", kind="ScrolledWindow"),
            "CSelect": UiInterfaceEntry(public_name="CSelect", kind="Select"),
            "CSeparator": UiInterfaceEntry(public_name="CSeparator", kind="Separator"),
            "CShell": UiInterfaceEntry(public_name="CShell", kind="Shell"),
            "CSizegrip": UiInterfaceEntry(public_name="CSizegrip", kind="Sizegrip"),
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
            "CScrolledtextScrolledText": UiInterfaceEntry(public_name="CScrolledtextScrolledText", kind="scrolledtext_ScrolledText"),
            "CTixLabelFrame": UiInterfaceEntry(public_name="CTixLabelFrame", kind="tix_LabelFrame"),
            "CTixOptionMenu": UiInterfaceEntry(public_name="CTixOptionMenu", kind="tix_OptionMenu"),
            "CTixPanedWindow": UiInterfaceEntry(public_name="CTixPanedWindow", kind="tix_PanedWindow"),
            "CTixScrolledText": UiInterfaceEntry(public_name="CTixScrolledText", kind="tix_ScrolledText"),
            "CButton": UiInterfaceEntry(public_name="CButton", kind="tkinter_Button"),
            "CCheckbutton": UiInterfaceEntry(public_name="CCheckbutton", kind="tkinter_Checkbutton"),
            "CEntry": UiInterfaceEntry(public_name="CEntry", kind="tkinter_Entry"),
            "CFrame": UiInterfaceEntry(public_name="CFrame", kind="tkinter_Frame"),
            "CLabel": UiInterfaceEntry(public_name="CLabel", kind="tkinter_Label"),
            "CLabelFrame": UiInterfaceEntry(public_name="CLabelFrame", kind="tkinter_LabelFrame"),
            "CMenubutton": UiInterfaceEntry(public_name="CMenubutton", kind="tkinter_Menubutton"),
            "COptionMenu": UiInterfaceEntry(public_name="COptionMenu", kind="tkinter_OptionMenu"),
            "CPanedWindow": UiInterfaceEntry(public_name="CPanedWindow", kind="tkinter_PanedWindow"),
            "CRadiobutton": UiInterfaceEntry(public_name="CRadiobutton", kind="tkinter_Radiobutton"),
            "CScale": UiInterfaceEntry(public_name="CScale", kind="tkinter_Scale"),
            "CScrollbar": UiInterfaceEntry(public_name="CScrollbar", kind="tkinter_Scrollbar"),
            "CSpinbox": UiInterfaceEntry(public_name="CSpinbox", kind="tkinter_Spinbox"),
            "CTtkButton": UiInterfaceEntry(public_name="CTtkButton", kind="ttk_Button"),
            "CTtkCheckbutton": UiInterfaceEntry(public_name="CTtkCheckbutton", kind="ttk_Checkbutton"),
            "CTtkEntry": UiInterfaceEntry(public_name="CTtkEntry", kind="ttk_Entry"),
            "CTtkFrame": UiInterfaceEntry(public_name="CTtkFrame", kind="ttk_Frame"),
            "CTtkLabel": UiInterfaceEntry(public_name="CTtkLabel", kind="ttk_Label"),
            "CTtkMenubutton": UiInterfaceEntry(public_name="CTtkMenubutton", kind="ttk_Menubutton"),
            "CTtkOptionMenu": UiInterfaceEntry(public_name="CTtkOptionMenu", kind="ttk_OptionMenu"),
            "CTtkRadiobutton": UiInterfaceEntry(public_name="CTtkRadiobutton", kind="ttk_Radiobutton"),
            "CTtkScale": UiInterfaceEntry(public_name="CTtkScale", kind="ttk_Scale"),
            "CTtkScrollbar": UiInterfaceEntry(public_name="CTtkScrollbar", kind="ttk_Scrollbar"),
            "CTtkSpinbox": UiInterfaceEntry(public_name="CTtkSpinbox", kind="ttk_Spinbox"),
    }))

    class mounts:
        grid = MountSelector.named("grid")
        pack = MountSelector.named("pack")
        pane = MountSelector.named("pane")
        tab = MountSelector.named("tab")

    @classmethod
    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
        return UIElement(kind=kind, props=dict(kwds))
