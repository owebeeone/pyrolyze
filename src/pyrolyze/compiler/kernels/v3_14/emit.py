from __future__ import annotations

import ast
from types import CodeType
from typing import Any

from ...artifacts import ModuleTransformPlan
from .rewrite import lower_module_plan


def emit_module_ast(plan: ModuleTransformPlan) -> ast.Module:
    return lower_module_plan(plan)


def emit_source(module_ast: ast.Module) -> str:
    return ast.unparse(module_ast)


def emit_code(module_ast: ast.Module, *, filename: str) -> CodeType:
    return compile(module_ast, filename, "exec")


def exec_module_ast(
    module_ast: ast.Module,
    *,
    filename: str,
    namespace: dict[str, Any],
) -> None:
    exec(emit_code(module_ast, filename=filename), namespace)
