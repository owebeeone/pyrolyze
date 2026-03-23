"""Native DearPyGui host for ``UIElement`` trees (``DearPyGuiUiLibrary`` specs)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from pyrolyze.api import UIElement
from pyrolyze.backends.dearpygui.engine import DpgMountableEngine
from pyrolyze.backends.dearpygui.generated_library import DearPyGuiUiLibrary
from pyrolyze.backends.dearpygui.live_host import LiveDpgHost
from pyrolyze.backends.mountable_engine import MountedMountableNode


@dataclass(slots=True)
class NativeDearPyGuiHost:
    """Holds a live DearPyGui context, staging host, and mountable engine."""

    dpg_host: LiveDpgHost
    engine: DpgMountableEngine
    root_node: MountedMountableNode | None = None

    def run(self) -> None:
        """Block with ``dearpygui.start_dearpygui()`` until the viewport exits."""

        import dearpygui.dearpygui as dpg

        dpg.start_dearpygui()

    def close(self) -> None:
        """Clear mount bookkeeping and destroy the DearPyGui context."""

        self.root_node = None
        self.dpg_host.stop()


def create_host(
    *,
    title: str = "PyRolyze",
    width: int = 800,
    height: int = 600,
    show_viewport: bool = True,
    vsync: bool = False,
) -> NativeDearPyGuiHost:
    """Create a started :class:`~pyrolyze.backends.dearpygui.live_host.LiveDpgHost` and engine."""

    dpg_host = LiveDpgHost(
        title=title,
        width=width,
        height=height,
        show_viewport=show_viewport,
        vsync=vsync,
    )
    dpg_host.start()
    engine = DpgMountableEngine(DearPyGuiUiLibrary.WIDGET_SPECS, dpg_host)
    return NativeDearPyGuiHost(dpg_host=dpg_host, engine=engine, root_node=None)


def reconcile_window_content(
    host: NativeDearPyGuiHost,
    elements: Sequence[UIElement],
) -> MountedMountableNode:
    """Mount or update the single root ``UIElement`` (same contract as Qt/Tk native hosts)."""

    if len(elements) != 1:
        msg = (
            "pyrolyze_native_dearpygui requires exactly one root UIElement; "
            f"received {len(elements)}"
        )
        raise ValueError(msg)
    (element,) = elements
    if host.root_node is None:
        host.root_node = host.engine.mount(
            element,
            slot_id=element.slot_id,
            call_site_id=element.call_site_id,
        )
    else:
        host.root_node = host.engine.update(
            host.root_node,
            element,
            slot_id=element.slot_id,
            call_site_id=element.call_site_id,
        )
    return host.root_node


__all__ = ["NativeDearPyGuiHost", "create_host", "reconcile_window_content"]
