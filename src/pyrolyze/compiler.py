"""Minimal compiler prototype to satisfy the initial PyRolyze TDD specification."""

from __future__ import annotations

import ast
import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable


_DUMP_TRANSFORMED_PY_ENV = "PYROLYZE_DUMP_TRANSFORMED_PY"
_DUMP_TRANSFORMED_DIR_ENV = "PYROLYZE_DUMP_TRANSFORMED_DIR"


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


class PyRolyzeCompileError(RuntimeError):
    """Compile-time error with stable code and source-location metadata."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "PYR-E-COMPILE",
        path: str | None = None,
        line: int | None = None,
        column: int | None = None,
        node_class: str | None = None,
        suggested_fix: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.path = path
        self.line = line
        self.column = column
        self.node_class = node_class
        self.suggested_fix = suggested_fix


@dataclass(frozen=True, slots=True)
class HookRecord:
    name: str
    line: int
    column: int
    component: str


@dataclass(slots=True)
class CompileMetadata:
    hooks: list[HookRecord] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class CompileWarning:
    code: str
    message: str


@dataclass(slots=True)
class CompileArtifact:
    metadata: CompileMetadata
    init_ir: dict[str, Any]
    update_ir: dict[str, Any]
    components: dict[str, Any]
    source_map: dict[str, Any]
    component_factory: Callable[..., Any]
    warnings: list[CompileWarning] = field(default_factory=list)
    non_reactive: bool = False


@dataclass(frozen=True, slots=True)
class ComponentFactory:
    module_name: str
    mode: str = "reactive"

    def __call__(self, component_name: str, **props: Any) -> dict[str, Any]:
        payload = {
            "component": component_name,
            "module": self.module_name,
            "props": props,
        }
        if self.mode == "raw-fallback":
            payload["mode"] = "raw-fallback"
        return payload


@dataclass(frozen=True, slots=True)
class _ReactiveComponentDef:
    name: str
    node: ast.FunctionDef | ast.AsyncFunctionDef


@dataclass(frozen=True, slots=True)
class _ComponentAnalysis:
    hooks: list[HookRecord]
    has_if: bool
    has_for: bool


class _UnsupportedSyntaxFinder(ast.NodeVisitor):
    def __init__(self) -> None:
        self.first_unsupported: ast.AST | None = None
        self.reason: str | None = None

    def _mark(self, node: ast.AST, reason: str) -> None:
        if self.first_unsupported is None:
            self.first_unsupported = node
            self.reason = reason

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
            raise PyRolyzeCompileError(
                "Mutable loop must use keyed(items, key=...)",
                code="PYR-E-MISSING-KEY",
                path=self.module_name,
                line=getattr(node, "lineno", None),
                column=getattr(node, "col_offset", None),
                node_class=node.__class__.__name__,
                suggested_fix="use_keyed_loop",
            )

        self._loop_depth += 1
        for stmt in node.body:
            self.visit(stmt)
        for stmt in node.orelse:
            self.visit(stmt)
        self._loop_depth -= 1

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self._nested_fn_depth += 1
        for stmt in node.body:
            self.visit(stmt)
        self._nested_fn_depth -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        self._nested_fn_depth += 1
        for stmt in node.body:
            self.visit(stmt)
        self._nested_fn_depth -= 1

    def visit_Call(self, node: ast.Call) -> Any:
        call_name = _call_name(node)
        if call_name in _HOOK_NAMES:
            if self._if_depth > 0 or self._loop_depth > 0 or self._nested_fn_depth > 0:
                raise PyRolyzeCompileError(
                    f"Hook '{call_name}' must be top-level in component scope",
                    code="PYR-E-HOOK-PLACEMENT",
                    path=self.module_name,
                    line=getattr(node, "lineno", None),
                    column=getattr(node, "col_offset", None),
                    node_class=node.__class__.__name__,
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



def compile_source(
    source: str,
    *,
    module_name: str,
    env: str = "dev",
    enable_raw_fallback: bool = False,
) -> CompileArtifact:
    """Compile declarative source into a minimal IR artifact for tests."""
    if env == "prod" and enable_raw_fallback:
        raise PyRolyzeCompileError(
            "Raw fallback is forbidden in production mode",
            code="PYR-E-RAW-FALLBACK-PROD",
            path=module_name,
            suggested_fix="disable_raw_fallback_in_prod",
        )

    try:
        module_ast = ast.parse(source, filename=module_name)
    except SyntaxError as exc:
        raise PyRolyzeCompileError(
            str(exc),
            code="PYR-E-SYNTAX",
            path=module_name,
            line=exc.lineno,
            column=exc.offset,
            node_class="SyntaxError",
        ) from exc

    unsupported_finder = _UnsupportedSyntaxFinder()
    unsupported_finder.visit(module_ast)
    if unsupported_finder.first_unsupported is not None:
        if enable_raw_fallback and env != "prod":
            _maybe_dump_transformed_py(module_ast, module_name)
            fallback = _build_fallback_artifact(module_name)
            _maybe_dump_artifact(fallback, module_name)
            return fallback

        node = unsupported_finder.first_unsupported
        raise PyRolyzeCompileError(
            unsupported_finder.reason or "Unsupported syntax",
            code="PYR-E-UNSUPPORTED-SYNTAX",
            path=module_name,
            line=getattr(node, "lineno", None),
            column=getattr(node, "col_offset", None),
            node_class=node.__class__.__name__,
            suggested_fix="rewrite_unsupported_syntax",
        )

    _maybe_dump_transformed_py(module_ast, module_name)
    components = _extract_reactive_components(module_ast)

    all_hooks: list[HookRecord] = []
    component_records: dict[str, Any] = {}
    init_components: list[dict[str, Any]] = []
    block_records: list[dict[str, Any]] = []

    for component in components:
        analysis = _analyze_component(module_name, component)
        all_hooks.extend(analysis.hooks)

        component_entry = {
            "name": component.name,
            "kind": "method" if "." in component.name else "function",
            "source_line": int(getattr(component.node, "lineno", -1)),
        }
        component_records[component.name] = component_entry

        init_components.append(
            {
                "name": component.name,
                "kind": component_entry["kind"],
                "mount_ops": [
                    "create_widgets",
                    "bind_static_props",
                    "create_anchors",
                ],
            }
        )

        if analysis.has_if and not _contains_block(block_records, "SwitchBlock"):
            block_records.append({"type": "SwitchBlock", "strategy": "branch_mount_patch_unmount"})

        if analysis.has_for and not _contains_block(block_records, "ForBlock"):
            block_records.append({"type": "ForBlock", "reconcile": "keyed"})

    metadata = CompileMetadata(hooks=all_hooks)

    init_ir = {
        "kind": "InitGraph",
        "components": init_components,
    }

    update_ir = {
        "kind": "UpdateGraph",
        "blocks": block_records,
    }

    source_map = {
        "module_name": module_name,
        "version": 1,
        "mappings": [
            {
                "component": component_name,
                "source_line": int(component_data["source_line"]),
                "generated_symbol": _generated_symbol_for_component(component_name),
            }
            for component_name, component_data in component_records.items()
        ],
    }


    artifact = CompileArtifact(
        metadata=metadata,
        init_ir=init_ir,
        update_ir=update_ir,
        components=component_records,
        source_map=source_map,
        component_factory=ComponentFactory(module_name=module_name),
    )
    _maybe_dump_artifact(artifact, module_name)
    return artifact



def _build_fallback_artifact(module_name: str) -> CompileArtifact:
    return CompileArtifact(
        metadata=CompileMetadata(hooks=[]),
        init_ir={"kind": "InitGraph", "components": []},
        update_ir={"kind": "UpdateGraph", "blocks": []},
        components={},
        source_map={"module_name": module_name, "version": 1, "mappings": []},
        component_factory=ComponentFactory(module_name=module_name, mode="raw-fallback"),
        warnings=[
            CompileWarning(
                code="PYR-W-RAW-FALLBACK",
                message="Compilation fell back to raw module execution.",
            )
        ],
        non_reactive=True,
    )



def _analyze_component(module_name: str, component: _ReactiveComponentDef) -> _ComponentAnalysis:
    analyzer = _ComponentAnalyzer(module_name=module_name, component_name=component.name)
    for statement in component.node.body:
        analyzer.visit(statement)

    return _ComponentAnalysis(
        hooks=analyzer.hooks,
        has_if=analyzer.has_if,
        has_for=analyzer.has_for,
    )



def _extract_reactive_components(module_ast: ast.Module) -> list[_ReactiveComponentDef]:
    components: list[_ReactiveComponentDef] = []

    for node in module_ast.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_reactive_component(node):
            components.append(_ReactiveComponentDef(name=node.name, node=node))
            continue

        if isinstance(node, ast.ClassDef):
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_reactive_component(member):
                    components.append(
                        _ReactiveComponentDef(
                            name=f"{node.name}.{member.name}",
                            node=member,
                        )
                    )

    return components



def _contains_block(blocks: list[dict[str, Any]], block_type: str) -> bool:
    return any(str(block.get("type")) == block_type for block in blocks)



def _generated_symbol_for_component(component_name: str) -> str:
    normalized = component_name.replace(".", "__")
    return f"_pyrolyze_gen_{normalized}"



def _is_reactive_component(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(
        _decorator_name(decorator) in {"pyrolyse", "reactive_component"}
        for decorator in node.decorator_list
    )



def _is_keyed_call(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and _call_name(node) == "keyed"



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


def _is_truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _dump_dir() -> Path | None:
    if not _is_truthy(os.getenv(_DUMP_TRANSFORMED_PY_ENV, "")):
        return None
    out_dir = os.getenv(_DUMP_TRANSFORMED_DIR_ENV, ".pyrolyze_dump")
    path = Path(out_dir).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _maybe_dump_transformed_py(module_ast: ast.Module, module_name: str) -> None:
    """If PYROLYZE_DUMP_TRANSFORMED_PY is set, unparse AST to a .py file."""
    path = _dump_dir()
    if path is None:
        return
    safe_name = module_name.replace(".", "_")
    out_file = path / f"{safe_name}.pyrolyze-transformed.py"
    try:
        out_file.write_text(ast.unparse(module_ast), encoding="utf-8")
    except OSError:
        pass  # best-effort; avoid breaking compilation


def _artifact_to_json_safe(artifact: CompileArtifact) -> dict[str, Any]:
    """Build a JSON-serializable view of CompileArtifact (no callables)."""
    return {
        "metadata": {
            "hooks": [asdict(h) for h in artifact.metadata.hooks],
        },
        "init_ir": artifact.init_ir,
        "update_ir": artifact.update_ir,
        "components": artifact.components,
        "source_map": artifact.source_map,
        "component_factory": (
            {"module_name": artifact.component_factory.module_name, "mode": artifact.component_factory.mode}
            if isinstance(artifact.component_factory, ComponentFactory)
            else None
        ),
        "warnings": [asdict(w) for w in artifact.warnings],
        "non_reactive": artifact.non_reactive,
    }


def _maybe_dump_artifact(artifact: CompileArtifact, module_name: str) -> None:
    """If PYROLYZE_DUMP_TRANSFORMED_PY is set, write compiler artifact as JSON."""
    path = _dump_dir()
    if path is None:
        return
    safe_name = module_name.replace(".", "_")
    out_file = path / f"{safe_name}.pyrolyze-artifact.json"
    try:
        out_file.write_text(
            json.dumps(_artifact_to_json_safe(artifact), indent=2),
            encoding="utf-8",
        )
    except (OSError, TypeError):
        pass  # best-effort; avoid breaking compilation


def compile_source_with_env(source: str, *, module_name: str) -> CompileArtifact:
    """Compile source using env-driven fallback policy flags."""
    env_name = str(os.getenv("PYROLYZE_ENV", "dev")).strip().lower() or "dev"
    raw_flag = str(os.getenv("PYROLYZE_ENABLE_RAW_FALLBACK", "")).strip().lower()
    enable_raw_fallback = raw_flag in {"1", "true", "yes", "on"}

    return compile_source(
        source,
        module_name=module_name,
        env=env_name,
        enable_raw_fallback=enable_raw_fallback,
    )


__all__ = [
    "CompileArtifact",
    "ComponentFactory",
    "CompileMetadata",
    "CompileWarning",
    "HookRecord",
    "PyRolyzeCompileError",
    "compile_source",
    "compile_source_with_env",
]






