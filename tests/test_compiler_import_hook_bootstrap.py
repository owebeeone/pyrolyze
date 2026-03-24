"""Compiler meta-path hook is registered when the ``pyrolyze`` package loads (no ``.pth`` required)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_subprocess_import_generated_library_without_pth_via_dash_c() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src = repo_root / "src"
    code = f"""
import sys
sys.path.insert(0, {str(src)!r})
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary
assert PySide6UiLibrary.__name__ == "PySide6UiLibrary"
print("ok")
"""
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_subprocess_run_py_script(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src = repo_root / "src"
    script = tmp_path / "use_generated.py"
    script.write_text(
        f"""import sys
sys.path.insert(0, {str(src)!r})
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary
assert PySide6UiLibrary.__name__ == "PySide6UiLibrary"
print("ok")
""",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "ok" in proc.stdout
