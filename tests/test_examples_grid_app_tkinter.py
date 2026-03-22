from __future__ import annotations

from pathlib import Path
from runpy import run_path

import pytest

from pyrolyze.compiler import load_transformed_namespace
import pyrolyze.pyrolyze_tkinter as tk_wrapper
from pyrolyze.runtime import RenderContext, dirtyof


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples"
GRID_APP_PATH = EXAMPLES_ROOT / "grid_app_tkinter.py"
RUNNER_PATH = EXAMPLES_ROOT / "run_grid_app_tkinter.py"


@pytest.fixture
def tk_runtime(monkeypatch: pytest.MonkeyPatch):
    if not tk_wrapper.tkinter_available():
        pytest.skip("Tk root unavailable in this environment")
    monkeypatch.setattr(tk_wrapper, "tkinter_available", lambda: True)
    yield
    hidden_root = getattr(tk_wrapper, "_TK_ROOT", None)
    if hidden_root is not None:
        hidden_root.destroy()
        tk_wrapper._TK_ROOT = None


def test_tkinter_grid_app_example_renders_initial_tree() -> None:
    assert GRID_APP_PATH.exists()

    source = GRID_APP_PATH.read_text(encoding="utf-8")
    namespace = load_transformed_namespace(
        source,
        module_name="examples.grid_app_tkinter",
        filename=str(GRID_APP_PATH),
    )
    component = namespace["grid_app_tkinter"]
    ctx = RenderContext()
    ctx.mount(lambda: component._pyrolyze_meta._func(ctx, dirtyof()))

    committed = ctx.committed_ui()
    assert len(committed) == 1
    root = committed[0]
    assert root.kind == "section"
    assert root.props["title"] == "Grid App"
    assert len(root.children) == 2


def test_run_grid_app_tkinter_builds_host(tk_runtime) -> None:
    assert RUNNER_PATH.exists()

    namespace = run_path(str(RUNNER_PATH))
    build_app_host = namespace["build_app_host"]
    host, ctx = build_app_host()

    try:
        assert len(tuple(host.content_frame.pack_slaves())) == 1
    finally:
        ctx.close_app_contexts()
        host.close()
