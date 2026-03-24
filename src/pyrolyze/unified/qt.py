"""Qt / PySide6 unified native adapter.

Portable control methods (:meth:`QtUnifiedNativeLibrary.push_button`, …) build
``UIElement`` values for ``call_native``.

Structural PyRolyze containers still use generated ``CQ*`` helpers. Those are
re-attached here (same objects as :class:`~pyrolyze.backends.pyside6.generated_library.PySide6UiLibrary`)
so authors can write ``with QtUx.CQMainWindow():`` and ``mount(QtUx.mounts.…)``
without a separate ``PySide6UiLibrary`` import. :data:`QtUx` is an alias of
:class:`QtUnifiedNativeLibrary` for shorter qualified names at compile time.
"""

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

    def toggle(self, *, checked: bool = False, text: str = "", **props: Any) -> UIElement:
        merged = {"text": text, "checked": checked, **props}
        return UIElement(kind="QCheckBox", props=merged)

    def text_field(self, *, text: str = "", **props: Any) -> UIElement:
        merged = {"text": text, **props}
        return UIElement(kind="QLineEdit", props=merged)

    def int_field(
        self,
        *,
        value: int = 0,
        min_value: int | None = None,
        max_value: int | None = None,
        step: int = 1,
        **props: Any,
    ) -> UIElement:
        merged: dict[str, Any] = {"value": value, "singleStep": step, **props}
        if min_value is not None:
            merged["minimum"] = min_value
        if max_value is not None:
            merged["maximum"] = max_value
        return UIElement(kind="QSpinBox", props=merged)

    def float_field(
        self,
        *,
        value: float = 0.0,
        min_value: float | None = None,
        max_value: float | None = None,
        step: float = 0.1,
        **props: Any,
    ) -> UIElement:
        merged: dict[str, Any] = {"value": value, "singleStep": step, **props}
        if min_value is not None:
            merged["minimum"] = min_value
        if max_value is not None:
            merged["maximum"] = max_value
        return UIElement(kind="QDoubleSpinBox", props=merged)

    def combo_box(
        self,
        *,
        items: tuple[str, ...] = (),
        current_index: int = 0,
        **props: Any,
    ) -> UIElement:
        merged: dict[str, Any] = {"items": list(items), "currentIndex": current_index, **props}
        return UIElement(kind="QComboBox", props=merged)

    def slider(
        self,
        *,
        value: int = 0,
        min_value: int = 0,
        max_value: int = 100,
        **props: Any,
    ) -> UIElement:
        merged: dict[str, Any] = {
            "minimum": min_value,
            "maximum": max_value,
            "value": value,
            "orientation": "Horizontal",
            **props,
        }
        return UIElement(kind="QSlider", props=merged)

    def progress(self, *, value: float = 0.0, **props: Any) -> UIElement:
        v = max(0.0, min(1.0, value))
        merged = {"maximum": 100, "value": int(round(v * 100)), **props}
        return UIElement(kind="QProgressBar", props=merged)

    def tab_stack(self, **props: Any) -> UIElement:
        return UIElement(kind="QTabWidget", props=dict(props))

    def radio_button(self, *, text: str = "", checked: bool = False, **props: Any) -> UIElement:
        merged = {"text": text, "checked": checked, **props}
        return UIElement(kind="QRadioButton", props=merged)

    def text_area(self, *, text: str = "", read_only: bool = False, **props: Any) -> UIElement:
        merged: dict[str, Any] = {"plainText": text, "readOnly": read_only, **props}
        return UIElement(kind="QPlainTextEdit", props=merged)

    def static_text(self, *, text: str = "", **props: Any) -> UIElement:
        merged = {"text": text, **props}
        return UIElement(kind="QLabel", props=merged)

    def menu_bar(self, **props: Any) -> UIElement:
        return UIElement(kind="QMenuBar", props=dict(props))

    def tool_bar(self, *, title: str = "", **props: Any) -> UIElement:
        merged = {"title": title, **props}
        return UIElement(kind="QToolBar", props=merged)

    def separator(self, *, horizontal: bool = True, **props: Any) -> UIElement:
        shape = "HLine" if horizontal else "VLine"
        merged: dict[str, Any] = {"frameShape": shape, "frameShadow": "Sunken", **props}
        return UIElement(kind="QFrame", props=merged)

    def scroll_panel(self, **props: Any) -> UIElement:
        merged: dict[str, Any] = {"widgetResizable": True, **props}
        return UIElement(kind="QScrollArea", props=merged)

    def spacer(self, *, width: int = 0, height: int = 0, **props: Any) -> UIElement:
        merged: dict[str, Any] = dict(props)
        if width > 0:
            merged.setdefault("minimumWidth", width)
            merged.setdefault("maximumWidth", width)
        if height > 0:
            merged.setdefault("minimumHeight", height)
            merged.setdefault("maximumHeight", height)
        return UIElement(kind="QWidget", props=merged)


def _register_structural_component_refs(cls: type[QtUnifiedNativeLibrary]) -> None:
    """Attach generated ``PySide6UiLibrary`` ``with CQ*`` helpers to the unified class.

    The PyRolyze compiler treats ``with Some.CQMainWindow():`` as a native
    container when ``Some`` is an imported class whose ``UI_INTERFACE`` lists
    ``CQMainWindow``. Reusing the same component refs here lets authors write
    ``with QtUx.CQMainWindow():`` alongside :meth:`QtUnifiedNativeLibrary.push_button`
    without importing ``PySide6UiLibrary`` separately.
    """

    native = PySide6UiLibrary
    cls.UI_INTERFACE = native.UI_INTERFACE.bind_owner(cls)
    cls.mounts = native.mounts
    for public_name in native.UI_INTERFACE.entries:
        setattr(cls, public_name, getattr(native, public_name))


_register_structural_component_refs(QtUnifiedNativeLibrary)

# Short import name so qualified calls are ``QtUx.CQMainWindow`` (registered at compile time).
QtUx = QtUnifiedNativeLibrary

__all__ = ["QtUnifiedNativeLibrary", "QtUx"]
