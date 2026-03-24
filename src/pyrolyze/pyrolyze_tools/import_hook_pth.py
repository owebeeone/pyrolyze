"""Install or remove ``pyrolyze_import_hook.pth`` in the active environment's purelib."""

from __future__ import annotations

import argparse
import sys
import sysconfig
from pathlib import Path

PTH_FILENAME = "pyrolyze_import_hook.pth"
PTH_LINE = "import pyrolyze.import_hook; pyrolyze.import_hook.install_startup_import_hook()\n"


def _purelib() -> Path:
    return Path(sysconfig.get_paths()["purelib"])


def _require_venv() -> None:
    if sys.prefix == sys.base_prefix and not hasattr(sys, "real_prefix"):
        print(
            "pyrolyze-import-hook-pth: no virtual environment detected "
            "(sys.prefix == sys.base_prefix). Activate a venv or use uv run.",
            file=sys.stderr,
        )
        sys.exit(1)


def install_pth() -> int:
    _require_venv()
    purelib = _purelib()
    purelib.mkdir(parents=True, exist_ok=True)
    path = purelib / PTH_FILENAME
    path.write_text(PTH_LINE, encoding="utf-8")
    print(f"Wrote {path}")
    return 0


def remove_pth() -> int:
    _require_venv()
    path = _purelib() / PTH_FILENAME
    if not path.is_file():
        print(f"Nothing to remove ({path} missing)", file=sys.stderr)
        return 1
    path.unlink()
    print(f"Removed {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Manage pyrolyze_import_hook.pth (venv import hook for #@pyrolyze modules).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("install", help=f"Write {PTH_FILENAME} under site-packages purelib.")
    sub.add_parser("remove", help=f"Delete {PTH_FILENAME} from site-packages purelib.")

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if args.command == "install":
        return install_pth()
    if args.command == "remove":
        return remove_pth()
    raise AssertionError(args.command)


def main_cli() -> None:
    """Setuptools ``pyrolyze-import-hook-pth`` entry point."""

    raise SystemExit(main())


if __name__ == "__main__":
    raise SystemExit(main())
