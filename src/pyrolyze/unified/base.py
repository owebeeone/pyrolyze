"""Abstract unified native facade (one implementation per toolkit)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pyrolyze.api import Label, UIElement


class UnifiedNativeLibrary(ABC):
    """Stable author surface; swap concrete subclass for Qt / Tk / Dear PyGui."""

    @property
    @abstractmethod
    def backend_id(self) -> str:
        """Short id: ``qt``, ``tk``, ``dpg``."""

    @property
    @abstractmethod
    def native_library_type(self) -> type[Any]:
        """Generated ``*UiLibrary`` class for this backend (for advanced use)."""

    @property
    def mounts(self) -> Any:
        """Mount selector namespace from the generated ``*UiLibrary``, or ``None`` if absent."""
        return getattr(self.native_library_type, "mounts", None)

    @abstractmethod
    def push_button(self, *, text: str = "", **props: Any) -> UIElement:
        """Primary click target; maps to toolkit-specific kind and props."""

    @abstractmethod
    def toggle(self, *, checked: bool = False, text: str = "", **props: Any) -> UIElement:
        """Boolean control (checkbox semantics)."""

    @abstractmethod
    def text_field(self, *, text: str = "", **props: Any) -> UIElement:
        """Single-line text entry; ``text`` is the initial / bound value string."""

    @abstractmethod
    def int_field(
        self,
        *,
        value: int = 0,
        min_value: int | None = None,
        max_value: int | None = None,
        step: int = 1,
        **props: Any,
    ) -> UIElement:
        """Integer numeric entry (spin / stepper semantics)."""

    @abstractmethod
    def float_field(
        self,
        *,
        value: float = 0.0,
        min_value: float | None = None,
        max_value: float | None = None,
        step: float = 0.1,
        **props: Any,
    ) -> UIElement:
        """Floating-point numeric entry."""

    @abstractmethod
    def combo_box(
        self,
        *,
        items: tuple[str, ...] = (),
        current_index: int = 0,
        **props: Any,
    ) -> UIElement:
        """Discrete choice from a list; ``current_index`` selects the initial item."""

    @abstractmethod
    def slider(
        self,
        *,
        value: int = 0,
        min_value: int = 0,
        max_value: int = 100,
        **props: Any,
    ) -> UIElement:
        """Bounded integer range control (best-effort orientation: horizontal)."""

    @abstractmethod
    def progress(self, *, value: float = 0.0, **props: Any) -> UIElement:
        """Determinate progress; ``value`` is **0.0..1.0** (adapters map per toolkit)."""

    @abstractmethod
    def tab_stack(self, **props: Any) -> UIElement:
        """Tab container shell; children mount per PyRolyze tree (subset on DPG: tab bar)."""

    @abstractmethod
    def radio_button(self, *, text: str = "", checked: bool = False, **props: Any) -> UIElement:
        """Single radio option; grouping uses toolkit variables / DPG ``items`` + ``value``."""

    @abstractmethod
    def text_area(self, *, text: str = "", read_only: bool = False, **props: Any) -> UIElement:
        """Multiline plain text (not rich text); best-effort read-only mapping."""

    @abstractmethod
    def static_text(self, *, text: str = "", **props: Any) -> UIElement:
        """Non-interactive native text line (DPG uses ``DpgText`` / ``default_value``, not shared ``Label``)."""

    @abstractmethod
    def menu_bar(self, **props: Any) -> UIElement:
        """Empty menu bar shell; children attach per toolkit."""

    @abstractmethod
    def tool_bar(self, *, title: str = "", **props: Any) -> UIElement:
        """Toolbar / action row host (DPG: horizontal ``DpgGroup``)."""

    @abstractmethod
    def separator(self, *, horizontal: bool = True, **props: Any) -> UIElement:
        """Visual rule between controls (orientation follows ``horizontal``)."""

    @abstractmethod
    def scroll_panel(self, **props: Any) -> UIElement:
        """Scrollable child viewport (Tk: ``Canvas`` best-effort; DPG: ``DpgChildWindow`` with scrollbars)."""

    @abstractmethod
    def spacer(self, *, width: int = 0, height: int = 0, **props: Any) -> UIElement:
        """Fixed layout gap; zero dimensions mean toolkit default minimum."""

    def label(self, *, text: str) -> UIElement:
        """Shared helper; same ``UIElement`` shape on every backend."""
        return Label(text=text)
