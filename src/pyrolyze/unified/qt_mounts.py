"""PySide6 ``mounts.*`` selectors for :mod:`pyrolyze.unified.mount_keys` strings.

Use with :func:`pyrolyze.api.advertise_mount` ``target=`` when wiring shell-shaped
trees. See ``dev-docs/MountKeys.md`` and ``dev-docs/ReferenceShellLayout.md``.

Tk / DPG mappings stay toolkit-specific (often ``MountSelector.named(...)`` in
bootstrap); this module is **Qt-only**.
"""

from __future__ import annotations

from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary
from pyrolyze.unified import mount_keys as mk

_m = PySide6UiLibrary.mounts

#: Every constant in :mod:`pyrolyze.unified.mount_keys` → typical Qt mount selector.
QT_MOUNT_TARGET_BY_KEY: dict[str, object] = {
    mk.SHELL_BODY: _m.central_widget,
    mk.SHELL_MENU_BAR: _m.menu_bar,
    mk.SHELL_STATUS: _m.status_bar,
    mk.SHELL_CHROME: _m.title_bar_widget,
    mk.DIALOG_CONTENT: _m.layout,
    mk.DIALOG_ACTIONS: _m.layout,
}


def qt_mount_target(key: str) -> object:
    """Return the PySide6 :class:`~pyrolyze.api.MountSelector` for ``key``."""
    try:
        return QT_MOUNT_TARGET_BY_KEY[key]
    except KeyError as exc:
        known = ", ".join(sorted(QT_MOUNT_TARGET_BY_KEY))
        msg = f"unknown mount key {key!r} for Qt (known: {known})"
        raise KeyError(msg) from exc


__all__ = ["QT_MOUNT_TARGET_BY_KEY", "qt_mount_target"]
