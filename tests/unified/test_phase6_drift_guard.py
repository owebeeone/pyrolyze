"""Phase 6.3: guard against reintroducing removed ``backends/common`` imports."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_phase6_no_forbidden_backend_common_references() -> None:
    repo = Path(__file__).resolve().parents[2]
    script = repo / "scripts" / "check_unified_drift.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout or "(no output)"
