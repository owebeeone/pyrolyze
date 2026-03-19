from __future__ import annotations

import ast
from pathlib import Path
import sys

import pytest

from pyrolyze.compiler import emit_transformed_source
from tests.versioned_test_harness import actual_results_dir


_GOLDENS_DIR = Path(__file__).parent / "v3_14" / "goldens"
_GOLD_SRC_DIR = Path(__file__).parent / "v3_14" / "gold_src"
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_ACTUAL_GOLDENS_DIR = actual_results_dir(
    _PROJECT_ROOT,
    runtime_version=(sys.version_info.major, sys.version_info.minor),
    kernel_tag="v3_14",
) / "goldens"


_CASES: dict[str, str] = {
    "phase3_greeting.py": "golden.phase3.greeting",
    "phase3_panel_methods.py": "golden.phase3.panel_methods",
    "phase3_nested_factory.py": "golden.phase3.nested_factory",
    "phase3_nested_method_factory.py": "golden.phase3.nested_method_factory",
    "phase3_imported_aliases.py": "golden.phase3.imported_aliases",
    "phase4_stats_panel.py": "golden.phase4.stats_panel",
    "phase4_nested_grid.py": "golden.phase4.nested_grid",
    "phase4_nested_pair_panel.py": "golden.phase4.nested_pair_panel",
    "phase5_parent_panel.py": "golden.phase5.parent_panel",
    "phase5_method_structures.py": "golden.phase5.method_structures",
    "phase5_imported_annotations.py": "golden.phase5.imported_annotations",
    "phase7_label_panel.py": "golden.phase7.label_panel",
}


def test_golden_fixture_sets_match() -> None:
    source_names = {path.name for path in _GOLD_SRC_DIR.glob("*.py")}
    golden_names = {path.name for path in _GOLDENS_DIR.glob("*.py")}

    assert source_names == set(_CASES)
    assert golden_names == set(_CASES)


def test_golden_sources_are_tagged_for_pyrolyte() -> None:
    for golden_name in _CASES:
        lines = (_GOLD_SRC_DIR / golden_name).read_text(encoding="utf-8").splitlines()
        assert lines[0].strip() == "#@pyrolyte"


def test_golden_sources_are_fully_type_annotated() -> None:
    for golden_name in _CASES:
        module = ast.parse((_GOLD_SRC_DIR / golden_name).read_text(encoding="utf-8"))
        for node in ast.walk(module):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            assert node.returns is not None, f"{golden_name}: {node.name} is missing a return annotation"
            for argument in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]:
                if argument.arg in {"self", "cls"}:
                    continue
                assert argument.annotation is not None, (
                    f"{golden_name}: {node.name} parameter '{argument.arg}' is missing an annotation"
                )
            if node.args.vararg is not None:
                assert node.args.vararg.annotation is not None, (
                    f"{golden_name}: {node.name} vararg '*{node.args.vararg.arg}' is missing an annotation"
                )
            if node.args.kwarg is not None:
                assert node.args.kwarg.annotation is not None, (
                    f"{golden_name}: {node.name} kwarg '**{node.args.kwarg.arg}' is missing an annotation"
                )


@pytest.mark.parametrize(
    ("golden_name", "module_name"),
    list(_CASES.items()),
)
def test_transformed_source_matches_v3_14_golden(
    golden_name: str,
    module_name: str,
) -> None:
    source_path = _GOLD_SRC_DIR / golden_name
    transformed = emit_transformed_source(
        source_path.read_text(encoding="utf-8"),
        module_name=module_name,
        filename=str(source_path),
    )
    _ACTUAL_GOLDENS_DIR.mkdir(parents=True, exist_ok=True)
    (_ACTUAL_GOLDENS_DIR / golden_name).write_text(transformed + "\n", encoding="utf-8")

    expected = _read_golden(_GOLDENS_DIR / golden_name)
    assert transformed == expected


def _read_golden(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text[:-1] if text.endswith("\n") else text
