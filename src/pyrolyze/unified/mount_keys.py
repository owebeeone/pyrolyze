"""Canonical mount key strings for shell / dialog composition (Phase 2).

Map these in author code to ``advertise_mount`` / ``mount``. Per-backend
selector attachment and a reference shell tree diagram live in
``dev-docs/ReferenceShellLayout.md``; ``dev-docs/MountKeys.md`` is the compact
key table.
"""

from __future__ import annotations

# Shell regions (string keys; stable across backends when adverts agree).
SHELL_BODY = "shell.body"
SHELL_CHROME = "shell.chrome"
SHELL_MENU_BAR = "shell.menu_bar"
SHELL_STATUS = "shell.status"

# Dialog regions
DIALOG_ACTIONS = "dialog.actions"
DIALOG_CONTENT = "dialog.content"

__all__ = [
    "DIALOG_ACTIONS",
    "DIALOG_CONTENT",
    "SHELL_BODY",
    "SHELL_CHROME",
    "SHELL_MENU_BAR",
    "SHELL_STATUS",
]
