from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from pyrolyze.runtime import RenderContext

from Studio.host import app_host


SOURCE_PATH = app_host.SOURCE_PATH


def _ensure_repo_root_on_syspath() -> Path:
    return app_host._ensure_repo_root_on_syspath()


def build_parser() -> argparse.ArgumentParser:
    return app_host.build_parser()


def _load_component() -> Any:
    return app_host._load_component()


def build_host(root_path: str) -> tuple[Any, RenderContext]:
    return app_host.build_host(root_path)


def main(argv: list[str] | None = None) -> int:
    return app_host.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())

