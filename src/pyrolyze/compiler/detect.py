from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any

from .artifacts import (
    ComponentDetection,
    DetectionResult,
    EventBoundaryInfo,
    HookRecord,
    SlottedHelperInfo,
)
from .diagnostics import PyRolyzeCompileError, error_from_node


_HOOK_NAMES = {
    "use_state",
    "use_effect",
    "use_mount",
    "use_unmount",
    "use_external_store",
    "use_store",
    "use_grip",
}

_UNSUPPORTED_CALLS = {"exec", "eval"}


@dataclass(frozen=True, slots=True)
class _UnsupportedSyntax:
    node: ast.AST
    reason: str


class _UnsupportedSyntaxFinder(ast.NodeVisitor):
    def __init__(self) -> None:
        self.first_unsupported: _UnsupportedSyntax | None = None

    def _mark(self, node: ast.AST, reason: str) -> None:
        if self.first_unsupported is None:
            self.first_unsupported = _UnsupportedSyntax(node=node, reason=reason)

    def visit_Call(self, node: ast.Call) -> Any:
        call_name = _call_name(node)
        if call_name in _UNSUPPORTED_CALLS:
            self._mark(node, f"Unsupported call '{call_name}' in reactive source")
            return
        self.generic_visit(node)

    def visit_Yield(self, node: ast.Yield) -> Any:
        self._mark(node, "Unsupported 'yield' in reactive source")

    def visit_YieldFrom(self, node: ast.YieldFrom) -> Any:
        self._mark(node, "Unsupported 'yield from' in reactive source")


class _ComponentAnalyzer(ast.NodeVisitor):
    def __init__(self, module_name: str, component_name: str) -> None:
        self.module_name = module_name
        self.component_name = component_name
        self.hooks: list[HookRecord] = []
        self.has_if = False
        self.has_for = False
        self._if_depth = 0
        self._loop_depth = 0
        self._nested_fn_depth = 0

    def visit_If(self, node: ast.If) -> Any:
        self.has_if = True
        self._if_depth += 1
        for stmt in node.body:
            self.visit(stmt)
        for stmt in node.orelse:
            self.visit(stmt)
        self._if_depth -= 1

    def visit_For(self, node: ast.For) -> Any:
        self.has_for = True
        if not _is_keyed_call(node.iter):
            raise error_from_node(
                node,
                code="PYR-E-MISSING-KEY",
                message="Mutable loop must use keyed(items, key=...)",
                module_name=self.module_name,
                suggested_fix="use_keyed_loop",
            )

        self._loop_depth += 1
        for stmt in node.body:
            self.visit(stmt)
        for stmt in node.orelse:
            self.visit(stmt)
        self._loop_depth -= 1

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        if _is_transformed_function(node):
            return None
        self._nested_fn_depth += 1
        for stmt in node.body:
            self.visit(stmt)
        self._nested_fn_depth -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        if _is_transformed_function(node):
            return None
        self._nested_fn_depth += 1
        for stmt in node.body:
            self.visit(stmt)
        self._nested_fn_depth -= 1

    def visit_Call(self, node: ast.Call) -> Any:
        call_name = _call_name(node)
        if call_name in _HOOK_NAMES:
            if self._if_depth > 0 or self._loop_depth > 0 or self._nested_fn_depth > 0:
                raise error_from_node(
                    node,
                    code="PYR-E-HOOK-PLACEMENT",
                    message=f"Hook '{call_name}' must be top-level in component scope",
                    module_name=self.module_name,
                    suggested_fix="move_hook_top_level",
                )

            self.hooks.append(
                HookRecord(
                    name=call_name,
                    line=getattr(node, "lineno", -1),
                    column=getattr(node, "col_offset", -1),
                    component=self.component_name,
                )
            )

        self.generic_visit(node)


def detect_module(
    module_ast: ast.Module,
    *,
    module_name: str,
    filename: str | None = None,
) -> DetectionResult:
    unsupported = _find_unsupported_syntax(module_ast)
    if unsupported is not None:
        raise error_from_node(
            unsupported.node,
            code="PYR-E-UNSUPPORTED-SYNTAX",
            message=unsupported.reason,
            module_name=filename or module_name,
            suggested_fix="rewrite_unsupported_syntax",
        )

    components = tuple(_analyze_component(module_name, component) for component in _extract_reactive_components(module_ast))
    slotted_helpers = tuple(detect_slotted_helpers(module_ast))
    event_boundaries = tuple(
        boundary
        for component in components
        for boundary in detect_event_boundaries(component.node, component_name=component.name)
    )

    return DetectionResult(
        module_name=module_name,
        filename=filename or module_name,
        module_ast=module_ast,
        components=components,
        slotted_helpers=slotted_helpers,
        event_boundaries=event_boundaries,
        diagnostics=(),
    )


def detect_slotted_helpers(module_ast: ast.Module) -> list[SlottedHelperInfo]:
    helpers: list[SlottedHelperInfo] = []
    for node in ast.walk(module_ast):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_pyrolyze_slotted(node):
            helpers.append(
                SlottedHelperInfo(
                    name=node.name,
                    line=getattr(node, "lineno", -1),
                    column=getattr(node, "col_offset", -1),
                )
            )
    return helpers


def detect_event_boundaries(
    component: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    component_name: str,
) -> list[EventBoundaryInfo]:
    boundaries: list[EventBoundaryInfo] = []
    all_arguments = [
        *component.args.posonlyargs,
        *component.args.args,
        *component.args.kwonlyargs,
    ]
    for argument in all_arguments:
        if _annotation_contains_event_handler(argument.annotation):
            boundaries.append(
                EventBoundaryInfo(
                    component_name=component_name,
                    parameter_name=argument.arg,
                    line=getattr(argument, "lineno", getattr(component, "lineno", -1)),
                    column=getattr(argument, "col_offset", getattr(component, "col_offset", -1)),
                )
            )
    return boundaries


def _find_unsupported_syntax(module_ast: ast.Module) -> _UnsupportedSyntax | None:
    finder = _UnsupportedSyntaxFinder()
    finder.visit(module_ast)
    return finder.first_unsupported


def _analyze_component(
    module_name: str,
    component: tuple[str, ast.FunctionDef | ast.AsyncFunctionDef],
) -> ComponentDetection:
    component_name, component_node = component
    analyzer = _ComponentAnalyzer(module_name=module_name, component_name=component_name)
    for statement in component_node.body:
        analyzer.visit(statement)
    return ComponentDetection(
        name=component_name,
        node=component_node,
        hooks=tuple(analyzer.hooks),
        has_if=analyzer.has_if,
        has_for=analyzer.has_for,
    )


def _extract_reactive_components(
    module_ast: ast.Module,
) -> list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]:
    components: list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]] = []

    def walk_body(body: list[ast.stmt], prefix: str = "") -> None:
        for node in body:
            if isinstance(node, ast.ClassDef):
                class_prefix = f"{prefix}.{node.name}" if prefix else node.name
                walk_body(node.body, class_prefix)
                continue

            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            qualified_name = f"{prefix}.{node.name}" if prefix else node.name
            if _is_reactive_component(node):
                components.append((qualified_name, node))

            walk_body(node.body, f"{qualified_name}.<locals>")

    walk_body(module_ast.body)
    return components


def _is_reactive_component(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(
        _decorator_name(decorator) in {"pyrolyse", "reactive_component"}
        for decorator in node.decorator_list
    )


def _is_pyrolyze_slotted(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(_decorator_name(decorator) == "pyrolyze_slotted" for decorator in node.decorator_list)


def _is_transformed_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return _is_reactive_component(node) or _is_pyrolyze_slotted(node)


def _is_keyed_call(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and _call_name(node) == "keyed"


def _annotation_contains_event_handler(annotation: ast.AST | None) -> bool:
    if annotation is None:
        return False
    for node in ast.walk(annotation):
        if isinstance(node, ast.Name) and node.id == "PyrolyteHandler":
            return True
        if isinstance(node, ast.Attribute) and node.attr == "PyrolyteHandler":
            return True
    return False


def _decorator_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _call_name(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None
