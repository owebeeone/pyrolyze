"""DearPyGui backend package."""

from __future__ import annotations

import pyrolyze.backends.dearpygui.author_ui as _author_ui  # noqa: F401 — attaches ``DearPyGuiUiLibrary.C``
from pyrolyze.backends.dearpygui.generated_library import DearPyGuiUiLibrary

__all__ = ("DearPyGuiUiLibrary",)
