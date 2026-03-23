from __future__ import annotations

from pathlib import Path

from pyrolyze.api import UIElement
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples"
GRID_APP_PATH = EXAMPLES_ROOT / "grid_app_dearpygui.py"
RUNNER_PATH = EXAMPLES_ROOT / "run_grid_app_dearpygui_pyrolyze.py"


def _load_grid_namespace() -> dict[str, object]:
    source = GRID_APP_PATH.read_text(encoding="utf-8")
    return load_transformed_namespace(
        source,
        module_name="examples.grid_app_dearpygui",
        filename=str(GRID_APP_PATH),
    )


def test_grid_app_dearpygui_example_compiles() -> None:
    assert GRID_APP_PATH.exists()
    assert RUNNER_PATH.exists()
    namespace = _load_grid_namespace()
    assert callable(namespace["grid_app_dearpygui"])


def test_grid_app_dearpygui_committed_ui_root_is_dpg_window() -> None:
    namespace = _load_grid_namespace()
    grid_app_dearpygui = namespace["grid_app_dearpygui"]
    ctx = RenderContext()
    ctx.mount(lambda: grid_app_dearpygui._pyrolyze_meta._func(ctx, dirtyof()))
    committed = ctx.committed_ui()
    assert len(committed) == 1
    root = committed[0]
    assert isinstance(root, UIElement)
    assert root.kind == "DpgWindow"
    assert root.props.get("label") == "Native DearPyGui Grid"
    assert root.props.get("width") == 960
    assert root.props.get("height") == 640
