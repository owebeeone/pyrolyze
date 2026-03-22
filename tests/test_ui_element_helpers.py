from __future__ import annotations

from pathlib import Path

from pyrolyze.compiler import emit_transformed_source, load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof


def test_ui_element_helpers_export_component_refs_for_core_kinds() -> None:
    from pyrolyze import ui

    helpers = (
        ui.section,
        ui.row,
        ui.badge,
        ui.button,
        ui.text_field,
        ui.toggle,
        ui.select_field,
    )
    for helper in helpers:
        assert hasattr(helper, "_pyrolyze_meta"), helper.__name__
        assert helper.__module__ == "pyrolyze.ui.elements_pyr"


def test_ui_element_source_mirror_is_regular_pyrolyze_syntax() -> None:
    from pyrolyze import ui

    source_path = Path(ui.__file__).with_name("elements.py")
    source = source_path.read_text(encoding="utf-8")

    assert "@pyrolyze" in source
    assert "def section(" in source


def test_compiler_lowers_imported_ui_helpers_and_runtime_emits_expected_tree() -> None:
    source = """
from pyrolyze.api import pyrolyze
from pyrolyze.ui import badge, section

@pyrolyze
def panel(text):
    with section("Root", accent="blue"):
        badge(text, tone="info")
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.ui_helpers.panel",
        filename="/virtual/example/ui_helpers/panel.py",
    )

    assert ".container_call(" in transformed
    assert ".component_call(" in transformed
    assert "section" in transformed
    assert "badge" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.ui_helpers.panel",
        filename="/virtual/example/ui_helpers/panel.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(text=True), "Hello")
    committed = ctx.committed_ui()

    assert len(committed) == 1
    root = committed[0]
    assert root.kind == "section"
    assert root.props["title"] == "Root"
    assert len(root.children) == 1
    child = root.children[0]
    assert child.kind == "badge"
    assert child.props["text"] == "Hello"
    assert child.props["tone"] == "info"
