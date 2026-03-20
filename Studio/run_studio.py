from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

_THIS_FILE = Path(__file__).resolve()
_REPO_ROOT = _THIS_FILE.parent.parent.resolve()
_SRC_ROOT = _REPO_ROOT / "src"


def _bootstrap_local_import_paths() -> Path:
    repo_str = str(_REPO_ROOT)
    src_str = str(_SRC_ROOT)

    while src_str in sys.path:
        sys.path.remove(src_str)
    while repo_str in sys.path:
        sys.path.remove(repo_str)

    sys.path.insert(0, src_str)
    sys.path.insert(0, repo_str)
    return _REPO_ROOT


_bootstrap_local_import_paths()

from Studio.host import app_host

if TYPE_CHECKING:
    from pyrolyze.runtime import RenderContext


SOURCE_PATH = app_host.SOURCE_PATH


def _ensure_repo_root_on_syspath() -> Path:
    return app_host._ensure_repo_root_on_syspath()


def build_parser() -> argparse.ArgumentParser:
    return app_host.build_parser()


def _load_component() -> Any:
    return app_host._load_component()


def build_host(root_path: str) -> tuple[Any, "RenderContext"]:
    return app_host.build_host(root_path)


def main(argv: list[str] | None = None) -> int:
    return app_host.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
