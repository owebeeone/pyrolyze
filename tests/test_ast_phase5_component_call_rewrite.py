from __future__ import annotations

from pyrolyze.compiler import emit_transformed_source, load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof
from pyrolyze_testsupport import imported_annotations as imported_support


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
    assert "__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=15, is_top_level=True)" in transformed
    assert "__pyr_slot_2 =" not in transformed

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


def test_phase5_lowers_imported_annotated_functions_correctly() -> None:
    source = """
from pyrolyze.api import pyrolyse
from pyrolyze_testsupport.imported_annotations import imported_child, imported_upper

log = []

def record(value):
    log.append(("record", value))

@pyrolyse
def imported_panel(text):
    value = imported_upper(text)
    record(value)
    imported_child(value)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase5.imported_panel",
        filename="/virtual/example/phase5/imported_panel.py",
    )

    assert ".call_plain(" in transformed
    assert "imported_upper" in transformed
    assert ".component_call(" in transformed
    assert "imported_child" in transformed

    imported_support.reset_logs()
    namespace = load_transformed_namespace(
        source,
        module_name="example.phase5.imported_panel",
        filename="/virtual/example/phase5/imported_panel.py",
    )
    panel = namespace["imported_panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(text=True), "Hello")
    panel._pyrolyze_meta._func(ctx, dirtyof(text=False), "Hello")
    panel._pyrolyze_meta._func(ctx, dirtyof(text=True), "World")

    assert namespace["log"] == [
        ("record", "HELLO"),
        ("record", "HELLO"),
        ("record", "WORLD"),
    ]
    assert imported_support.LOG == [
        ("upper", "Hello"),
        ("badge", "HELLO", "info"),
        ("upper", "World"),
        ("badge", "WORLD", "info"),
    ]
