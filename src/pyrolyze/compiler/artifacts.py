from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any, Callable


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
    transformed_source: str | None = None
    generated_relpath: str | None = None


@dataclass(frozen=True, slots=True)
class SlottedHelperInfo:
    name: str
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class EventBoundaryInfo:
    component_name: str
    parameter_name: str
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class ComponentDetection:
    name: str
    node: ast.FunctionDef | ast.AsyncFunctionDef
    hooks: tuple[HookRecord, ...]
    has_if: bool
    has_for: bool


@dataclass(frozen=True, slots=True)
class DetectionResult:
    module_name: str
    filename: str
    module_ast: ast.Module
    components: tuple[ComponentDetection, ...]
    slotted_helpers: tuple[SlottedHelperInfo, ...]
    event_boundaries: tuple[EventBoundaryInfo, ...]
    diagnostics: tuple[CompileWarning, ...] = ()


@dataclass(frozen=True, slots=True)
class ProvenanceRecord:
    generated_symbol: str
    source_line: int
    source_column: int
    reason: str


@dataclass(frozen=True, slots=True)
class ComponentTransformPlan:
    public_name: str
    generated_private_name: str
    node: ast.FunctionDef | ast.AsyncFunctionDef
    hooks: tuple[HookRecord, ...]
    kind: str
    source_line: int
    has_if: bool
    has_for: bool


@dataclass(frozen=True, slots=True)
class ModuleTransformPlan:
    module_name: str
    filename: str
    module_ast: ast.Module
    component_plans: tuple[ComponentTransformPlan, ...]
    diagnostics: tuple[CompileWarning, ...]
    provenance_records: tuple[ProvenanceRecord, ...]


@dataclass(slots=True)
class DebugArtifacts:
    version: int
    module_name: str
    source_filename: str
    generated_relpath: str
    transformed_source: str
    provenance: list[dict[str, Any]]
    source_map: dict[str, Any]
    diagnostics: list[dict[str, Any]]
    compile_artifact: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "module_name": self.module_name,
            "source_filename": self.source_filename,
            "generated_relpath": self.generated_relpath,
            "provenance": self.provenance,
            "source_map": self.source_map,
            "diagnostics": self.diagnostics,
            "compile_artifact": self.compile_artifact,
        }
