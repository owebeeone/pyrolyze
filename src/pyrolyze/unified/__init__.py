"""Unified native UI facade (Qt, Tkinter, Dear PyGui) with runtime backend selection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import mount_keys
from pyrolyze.unified._constants import (
    DEFAULT_UNIFIED_BACKEND,
    PYROLYZE_UNIFIED_BACKEND_ENV,
    UNIFIED_NATIVE_API_VERSION,
)
from pyrolyze.unified.base import UnifiedNativeLibrary

if TYPE_CHECKING:
    from pyrolyze.unified.dpg import DpgUnifiedNativeLibrary
    from pyrolyze.unified.qt import QtUnifiedNativeLibrary
    from pyrolyze.unified.tk import TkUnifiedNativeLibrary

__all__ = [
    "DEFAULT_UNIFIED_BACKEND",
    "DpgUnifiedNativeLibrary",
    "PYROLYZE_UNIFIED_BACKEND_ENV",
    "QtUx",
    "QtUnifiedNativeLibrary",
    "TkUnifiedNativeLibrary",
    "UNIFIED_NATIVE_API_VERSION",
    "UnifiedNativeLibrary",
    "context_keys",
    "get_unified_native_library",
    "mount_keys",
]


def __getattr__(name: str) -> Any:
    if name == "DpgUnifiedNativeLibrary":
        from pyrolyze.unified.dpg import DpgUnifiedNativeLibrary

        return DpgUnifiedNativeLibrary
    if name == "QtUnifiedNativeLibrary":
        from pyrolyze.unified.qt import QtUnifiedNativeLibrary

        return QtUnifiedNativeLibrary
    if name == "QtUx":
        from pyrolyze.unified.qt import QtUx

        return QtUx
    if name == "TkUnifiedNativeLibrary":
        from pyrolyze.unified.tk import TkUnifiedNativeLibrary

        return TkUnifiedNativeLibrary
    if name == "get_unified_native_library":
        from pyrolyze.unified.factory import get_unified_native_library

        return get_unified_native_library
    if name == "context_keys":
        from pyrolyze.unified import context_keys as context_keys_module

        return context_keys_module
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
