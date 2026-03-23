"""Load and normalize the checked-in DearPyGui API dump for code generation."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from frozendict import frozendict


@dataclass(frozen=True, slots=True)
class DpgDumpParameter:
    name: str
    kind: str
    annotation: str | None
    default_repr: str | None


@dataclass(frozen=True, slots=True)
class DpgDumpFunctionRecord:
    name: str
    module: str
    signature: str
    signature_error: str | None
    doc_summary: str
    classification: str
    reason: str
    alias_of: str | None
    returns_item_handle: bool
    parameters: tuple[DpgDumpParameter, ...]
    parameter_names: tuple[str, ...]
    event_params: tuple[str, ...]
    source_params: tuple[str, ...]
    has_tag_param: bool
    has_parent_param: bool
    has_before_param: bool
    has_source_param: bool
    parent_default_repr: str | None
    before_default_repr: str | None
    source_default_repr: str | None


@dataclass(frozen=True, slots=True)
class DpgLoadedDump:
    dearpygui_version: str
    function_count: int
    classification_counts: frozendict[str, int]
    functions: frozendict[str, DpgDumpFunctionRecord]
    context_alias_to_factory: frozendict[str, str | None]


@dataclass(frozen=True, slots=True)
class DpgCanonicalMountable:
    """One author-facing semantic item: a canonical ``add_*`` factory plus alias metadata."""

    factory_name: str
    kind_name: str
    record: DpgDumpFunctionRecord
    context_alias_names: tuple[str, ...]


def dearpygui_default_dump_path() -> Path:
    """Path to the checked-in dump under ``scratch/dpg`` (py-rolyze repo root)."""

    here = Path(__file__).resolve()
    repo_root = here.parents[4]
    return repo_root / "scratch" / "dpg" / "dearpygui_api_dump.py"


def _coerce_parameter(raw: Mapping[str, Any]) -> DpgDumpParameter:
    return DpgDumpParameter(
        name=str(raw["name"]),
        kind=str(raw["kind"]),
        annotation=None if raw.get("annotation") is None else str(raw["annotation"]),
        default_repr=None if raw.get("default_repr") is None else str(raw["default_repr"]),
    )


def _coerce_function_record(name: str, raw: Mapping[str, Any]) -> DpgDumpFunctionRecord:
    params_raw = raw.get("parameters") or ()
    parameters = tuple(_coerce_parameter(entry) for entry in params_raw)
    return DpgDumpFunctionRecord(
        name=str(raw.get("name", name)),
        module=str(raw["module"]),
        signature=str(raw["signature"]),
        signature_error=None if raw.get("signature_error") is None else str(raw["signature_error"]),
        doc_summary=str(raw.get("doc_summary", "")),
        classification=str(raw["classification"]),
        reason=str(raw.get("reason", "")),
        alias_of=None if raw.get("alias_of") is None else str(raw["alias_of"]),
        returns_item_handle=bool(raw.get("returns_item_handle", False)),
        parameters=parameters,
        parameter_names=tuple(str(n) for n in raw.get("parameter_names", ())),
        event_params=tuple(str(n) for n in raw.get("event_params", ())),
        source_params=tuple(str(n) for n in raw.get("source_params", ())),
        has_tag_param=bool(raw.get("has_tag_param", False)),
        has_parent_param=bool(raw.get("has_parent_param", False)),
        has_before_param=bool(raw.get("has_before_param", False)),
        has_source_param=bool(raw.get("has_source_param", False)),
        parent_default_repr=(
            None if raw.get("parent_default_repr") is None else str(raw["parent_default_repr"])
        ),
        before_default_repr=(
            None if raw.get("before_default_repr") is None else str(raw["before_default_repr"])
        ),
        source_default_repr=(
            None if raw.get("source_default_repr") is None else str(raw["source_default_repr"])
        ),
    )


def _import_dump_module(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("dearpygui_checked_in_api_dump", path)
    if spec is None or spec.loader is None:
        msg = f"Cannot load DearPyGui dump module from {path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_dearpygui_dump(*, dump_path: Path | None = None) -> DpgLoadedDump:
    """Load ``SUMMARY``, ``FUNCTIONS``, and ``CONTEXT_ALIAS_TO_FACTORY`` from a dump file."""

    path = dearpygui_default_dump_path() if dump_path is None else dump_path
    if not path.is_file():
        msg = f"DearPyGui API dump not found at {path}"
        raise FileNotFoundError(msg)

    mod = _import_dump_module(path)
    summary = getattr(mod, "SUMMARY", {})
    functions_raw: Mapping[str, Mapping[str, Any]] = getattr(mod, "FUNCTIONS", {})
    ctx_raw: Mapping[str, str | None] = getattr(mod, "CONTEXT_ALIAS_TO_FACTORY", {})

    functions = frozendict(
        {name: _coerce_function_record(name, raw) for name, raw in functions_raw.items()}
    )
    context_alias_to_factory = frozendict({str(k): v for k, v in ctx_raw.items()})

    classification_counts = frozendict(
        {str(k): int(v) for k, v in summary.get("classification_counts", {}).items()}
    )

    return DpgLoadedDump(
        dearpygui_version=str(summary.get("dearpygui_version", "")),
        function_count=int(summary.get("function_count", 0)),
        classification_counts=classification_counts,
        functions=functions,
        context_alias_to_factory=context_alias_to_factory,
    )


def _snake_tail_to_pascal(snake: str) -> str:
    return "".join(part[:1].upper() + part[1:] if part else "" for part in snake.split("_"))


def factory_to_kind_name(factory_name: str) -> str:
    """``add_plot_axis`` -> ``PlotAxis``; ``draw_line`` -> ``DrawLine``."""

    if factory_name.startswith("add_"):
        return _snake_tail_to_pascal(factory_name.removeprefix("add_"))
    if factory_name.startswith("draw_"):
        return "Draw" + _snake_tail_to_pascal(factory_name.removeprefix("draw_"))
    msg = f"Expected DearPyGui factory name starting with 'add_' or 'draw_', got {factory_name!r}"
    raise ValueError(msg)


def factory_to_context_aliases(
    context_alias_to_factory: Mapping[str, str | None],
) -> frozendict[str, tuple[str, ...]]:
    """Map ``add_group`` -> ``('group', ...)`` for alias collapse metadata."""

    buckets: dict[str, list[str]] = {}
    for alias, target in context_alias_to_factory.items():
        if target is None:
            continue
        buckets.setdefault(target, []).append(alias)
    return frozendict({factory: tuple(sorted(names)) for factory, names in buckets.items()})


def iter_canonical_mountables(loaded: DpgLoadedDump) -> tuple[DpgCanonicalMountable, ...]:
    """Yield one entry per ``mountable_factory`` ``add_*`` function (aliases folded)."""

    aliases = factory_to_context_aliases(loaded.context_alias_to_factory)
    items: list[DpgCanonicalMountable] = []
    for name, record in sorted(loaded.functions.items(), key=lambda kv: kv[0]):
        if record.classification != "mountable_factory":
            continue
        if not (name.startswith("add_") or name.startswith("draw_")):
            continue
        kind = factory_to_kind_name(name)
        items.append(
            DpgCanonicalMountable(
                factory_name=name,
                kind_name=kind,
                record=record,
                context_alias_names=aliases.get(name, ()),
            )
        )
    return tuple(items)


def classification_for(loaded: DpgLoadedDump, function_name: str) -> str:
    return loaded.functions[function_name].classification


__all__ = [
    "DpgCanonicalMountable",
    "DpgDumpFunctionRecord",
    "DpgDumpParameter",
    "DpgLoadedDump",
    "classification_for",
    "dearpygui_default_dump_path",
    "factory_to_context_aliases",
    "factory_to_kind_name",
    "iter_canonical_mountables",
    "load_dearpygui_dump",
]
