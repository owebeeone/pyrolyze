"""PySide6 backend package."""

from .engine import MountedWidgetNode, PySide6WidgetEngine, WidgetNodeKey
from .generated_library import PySide6UiLibrary
from typing import Any

__all__ = ["LEARNINGS", "MountedWidgetNode", "PySide6UiLibrary", "PySide6WidgetEngine", "WidgetNodeKey"]


def __getattr__(name: str) -> Any:
    if name == "LEARNINGS":
        from .learnings import LEARNINGS

        globals()[name] = LEARNINGS
        return LEARNINGS
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
