from __future__ import annotations

import ast

from ...artifacts import ModuleTransformPlan
from ...diagnostics import PyRolyzeCompileError


def validate_plan(plan: ModuleTransformPlan) -> None:
    if not plan.module_name:
        raise PyRolyzeCompileError("module_name is required", code="PYR-E-INVALID-PLAN")


def validate_module_ast(module_ast: ast.Module, *, module_name: str) -> None:
    try:
        ast.unparse(module_ast)
    except Exception as exc:  # pragma: no cover - defensive
        raise PyRolyzeCompileError(
            f"Unable to emit helper source for '{module_name}': {exc}",
            code="PYR-E-UNPARSE",
            path=module_name,
        ) from exc


def validate_generated_signatures(module_ast: ast.Module) -> None:
    del module_ast


def validate_provenance(plan: ModuleTransformPlan, module_ast: ast.Module) -> None:
    del module_ast
    for record in plan.provenance_records:
        if record.source_line < 0:
            raise PyRolyzeCompileError(
                "Generated node is missing provenance",
                code="PYR-E-MISSING-PROVENANCE",
                path=plan.module_name,
            )
