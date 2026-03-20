from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.pyrolyze_pyside6 import create_window, reconcile_window_content
from pyrolyze.runtime import RenderContext, dirtyof


SOURCE_PATH = Path(__file__).resolve().parent.parent / "ui" / "studio_root.py"


def _ensure_repo_root_on_syspath() -> Path:
    repo_root = SOURCE_PATH.parent.parent.parent.resolve()
    root_str = str(repo_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return repo_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the Studio prototype with architecture-aligned modules."
    )
    parser.add_argument(
        "--root",
        type=str,
        default="",
        help="Initial root path for explorer simulation (defaults to cwd).",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run a short startup smoke cycle and exit automatically.",
    )
    return parser


def _load_component() -> Any:
    _ensure_repo_root_on_syspath()
    source = SOURCE_PATH.read_text(encoding="utf-8")
    namespace = load_transformed_namespace(
        source,
        module_name="Studio.ui.studio_root",
        filename=str(SOURCE_PATH),
    )
    return namespace["studio_app"]


def build_host(root_path: str) -> tuple[Any, RenderContext]:
    component = _load_component()
    host = create_window("PyRolyze Studio Prototype", width=1200, height=820)
    ctx = RenderContext()

    def reconcile_host() -> None:
        reconcile_window_content(
            host,
            ctx.committed_ui(),
            on_after_event=run_flush_and_reconcile,
        )

    def run_flush_and_reconcile() -> None:
        ctx.run_pending_invalidations()
        reconcile_host()

    def render_root() -> None:
        component._pyrolyze_meta._func(ctx, dirtyof(), root_path)
        reconcile_host()

    from PySide6.QtCore import QTimer

    ctx.set_flush_poster(lambda callback: QTimer.singleShot(0, lambda: (callback(), reconcile_host())))
    ctx.mount(render_root)
    return host, ctx


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    host, ctx = build_host(args.root)
    try:
        if args.smoke:
            from PySide6.QtCore import QTimer

            QTimer.singleShot(120, host.close)
        return host.exec()
    finally:
        ctx.close_app_contexts()


if __name__ == "__main__":
    raise SystemExit(main())
