from __future__ import annotations

from pathlib import Path
from typing import TypedDict


class ExplorerEntry(TypedDict):
    key: str
    name: str
    path: str
    is_dir: bool
    kind: str


def normalize_root_path(raw_path: str) -> str:
    text = raw_path.strip()
    if not text:
        return str(Path.cwd())
    return str(Path(text).expanduser())


def list_entries(root_path: str, *, show_hidden: bool, limit: int = 50) -> tuple[ExplorerEntry, ...]:
    normalized_root = Path(normalize_root_path(root_path))
    max_items = max(1, int(limit))

    try:
        if not normalized_root.exists():
            raise FileNotFoundError(f"path not found: {normalized_root}")
        if not normalized_root.is_dir():
            raise NotADirectoryError(f"not a directory: {normalized_root}")

        items: list[ExplorerEntry] = []
        children = sorted(normalized_root.iterdir(), key=lambda path: (not path.is_dir(), path.name.lower()))
        for child in children:
            if not show_hidden and child.name.startswith("."):
                continue
            items.append(
                ExplorerEntry(
                    key=str(child),
                    name=child.name,
                    path=str(child),
                    is_dir=child.is_dir(),
                    kind="dir" if child.is_dir() else "file",
                )
            )
            if len(items) >= max_items:
                break
        return tuple(items)
    except Exception as exc:
        return (
            ExplorerEntry(
                key="__error__",
                name=str(exc),
                path=str(normalized_root),
                is_dir=False,
                kind="error",
            ),
        )


def safe_preview(path: str, *, max_chars: int = 1200) -> str:
    if not path:
        return "No file selected."
    target = Path(path)
    if not target.exists():
        return f"Path not found: {target}"
    if target.is_dir():
        return f"Selected path is a directory: {target}"
    try:
        content = target.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return f"Unable to read file: {exc}"

    if max_chars < 1:
        max_chars = 1
    if len(content) > max_chars:
        return f"{content[:max_chars]}\n\n...[truncated]..."
    return content


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

