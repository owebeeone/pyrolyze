"""Compatibility shim for the canonical PyRolyze import hook.

The single real implementation lives in :mod:`pyrolyze.import_hook`. This
module remains as a stable import location for pytest/plugin/bootstrap code and
older tests that still import from ``pyrolyze.compiler.import_hook``.
"""

from __future__ import annotations

from .. import import_hook as _canonical

_raw_source_has_pyrolyze_marker = _canonical._raw_source_has_pyrolyze_marker
PyrolyzeLoader = _canonical.PyrolyzeLoader
PyrolyzeMetaPathFinder = _canonical.PyrolyzeMetaPathFinder


def install() -> None:
    """Install the canonical finder unconditionally for pytest/startup paths."""

    _canonical.install_startup_import_hook()


def uninstall() -> None:
    """Remove the canonical finder used by compatibility entrypoints."""

    _canonical.uninstall_startup_import_hook()
__all__ = [
    "PyrolyzeLoader",
    "PyrolyzeMetaPathFinder",
    "_raw_source_has_pyrolyze_marker",
    "install",
    "uninstall",
]
