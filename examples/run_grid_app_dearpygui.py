"""Run the DearPyGui table grid demo (Phase 8) via ``pyrolyze_native_dearpygui``.

``uv run --extra dpg python examples/run_grid_app_dearpygui.py``

Rebuilds run synchronously after each interaction (DearPyGui 2.x
``set_frame_callback(frame, callback)`` is frame-indexed, not a single-arg API).

Counters match ``grid_app_pyside6.py``: each value uses **[-] [input] [+]**; typed
values are pulled from DearPyGui before each rebuild.
"""

from __future__ import annotations

import sys
from pathlib import Path

import dearpygui.dearpygui as dpg

_EX_DIR = Path(__file__).resolve().parent
if str(_EX_DIR) not in sys.path:
    sys.path.insert(0, str(_EX_DIR))

from dearpygui_demo_trees import DpgGridAppState, build_table_counter_grid
from pyrolyze.backends.mountable_engine import MountedMountableNode
from pyrolyze.pyrolyze_native_dearpygui import create_host, reconcile_window_content

_GRID_PREFIX = "grid"


def _tag_for_slot(node: MountedMountableNode, slot_id: str) -> int | None:
    if node.element.slot_id == slot_id:
        return int(node.mountable.tag)
    for ch in node.child_nodes:
        found = _tag_for_slot(ch, slot_id)
        if found is not None:
            return found
    return None


def _parse_dim(raw: str, fallback: int) -> int:
    try:
        return max(1, min(8, int(raw.strip())))
    except ValueError:
        return fallback


def _parse_cell_count(raw: str, fallback: int) -> int:
    try:
        return max(0, int(raw.strip()))
    except ValueError:
        return fallback


def main() -> int:
    state = DpgGridAppState()
    nhost = create_host(title="PyRolyze DearPyGui grid", width=560, height=680)
    name_slot = f"{_GRID_PREFIX}:ve:name"
    chk_slot = f"{_GRID_PREFIX}:ve:chk"

    def sync_value_widgets_from_dpg() -> None:
        root = nhost.root_node
        if root is None:
            return
        nt = _tag_for_slot(root, name_slot)
        if nt is not None and dpg.does_item_exist(nt):
            raw = dpg.get_value(nt)
            if isinstance(raw, str):
                state.name_field = raw
        ct = _tag_for_slot(root, chk_slot)
        if ct is not None and dpg.does_item_exist(ct):
            state.verbose = bool(dpg.get_value(ct))

        cv = _tag_for_slot(root, f"{_GRID_PREFIX}:header:cols:value")
        if cv is not None and dpg.does_item_exist(cv):
            raw = dpg.get_value(cv)
            if isinstance(raw, str):
                state.cols = _parse_dim(raw, state.cols)
        rv = _tag_for_slot(root, f"{_GRID_PREFIX}:header:rows:value")
        if rv is not None and dpg.does_item_exist(rv):
            raw = dpg.get_value(rv)
            if isinstance(raw, str):
                state.rows = _parse_dim(raw, state.rows)

        for r in range(state.rows):
            for c in range(state.cols):
                tv = _tag_for_slot(root, f"{_GRID_PREFIX}:cell:{r}:{c}:value")
                if tv is not None and dpg.does_item_exist(tv):
                    raw = dpg.get_value(tv)
                    if isinstance(raw, str):
                        cur = state.counts.get((r, c), 0)
                        state.counts[(r, c)] = _parse_cell_count(raw, cur)

    def rebuild_update() -> None:
        sync_value_widgets_from_dpg()

        def schedule_rebuild() -> None:
            rebuild_update()

        tree = build_table_counter_grid(
            state,
            on_quit=dpg.stop_dearpygui,
            on_cols_delta=lambda d: _dim_cols(d),
            on_rows_delta=lambda d: _dim_rows(d),
            on_cell_delta=_cell_delta,
            on_counter_value_edited=schedule_rebuild,
            include_value_panel=True,
            value_handlers=(schedule_rebuild, schedule_rebuild),
            prefix=_GRID_PREFIX,
        )
        reconcile_window_content(nhost, (tree,))

    def _dim_cols(delta: int) -> None:
        sync_value_widgets_from_dpg()
        state.cols = max(1, min(8, state.cols + delta))
        rebuild_update()

    def _dim_rows(delta: int) -> None:
        sync_value_widgets_from_dpg()
        state.rows = max(1, min(8, state.rows + delta))
        rebuild_update()

    def _cell_delta(r: int, c: int, delta: int) -> None:
        sync_value_widgets_from_dpg()
        v = state.counts.get((r, c), 0)
        state.counts[(r, c)] = max(0, v + delta)
        rebuild_update()

    try:
        rebuild_update()
        nhost.run()
    finally:
        nhost.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
