"""Dear PyGui unified native adapter."""

from __future__ import annotations

from typing import Any

from pyrolyze.api import UIElement
from pyrolyze.backends.dearpygui.generated_library import DearPyGuiUiLibrary

from pyrolyze.unified.base import UnifiedNativeLibrary


class DpgUnifiedNativeLibrary(UnifiedNativeLibrary):
    @property
    def backend_id(self) -> str:
        return "dpg"

    @property
    def native_library_type(self) -> type[Any]:
        return DearPyGuiUiLibrary

    def push_button(self, *, text: str = "", **props: Any) -> UIElement:
        # Aligns with ``DearPyGuiC.Button`` / ``DpgButton`` author surface (label=...).
        merged = {**props}
        if text:
            merged["label"] = text
        return UIElement(kind="DpgButton", props=merged)

    def toggle(self, *, checked: bool = False, text: str = "", **props: Any) -> UIElement:
        merged = {**props}
        if text:
            merged["label"] = text
        merged["value"] = checked
        return UIElement(kind="DpgCheckbox", props=merged)

    def text_field(self, *, text: str = "", **props: Any) -> UIElement:
        merged = {**props}
        if text:
            merged["value"] = text
        return UIElement(kind="DpgInputText", props=merged)
