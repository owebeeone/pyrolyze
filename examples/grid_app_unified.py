"""Reactive grid demo like ``grid_app_pyside6``, entirely wired through ``pyrolyze.unified.qt``.

- **Structural** native containers use the compile-time class :data:`QtUx`
  (``with QtUx.CQMainWindow():``, ``mount(QtUx.mounts.widget(...))``, …). Those
  attributes are the same generated ``PySide6UiLibrary`` component refs
  re-exported on :class:`QtUnifiedNativeLibrary` for ergonomics.
- **Portable emitters** use an instance — :meth:`QtUnifiedNativeLibrary.push_button`,
  :meth:`~QtUnifiedNativeLibrary.text_field`, :meth:`~QtUnifiedNativeLibrary.static_text`
  — plus ``call_native(UIElement)``.

Only external Qt import: ``QBoxLayout.Direction`` for ``CQBoxLayout``.

Run via ``examples/run_grid_app_unified.py`` (compiler-transformed); do not
execute this module directly.
"""

from __future__ import annotations

from PySide6.QtWidgets import QBoxLayout

from pyrolyze.api import UIElement, call_native, keyed, mount, pyrolyze, use_state
from pyrolyze.unified.qt import QtUnifiedNativeLibrary, QtUx

_lib = QtUnifiedNativeLibrary()


def _coerce_count(raw_value: str) -> int:
    try:
        return max(0, int(raw_value))
    except ValueError:
        return 0


def _decrement(value: int) -> int:
    return max(0, value - 1)


# One ``call_native`` per ``@pyrolyze`` child so each native layout pass sees a
# single structural child (same rule as ``unified_hello_pyside6``).


@pyrolyze
def unified_counter_dec(field_id: str, set_count) -> None:
    el = _lib.push_button(
        text="-",
        objectName=f"{field_id}:decrement",
        on_clicked=lambda: set_count(lambda current: _decrement(int(current))),
    )
    call_native(UIElement)(kind=el.kind, props=dict(el.props))


@pyrolyze
def unified_counter_field(field_id: str, count: int, set_count) -> None:
    el = _lib.text_field(
        text=str(count),
        objectName=f"{field_id}:value",
        on_textChanged=lambda next_value: set_count(_coerce_count(next_value)),
    )
    call_native(UIElement)(kind=el.kind, props=dict(el.props))


@pyrolyze
def unified_counter_inc(field_id: str, set_count) -> None:
    el = _lib.push_button(
        text="+",
        objectName=f"{field_id}:increment",
        on_clicked=lambda: set_count(lambda current: int(current) + 1),
    )
    call_native(UIElement)(kind=el.kind, props=dict(el.props))


@pyrolyze
def counter(
    title: str,
    field_id: str,
    count: int,
    set_count,
) -> None:
    with QtUx.CQGroupBox(title, objectName=f"{field_id}:group"):
        with QtUx.CQHBoxLayout():
            unified_counter_dec(field_id, set_count)
            unified_counter_field(field_id, count, set_count)
            unified_counter_inc(field_id, set_count)


@pyrolyze
def unified_header_layout_toggle(use_grid: bool, set_use_grid) -> None:
    el = _lib.push_button(
        text="Use Row Layout" if use_grid else "Use Qt Grid",
        objectName="header:layout:toggle",
        on_clicked=lambda: set_use_grid(lambda current: not bool(current)),
    )
    call_native(UIElement)(kind=el.kind, props=dict(el.props))


@pyrolyze
def header(
    cols: int,
    set_cols,
    rows: int,
    set_rows,
    use_grid: bool,
    set_use_grid,
) -> None:
    with QtUx.CQGroupBox("Dimensions", objectName="header:group"):
        with QtUx.CQHBoxLayout():
            counter(
                "Cols",
                "header:cols",
                cols,
                set_cols,
            )
            counter(
                "Rows",
                "header:rows",
                rows,
                set_rows,
            )
            with QtUx.CQGroupBox("Layout", objectName="header:layout:group"):
                with QtUx.CQHBoxLayout():
                    unified_header_layout_toggle(use_grid, set_use_grid)


@pyrolyze
def app_menu_bar(set_use_grid) -> None:
    with QtUx.CQMenuBar(objectName="app:menu_bar", nativeMenuBar=False):
        with mount(QtUx.mounts.action):
            with QtUx.CQAction("File", objectName="menu:file:action"):
                with QtUx.CQMenu("File", objectName="menu:file:menu"):
                    with mount(QtUx.mounts.action):
                        QtUx.CQAction("New Grid", objectName="menu:file:new:action")
                        QtUx.CQAction("Reset Counts", objectName="menu:file:reset:action")
                        QtUx.CQAction("Randomize", objectName="menu:file:randomize:action")
                        QtUx.CQAction("Expand", objectName="menu:file:expand:action")
                        QtUx.CQAction("Collapse", objectName="menu:file:collapse:action")
                        with QtUx.CQAction("Advanced", objectName="menu:file:advanced:action"):
                            with QtUx.CQMenu("Advanced", objectName="menu:file:advanced:menu"):
                                with mount(QtUx.mounts.action):
                                    QtUx.CQAction(
                                        "Toggle Grid Mode",
                                        objectName="menu:file:advanced:toggle_layout:action",
                                        on_triggered=lambda: set_use_grid(
                                            lambda current: not bool(current)
                                        ),
                                    )
                                    QtUx.CQAction(
                                        "Snapshot",
                                        objectName="menu:file:advanced:snapshot:action",
                                    )


@pyrolyze
def cell(row_index: int, col_index: int) -> None:
    count, set_count = use_state(0)
    counter(
        f"R{row_index + 1} C{col_index + 1}",
        f"cell:{row_index}:{col_index}",
        count,
        set_count,
    )


@pyrolyze
def grid(cols: int, rows: int, use_grid: bool) -> None:
    with QtUx.CQGroupBox("Grid", objectName="grid:group"):
        with QtUx.CQVBoxLayout(objectName="grid:outer:layout"):
            if use_grid:
                with QtUx.CQWidget(objectName="grid:matrix:widget"):
                    with QtUx.CQGridLayout(objectName="grid:matrix:layout"):
                        for row_index in keyed(range(rows), key=lambda value: value):
                            for col_index in keyed(range(cols), key=lambda value: value):
                                with mount(
                                    QtUx.mounts.widget(
                                        row=row_index,
                                        column=col_index,
                                        rowSpan=1,
                                        columnSpan=1,
                                    )
                                ):
                                    cell(row_index, col_index)
            else:
                with QtUx.CQWidget(objectName="grid:rows:widget"):
                    with QtUx.CQVBoxLayout(objectName="grid:rows:layout"):
                        for row_index in keyed(range(rows), key=lambda value: value):
                            with QtUx.CQWidget(objectName=f"grid:row:{row_index}"):
                                with QtUx.CQHBoxLayout():
                                    for col_index in keyed(range(cols), key=lambda value: value):
                                        cell(row_index, col_index)


@pyrolyze
def unified_caption(text: str, objectName: str, styleSheet: str) -> None:
    el = _lib.static_text(text=text, objectName=objectName, styleSheet=styleSheet)
    call_native(UIElement)(kind=el.kind, props=dict(el.props))


@pyrolyze
def grid_app_unified() -> None:
    cols, set_cols = use_state(2)
    rows, set_rows = use_state(2)
    use_grid, set_use_grid = use_state(False)

    with QtUx.CQMainWindow(
        windowTitle="Grip PyRolyze Grid (unified controls)",
        minimumWidth=960,
        minimumHeight=640,
    ):
        app_menu_bar(set_use_grid)
        with QtUx.CQWidget(objectName="central_widget"):
            with QtUx.CQBoxLayout(QBoxLayout.Direction.TopToBottom):
                with QtUx.CQHBoxLayout(objectName="app:header:row"):
                    unified_caption(
                        "PyRolyze — reactive grid (unified API)",
                        "app:title",
                        "font-weight: bold; font-size: 16px;",
                    )
                    unified_caption(
                        "PySide6 · QtUx (structural) + _lib.push_button / text_field / static_text",
                        "app:subtitle",
                        "color: #555;",
                    )
                header(cols, set_cols, rows, set_rows, use_grid, set_use_grid)
                with QtUx.CQScrollArea(objectName="grid:scroll", widgetResizable=True):
                    with QtUx.CQWidget(objectName="grid:content"):
                        with QtUx.CQVBoxLayout():
                            grid(cols, rows, use_grid)


if __name__ == "__main__":
    raise SystemExit(
        "Run examples/run_grid_app_unified.py instead "
        "(this module must be compiler-transformed)."
    )
