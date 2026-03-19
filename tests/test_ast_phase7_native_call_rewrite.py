from __future__ import annotations

from pyrolyze.api import UIElement
from pyrolyze.compiler import emit_transformed_source, load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof


def test_phase7_lowers_call_native_factory_calls() -> None:
    source = """
from pyrolyze.api import Label, call_native, pyrolyse

@pyrolyse
def label_panel(text):
    call_native(Label)(text=text)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase7.label_panel",
        filename="/virtual/example/phase7/label_panel.py",
    )

    assert "__pyr_ctx.call_native(Label, text=text)" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase7.label_panel",
        filename="/virtual/example/phase7/label_panel.py",
    )
    panel = namespace["label_panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(text=True), "Hello")
    assert ctx.debug_ui() == (
        UIElement(kind="Label", props={"text": "Hello"}),
    )

    panel._pyrolyze_meta._func(ctx, dirtyof(text=False), "Hello")
    assert ctx.debug_ui() == (
        UIElement(kind="Label", props={"text": "Hello"}),
    )
