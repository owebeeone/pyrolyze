#@pyrolyze
from PySide6.QtWidgets import QBoxLayout

from pyrolyze.api import keyed, mount, pyrolyze, use_state
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
    with Qt.CQGroupBox(title, objectName=f"{field_id}:group"):
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
    use_grid: bool,
    set_use_grid,
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
            with Qt.CQGroupBox("Layout", objectName="header:layout:group"):
                with Qt.CQHBoxLayout():
                    Qt.CQPushButton(
                        "Use Row Layout" if use_grid else "Use Qt Grid",
                        objectName="header:layout:toggle",
                        on_clicked=lambda: set_use_grid(lambda current: not bool(current)),
                    )


@pyrolyze
def app_menu_bar(set_use_grid) -> None:
    with Qt.CQMenuBar(objectName="app:menu_bar", nativeMenuBar=False):
        with mount(Qt.mounts.action):
            with Qt.CQAction("File", objectName="menu:file:action"):
                with Qt.CQMenu("File", objectName="menu:file:menu"):
                    with mount(Qt.mounts.action):
                        Qt.CQAction("New Grid", objectName="menu:file:new:action")
                        Qt.CQAction("Reset Counts", objectName="menu:file:reset:action")
                        Qt.CQAction("Randomize", objectName="menu:file:randomize:action")
                        Qt.CQAction("Expand", objectName="menu:file:expand:action")
                        Qt.CQAction("Collapse", objectName="menu:file:collapse:action")
                        with Qt.CQAction("Advanced", objectName="menu:file:advanced:action"):
                            with Qt.CQMenu("Advanced", objectName="menu:file:advanced:menu"):
                                with mount(Qt.mounts.action):
                                    Qt.CQAction(
                                        "Toggle Grid Mode",
                                        objectName="menu:file:advanced:toggle_layout:action",
                                        on_triggered=lambda: set_use_grid(lambda current: not bool(current)),
                                    )
                                    Qt.CQAction(
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
    with Qt.CQGroupBox("Grid", objectName="grid:group"):
        with Qt.CQVBoxLayout(objectName="grid:outer:layout"):
            if use_grid:
                with Qt.CQWidget(objectName="grid:matrix:widget"):
                    with Qt.CQGridLayout(objectName="grid:matrix:layout"):
                        for row_index in keyed(range(rows), key=lambda value: value):
                            for col_index in keyed(range(cols), key=lambda value: value):
                                with mount(
                                    Qt.mounts.widget(
                                        row=row_index,
                                        column=col_index,
                                        rowSpan=1,
                                        columnSpan=1,
                                    )
                                ):
                                    cell(row_index, col_index)
            else:
                with Qt.CQWidget(objectName="grid:rows:widget"):
                    with Qt.CQVBoxLayout(objectName="grid:rows:layout"):
                        for row_index in keyed(range(rows), key=lambda value: value):
                            with Qt.CQWidget(objectName=f"grid:row:{row_index}"):
                                with Qt.CQHBoxLayout():
                                    for col_index in keyed(range(cols), key=lambda value: value):
                                        cell(row_index, col_index)


@pyrolyze
def grid_app_pyside6() -> None:
    cols, set_cols = use_state(2)
    rows, set_rows = use_state(2)
    use_grid, set_use_grid = use_state(False)

    with Qt.CQMainWindow(
        windowTitle="Native Grid App",
        minimumWidth=960,
        minimumHeight=640,
    ):
        app_menu_bar(set_use_grid)
        with Qt.CQWidget(objectName="central_widget"):
            with Qt.CQBoxLayout(QBoxLayout.Direction.TopToBottom):
                header(cols, set_cols, rows, set_rows, use_grid, set_use_grid)
                with Qt.CQScrollArea(objectName="grid:scroll", widgetResizable=True):
                    with Qt.CQWidget(objectName="grid:content"):
                        with Qt.CQVBoxLayout():
                            grid(cols, rows, use_grid)
