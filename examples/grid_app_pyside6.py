#@pyrolyze
from PySide6.QtWidgets import QBoxLayout

from pyrolyze.api import keyed, pyrolyse, use_state
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt


def _decrement(value: int) -> int:
    return max(1, value - 1)


@pyrolyse
def value_stepper(
    title: str,
    value: int,
    *,
    decrement_name: str,
    value_name: str,
    increment_name: str,
    on_decrement,
    on_increment,
) -> None:
    with Qt.CQGroupBox(title):
        with Qt.CQHBoxLayout():
            Qt.CQPushButton("-", objectName=decrement_name, on_clicked=on_decrement)
            Qt.CQLabel(str(value), objectName=value_name)
            Qt.CQPushButton("+", objectName=increment_name, on_clicked=on_increment)


@pyrolyse
def header(
    cols: int,
    set_cols,
    rows: int,
    set_rows,
) -> None:
    with Qt.CQGroupBox("Dimensions", objectName="header:group"):
        with Qt.CQHBoxLayout():
            value_stepper(
                "Cols",
                cols,
                decrement_name="header:cols:decrement",
                value_name="header:cols:value",
                increment_name="header:cols:increment",
                on_decrement=lambda: set_cols(lambda current: _decrement(int(current))),
                on_increment=lambda: set_cols(lambda current: int(current) + 1),
            )
            value_stepper(
                "Rows",
                rows,
                decrement_name="header:rows:decrement",
                value_name="header:rows:value",
                increment_name="header:rows:increment",
                on_decrement=lambda: set_rows(lambda current: _decrement(int(current))),
                on_increment=lambda: set_rows(lambda current: int(current) + 1),
            )


@pyrolyse
def cell(row_index: int, col_index: int) -> None:
    count, set_count = use_state(0)
    with Qt.CQGroupBox(f"R{row_index + 1} C{col_index + 1}", objectName=f"cell:{row_index}:{col_index}:group"):
        with Qt.CQVBoxLayout():
            Qt.CQLabel(str(count), objectName=f"cell:{row_index}:{col_index}:value")
            Qt.CQPushButton(
                "Increment",
                objectName=f"cell:{row_index}:{col_index}:increment",
                on_clicked=lambda: set_count(lambda current: int(current) + 1),
            )


@pyrolyse
def grid(cols: int, rows: int) -> None:
    with Qt.CQGroupBox("Grid", objectName="grid:group"):
        with Qt.CQVBoxLayout():
            for row_index in keyed(range(rows), key=lambda value: value):
                with Qt.CQWidget(objectName=f"grid:row:{row_index}"):
                    with Qt.CQHBoxLayout():
                        for col_index in keyed(range(cols), key=lambda value: value):
                            cell(row_index, col_index)


@pyrolyse
def grid_app_pyside6() -> None:
    cols, set_cols = use_state(2)
    rows, set_rows = use_state(2)

    with Qt.CQMainWindow(windowTitle="Native Grid App"):
        with Qt.CQWidget(objectName="central_widget"):
            with Qt.CQBoxLayout(QBoxLayout.Direction.TopToBottom):
                header(cols, set_cols, rows, set_rows)
                grid(cols, rows)
