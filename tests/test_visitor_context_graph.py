from __future__ import annotations

from pathlib import Path

from pyrolyze.api import UIElement
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import ContextBase, ModuleRegistry, RenderContext, SlotId, dirtyof
from pyrolyze.visitor import capture_context_graph, compare_context_graphs


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.visitor_context_graph")

_SECTION_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_ITEM_LOOP_SLOT = SlotId(_MODULE_ID, 2, line_no=11)
_BADGE_SLOT = SlotId(_MODULE_ID, 3, line_no=12)


def section(ctx: ContextBase, title: str) -> None:
    ctx.call_native(UIElement, kind="section", props={"title": title})


def badge(ctx: ContextBase, text: str) -> None:
    ctx.call_native(UIElement, kind="badge", props={"text": text})


def _read_test_source(test_name: str) -> tuple[Path, str]:
    source_path = Path(__file__).resolve().parent / "data" / test_name / "source.py"
    return source_path, source_path.read_text(encoding="utf-8")


def test_capture_context_graph_records_context_kinds_and_render_owners() -> None:
    ctx = RenderContext()

    def render() -> None:
        with ctx.pass_scope():
            if ctx.visit_slot_and_dirty(_SECTION_SLOT):
                with ctx.container_call(_SECTION_SLOT, section, "Stats") as section_ctx:
                    if section_ctx.visit_slot_and_dirty(_ITEM_LOOP_SLOT):
                        for item_ctx in section_ctx.keyed_loop(_ITEM_LOOP_SLOT, ["a", "b"], key_fn=lambda value: value):
                            with item_ctx.pass_scope():
                                item_dirty, value = item_ctx.current_value()
                                if not (item_dirty or item_ctx.visit_self_and_dirty()):
                                    continue
                                if item_ctx.visit_slot_and_dirty(_BADGE_SLOT):
                                    item_ctx.leaf_call(_BADGE_SLOT, badge, value.upper())

    ctx.mount(render)
    graph = capture_context_graph(ctx)

    assert graph.generation_id == 1
    assert graph.root.kind == "render_root"
    assert graph.root.slot_id is None
    assert [child.kind for child in graph.root.children] == ["container"]
    container = graph.root.children[0]
    assert container.slot_id == _SECTION_SLOT
    assert container.ui == (
        graph.root.children[0].ui[0],
    )
    assert container.ui[0].slot_id == _SECTION_SLOT
    assert container.ui[0].render_owner_slot_id is None
    assert container.ui[0].element == UIElement(kind="section", props={"title": "Stats"})

    loop = container.children[0]
    assert loop.kind == "keyed_loop"
    first_item, second_item = loop.children
    assert first_item.kind == "loop_item"
    assert second_item.kind == "loop_item"
    assert first_item.slot_id == SlotId(_MODULE_ID, 2, key_path=("a",), line_no=11)
    assert second_item.slot_id == SlotId(_MODULE_ID, 2, key_path=("b",), line_no=11)

    first_leaf = first_item.children[0]
    second_leaf = second_item.children[0]
    assert first_leaf.kind == "leaf"
    assert second_leaf.kind == "leaf"
    assert first_leaf.ui[0].slot_id == SlotId(_MODULE_ID, 3, key_path=("a",), line_no=12)
    assert second_leaf.ui[0].slot_id == SlotId(_MODULE_ID, 3, key_path=("b",), line_no=12)
    assert first_leaf.ui[0].render_owner_slot_id == _SECTION_SLOT
    assert second_leaf.ui[0].render_owner_slot_id == _SECTION_SLOT
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
