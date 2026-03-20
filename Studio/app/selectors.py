from __future__ import annotations

from Studio.app.models import PANEL_OPTIONS, StudioState
from Studio.services.snapshot_service import build_snapshot_text


def panel_options() -> tuple[str, ...]:
    return PANEL_OPTIONS


def snapshot_text(state: StudioState, *, entry_count: int) -> str:
    return build_snapshot_text(
        root_path=state.root_path,
        entry_count=entry_count,
        selected_path=state.selected_path,
        active_panel=state.active_panel,
        refresh_tick=state.refresh_tick,
    )
