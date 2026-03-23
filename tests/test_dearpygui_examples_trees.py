"""Phase 8: structural tests for DearPyGui example ``UIElement`` trees."""

from __future__ import annotations

import sys
from pathlib import Path


def _demo_mod():
    ex = Path(__file__).resolve().parents[1] / "examples"
    if str(ex) not in sys.path:
        sys.path.insert(0, str(ex))
    import dearpygui_demo_trees as m

    return m


def test_window_menu_tree_has_menu_and_quit() -> None:
    m = _demo_mod()
    called: list[int] = []

    def on_quit() -> None:
        called.append(1)

    tree = m.build_window_menu_bar(on_quit=on_quit, prefix="t")
    assert tree.kind == "DpgWindow"
    assert len(tree.children) >= 2
    assert tree.children[0].kind == "DpgMenuBar"
    mb = tree.children[0]
    assert mb.children[0].kind == "DpgMenu"
    assert mb.children[0].children[0].kind == "DpgMenuItem"
    quit_item = mb.children[0].children[0]
    assert quit_item.props.get("label") == "Quit"
    quit_item.props["callback"]()
    assert called == [1]


def test_grid_tree_table_dimensions_and_cells() -> None:
    m = _demo_mod()
    state = m.DpgGridAppState(cols=2, rows=3)
    noop = lambda: None
    tree = m.build_table_counter_grid(
        state,
        on_quit=noop,
        on_cols_delta=lambda _d: None,
        on_rows_delta=lambda _d: None,
        on_cell_delta=lambda _r, _c, _d: None,
        on_counter_value_edited=noop,
        include_value_panel=False,
        prefix="g",
    )
    assert tree.kind == "DpgWindow"
    table = next(ch for ch in tree.children if ch.kind == "DpgTable")
    cols = [ch for ch in table.children if ch.kind == "DpgTableColumn"]
    rows = [ch for ch in table.children if ch.kind == "DpgTableRow"]
    assert len(cols) == 2
    assert len(rows) == 3
    for row in rows:
        assert len(row.children) == 2
        for cell in row.children:
            assert cell.kind == "DpgGroup"
            assert cell.children[0].kind == "DpgText"
            inner = cell.children[1]
            assert inner.kind == "DpgGroup"
            assert inner.props.get("horizontal") is True
            assert len(inner.children) == 3
            assert inner.children[0].kind == "DpgButton"
            assert inner.children[1].kind == "DpgInputText"
            assert inner.children[2].kind == "DpgButton"


def test_value_events_children_kinds() -> None:
    m = _demo_mod()
    state = m.DpgGridAppState()
    ch = m.build_value_events_children(state, on_name_change=lambda: None, on_toggle=lambda: None)
    kinds = [x.kind for x in ch]
    assert "DpgInputText" in kinds
    assert "DpgCheckbox" in kinds
    assert kinds.count("DpgButton") >= 1
