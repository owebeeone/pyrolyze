"""Preserve an accepted emitted catalog while changing its storage partition."""

from __future__ import annotations

import ast
from collections.abc import Mapping
from pathlib import Path


def _library(tree: ast.Module) -> ast.ClassDef:
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    if len(classes) != 1:
        raise ValueError("catalog must contain one library class")
    return classes[0]


def _specs(library: ast.ClassDef) -> ast.Dict:
    assignment = next(node for node in library.body if isinstance(node, ast.AnnAssign)
                      and isinstance(node.target, ast.Name) and node.target.id == "WIDGET_SPECS")
    if not isinstance(assignment.value, ast.Call) or not isinstance(assignment.value.args[0], ast.Dict):
        raise ValueError("invalid emitted spec dictionary")
    return assignment.value.args[0]


def catalog_public_names(source: str) -> set[str]:
    return {node.name for node in _library(ast.parse(source)).body
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")}


def _segment(lines: list[bytes], node: ast.expr) -> str:
    if node.end_lineno is None or node.end_col_offset is None:
        raise ValueError("catalog expression has no source boundary")
    start, end = node.lineno - 1, node.end_lineno - 1
    if start == end:
        return lines[start][node.col_offset:node.end_col_offset].decode("utf-8")
    return (lines[start][node.col_offset:] + b"".join(lines[start + 1:end])
            + lines[end][:node.end_col_offset]).decode("utf-8")


def catalog_source_from_groups(directory: Path) -> str:
    """Reconstruct offline emitter input from a validated accepted generation."""
    from pyrolyze_tools.generated_library_publication import require_admitted_generation

    require_admitted_generation(directory)
    facade_source = (directory / "facade.py").read_text()
    facade = _library(ast.parse(facade_source))
    values: dict[str, str] = {}
    functions: dict[str, str] = {}
    element_helper = ""
    header = ""
    for path in sorted(directory.glob("family_*.py")):
        source = path.read_text()
        lines = source.splitlines(keepends=True)
        byte_lines = source.encode("utf-8").splitlines(keepends=True)
        library = _library(ast.parse(source))
        if not header:
            start = min(item.lineno for item in [library, *library.decorator_list]) - 1
            header = "".join(lines[:start])
        specs = _specs(library)
        for key, value in zip(specs.keys, specs.values, strict=True):
            kind = ast.literal_eval(key)
            if kind in values:
                raise ValueError("duplicate accepted kind")
            values[kind] = _segment(byte_lines, value)
        for node in library.body:
            if isinstance(node, ast.FunctionDef) and node.name == "__element" and not element_helper:
                start = min(item.lineno for item in [node, *node.decorator_list]) - 1
                element_helper = "".join(lines[start:node.end_lineno])
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                if node.name in functions:
                    raise ValueError("duplicate accepted callable")
                start = min(item.lineno for item in [node, *node.decorator_list]) - 1
                functions[node.name] = "".join(lines[start:node.end_lineno])
    if not header:
        raise ValueError("accepted catalog has no groups")
    body = ""
    facade_lines = facade_source.splitlines(keepends=True)
    for node in facade.body:
        keep = (isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "UI_INTERFACE"
                                                    for target in node.targets))
        keep = keep or isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "ROOT_MODULE"
        keep = keep or isinstance(node, ast.ClassDef) and node.name == "mounts"
        keep = keep or isinstance(node, ast.FunctionDef) and node.name == "__element" and not element_helper
        if keep:
            start = min(item.lineno for item in [node, *getattr(node, "decorator_list", [])]) - 1
            body += "".join(facade_lines[start:node.end_lineno]) + "\n"
    # The facade's generic helper omits accepted comments between decorator/body.
    body += element_helper + "\n"
    body += "    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({\n"
    body += "".join(f"        {kind!r}: {value},\n" for kind, value in sorted(values.items())) + "    })\n\n"
    body += "\n\n".join(functions[name] for name in sorted(functions)) + "\n"
    return header + f"@ui_interface\nclass {facade.name}:\n" + body


def preserve_catalog(sources: Mapping[str, str], accepted_source: str) -> dict[str, str]:
    """Use AST-owned ranges, including decorators, without rewriting accepted bodies."""
    accepted = _library(ast.parse(accepted_source))
    accepted_lines = accepted_source.splitlines(keepends=True)
    byte_lines = accepted_source.encode("utf-8").splitlines(keepends=True)
    functions = {node.name: node for node in accepted.body if isinstance(node, ast.FunctionDef)}
    accepted_specs = _specs(accepted)
    # Split once: ast.get_source_segment otherwise rescans the catalog per kind.
    values = {ast.literal_eval(key): _segment(byte_lines, value)
              for key, value in zip(accepted_specs.keys, accepted_specs.values, strict=True)}
    result = dict(sources)
    for name, source in sources.items():
        if not name.startswith("family_") or not name.endswith(".py"):
            continue
        library = _library(ast.parse(source))
        lines = source.splitlines(keepends=True)
        edits: list[tuple[int, int, str]] = []
        for node in library.body:
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "WIDGET_SPECS":
                kinds = [ast.literal_eval(key) for key in _specs(library).keys]
                replacement = "    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({\n"
                replacement += "".join(f"        {kind!r}: {values[kind]},\n" for kind in kinds)
                replacement += "    })\n"
                edits.append((node.lineno - 1, node.end_lineno, replacement))
            elif isinstance(node, ast.FunctionDef) and node.name in functions:
                original = functions[node.name]
                start = min(item.lineno for item in [node, *node.decorator_list]) - 1
                original_start = min(item.lineno for item in [original, *original.decorator_list]) - 1
                edits.append((start, node.end_lineno, "".join(accepted_lines[original_start:original.end_lineno])))
        for start, end, replacement in sorted(edits, reverse=True):
            lines[start:end] = [replacement]
        result[name] = "".join(lines)
    stub = sources["facade.pyi"]
    lines = stub.splitlines(keepends=True)
    edits = []
    for node in _library(ast.parse(stub)).body:
        if isinstance(node, ast.FunctionDef):
            original = functions[node.name]
            start = min(item.lineno for item in [node, *node.decorator_list]) - 1
            header = "".join(accepted_lines[original.lineno - 1:original.body[0].lineno - 1])
            edits.append((start, node.end_lineno, "    @classmethod\n" + header + "        ...\n"))
    for start, end, replacement in sorted(edits, reverse=True):
        lines[start:end] = [replacement]
    result["facade.pyi"] = "".join(lines)
    return result
