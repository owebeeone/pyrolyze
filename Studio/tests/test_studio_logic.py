from __future__ import annotations

from pathlib import Path

from Studio.studio_logic import (
    build_snapshot_text,
    list_entries,
    normalize_root_path,
    safe_preview,
)


def test_normalize_root_path_uses_cwd_for_blank() -> None:
    result = normalize_root_path("   ")
    assert result == str(Path.cwd())


def test_list_entries_sorts_directories_first_and_filters_hidden(tmp_path: Path) -> None:
    (tmp_path / ".hidden.txt").write_text("hidden", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    (tmp_path / "a_dir").mkdir()

    entries = list_entries(str(tmp_path), show_hidden=False, limit=10)
    names = [entry["name"] for entry in entries]

    assert names[0] == "a_dir"
    assert ".hidden.txt" not in names
    assert "b.txt" in names


def test_list_entries_returns_error_entry_for_missing_path(tmp_path: Path) -> None:
    missing = tmp_path / "missing_dir"
    entries = list_entries(str(missing), show_hidden=True, limit=10)

    assert len(entries) == 1
    assert entries[0]["kind"] == "error"
    assert "not found" in str(entries[0]["name"]).lower()


def test_safe_preview_returns_file_content(tmp_path: Path) -> None:
    target = tmp_path / "example.txt"
    target.write_text("hello world", encoding="utf-8")

    assert safe_preview(str(target), max_chars=20) == "hello world"


def test_safe_preview_for_directory_returns_message(tmp_path: Path) -> None:
    assert "directory" in safe_preview(str(tmp_path), max_chars=20).lower()


def test_build_snapshot_text_contains_key_fields() -> None:
    snapshot = build_snapshot_text(
        root_path="/tmp",
        entry_count=8,
        selected_path="/tmp/file.txt",
        active_panel="Output",
        refresh_tick=3,
    )
    assert "entries=8" in snapshot
    assert "active_panel=Output" in snapshot
    assert "refresh_tick=3" in snapshot
