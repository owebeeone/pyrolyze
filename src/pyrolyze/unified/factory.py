"""Resolve ``UnifiedNativeLibrary`` from env var or explicit backend id."""

from __future__ import annotations

import os

from pyrolyze.unified._constants import (
    DEFAULT_UNIFIED_BACKEND,
    PYROLYZE_UNIFIED_BACKEND_ENV,
)
from pyrolyze.unified.base import UnifiedNativeLibrary


def _normalize_backend_key(raw: str) -> str:
    return raw.strip().lower()


def get_unified_native_library(*, backend: str | None = None) -> UnifiedNativeLibrary:
    """Return the unified library for the given or configured backend.

    Reads :data:`PYROLYZE_UNIFIED_BACKEND_ENV` when ``backend`` is omitted.
    Default is :data:`DEFAULT_UNIFIED_BACKEND` (``qt``).

    Imports only the selected backend implementation (avoids loading PySide6
    when only Tk/DPG is needed).
    """
    if backend is not None:
        key = _normalize_backend_key(backend)
    else:
        raw = os.environ.get(PYROLYZE_UNIFIED_BACKEND_ENV, DEFAULT_UNIFIED_BACKEND)
        key = _normalize_backend_key(raw)

    if key == "qt":
        from pyrolyze.unified.qt import QtUnifiedNativeLibrary

        return QtUnifiedNativeLibrary()
    if key == "tk":
        from pyrolyze.unified.tk import TkUnifiedNativeLibrary

        return TkUnifiedNativeLibrary()
    if key == "dpg":
        from pyrolyze.unified.dpg import DpgUnifiedNativeLibrary

        return DpgUnifiedNativeLibrary()

    known = "dpg, qt, tk"
    msg = f"unknown unified backend {key!r} (expected one of: {known})"
    raise ValueError(msg)
