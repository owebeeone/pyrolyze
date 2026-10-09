from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest


def test_tkinter_generated_history_and_rollback_fuzz() -> None:
    # Tk and Qt cannot safely share a GUI process on macOS.
    worker = Path(__file__).with_name("tkinter_host_surface_fuzz_worker.py")
    result = subprocess.run(
        [sys.executable, str(worker)],
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if result.returncode == 77:
        pytest.skip(result.stdout.strip())
    assert result.returncode == 0, result.stdout + result.stderr
    print(result.stdout)
