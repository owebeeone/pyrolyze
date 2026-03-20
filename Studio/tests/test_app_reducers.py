from __future__ import annotations

from pathlib import Path

from Studio.app.reducers import (
    bump_refresh_tick,
    create_initial_state,
    select_entry,
    set_active_panel,
    set_root_path,
)


def test_create_initial_state_normalizes_blank_root() -> None:
    state = create_initial_state("   ")
    assert state.root_path == str(Path.cwd())
    assert state.active_panel == "Output"
    assert state.refresh_tick == 0


def test_select_entry_directory_updates_root_and_clears_selection(tmp_path: Path) -> None:
    child_dir = tmp_path / "child"
    child_dir.mkdir()
    selected_file = tmp_path / "x.txt"
    selected_file.write_text("x", encoding="utf-8")
    state = create_initial_state(str(tmp_path))
    state = select_entry(state, str(selected_file), is_dir=False)

    next_state = select_entry(state, str(child_dir), is_dir=True)

    assert next_state.root_path == str(child_dir)
    assert next_state.selected_path == ""


def test_select_entry_file_updates_selected_path(tmp_path: Path) -> None:
    target = tmp_path / "example.txt"
    target.write_text("hello", encoding="utf-8")
    state = create_initial_state(str(tmp_path))

    next_state = select_entry(state, str(target), is_dir=False)

    assert next_state.selected_path == str(target)
    assert next_state.root_path == str(tmp_path)


def test_set_active_panel_unknown_value_falls_back_to_output(tmp_path: Path) -> None:
    state = create_initial_state(str(tmp_path))

    next_state = set_active_panel(state, "nonexistent")

    assert next_state.active_panel == "Output"


def test_bump_refresh_tick_increments_by_one(tmp_path: Path) -> None:
    state = create_initial_state(str(tmp_path))

    next_state = bump_refresh_tick(state)

    assert next_state.refresh_tick == state.refresh_tick + 1


def test_set_root_path_resets_selection_and_status(tmp_path: Path) -> None:
    file_path = tmp_path / "note.txt"
    file_path.write_text("hi", encoding="utf-8")
    state = create_initial_state(str(tmp_path))
    state = select_entry(state, str(file_path), is_dir=False)

    next_state = set_root_path(state, str(tmp_path))

    assert next_state.selected_path == ""
    assert "Root set to" in next_state.status_message
