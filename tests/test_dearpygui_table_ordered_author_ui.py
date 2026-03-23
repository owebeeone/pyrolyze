"""``DearPyGuiC.TableOrdered`` enforces columns-then-rows at the API shape level."""

from __future__ import annotations

from pyrolyze.backends.dearpygui.author_ui import (
    DearPyGuiC,
    DearPyGuiTableColumnPhase,
    DearPyGuiTableRowPhase,
)


def test_table_ordered_emits_columns_before_rows() -> None:
    c1 = DearPyGuiC.TableColumn(slot_id="c1")
    c2 = DearPyGuiC.TableColumn(slot_id="c2")
    r1 = DearPyGuiC.TableRow(slot_id="r1", children=())
    table = DearPyGuiC.TableOrdered(slot_id="tbl", header_row=False).columns(c1, c2).rows(r1)
    assert table.kind == "DpgTable"
    kinds = [ch.kind for ch in table.children]
    assert kinds[:2] == ["DpgTableColumn", "DpgTableColumn"]
    assert kinds[2] == "DpgTableRow"
    assert table.props.get("header_row") is False


def test_table_column_phase_has_no_rows_method() -> None:
    phase = DearPyGuiC.TableOrdered()
    assert isinstance(phase, DearPyGuiTableColumnPhase)
    assert not hasattr(phase, "rows")
    row_phase = phase.columns()
    assert isinstance(row_phase, DearPyGuiTableRowPhase)


def test_table_row_phase_has_no_columns_method() -> None:
    phase = DearPyGuiC.TableOrdered().columns(DearPyGuiC.TableColumn(slot_id="c0"))
    assert not hasattr(phase, "columns")
