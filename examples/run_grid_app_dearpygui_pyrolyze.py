"""Run the native ``@pyrolyze`` DearPyGui grid example (``CDpg*`` + ``pyrolyze_native_dearpygui``).

``uv run python examples/run_grid_app_dearpygui_pyrolyze.py``
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.pyrolyze_native_dearpygui import create_host, reconcile_window_content
from pyrolyze.runtime import RenderContext, dirtyof


SOURCE_PATH = Path(__file__).with_name("grid_app_dearpygui.py")


def _load_component() -> Any:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    namespace = load_transformed_namespace(
        source,
        module_name="examples.grid_app_dearpygui",
        filename=str(SOURCE_PATH),
    )
    return namespace["grid_app_dearpygui"]


def build_app_host() -> tuple[Any, RenderContext]:
    component = _load_component()
    host = create_host(title="Native DearPyGui Grid", width=960, height=640)
    ctx = RenderContext()

    def reconcile_host() -> None:
        reconcile_window_content(host, ctx.committed_ui())

    def render_root() -> None:
        component._pyrolyze_meta._func(ctx, dirtyof())
        reconcile_host()

    def post_flush(callback: Any) -> None:
        callback()
        reconcile_host()

    ctx.set_flush_poster(post_flush)
    ctx.mount(render_root)
    return host, ctx


def main() -> int:
    host, ctx = build_app_host()
    try:
        host.run()
        return 0
    finally:
        ctx.close_app_contexts()
        host.close()


if __name__ == "__main__":
    raise SystemExit(main())
