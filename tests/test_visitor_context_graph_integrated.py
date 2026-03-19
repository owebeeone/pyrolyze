from __future__ import annotations

from pathlib import Path

from pyrolyze.api import UIElement
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof
from pyrolyze.visitor import CapturedContext, CapturedUiElement, capture_context_graph, compare_context_graphs


def _read_test_source(test_name: str) -> tuple[Path, str]:
    source_path = Path(__file__).resolve().parent / "data" / test_name / "source.py"
    return source_path, source_path.read_text(encoding="utf-8")


def _iter_ui(context: CapturedContext) -> list[CapturedUiElement]:
    ui = list(context.ui)
    for child in context.children:
        ui.extend(_iter_ui(child))
    return ui


def test_integrated_nested_grid_toggle_isolates_one_cell_ui_change() -> None:
    source_path, source = _read_test_source("integrated_nested_grid_toggle")
    namespace = load_transformed_namespace(
        source,
        module_name="tests.data.integrated_nested_grid_toggle.source",
        filename=str(source_path),
    )
    panel = namespace["grid_panel"]
    ctx = RenderContext()
    labels = ["a", "b"]
    values = [1, 2]

    ctx.mount(lambda: panel._pyrolyze_meta._func(ctx, dirtyof(labels=True, values=True), labels, values))
    before = capture_context_graph(ctx)

    setters = namespace["toggle_setters"]
    setters[("a", 2)](True)
    ctx.run_pending_invalidations()

    after = capture_context_graph(ctx)
    diff = compare_context_graphs(before, after)

    assert after.generation_id == before.generation_id + 1
    assert diff.added_contexts == ()
    assert diff.removed_contexts == ()
    assert len(diff.added_ui) == 1
    assert len(diff.removed_ui) == 1
    assert diff.removed_ui[0].ui.element == UIElement(
        kind="button",
        props={"label": "a:2:off", "active": False},
    )
    assert diff.added_ui[0].ui.element == UIElement(
        kind="button",
        props={"label": "a:2:on", "active": True},
    )


def test_integrated_container_loop_container_preserves_render_owner_boundaries() -> None:
    source_path, source = _read_test_source("integrated_container_loop_container")
    namespace = load_transformed_namespace(
        source,
        module_name="tests.data.integrated_container_loop_container.source",
        filename=str(source_path),
    )
    board = namespace["board"]
    ctx = RenderContext()

    ctx.mount(lambda: board._pyrolyze_meta._func(ctx, dirtyof(labels=True), ["a", "b"]))
    graph = capture_context_graph(ctx)

    outer_container = graph.root.children[0]
    loop = outer_container.children[0]
    first_item = loop.children[0]
    inner_container = first_item.children[0]
    badge_component = inner_container.children[0]

    assert outer_container.kind == "container"
    assert outer_container.ui[0].element == UIElement(kind="panel", props={"title": "Board"})
    assert outer_container.ui[0].render_owner_slot_id is None

    assert loop.kind == "keyed_loop"
    assert first_item.kind == "loop_item"

    assert inner_container.kind == "container"
    assert inner_container.ui[0].element == UIElement(kind="panel", props={"title": "Cell:a"})
    assert inner_container.ui[0].render_owner_slot_id == outer_container.slot_id

    assert badge_component.kind == "component_call"
    assert badge_component.ui[0].element == UIElement(kind="badge", props={"text": "A"})
    assert badge_component.ui[0].render_owner_slot_id == inner_container.slot_id


def test_integrated_loop_component_call_isolates_child_component_rerender() -> None:
    source_path, source = _read_test_source("integrated_loop_component_call")
    namespace = load_transformed_namespace(
        source,
        module_name="tests.data.integrated_loop_component_call.source",
        filename=str(source_path),
    )
    board = namespace["board"]
    ctx = RenderContext()
    items = ["alpha", "beta", "gamma"]

    ctx.mount(lambda: board._pyrolyze_meta._func(ctx, dirtyof(items=True), items))
    before = capture_context_graph(ctx)

    setters = namespace["toggle_setters"]
    setters["beta"](True)
    ctx.run_pending_invalidations()

    after = capture_context_graph(ctx)
    diff = compare_context_graphs(before, after)
    ui_after = _iter_ui(after.root)

    assert after.generation_id == before.generation_id + 1
    assert diff.added_contexts == ()
    assert diff.removed_contexts == ()
    assert len(diff.added_ui) == 1
    assert len(diff.removed_ui) == 1
    assert diff.removed_ui[0].ui.element == UIElement(
        kind="badge",
        props={"text": "beta", "active": False},
    )
    assert diff.added_ui[0].ui.element == UIElement(
        kind="badge",
        props={"text": "beta", "active": True},
    )
    assert any(ui.element == UIElement(kind="badge", props={"text": "alpha", "active": False}) for ui in ui_after)
    assert any(ui.element == UIElement(kind="badge", props={"text": "gamma", "active": False}) for ui in ui_after)
