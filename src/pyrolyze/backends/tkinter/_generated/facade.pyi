from typing import Any, ClassVar
from collections.abc import Mapping
from pyrolyze.api import MISSING, MissingType, MountSelector, PyrolyzeHandler
from pyrolyze.backends.model import UiInterface, UiWidgetSpec
import tkinter

class TkinterUiLibrary:
    ROOT_MODULE: ClassVar[str]
    UI_INTERFACE: ClassVar[UiInterface]
    WIDGET_SPECS: ClassVar[Mapping[str, UiWidgetSpec]]

    class mounts:
        grid = MountSelector.named("grid")
        pack = MountSelector.named("pack")
        pane = MountSelector.named("pane")
        tab = MountSelector.named("tab")

    @classmethod
    def CBalloon(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CButtonBox(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CCObjView(
        cls,
        master = None,
        widgetName = None,
        static_options = None,
        cnf = {},
        kw = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CCanvas(
        cls,
        master = None,
        cnf = {},
        *,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        closeenough: Any | MissingType = MISSING,
        confine: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        insertbackground: Any | MissingType = MISSING,
        insertborderwidth: Any | MissingType = MISSING,
        insertofftime: Any | MissingType = MISSING,
        insertontime: Any | MissingType = MISSING,
        insertwidth: Any | MissingType = MISSING,
        offset: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        scrollregion: Any | MissingType = MISSING,
        selectbackground: Any | MissingType = MISSING,
        selectborderwidth: Any | MissingType = MISSING,
        selectforeground: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        xscrollcommand: Any | MissingType = MISSING,
        xscrollincrement: Any | MissingType = MISSING,
        yscrollcommand: Any | MissingType = MISSING,
        yscrollincrement: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CCheckList(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
        entrypath: Any | MissingType = MISSING,
        mode: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CComboBox(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CCombobox(
        cls,
        master = None,
        *,
        background: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        exportselection: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        invalidcommand: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        placeholder: Any | MissingType = MISSING,
        placeholderforeground: Any | MissingType = MISSING,
        postcommand: Any | MissingType = MISSING,
        show: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        validate: Any | MissingType = MISSING,
        validatecommand: Any | MissingType = MISSING,
        values: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        xscrollcommand: Any | MissingType = MISSING,
        value: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CControl(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CDialog(
        cls,
        master = None,
        cnf = {},
    ) -> None:
        ...

    @classmethod
    def CDialogShell(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CDirList(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CDirSelectBox(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CDirSelectDialog(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CDirTree(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CExFileSelectBox(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CExFileSelectDialog(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CFileEntry(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CFileSelectBox(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CFileSelectDialog(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CGrid(
        cls,
        master = None,
        cnf = {},
        *,
        x: Any | MissingType = MISSING,
        y: Any | MissingType = MISSING,
        itemtype: Any | MissingType = MISSING,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CHList(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CInputOnly(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CLabelEntry(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CLabeledScale(
        cls,
        master = None,
        variable = None,
        from_ = 0,
        to = 10,
        *,
        borderwidth: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CLabelframe(
        cls,
        master = None,
        *,
        borderwidth: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        labelanchor: Any | MissingType = MISSING,
        labelwidget: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CListNoteBook(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CListbox(
        cls,
        master = None,
        cnf = {},
        *,
        activestyle: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        disabledforeground: Any | MissingType = MISSING,
        exportselection: Any | MissingType = MISSING,
        fg: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        listvariable: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        selectbackground: Any | MissingType = MISSING,
        selectborderwidth: Any | MissingType = MISSING,
        selectforeground: Any | MissingType = MISSING,
        selectmode: Any | MissingType = MISSING,
        setgrid: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        xscrollcommand: Any | MissingType = MISSING,
        yscrollcommand: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CMenu(
        cls,
        *,
        activebackground: Any | MissingType = MISSING,
        activeborderwidth: Any | MissingType = MISSING,
        activeforeground: Any | MissingType = MISSING,
        activerelief: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        disabledforeground: Any | MissingType = MISSING,
        fg: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        postcommand: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        selectcolor: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        tearoff: Any | MissingType = MISSING,
        tearoffcommand: Any | MissingType = MISSING,
        title: Any | MissingType = MISSING,
        type: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CMessage(
        cls,
        master = None,
        cnf = {},
        *,
        anchor: Any | MissingType = MISSING,
        aspect: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        fg: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        padx: Any | MissingType = MISSING,
        pady: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CMeter(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CNoteBook(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CNoteBookFrame(
        cls,
        master = None,
        widgetName = None,
        static_options = None,
        cnf = {},
        kw = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CNotebook(
        cls,
        *,
        cursor: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CPanedwindow(
        cls,
        *,
        cursor: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        orient: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CPopupMenu(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CProgressbar(
        cls,
        master = None,
        *,
        anchor: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        length: Any | MissingType = MISSING,
        maximum: Any | MissingType = MISSING,
        mode: Any | MissingType = MISSING,
        orient: Any | MissingType = MISSING,
        phase: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        value: Any | MissingType = MISSING,
        variable: Any | MissingType = MISSING,
        wraplength: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CResizeHandle(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CScrolledGrid(
        cls,
        master = None,
        cnf = {},
        *,
        x: Any | MissingType = MISSING,
        y: Any | MissingType = MISSING,
        itemtype: Any | MissingType = MISSING,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CScrolledHList(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CScrolledListBox(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CScrolledTList(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CScrolledWindow(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CSelect(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CSeparator(
        cls,
        master = None,
        *,
        cursor: Any | MissingType = MISSING,
        orient: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CShell(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CSizegrip(
        cls,
        master = None,
        *,
        cursor: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CStdButtonBox(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTList(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CText(
        cls,
        master = None,
        cnf = {},
        *,
        autoseparators: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        blockcursor: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        endline: Any | MissingType = MISSING,
        exportselection: Any | MissingType = MISSING,
        fg: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        inactiveselectbackground: Any | MissingType = MISSING,
        insertbackground: Any | MissingType = MISSING,
        insertborderwidth: Any | MissingType = MISSING,
        insertofftime: Any | MissingType = MISSING,
        insertontime: Any | MissingType = MISSING,
        insertunfocussed: Any | MissingType = MISSING,
        insertwidth: Any | MissingType = MISSING,
        maxundo: Any | MissingType = MISSING,
        padx: Any | MissingType = MISSING,
        pady: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        selectbackground: Any | MissingType = MISSING,
        selectborderwidth: Any | MissingType = MISSING,
        selectforeground: Any | MissingType = MISSING,
        setgrid: Any | MissingType = MISSING,
        spacing1: Any | MissingType = MISSING,
        spacing2: Any | MissingType = MISSING,
        spacing3: Any | MissingType = MISSING,
        startline: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        tabs: Any | MissingType = MISSING,
        tabstyle: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        undo: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        wrap: Any | MissingType = MISSING,
        xscrollcommand: Any | MissingType = MISSING,
        yscrollcommand: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTixSubWidget(
        cls,
        master,
        name,
        destroy_physically = 1,
        check_intermediate = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTixWidget(
        cls,
        master = None,
        widgetName = None,
        static_options = None,
        cnf = {},
        kw = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTree(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
        entrypath: Any | MissingType = MISSING,
        mode: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTreeview(
        cls,
        master = None,
        *,
        columns: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        displaycolumns: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        selectmode: Any | MissingType = MISSING,
        selecttype: Any | MissingType = MISSING,
        show: Any | MissingType = MISSING,
        striped: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        titlecolumns: Any | MissingType = MISSING,
        titleitems: Any | MissingType = MISSING,
        xscrollcommand: Any | MissingType = MISSING,
        yscrollcommand: Any | MissingType = MISSING,
        item: Any | MissingType = MISSING,
        column: Any | MissingType = MISSING,
        value: Any | MissingType = MISSING,
        _children: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyButton(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyCheckbutton(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyComboBox(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyDirList(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyDirSelectBox(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyEntry(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyExFileSelectBox(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyFileComboBox(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyFileSelectBox(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyFrame(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyHList(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyLabel(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyListbox(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyMenu(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyMenubutton(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyNoteBookFrame(
        cls,
        master,
        name,
        destroy_physically = 0,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyPanedWindow(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyScrollbar(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        first: Any | MissingType = MISSING,
        last: Any | MissingType = MISSING,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyScrolledHList(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyScrolledListBox(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyStdButtonBox(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyTList(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def C_dummyText(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CScrolledtextScrolledText(
        cls,
        master = None,
        *,
        autoseparators: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        blockcursor: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        endline: Any | MissingType = MISSING,
        exportselection: Any | MissingType = MISSING,
        fg: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        inactiveselectbackground: Any | MissingType = MISSING,
        insertbackground: Any | MissingType = MISSING,
        insertborderwidth: Any | MissingType = MISSING,
        insertofftime: Any | MissingType = MISSING,
        insertontime: Any | MissingType = MISSING,
        insertunfocussed: Any | MissingType = MISSING,
        insertwidth: Any | MissingType = MISSING,
        maxundo: Any | MissingType = MISSING,
        padx: Any | MissingType = MISSING,
        pady: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        selectbackground: Any | MissingType = MISSING,
        selectborderwidth: Any | MissingType = MISSING,
        selectforeground: Any | MissingType = MISSING,
        setgrid: Any | MissingType = MISSING,
        spacing1: Any | MissingType = MISSING,
        spacing2: Any | MissingType = MISSING,
        spacing3: Any | MissingType = MISSING,
        startline: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        tabs: Any | MissingType = MISSING,
        tabstyle: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        undo: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        wrap: Any | MissingType = MISSING,
        xscrollcommand: Any | MissingType = MISSING,
        yscrollcommand: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTixLabelFrame(
        cls,
        master = None,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTixOptionMenu(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTixPanedWindow(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTixScrolledText(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CButton(
        cls,
        *,
        activebackground: Any | MissingType = MISSING,
        activeforeground: Any | MissingType = MISSING,
        anchor: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        bitmap: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        compound: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        default: Any | MissingType = MISSING,
        disabledforeground: Any | MissingType = MISSING,
        fg: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        image: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        overrelief: Any | MissingType = MISSING,
        padx: Any | MissingType = MISSING,
        pady: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        repeatdelay: Any | MissingType = MISSING,
        repeatinterval: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        wraplength: Any | MissingType = MISSING,
        on_command: PyrolyzeHandler[[], None] | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CCheckbutton(
        cls,
        master = None,
        cnf = {},
        *,
        activebackground: Any | MissingType = MISSING,
        activeforeground: Any | MissingType = MISSING,
        anchor: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        bitmap: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        command: Any | MissingType = MISSING,
        compound: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        disabledforeground: Any | MissingType = MISSING,
        fg: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        image: Any | MissingType = MISSING,
        indicatoron: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        offrelief: Any | MissingType = MISSING,
        offvalue: Any | MissingType = MISSING,
        onvalue: Any | MissingType = MISSING,
        overrelief: Any | MissingType = MISSING,
        padx: Any | MissingType = MISSING,
        pady: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        selectcolor: Any | MissingType = MISSING,
        selectimage: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        tristateimage: Any | MissingType = MISSING,
        tristatevalue: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        variable: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        wraplength: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CEntry(
        cls,
        *,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        disabledbackground: Any | MissingType = MISSING,
        disabledforeground: Any | MissingType = MISSING,
        exportselection: Any | MissingType = MISSING,
        fg: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        insertbackground: Any | MissingType = MISSING,
        insertborderwidth: Any | MissingType = MISSING,
        insertofftime: Any | MissingType = MISSING,
        insertontime: Any | MissingType = MISSING,
        insertwidth: Any | MissingType = MISSING,
        invalidcommand: Any | MissingType = MISSING,
        invcmd: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        placeholder: Any | MissingType = MISSING,
        placeholderforeground: Any | MissingType = MISSING,
        readonlybackground: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        selectbackground: Any | MissingType = MISSING,
        selectborderwidth: Any | MissingType = MISSING,
        selectforeground: Any | MissingType = MISSING,
        show: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        validate: Any | MissingType = MISSING,
        validatecommand: Any | MissingType = MISSING,
        vcmd: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        xscrollcommand: Any | MissingType = MISSING,
        on_key_release: PyrolyzeHandler[[Any], None] | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CFrame(
        cls,
        *,
        background: Any | MissingType = MISSING,
        backgroundimage: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        bgimg: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        colormap: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        padx: Any | MissingType = MISSING,
        pady: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        tile: Any | MissingType = MISSING,
        visual: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CLabel(
        cls,
        master = None,
        cnf = {},
        *,
        activebackground: Any | MissingType = MISSING,
        activeforeground: Any | MissingType = MISSING,
        anchor: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        bitmap: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        compound: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        disabledforeground: Any | MissingType = MISSING,
        fg: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        image: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        padx: Any | MissingType = MISSING,
        pady: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        wraplength: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CLabelFrame(
        cls,
        master = None,
        cnf = {},
        *,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        colormap: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        fg: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        labelanchor: Any | MissingType = MISSING,
        labelwidget: Any | MissingType = MISSING,
        padx: Any | MissingType = MISSING,
        pady: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        visual: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CMenubutton(
        cls,
        master = None,
        cnf = {},
        *,
        activebackground: Any | MissingType = MISSING,
        activeforeground: Any | MissingType = MISSING,
        anchor: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        bitmap: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        compound: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        direction: Any | MissingType = MISSING,
        disabledforeground: Any | MissingType = MISSING,
        fg: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        image: Any | MissingType = MISSING,
        indicatoron: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        menu: Any | MissingType = MISSING,
        padx: Any | MissingType = MISSING,
        pady: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        wraplength: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def COptionMenu(
        cls,
        master,
        variable,
        value,
    ) -> None:
        ...

    @classmethod
    def CPanedWindow(
        cls,
        *,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        handlepad: Any | MissingType = MISSING,
        handlesize: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        opaqueresize: Any | MissingType = MISSING,
        orient: Any | MissingType = MISSING,
        proxybackground: Any | MissingType = MISSING,
        proxyborderwidth: Any | MissingType = MISSING,
        proxyrelief: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        sashcursor: Any | MissingType = MISSING,
        sashpad: Any | MissingType = MISSING,
        sashrelief: Any | MissingType = MISSING,
        sashwidth: Any | MissingType = MISSING,
        showhandle: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CRadiobutton(
        cls,
        master = None,
        cnf = {},
        *,
        activebackground: Any | MissingType = MISSING,
        activeforeground: Any | MissingType = MISSING,
        anchor: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        bitmap: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        command: Any | MissingType = MISSING,
        compound: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        disabledforeground: Any | MissingType = MISSING,
        fg: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        image: Any | MissingType = MISSING,
        indicatoron: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        offrelief: Any | MissingType = MISSING,
        overrelief: Any | MissingType = MISSING,
        padx: Any | MissingType = MISSING,
        pady: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        selectcolor: Any | MissingType = MISSING,
        selectimage: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        tristateimage: Any | MissingType = MISSING,
        tristatevalue: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        value: Any | MissingType = MISSING,
        variable: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        wraplength: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CScale(
        cls,
        master = None,
        cnf = {},
        *,
        activebackground: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        bigincrement: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        command: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        digits: Any | MissingType = MISSING,
        fg: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        label: Any | MissingType = MISSING,
        length: Any | MissingType = MISSING,
        orient: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        repeatdelay: Any | MissingType = MISSING,
        repeatinterval: Any | MissingType = MISSING,
        resolution: Any | MissingType = MISSING,
        showvalue: Any | MissingType = MISSING,
        sliderlength: Any | MissingType = MISSING,
        sliderrelief: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        tickinterval: Any | MissingType = MISSING,
        to: Any | MissingType = MISSING,
        troughcolor: Any | MissingType = MISSING,
        variable: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        value: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CScrollbar(
        cls,
        master = None,
        cnf = {},
        *,
        activebackground: Any | MissingType = MISSING,
        activerelief: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        command: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        elementborderwidth: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        jump: Any | MissingType = MISSING,
        orient: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        repeatdelay: Any | MissingType = MISSING,
        repeatinterval: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        troughcolor: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        first: Any | MissingType = MISSING,
        last: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CSpinbox(
        cls,
        master = None,
        cnf = {},
        *,
        activebackground: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        buttonbackground: Any | MissingType = MISSING,
        buttoncursor: Any | MissingType = MISSING,
        buttondownrelief: Any | MissingType = MISSING,
        buttonuprelief: Any | MissingType = MISSING,
        command: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        disabledbackground: Any | MissingType = MISSING,
        disabledforeground: Any | MissingType = MISSING,
        exportselection: Any | MissingType = MISSING,
        fg: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        format: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        increment: Any | MissingType = MISSING,
        insertbackground: Any | MissingType = MISSING,
        insertborderwidth: Any | MissingType = MISSING,
        insertofftime: Any | MissingType = MISSING,
        insertontime: Any | MissingType = MISSING,
        insertwidth: Any | MissingType = MISSING,
        invalidcommand: Any | MissingType = MISSING,
        invcmd: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        placeholder: Any | MissingType = MISSING,
        placeholderforeground: Any | MissingType = MISSING,
        readonlybackground: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        repeatdelay: Any | MissingType = MISSING,
        repeatinterval: Any | MissingType = MISSING,
        selectbackground: Any | MissingType = MISSING,
        selectborderwidth: Any | MissingType = MISSING,
        selectforeground: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        to: Any | MissingType = MISSING,
        validate: Any | MissingType = MISSING,
        validatecommand: Any | MissingType = MISSING,
        values: Any | MissingType = MISSING,
        vcmd: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        wrap: Any | MissingType = MISSING,
        xscrollcommand: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTtkButton(
        cls,
        *,
        compound: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        default: Any | MissingType = MISSING,
        image: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        on_command: PyrolyzeHandler[[], None] | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTtkCheckbutton(
        cls,
        master = None,
        *,
        command: Any | MissingType = MISSING,
        compound: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        image: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        offvalue: Any | MissingType = MISSING,
        onvalue: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        variable: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTtkEntry(
        cls,
        *,
        background: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        exportselection: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        invalidcommand: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        placeholder: Any | MissingType = MISSING,
        placeholderforeground: Any | MissingType = MISSING,
        show: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        validate: Any | MissingType = MISSING,
        validatecommand: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        xscrollcommand: Any | MissingType = MISSING,
        on_key_release: PyrolyzeHandler[[Any], None] | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTtkFrame(
        cls,
        *,
        borderwidth: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTtkLabel(
        cls,
        master = None,
        *,
        anchor: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        compound: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        image: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        wraplength: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTtkMenubutton(
        cls,
        master = None,
        *,
        compound: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        direction: Any | MissingType = MISSING,
        image: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        menu: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTtkOptionMenu(
        cls,
        master,
        variable,
        default = None,
        *,
        _menu: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTtkRadiobutton(
        cls,
        master = None,
        *,
        command: Any | MissingType = MISSING,
        compound: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        image: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        value: Any | MissingType = MISSING,
        variable: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTtkScale(
        cls,
        master = None,
        *,
        command: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        length: Any | MissingType = MISSING,
        orient: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        to: Any | MissingType = MISSING,
        value: Any | MissingType = MISSING,
        variable: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTtkScrollbar(
        cls,
        master = None,
        *,
        command: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        orient: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        first: Any | MissingType = MISSING,
        last: Any | MissingType = MISSING,
    ) -> None:
        ...

    @classmethod
    def CTtkSpinbox(
        cls,
        master = None,
        *,
        background: Any | MissingType = MISSING,
        command: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        exportselection: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        format: Any | MissingType = MISSING,
        increment: Any | MissingType = MISSING,
        invalidcommand: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        placeholder: Any | MissingType = MISSING,
        placeholderforeground: Any | MissingType = MISSING,
        show: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        to: Any | MissingType = MISSING,
        validate: Any | MissingType = MISSING,
        validatecommand: Any | MissingType = MISSING,
        values: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        wrap: Any | MissingType = MISSING,
        xscrollcommand: Any | MissingType = MISSING,
        value: Any | MissingType = MISSING,
    ) -> None:
        ...
