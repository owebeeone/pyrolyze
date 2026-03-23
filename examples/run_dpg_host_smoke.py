"""Minimal DearPyGui smoke test via ``pyrolyze_native_dearpygui``.

Run: ``uv run --extra dpg python examples/run_dpg_host_smoke.py``
"""

from __future__ import annotations

import dearpygui.dearpygui as dpg

from pyrolyze.api import UIElement
from pyrolyze.pyrolyze_native_dearpygui import create_host, reconcile_window_content


def main() -> None:
    host = create_host(title="PyRolyze DPG smoke", width=320, height=240)
    try:
        reconcile_window_content(
            host,
            (
                UIElement(
                    kind="DpgWindow",
                    props={"label": "Hello"},
                    slot_id="win",
                    children=(UIElement(kind="DpgButton", props={"label": "OK"}, slot_id="btn"),),
                ),
            ),
        )
        dpg.start_dearpygui()
    finally:
        host.close()


if __name__ == "__main__":
    main()
