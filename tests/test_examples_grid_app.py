from __future__ import annotations

import os
import subprocess
import sys
from io import StringIO
from pathlib import Path
from runpy import run_path

import pytest

from pyrolyze.api import UIElement
from pyrolyze.compiler import load_transformed_namespace
import pyrolyze.pyrolyze_tkinter as tk_wrapper
from pyrolyze.runtime import RenderContext, TraceChannel, TraceRecord, dirtyof
from pyrolyze.pyrolyze_tkinter import _create_tk_root, tkinter_available


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


def _find_text_field(node: UIElement, field_id: str) -> UIElement:
    if node.kind == "text_field" and node.props.get("field_id") == field_id:
        return node
    for child in node.children:
        try:
            return _find_text_field(child, field_id)
        except StopIteration:
            continue
    raise StopIteration(field_id)


def _find_button(node: UIElement, label: str) -> UIElement:
    if node.kind == "button" and node.props.get("label") == label:
        return node
    for child in node.children:
        try:
            return _find_button(child, label)
        except StopIteration:
            continue
    raise StopIteration(label)


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


def _grid_cell(root: UIElement, row_index: int, col_index: int) -> UIElement:
    grid_section = _find_section(root.children, "Grid")
    row = next(
        child
        for child in grid_section.children
        if child.kind == "row" and child.props.get("row_id") == f"grid:row:{row_index}"
    )
    return _find_section(row.children, f"R{row_index + 1} C{col_index + 1}")


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


def test_grid_app_example_cell_increment_updates_immediately_in_pyside_host() -> None:
    from PySide6.QtWidgets import QGroupBox, QLineEdit, QPushButton

    namespace = run_path(str(RUNNER_PATH))
    build_app_host = namespace["build_app_host"]
    host, ctx = build_app_host("pyside6")

    def _pump_events() -> None:
        for _ in range(10):
            host.app.processEvents()

    try:
        first_cell = next(
            widget
            for widget in host.content_widget.findChildren(QGroupBox)
            if widget.title() == "R1 C1"
        )
        first_cell_field = host.content_widget.findChild(QLineEdit, "cell:0:0:value")
        assert first_cell_field is not None
        first_cell_plus = next(
            button for button in first_cell.findChildren(QPushButton) if button.text() == "+"
        )

        first_cell_plus.click()
        _pump_events()

        assert first_cell_field.text() == "1"
    finally:
        ctx.close_app_contexts()
        host.close()


def test_grid_app_example_cell_increment_preserves_committed_grid_structure() -> None:
    ctx = _mount_grid_app()
    root = ctx.committed_ui()[0]
    first_cell = _grid_cell(root, 0, 0)
    first_cell_plus = _find_button(first_cell, "+")

    first_cell_plus.props["on_press"]()
    ctx.run_pending_invalidations()

    committed = ctx.committed_ui()
    assert len(committed) == 1
    root = committed[0]
    assert root.kind == "section"
    assert root.props["title"] == "Grid App"
    assert _grid_shape(root) == (2, 2)
    assert _find_text_field(_grid_cell(root, 0, 0), "cell:0:0:value").props["value"] == "1"
    assert _find_text_field(_grid_cell(root, 0, 1), "cell:0:1:value").props["value"] == "0"


def test_run_grid_app_parser_selects_backend_and_builds_pyside_host() -> None:
    namespace = run_path(str(RUNNER_PATH))
    parser = namespace["build_parser"]()

    assert parser.parse_args([]).backend == "pyside6"
    assert parser.parse_args(["--backend", "tkinter"]).backend == "tkinter"
    assert parser.parse_args(["--backend", "dearpygui"]).backend == "dearpygui"
    assert parser.parse_args(["--trace", "invalidation,boundary"]).trace == ["invalidation,boundary"]
    assert parser.parse_args(["--trace", "reconcile", "--trace", "flush"]).trace == ["reconcile", "flush"]
    assert parser.parse_args(["--trace-stdout"]).trace_stdout is True

    build_app_host = namespace["build_app_host"]
    host, ctx = build_app_host("pyside6")
    try:
        assert host.content_layout.count() == 1
    finally:
        ctx.close_app_contexts()
        host.close()


def test_run_grid_app_resolves_trace_channels_from_cli_tokens() -> None:
    namespace = run_path(str(RUNNER_PATH))
    resolve_trace_channels = namespace["resolve_trace_channels"]

    assert resolve_trace_channels(None) == ()
    assert resolve_trace_channels(["invalidation,boundary", "reconcile"]) == (
        TraceChannel.INVALIDATION,
        TraceChannel.BOUNDARY,
        TraceChannel.RECONCILE,
    )
    assert resolve_trace_channels(["all"]) == tuple(TraceChannel)


def test_run_grid_app_main_configures_trace_from_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    namespace = run_path(str(RUNNER_PATH))
    calls: list[tuple[tuple[TraceChannel, ...], object | None]] = []

    class _FakeContext:
        def close_app_contexts(self) -> None:
            return None

    class _FakeHost:
        def exec(self) -> int:
            return 17

    def _fake_build_app_host(_backend: str) -> tuple[object, object]:
        return _FakeHost(), _FakeContext()

    def _fake_configure_trace(*, enabled: object, sink: object | None = None) -> None:
        calls.append((tuple(enabled), sink))

    main = namespace["main"]
    main.__globals__["build_app_host"] = _fake_build_app_host
    main.__globals__["configure_trace"] = _fake_configure_trace

    assert main(["--backend", "pyside6", "--trace", "invalidation,reconcile"]) == 17
    assert calls == [((TraceChannel.INVALIDATION, TraceChannel.RECONCILE), None)]


def test_run_grid_app_main_configures_stdout_trace_sink() -> None:
    namespace = run_path(str(RUNNER_PATH))
    calls: list[tuple[tuple[TraceChannel, ...], object | None]] = []

    class _FakeContext:
        def close_app_contexts(self) -> None:
            return None

    class _FakeHost:
        def exec(self) -> int:
            return 23

    def _fake_build_app_host(_backend: str) -> tuple[object, object]:
        return _FakeHost(), _FakeContext()

    def _fake_configure_trace(*, enabled: object, sink: object | None = None) -> None:
        calls.append((tuple(enabled), sink))

    buffer = StringIO()
    main = namespace["main"]
    main.__globals__["build_app_host"] = _fake_build_app_host
    main.__globals__["configure_trace"] = _fake_configure_trace
    main.__globals__["sys"] = type("_FakeSys", (), {"stdout": buffer})()

    assert main(["--backend", "pyside6", "--trace", "flush", "--trace-stdout"]) == 23
    assert calls[0][0] == (TraceChannel.FLUSH,)
    assert calls[0][1] is not None
    calls[0][1](TraceRecord(channel=TraceChannel.FLUSH, event="start", fields={"queued": ()}))
    output_lines = buffer.getvalue().splitlines()
    assert len(output_lines) == 2
    assert output_lines[0].startswith("process.start pid=")
    assert "backend=pyside6" in output_lines[0]
    assert "argv=['--backend', 'pyside6', '--trace', 'flush', '--trace-stdout']" in output_lines[0]
    assert output_lines[1].endswith("flush.start queued=()")


@pytest.fixture
def tk_runtime(monkeypatch: pytest.MonkeyPatch):
    root = _create_tk_root()
    root.destroy()
    monkeypatch.setattr(tk_wrapper, "tkinter_available", lambda: True)
    yield
    hidden_root = getattr(tk_wrapper, "_TK_ROOT", None)
    if hidden_root is not None:
        hidden_root.destroy()
        tk_wrapper._TK_ROOT = None


def test_run_grid_app_builds_tkinter_host(tk_runtime) -> None:
    namespace = run_path(str(RUNNER_PATH))
    build_app_host = namespace["build_app_host"]
    host, ctx = build_app_host("tkinter")
    try:
        assert len(tuple(host.content_frame.pack_slaves())) == 1
    finally:
        ctx.close_app_contexts()
        host.close()


def test_run_grid_app_builds_dearpygui_host() -> None:
    """Run in a subprocess: loading ``dearpygui`` in-process breaks later Tk tests (GL/Tk clash)."""

    pytest.importorskip("dearpygui")
    runner = str(RUNNER_PATH)
    repo = str(REPO_ROOT)
    code = (
        "import sys\n"
        f"sys.path.insert(0, {repo!r})\n"
        "from runpy import run_path\n"
        f"ns = run_path({runner!r})\n"
        'host, ctx = ns["build_app_host"]("dearpygui")\n'
        "assert host.owner_state is not None\n"
        "assert len(host.owner_state.mounted_nodes) == 1\n"
        "ctx.close_app_contexts()\n"
        "host.close()\n"
    )
    subprocess.check_call([sys.executable, "-c", code], cwd=repo)
