#!/usr/bin/env python3
"""Invalidate PyRolyze import-hook caches.

Run from the ``pyrolyze`` repository root::

    uv run python scripts/invalidate_import_hook_cache.py module examples/grid_app.py
    uv run python scripts/invalidate_import_hook_cache.py transformer
    uv run python scripts/invalidate_import_hook_cache.py all --module examples/grid_app.py

This utility supports three practical cases:

- cold-import one ``#@pyrolyze`` module by removing its sibling ``__pycache__``
- invalidate the transformer fingerprint by touching a compiler file
- remove the optional persistent artifact cache directory
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRANSFORMER_TOUCH = Path("src/pyrolyze/compiler/kernel_loader.py")
DEFAULT_PERSISTENT_CACHE = Path(".pyrolyze_cache")


@dataclass(frozen=True)
class InvalidateResult:
    action: str
    path: Path
    detail: str


def _resolve_repo_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def remove_module_pycache(module_path: Path) -> list[InvalidateResult]:
    results: list[InvalidateResult] = []
    pycache_dir = module_path.parent / "__pycache__"
    if not pycache_dir.is_dir():
        results.append(
            InvalidateResult("skip", pycache_dir, "no sibling __pycache__ directory"),
        )
        return results

    stem = module_path.stem
    removed = 0
    for entry in pycache_dir.iterdir():
        if entry.is_file() and entry.name.startswith(stem + "."):
            entry.unlink()
            removed += 1
            results.append(
                InvalidateResult("remove", entry, "removed module bytecode cache"),
            )

    if removed == 0:
        results.append(
            InvalidateResult("skip", pycache_dir, f"no cached entries matching {stem!r}"),
        )
    return results


def touch_file(path: Path) -> InvalidateResult:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        raise FileNotFoundError(path)
    now = time.time() + 1.0
    os.utime(path, (now, now))
    return InvalidateResult("touch", path, "updated mtime")


def remove_persistent_cache(cache_dir: Path) -> InvalidateResult:
    if not cache_dir.exists():
        return InvalidateResult("skip", cache_dir, "persistent cache directory missing")
    shutil.rmtree(cache_dir)
    return InvalidateResult("remove", cache_dir, "removed persistent cache directory")


def _cmd_module(args: argparse.Namespace) -> int:
    module_path = _resolve_repo_path(args.module)
    if not module_path.is_file():
        print(f"Missing module file: {module_path}", file=sys.stderr)
        return 1

    results = remove_module_pycache(module_path)
    if args.touch_source:
        results.append(touch_file(module_path))
    _print_results(results)
    return 0


def _cmd_transformer(args: argparse.Namespace) -> int:
    touch_path = _resolve_repo_path(args.touch_file)
    if not touch_path.is_file():
        print(f"Missing transformer file: {touch_path}", file=sys.stderr)
        return 1
    _print_results([touch_file(touch_path)])
    return 0


def _cmd_all(args: argparse.Namespace) -> int:
    results: list[InvalidateResult] = []
    if args.module is not None:
        module_path = _resolve_repo_path(args.module)
        if not module_path.is_file():
            print(f"Missing module file: {module_path}", file=sys.stderr)
            return 1
        results.extend(remove_module_pycache(module_path))
        if args.touch_source:
            results.append(touch_file(module_path))

    transformer_path = _resolve_repo_path(args.touch_file)
    if not transformer_path.is_file():
        print(f"Missing transformer file: {transformer_path}", file=sys.stderr)
        return 1
    results.append(touch_file(transformer_path))

    if args.clear_persistent_cache:
        cache_dir = _resolve_repo_path(args.cache_dir)
        results.append(remove_persistent_cache(cache_dir))

    _print_results(results)
    return 0


def _print_results(results: list[InvalidateResult]) -> None:
    for result in results:
        try:
            shown = result.path.relative_to(REPO_ROOT)
        except ValueError:
            shown = result.path
        print(f"{result.action:>6}  {shown}  {result.detail}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Invalidate PyRolyze import-hook bytecode and transformer caches.",
    )
    sub = parser.add_subparsers(dest="command", required=False)

    parser_module = sub.add_parser(
        "module",
        help="Remove cached bytecode for one module and optionally touch the source file.",
    )
    parser_module.add_argument("module", help="Module source path, relative to the pyrolyze repo root.")
    parser_module.add_argument(
        "--touch-source",
        action="store_true",
        help="Also touch the module source file to force source-level invalidation.",
    )
    parser_module.set_defaults(func=_cmd_module)

    parser_transformer = sub.add_parser(
        "transformer",
        help="Touch a compiler file to change the transformer fingerprint.",
    )
    parser_transformer.add_argument(
        "--touch-file",
        default=str(DEFAULT_TRANSFORMER_TOUCH),
        help="Compiler file to touch, relative to the pyrolyze repo root.",
    )
    parser_transformer.set_defaults(func=_cmd_transformer)

    parser_all = sub.add_parser(
        "all",
        help="Cold-start a module import, bump transformer fingerprint, and optionally clear persistent cache.",
    )
    parser_all.add_argument(
        "--module",
        help="Optional module source path, relative to the pyrolyze repo root.",
    )
    parser_all.add_argument(
        "--touch-source",
        action="store_true",
        help="Also touch the module source file when --module is provided.",
    )
    parser_all.add_argument(
        "--touch-file",
        default=str(DEFAULT_TRANSFORMER_TOUCH),
        help="Compiler file to touch, relative to the pyrolyze repo root.",
    )
    parser_all.add_argument(
        "--clear-persistent-cache",
        action="store_true",
        help="Remove the persistent artifact cache directory as well.",
    )
    parser_all.add_argument(
        "--cache-dir",
        default=str(DEFAULT_PERSISTENT_CACHE),
        help="Persistent cache directory, relative to the pyrolyze repo root.",
    )
    parser_all.set_defaults(func=_cmd_all)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    raw_argv = list(argv if argv is not None else sys.argv[1:])
    if not raw_argv or raw_argv[0] not in {"module", "transformer", "all", "-h", "--help"}:
        raw_argv = ["transformer", *raw_argv]
    args = parser.parse_args(raw_argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
