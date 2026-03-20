from __future__ import annotations

from pyrolyze.compiler import emit_transformed_source, load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof


def test_ui_element_helpers_export_component_refs_for_core_kinds() -> None:
    from pyrolyze.ui import elements as ui_elements

    names = (
        "section",
        "row",
        "badge",
        "button",
        "text_field",
        "toggle",
        "select_field",
    )
    for name in names:
        helper = getattr(ui_elements, name)
        assert hasattr(helper, "_pyrolyze_meta"), name


def test_compiler_lowers_imported_ui_helpers_and_runtime_emits_expected_tree() -> None:
    source = """
from pyrolyze.api import pyrolyse
from pyrolyze.ui.elements import badge, section

@pyrolyse
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
