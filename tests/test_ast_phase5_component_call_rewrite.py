from __future__ import annotations

from pyrolyze.compiler import emit_transformed_source, load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof
from pyrolyze_testsupport import imported_annotations as imported_support


def test_phase5_lowers_direct_component_calls_to_component_call() -> None:
    source = """
from pyrolyze.api import pyrolyze

log = []

def badge(text, *, tone):
    log.append(("badge", text, tone))

@pyrolyze
def child_badge(text):
    badge(text, tone="info")

@pyrolyze
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
from pyrolyze.api import pyrolyze
from pyrolyze_testsupport.imported_annotations import imported_child, imported_upper

log = []

def record(value):
    log.append(("record", value))

@pyrolyze
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


def test_phase5_lowers_pyrolyze_handler_event_params_and_keeps_plain_callables_plain() -> None:
    source = """
from typing import Callable

from pyrolyze.api import PyrolyzeHandler as ClickHandler, UIElement, call_native, pyrolyze

log = []

@pyrolyze
def button(
    label: str,
    *,
    on_press: ClickHandler[[], None] | None = None,
    formatter: Callable[[str], str] | None = None,
) -> None:
    display = formatter(label) if formatter is not None else label
    call_native(UIElement)(
        kind="button",
        props={"label": display, "on_press": on_press},
    )

@pyrolyze
def panel(name: str) -> None:
    button(
        "Save",
        on_press=lambda: log.append(name),
        formatter=lambda value: f"[{value}]",
    )
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase5.event_handler_local",
        filename="/virtual/example/phase5/event_handler_local.py",
    )

    assert ".event_handler(" in transformed
    assert "on_press=__pyr_ctx.event_handler(" in transformed
    assert "callback=lambda: log.append(name)" in transformed
    assert "formatter=lambda value: f'[{value}]'" in transformed
    assert "formatter=__pyr_ctx.event_handler(" not in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase5.event_handler_local",
        filename="/virtual/example/phase5/event_handler_local.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(name=True), "Ada")
    (button_node,) = ctx.committed_ui()
    dispatch = button_node.props["on_press"]
    assert button_node.props["label"] == "[Save]"
    assert callable(dispatch)

    dispatch()
    assert namespace["log"] == ["Ada"]

    panel._pyrolyze_meta._func(ctx, dirtyof(name=True), "Bea")
    (updated_button_node,) = ctx.committed_ui()
    updated_dispatch = updated_button_node.props["on_press"]

    assert updated_button_node.props["label"] == "[Save]"
    assert updated_dispatch is dispatch

    updated_dispatch()
    assert namespace["log"] == ["Ada", "Bea"]


def test_phase5_lowers_qualified_pyrolyze_handler_annotations() -> None:
    source = """
import pyrolyze.api as pyr

@pyr.pyrolyze
def button(
    label: str,
    *,
    on_press: pyr.PyrolyzeHandler[[], None] | None = None,
) -> None:
    pyr.call_native(pyr.UIElement)(
        kind="button",
        props={"label": label, "on_press": on_press},
    )

@pyr.pyrolyze
def panel(name: str) -> None:
    button("Save", on_press=lambda: print(name))
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase5.event_handler_qualified",
        filename="/virtual/example/phase5/event_handler_qualified.py",
    )

    assert "on_press=__pyr_ctx.event_handler(" in transformed
    assert "callback=lambda: print(name)" in transformed


def test_phase5_lowers_imported_component_event_params_from_runtime_annotations() -> None:
    source = """
from pyrolyze.api import pyrolyze
from pyrolyze_testsupport.imported_annotations import imported_button

log = []

@pyrolyze
def panel(name: str) -> None:
    imported_button("Save", on_press=lambda: log.append(name))
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase5.event_handler_imported",
        filename="/virtual/example/phase5/event_handler_imported.py",
    )

    assert "imported_button" in transformed
    assert "on_press=__pyr_ctx.event_handler(" in transformed

    imported_support.reset_logs()
    namespace = load_transformed_namespace(
        source,
        module_name="example.phase5.event_handler_imported",
        filename="/virtual/example/phase5/event_handler_imported.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(name=True), "Ada")
    (button_node,) = ctx.committed_ui()
    dispatch = button_node.props["on_press"]
    assert button_node.props["label"] == "Save"
    assert callable(dispatch)

    dispatch()
    assert namespace["log"] == ["Ada"]
    assert imported_support.LOG == []

    panel._pyrolyze_meta._func(ctx, dirtyof(name=True), "Bea")
    (updated_button_node,) = ctx.committed_ui()
    updated_dispatch = updated_button_node.props["on_press"]
    assert updated_dispatch is dispatch

    updated_dispatch()
    assert namespace["log"] == ["Ada", "Bea"]
