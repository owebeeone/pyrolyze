"""Phase 8: mount smoke tests (optional ``dearpygui``)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("dearpygui")

import dearpygui.dearpygui as dpg

_EX = Path(__file__).resolve().parents[1] / "examples"
if str(_EX) not in sys.path:
    sys.path.insert(0, str(_EX))
import dearpygui_demo_trees as demo

from pyrolyze.backends.dearpygui.engine import DpgMountableEngine
from pyrolyze.backends.dearpygui.live_host import LiveDpgHost
from pyrolyze.backends.dearpygui.specs import FIXTURE_WIDGET_SPECS


def test_mount_window_menu_smoke() -> None:
    host = LiveDpgHost(title="t", width=80, height=80, show_viewport=False)
    host.start()
    try:
        eng = DpgMountableEngine(FIXTURE_WIDGET_SPECS, host)
        tree = demo.build_window_menu_bar(on_quit=lambda: None, prefix="ms")
        root = eng.mount(tree)
        assert dpg.does_item_exist(int(root.mountable.tag))
    finally:
        host.stop()


def test_mount_full_grid_tree_smoke() -> None:
    host = LiveDpgHost(title="g", width=120, height=120, show_viewport=False)
    host.start()
    try:
        eng = DpgMountableEngine(FIXTURE_WIDGET_SPECS, host)
        state = demo.DpgGridAppState(cols=2, rows=2)
        noop = lambda: None
        tree = demo.build_table_counter_grid(
            state,
            on_quit=noop,
            on_cols_delta=lambda _d: None,
            on_rows_delta=lambda _d: None,
            on_cell_delta=lambda _r, _c, _d: None,
            on_counter_value_edited=noop,
            include_value_panel=True,
            value_handlers=(noop, noop),
        )
        root = eng.mount(tree)
        assert dpg.does_item_exist(int(root.mountable.tag))
    finally:
        host.stop()
