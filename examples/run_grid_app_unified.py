"""Run ``grid_app_unified`` with the stock PySide6 native host."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QTimer

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.pyrolyze_native_pyside6 import create_host, reconcile_window_content
from pyrolyze.runtime import RenderContext, dirtyof

SOURCE_PATH = Path(__file__).with_name("grid_app_unified.py")


def _load_component() -> Any:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    namespace = load_transformed_namespace(
        source,
        module_name="examples.grid_app_unified",
        filename=str(SOURCE_PATH),
    )
    return namespace["grid_app_unified"]


def build_app_host() -> tuple[Any, RenderContext]:
    component = _load_component()
    host = create_host()
    ctx = RenderContext()

    def reconcile_host() -> None:
        reconcile_window_content(host, ctx.committed_ui())

    def render_root() -> None:
        component._pyrolyze_meta._func(ctx, dirtyof())
        reconcile_host()

    def post_flush(callback: Any) -> None:
        QTimer.singleShot(
            0,
            lambda: (
                callback(),
                reconcile_host(),
            ),
        )

    ctx.set_flush_poster(post_flush)
    ctx.mount(render_root)
    return host, ctx


def main() -> int:
    host, ctx = build_app_host()
    try:
        return host.exec()
    finally:
        ctx.close_app_contexts()


if __name__ == "__main__":
    raise SystemExit(main())
