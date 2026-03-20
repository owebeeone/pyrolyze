from __future__ import annotations

import sys
from pathlib import Path

from Studio import run_studio


def test_source_path_matches_host_app_host() -> None:
    assert run_studio.SOURCE_PATH == run_studio.app_host.SOURCE_PATH


def test_ensure_repo_root_on_syspath_inserts_expected_path(monkeypatch) -> None:
    repo_root = Path(run_studio.__file__).resolve().parent.parent
    root_str = str(repo_root)
    src_str = str(repo_root / "src")
    trimmed = [value for value in sys.path if value not in {root_str, src_str}]
    monkeypatch.setattr(sys, "path", trimmed)

    returned = run_studio._ensure_repo_root_on_syspath()

    assert returned == repo_root
    assert sys.path[0] == root_str
    assert sys.path[1] == src_str


def test_ensure_repo_root_on_syspath_is_idempotent(monkeypatch) -> None:
    repo_root = Path(run_studio.__file__).resolve().parent.parent
    root_str = str(repo_root)
    src_str = str(repo_root / "src")
    monkeypatch.setattr(sys, "path", [root_str, src_str, "C:\\tmp", "C:\\tmp2"])

    run_studio._ensure_repo_root_on_syspath()

    assert sys.path.count(root_str) == 1
    assert sys.path.count(src_str) == 1
    assert sys.path[0] == root_str
    assert sys.path[1] == src_str


def test_build_parser_supports_root_and_smoke_flags() -> None:
    parser = run_studio.build_parser()

    parsed = parser.parse_args(["--root", "C:\\x", "--smoke"])

    assert parsed.root == "C:\\x"
    assert parsed.smoke is True
