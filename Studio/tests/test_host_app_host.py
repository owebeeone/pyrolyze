from __future__ import annotations

import sys
from pathlib import Path

from Studio.host import app_host


def test_ensure_repo_root_on_syspath_inserts_root_once(monkeypatch) -> None:
    root_str = str(app_host.SOURCE_PATH.parent.parent.parent.resolve())
    monkeypatch.setattr(sys, "path", [root_str, "C:\\tmp", "C:\\tmp2"])

    app_host._ensure_repo_root_on_syspath()

    assert sys.path.count(root_str) == 1


def test_ensure_repo_root_on_syspath_inserts_when_missing(monkeypatch) -> None:
    root_str = str(app_host.SOURCE_PATH.parent.parent.parent.resolve())
    monkeypatch.setattr(sys, "path", ["C:\\tmp", "C:\\tmp2"])

    returned = app_host._ensure_repo_root_on_syspath()

    assert returned == Path(root_str)
    assert sys.path[0] == root_str


def test_source_path_points_to_ui_studio_root() -> None:
    assert app_host.SOURCE_PATH.name == "studio_root.py"
    assert app_host.SOURCE_PATH.parent.name == "ui"
    assert app_host.SOURCE_PATH.exists()


def test_build_parser_supports_root_and_smoke_flags() -> None:
    parser = app_host.build_parser()

    parsed = parser.parse_args(["--root", "C:\\x", "--smoke"])

    assert parsed.root == "C:\\x"
    assert parsed.smoke is True
