#@pyrolyze
from tkinter import StringVar

from pyrolyze.api import keyed, mount, pyrolyze, use_state
from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary as Tk


def _coerce_count(raw_value: str) -> int:
    try:
        return max(0, int(raw_value))
    except ValueError:
        return 0


def _decrement(value: int) -> int:
    return max(0, value - 1)


def _request_decrement(set_count) -> None:
    set_count(lambda current: _decrement(int(current)))


def _request_increment(set_count) -> None:
    set_count(lambda current: int(current) + 1)


def _request_count_update(event, set_count) -> None:
    set_count(_coerce_count(event.widget.get()))


def _toggle_layout(set_use_grid) -> None:
    set_use_grid(lambda current: not bool(current))


@pyrolyze
def counter(
    title: str,
    count: int,
    set_count,
    *,
    decrement_text: str = "-",
    increment_text: str = "+",
) -> None:
    with Tk.CTtkFrame():
        with mount(Tk.mounts.pack(side="left", padx=4, pady=4)):
            Tk.CTtkLabel(text=title)
            Tk.CTtkButton(
                text=decrement_text,
                on_command=lambda: _request_decrement(set_count),
            )
            Tk.CTtkEntry(
                textvariable=StringVar(value=str(count)),
                width=5,
                on_key_release=lambda event: _request_count_update(event, set_count),
            )
            Tk.CTtkButton(
                text=increment_text,
                on_command=lambda: _request_increment(set_count),
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
    with Tk.CTtkFrame():
        with mount(Tk.mounts.pack(side="left", padx=6, pady=6)):
            Tk.CTtkLabel(text="Grid App")
            counter(
                "Cols",
                cols,
                set_cols,
                decrement_text="Cols -",
                increment_text="Cols +",
            )
            counter(
                "Rows",
                rows,
                set_rows,
                decrement_text="Rows -",
                increment_text="Rows +",
            )
            Tk.CTtkButton(
                text="Use Row Layout" if use_grid else "Use Grid Layout",
                on_command=lambda: _toggle_layout(set_use_grid),
            )


@pyrolyze
def cell(row_index: int, col_index: int) -> None:
    count, set_count = use_state(0)
    with Tk.CTtkFrame():
        with mount(Tk.mounts.pack(side="left", padx=3, pady=3)):
            Tk.CTtkLabel(text=f"R{row_index + 1} C{col_index + 1}")
            Tk.CTtkButton(
                text="-",
                on_command=lambda: _request_decrement(set_count),
            )
            Tk.CTtkLabel(text=str(count))
            Tk.CTtkButton(
                text="+",
                on_command=lambda: _request_increment(set_count),
            )


@pyrolyze
def grid(cols: int, rows: int, use_grid: bool) -> None:
    with Tk.CTtkFrame():
        if use_grid:
            for row_index in keyed(range(rows), key=lambda value: value):
                for col_index in keyed(range(cols), key=lambda value: value):
                    with mount(Tk.mounts.grid(row=row_index, column=col_index, padx=6, pady=6)):
                        cell(row_index, col_index)
        else:
            for row_index in keyed(range(rows), key=lambda value: value):
                with Tk.CTtkFrame():
                    with mount(Tk.mounts.pack(side="left", padx=6, pady=6)):
                        for col_index in keyed(range(cols), key=lambda value: value):
                            cell(row_index, col_index)


@pyrolyze
def grid_app_tkinter() -> None:
    cols, set_cols = use_state(2)
    rows, set_rows = use_state(2)
    use_grid, set_use_grid = use_state(False)

    with Tk.CTtkFrame():
        with mount(Tk.mounts.pack(fill="x", padx=8, pady=8)):
            header(cols, set_cols, rows, set_rows, use_grid, set_use_grid)
        with mount(Tk.mounts.pack(fill="both", expand=True, padx=8, pady=8)):
            grid(cols, rows, use_grid)
