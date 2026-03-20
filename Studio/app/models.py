from __future__ import annotations

from dataclasses import dataclass


PANEL_OPTIONS: tuple[str, ...] = ("Output", "Terminal", "Problems")


@dataclass(frozen=True, slots=True)
class StudioState:
    root_path: str
    show_hidden: bool = False
    selected_path: str = ""
    active_panel: str = "Output"
    refresh_tick: int = 0
    status_message: str = "Ready"
