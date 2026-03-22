from __future__ import annotations

import os
from pathlib import Path
from runpy import run_path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples"
GRID_APP_PATH = EXAMPLES_ROOT / "grid_app_pyside6.py"
RUNNER_PATH = EXAMPLES_ROOT / "run_grid_app_pyside6.py"


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

        cols_value = host.root_widget.findChild(QLabel, "header:cols:value")
        rows_value = host.root_widget.findChild(QLabel, "header:rows:value")
        first_cell_value = host.root_widget.findChild(QLabel, "cell:0:0:value")
        first_cell_increment = host.root_widget.findChild(QPushButton, "cell:0:0:increment")
        assert cols_value is not None
        assert rows_value is not None
        assert first_cell_value is not None
        assert first_cell_increment is not None
        assert cols_value.text() == "2"
        assert rows_value.text() == "2"
        assert first_cell_value.text() == "0"

        first_cell_increment.click()
        _pump_events()
        first_cell_value = host.root_widget.findChild(QLabel, "cell:0:0:value")
        assert first_cell_value is not None
        assert first_cell_value.text() == "1"

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

        cols_value = host.root_widget.findChild(QLabel, "header:cols:value")
        rows_value = host.root_widget.findChild(QLabel, "header:rows:value")
        assert cols_value is not None
        assert rows_value is not None
        assert cols_value.text() == "3"
        assert rows_value.text() == "1"
        assert host.root_widget.findChild(QLabel, "cell:0:2:value") is not None
        assert host.root_widget.findChild(QLabel, "cell:1:0:value") is None
    finally:
        ctx.close_app_contexts()
        host.close()
