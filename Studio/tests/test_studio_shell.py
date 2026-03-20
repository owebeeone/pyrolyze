from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMenuBar, QPushButton, QSplitter, QTabWidget

from Studio.host.studio_shell import StudioMainWindow, create_studio_window


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_shell_host_window_is_frameless() -> None:
    _app()
    host = create_studio_window("Studio", width=1000, height=700)
    try:
        flags = host.window.windowFlags()
        assert bool(flags & Qt.WindowType.FramelessWindowHint)
    finally:
        host.close()


def test_shell_has_custom_title_bar_controls() -> None:
    _app()
    host = create_studio_window("Studio", width=1000, height=700)
    try:
        window = host.window
        assert window.title_bar.objectName() == "custom_title_bar_widget"
        assert isinstance(window.menu_bar, QMenuBar)
        assert window.menu_bar.objectName() == "title_bar_menu_bar_widget"
        assert isinstance(window.close_button, QPushButton)
        assert window.close_button.objectName() == "close_button"
        assert window.min_button.text() == "\u2500"
        assert window.max_button.text() == "\u25A1"
        assert window.close_button.text() == "\u2715"
    finally:
        host.close()


def test_shell_context_menu_contains_expected_actions() -> None:
    _app()
    host = create_studio_window("Studio", width=1000, height=700)
    try:
        actions = [action.text() for action in host.window.build_title_bar_context_menu().actions()]
        for expected in ("Maximize", "Move", "Size", "Open Inspector", "Minimize", "Close"):
            assert expected in actions
    finally:
        host.close()


def test_shell_creates_eight_resize_handles() -> None:
    _app()
    host = create_studio_window("Studio", width=1000, height=700)
    try:
        assert len(host.window.resize_handles) == 8
    finally:
        host.close()


def test_shell_exposes_workspace_splitter_topology() -> None:
    _app()
    host = create_studio_window("Studio", width=1200, height=820)
    try:
        window = host.window
        assert isinstance(window.workspace_splitter, QSplitter)
        assert window.workspace_splitter.orientation() == Qt.Orientation.Horizontal
        assert window.workspace_splitter.count() == 2

        assert isinstance(window.vertical_splitter, QSplitter)
        assert window.vertical_splitter.orientation() == Qt.Orientation.Vertical
        assert window.vertical_splitter.count() == 2
    finally:
        host.close()


def test_shell_configures_editor_and_bottom_tabs() -> None:
    _app()
    host = create_studio_window("Studio", width=1200, height=820)
    try:
        window = host.window
        assert isinstance(window.editor_tabs, QTabWidget)
        assert window.editor_tabs.tabsClosable() is True
        assert window.editor_tabs.isMovable() is True
        assert [window.editor_tabs.tabText(i) for i in range(window.editor_tabs.count())] == [
            "Editor 1",
            "Editor 2",
            "Welcome",
        ]

        assert isinstance(window.bottom_tabs, QTabWidget)
        assert [window.bottom_tabs.tabText(i) for i in range(window.bottom_tabs.count())] == [
            "Output",
            "Terminal",
        ]
    finally:
        host.close()


def test_shell_mount_target_lives_inside_first_editor_tab() -> None:
    _app()
    host = create_studio_window("Studio", width=1200, height=820)
    try:
        window = host.window
        assert host.content_widget.parentWidget() is window.editor_render_page
        assert window.editor_tabs.indexOf(window.editor_render_page) == 0
        assert window.editor_tabs.tabText(0) == "Editor 1"
    finally:
        host.close()


def test_shell_explorer_panel_has_toolbar_and_tree() -> None:
    _app()
    host = create_studio_window("Studio", width=1200, height=820)
    try:
        window = host.window
        assert window.explorer_toolbar.objectName() == "explorer_toolbar"
        assert len(window.explorer_toolbar.actions()) == 3
        assert window.explorer_toolbar.actions()[0].toolTip() == "Open Folder"
        assert window.explorer_toolbar.actions()[1].toolTip() == "Refresh Explorer"
        assert window.explorer_toolbar.actions()[2].toolTip() == "Collapse Folders"
        assert window.explorer_tree is not None
        assert window.explorer_model is not None
    finally:
        host.close()
