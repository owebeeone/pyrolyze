from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.pyrolyze_native_pyside6 import create_host, reconcile_window_content
from pyrolyze.runtime import RenderContext, dirtyof

_STUDIO_DIR = Path(__file__).resolve().parent
SOURCE_PATH = _STUDIO_DIR / "studio_shell.py"


def _load_component() -> Any:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    namespace = load_transformed_namespace(
        source,
        module_name="examples.studio.studio_shell",
        filename=str(SOURCE_PATH),
    )
    return namespace["studio_phase1_shell"]


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
    # Local imports: keep ``examples/studio`` self-contained.
    import studio_native  # noqa: PLC0415 — same directory as this script
    import studio_theme  # noqa: PLC0415

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("PyRolyze Studio")
    app.setOrganizationName("PyRolyze")

    base = QFont()
    app.setFont(QFont(base.family(), 10))

    host, ctx = build_app_host()

    root = host.root_widget
    if root is not None:
        root.setStyleSheet(studio_theme.VS_CODE_STUDIO_STYLESHEET)

    studio_native.apply_frameless_root_hints(host)
    studio_native.wire_title_bar_controls(host)
    studio_native.attach_explorer_model(host)
    studio_native.show_status_message(host)

    try:
        return host.exec()
    finally:
        ctx.close_app_contexts()


if __name__ == "__main__":
    # Ensure sibling modules resolve when run as ``python run_studio.py``.
    sd = str(_STUDIO_DIR)
    if sd not in sys.path:
        sys.path.insert(0, sd)
    raise SystemExit(main())
