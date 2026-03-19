from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any

from ...artifacts import (
    CompileWarning,
    ComponentDetection,
    DetectionResult,
    EventBoundaryInfo,
    SlottedHelperInfo,
)
from ...diagnostics import error_from_node


_REACTIVE_DECORATORS = {"pyrolyse", "reactive_component"}
_SLOTTED_DECORATORS = {"pyrolyze_slotted"}
_EVENT_HANDLER_TYPES = {"PyrolyzeHandler", "PyrolyteHandler"}


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
    def __init__(
        self,
        module_name: str,
    ) -> None:
        self.module_name = module_name
        self.has_if = False
        self.has_for = False

    def visit_If(self, node: ast.If) -> Any:
        self.has_if = True
        for stmt in node.body:
            self.visit(stmt)
        for stmt in node.orelse:
            self.visit(stmt)

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

        for stmt in node.body:
            self.visit(stmt)
        for stmt in node.orelse:
            self.visit(stmt)


def detect_module(
    module_ast: ast.Module,
    *,
    module_name: str,
    filename: str | None = None,
) -> DetectionResult:
    _validate_import_prelude(module_ast, module_name=filename or module_name)
    reactive_decorator_names, slotted_decorator_names, event_handler_type_names = _collect_source_api_aliases(
        module_ast
    )
    reactive_components = _extract_reactive_components(
        module_ast,
        reactive_decorator_names=reactive_decorator_names,
    )
    for component_name, component_node in reactive_components:
        unsupported = _find_unsupported_syntax(component_node)
        if unsupported is not None:
            raise error_from_node(
                unsupported.node,
                code="PYR-E-UNSUPPORTED-SYNTAX",
                message=unsupported.reason,
                module_name=filename or component_name,
                suggested_fix="rewrite_unsupported_syntax",
            )

    components = tuple(
        _analyze_component(
            module_name,
            component,
            reactive_decorator_names=reactive_decorator_names,
            slotted_decorator_names=slotted_decorator_names,
        )
        for component in reactive_components
    )
    slotted_helpers = tuple(
        detect_slotted_helpers(
            module_ast,
            slotted_decorator_names=slotted_decorator_names,
        )
    )
    event_boundaries = tuple(
        boundary
        for component in components
        for boundary in detect_event_boundaries(
            component.node,
            component_name=component.name,
            event_handler_type_names=event_handler_type_names,
        )
    )
    diagnostics = tuple(
        _collect_component_return_type_warnings(
            module_ast,
            module_name=filename or module_name,
            reactive_decorator_names=reactive_decorator_names,
        )
    )

    return DetectionResult(
        module_name=module_name,
        filename=filename or module_name,
        module_ast=module_ast,
        components=components,
        slotted_helpers=slotted_helpers,
        event_boundaries=event_boundaries,
        diagnostics=diagnostics,
    )


def detect_slotted_helpers(
    module_ast: ast.Module,
    *,
    slotted_decorator_names: set[str] | None = None,
) -> list[SlottedHelperInfo]:
    slotted_names = slotted_decorator_names or set(_SLOTTED_DECORATORS)
    helpers: list[SlottedHelperInfo] = []
    for node in ast.walk(module_ast):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_pyrolyze_slotted(
            node,
            slotted_decorator_names=slotted_names,
        ):
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
    event_handler_type_names: set[str] | None = None,
) -> list[EventBoundaryInfo]:
    boundaries: list[EventBoundaryInfo] = []
    handler_names = event_handler_type_names or set(_EVENT_HANDLER_TYPES)
    all_arguments = [
        *component.args.posonlyargs,
        *component.args.args,
        *component.args.kwonlyargs,
    ]
    for argument in all_arguments:
        if _annotation_contains_event_handler(argument.annotation, event_handler_type_names=handler_names):
            boundaries.append(
                EventBoundaryInfo(
                    component_name=component_name,
                    parameter_name=argument.arg,
                    line=getattr(argument, "lineno", getattr(component, "lineno", -1)),
                    column=getattr(argument, "col_offset", getattr(component, "col_offset", -1)),
                )
            )
    return boundaries


def _collect_component_return_type_warnings(
    module_ast: ast.Module,
    *,
    module_name: str,
    reactive_decorator_names: set[str],
) -> list[CompileWarning]:
    warnings: list[CompileWarning] = []

    def walk_body(body: list[ast.stmt], *, qual_prefix: str) -> None:
        for statement in body:
            if isinstance(statement, ast.ClassDef):
                class_prefix = _qualified_name(qual_prefix, statement.name)
                walk_body(statement.body, qual_prefix=class_prefix)
                continue
            if not isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            function_name = _qualified_name(qual_prefix, statement.name)
            warnings.extend(
                _component_return_type_warnings_for_function(
                    statement,
                    function_name=function_name,
                    module_name=module_name,
                    reactive_decorator_names=reactive_decorator_names,
                )
            )

            if not _is_reactive_component(statement, reactive_decorator_names=reactive_decorator_names):
                walk_body(statement.body, qual_prefix=f"{function_name}.<locals>")

    walk_body(module_ast.body, qual_prefix="")
    return warnings


def _component_return_type_warnings_for_function(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    function_name: str,
    module_name: str,
    reactive_decorator_names: set[str],
) -> list[CompileWarning]:
    nested_components = {
        statement.name: statement
        for statement in function.body
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef))
        and _is_reactive_component(statement, reactive_decorator_names=reactive_decorator_names)
    }
    if not nested_components:
        return []

    warnings: list[CompileWarning] = []
    seen_names: set[str] = set()
    for return_node in _find_returns_excluding_nested_defs(function):
        value = return_node.value
        if not isinstance(value, ast.Name) or value.id not in nested_components or value.id in seen_names:
            continue
        seen_names.add(value.id)
        if _annotation_contains_component_ref(function.returns):
            continue

        nested_component = nested_components[value.id]
        expected = _expected_component_ref_annotation(nested_component)
        warnings.append(
            CompileWarning(
                code="PYR-W-COMPONENT-RETURN-TYPE",
                message=(
                    f"Function '{function_name}' returns nested @pyrolyse component "
                    f"'{value.id}'; annotate its return type as {expected}"
                ),
                path=module_name,
                line=getattr(return_node, "lineno", getattr(function, "lineno", None)),
                column=getattr(return_node, "col_offset", getattr(function, "col_offset", None)),
                node_class=return_node.__class__.__name__,
            )
        )
    return warnings


def _find_returns_excluding_nested_defs(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[ast.Return]:
    returns: list[ast.Return] = []

    class _ReturnFinder(ast.NodeVisitor):
        def visit_Return(self, node: ast.Return) -> Any:
            returns.append(node)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
            return None

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
            return None

        def visit_ClassDef(self, node: ast.ClassDef) -> Any:
            return None

    finder = _ReturnFinder()
    for statement in function.body:
        finder.visit(statement)
    return returns


def _annotation_contains_component_ref(annotation: ast.AST | None) -> bool:
    if annotation is None:
        return False
    for node in ast.walk(annotation):
        if isinstance(node, ast.Name) and node.id == "ComponentRef":
            return True
        if isinstance(node, ast.Attribute) and node.attr == "ComponentRef":
            return True
    return False


def _expected_component_ref_annotation(component: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    arg_types: list[str] = []
    for argument in [*component.args.posonlyargs, *component.args.args, *component.args.kwonlyargs]:
        if argument.annotation is None:
            arg_types.append("Any")
        else:
            arg_types.append(ast.unparse(argument.annotation))
    return f"ComponentRef[[{', '.join(arg_types)}]]"


def _find_unsupported_syntax(module_ast: ast.Module) -> _UnsupportedSyntax | None:
    finder = _UnsupportedSyntaxFinder()
    finder.visit(module_ast)
    return finder.first_unsupported


def _analyze_component(
    module_name: str,
    component: tuple[str, ast.FunctionDef | ast.AsyncFunctionDef],
    *,
    reactive_decorator_names: set[str],
    slotted_decorator_names: set[str],
) -> ComponentDetection:
    component_name, component_node = component
    analyzer = _ComponentAnalyzer(
        module_name=module_name,
    )
    for statement in component_node.body:
        analyzer.visit(statement)
    return ComponentDetection(
        name=component_name,
        node=component_node,
        hooks=(),
        has_if=analyzer.has_if,
        has_for=analyzer.has_for,
    )


def _extract_reactive_components(
    module_ast: ast.Module,
    *,
    reactive_decorator_names: set[str],
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
            if _is_reactive_component(node, reactive_decorator_names=reactive_decorator_names):
                components.append((qualified_name, node))

            walk_body(node.body, f"{qualified_name}.<locals>")

    walk_body(module_ast.body)
    return components


def _is_reactive_component(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    reactive_decorator_names: set[str],
) -> bool:
    return any(
        _decorator_name(decorator) in reactive_decorator_names
        for decorator in node.decorator_list
    )


def _is_pyrolyze_slotted(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    slotted_decorator_names: set[str],
) -> bool:
    return any(_decorator_name(decorator) in slotted_decorator_names for decorator in node.decorator_list)

def _is_keyed_call(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and _call_name(node) == "keyed"


def _annotation_contains_event_handler(
    annotation: ast.AST | None,
    *,
    event_handler_type_names: set[str],
) -> bool:
    if annotation is None:
        return False
    for node in ast.walk(annotation):
        if isinstance(node, ast.Name) and node.id in event_handler_type_names:
            return True
        if isinstance(node, ast.Attribute) and node.attr in _EVENT_HANDLER_TYPES:
            return True
    return False


def _qualified_name(prefix: str, name: str) -> str:
    if not prefix:
        return name
    return f"{prefix}.{name}"


def _decorator_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _collect_source_api_aliases(module_ast: ast.Module) -> tuple[set[str], set[str], set[str]]:
    reactive = set(_REACTIVE_DECORATORS)
    slotted = set(_SLOTTED_DECORATORS)
    event_handlers = set(_EVENT_HANDLER_TYPES)
    for statement in module_ast.body:
        if not isinstance(statement, ast.ImportFrom) or statement.module != "pyrolyze.api":
            continue
        for alias in statement.names:
            local_name = alias.asname or alias.name
            if alias.name in _REACTIVE_DECORATORS:
                reactive.add(local_name)
            if alias.name in _SLOTTED_DECORATORS:
                slotted.add(local_name)
            if alias.name in _EVENT_HANDLER_TYPES:
                event_handlers.add(local_name)
    return reactive, slotted, event_handlers


def _validate_import_prelude(module_ast: ast.Module, *, module_name: str) -> None:
    seen_non_prelude = False
    for statement in module_ast.body:
        if _is_import_prelude_statement(statement):
            if seen_non_prelude and _contains_import_statement(statement):
                raise error_from_node(
                    statement,
                    code="PYR-E-IMPORT-PRELUDE",
                    message="Reactive modules require a top-of-file import prelude before executable code",
                    module_name=module_name,
                    suggested_fix="move_imports_to_module_prelude",
                )
            continue
        seen_non_prelude = True


def _is_import_prelude_statement(statement: ast.stmt) -> bool:
    if isinstance(statement, (ast.Import, ast.ImportFrom)):
        return True
    if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, str):
        return True
    if isinstance(statement, ast.If):
        return all(_is_import_prelude_statement(child) for child in [*statement.body, *statement.orelse])
    if isinstance(statement, ast.Try):
        handlers_ok = all(
            all(_is_import_prelude_statement(child) for child in handler.body)
            for handler in statement.handlers
        )
        return (
            all(_is_import_prelude_statement(child) for child in statement.body)
            and handlers_ok
            and all(_is_import_prelude_statement(child) for child in statement.orelse)
            and all(_is_import_prelude_statement(child) for child in statement.finalbody)
        )
    return False


def _contains_import_statement(statement: ast.stmt) -> bool:
    if isinstance(statement, (ast.Import, ast.ImportFrom)):
        return True
    for node in ast.walk(statement):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return True
    return False


def _call_name(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None
