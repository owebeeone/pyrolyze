from __future__ import annotations

import pytest

from pyrolyze.compiler import (
    PyRolyzeCompileError,
    emit_transformed_source,
    load_transformed_namespace,
)
from pyrolyze.runtime import RenderContext, dirtyof


def test_phase4_lowers_container_and_branching_regions() -> None:
    source = """
from pyrolyze.api import UIElement, call_native, pyrolyse

log = []

@pyrolyse
def section(title, *, accent):
    log.append(("section", title, accent))
    call_native(UIElement)(kind="section", props={"title": title, "accent": accent})

def badge(text, *, tone):
    log.append(("badge", text, tone))

@pyrolyse
def stats_panel(show_extra, count):
    with section("Stats", accent="green"):
        badge(f"Count: {count}", tone="info")
        if show_extra:
            badge("Visible", tone="success")
        else:
            badge("Hidden", tone="muted")
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase4.stats_panel",
        filename="/virtual/example/phase4/stats_panel.py",
    )

    assert "__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=16)" in transformed
    assert "with __pyr_ctx.container_call(" in transformed
    assert "dirty_state=__pyr_dirtyof(title=False, accent=False)" in transformed
    assert "if show_extra:" in transformed
    assert "badge(f'Count: {count}', tone='info')" in transformed
    assert ".leaf_call(" not in transformed
    assert "__pyr_slot_2 =" not in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase4.stats_panel",
        filename="/virtual/example/phase4/stats_panel.py",
    )
    panel = namespace["stats_panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(show_extra=True, count=True), False, 1)
    assert namespace["log"] == [
        ("section", "Stats", "green"),
        ("badge", "Count: 1", "info"),
        ("badge", "Hidden", "muted"),
    ]

    panel._pyrolyze_meta._func(ctx, dirtyof(show_extra=False, count=False), False, 1)
    assert namespace["log"] == [
        ("section", "Stats", "green"),
        ("badge", "Count: 1", "info"),
        ("badge", "Hidden", "muted"),
    ]

    panel._pyrolyze_meta._func(ctx, dirtyof(show_extra=True, count=False), True, 1)
    assert namespace["log"] == [
        ("section", "Stats", "green"),
        ("badge", "Count: 1", "info"),
        ("badge", "Hidden", "muted"),
        ("section", "Stats", "green"),
        ("badge", "Count: 1", "info"),
        ("badge", "Visible", "success"),
    ]


def test_phase4_lowers_keyed_loops_and_reuses_item_contexts_on_reorder() -> None:
    source = """
from pyrolyze.api import keyed, pyrolyse, pyrolyze_slotted

log = []

def identity_key(value):
    return value

@pyrolyze_slotted
def use_value(item):
    log.append(("use_value", item))
    return item.upper()

def badge(text, *, tone):
    log.append(("badge", text, tone))

@pyrolyse
def values_panel(items):
    for item in keyed(items, key=identity_key):
        value = use_value(item)
        badge(value, tone="neutral")
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase4.values_panel",
        filename="/virtual/example/phase4/values_panel.py",
    )

    assert "keyed_loop(" in transformed
    assert "with __pyr_ctx_slot_1_k.pass_scope():" in transformed
    assert "current_value()" in transformed
    assert "visit_self_and_dirty()" in transformed
    assert ".call_plain(" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase4.values_panel",
        filename="/virtual/example/phase4/values_panel.py",
    )
    panel = namespace["values_panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(items=True), ["a", "b"])
    assert namespace["log"] == [
        ("use_value", "a"),
        ("badge", "A", "neutral"),
        ("use_value", "b"),
        ("badge", "B", "neutral"),
    ]

    namespace["log"].clear()
    panel._pyrolyze_meta._func(ctx, dirtyof(items=True), ["b", "a"])
    assert namespace["log"] == [
        ("badge", "B", "neutral"),
        ("badge", "A", "neutral"),
    ]


def test_phase4_lowers_nested_keyed_loops_and_nested_containers() -> None:
    source = """
from pyrolyze.api import UIElement, call_native, keyed, pyrolyse

log = []

@pyrolyse
def row(title):
    log.append(("row", title))
    call_native(UIElement)(kind="row", props={"title": title})

def button(label, *, value):
    log.append(("button", label, value))

@pyrolyse
def grid_panel(labels, values):
    for label in keyed(labels, key=lambda x: x):
        with row(label):
            for value in keyed(values, key=lambda x: x):
                with row(f"{label}:{value}"):
                    button(f"{label}:{value}", value=value)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase4.grid_panel",
        filename="/virtual/example/phase4/grid_panel.py",
    )

    assert transformed.count("keyed_loop(") == 2
    assert transformed.count("container_call(") == 2
    assert "for __pyr_ctx_slot_1_k in __pyr_ctx.keyed_loop(__pyr_slot_1, labels, key_fn=lambda x: x):" in transformed
    assert "with __pyr_ctx_slot_1_k.pass_scope():" in transformed
    assert "__pyr_label_dirty, label = __pyr_ctx_slot_1_k.current_value()" in transformed
    assert "with __pyr_ctx_slot_1_k.container_call(__pyr_slot_2, row, label, dirty_state=__pyr_dirtyof(title=__pyr_label_dirty)) as __pyr_ctx_slot_2:" in transformed
    assert "for __pyr_ctx_slot_3_k in __pyr_ctx_slot_2.keyed_loop(__pyr_slot_3, values, key_fn=lambda x: x):" in transformed
    assert "with __pyr_ctx_slot_3_k.pass_scope():" in transformed
    assert "__pyr_value_dirty, value = __pyr_ctx_slot_3_k.current_value()" in transformed
    assert "with __pyr_ctx_slot_3_k.container_call(__pyr_slot_4, row, f'{label}:{value}', dirty_state=__pyr_dirtyof(title=__pyr_label_dirty or __pyr_value_dirty)) as __pyr_ctx_slot_4:" in transformed
    assert "_item" not in transformed
    assert "button(f'{label}:{value}', value=value)" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase4.grid_panel",
        filename="/virtual/example/phase4/grid_panel.py",
    )
    panel = namespace["grid_panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(labels=True, values=True), ["a", "b"], [1, 2])
    assert namespace["log"] == [
        ("row", "a"),
        ("row", "a:1"),
        ("button", "a:1", 1),
        ("row", "a:2"),
        ("button", "a:2", 2),
        ("row", "b"),
        ("row", "b:1"),
        ("button", "b:1", 1),
        ("row", "b:2"),
        ("button", "b:2", 2),
    ]


def test_phase4_lowers_destructured_keyed_targets_with_structured_dirty_projection() -> None:
    source = """
from pyrolyze.api import keyed, pyrolyse

log = []

def button(label, *, value):
    log.append((label, value))

@pyrolyse
def list_render(items):
    for (index, (x, y)) in keyed(enumerate(items), key=lambda element: element[0]):
        button(f"{index}:{x}", value=y)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase4.list_render",
        filename="/virtual/example/phase4/list_render.py",
    )

    assert "for __pyr_ctx_slot_1_k in __pyr_ctx.keyed_loop(__pyr_slot_1, enumerate(items), key_fn=lambda element: element[0]):" in transformed
    assert "with __pyr_ctx_slot_1_k.pass_scope():" in transformed
    assert "__pyr_item_dirty, __pyr_item_value = __pyr_ctx_slot_1_k.current_value()" in transformed
    assert "__pyr_index_dirty, (__pyr_x_dirty, __pyr_y_dirty) = __pyr_item_dirty" in transformed
    assert "index, (x, y) = __pyr_item_value" in transformed
    assert "visit_self_and_dirty()" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase4.list_render",
        filename="/virtual/example/phase4/list_render.py",
    )
    panel = namespace["list_render"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(items=True), [("a", "A"), ("b", "B")])
    assert namespace["log"] == [("0:a", "A"), ("1:b", "B")]


def test_phase4_preserves_plain_python_with_as_context_managers() -> None:
    source = """
from contextlib import contextmanager

from pyrolyze.api import pyrolyse

log = []

@contextmanager
def openfoo(name):
    log.append(("enter", name))
    try:
        yield name.upper()
    finally:
        log.append(("exit", name))

def record(value):
    log.append(("record", value))

@pyrolyse
def panel(name):
    with openfoo(name) as current:
        record(current)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase4.with_as_plain",
        filename="/virtual/example/phase4/with_as_plain.py",
    )

    assert "with openfoo(name) as current:" in transformed
    assert ".container_call(" not in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase4.with_as_plain",
        filename="/virtual/example/phase4/with_as_plain.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()
    panel._pyrolyze_meta._func(ctx, dirtyof(name=True), "hello")

    assert namespace["log"] == [
        ("enter", "hello"),
        ("record", "HELLO"),
        ("exit", "hello"),
    ]


def test_phase4_still_rejects_non_keyed_render_loops() -> None:
    source = """
from pyrolyze.api import pyrolyse

def badge(text):
    return text

@pyrolyse
def bad_panel(items):
    for item in items:
        badge(item)
"""

    with pytest.raises(
        PyRolyzeCompileError,
        match="Mutable loop must use keyed\\(items, key=\\.\\.\\.\\)",
    ):
        emit_transformed_source(
            source,
            module_name="example.phase4.bad_panel",
            filename="/virtual/example/phase4/bad_panel.py",
        )


def test_phase4_rejects_with_as_in_render_scope() -> None:
    source = """
from pyrolyze.api import pyrolyse
from pyrolyze.api import call_native, UIElement

@pyrolyse
def row(name):
    call_native(UIElement)(kind="row", props={"name": name})

@pyrolyse
def bad_panel():
    with row("outer") as current:
        print(current)
"""

    with pytest.raises(PyRolyzeCompileError, match="ordinary Python"):
        emit_transformed_source(
            source,
            module_name="example.phase4.bad_with_as",
            filename="/virtual/example/phase4/bad_with_as.py",
        )


def test_phase4_rejects_plain_python_with_without_as_in_render_scope() -> None:
    source = """
from pyrolyze.api import pyrolyse

def openfoo(name):
    return name

@pyrolyse
def bad_panel(name):
    with openfoo(name):
        print(name)
"""

    with pytest.raises(PyRolyzeCompileError, match="reserved for PyRolyze container syntax"):
        emit_transformed_source(
            source,
            module_name="example.phase4.bad_plain_with",
            filename="/virtual/example/phase4/bad_plain_with.py",
        )


def test_phase4_rejects_legacy_contextmanager_container_syntax() -> None:
    source = """
from contextlib import contextmanager

from pyrolyze.api import pyrolyse

@contextmanager
def row(name):
    yield

@pyrolyse
def bad_panel(name):
    with row(name):
        print(name)
"""

    with pytest.raises(PyRolyzeCompileError, match="reserved for PyRolyze container syntax"):
        emit_transformed_source(
            source,
            module_name="example.phase4.legacy_contextmanager",
            filename="/virtual/example/phase4/legacy_contextmanager.py",
        )


def test_phase4_rejects_hook_inside_keyed_loop() -> None:
    source = """
from pyrolyze.api import keyed, pyrolyse, use_state

def button(label, *, on):
    return (label, on)

@pyrolyse
def bad_panel(items):
    for item in keyed(items, key=lambda x: x):
        on, set_on = use_state(False)
        button(item, on=on)
"""

    with pytest.raises(
        PyRolyzeCompileError,
        match="Hook 'use_state' must be top-level in component scope",
    ):
        emit_transformed_source(
            source,
            module_name="example.phase4.bad_hook_loop",
            filename="/virtual/example/phase4/bad_hook_loop.py",
        )
