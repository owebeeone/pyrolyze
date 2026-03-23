#@pyrolyze
from pyrolyze.api import keyed, pyrolyze, use_state
from pyrolyze.backends.dearpygui.pyrolyze_library import DearPyGuiPyrolyzeUiLibrary as Dpg


def _coerce_count(raw_value: str) -> int:
    try:
        return max(0, int(raw_value))
    except ValueError:
        return 0


def _decrement(value: int) -> int:
    return max(0, value - 1)


@pyrolyze
def counter(
    title: str,
    count: int,
    set_count,
    *,
    decrement_label: str = "-",
    increment_label: str = "+",
) -> None:
    with Dpg.CDpgGroup(horizontal=True):
        Dpg.CDpgText(default_value=title, wrap=0)
        Dpg.CDpgButton(
            label=decrement_label,
            width=36,
            on_press=lambda: set_count(lambda current: _decrement(int(current))),
        )
        Dpg.CDpgInputText(
            label="",
            value=str(count),
            width=72,
            on_change=lambda next_value: set_count(_coerce_count(next_value)),
        )
        Dpg.CDpgButton(
            label=increment_label,
            width=36,
            on_press=lambda: set_count(lambda current: int(current) + 1),
        )


@pyrolyze
def header(
    cols: int,
    set_cols,
    rows: int,
    set_rows,
    use_grid: bool,
    set_use_grid,
) -> None:
    with Dpg.CDpgGroup(horizontal=False, label="Header"):
        with Dpg.CDpgGroup(horizontal=True):
            counter(
                "Cols",
                cols,
                set_cols,
                decrement_label="C-",
                increment_label="C+",
            )
            counter(
                "Rows",
                rows,
                set_rows,
                decrement_label="R-",
                increment_label="R+",
            )
            Dpg.CDpgButton(
                label="Use row layout" if use_grid else "Use column-major layout",
                width=220,
                on_press=lambda: set_use_grid(lambda current: not bool(current)),
            )


@pyrolyze
def cell(row_index: int, col_index: int) -> None:
    count, set_count = use_state(0)
    counter(
        f"R{row_index + 1} C{col_index + 1}",
        count,
        set_count,
    )


@pyrolyze
def grid(cols: int, rows: int, use_grid: bool) -> None:
    with Dpg.CDpgGroup(horizontal=False, label="Grid"):
        if use_grid:
            with Dpg.CDpgGroup(horizontal=True):
                for col_index in keyed(range(cols), key=lambda value: value):
                    with Dpg.CDpgGroup(horizontal=False):
                        for row_index in keyed(range(rows), key=lambda value: value):
                            cell(row_index, col_index)
        else:
            with Dpg.CDpgGroup(horizontal=False):
                for row_index in keyed(range(rows), key=lambda value: value):
                    with Dpg.CDpgGroup(horizontal=True):
                        for col_index in keyed(range(cols), key=lambda value: value):
                            cell(row_index, col_index)


@pyrolyze
def grid_app_dearpygui() -> None:
    cols, set_cols = use_state(2)
    rows, set_rows = use_state(2)
    use_grid, set_use_grid = use_state(False)

    with Dpg.CDpgWindow(label="Native DearPyGui Grid", width=960, height=640, no_resize=False):
        with Dpg.CDpgGroup(horizontal=False):
            header(cols, set_cols, rows, set_rows, use_grid, set_use_grid)
            grid(cols, rows, use_grid)
