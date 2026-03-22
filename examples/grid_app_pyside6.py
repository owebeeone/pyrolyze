#@pyrolyze
from PySide6.QtWidgets import QBoxLayout

from pyrolyze.api import keyed, pyrolyze, use_state
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt


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
    field_id: str,
    count: int,
    set_count,
) -> None:
    with Qt.CQGroupBox(title):
        with Qt.CQHBoxLayout():
            Qt.CQPushButton(
                "-",
                objectName=f"{field_id}:decrement",
                on_clicked=lambda: set_count(lambda current: _decrement(int(current))),
            )
            Qt.CQLineEdit(
                str(count),
                objectName=f"{field_id}:value",
                on_textChanged=lambda next_value: set_count(_coerce_count(next_value)),
            )
            Qt.CQPushButton(
                "+",
                objectName=f"{field_id}:increment",
                on_clicked=lambda: set_count(lambda current: int(current) + 1),
            )


@pyrolyze
def header(
    cols: int,
    set_cols,
    rows: int,
    set_rows,
) -> None:
    with Qt.CQGroupBox("Dimensions", objectName="header:group"):
        with Qt.CQHBoxLayout():
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
def grid(cols: int, rows: int) -> None:
    with Qt.CQGroupBox("Grid", objectName="grid:group"):
        with Qt.CQVBoxLayout():
            for row_index in keyed(range(rows), key=lambda value: value):
                with Qt.CQWidget(objectName=f"grid:row:{row_index}"):
                    with Qt.CQHBoxLayout():
                        for col_index in keyed(range(cols), key=lambda value: value):
                            cell(row_index, col_index)


@pyrolyze
def grid_app_pyside6() -> None:
    cols, set_cols = use_state(2)
    rows, set_rows = use_state(2)

    with Qt.CQMainWindow(windowTitle="Native Grid App"):
        with Qt.CQWidget(objectName="central_widget"):
            with Qt.CQBoxLayout(QBoxLayout.Direction.TopToBottom):
                header(cols, set_cols, rows, set_rows)
                with Qt.CQScrollArea(objectName="grid:scroll", widgetResizable=True):
                    with Qt.CQWidget(objectName="grid:content"):
                        with Qt.CQVBoxLayout():
                            grid(cols, rows)
