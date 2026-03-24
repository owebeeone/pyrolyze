"""Backward-compatible entry: ``pyrolyze-install-import-hook`` → install only."""

from __future__ import annotations

import sys

from pyrolyze.pyrolyze_tools.import_hook_pth import install_pth


def main() -> None:
    raise SystemExit(install_pth())
