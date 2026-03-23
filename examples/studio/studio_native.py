"""Phase 1 native helpers living next to the Studio example (see ``StudioAppRecreation.md``).

The declarative tree cannot model ``QFileSystemModel`` or unhooked title-bar chrome;
this module attaches them after the first reconcile from the runner.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QDir, Qt
from PySide6.QtWidgets import QFileSystemModel, QMainWindow, QPushButton, QStatusBar, QTreeView

if TYPE_CHECKING:
    from pyrolyze.pyrolyze_native_pyside6 import NativePySide6Host


def wire_title_bar_controls(host: NativePySide6Host) -> None:
    """Connect minimize / maximize / close for frameless chrome (Phase 2 adds drag)."""
    root = host.root_widget
    if not isinstance(root, QMainWindow):
        return

    min_btn = root.findChild(QPushButton, "studio_title_min")
    max_btn = root.findChild(QPushButton, "studio_title_max")
    close_btn = root.findChild(QPushButton, "studio_title_close")

    if min_btn is not None:
        min_btn.clicked.connect(root.showMinimized)

    if max_btn is not None:

        def _toggle_max() -> None:
            if root.isMaximized():
                root.showNormal()
                max_btn.setText("□")
            else:
                root.showMaximized()
                max_btn.setText("❐")

        max_btn.clicked.connect(_toggle_max)

    if close_btn is not None:
        close_btn.clicked.connect(root.close)


def show_status_message(host: NativePySide6Host, message: str = "Phase 1 shell — PySide6UiLibrary") -> None:
    root = host.root_widget
    if not isinstance(root, QMainWindow):
        return
    bar = root.findChild(QStatusBar, "studio:status")
    if bar is not None:
        bar.showMessage(message)


def attach_explorer_model(host: NativePySide6Host, root_path: str | None = None) -> None:
    """Attach a simple ``QFileSystemModel`` to the explorer ``QTreeView`` (placeholder bridge)."""
    root = host.root_widget
    if not isinstance(root, QMainWindow):
        return
    tree = root.findChild(QTreeView, "studio:explorer:tree")
    if tree is None:
        return
    model = QFileSystemModel()
    path = root_path or QDir.homePath()
    model.setRootPath(path)
    tree.setModel(model)
    tree.setRootIndex(model.index(path))
    tree.setHeaderHidden(False)


def apply_frameless_root_hints(host: NativePySide6Host) -> None:
    """Phase 1: frameless flag is not a supported ``CQMainWindow`` mount prop — apply here."""
    root = host.root_widget
    if isinstance(root, QMainWindow):
        root.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
        )
        root.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
