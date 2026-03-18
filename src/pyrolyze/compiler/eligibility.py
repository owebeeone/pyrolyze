from __future__ import annotations

import ast

from .diagnostics import PyRolyzeCompileError


def is_pyrolyze_module(source: str, *, module_name: str) -> bool:
    del module_name
    marker_window = source.splitlines()[:2]
    return any(line.strip() == "#@pyrolyze" for line in marker_window)


def should_transform_module(
    source: str,
    *,
    module_name: str,
    file_path: str | None = None,
) -> bool:
    del file_path
    return is_pyrolyze_module(source, module_name=module_name)


def parse_module(
    source: str,
    *,
    module_name: str,
    filename: str | None = None,
) -> ast.Module:
    parse_name = filename or module_name
    try:
        return ast.parse(source, filename=parse_name)
    except SyntaxError as exc:
        raise PyRolyzeCompileError(
            str(exc),
            code="PYR-E-SYNTAX",
            path=parse_name,
            line=exc.lineno,
            column=exc.offset,
            node_class="SyntaxError",
        ) from exc
