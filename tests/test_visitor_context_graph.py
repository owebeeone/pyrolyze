from __future__ import annotations

from pathlib import Path

from pyrolyze.api import UIElement
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import ContextBase, RenderContext, dirtyof
from pyrolyze_testsupport import pyrolize_test_native
from pyrolyze.visitor import capture_context_graph, compare_context_graphs




@pyrolize_test_native
def section(ctx: ContextBase, title: str) -> None:
    ctx.call_native(UIElement, kind="section", props={"title": title})


@pyrolize_test_native
def badge(ctx: ContextBase, text: str) -> None:
    ctx.call_native(UIElement, kind="badge", props={"text": text})


def _read_test_source(test_name: str) -> tuple[Path, str]:
    source_path = Path(__file__).resolve().parent / "data" / test_name / "source.py"
    return source_path, source_path.read_text(encoding="utf-8")


def test_capture_context_graph_records_context_kinds_and_render_owners() -> None:
    ctx = RenderContext()

    namespace = load_transformed_namespace(
        '''
from pyrolyze.api import component, keyed, pyrolyze

@pyrolyze
def panel():
    with component(section, "Stats"):
        for value in keyed(["a", "b"], key=lambda item: item):
            component(badge, value.upper())
''',
        module_name="tests.visitor_context_graph.compiled",
        globals_dict={"section": section, "badge": badge},
    )
    render = namespace["panel"]._pyrolyze_meta._func
    ctx.mount(lambda: render(ctx, dirtyof()))
    graph = capture_context_graph(ctx)

    assert graph.generation_id == 1
    assert graph.root.kind == "render_root"
    assert graph.root.slot_id is None
    assert [child.kind for child in graph.root.children] == ["container"]
    container = graph.root.children[0]
    section_slot = ctx.debug_children_of()[0]
    assert container.slot_id == section_slot
    assert container.ui == (
        graph.root.children[0].ui[0],
    )
    assert container.ui[0].slot_id == section_slot
    assert container.ui[0].render_owner_slot_id is None
    assert container.ui[0].element == UIElement(kind="section", props={"title": "Stats"})

    loop = container.children[0]
    assert loop.kind == "keyed_loop"
    first_item, second_item = loop.children
    assert first_item.kind == "loop_item"
    assert second_item.kind == "loop_item"
    assert first_item.slot_id.key_path == ("a",)
    assert second_item.slot_id.key_path == ("b",)

    first_leaf = first_item.children[0]
    second_leaf = second_item.children[0]
    assert first_leaf.kind == "component_call"
    assert second_leaf.kind == "component_call"
    assert first_leaf.ui[0].slot_id == first_leaf.slot_id
    assert second_leaf.ui[0].slot_id == second_leaf.slot_id
    assert first_leaf.ui[0].render_owner_slot_id == section_slot
    assert second_leaf.ui[0].render_owner_slot_id == section_slot
    assert first_leaf.ui[0].element == UIElement(kind="badge", props={"text": "A"})
    assert second_leaf.ui[0].element == UIElement(kind="badge", props={"text": "B"})


def test_compare_context_graphs_isolates_use_state_rerender_changes_from_file_backed_source() -> None:
    source_path, source = _read_test_source("integrated_use_state_graph")
    namespace = load_transformed_namespace(
        source,
        module_name="tests.data.integrated_use_state_graph.source",
        filename=str(source_path),
    )
    panel = namespace["counter_panel"]
    ctx = RenderContext()

    ctx.mount(lambda: panel._pyrolyze_meta._func(ctx, dirtyof()))
    before = capture_context_graph(ctx)
    assert before.generation_id == 1

    setter = namespace["captured_setter"]
    assert callable(setter)
    setter(lambda current: current + 1)
    ctx.run_pending_invalidations()

    after = capture_context_graph(ctx)
    diff = compare_context_graphs(before, after)

    assert after.generation_id == 2
    assert ctx.current_generation_id() == 2
    assert ctx.committed_ui() == (
        UIElement(kind="Label", props={"text": "Count: 1"}),
    )
    assert diff.generation_before == 1
    assert diff.generation_after == 2
    assert diff.added_contexts == ()
    assert diff.removed_contexts == ()
    assert diff.changed_contexts
    assert diff.added_ui
    assert diff.removed_ui
    assert diff.removed_ui[0].ui.element == UIElement(kind="Label", props={"text": "Count: 0"})
    assert diff.removed_ui[0].ui.generation_id == 1
    assert diff.added_ui[0].ui.element == UIElement(kind="Label", props={"text": "Count: 1"})
    assert diff.added_ui[0].ui.generation_id == 2
