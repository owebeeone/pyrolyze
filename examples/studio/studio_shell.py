#@pyrolyze
"""Phase 1 Studio shell: frameless chrome, menus, explorer column, panel layout, tab strips, status bar.

See ``dev-docs/StudioAppRecreation.md``. Uses box layouts with stretch factors instead of
``QSplitter`` (splitter child mounts currently hit mount-engine limitations). Drag/resize,
inspector services, and screenshot drawing are out of scope; title buttons and explorer
model are wired from ``run_studio.py`` / ``studio_native``.

Editor buffers sync from menu actions (New/Open/Save) into ``use_state``; unsourced typing
is not written back (``QTextEdit`` has no generated ``textChanged`` hook), so switching tabs
or reconciling can discard in-widget edits that were not saved via the File menu.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFileSystemModel,
    QMainWindow,
    QMessageBox,
    QTextEdit,
    QTreeView,
)

from pyrolyze.api import mount, pyrolyze, use_state
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as W

_EDITOR_TEXTS = (
    (
        "Welcome to the PyRolyze Studio Phase 1 shell.\n\n"
        "This recreates the imperative ``studio_app.py`` layout using "
        "PySide6UiLibrary inside @pyrolyze (see dev-docs/StudioAppRecreation.md).\n"
    ),
    "# main.py\nprint('hello studio')\n",
    '{\n  "phase": 1\n}\n',
)

_BOTTOM_TEXTS = (
    "No problems.\n",
    "[Output] Phase 1 shell — build succeeded.\n",
    "$ \n",
)

# Updated each ``studio_phase1_shell`` render so menu ``on_triggered`` handlers can patch buffers.
_menu_sink: list[tuple[Callable[[Callable[[tuple[str, str, str]], tuple[str, str, str]]], None], int]] = []


def _menu_register(
    set_editor_buffers: Callable[[Callable[[tuple[str, str, str]], tuple[str, str, str]]], None],
    editor_tab: int,
) -> None:
    _menu_sink.clear()
    _menu_sink.append((set_editor_buffers, editor_tab))


def _menu_patch_buffer(tab_index: int, text: str) -> None:
    if not _menu_sink:
        return
    set_buffers, _ = _menu_sink[0]

    def _upd(prev: tuple[str, str, str]) -> tuple[str, str, str]:
        row = list(prev)
        row[tab_index] = text
        return tuple(row)

    set_buffers(_upd)


def _menu_active_tab() -> int:
    return _menu_sink[0][1] if _menu_sink else 0


def _studio_root() -> QMainWindow | None:
    app = QApplication.instance()
    if app is None:
        return None
    for top in app.topLevelWidgets():
        if isinstance(top, QMainWindow) and top.objectName() == "studio:main":
            return top
    return None


def _studio_text_edit(object_name: str) -> QTextEdit | None:
    root = _studio_root()
    return None if root is None else root.findChild(QTextEdit, object_name)


def _studio_tree_view() -> QTreeView | None:
    root = _studio_root()
    return None if root is None else root.findChild(QTreeView, "studio:explorer:tree")


def _log_bottom(message: str) -> None:
    te = _studio_text_edit("studio:bottom:body")
    if te is not None:
        te.appendPlainText(message + "\n")


def _active_text_edit() -> QTextEdit | None:
    app = QApplication.instance()
    if app is None:
        return None
    fw = app.focusWidget()
    if isinstance(fw, QTextEdit):
        return fw
    return _studio_text_edit("studio:editor:body")


def _menu_file_new() -> None:
    tab = _menu_active_tab()
    if tab == 0:
        _log_bottom("[File] New — welcome tab is read-only; switch to an editor tab.")
        return
    _menu_patch_buffer(tab, "")
    _log_bottom("[File] New (cleared current buffer)")


def _menu_file_open() -> None:
    root = _studio_root()
    path, _ = QFileDialog.getOpenFileName(root, "Open File", "", "All files (*.*)")
    if not path:
        return
    tab = _menu_active_tab()
    if tab == 0:
        _log_bottom("[File] Open — switch off the welcome tab to load into the buffer.")
        return
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        QMessageBox.warning(root, "Open File", str(exc))
        return
    _menu_patch_buffer(tab, text)
    _log_bottom(f"[File] Opened {path}")


def _menu_file_open_folder() -> None:
    root = _studio_root()
    path = QFileDialog.getExistingDirectory(root, "Open Folder", str(Path.home()))
    if not path:
        return
    try:
        tree = _studio_tree_view()
        if tree is None:
            return
        model = QFileSystemModel()
        model.setRootPath(path)
        tree.setModel(model)
        tree.setRootIndex(model.index(path))
        _log_bottom(f"[File] Explorer root → {path}")
    except Exception as exc:  # noqa: BLE001 — show any model failure
        QMessageBox.warning(root, "Open Folder", str(exc))


def _menu_file_save() -> None:
    root = _studio_root()
    body = _studio_text_edit("studio:editor:body")
    if body is None:
        return
    tab = _menu_active_tab()
    if tab == 0:
        _log_bottom("[File] Save — welcome tab is read-only.")
        return
    path, _ = QFileDialog.getSaveFileName(root, "Save File", "", "All files (*.*)")
    if not path:
        return
    try:
        Path(path).write_text(body.toPlainText(), encoding="utf-8")
    except OSError as exc:
        QMessageBox.warning(root, "Save File", str(exc))
        return
    _menu_patch_buffer(tab, body.toPlainText())
    _log_bottom(f"[File] Saved {path}")


def _menu_file_save_as() -> None:
    _menu_file_save()


def _menu_file_exit() -> None:
    root = _studio_root()
    if root is not None:
        root.close()


def _menu_edit_undo() -> None:
    te = _active_text_edit()
    if te is not None:
        te.undo()


def _menu_edit_redo() -> None:
    te = _active_text_edit()
    if te is not None:
        te.redo()


def _menu_edit_cut() -> None:
    te = _active_text_edit()
    if te is not None:
        te.cut()


def _menu_edit_copy() -> None:
    te = _active_text_edit()
    if te is not None:
        te.copy()


def _menu_edit_paste() -> None:
    te = _active_text_edit()
    if te is not None:
        te.paste()


def _menu_view_zoom(delta: int) -> None:
    app = QApplication.instance()
    if app is None:
        return
    f = app.font()
    f.setPointSize(max(6, min(36, f.pointSize() + delta)))
    app.setFont(f)


def _menu_view_fullscreen() -> None:
    root = _studio_root()
    if root is None:
        return
    if root.isFullScreen():
        root.showNormal()
    else:
        root.showFullScreen()


def _menu_help_about() -> None:
    root = _studio_root()
    QMessageBox.about(
        root,
        "About PyRolyze Studio",
        "PyRolyze Studio — Phase 1 shell example.\n\n"
        "Declarative UI via PySide6UiLibrary; see dev-docs/StudioAppRecreation.md.",
    )


@pyrolyze
def studio_menus(set_editor_tab, set_show_explorer) -> None:
    """Menus use ``on_triggered``; structure matches ``grid_app_pyside6.app_menu_bar``."""
    with W.CQMenuBar(objectName="studio:menubar", nativeMenuBar=False):
        with mount(W.mounts.action):
            with W.CQAction("&File", objectName="studio:menu:file:top"):
                with W.CQMenu("&File", objectName="studio:menu:file"):
                    with mount(W.mounts.action):
                        W.CQAction("&New", objectName="studio:menu:file:new", on_triggered=_menu_file_new)
                        W.CQAction("&Open…", objectName="studio:menu:file:open", on_triggered=_menu_file_open)
                        W.CQAction(
                            "Open &Folder…",
                            objectName="studio:menu:file:folder",
                            on_triggered=_menu_file_open_folder,
                        )
                        W.CQAction("&Save", objectName="studio:menu:file:save", on_triggered=_menu_file_save)
                        W.CQAction(
                            "Save &As…",
                            objectName="studio:menu:file:saveas",
                            on_triggered=_menu_file_save_as,
                        )
                        W.CQAction("E&xit", objectName="studio:menu:file:exit", on_triggered=_menu_file_exit)
            with W.CQAction("&Edit", objectName="studio:menu:edit:top"):
                with W.CQMenu("&Edit", objectName="studio:menu:edit"):
                    with mount(W.mounts.action):
                        W.CQAction("&Undo", objectName="studio:menu:edit:undo", on_triggered=_menu_edit_undo)
                        W.CQAction("&Redo", objectName="studio:menu:edit:redo", on_triggered=_menu_edit_redo)
                        W.CQAction("Cu&t", objectName="studio:menu:edit:cut", on_triggered=_menu_edit_cut)
                        W.CQAction("&Copy", objectName="studio:menu:edit:copy", on_triggered=_menu_edit_copy)
                        W.CQAction("&Paste", objectName="studio:menu:edit:paste", on_triggered=_menu_edit_paste)
            with W.CQAction("&View", objectName="studio:menu:view:top"):
                with W.CQMenu("&View", objectName="studio:menu:view"):
                    with mount(W.mounts.action):
                        W.CQAction(
                            "Toggle &Explorer",
                            objectName="studio:menu:view:explorer",
                            on_triggered=lambda: set_show_explorer(lambda v: not bool(v)),
                        )
                        W.CQAction(
                            "Toggle &Welcome",
                            objectName="studio:menu:view:welcome",
                            on_triggered=lambda: set_editor_tab(0),
                        )
                        W.CQAction(
                            "Zoom &In",
                            objectName="studio:menu:view:zoomin",
                            on_triggered=lambda: _menu_view_zoom(1),
                        )
                        W.CQAction(
                            "Zoom &Out",
                            objectName="studio:menu:view:zoomout",
                            on_triggered=lambda: _menu_view_zoom(-1),
                        )
                        W.CQAction(
                            "&Fullscreen",
                            objectName="studio:menu:view:fullscreen",
                            on_triggered=_menu_view_fullscreen,
                        )
            with W.CQAction("&Help", objectName="studio:menu:help:top"):
                with W.CQMenu("&Help", objectName="studio:menu:help"):
                    with mount(W.mounts.action):
                        W.CQAction(
                            "&About",
                            objectName="studio:menu:help:about",
                            on_triggered=_menu_help_about,
                        )


@pyrolyze
def studio_title_bar() -> None:
    """Custom chrome row (caption + window controls). Menus live on ``QMainWindow`` via ``mount(menu_bar)``."""
    with W.CQWidget(objectName="studio_title_bar"):
        with W.CQHBoxLayout():
            W.CQLabel(
                "PyRolyze Studio — Phase 1",
                objectName="studio_title_caption",
            )
            W.CQPushButton(
                "—",
                objectName="studio_title_min",
                flat=True,
            )
            W.CQPushButton(
                "□",
                objectName="studio_title_max",
                flat=True,
            )
            W.CQPushButton(
                "×",
                objectName="studio_title_close",
                flat=True,
            )


@pyrolyze
def studio_explorer_pane() -> None:
    with W.CQWidget(objectName="studio:explorer:column"):
        with W.CQVBoxLayout():
            with W.CQWidget(objectName="studio:explorer:toolbar_row"):
                with W.CQHBoxLayout():
                    W.CQLabel("Explorer", objectName="studio:explorer:toolbar:caption")
                    W.CQPushButton(
                        "Open Folder",
                        objectName="studio:explorer:tb:folder",
                        flat=True,
                    )
                    W.CQPushButton(
                        "Refresh",
                        objectName="studio:explorer:tb:refresh",
                        flat=True,
                    )
                    W.CQPushButton(
                        "Collapse",
                        objectName="studio:explorer:tb:collapse",
                        flat=True,
                    )
            W.CQTreeView(
                objectName="studio:explorer:tree",
                headerHidden=False,
                alternatingRowColors=True,
            )


@pyrolyze
def studio_editor_area(editor_tab: int, set_editor_tab, editor_buffers: tuple[str, str, str]) -> None:
    """Tab strip + single ``QTextEdit`` (avoids ``QStackedWidget`` multi-child mount issues)."""
    with W.CQWidget(objectName="studio:editor:wrap"):
        with W.CQVBoxLayout():
            with W.CQWidget(objectName="studio:editor:tabs"):
                with W.CQHBoxLayout():
                    W.CQPushButton(
                        "Welcome",
                        objectName="studio:editor:tab:0",
                        checkable=True,
                        checked=editor_tab == 0,
                        on_clicked=lambda: set_editor_tab(0),
                    )
                    W.CQPushButton(
                        "main.py",
                        objectName="studio:editor:tab:1",
                        checkable=True,
                        checked=editor_tab == 1,
                        on_clicked=lambda: set_editor_tab(1),
                    )
                    W.CQPushButton(
                        "settings.json",
                        objectName="studio:editor:tab:2",
                        checkable=True,
                        checked=editor_tab == 2,
                        on_clicked=lambda: set_editor_tab(2),
                    )
            W.CQTextEdit(
                readOnly=(editor_tab == 0),
                plainText=editor_buffers[editor_tab],
                objectName="studio:editor:body",
            )


@pyrolyze
def studio_bottom_area(bottom_tab: int, set_bottom_tab) -> None:
    with W.CQWidget(objectName="studio:bottom:wrap"):
        with W.CQVBoxLayout():
            with W.CQWidget(objectName="studio:bottom:tabs"):
                with W.CQHBoxLayout():
                    W.CQPushButton(
                        "Problems",
                        objectName="studio:bottom:tab:0",
                        checkable=True,
                        checked=bottom_tab == 0,
                        on_clicked=lambda: set_bottom_tab(0),
                    )
                    W.CQPushButton(
                        "Output",
                        objectName="studio:bottom:tab:1",
                        checkable=True,
                        checked=bottom_tab == 1,
                        on_clicked=lambda: set_bottom_tab(1),
                    )
                    W.CQPushButton(
                        "Terminal",
                        objectName="studio:bottom:tab:2",
                        checkable=True,
                        checked=bottom_tab == 2,
                        on_clicked=lambda: set_bottom_tab(2),
                    )
            W.CQTextEdit(
                readOnly=(bottom_tab != 2),
                plainText=_BOTTOM_TEXTS[bottom_tab],
                objectName="studio:bottom:body",
            )


@pyrolyze
def studio_main_panels(
    editor_tab: int,
    set_editor_tab,
    editor_buffers: tuple[str, str, str],
    bottom_tab: int,
    set_bottom_tab,
) -> None:
    """Vertical stack without ``QSplitter`` (splitter widget mounts hit ordered-mount limitations)."""
    with W.CQWidget(objectName="studio:split:vertical"):
        with W.CQVBoxLayout():
            with mount(W.mounts.widget(stretch=5)):
                studio_editor_area(editor_tab, set_editor_tab, editor_buffers)
            with mount(W.mounts.widget(stretch=2)):
                studio_bottom_area(bottom_tab, set_bottom_tab)


@pyrolyze
def studio_central(
    editor_tab: int,
    set_editor_tab,
    editor_buffers: tuple[str, str, str],
    bottom_tab: int,
    set_bottom_tab,
    show_explorer: bool,
) -> None:
    with W.CQWidget(objectName="studio:split:horizontal"):
        with W.CQHBoxLayout():
            if show_explorer:
                with mount(W.mounts.widget(stretch=1)):
                    studio_explorer_pane()
            with mount(W.mounts.widget(stretch=4 if show_explorer else 1)):
                studio_main_panels(
                    editor_tab,
                    set_editor_tab,
                    editor_buffers,
                    bottom_tab,
                    set_bottom_tab,
                )


@pyrolyze
def studio_phase1_shell() -> None:
    editor_buffers, set_editor_buffers = use_state(_EDITOR_TEXTS)
    editor_tab, set_editor_tab = use_state(0)
    bottom_tab, set_bottom_tab = use_state(1)
    show_explorer, set_show_explorer = use_state(True)
    _menu_register(set_editor_buffers, editor_tab)

    with W.CQMainWindow(
        windowTitle="PyRolyze Studio",
        objectName="studio:main",
        minimumWidth=1024,
        minimumHeight=700,
    ):
        # QMenuBar must attach via QMainWindow.setMenuBar (menu_bar mount), not inside central layout.
        with mount(W.mounts.menu_bar):
            studio_menus(set_editor_tab, set_show_explorer)
        with mount(W.mounts.central_widget):
            with W.CQWidget(objectName="studio:central"):
                with W.CQVBoxLayout():
                    studio_title_bar()
                    studio_central(
                        editor_tab,
                        set_editor_tab,
                        editor_buffers,
                        bottom_tab,
                        set_bottom_tab,
                        show_explorer,
                    )
        with mount(W.mounts.status_bar):
            W.CQStatusBar(objectName="studio:status")
