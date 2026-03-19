"""Public compiler surface for the PyRolyze prototype implementation."""

from .artifacts import (
    CompileArtifact,
    CompileMetadata,
    CompileWarning,
    ComponentFactory,
    ComponentTransformPlan,
    DebugArtifacts,
    HookRecord,
    ModuleTransformPlan,
    TransformFlags,
)
from .debug import write_debug_artifacts
from .diagnostics import PyRolyzeCompileError
from .facade import (
    analyze_source,
    build_debug_artifacts_for_source,
    compile_source,
    compile_source_with_env,
    emit_transformed_source,
    load_transformed_namespace,
    lower_plan_to_ast,
)
from . import kernel_loader

__all__ = [
    "CompileArtifact",
    "CompileMetadata",
    "CompileWarning",
    "ComponentFactory",
    "ComponentTransformPlan",
    "DebugArtifacts",
    "HookRecord",
    "ModuleTransformPlan",
    "PyRolyzeCompileError",
    "TransformFlags",
    "analyze_source",
    "build_debug_artifacts_for_source",
    "compile_source",
    "compile_source_with_env",
    "emit_transformed_source",
    "kernel_loader",
    "load_transformed_namespace",
    "lower_plan_to_ast",
    "write_debug_artifacts",
]
