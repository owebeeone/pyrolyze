"""Canonical :class:`AppContextKey` objects for unified + mount-key authoring.

Use with ``app_context_override[...]`` / ``use_app_context`` so subtree widgets
(including values passed into :class:`~pyrolyze.unified.base.UnifiedNativeLibrary`
emitters) can follow theme, density, and typography without ad hoc string keys.

Mount resolution still does **not** read app context (see
``dev-docs/HierarchicalContextManagementPlan.md``); authors **read** keys in
components and map them into ``UIElement`` props or unified method arguments.
"""

from __future__ import annotations

from pyrolyze.runtime import AppContextKey

# Stable string ids for debugging / cross-process contracts (e.g. GRIP later).
UNIFIED_THEME = AppContextKey("unified.theme", factory=lambda _host: "light")

UNIFIED_DENSITY = AppContextKey("unified.density", factory=lambda _host: "comfortable")

UNIFIED_TYPOGRAPHY = AppContextKey("unified.typography", factory=lambda _host: "default")

__all__ = [
    "UNIFIED_DENSITY",
    "UNIFIED_THEME",
    "UNIFIED_TYPOGRAPHY",
]
