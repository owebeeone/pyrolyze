from __future__ import annotations

import ast

import pytest

from pyrolyze.api import CallFromNonPyrolyzeContext
from pyrolyze.compiler import (
    PyRolyzeCompileError,
    analyze_source,
    emit_transformed_source,
    load_transformed_namespace,
    lower_plan_to_ast,
)
from pyrolyze.runtime import RenderContext, dirtyof


def test_phase3_emits_private_wrapper_and_lowered_straight_line_body() -> None:
    source = """
from pyrolyze.api import pyrolyse, pyrolyze_slotted

@pyrolyze_slotted
def format_title(name):
    return f"Hello {name}"

def record(value):
    return value

@pyrolyse
def greeting(name):
    title = format_title(name)
    label = title + "!"
    record(label)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.greeting",
        filename="/virtual/example/greeting.py",
    )

    assert "def __pyr_greeting(ctx, __pyr_dirty_state, name):" in transformed
    assert "__pyr_component_ref(__pyr_ComponentMetadata(" in transformed
    assert "__pyr_greeting" in transformed
    assert "__pyr_CallFromNonPyrolyzeContext(" in transformed
    assert "with ctx.pass_scope():" in transformed
    assert "__pyr_title_dirty, title = ctx.call_plain(" in transformed
    assert "ctx.leaf_call(__pyr_slot_2, record, label)" in transformed


def test_phase3_runtime_bridge_executes_generated_component_and_reuses_clean_pass() -> None:
    source = """
from pyrolyze.api import pyrolyse, pyrolyze_slotted

log = []

@pyrolyze_slotted
def format_title(name):
    log.append(("format_title", name))
    return f"Hello {name}"

def record(value):
    log.append(("record", value))

@pyrolyse
def greeting(name):
    title = format_title(name)
    label = title + "!"
    record(label)
"""

    namespace = load_transformed_namespace(
        source,
        module_name="example.bridge",
        filename="/virtual/example/bridge.py",
    )

    greeting = namespace["greeting"]
    ctx = RenderContext()

    with pytest.raises(CallFromNonPyrolyzeContext, match="greeting"):
        greeting("Ada")

    greeting._pyrolyze_meta._func(ctx, dirtyof(name=True), "Ada")
    greeting._pyrolyze_meta._func(ctx, dirtyof(name=False), "Ada")
    greeting._pyrolyze_meta._func(ctx, dirtyof(name=True), "Bea")

    assert namespace["log"] == [
        ("format_title", "Ada"),
        ("record", "Hello Ada!"),
        ("format_title", "Bea"),
        ("record", "Hello Bea!"),
    ]


def test_phase3_lowers_tuple_destructuring_with_result_shape() -> None:
    source = """
from pyrolyze.api import pyrolyse, pyrolyze_slotted

log = []

@pyrolyze_slotted
def use_pair(label):
    log.append(("use_pair", label))
    return (label.upper(), f"set:{label}")

def record_pair(value, setter):
    log.append(("record_pair", value, setter))

@pyrolyse
def pair_panel(label):
    value, setter = use_pair(label)
    record_pair(value, setter)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.pair_panel",
        filename="/virtual/example/pair_panel.py",
    )

    assert "result_shape=('tuple', 2)" in transformed
    assert "(__pyr_value_dirty, __pyr_setter_dirty), (value, setter) = ctx.call_plain(" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.pair_panel",
        filename="/virtual/example/pair_panel.py",
    )
    panel = namespace["pair_panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(label=True), "alpha")
    panel._pyrolyze_meta._func(ctx, dirtyof(label=False), "alpha")
    panel._pyrolyze_meta._func(ctx, dirtyof(label=True), "beta")

    assert namespace["log"] == [
        ("use_pair", "alpha"),
        ("record_pair", "ALPHA", "set:alpha"),
        ("use_pair", "beta"),
        ("record_pair", "BETA", "set:beta"),
    ]


def test_phase3_preserves_instance_class_and_static_wrapper_semantics() -> None:
    source = """
from pyrolyze.api import pyrolyse, pyrolyze_slotted

log = []

@pyrolyze_slotted
def upper(label):
    log.append(("upper", label))
    return label.upper()

def record(value):
    log.append(("record", value))

class Panel:
    def __init__(self, prefix):
        self.prefix = prefix

    @pyrolyse
    def show(self, label):
        value = upper(label)
        record(self.prefix + ":" + value)

    @classmethod
    @pyrolyse
    def build(cls, label):
        value = upper(label)
        record(cls.__name__ + ":" + value)

    @staticmethod
    @pyrolyse
    def static(label):
        value = upper(label)
        record("static:" + value)
"""

    namespace = load_transformed_namespace(
        source,
        module_name="example.panel_methods",
        filename="/virtual/example/panel_methods.py",
    )
    Panel = namespace["Panel"]
    panel = Panel("P")
    ctx = RenderContext()

    with pytest.raises(CallFromNonPyrolyzeContext, match="Panel.show"):
        panel.show("alpha")
    with pytest.raises(CallFromNonPyrolyzeContext, match="Panel.build"):
        Panel.build("beta")
    with pytest.raises(CallFromNonPyrolyzeContext, match="Panel.static"):
        Panel.static("gamma")

    panel.show.__func__._pyrolyze_meta._func(panel, ctx, dirtyof(label=True), "alpha")
    Panel.build.__func__._pyrolyze_meta._func(Panel, ctx, dirtyof(label=True), "beta")
    Panel.static._pyrolyze_meta._func(ctx, dirtyof(label=True), "gamma")

    assert namespace["log"] == [
        ("upper", "alpha"),
        ("record", "P:ALPHA"),
        ("upper", "beta"),
        ("record", "Panel:BETA"),
        ("upper", "gamma"),
        ("record", "static:GAMMA"),
    ]


def test_phase4_still_rejects_unsupported_control_flow() -> None:
    source = """
from pyrolyze.api import pyrolyse

def record(value):
    return value

@pyrolyse
def conditional_panel(flag, label):
    while flag:
        record(label)
"""

    with pytest.raises(PyRolyzeCompileError, match="Phase 04 does not yet lower this control-flow form"):
        emit_transformed_source(
            source,
            module_name="example.conditional_panel",
            filename="/virtual/example/conditional_panel.py",
        )


def test_phase3_copies_source_locations_to_generated_dirty_assignments() -> None:
    source = """
from pyrolyze.api import pyrolyse, pyrolyze_slotted

@pyrolyze_slotted
def format_title(name):
    return f"Hello {name}"

def record(value):
    return value

@pyrolyse
def greeting(name):
    title = format_title(name)
    label = title + "!"
    record(label)
"""

    plan = analyze_source(
        source,
        module_name="example.location_copy",
        filename="/virtual/example/location_copy.py",
    )
    module_ast = lower_plan_to_ast(plan, filename="/virtual/example/location_copy.py")

    dirty_assign = next(
        node
        for node in ast.walk(module_ast)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__pyr_label_dirty" for target in node.targets)
    )

    assert dirty_assign.lineno == 14
    assert dirty_assign.col_offset == 4
