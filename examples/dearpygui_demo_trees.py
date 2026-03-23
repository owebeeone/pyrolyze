"""DearPyGui example ``UIElement`` trees (Phase 8).

Uses :class:`~pyrolyze.backends.dearpygui.generated_library.DearPyGuiUiLibrary`.**C**
author emitters (same role as PySide6 ``CQ*`` helpers). Runners use
:class:`~pyrolyze.backends.dearpygui.engine.DpgMountableEngine` /
:class:`~pyrolyze.pyrolyze_native_dearpygui.NativeDearPyGuiHost`.

Grid counters mirror ``examples/grid_app_pyside6.py``: each value is edited with
``[-] [input] [+]`` (see ``counter`` there).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from pyrolyze.api import UIElement
from pyrolyze.backends.dearpygui import DearPyGuiUiLibrary

C = DearPyGuiUiLibrary.C


@dataclass
class DpgGridAppState:
    """Mutable snapshot for the table-based grid demo."""

    cols: int = 2
    rows: int = 2
    counts: dict[tuple[int, int], int] = field(default_factory=dict)
    log_lines: list[str] = field(default_factory=list)
    name_field: str = ""
    verbose: bool = False


def _log_append(state: DpgGridAppState, line: str) -> None:
    state.log_lines.append(line)
    if len(state.log_lines) > 12:
        del state.log_lines[:-12]


def build_counter_row(
    *,
    box_title: str,
    field_id: str,
    display_value: int,
    on_minus: Callable[[], None],
    on_plus: Callable[[], None],
    on_value_change: Callable[[], None],
    prefix: str,
    input_width: int = 72,
) -> UIElement:
    """One titled counter: **[-] [input] [+]**, aligned with PySide6 ``counter()`` slot names."""

    base = f"{prefix}:{field_id}"
    return C.Group(
        slot_id=f"{base}:group",
        children=(
            C.Text(default_value=box_title, slot_id=f"{base}:title"),
            C.Group(
                horizontal=True,
                children=(
                    C.Button(
                        label="-",
                        on_press=on_minus,
                        slot_id=f"{base}:decrement",
                    ),
                    C.InputText(
                        label="",
                        value=str(display_value),
                        on_change=on_value_change,
                        width=input_width,
                        slot_id=f"{base}:value",
                    ),
                    C.Button(
                        label="+",
                        on_press=on_plus,
                        slot_id=f"{base}:increment",
                    ),
                ),
            ),
        ),
    )


def build_window_menu_bar(*, on_quit: Callable[[], None], prefix: str = "demo") -> UIElement:
    """Window with **File → Quit** (menu uses DearPyGui ``callback``)."""

    return C.Window(
        label="Menu sample",
        slot_id=f"{prefix}:win",
        children=(
            C.MenuBar(
                slot_id=f"{prefix}:mb",
                children=(
                    C.Menu(
                        label="File",
                        slot_id=f"{prefix}:m_file",
                        children=(
                            C.MenuItem(
                                label="Quit",
                                callback=on_quit,
                                slot_id=f"{prefix}:mi_quit",
                            ),
                        ),
                    ),
                ),
            ),
            C.Text(
                default_value="Use File → Quit to close.",
                slot_id=f"{prefix}:hint",
            ),
        ),
    )


def build_value_events_children(
    state: DpgGridAppState,
    *,
    on_name_change: Callable[[], None],
    on_toggle: Callable[[], None],
    prefix: str = "ve",
) -> tuple[UIElement, ...]:
    """Input text, checkbox, drag/drop button, and log text (flat siblings under a window)."""

    log_text = "\n".join(state.log_lines) if state.log_lines else "(drag/drop events when Verbose is on)"

    def _drag(*args: object) -> None:
        if state.verbose:
            _log_append(state, f"drag {args!r}")

    def _drop(*args: object) -> None:
        if state.verbose:
            _log_append(state, f"drop {args!r}")

    return (
        C.Text(
            default_value="— Values & events —",
            wrap=480,
            slot_id=f"{prefix}:hdr",
        ),
        C.InputText(
            label="Name",
            value=state.name_field,
            on_change=on_name_change,
            slot_id=f"{prefix}:name",
        ),
        C.Checkbox(
            label="Verbose drag/drop log",
            value=state.verbose,
            on_change=on_toggle,
            slot_id=f"{prefix}:chk",
        ),
        C.Button(
            label="Drag / drop here (payload test)",
            on_drag=_drag,
            on_drop=_drop,
            slot_id=f"{prefix}:dd",
        ),
        C.Text(
            default_value=log_text,
            wrap=480,
            slot_id=f"{prefix}:log",
        ),
    )


def build_table_counter_grid(
    state: DpgGridAppState,
    *,
    on_quit: Callable[[], None],
    on_cols_delta: Callable[[int], None],
    on_rows_delta: Callable[[int], None],
    on_cell_delta: Callable[[int, int, int], None],
    on_counter_value_edited: Callable[[], None],
    include_value_panel: bool = True,
    value_handlers: tuple[Callable[[], None], Callable[[], None]] | None = None,
    prefix: str = "grid",
) -> UIElement:
    """Menu + dimension counters + **table** cell counters + optional value/event widgets."""

    cols = tuple(C.TableColumn(slot_id=f"{prefix}:tc:{j}") for j in range(state.cols))
    rows: list[UIElement] = []
    for r in range(state.rows):
        cells: list[UIElement] = []
        for c in range(state.cols):
            count = state.counts.get((r, c), 0)
            cells.append(
                C.Group(
                    slot_id=f"{prefix}:cell:{r}:{c}:group",
                    children=(
                        C.Text(
                            default_value=f"R{r + 1} C{c + 1}",
                            slot_id=f"{prefix}:cell:{r}:{c}:title",
                        ),
                        C.Group(
                            horizontal=True,
                            children=(
                                C.Button(
                                    label="-",
                                    on_press=(lambda ri=r, ci=c: on_cell_delta(ri, ci, -1)),
                                    slot_id=f"{prefix}:cell:{r}:{c}:decrement",
                                ),
                                C.InputText(
                                    label="",
                                    value=str(count),
                                    on_change=on_counter_value_edited,
                                    width=64,
                                    slot_id=f"{prefix}:cell:{r}:{c}:value",
                                ),
                                C.Button(
                                    label="+",
                                    on_press=(lambda ri=r, ci=c: on_cell_delta(ri, ci, 1)),
                                    slot_id=f"{prefix}:cell:{r}:{c}:increment",
                                ),
                            ),
                        ),
                    ),
                )
            )
        rows.append(
            C.TableRow(
                slot_id=f"{prefix}:tr:{r}",
                children=tuple(cells),
            )
        )

    table = C.Table(
        slot_id=f"{prefix}:table",
        children=cols + tuple(rows),
    )

    header_row = C.Group(
        horizontal=True,
        slot_id=f"{prefix}:header:dims",
        children=(
            build_counter_row(
                box_title="Cols",
                field_id="header:cols",
                display_value=state.cols,
                on_minus=lambda: on_cols_delta(-1),
                on_plus=lambda: on_cols_delta(1),
                on_value_change=on_counter_value_edited,
                prefix=prefix,
            ),
            build_counter_row(
                box_title="Rows",
                field_id="header:rows",
                display_value=state.rows,
                on_minus=lambda: on_rows_delta(-1),
                on_plus=lambda: on_rows_delta(1),
                on_value_change=on_counter_value_edited,
                prefix=prefix,
            ),
        ),
    )

    header_bits: list[UIElement] = [
        C.Text(
            default_value="DearPyGui grid — edit counts or use − / + (like the PySide6 example).",
            slot_id=f"{prefix}:title",
        ),
        header_row,
    ]

    menu = C.MenuBar(
        slot_id=f"{prefix}:mb",
        children=(
            C.Menu(
                label="File",
                slot_id=f"{prefix}:menu_file",
                children=(
                    C.MenuItem(
                        label="Quit",
                        callback=on_quit,
                        slot_id=f"{prefix}:quit",
                    ),
                ),
            ),
        ),
    )

    body: list[UIElement] = [menu, *header_bits, table]
    if include_value_panel and value_handlers is not None:
        h1, h2 = value_handlers
        body.extend(build_value_events_children(state, on_name_change=h1, on_toggle=h2, prefix=f"{prefix}:ve"))

    return C.Window(
        label="PyRolyze DearPyGui grid",
        width=520,
        height=620,
        slot_id=f"{prefix}:root",
        children=tuple(body),
    )


__all__ = [
    "DpgGridAppState",
    "build_counter_row",
    "build_table_counter_grid",
    "build_value_events_children",
    "build_window_menu_bar",
]
