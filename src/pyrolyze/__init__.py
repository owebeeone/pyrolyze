"""Public package surface for the PyRolyze prototype implementation."""

from .api import pyrolyze
from .compiler import (
    CompileArtifact,
    ComponentFactory,
    CompileMetadata,
    CompileWarning,
    HookRecord,
    PyRolyzeCompileError,
    TransformFlags,
    compile_source,
    compile_source_with_env,
)

__all__ = [
    "CompileArtifact",
    "ComponentFactory",
    "CompileMetadata",
    "CompileWarning",
    "HookRecord",
    "PyRolyzeCompileError",
    "TransformFlags",
    "compile_source",
    "compile_source_with_env",
    "pyrolyze",
]
