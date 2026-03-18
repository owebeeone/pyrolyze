from __future__ import annotations

import ast
from typing import Any, Protocol

from .artifacts import DetectionResult, ModuleTransformPlan


class AstKernel(Protocol):
    def parse_module(
        self,
        source: str,
        *,
        module_name: str,
        filename: str | None = None,
    ) -> ast.Module: ...

    def detect_module(
        self,
        module_ast: ast.Module,
        *,
        module_name: str,
        filename: str | None = None,
    ) -> DetectionResult: ...

    def build_transform_plan(
        self,
        detection: DetectionResult,
        *,
        module_name: str,
    ) -> ModuleTransformPlan: ...

    def lower_module_plan(self, plan: ModuleTransformPlan) -> ast.Module: ...
    def validate_plan(self, plan: ModuleTransformPlan) -> None: ...
    def validate_module_ast(self, module_ast: ast.Module, *, module_name: str) -> None: ...
    def validate_provenance(self, plan: ModuleTransformPlan, module_ast: ast.Module) -> None: ...
    def emit_source(self, module_ast: ast.Module) -> str: ...
    def exec_module_ast(
        self,
        module_ast: ast.Module,
        *,
        filename: str,
        namespace: dict[str, Any],
    ) -> None: ...
