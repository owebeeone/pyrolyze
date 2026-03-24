from __future__ import annotations

from pyrolyze.backends.model import TypeRef
from pyrolyze.runtime import RenderContext, dirtyof
from pyrolyze.testing.generic_backend import (
    BuildPyroNodeBackend,
    MountInterfaceKind,
    MountSpec,
    NodeGenSpec,
    ParamSpec,
    run_pyro_ui,
)


def _source_specs() -> tuple[NodeGenSpec, ...]:
    return (
        NodeGenSpec(
            name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
        ),
        NodeGenSpec(
            name="text",
            base_name="node",
            constructor=(
                ParamSpec(name="name", annotation=TypeRef("str")),
                ParamSpec(name="text", annotation=TypeRef("str")),
            ),
        ),
        NodeGenSpec(
            name="row",
            base_name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            mounts=(
                MountSpec(
                    name="child",
                    accepted_base="node",
                    interface=MountInterfaceKind.ORDERED,
                    default=True,
                ),
            ),
        ),
    )


def test_generated_source_module_text_uses_regular_author_style_pyrolyze_syntax() -> None:
    backend = BuildPyroNodeBackend(_source_specs(), module_name="example.generic_backend.source")

    source = backend.source_module_text()

    assert "@pyrolyze" in source
    assert "def text(" in source
    assert "def row(" in source
    assert "call_native(UIElement)" in source


def test_generated_source_namespace_matches_direct_helper_ui_output_for_simple_node() -> None:
    backend = BuildPyroNodeBackend(_source_specs(), module_name="example.generic_backend.source_match")
    direct_text = backend.pyro_func("text")
    source_text = backend.source_namespace()["text"]

    direct_ctx = RenderContext()
    source_ctx = RenderContext()

    direct_text._pyrolyze_meta._func(direct_ctx, dirtyof(name=True, text=True), "leaf", "hello")
    source_text._pyrolyze_meta._func(source_ctx, dirtyof(name=True, text=True), "leaf", "hello")

    assert run_pyro_ui(direct_ctx) == run_pyro_ui(source_ctx)
