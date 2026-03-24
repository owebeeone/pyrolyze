"""Tkinter / ttk unified native adapter."""

from __future__ import annotations

from typing import Any

from pyrolyze.api import UIElement
from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary

from pyrolyze.unified.base import UnifiedNativeLibrary


class TkUnifiedNativeLibrary(UnifiedNativeLibrary):
    @property
    def backend_id(self) -> str:
        return "tk"

    @property
    def native_library_type(self) -> type[Any]:
        return TkinterUiLibrary

    def push_button(self, *, text: str = "", **props: Any) -> UIElement:
        merged = {"text": text, **props}
        return UIElement(kind="ttk_Button", props=merged)

    def toggle(self, *, checked: bool = False, text: str = "", **props: Any) -> UIElement:
        merged = {"text": text, "checked": checked, **props}
        return UIElement(kind="ttk_Checkbutton", props=merged)

    def text_field(self, *, text: str = "", **props: Any) -> UIElement:
        merged = {"text": text, **props}
        return UIElement(kind="ttk_Entry", props=merged)
