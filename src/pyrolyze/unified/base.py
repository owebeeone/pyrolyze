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

    @abstractmethod
    def push_button(self, *, text: str = "", **props: Any) -> UIElement:
        """Primary click target; maps to toolkit-specific kind and props."""

    def label(self, *, text: str) -> UIElement:
        """Shared helper; same ``UIElement`` shape on every backend."""
        return Label(text=text)
