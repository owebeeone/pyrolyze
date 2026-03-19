#@pyrolyze
from typing import Callable

from pyrolyze.api import UIElement, call_native, keyed, pyrolyse, use_state


def _coerce_count(raw_value: str) -> int:
    try:
        return max(0, int(raw_value))
    except ValueError:
        return 0


@pyrolyse
def section(title: str, *, accent: str) -> None:
    call_native(UIElement)(
        kind="section",
        props={
            "title": title,
            "accent": accent,
            "visible": True,
        },
    )


@pyrolyse
def row(row_id: str, *, headline: str) -> None:
    call_native(UIElement)(
        kind="row",
        props={
            "row_id": row_id,
            "headline": headline,
            "visible": True,
        },
    )


@pyrolyse
def button(
    label: str,
    *,
    on_press: Callable[[], None],
    enabled: bool = True,
    tone: str = "default",
) -> None:
    call_native(UIElement)(
        kind="button",
        props={
            "label": label,
            "enabled": enabled,
            "tone": tone,
            "visible": True,
            "on_press": on_press,
        },
    )


@pyrolyse
def text_field(
    field_id: str,
    label: str,
    value: str,
    *,
    on_change: Callable[[str], None],
    enabled: bool = True,
) -> None:
    call_native(UIElement)(
        kind="text_field",
        props={
            "field_id": field_id,
            "label": label,
            "value": value,
            "enabled": enabled,
            "placeholder": None,
            "visible": True,
            "on_change": on_change,
        },
    )


@pyrolyse
def counter(
    label: str,
    field_id: str,
    count: int,
    set_count: Callable[[int | Callable[[int], int]], None],
) -> None:
    with section(label, accent="slate"):
        with row(f"{field_id}:controls", headline="Adjust"):
            button(
                "-",
                on_press=lambda: set_count(lambda current: max(0, int(current) - 1)),
                tone="danger",
            )
            text_field(
                f"{field_id}:value",
                "Count",
                str(count),
                on_change=lambda next_value: set_count(_coerce_count(next_value)),
            )
            button(
                "+",
                on_press=lambda: set_count(lambda current: int(current) + 1),
                tone="success",
            )


@pyrolyse
def header(
    cols: int,
    set_cols: Callable[[int | Callable[[int], int]], None],
    rows: int,
    set_rows: Callable[[int | Callable[[int], int]], None],
) -> None:
    with section("Header", accent="cyan"):
        with row("header:dimensions", headline="Dimensions"):
            counter("Cols", "header:cols", cols, set_cols)
            counter("Rows", "header:rows", rows, set_rows)


@pyrolyse
def grid_counter(row_index: int, col_index: int) -> None:
    count, set_count = use_state(0)
    counter(
        f"R{row_index + 1} C{col_index + 1}",
        f"cell:{row_index}:{col_index}",
        count,
        set_count,
    )


@pyrolyse
def dyna_grid(cols: int, rows: int) -> None:
    with section("Grid", accent="green"):
        for row_index in keyed(range(rows), key=lambda value: value):
            with row(f"grid:row:{row_index}", headline=f"Row {row_index + 1}"):
                for col_index in keyed(range(cols), key=lambda value: value):
                    grid_counter(row_index, col_index)


@pyrolyse
def grid_app() -> None:
    cols, set_cols = use_state(2)
    rows, set_rows = use_state(2)

    with section("Grid App", accent="blue"):
        header(cols, set_cols, rows, set_rows)
        dyna_grid(cols, rows)
