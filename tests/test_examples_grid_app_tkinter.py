from __future__ import annotations

from pathlib import Path
from runpy import run_path

import pytest

pytest.importorskip("tkinter")
pytest.importorskip("tkinter.ttk")

from tkinter import ttk


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples"
GRID_APP_PATH = EXAMPLES_ROOT / "grid_app_tkinter.py"
RUNNER_PATH = EXAMPLES_ROOT / "run_grid_app_tkinter.py"


def _walk_widgets(widget):
    yield widget
    for child in widget.winfo_children():
        yield from _walk_widgets(child)


def _find_buttons_by_text(root, text: str) -> list[ttk.Button]:
    return [
        widget
        for widget in _walk_widgets(root)
        if isinstance(widget, ttk.Button) and str(widget.cget("text")) == text
    ]


def _find_entries(root) -> list[ttk.Entry]:
    return [widget for widget in _walk_widgets(root) if isinstance(widget, ttk.Entry)]


def _label_texts(root) -> list[str]:
    texts: list[str] = []
    for widget in _walk_widgets(root):
        if isinstance(widget, ttk.Label):
            texts.append(str(widget.cget("text")))
    return texts


def _count_manager(root, manager: str) -> int:
    return sum(1 for widget in _walk_widgets(root) if widget.winfo_manager() == manager)


def _pump_events(root) -> None:
    for _ in range(10):
        root.update_idletasks()
        root.update()


def test_native_tkinter_grid_app_example_mounts_and_rerenders() -> None:
    assert GRID_APP_PATH.exists()
    assert RUNNER_PATH.exists()

    namespace = run_path(str(RUNNER_PATH))
    build_app_host = namespace["build_app_host"]
    host, ctx = build_app_host()

    try:
        assert isinstance(host.root_widget, ttk.Frame)
        host.show()
        _pump_events(host.root)

        texts = _label_texts(host.root)
        assert "Grid App" in texts
        assert "Cols" in texts
        assert "Rows" in texts
        assert "R1 C1" in texts
        assert "R2 C2" in texts
        entries = _find_entries(host.root)
        assert len(entries) == 2
        assert entries[0].get() == "2"
        assert entries[1].get() == "2"

        assert _count_manager(host.root, "pack") > 0
        assert _count_manager(host.root, "grid") == 0

        entries[0].focus_force()
        _pump_events(host.root)
        entries[0].delete(0, "end")
        entries[0].insert(0, "3")
        entries[0].event_generate("<KeyRelease>", keysym="3")
        entries[1].focus_force()
        _pump_events(host.root)
        entries[1].delete(0, "end")
        entries[1].insert(0, "1")
        entries[1].event_generate("<KeyRelease>", keysym="1")
        _pump_events(host.root)

        texts = _label_texts(host.root)
        assert "R1 C3" in texts
        assert "R2 C1" not in texts

        toggle_buttons = _find_buttons_by_text(host.root, "Use Grid Layout")
        assert len(toggle_buttons) == 1

        toggle_buttons[0].invoke()
        _pump_events(host.root)

        texts = _label_texts(host.root)
        assert "R1 C3" in texts
        assert _count_manager(host.root, "grid") >= 3
        assert _find_buttons_by_text(host.root, "Use Row Layout")

        cols_plus = _find_buttons_by_text(host.root, "Cols +")
        rows_plus = _find_buttons_by_text(host.root, "Rows +")
        assert len(cols_plus) == 1
        assert len(rows_plus) == 1
        cols_plus[0].invoke()
        rows_plus[0].invoke()
        _pump_events(host.root)

        texts = _label_texts(host.root)
        assert "R1 C4" in texts
        assert "R2 C1" in texts
        assert _count_manager(host.root, "grid") >= 8
    finally:
        ctx.close_app_contexts()
        host.close()
