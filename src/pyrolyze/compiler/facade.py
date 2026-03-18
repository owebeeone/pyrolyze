from __future__ import annotations

from dataclasses import asdict
import os
from typing import Any

from .artifacts import (
    CompileArtifact,
    CompileMetadata,
    CompileWarning,
    ComponentFactory,
    DebugArtifacts,
    ModuleTransformPlan,
)
from .debug import build_debug_artifacts, dump_dir, write_debug_artifacts
from .diagnostics import PyRolyzeCompileError
from .kernel_loader import load_ast_kernel


def analyze_source(
    source: str,
    *,
    module_name: str,
    filename: str | None = None,
) -> ModuleTransformPlan:
    kernel = load_ast_kernel()
    module_ast = kernel.parse_module(source, module_name=module_name, filename=filename)
    detection = kernel.detect_module(module_ast, module_name=module_name, filename=filename)
    plan = kernel.build_transform_plan(detection, module_name=module_name)
    kernel.validate_plan(plan)
    return plan


def lower_plan_to_ast(
    plan: ModuleTransformPlan,
    *,
    filename: str | None = None,
) -> Any:
    del filename
    kernel = load_ast_kernel()
    module_ast = kernel.lower_module_plan(plan)
    kernel.validate_module_ast(module_ast, module_name=plan.module_name)
    kernel.validate_provenance(plan, module_ast)
    return module_ast


def emit_transformed_source(
    source: str,
    *,
    module_name: str,
    filename: str | None = None,
) -> str:
    plan = analyze_source(source, module_name=module_name, filename=filename)
    module_ast = lower_plan_to_ast(plan, filename=filename)
    return load_ast_kernel().emit_source(module_ast)


def build_debug_artifacts_for_source(
    source: str,
    *,
    module_name: str,
    filename: str | None = None,
) -> Any:
    plan = analyze_source(source, module_name=module_name, filename=filename)
    transformed_source = emit_transformed_source(source, module_name=module_name, filename=filename)
    return build_debug_artifacts(plan, transformed_source)


def load_transformed_namespace(
    source: str,
    *,
    module_name: str,
    filename: str | None = None,
    globals_dict: dict[str, object] | None = None,
) -> dict[str, object]:
    plan = analyze_source(source, module_name=module_name, filename=filename)
    module_ast = lower_plan_to_ast(plan, filename=filename)
    namespace: dict[str, object] = {} if globals_dict is None else dict(globals_dict)
    namespace.setdefault("__name__", module_name)
    namespace.setdefault("__file__", filename or plan.filename)
    namespace.setdefault("__package__", module_name.rpartition(".")[0])
    load_ast_kernel().exec_module_ast(
        module_ast,
        filename=filename or plan.filename,
        namespace=namespace,
    )
    return namespace


def compile_source(
    source: str,
    *,
    module_name: str,
    filename: str | None = None,
    env: str = "dev",
    enable_raw_fallback: bool = False,
) -> CompileArtifact:
    if env == "prod" and enable_raw_fallback:
        raise PyRolyzeCompileError(
            "Raw fallback is forbidden in production mode",
            code="PYR-E-RAW-FALLBACK-PROD",
            path=filename or module_name,
            suggested_fix="disable_raw_fallback_in_prod",
        )

    try:
        plan = analyze_source(source, module_name=module_name, filename=filename)
    except PyRolyzeCompileError as exc:
        if exc.code == "PYR-E-UNSUPPORTED-SYNTAX" and enable_raw_fallback and env != "prod":
            fallback = _build_fallback_artifact(module_name=module_name, filename=filename)
            debug_artifacts = _build_fallback_debug_artifacts(
                source,
                module_name=module_name,
                filename=filename,
                fallback=fallback,
            )
            _maybe_dump_debug_artifacts(
                debug_artifacts,
                compile_artifact=fallback,
            )
            return fallback
        raise

    transformed_source = emit_transformed_source(source, module_name=module_name, filename=filename)
    debug_artifacts = build_debug_artifacts(plan, transformed_source)
    artifact = _compile_artifact_from_plan(plan, debug_artifacts=debug_artifacts)
    _maybe_dump_debug_artifacts(debug_artifacts, compile_artifact=artifact)
    return artifact


def compile_source_with_env(
    source: str,
    *,
    module_name: str,
    filename: str | None = None,
) -> CompileArtifact:
    env_name = str(os.getenv("PYROLYZE_ENV", "dev")).strip().lower() or "dev"
    raw_flag = str(os.getenv("PYROLYZE_ENABLE_RAW_FALLBACK", "")).strip().lower()
    enable_raw_fallback = raw_flag in {"1", "true", "yes", "on"}
    return compile_source(
        source,
        module_name=module_name,
        filename=filename,
        env=env_name,
        enable_raw_fallback=enable_raw_fallback,
    )


def _compile_artifact_from_plan(
    plan: ModuleTransformPlan,
    *,
    debug_artifacts: Any,
) -> CompileArtifact:
    component_records = {
        component.public_name: {
            "name": component.public_name,
            "kind": component.kind,
            "source_line": component.source_line,
            "generated_symbol": component.generated_private_name,
        }
        for component in plan.component_plans
    }
    init_components = [
        {
            "name": component.public_name,
            "kind": component.kind,
            "mount_ops": [
                "create_widgets",
                "bind_static_props",
                "create_anchors",
            ],
        }
        for component in plan.component_plans
    ]
    blocks: list[dict[str, str]] = []
    if any(component.has_if for component in plan.component_plans):
        blocks.append({"type": "SwitchBlock", "strategy": "branch_mount_patch_unmount"})
    if any(component.has_for for component in plan.component_plans):
        blocks.append({"type": "ForBlock", "reconcile": "keyed"})

    metadata = CompileMetadata(
        hooks=[hook for component in plan.component_plans for hook in component.hooks]
    )
    return CompileArtifact(
        metadata=metadata,
        init_ir={"kind": "InitGraph", "components": init_components},
        update_ir={"kind": "UpdateGraph", "blocks": blocks},
        components=component_records,
        source_map=debug_artifacts.source_map,
        component_factory=ComponentFactory(module_name=plan.module_name),
        warnings=[],
        non_reactive=False,
        transformed_source=debug_artifacts.transformed_source,
        generated_relpath=debug_artifacts.generated_relpath,
    )


def _build_fallback_artifact(
    *,
    module_name: str,
    filename: str | None,
) -> CompileArtifact:
    generated_relpath = None
    if filename is not None:
        from .debug import _generated_relpath  # local import to keep surface small

        generated_relpath = _generated_relpath(module_name, filename).as_posix()

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
        transformed_source=source_placeholder(module_name=module_name),
        generated_relpath=generated_relpath,
    )


def _build_fallback_debug_artifacts(
    source: str,
    *,
    module_name: str,
    filename: str | None,
    fallback: CompileArtifact,
) -> DebugArtifacts:
    from .debug import _generated_relpath  # local import to keep surface small

    kernel = load_ast_kernel()
    module_ast = kernel.parse_module(source, module_name=module_name, filename=filename)
    source_filename = filename or module_name
    transformed_source = kernel.emit_source(module_ast)
    generated_relpath = _generated_relpath(module_name, source_filename).as_posix()
    fallback.transformed_source = transformed_source
    fallback.generated_relpath = generated_relpath
    return DebugArtifacts(
        version=1,
        module_name=module_name,
        source_filename=source_filename,
        generated_relpath=generated_relpath,
        transformed_source=transformed_source,
        provenance=[],
        source_map={"module_name": module_name, "version": 1, "mappings": []},
        diagnostics=[
            {
                "code": warning.code,
                "message": warning.message,
            }
            for warning in fallback.warnings
        ],
    )


def _maybe_dump_debug_artifacts(debug_artifacts: Any, *, compile_artifact: CompileArtifact) -> None:
    out_dir = dump_dir()
    if out_dir is None:
        return
    debug_artifacts.compile_artifact = _artifact_to_json_safe(compile_artifact)
    write_debug_artifacts(debug_artifacts, out_dir=out_dir, module_name=debug_artifacts.module_name)


def _artifact_to_json_safe(artifact: CompileArtifact) -> dict[str, Any]:
    return {
        "metadata": {
            "hooks": [asdict(hook) for hook in artifact.metadata.hooks],
        },
        "init_ir": artifact.init_ir,
        "update_ir": artifact.update_ir,
        "components": artifact.components,
        "source_map": artifact.source_map,
        "component_factory": (
            {
                "module_name": artifact.component_factory.module_name,
                "mode": artifact.component_factory.mode,
            }
            if isinstance(artifact.component_factory, ComponentFactory)
            else None
        ),
        "warnings": [asdict(warning) for warning in artifact.warnings],
        "non_reactive": artifact.non_reactive,
        "generated_relpath": artifact.generated_relpath,
    }


def source_placeholder(*, module_name: str) -> str:
    return f"# raw fallback for {module_name}\n"
