from __future__ import annotations

import ast
from dataclasses import replace
import inspect
from pathlib import Path

from pyrolyze_tools.generate_grouped_native_library import generate_grouped_library_sources
from pyrolyze_tools.generate_semantic_library import DiscoveredParameter, DiscoveredWidgetClass, generate_library_source


def test_partition_preserves_accepted_function_and_spec_ast() -> None:
    widget = DiscoveredWidgetClass("builtins", "Button", "CButton", ())
    accepted = generate_library_source("builtins", (widget,))
    changed = replace(widget, parameters=(DiscoveredParameter("new_argument", inspect.Parameter.KEYWORD_ONLY,
                                                             "str", "''", "new_argument"),))
    output = generate_grouped_library_sources("builtins", (changed,), families={"CButton": "controls"},
                                              maximum_kinds=1, accepted_source=accepted)
    shard = next(source for name, source in output.items() if name.startswith("family_"))
    def nodes(source: str) -> tuple[str, str]:
        library = next(node for node in ast.parse(source).body if isinstance(node, ast.ClassDef))
        method = next(node for node in library.body if isinstance(node, ast.FunctionDef) and node.name == "CButton")
        specs = next(node for node in library.body if isinstance(node, ast.AnnAssign)
                     and isinstance(node.target, ast.Name) and node.target.id == "WIDGET_SPECS")
        return ast.dump(method), ast.dump(specs.value)
    assert nodes(shard) == nodes(accepted)
    stub = ast.parse(output["facade.pyi"])
    method = next(node for node in ast.walk(stub) if isinstance(node, ast.FunctionDef) and node.name == "CButton")
    assert not method.args.kwonlyargs


def test_checked_in_groups_can_supply_the_next_partition(tmp_path: Path) -> None:
    from pyrolyze_tools.generate_grouped_native_library import write_grouped_library
    from pyrolyze_tools.preserve_native_catalog import catalog_source_from_groups, catalog_public_names

    widgets = tuple(DiscoveredWidgetClass("builtins", name, f"C{name}", ()) for name in ("Button", "Row"))
    root = tmp_path / "generated"
    write_grouped_library("builtins", widgets, families={"CButton": "controls", "CRow": "controls"},
                          maximum_kinds=1, output_dir=root)
    source = catalog_source_from_groups(root)
    assert catalog_public_names(source) == {"CButton", "CRow"}
    regrouped = generate_grouped_library_sources("builtins", widgets,
                                                 families={"CButton": "controls", "CRow": "controls"},
                                                 maximum_kinds=2, accepted_source=source)
    assert len([name for name in regrouped if name.startswith("family_")]) == 1
