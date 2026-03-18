from __future__ import annotations

from pyrolyze.compiler import emit_transformed_source, load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof


def test_phase5_lowers_direct_component_calls_to_component_call() -> None:
    source = """
from pyrolyze.api import pyrolyse

log = []

def badge(text, *, tone):
    log.append(("badge", text, tone))

@pyrolyse
def child_badge(text):
    badge(text, tone="info")

@pyrolyse
def parent_panel(text):
    child_badge(text)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase5.parent_panel",
        filename="/virtual/example/phase5/parent_panel.py",
    )

    assert ".component_call(" in transformed
    assert "dirty_state=__pyr_dirtyof(text=__pyr_dirty_state.text)" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase5.parent_panel",
        filename="/virtual/example/phase5/parent_panel.py",
    )
    panel = namespace["parent_panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(text=True), "Hello")
    assert namespace["log"] == [("badge", "Hello", "info")]

    panel._pyrolyze_meta._func(ctx, dirtyof(text=False), "Hello")
    assert namespace["log"] == [("badge", "Hello", "info")]

    panel._pyrolyze_meta._func(ctx, dirtyof(text=True), "World")
    assert namespace["log"] == [
        ("badge", "Hello", "info"),
        ("badge", "World", "info"),
    ]
