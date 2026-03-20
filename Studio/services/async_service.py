from __future__ import annotations

from collections.abc import Callable


def run_on_ui_flush(callback: Callable[[], None]) -> None:
    callback()
