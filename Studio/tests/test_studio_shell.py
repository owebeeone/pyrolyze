from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMenuBar, QPushButton

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
        assert window.min_button.text() == "─"
        assert window.max_button.text() == "□"
        assert window.close_button.text() == "✕"
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
