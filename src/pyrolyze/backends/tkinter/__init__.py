"""tkinter backend package."""

from typing import Any

from .generated_library import TkinterUiLibrary


def __getattr__(name: str) -> Any:
    if name == "LEARNINGS":
        from .learnings import LEARNINGS

        globals()[name] = LEARNINGS
        return LEARNINGS
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["LEARNINGS", "TkinterUiLibrary"]
