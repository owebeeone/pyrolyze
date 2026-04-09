from __future__ import annotations

import ast
from collections import Counter, defaultdict
from dataclasses import dataclass, field
import importlib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = ("src", "tests", "examples")
GENERATED_MARKERS = (
    "tests/actual_test_results/",
    "tests/data/",
)


@dataclass
class FileUsage:
    path: str
    imports_context: set[str] = field(default_factory=set)
    imports_runtime: set[str] = field(default_factory=set)
    module_attr_uses: Counter[str] = field(default_factory=Counter)
    type_method_calls: dict[str, Counter[str]] = field(default_factory=lambda: defaultdict(Counter))
    constructed_types: Counter[str] = field(default_factory=Counter)


def _is_generated(rel_path: str) -> bool:
    return any(marker in rel_path for marker in GENERATED_MARKERS)


def _iter_python_files() -> list[Path]:
    paths: list[Path] = []
    for dirname in SCAN_DIRS:
        base = ROOT / dirname
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            parts = set(path.parts)
            if "__pycache__" in parts:
                continue
            paths.append(path)
    return sorted(paths)


def _get_exports(module_name: str) -> list[str]:
    module = importlib.import_module(module_name)
    exported = [name for name in vars(module) if not name.startswith("_")]
    return sorted(exported)


def _resolve_constructor_name(node: ast.AST, imported_names: dict[str, str], module_aliases: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        resolved = imported_names.get(node.id)
        return resolved
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        module_name = module_aliases.get(node.value.id)
        if module_name in {"pyrolyze.runtime", "pyrolyze.runtime.context"}:
            return node.attr
    return None


def _bind_assignment_target(target: ast.AST, type_name: str, inferred_vars: dict[str, str]) -> None:
    if isinstance(target, ast.Name):
        inferred_vars[target.id] = type_name
        return
    if isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            if isinstance(elt, ast.Name):
                inferred_vars[elt.id] = type_name


def _record_call_attr(node: ast.Call, inferred_vars: dict[str, str], usage: FileUsage) -> None:
    func = node.func
    if not isinstance(func, ast.Attribute):
        return
    owner = func.value
    if not isinstance(owner, ast.Name):
        return
    inferred_type = inferred_vars.get(owner.id)
    if inferred_type is None:
        return
    usage.type_method_calls[inferred_type][func.attr] += 1


def analyze_file(path: Path) -> FileUsage | None:
    rel_path = path.relative_to(ROOT).as_posix()
    try:
        source = path.read_text()
    except UnicodeDecodeError:
        return None
    try:
        tree = ast.parse(source, filename=rel_path)
    except SyntaxError:
        return None

    usage = FileUsage(path=rel_path)
    imported_names: dict[str, str] = {}
    module_aliases: dict[str, str] = {}
    inferred_vars: dict[str, str] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "pyrolyze.runtime.context":
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    local = alias.asname or alias.name
                    imported_names[local] = alias.name
                    usage.imports_context.add(alias.name)
            elif node.module == "pyrolyze.runtime":
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    local = alias.asname or alias.name
                    imported_names[local] = alias.name
                    usage.imports_runtime.add(alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in {"pyrolyze.runtime", "pyrolyze.runtime.context"}:
                    module_aliases[alias.asname or alias.name] = alias.name

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            ctor_name = _resolve_constructor_name(node.value.func, imported_names, module_aliases)
            if ctor_name is not None:
                usage.constructed_types[ctor_name] += 1
                for target in node.targets:
                    _bind_assignment_target(target, ctor_name, inferred_vars)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and isinstance(node.value, ast.Call):
            ctor_name = _resolve_constructor_name(node.value.func, imported_names, module_aliases)
            if ctor_name is not None:
                usage.constructed_types[ctor_name] += 1
                inferred_vars[node.target.id] = ctor_name

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            module_name = module_aliases.get(node.value.id)
            if module_name in {"pyrolyze.runtime", "pyrolyze.runtime.context"}:
                usage.module_attr_uses[node.attr] += 1
        if isinstance(node, ast.Call):
            _record_call_attr(node, inferred_vars, usage)

    return usage


def _top(counter: Counter[str], limit: int = 20) -> list[tuple[str, int]]:
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:limit]


def build_report() -> str:
    context_exports = _get_exports("pyrolyze.runtime.context")
    runtime_exports = _get_exports("pyrolyze.runtime")

    handwritten: list[FileUsage] = []
    generated: list[FileUsage] = []

    for path in _iter_python_files():
        usage = analyze_file(path)
        if usage is None:
            continue
        if not (usage.imports_context or usage.imports_runtime or usage.module_attr_uses or usage.constructed_types or usage.type_method_calls):
            continue
        if _is_generated(usage.path):
            generated.append(usage)
        else:
            handwritten.append(usage)

    hand_context_imports: Counter[str] = Counter()
    hand_runtime_imports: Counter[str] = Counter()
    hand_module_attrs: Counter[str] = Counter()
    hand_constructed: Counter[str] = Counter()
    hand_methods: dict[str, Counter[str]] = defaultdict(Counter)

    generated_runtime_imports: Counter[str] = Counter()
    generated_module_attrs: Counter[str] = Counter()
    generated_constructed: Counter[str] = Counter()
    generated_methods: dict[str, Counter[str]] = defaultdict(Counter)

    for usage in handwritten:
        hand_context_imports.update(usage.imports_context)
        hand_runtime_imports.update(usage.imports_runtime)
        hand_module_attrs.update(usage.module_attr_uses)
        hand_constructed.update(usage.constructed_types)
        for type_name, methods in usage.type_method_calls.items():
            hand_methods[type_name].update(methods)

    for usage in generated:
        generated_runtime_imports.update(usage.imports_runtime)
        generated_runtime_imports.update(usage.imports_context)
        generated_module_attrs.update(usage.module_attr_uses)
        generated_constructed.update(usage.constructed_types)
        for type_name, methods in usage.type_method_calls.items():
            generated_methods[type_name].update(methods)

    lines: list[str] = []
    lines.append("# Context Runtime Public API Inventory")
    lines.append("")
    lines.append("This report inventories the practical public API surface used across the repo.")
    lines.append("It distinguishes hand-written consumers from generated/golden imports.")
    lines.append("")
    lines.append("## Exported Module Surfaces")
    lines.append("")
    lines.append(f"- `pyrolyze.runtime.context` non-private exports: {len(context_exports)}")
    lines.append(f"- `pyrolyze.runtime` non-private exports: {len(runtime_exports)}")
    lines.append("")
    lines.append("## Hand-Written Import Surface")
    lines.append("")
    lines.append(f"- Files importing `pyrolyze.runtime` or `pyrolyze.runtime.context`: {len(handwritten)}")
    lines.append("")
    lines.append("### Top `pyrolyze.runtime.context` direct imports")
    lines.append("")
    for name, count in _top(hand_context_imports):
        lines.append(f"- `{name}`: {count}")
    if not hand_context_imports:
        lines.append("- none")
    lines.append("")
    lines.append("### Top `pyrolyze.runtime` direct imports")
    lines.append("")
    for name, count in _top(hand_runtime_imports):
        lines.append(f"- `{name}`: {count}")
    if not hand_runtime_imports:
        lines.append("- none")
    lines.append("")
    lines.append("### Module attribute access via imported runtime modules")
    lines.append("")
    for name, count in _top(hand_module_attrs):
        lines.append(f"- `{name}`: {count}")
    if not hand_module_attrs:
        lines.append("- none")
    lines.append("")
    lines.append("### Constructed Runtime Types")
    lines.append("")
    for name, count in _top(hand_constructed):
        lines.append(f"- `{name}`: {count}")
    if not hand_constructed:
        lines.append("- none")
    lines.append("")
    lines.append("## Inferred Instance Method Usage")
    lines.append("")
    for type_name in sorted(hand_methods):
        lines.append(f"### `{type_name}`")
        lines.append("")
        for method_name, count in _top(hand_methods[type_name]):
            lines.append(f"- `{method_name}`: {count}")
        lines.append("")
    if not hand_methods:
        lines.append("- no inferred instance methods")
        lines.append("")
    lines.append("## Generated / Golden Import Surface")
    lines.append("")
    lines.append("These are imports found under generated/golden trees. They matter for codegen compatibility and lowering-facing public API.")
    lines.append("")
    for name, count in _top(generated_runtime_imports):
        lines.append(f"- `{name}`: {count}")
    if not generated_runtime_imports:
        lines.append("- none")
    lines.append("")
    lines.append("### Generated / Lowering Constructed Types")
    lines.append("")
    for name, count in _top(generated_constructed):
        lines.append(f"- `{name}`: {count}")
    if not generated_constructed:
        lines.append("- none")
    lines.append("")
    lines.append("### Generated / Lowering Inferred Instance Method Usage")
    lines.append("")
    for type_name in sorted(generated_methods):
        lines.append(f"#### `{type_name}`")
        lines.append("")
        for method_name, count in _top(generated_methods[type_name]):
            lines.append(f"- `{method_name}`: {count}")
        lines.append("")
    if not generated_methods:
        lines.append("- no inferred lowering methods")
        lines.append("")
    lines.append("## Hand-Written Consumer Files")
    lines.append("")
    for usage in sorted(handwritten, key=lambda item: item.path):
        imported = sorted(usage.imports_context | usage.imports_runtime)
        module_attrs = sorted(usage.module_attr_uses)
        lines.append(f"- `{usage.path}`")
        if imported:
            lines.append(f"  - imports: {', '.join(f'`{name}`' for name in imported)}")
        if module_attrs:
            lines.append(f"  - module attrs: {', '.join(f'`{name}`' for name in module_attrs)}")
        constructed = sorted(usage.constructed_types)
        if constructed:
            lines.append(f"  - constructed: {', '.join(f'`{name}`' for name in constructed)}")
    lines.append("")
    lines.append("## Initial Design Implications")
    lines.append("")
    lines.append("- The external design target should be the combined surface of `pyrolyze.runtime.context` and the `pyrolyze.runtime` re-export layer, not every helper inside `context_original.py`.")
    lines.append("- `RenderContext`, `ModuleRegistry`, `SlotId`, `dirtyof`, and several slot-context classes are part of the practical public API.")
    lines.append("- Many behaviors are specified by tests rather than by broad import usage, especially context-manager protocols and UI ordering invariants.")
    return "\n".join(lines) + "\n"


def main() -> None:
    print(build_report())


if __name__ == "__main__":
    main()
