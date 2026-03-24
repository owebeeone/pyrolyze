"""Shared fixtures for unified backend tests (Phase 5 smokes + mount routing)."""

from __future__ import annotations

import sys
from collections.abc import Generator
from typing import Any

import pytest


def _skip_tk_mount_on_darwin() -> None:
    """Tk main window + PySide6 (or other GUI stacks) in one process aborts on macOS."""
    if sys.platform == "darwin":
        pytest.skip(
            "macOS: Tk MountableEngine tests are skipped in-process after other GUI stacks load; "
            "Linux CI runs them (Phase 5.4)."
        )


@pytest.fixture(scope="session")
def qapplication() -> Any:
    """Single Qt app for headless widget construction (MountableEngine + PySide6)."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def tk_root() -> Generator[Any, None, None]:
    """Hidden Tk root for Tkinter MountableEngine tests."""
    _skip_tk_mount_on_darwin()
    import tkinter as tk

    root = tk.Tk()
    root.withdraw()
    try:
        yield root
    finally:
        root.destroy()


@pytest.fixture
def recording_dpg_host() -> Generator[Any, None, None]:
    """In-memory DearPyGui host for mount tests without a live viewport."""
    from pyrolyze.backends.dearpygui.host import RecordingDpgHost, dpg_host_reset, dpg_host_token

    host = RecordingDpgHost()
    token = dpg_host_token(host)
    try:
        yield host
    finally:
        dpg_host_reset(token)
