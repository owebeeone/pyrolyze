#!/usr/bin/env python3
"""Fail if removed ``pyrolyze.backends.common`` paths reappear (Phase 6.3).

Uses AST so docstrings and comments are not false positives. Run from the
``pyrolyze`` repository root::

    uv run python scripts/check_unified_drift.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

_FORBIDDEN = "pyrolyze.backends.common"

REPO = Path(__file__).resolve().parents[1]


def _forbidden_module(name: str | None) -> bool:
    if not name:
        return False
    return name == _FORBIDDEN or name.startswith(_FORBIDDEN + ".")


def _scan_ast(tree: ast.AST, rel_path: Path) -> list[str]:
    bad: list[str] = []

    class Visitor(ast.NodeVisitor):
        def visit_Import(self, node: ast.Import) -> None:
            for alias in node.names:
                if _forbidden_module(alias.name):
                    bad.append(f"{rel_path}: import {alias.name!r}")
            self.generic_visit(node)

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            if node.module and _forbidden_module(node.module):
                bad.append(f"{rel_path}: from {node.module} import ...")
            elif node.module == "pyrolyze.backends":
                for alias in node.names:
                    if alias.name == "common":
                        bad.append(f"{rel_path}: from pyrolyze.backends import common")
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "import_module"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "importlib"
                and node.args
            ):
                arg0 = node.args[0]
                if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                    if _forbidden_module(arg0.value):
                        bad.append(
                            f"{rel_path}: importlib.import_module({arg0.value!r})"
                        )
            self.generic_visit(node)

    Visitor().visit(tree)
    return bad


def _scan_file(path: Path) -> list[str]:
    rel = path.relative_to(REPO)
    try:
        text = path.read_text(encoding="utf-8-sig")
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        return [f"{rel}: syntax error ({exc.lineno}): {exc.msg}"]
    return _scan_ast(tree, rel)


def main() -> int:
    bad: list[str] = []
    for sub in ("src", "tests", "examples"):
        root = REPO / sub
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            bad.extend(_scan_file(path))
    if bad:
        print("Unified drift check failed:", file=sys.stderr)
        for line in bad:
            print(f"  {line}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
