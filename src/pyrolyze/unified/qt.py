"""Qt / PySide6 unified native adapter."""

from __future__ import annotations

from typing import Any

from pyrolyze.api import UIElement
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary

from pyrolyze.unified.base import UnifiedNativeLibrary


class QtUnifiedNativeLibrary(UnifiedNativeLibrary):
    @property
    def backend_id(self) -> str:
        return "qt"

    @property
    def native_library_type(self) -> type[Any]:
        return PySide6UiLibrary

    def push_button(self, *, text: str = "", **props: Any) -> UIElement:
        merged = {"text": text, **props}
        return UIElement(kind="QPushButton", props=merged)
