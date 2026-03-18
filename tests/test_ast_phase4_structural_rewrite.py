from __future__ import annotations

import pytest

from pyrolyze.compiler import emit_transformed_source, load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof


def test_phase4_lowers_container_and_branching_regions() -> None:
    source = """
from contextlib import contextmanager

from pyrolyze.api import pyrolyse

log = []

@contextmanager
def section(title, *, accent):
    log.append(("section.enter", title, accent))
    try:
        yield
    finally:
        log.append(("section.exit", title, accent))

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

    assert "with ctx.container_call(" in transformed
    assert "if show_extra:" in transformed
    assert ".leaf_call(" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase4.stats_panel",
        filename="/virtual/example/phase4/stats_panel.py",
    )
    panel = namespace["stats_panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(show_extra=True, count=True), False, 1)
    assert namespace["log"] == [
        ("section.enter", "Stats", "green"),
        ("badge", "Count: 1", "info"),
        ("badge", "Hidden", "muted"),
        ("section.exit", "Stats", "green"),
    ]

    panel._pyrolyze_meta._func(ctx, dirtyof(show_extra=False, count=False), False, 1)
    assert namespace["log"] == [
        ("section.enter", "Stats", "green"),
        ("badge", "Count: 1", "info"),
        ("badge", "Hidden", "muted"),
        ("section.exit", "Stats", "green"),
    ]

    panel._pyrolyze_meta._func(ctx, dirtyof(show_extra=True, count=False), True, 1)
    assert namespace["log"] == [
        ("section.enter", "Stats", "green"),
        ("badge", "Count: 1", "info"),
        ("badge", "Hidden", "muted"),
        ("section.exit", "Stats", "green"),
        ("section.enter", "Stats", "green"),
        ("badge", "Visible", "success"),
        ("section.exit", "Stats", "green"),
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
    assert "current_value()" in transformed
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
    assert namespace["log"] == []


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

    with pytest.raises(Exception):
        emit_transformed_source(
            source,
            module_name="example.phase4.bad_panel",
            filename="/virtual/example/phase4/bad_panel.py",
        )
