"""Resolve ``UnifiedNativeLibrary`` from env var or explicit backend id."""

from __future__ import annotations

import os

from pyrolyze.unified._constants import (
    DEFAULT_UNIFIED_BACKEND,
    PYROLYZE_UNIFIED_BACKEND_ENV,
)
from pyrolyze.unified.base import UnifiedNativeLibrary
from pyrolyze.unified.dpg import DpgUnifiedNativeLibrary
from pyrolyze.unified.qt import QtUnifiedNativeLibrary
from pyrolyze.unified.tk import TkUnifiedNativeLibrary

_REGISTRY: dict[str, type[UnifiedNativeLibrary]] = {
    "qt": QtUnifiedNativeLibrary,
    "tk": TkUnifiedNativeLibrary,
    "dpg": DpgUnifiedNativeLibrary,
}


def _normalize_backend_key(raw: str) -> str:
    return raw.strip().lower()


def get_unified_native_library(*, backend: str | None = None) -> UnifiedNativeLibrary:
    """Return the unified library for the given or configured backend.

    Reads :data:`PYROLYZE_UNIFIED_BACKEND_ENV` when ``backend`` is omitted.
    Default is :data:`DEFAULT_UNIFIED_BACKEND` (``qt``).
    """
    if backend is not None:
        key = _normalize_backend_key(backend)
    else:
        raw = os.environ.get(PYROLYZE_UNIFIED_BACKEND_ENV, DEFAULT_UNIFIED_BACKEND)
        key = _normalize_backend_key(raw)

    cls = _REGISTRY.get(key)
    if cls is None:
        known = ", ".join(sorted(_REGISTRY))
        msg = f"unknown unified backend {key!r} (expected one of: {known})"
        raise ValueError(msg)

    return cls()
