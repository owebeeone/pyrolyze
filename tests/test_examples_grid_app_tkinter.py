from __future__ import annotations

from pathlib import Path
from runpy import run_path
import time
from types import SimpleNamespace

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


def _dispatch_entry_key_release(host, entry, *, keysym: str) -> None:
    callback = host.engine._engine._event_callbacks[id(entry)]["on_key_release"]
    assert callable(callback)
    callback(SimpleNamespace(widget=entry, keysym=keysym))


def _pump_events_until(root, predicate, *, max_steps: int = 400) -> None:
    for _ in range(max_steps):
        root.update_idletasks()
        root.update()
        if predicate():
            return
    raise AssertionError("timed out waiting for tkinter example UI to settle")


def test_native_tkinter_grid_app_example_mounts_and_rerenders() -> None:
    assert GRID_APP_PATH.exists()
    assert RUNNER_PATH.exists()

    namespace = run_path(str(RUNNER_PATH))
    build_app_host = namespace["build_app_host"]
    host, ctx = build_app_host()

    try:
        assert isinstance(host.root_widget, ttk.Frame)
        _pump_events(host.root)
        assert not bool(host.root.winfo_viewable())

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

        entries[0].delete(0, "end")
        entries[0].insert(0, "3")
        _dispatch_entry_key_release(host, entries[0], keysym="3")
        entries[1].delete(0, "end")
        entries[1].insert(0, "1")
        _dispatch_entry_key_release(host, entries[1], keysym="1")
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


def test_native_tkinter_grid_app_large_layout_toggle_stays_within_time_budget() -> None:
    namespace = run_path(str(RUNNER_PATH))
    build_app_host = namespace["build_app_host"]
    host, ctx = build_app_host()

    try:
        _pump_events(host.root)

        entries = _find_entries(host.root)
        assert len(entries) == 2
        entries[0].delete(0, "end")
        entries[0].insert(0, "20")
        _dispatch_entry_key_release(host, entries[0], keysym="2")
        entries[1].delete(0, "end")
        entries[1].insert(0, "20")
        _dispatch_entry_key_release(host, entries[1], keysym="2")
        _pump_events_until(
            host.root,
            lambda: "R20 C20" in _label_texts(host.root),
        )

        toggle_buttons = _find_buttons_by_text(host.root, "Use Grid Layout")
        assert len(toggle_buttons) == 1

        started_at = time.perf_counter()
        toggle_buttons[0].invoke()
        _pump_events_until(
            host.root,
            lambda: _count_manager(host.root, "grid") >= 400,
        )

        toggle_buttons = _find_buttons_by_text(host.root, "Use Row Layout")
        assert len(toggle_buttons) == 1
        toggle_buttons[0].invoke()
        _pump_events_until(
            host.root,
            lambda: _find_buttons_by_text(host.root, "Use Grid Layout") and "R20 C20" in _label_texts(host.root),
        )
        elapsed_s = time.perf_counter() - started_at

        assert elapsed_s <= 8.0
    finally:
        ctx.close_app_contexts()
        host.close()
