"""Unified native UI facade (Qt, Tkinter, Dear PyGui) with runtime backend selection."""

from __future__ import annotations

from pyrolyze.unified._constants import DEFAULT_UNIFIED_BACKEND, PYROLYZE_UNIFIED_BACKEND_ENV
from pyrolyze.unified.base import UnifiedNativeLibrary
from pyrolyze.unified.dpg import DpgUnifiedNativeLibrary
from pyrolyze.unified.factory import get_unified_native_library
from pyrolyze.unified.qt import QtUnifiedNativeLibrary
from pyrolyze.unified.tk import TkUnifiedNativeLibrary

__all__ = [
    "DEFAULT_UNIFIED_BACKEND",
    "DpgUnifiedNativeLibrary",
    "PYROLYZE_UNIFIED_BACKEND_ENV",
    "QtUnifiedNativeLibrary",
    "TkUnifiedNativeLibrary",
    "UnifiedNativeLibrary",
    "get_unified_native_library",
]
