from __future__ import annotations

import ast

import pytest

from pyrolyze.api import CallFromNonPyrolyzeContext
from pyrolyze.compiler import (
    PyRolyzeCompileError,
    analyze_source,
    compile_source,
    emit_transformed_source,
    load_transformed_namespace,
    lower_plan_to_ast,
    TransformFlags,
)
from pyrolyze.runtime import RenderContext, SlotId, dirtyof


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

    assert "def __pyr_greeting(__pyr_ctx, __pyr_dirty_state, name):" in transformed
    assert "__pyr_component_ref(__pyr_ComponentMetadata(" in transformed
    assert "__pyr_greeting" in transformed
    assert "__pyr_CallFromNonPyrolyzeContext(" in transformed
    assert "with __pyr_ctx.pass_scope():" in transformed
    assert "__pyr_title_dirty, title = __pyr_ctx.call_plain(" in transformed
    assert "record(label)" in transformed
    assert ".leaf_call(" not in transformed


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
    assert "(__pyr_value_dirty, __pyr_setter_dirty), (value, setter) = __pyr_ctx.call_plain(" in transformed

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
        ("record_pair", "ALPHA", "set:alpha"),
        ("use_pair", "beta"),
        ("record_pair", "BETA", "set:beta"),
    ]


def test_phase3_lowers_slot_callable_parameters_and_return_typed_locals() -> None:
    source = """
from typing import Callable

from pyrolyze.api import SlotCallable, pyrolyse, pyrolyze_slotted

log = []

def choose_formatter(prefix: str) -> SlotCallable[[str], str]:
    return format_with_prefix

@pyrolyze_slotted
def format_with_prefix(label: str) -> str:
    return label

def record(value: str) -> None:
    log.append(("record", value))

@pyrolyse
def panel(prefix: str, formatter: SlotCallable[[str], str], plain: Callable[[str], str]) -> None:
    selected = choose_formatter(prefix)
    value = formatter(prefix)
    selected_value = selected(value)
    plain_value = plain(selected_value)
    record(plain_value)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase3.slot_callable_param",
        filename="/virtual/example/phase3/slot_callable_param.py",
    )

    assert transformed.count(".call_plain(") == 2
    assert "plain_value = plain(selected_value)" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase3.slot_callable_param",
        filename="/virtual/example/phase3/slot_callable_param.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    def plain(value: str) -> str:
        return f"plain:{value}"

    panel._pyrolyze_meta._func(ctx, dirtyof(prefix=True, formatter=True, plain=True), "x", namespace["format_with_prefix"], plain)
    assert namespace["log"] == [("record", "plain:x")]


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


def test_phase3_component_call_binds_classmethod_and_staticmethod_from_class_and_instance() -> None:
    source = """
from pyrolyze.api import pyrolyse

log = []

class Panel:
    def __init__(self, prefix):
        self.prefix = prefix

    @classmethod
    @pyrolyse
    def build(cls, label):
        log.append(("class", cls.__name__, label))

    @staticmethod
    @pyrolyse
    def static(label):
        log.append(("static", label))
"""

    namespace = load_transformed_namespace(
        source,
        module_name="example.panel_method_dispatch",
        filename="/virtual/example/panel_method_dispatch.py",
    )
    Panel = namespace["Panel"]
    panel = Panel("P")
    ctx = RenderContext()

    with ctx.pass_scope():
        ctx.component_call(
            SlotId(901, 1, line_no=1),
            Panel.build,
            "alpha",
            dirty_state=dirtyof(label=True),
        )
        ctx.component_call(
            SlotId(901, 2, line_no=2),
            panel.build,
            "beta",
            dirty_state=dirtyof(label=True),
        )
        ctx.component_call(
            SlotId(901, 3, line_no=3),
            Panel.static,
            "gamma",
            dirty_state=dirtyof(label=True),
        )
        ctx.component_call(
            SlotId(901, 4, line_no=4),
            panel.static,
            "delta",
            dirty_state=dirtyof(label=True),
        )

    assert namespace["log"] == [
        ("class", "Panel", "alpha"),
        ("class", "Panel", "beta"),
        ("static", "gamma"),
        ("static", "delta"),
    ]


def test_phase3_rewrites_nested_components_inside_plain_factories() -> None:
    source = """
from pyrolyze.api import ComponentRef, pyrolyse, pyrolyze_slotted

log = []

@pyrolyze_slotted
def upper(label):
    log.append(("upper", label))
    return label.upper()

def record(value):
    log.append(("record", value))

def make_panel(prefix) -> ComponentRef[[str]]:
    @pyrolyse
    def panel(label):
        value = upper(label)
        record(prefix + ":" + value)

    return panel
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.nested_factory",
        filename="/virtual/example/nested_factory.py",
    )

    assert "def __pyr_make_panel___locals___panel(__pyr_ctx, __pyr_dirty_state, label):" in transformed
    assert "@__pyr_component_ref(__pyr_ComponentMetadata('make_panel.<locals>.panel'" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.nested_factory",
        filename="/virtual/example/nested_factory.py",
    )
    panel = namespace["make_panel"]("P")
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(label=True), "alpha")
    panel._pyrolyze_meta._func(ctx, dirtyof(label=False), "alpha")
    panel._pyrolyze_meta._func(ctx, dirtyof(label=True), "beta")

    assert namespace["log"] == [
        ("upper", "alpha"),
        ("record", "P:ALPHA"),
        ("record", "P:ALPHA"),
        ("upper", "beta"),
        ("record", "P:BETA"),
    ]


def test_phase3_warns_when_factory_return_annotation_is_not_component_ref() -> None:
    source = """
from collections.abc import Callable

from pyrolyze.api import pyrolyse

def make_panel(prefix: str) -> Callable[[str], None]:
    @pyrolyse
    def panel(label: str) -> None:
        print(prefix, label)

    return panel
"""

    plan = analyze_source(
        source,
        module_name="example.nested_factory_warning",
        filename="/virtual/example/nested_factory_warning.py",
    )

    assert [diagnostic.code for diagnostic in plan.diagnostics] == [
        "PYR-W-COMPONENT-RETURN-TYPE",
    ]
    assert "ComponentRef[[str]]" in plan.diagnostics[0].message

    artifact = compile_source(
        source,
        module_name="example.nested_factory_warning",
        filename="/virtual/example/nested_factory_warning.py",
    )
    assert [warning.code for warning in artifact.warnings] == [
        "PYR-W-COMPONENT-RETURN-TYPE",
    ]


def test_phase3_can_promote_component_return_type_warning_to_error() -> None:
    source = """
from collections.abc import Callable

from pyrolyze.api import pyrolyse

def make_panel(prefix: str) -> Callable[[str], None]:
    @pyrolyse
    def panel(label: str) -> None:
        print(prefix, label)

    return panel
"""

    with pytest.raises(PyRolyzeCompileError, match="ComponentRef\\[\\[str\\]\\]"):
        emit_transformed_source(
            source,
            module_name="example.nested_factory_warning_error",
            filename="/virtual/example/nested_factory_warning_error.py",
            flags=TransformFlags(warnings_as_errors=True),
        )


def test_phase3_rewrites_nested_components_inside_class_factories() -> None:
    source = """
from pyrolyze.api import ComponentRef, pyrolyse, pyrolyze_slotted

log = []

@pyrolyze_slotted
def upper(label):
    log.append(("upper", label))
    return label.upper()

def record(value):
    log.append(("record", value))

class PanelFactory:
    def __init__(self, prefix):
        self.prefix = prefix

    def make(self) -> ComponentRef[[str]]:
        @pyrolyse
        def panel(label):
            value = upper(label)
            record(self.prefix + ":" + value)

        return panel
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.nested_method_factory",
        filename="/virtual/example/nested_method_factory.py",
    )

    assert "def __pyr_PanelFactory__make___locals___panel(__pyr_ctx, __pyr_dirty_state, label):" in transformed
    assert "PanelFactory.make.<locals>.panel" in transformed
    assert "__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=21, is_top_level=True)" in transformed
    assert "globals()['__pyr_slot_1']" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.nested_method_factory",
        filename="/virtual/example/nested_method_factory.py",
    )
    factory = namespace["PanelFactory"]("P")
    panel = factory.make()
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(label=True), "alpha")
    panel._pyrolyze_meta._func(ctx, dirtyof(label=False), "alpha")
    panel._pyrolyze_meta._func(ctx, dirtyof(label=True), "beta")

    assert namespace["log"] == [
        ("upper", "alpha"),
        ("record", "P:ALPHA"),
        ("record", "P:ALPHA"),
        ("upper", "beta"),
        ("record", "P:BETA"),
    ]


def test_phase3_supports_imported_pyrolyze_decorator_aliases() -> None:
    source = """
from pyrolyze.api import pyrolyse as component, pyrolyze_slotted as slotted

log = []

@slotted
def upper(label):
    log.append(("upper", label))
    return label.upper()

def record(value):
    log.append(("record", value))

@component
def panel(label):
    value = upper(label)
    record(value)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.imported_aliases",
        filename="/virtual/example/imported_aliases.py",
    )

    assert "def __pyr_panel(__pyr_ctx, __pyr_dirty_state, label):" in transformed
    assert "__pyr_value_dirty, value = __pyr_ctx.call_plain(" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.imported_aliases",
        filename="/virtual/example/imported_aliases.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(label=True), "alpha")
    panel._pyrolyze_meta._func(ctx, dirtyof(label=False), "alpha")
    panel._pyrolyze_meta._func(ctx, dirtyof(label=True), "beta")

    assert namespace["log"] == [
        ("upper", "alpha"),
        ("record", "ALPHA"),
        ("record", "ALPHA"),
        ("upper", "beta"),
        ("record", "BETA"),
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
