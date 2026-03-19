from __future__ import annotations

import os
from pathlib import Path
from runpy import run_path

import pytest

from pyrolyze.api import UIElement
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof
from pyrolyze.pyrolyze_tkinter import tkinter_available


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples"
GRID_APP_PATH = EXAMPLES_ROOT / "grid_app.py"
RUNNER_PATH = EXAMPLES_ROOT / "run_grid_app.py"


def _load_grid_namespace() -> dict[str, object]:
    source = GRID_APP_PATH.read_text(encoding="utf-8")
    return load_transformed_namespace(
        source,
        module_name="examples.grid_app",
        filename=str(GRID_APP_PATH),
    )


def _mount_grid_app() -> RenderContext:
    namespace = _load_grid_namespace()
    grid_app = namespace["grid_app"]
    ctx = RenderContext()
    ctx.mount(lambda: grid_app._pyrolyze_meta._func(ctx, dirtyof()))
    return ctx


def _find_section(children: tuple[UIElement, ...], title: str) -> UIElement:
    return next(
        child
        for child in children
        if child.kind == "section" and child.props.get("title") == title
    )


def _grid_shape(root: UIElement) -> tuple[int, int]:
    grid_section = _find_section(root.children, "Grid")
    rows = tuple(child for child in grid_section.children if child.kind == "row")
    if not rows:
        return (0, 0)
    return (len(rows), len(tuple(child for child in rows[0].children if child.kind == "section")))


def _header_counters(root: UIElement) -> tuple[UIElement, UIElement]:
    header_section = _find_section(root.children, "Header")
    header_row = next(child for child in header_section.children if child.kind == "row")
    counters = tuple(child for child in header_row.children if child.kind == "section")
    assert len(counters) == 2
    return counters[0], counters[1]


def _counter_controls(counter_section: UIElement) -> tuple[UIElement, UIElement, UIElement]:
    controls_row = next(child for child in counter_section.children if child.kind == "row")
    assert len(controls_row.children) == 3
    minus_button, count_field, plus_button = controls_row.children
    return minus_button, count_field, plus_button


def test_grid_app_example_renders_header_and_initial_grid() -> None:
    assert GRID_APP_PATH.exists()

    ctx = _mount_grid_app()
    committed = ctx.committed_ui()

    assert len(committed) == 1
    root = committed[0]
    assert root.kind == "section"
    assert root.props["title"] == "Grid App"
    assert _find_section(root.children, "Header").kind == "section"
    assert _find_section(root.children, "Grid").kind == "section"
    assert _grid_shape(root) == (2, 2)


def test_grid_app_example_header_events_resize_grid() -> None:
    ctx = _mount_grid_app()
    root = ctx.committed_ui()[0]
    cols_counter, rows_counter = _header_counters(root)

    _, _, cols_plus = _counter_controls(cols_counter)
    cols_plus.props["on_press"]()
    ctx.run_pending_invalidations()

    root = ctx.committed_ui()[0]
    assert _grid_shape(root) == (2, 3)

    _, rows_field, _ = _counter_controls(_header_counters(root)[1])
    rows_field.props["on_change"]("1")
    ctx.run_pending_invalidations()

    root = ctx.committed_ui()[0]
    assert _grid_shape(root) == (1, 3)
    assert _counter_controls(_header_counters(root)[1])[1].props["value"] == "1"


def test_run_grid_app_parser_selects_backend_and_builds_pyside_host() -> None:
    namespace = run_path(str(RUNNER_PATH))
    parser = namespace["build_parser"]()

    assert parser.parse_args([]).backend == "pyside6"
    assert parser.parse_args(["--backend", "tkinter"]).backend == "tkinter"

    build_app_host = namespace["build_app_host"]
    host, ctx = build_app_host("pyside6")
    try:
        assert host.content_layout.count() == 1
    finally:
        ctx.close_app_contexts()
        host.close()


@pytest.mark.skipif(not tkinter_available(), reason="Tk root unavailable in this environment")
def test_run_grid_app_builds_tkinter_host() -> None:
    namespace = run_path(str(RUNNER_PATH))
    build_app_host = namespace["build_app_host"]
    host, ctx = build_app_host("tkinter")
    try:
        assert len(tuple(host.content_frame.pack_slaves())) == 1
    finally:
        ctx.close_app_contexts()
        host.close()
