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

    def int_field(
        self,
        *,
        value: int = 0,
        min_value: int | None = None,
        max_value: int | None = None,
        step: int = 1,
        **props: Any,
    ) -> UIElement:
        _ = step  # DpgInputInt has no single-step analogue in unified v1
        merged: dict[str, Any] = {"value": value, **props}
        if min_value is not None:
            merged["min_value"] = min_value
        if max_value is not None:
            merged["max_value"] = max_value
        return UIElement(kind="DpgInputInt", props=merged)

    def float_field(
        self,
        *,
        value: float = 0.0,
        min_value: float | None = None,
        max_value: float | None = None,
        step: float = 0.1,
        **props: Any,
    ) -> UIElement:
        _ = step
        merged: dict[str, Any] = {"value": value, **props}
        if min_value is not None:
            merged["min_value"] = min_value
        if max_value is not None:
            merged["max_value"] = max_value
        return UIElement(kind="DpgInputFloat", props=merged)

    def combo_box(
        self,
        *,
        items: tuple[str, ...] = (),
        current_index: int = 0,
        **props: Any,
    ) -> UIElement:
        ci = max(0, min(current_index, len(items) - 1)) if items else 0
        val = items[ci] if items else ""
        merged: dict[str, Any] = {"items": list(items), "value": val, **props}
        return UIElement(kind="DpgCombo", props=merged)

    def slider(
        self,
        *,
        value: int = 0,
        min_value: int = 0,
        max_value: int = 100,
        **props: Any,
    ) -> UIElement:
        merged: dict[str, Any] = {
            "min_value": min_value,
            "max_value": max_value,
            "value": value,
            **props,
        }
        return UIElement(kind="DpgSliderInt", props=merged)

    def progress(self, *, value: float = 0.0, **props: Any) -> UIElement:
        v = max(0.0, min(1.0, value))
        merged = {"value": v, **props}
        return UIElement(kind="DpgProgressBar", props=merged)

    def tab_stack(self, **props: Any) -> UIElement:
        return UIElement(kind="DpgTabBar", props=dict(props))

    def radio_button(self, *, text: str = "", checked: bool = False, **props: Any) -> UIElement:
        merged: dict[str, Any] = {**props}
        if text:
            merged["label"] = text
            merged["items"] = (text,)
            merged["value"] = text if checked else ""
        else:
            merged.setdefault("items", ())
            merged.setdefault("value", "")
        return UIElement(kind="DpgRadioButton", props=merged)

    def text_area(self, *, text: str = "", read_only: bool = False, **props: Any) -> UIElement:
        merged: dict[str, Any] = {
            "value": text,
            "multiline": True,
            "readonly": read_only,
            **props,
        }
        return UIElement(kind="DpgInputText", props=merged)

    def static_text(self, *, text: str = "", **props: Any) -> UIElement:
        merged: dict[str, Any] = {"default_value": text, **props}
        return UIElement(kind="DpgText", props=merged)

    def menu_bar(self, **props: Any) -> UIElement:
        return UIElement(kind="DpgMenuBar", props=dict(props))

    def tool_bar(self, *, title: str = "", **props: Any) -> UIElement:
        merged: dict[str, Any] = {"horizontal": True, **props}
        if title:
            merged["label"] = title
        return UIElement(kind="DpgGroup", props=merged)

    def separator(self, *, horizontal: bool = True, **props: Any) -> UIElement:
        _ = horizontal
        return UIElement(kind="DpgSeparator", props=dict(props))

    def scroll_panel(self, **props: Any) -> UIElement:
        merged: dict[str, Any] = {
            "width": 240,
            "height": 180,
            "horizontal_scrollbar": True,
            "no_scrollbar": False,
            **props,
        }
        return UIElement(kind="DpgChildWindow", props=merged)

    def spacer(self, *, width: int = 0, height: int = 0, **props: Any) -> UIElement:
        merged: dict[str, Any] = {"width": width, "height": height, **props}
        return UIElement(kind="DpgSpacer", props=merged)
