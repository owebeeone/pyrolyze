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

    def int_field(
        self,
        *,
        value: int = 0,
        min_value: int | None = None,
        max_value: int | None = None,
        step: int = 1,
        **props: Any,
    ) -> UIElement:
        lo = 0 if min_value is None else min_value
        hi = 10**9 if max_value is None else max_value
        merged: dict[str, Any] = {
            "from_": lo,
            "to": hi,
            "increment": step,
            "text": str(value),
            **props,
        }
        return UIElement(kind="tkinter_Spinbox", props=merged)

    def float_field(
        self,
        *,
        value: float = 0.0,
        min_value: float | None = None,
        max_value: float | None = None,
        step: float = 0.1,
        **props: Any,
    ) -> UIElement:
        lo = 0.0 if min_value is None else min_value
        hi = 1e9 if max_value is None else max_value
        merged: dict[str, Any] = {
            "from_": lo,
            "to": hi,
            "increment": step,
            "format": "%.6g",
            "text": str(value),
            **props,
        }
        return UIElement(kind="tkinter_Spinbox", props=merged)

    def combo_box(
        self,
        *,
        items: tuple[str, ...] = (),
        current_index: int = 0,
        **props: Any,
    ) -> UIElement:
        ci = max(0, min(current_index, len(items) - 1)) if items else 0
        text = items[ci] if items else ""
        merged: dict[str, Any] = {"values": list(items), "text": text, **props}
        return UIElement(kind="Combobox", props=merged)

    def slider(
        self,
        *,
        value: int = 0,
        min_value: int = 0,
        max_value: int = 100,
        **props: Any,
    ) -> UIElement:
        merged: dict[str, Any] = {
            "from_": float(min_value),
            "to": float(max_value),
            "value": float(value),
            **props,
        }
        return UIElement(kind="ttk_Scale", props=merged)

    def progress(self, *, value: float = 0.0, **props: Any) -> UIElement:
        v = max(0.0, min(1.0, value))
        merged = {"maximum": 100, "value": int(round(v * 100)), **props}
        return UIElement(kind="Progressbar", props=merged)

    def tab_stack(self, **props: Any) -> UIElement:
        return UIElement(kind="Notebook", props=dict(props))

    def radio_button(self, *, text: str = "", checked: bool = False, **props: Any) -> UIElement:
        merged = {"text": text, "value": text, **props}
        if checked:
            merged["state"] = "selected"
        return UIElement(kind="ttk_Radiobutton", props=merged)

    def text_area(self, *, text: str = "", read_only: bool = False, **props: Any) -> UIElement:
        st = "disabled" if read_only else "normal"
        merged: dict[str, Any] = {"text": text, "height": 6, "width": 48, "wrap": "word", "state": st, **props}
        return UIElement(kind="Text", props=merged)

    def static_text(self, *, text: str = "", **props: Any) -> UIElement:
        merged = {"text": text, **props}
        return UIElement(kind="ttk_Label", props=merged)

    def menu_bar(self, **props: Any) -> UIElement:
        merged: dict[str, Any] = {"tearoff": 0, **props}
        return UIElement(kind="Menu", props=merged)

    def tool_bar(self, *, title: str = "", **props: Any) -> UIElement:
        _ = title
        merged: dict[str, Any] = {"padding": 2, **props}
        return UIElement(kind="ttk_Frame", props=merged)

    def separator(self, *, horizontal: bool = True, **props: Any) -> UIElement:
        orient = "horizontal" if horizontal else "vertical"
        merged: dict[str, Any] = {"orient": orient, **props}
        return UIElement(kind="Separator", props=merged)

    def scroll_panel(self, **props: Any) -> UIElement:
        merged: dict[str, Any] = {"width": 240, "height": 160, "background": "white", **props}
        return UIElement(kind="Canvas", props=merged)

    def spacer(self, *, width: int = 0, height: int = 0, **props: Any) -> UIElement:
        merged: dict[str, Any] = dict(props)
        if width > 0:
            merged["width"] = width
        if height > 0:
            merged["height"] = height
        return UIElement(kind="ttk_Frame", props=merged)
