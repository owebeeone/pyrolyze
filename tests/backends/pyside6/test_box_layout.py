from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from frozendict import frozendict

pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QBoxLayout, QLayoutItem

from pyrolyze.backends.model import MountState
from pyrolyze.backends.mounts import MountedRef
from pyrolyze.backends.pyside6.box_layout import reconcile_box_layout_children
from pyrolyze.backends.pyside6.engine import PySide6WidgetEngine
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary


class _CountingBoxLayout(QBoxLayout):
    def __init__(self) -> None:
        super().__init__(QBoxLayout.Direction.TopToBottom)
        self.reads = 0
        self.removals = 0

    def itemAt(self, index: int) -> QLayoutItem:
        self.reads += 1
        return super().itemAt(index)

    def takeAt(self, index: int) -> QLayoutItem:
        self.removals += 1
        return super().takeAt(index)


@pytest.mark.parametrize("size", (10, 100, 1000))
def test_box_layout_reorder_uses_one_linear_item_scan(size: int) -> None:
    app = QApplication.instance() or QApplication([])
    engine = PySide6WidgetEngine(PySide6UiLibrary.WIDGET_SPECS)._engine
    children = [
        engine.mount(PySide6UiLibrary.UI_INTERFACE.build_element("CQLabel", text=str(index)))
        for index in range(size)
    ]
    layout = _CountingBoxLayout()
    for child in reversed(children):
        layout.addWidget(child.mountable)
    state = MountState(
        PySide6UiLibrary.WIDGET_SPECS["QBoxLayout"].mount_points["widget"],
        ("widget",),
        frozendict(),
        tuple(MountedRef(index, child.mountable) for index, child in enumerate(children)),
    )
    reconcile_box_layout_children(layout, children, {state.instance_key: state})
    assert layout.reads == size
    assert layout.removals == size
    assert all(layout.itemAt(index).widget() is child.mountable for index, child in enumerate(children))
    assert app is not None


def test_box_layout_shared_reorder_preserves_mount_parameters_and_removes_children() -> None:
    app = QApplication.instance() or QApplication([])
    engine = PySide6WidgetEngine(PySide6UiLibrary.WIDGET_SPECS)._engine
    a = engine.mount(PySide6UiLibrary.UI_INTERFACE.build_element("CQLabel", text="A"))
    row = engine.mount(PySide6UiLibrary.UI_INTERFACE.build_element("CQHBoxLayout"))
    b = engine.mount(PySide6UiLibrary.UI_INTERFACE.build_element("CQLabel", text="B"))
    layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
    specs = PySide6UiLibrary.WIDGET_SPECS["QBoxLayout"].mount_points
    widgets = MountState(specs["widget"], ("widget",), frozendict(stretch=3, alignment=Qt.AlignRight),
                         (MountedRef("a", a.mountable), MountedRef("b", b.mountable)))
    layouts = MountState(specs["layout"], ("layout",), frozendict(stretch=5),
                         (MountedRef("row", row.mountable),))
    states = {widgets.instance_key: widgets, layouts.instance_key: layouts}
    reconcile_box_layout_children(layout, [a, row, b], states)
    reconcile_box_layout_children(layout, [b, row, a], states)
    assert tuple(layout.stretch(index) for index in range(3)) == (3, 5, 3)
    assert layout.itemAt(0).alignment() == Qt.AlignRight
    assert layout.itemAt(1).layout() is row.mountable
    assert layout.itemAt(2).alignment() == Qt.AlignRight
    reconcile_box_layout_children(layout, [], {})
    assert layout.count() == 0
    assert app is not None
