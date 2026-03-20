from __future__ import annotations

import sys
from pathlib import Path

from Studio import run_studio_poc


def test_ensure_repo_root_on_syspath_inserts_expected_path(monkeypatch) -> None:
    repo_root = Path(run_studio_poc.__file__).resolve().parent.parent
    root_str = str(repo_root)
    trimmed = [value for value in sys.path if value != root_str]
    monkeypatch.setattr(sys, "path", trimmed)

    returned = run_studio_poc._ensure_repo_root_on_syspath()

    assert returned == repo_root
    assert sys.path[0] == root_str


def test_ensure_repo_root_on_syspath_is_idempotent(monkeypatch) -> None:
    repo_root = Path(run_studio_poc.__file__).resolve().parent.parent
    root_str = str(repo_root)
    monkeypatch.setattr(sys, "path", [root_str, "C:\\tmp", "C:\\tmp2"])

    run_studio_poc._ensure_repo_root_on_syspath()

    assert sys.path.count(root_str) == 1
