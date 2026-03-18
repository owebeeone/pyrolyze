from __future__ import annotations

import ast
import copy

from ...artifacts import ComponentTransformPlan, ModuleTransformPlan


def lower_module_plan(plan: ModuleTransformPlan) -> ast.Module:
    module_ast = copy.deepcopy(plan.module_ast)
    ast.fix_missing_locations(module_ast)
    return module_ast


def lower_component(plan: ComponentTransformPlan) -> ast.FunctionDef | ast.AsyncFunctionDef:
    component = copy.deepcopy(plan.node)
    ast.fix_missing_locations(component)
    return component


def lower_statement_group(group: list[ast.stmt]) -> list[ast.stmt]:
    lowered = copy.deepcopy(group)
    for statement in lowered:
        ast.fix_missing_locations(statement)
    return lowered
