from __future__ import annotations


def build_snapshot_text(
    *,
    root_path: str,
    entry_count: int,
    selected_path: str,
    active_panel: str,
    refresh_tick: int,
) -> str:
    selected = selected_path or "<none>"
    return (
        "studio_snapshot\n"
        f"root={root_path}\n"
        f"entries={entry_count}\n"
        f"selected={selected}\n"
        f"active_panel={active_panel}\n"
        f"refresh_tick={refresh_tick}"
    )
