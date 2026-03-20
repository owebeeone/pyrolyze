from __future__ import annotations

from dataclasses import replace

from Studio.app.models import PANEL_OPTIONS, StudioState
from Studio.services.filesystem_service import normalize_root_path


def create_initial_state(start_root: str = "") -> StudioState:
    normalized = normalize_root_path(start_root)
    return StudioState(root_path=normalized)


def set_root_path(state: StudioState, raw_path: str) -> StudioState:
    normalized = normalize_root_path(raw_path)
    return replace(
        state,
        root_path=normalized,
        selected_path="",
        status_message=f"Root set to {normalized}",
    )


def select_entry(state: StudioState, path: str, *, is_dir: bool) -> StudioState:
    if is_dir:
        return set_root_path(state, path)
    return replace(
        state,
        selected_path=path,
        status_message=f"Selected file: {path}",
    )


def set_show_hidden(state: StudioState, show_hidden: bool) -> StudioState:
    checked = bool(show_hidden)
    return replace(
        state,
        show_hidden=checked,
        status_message="Showing hidden files" if checked else "Hidden files filtered",
    )


def set_active_panel(state: StudioState, panel: str) -> StudioState:
    next_panel = panel if panel in PANEL_OPTIONS else PANEL_OPTIONS[0]
    return replace(
        state,
        active_panel=next_panel,
        status_message=f"Panel switched to {next_panel}",
    )


def bump_refresh_tick(state: StudioState) -> StudioState:
    return replace(
        state,
        refresh_tick=int(state.refresh_tick) + 1,
        status_message="Refreshed",
    )


def set_status_message(state: StudioState, message: str) -> StudioState:
    return replace(state, status_message=str(message))
