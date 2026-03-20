from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SettingsSnapshot:
    root_path: str = ""
    show_hidden: bool = False
    active_panel: str = "Output"


def load_settings() -> SettingsSnapshot:
    # Placeholder service contract for upcoming parity migration work.
    return SettingsSnapshot()


def save_settings(snapshot: SettingsSnapshot) -> None:
    # Placeholder service contract for upcoming parity migration work.
    del snapshot
