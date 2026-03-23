from __future__ import annotations

import os
from pathlib import Path
from runpy import run_path
import time

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QGridLayout, QGroupBox, QLineEdit, QMainWindow, QMenu, QMenuBar, QPushButton, QScrollArea, QWidget
from pyrolyze.backends.mountable_engine import MountableEngine


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples"
GRID_APP_PATH = EXAMPLES_ROOT / "grid_app_pyside6.py"
RUNNER_PATH = EXAMPLES_ROOT / "run_grid_app_pyside6.py"


def _pump_events_until(host, predicate, *, max_steps: int = 400) -> None:
    for _ in range(max_steps):
        host.app.processEvents()
        if predicate():
            return
    raise AssertionError("timed out waiting for PySide6 example UI to settle")


def test_native_grid_app_example_mounts_and_rerenders() -> None:
    assert GRID_APP_PATH.exists()
    assert RUNNER_PATH.exists()

    namespace = run_path(str(RUNNER_PATH))
    build_app_host = namespace["build_app_host"]
    host, ctx = build_app_host()

    def _pump_events() -> None:
        for _ in range(10):
            host.app.processEvents()

    try:
        assert isinstance(host.root_widget, QMainWindow)
        host.show()
        _pump_events()
        assert host.root_widget.width() >= 800
        assert host.root_widget.height() >= 500
        menu_bar = host.root_widget.findChild(QMenuBar, "app:menu_bar")
        grid_scroll = host.root_widget.findChild(QScrollArea, "grid:scroll")
        header_group = host.root_widget.findChild(QGroupBox, "header:group")
        assert menu_bar is not None
        assert host.root_widget.menuBar() is menu_bar
        assert menu_bar.isNativeMenuBar() is False
        assert menu_bar.isVisible() is True
        assert grid_scroll is not None
        assert header_group is not None
        assert header_group.isVisible() is True
        assert grid_scroll.isVisible() is True
        assert grid_scroll.widgetResizable() is True
        assert header_group.parent() is not grid_scroll.widget()

        file_action = next(
            (action for action in menu_bar.actions() if action.objectName() == "menu:file:action"),
            None,
        )
        assert isinstance(file_action, QAction)
        file_menu = file_action.menu()
        assert isinstance(file_menu, QMenu)
        assert file_menu.objectName() == "menu:file:menu"
        assert [action.text() for action in file_menu.actions()] == [
            "New Grid",
            "Reset Counts",
            "Randomize",
            "Expand",
            "Collapse",
            "Advanced",
        ]

        advanced_action = next(
            (action for action in file_menu.actions() if action.objectName() == "menu:file:advanced:action"),
            None,
        )
        assert isinstance(advanced_action, QAction)
        advanced_menu = advanced_action.menu()
        assert isinstance(advanced_menu, QMenu)
        assert advanced_menu.objectName() == "menu:file:advanced:menu"
        assert [action.text() for action in advanced_menu.actions()] == [
            "Toggle Grid Mode",
            "Snapshot",
        ]
        toggle_layout_action = next(
            (action for action in advanced_menu.actions() if action.objectName() == "menu:file:advanced:toggle_layout:action"),
            None,
        )
        assert isinstance(toggle_layout_action, QAction)

        cols_value = host.root_widget.findChild(QLineEdit, "header:cols:value")
        rows_value = host.root_widget.findChild(QLineEdit, "header:rows:value")
        first_cell_decrement = host.root_widget.findChild(QPushButton, "cell:0:0:decrement")
        first_cell_value = host.root_widget.findChild(QLineEdit, "cell:0:0:value")
        first_cell_increment = host.root_widget.findChild(QPushButton, "cell:0:0:increment")
        assert cols_value is not None
        assert rows_value is not None
        assert first_cell_decrement is not None
        assert first_cell_value is not None
        assert first_cell_increment is not None
        assert cols_value.text() == "2"
        assert rows_value.text() == "2"
        assert first_cell_value.text() == "0"
        assert host.root_widget.findChild(QGridLayout, "grid:matrix:layout") is None
        assert host.root_widget.findChild(QPushButton, "header:layout:toggle") is not None
        assert host.root_widget.findChild(QGroupBox, "cell:0:0:group") is not None
        assert host.root_widget.findChild(QWidget, "grid:row:0") is not None

        first_cell_increment.click()
        _pump_events()
        first_cell_value = host.root_widget.findChild(QLineEdit, "cell:0:0:value")
        assert first_cell_value is not None
        assert first_cell_value.text() == "1"

        first_cell_value.setText("7")
        _pump_events()
        first_cell_value = host.root_widget.findChild(QLineEdit, "cell:0:0:value")
        assert first_cell_value is not None
        assert first_cell_value.text() == "7"

        cols_increment = host.root_widget.findChild(QPushButton, "header:cols:increment")
        rows_decrement = host.root_widget.findChild(QPushButton, "header:rows:decrement")
        assert cols_increment is not None
        assert rows_decrement is not None

        cols_increment.click()
        _pump_events()
        rows_decrement = host.root_widget.findChild(QPushButton, "header:rows:decrement")
        assert rows_decrement is not None
        rows_decrement.click()
        _pump_events()

        cols_value = host.root_widget.findChild(QLineEdit, "header:cols:value")
        rows_value = host.root_widget.findChild(QLineEdit, "header:rows:value")
        assert cols_value is not None
        assert rows_value is not None
        assert cols_value.text() == "3"
        assert rows_value.text() == "1"
        assert host.root_widget.findChild(QLineEdit, "cell:0:2:value") is not None
        assert host.root_widget.findChild(QLineEdit, "cell:1:0:value") is None

        layout_toggle = host.root_widget.findChild(QPushButton, "header:layout:toggle")
        assert layout_toggle is not None
        layout_toggle.click()
        _pump_events()

        grid_layout = host.root_widget.findChild(QGridLayout, "grid:matrix:layout")
        assert grid_layout is not None
        assert host.root_widget.findChild(QWidget, "grid:row:0") is None
        assert host.root_widget.findChild(QGroupBox, "cell:0:0:group") is not None

        cols_decrement = host.root_widget.findChild(QPushButton, "header:cols:decrement")
        assert cols_decrement is not None
        cols_decrement.click()
        _pump_events()

        assert host.root_widget.findChild(QGridLayout, "grid:matrix:layout") is not None
        assert host.root_widget.findChild(QGroupBox, "cell:0:2:group") is None
        assert host.root_widget.findChild(QGroupBox, "cell:0:1:group") is not None

        layout_toggle = host.root_widget.findChild(QPushButton, "header:layout:toggle")
        assert layout_toggle is not None
        layout_toggle.click()
        _pump_events()

        assert host.root_widget.findChild(QGridLayout, "grid:matrix:layout") is None
        assert host.root_widget.findChild(QWidget, "grid:row:0") is not None
        assert host.root_widget.findChild(QGroupBox, "cell:0:0:group") is not None

        toggle_layout_action.trigger()
        _pump_events()

        assert host.root_widget.findChild(QGridLayout, "grid:matrix:layout") is not None
        assert host.root_widget.findChild(QWidget, "grid:row:0") is None

        toggle_layout_action.trigger()
        _pump_events()

        assert host.root_widget.findChild(QGridLayout, "grid:matrix:layout") is None
        assert host.root_widget.findChild(QWidget, "grid:row:0") is not None
    finally:
        ctx.close_app_contexts()


def test_native_grid_app_large_layout_toggle_stays_within_operation_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    namespace = run_path(str(RUNNER_PATH))
    build_app_host = namespace["build_app_host"]
    host, ctx = build_app_host()

    counts = {
        "mount": 0,
        "update": 0,
        "_create_mountable": 0,
        "_replace_node_mountable": 0,
    }

    def _wrap(method_name: str) -> None:
        original = getattr(MountableEngine, method_name)

        def wrapped(self, *args, **kwargs):
            counts[method_name] += 1
            return original(self, *args, **kwargs)

        monkeypatch.setattr(MountableEngine, method_name, wrapped)

    try:
        host.show()
        _pump_events_until(host, lambda: host.root_widget is not None)

        cols_value = host.root_widget.findChild(QLineEdit, "header:cols:value")
        rows_value = host.root_widget.findChild(QLineEdit, "header:rows:value")
        toggle = host.root_widget.findChild(QPushButton, "header:layout:toggle")
        assert cols_value is not None
        assert rows_value is not None
        assert toggle is not None

        cols_value.setText("20")
        rows_value.setText("20")
        _pump_events_until(
            host,
            lambda: host.root_widget.findChild(QGroupBox, "cell:19:19:group") is not None,
        )

        for method_name in counts:
            _wrap(method_name)

        started_at = time.perf_counter()
        toggle.click()
        _pump_events_until(
            host,
            lambda: host.root_widget.findChild(QGridLayout, "grid:matrix:layout") is not None,
        )

        toggle = host.root_widget.findChild(QPushButton, "header:layout:toggle")
        assert toggle is not None
        toggle.click()
        _pump_events_until(
            host,
            lambda: host.root_widget.findChild(QWidget, "grid:row:19") is not None,
        )
        elapsed_s = time.perf_counter() - started_at

        assert counts["mount"] <= 6000
        assert counts["update"] <= 7000
        assert counts["_create_mountable"] <= 6000
        assert counts["_replace_node_mountable"] <= 50
        assert elapsed_s <= 6.0
    finally:
        ctx.close_app_contexts()
        host.close()
