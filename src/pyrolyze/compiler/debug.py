from __future__ import annotations

import json
import linecache
import os
from pathlib import Path

from .artifacts import DebugArtifacts, ModuleTransformPlan


_DUMP_TRANSFORMED_PY_ENV = "PYROLYZE_DUMP_TRANSFORMED_PY"
_DUMP_TRANSFORMED_DIR_ENV = "PYROLYZE_DUMP_TRANSFORMED_DIR"


def build_debug_artifacts(
    plan: ModuleTransformPlan,
    transformed_source: str,
) -> DebugArtifacts:
    generated_relpath = _generated_relpath(plan.module_name, plan.filename)
    source_map = {
        "module_name": plan.module_name,
        "version": 1,
        "mappings": [
            {
                "component": component.public_name,
                "source_line": component.source_line,
                "generated_symbol": component.generated_private_name,
            }
            for component in plan.component_plans
        ],
    }
    provenance = [
        {
            "generated_symbol": record.generated_symbol,
            "source_line": record.source_line,
            "source_column": record.source_column,
            "reason": record.reason,
        }
        for record in plan.provenance_records
    ]
    diagnostics = [
        {
            "code": diagnostic.code,
            "message": diagnostic.message,
        }
        for diagnostic in plan.diagnostics
    ]
    return DebugArtifacts(
        version=1,
        module_name=plan.module_name,
        source_filename=plan.filename,
        generated_relpath=generated_relpath.as_posix(),
        transformed_source=transformed_source,
        provenance=provenance,
        source_map=source_map,
        diagnostics=diagnostics,
    )


def write_debug_artifacts(
    artifacts: DebugArtifacts,
    *,
    out_dir: Path,
    module_name: str,
) -> None:
    del module_name
    target_path = out_dir / Path(artifacts.generated_relpath)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(artifacts.transformed_source, encoding="utf-8")

    _sidecar_path(target_path, "provenance").write_text(
        json.dumps(
            {
                "version": artifacts.version,
                "module_name": artifacts.module_name,
                "source_filename": artifacts.source_filename,
                "provenance": artifacts.provenance,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    _sidecar_path(target_path, "sourcemap").write_text(
        json.dumps(artifacts.source_map, indent=2),
        encoding="utf-8",
    )
    _sidecar_path(target_path, "artifact").write_text(
        json.dumps(artifacts.to_dict(), indent=2),
        encoding="utf-8",
    )


def register_linecache_source(filename: str, source: str) -> None:
    lines = [line + "\n" for line in source.splitlines()]
    if source and not source.endswith("\n"):
        lines[-1] = lines[-1][:-1]
    linecache.cache[filename] = (len(source), None, lines, filename)


def dump_dir() -> Path | None:
    if not _is_truthy(os.getenv(_DUMP_TRANSFORMED_PY_ENV, "")):
        return None
    out_dir = os.getenv(_DUMP_TRANSFORMED_DIR_ENV, ".pyrolyze_dump")
    path = Path(out_dir).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _generated_relpath(module_name: str, source_filename: str) -> Path:
    parts = [part for part in module_name.split(".") if part]
    source_name = Path(source_filename).name if source_filename else ""
    if source_name == "__init__.py":
        return Path(*parts) / "__init__.py"
    if source_name.endswith(".py"):
        if len(parts) > 1:
            return Path(*parts[:-1]) / source_name
        return Path(source_name)
    if len(parts) > 1:
        return Path(*parts[:-1]) / f"{parts[-1]}.py"
    if parts:
        return Path(f"{parts[0]}.py")
    return Path("module.py")


def _sidecar_path(target_path: Path, name: str) -> Path:
    return target_path.with_suffix(f".pyrolyze.{name}.json")


def _is_truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}
