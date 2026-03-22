"""Native PySide6 host for generated PySide6 UI libraries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from PySide6.QtWidgets import QApplication, QWidget

from pyrolyze.api import UIElement
from pyrolyze.backends.pyside6.engine import MountedWidgetNode, PySide6WidgetEngine
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary


@dataclass(slots=True)
class NativePySide6Host:
    app: QApplication
    engine: PySide6WidgetEngine
    root_node: MountedWidgetNode | None = None
    root_widget: QWidget | None = None
    _shown: bool = False

    def show(self) -> None:
        widget = self.root_widget
        if widget is None:
            raise RuntimeError("native PySide6 host has no mounted root widget")
        self._shown = True
        widget.show()

    def exec(self) -> int:
        self.show()
        return self.app.exec()

    def close(self) -> None:
        widget = self.root_widget
        if widget is not None:
            widget.close()
        self.root_node = None
        self.root_widget = None
        self._shown = False


def create_host() -> NativePySide6Host:
    app = QApplication.instance() or QApplication([])
    return NativePySide6Host(
        app=app,
        engine=PySide6WidgetEngine(PySide6UiLibrary.WIDGET_SPECS),
    )


def reconcile_window_content(
    host: NativePySide6Host,
    elements: Sequence[UIElement],
) -> MountedWidgetNode:
    if len(elements) != 1:
        raise ValueError(
            "pyrolyze_native_pyside6 requires exactly one root UIElement; "
            f"received {len(elements)}"
        )
    (element,) = elements
    if host.root_node is None:
        host.root_node = host.engine.mount(
            element,
            slot_id=element.slot_id,
            call_site_id=element.call_site_id,
        )
    else:
        host.engine.update(
            host.root_node,
            element,
            slot_id=element.slot_id,
            call_site_id=element.call_site_id,
        )
    host.root_widget = host.root_node.widget
    if host._shown and host.root_widget is not None:
        host.root_widget.show()
    return host.root_node


__all__ = ["NativePySide6Host", "create_host", "reconcile_window_content"]
