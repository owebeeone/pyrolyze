"""Native tkinter host for generated tkinter UI libraries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from pyrolyze.api import UIElement
from pyrolyze.backends.tkinter.engine import MountedWidgetNode, TkinterWidgetEngine
from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary
from pyrolyze.pyrolyze_tkinter import _create_tk_root


@dataclass(slots=True)
class NativeTkinterHost:
    root: Any
    engine: TkinterWidgetEngine
    root_node: MountedWidgetNode | None = None
    root_widget: Any | None = None
    _shown: bool = False

    def show(self) -> None:
        self.root.deiconify()
        self._shown = True

    def run(self) -> int:
        self.show()
        self.root.mainloop()
        return 0

    def close(self) -> None:
        if self.root is None:
            return
        try:
            self.root.destroy()
        except Exception:
            pass
        self.root_node = None
        self.root_widget = None
        self._shown = False


def create_host(title: str = "PyRolyze tkinter") -> NativeTkinterHost:
    import tkinter as tk

    root = _create_tk_root(tk)
    root.title(title)
    return NativeTkinterHost(
        root=root,
        engine=TkinterWidgetEngine(TkinterUiLibrary.WIDGET_SPECS),
    )


def reconcile_window_content(
    host: NativeTkinterHost,
    elements: Sequence[UIElement],
) -> MountedWidgetNode:
    if len(elements) != 1:
        raise ValueError(
            "pyrolyze_native_tkinter requires exactly one root UIElement; "
            f"received {len(elements)}"
        )
    (element,) = elements
    previous_widget = host.root_widget
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
    if previous_widget is not None and previous_widget is not host.root_widget:
        try:
            if previous_widget.winfo_manager() == "pack":
                previous_widget.pack_forget()
        except Exception:
            pass
    if host.root_widget is not None:
        if host.root_widget.winfo_manager() != "pack":
            host.root_widget.pack(fill="both", expand=True)
        else:
            host.root_widget.pack_configure(fill="both", expand=True)
    if host._shown:
        host.root.deiconify()
    return host.root_node


__all__ = ["NativeTkinterHost", "create_host", "reconcile_window_content"]
