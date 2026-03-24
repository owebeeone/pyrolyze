"""Minimal PySide6 example using ``pyrolyze.unified`` for a leaf widget.

Prefer :func:`pyrolyze.unified.get_unified_native_library` for portable control
types; use generated ``PySide6UiLibrary`` for layout chrome (main window,
layouts) until a unified shell API lands.

**Run this through the compiler** (do not execute this file directly — the
``@pyrolyze`` stub will fail). From the ``pyrolyze`` repo root::

    uv run python examples/run_unified_hello_pyside6.py
"""

from __future__ import annotations

from PySide6.QtWidgets import QBoxLayout

from pyrolyze.api import UIElement, call_native, pyrolyze
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt
from pyrolyze.unified import get_unified_native_library

_Lib = get_unified_native_library(backend="qt")


@pyrolyze
def unified_hello_content() -> None:
    """Body under the main window: one component so parent ``CQVBoxLayout`` has a single child."""
    Qt.CQLabel(
        "Button below is emitted via UnifiedNativeLibrary → QPushButton",
        objectName="unified:hint",
    )
    btn = _Lib.push_button(text="Hello (unified)")
    call_native(UIElement)(kind=btn.kind, props=dict(btn.props))


@pyrolyze
def unified_hello_pyside6() -> None:
    with Qt.CQMainWindow(
        windowTitle="PyRolyze — unified hello",
        minimumWidth=360,
        minimumHeight=200,
    ):
        with Qt.CQWidget(objectName="central_widget"):
            with Qt.CQBoxLayout(QBoxLayout.Direction.TopToBottom):
                # BoxLayout: one structural child (``grid_app_pyside6`` uses the same pattern).
                with Qt.CQWidget(objectName="unified:hello:body"):
                    with Qt.CQVBoxLayout(objectName="unified:hello:column"):
                        unified_hello_content()


if __name__ == "__main__":
    raise SystemExit(
        "Run examples/run_unified_hello_pyside6.py instead "
        "(this module must be compiler-transformed)."
    )
