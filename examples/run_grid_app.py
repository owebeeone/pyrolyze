from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Literal

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.pyrolyze_pyside6 import create_window as create_pyside_window
from pyrolyze.pyrolyze_pyside6 import reconcile_window_content as reconcile_pyside_content
from pyrolyze.pyrolyze_tkinter import create_window as create_tk_window
from pyrolyze.pyrolyze_tkinter import reconcile_window_content as reconcile_tk_content
from pyrolyze.runtime import RenderContext, dirtyof


BackendName = Literal["pyside6", "tkinter"]
SOURCE_PATH = Path(__file__).with_name("grid_app.py")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the PyRolyze dynamic grid example.")
    parser.add_argument(
        "--backend",
        choices=("pyside6", "tkinter"),
        default="pyside6",
        help="Select the native UI backend.",
    )
    return parser


def _load_grid_app() -> Any:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    namespace = load_transformed_namespace(
        source,
        module_name="examples.grid_app",
        filename=str(SOURCE_PATH),
    )
    return namespace["grid_app"]


def _post_flush(host: Any, backend: BackendName, callback: Any) -> None:
    if backend == "pyside6":
        from PySide6.QtCore import QTimer

        QTimer.singleShot(0, callback)
        return

    host.root.after(0, callback)


def build_app_host(backend: BackendName) -> tuple[Any, RenderContext]:
    component = _load_grid_app()
    if backend == "pyside6":
        host = create_pyside_window("PyRolyze Dynamic Grid")
        reconcile_content = reconcile_pyside_content
    else:
        host = create_tk_window("PyRolyze Dynamic Grid")
        reconcile_content = reconcile_tk_content

    ctx = RenderContext()

    def render_root() -> None:
        component._pyrolyze_meta._func(ctx, dirtyof())
        reconcile_content(host, ctx.committed_ui())

    ctx.set_flush_poster(lambda callback: _post_flush(host, backend, callback))
    ctx.mount(render_root)
    return host, ctx


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    host, ctx = build_app_host(args.backend)
    try:
        if args.backend == "pyside6":
            return host.exec()
        host.run()
        return 0
    finally:
        ctx.close_app_contexts()


if __name__ == "__main__":
    raise SystemExit(main())
