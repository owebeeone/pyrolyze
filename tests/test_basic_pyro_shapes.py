from __future__ import annotations

from pyrolyze.testing.comprehensive_backend import (
    build_comprehensive_backend,
    write_render_context_graph,
)
from pyrolyze.testing.generic_backend import describe_pyro_node_diff, run_pyro

from tests.basic_pyro_shapes import (
    CallShape,
    ShapeBasic,
    ShapeBranch,
    ShapeRoot,
    ShapeToggleStack,
    load_basic_shapes_namespace,
    notify_shape_value,
    reset_shape_stores,
    scratch_test_output_stem,
    write_snapshot_graph,
)


def _populate_recursive_shape_state(backend, shape_basic, *, nested_label: str = "Nested Child") -> None:
    nested_shape = ShapeBasic(
        top_leaf=CallShape.capture(
            backend.pyro_func("LeafAB00"),
            name="nested_top",
            label="Nested Top",
        ),
        container=CallShape.capture(
            backend.pyro_func("BinAB00"),
            name="nested_container",
        ),
        children=(
            CallShape.capture(
                backend.pyro_func("LeafAB01"),
                name="nested_child_leaf",
                label=nested_label,
            ),
        ),
        bottom_leaf=CallShape.capture(
            backend.pyro_func("LeafAA00"),
            name="nested_bottom",
            label="Nested Bottom",
        ),
    )
    notify_shape_value("B", nested_shape)

    basic_shape = ShapeBasic(
        top_leaf=CallShape.capture(
            backend.pyro_func("LeafAA00"),
            name="top_leaf",
            label="Top",
        ),
        container=CallShape.capture(
            backend.pyro_func("BinAA01"),
            name="container",
        ),
        children=(
            CallShape.capture(
                backend.pyro_func("LeafAA01"),
                name="child_leaf",
                label="Child",
            ),
            CallShape.capture(shape_basic, key="B"),
            CallShape.capture(shape_basic, key="B"),
        ),
        bottom_leaf=CallShape.capture(
            backend.pyro_func("LeafAB00"),
            name="bottom_leaf",
            label="Bottom",
        ),
    )
    notify_shape_value("BASIC", basic_shape)

    root_shape = ShapeRoot(
        container=CallShape.capture(
            backend.pyro_func("BinAA01"),
            name="root_container",
        ),
        child=CallShape.capture(shape_basic, key="BASIC"),
    )
    notify_shape_value("ROOT", root_shape)


def test_basic_shape_module_renders_recursive_shapes_from_external_shape_store() -> None:
    reset_shape_stores()
    backend = build_comprehensive_backend(
        module_name="example.generic_backend.comprehensive_shapes_test"
    )
    namespace = load_basic_shapes_namespace(module_name="example.pyro_shapes.basic_test")
    shape_basic = namespace["shape_basic"]
    shape_root = namespace["shape_root"]
    _populate_recursive_shape_state(backend, shape_basic)

    harness = backend.context(shape_root, "ROOT")
    result = harness.get()
    snapshot = run_pyro(result)
    output_stem = scratch_test_output_stem("test_basic_shape_module_render0")
    dot_path, svg_path = write_snapshot_graph(
        snapshot,
        output_stem,
    )
    context_dot_path, context_svg_path = write_render_context_graph(
        harness,
        output_stem.parent / "basic_shape_context_overlay",
    )

    assert dot_path.exists()
    assert svg_path is not None
    assert svg_path.exists()
    assert context_dot_path.exists()
    assert context_svg_path is not None
    assert context_svg_path.exists()

    assert snapshot.node_type == "BinAA01"

    root_child_names = tuple(
        entry.node.kwargs["name"]
        for entry in snapshot.mounts["MountOrderedAA"][0].entries
    )
    assert root_child_names == (
        "top_leaf",
        "container",
        "bottom_leaf",
    )

    basic_container = snapshot.mounts["MountOrderedAA"][0].entries[1].node
    nested_names = tuple(
        entry.node.kwargs["name"]
        for entry in basic_container.mounts["MountOrderedAA"][0].entries
    )
    assert nested_names == (
        "child_leaf",
        "nested_top",
        "nested_container",
        "nested_bottom",
        "nested_top",
        "nested_container",
        "nested_bottom",
    )


def test_basic_shape_module_rerender_matches_fresh_render_after_store_mutation() -> None:
    reset_shape_stores()
    backend = build_comprehensive_backend(
        module_name="example.generic_backend.comprehensive_shapes_rerender_test"
    )
    namespace = load_basic_shapes_namespace(module_name="example.pyro_shapes.basic_rerender_test")
    shape_basic = namespace["shape_basic"]
    shape_root = namespace["shape_root"]
    _populate_recursive_shape_state(backend, shape_basic, nested_label="Nested Child")

    live_harness = backend.context(shape_root, "ROOT")
    initial_result = live_harness.get()
    initial_graph = run_pyro(initial_result)

    notify_shape_value(
        "B",
        ShapeBasic(
            top_leaf=CallShape.capture(
                backend.pyro_func("LeafAB00"),
                name="nested_top",
                label="Nested Top",
            ),
            container=CallShape.capture(
                backend.pyro_func("BinAB00"),
                name="nested_container",
            ),
            children=(
                CallShape.capture(
                    backend.pyro_func("LeafAB01"),
                    name="nested_child_leaf",
                    label="Nested Child Updated",
                ),
            ),
            bottom_leaf=CallShape.capture(
                backend.pyro_func("LeafAA00"),
                name="nested_bottom",
                label="Nested Bottom",
            ),
        ),
    )
    rerender_result = live_harness.flush_invalidations().get()
    rerender_graph = run_pyro(rerender_result)

    fresh_harness = backend.context(shape_root, "ROOT")
    fresh_result = fresh_harness.get()
    fresh_graph = run_pyro(fresh_result)

    output_dir = scratch_test_output_stem("test_basic_shape_module_rerender_matches_fresh_render0").parent
    write_snapshot_graph(initial_graph, output_dir / "initial_snapshot")
    write_snapshot_graph(rerender_graph, output_dir / "rerender_snapshot")
    write_snapshot_graph(fresh_graph, output_dir / "fresh_snapshot")
    write_render_context_graph(live_harness, output_dir / "rerender_context_overlay")
    write_render_context_graph(fresh_harness, output_dir / "fresh_context_overlay")

    diff = describe_pyro_node_diff(rerender_graph, fresh_graph)
    assert diff is None, diff
    assert rerender_graph != initial_graph


def test_branch_shape_renders_before_children_and_after() -> None:
    reset_shape_stores()
    backend = build_comprehensive_backend(
        module_name="example.generic_backend.comprehensive_shapes_branch_test"
    )
    namespace = load_basic_shapes_namespace(module_name="example.pyro_shapes.branch_test")
    shape_branch = namespace["shape_branch"]

    notify_shape_value(
        "BRANCH_CHILD",
        ShapeBranch(
            node=CallShape.capture(
                backend.pyro_func("BinAB00"),
                name="branch_child_container",
            ),
            is_container=True,
            children=(
                CallShape.capture(
                    backend.pyro_func("LeafAB01"),
                    name="branch_grandchild",
                    label="Grandchild",
                ),
            ),
            before=(
                CallShape.capture(
                    backend.pyro_func("LeafAB00"),
                    name="branch_child_before",
                    label="Child Before",
                ),
            ),
            after=(
                CallShape.capture(
                    backend.pyro_func("LeafAA01"),
                    name="branch_child_after",
                    label="Child After",
                ),
            ),
        ),
    )

    notify_shape_value(
        "BRANCH_ROOT",
        ShapeBranch(
            node=CallShape.capture(
                backend.pyro_func("BinAA01"),
                name="branch_root_container",
            ),
            is_container=True,
            children=(
                CallShape.capture(shape_branch, key="BRANCH_CHILD"),
            ),
            before=(
                CallShape.capture(
                    backend.pyro_func("LeafAA00"),
                    name="branch_before",
                    label="Before",
                ),
            ),
            after=(
                CallShape.capture(
                    backend.pyro_func("LeafAB00"),
                    name="branch_after",
                    label="After",
                ),
            ),
        ),
    )

    harness = backend.context(shape_branch, "BRANCH_ROOT")
    snapshot = run_pyro(harness.get())
    output_stem = scratch_test_output_stem("test_branch_shape_render0")
    dot_path, svg_path = write_snapshot_graph(snapshot, output_stem)
    context_dot_path, context_svg_path = write_render_context_graph(
        harness,
        output_stem.parent / "branch_shape_context_overlay",
    )

    assert dot_path.exists()
    assert svg_path is not None
    assert svg_path.exists()
    assert context_dot_path.exists()
    assert context_svg_path is not None
    assert context_svg_path.exists()

    assert isinstance(snapshot, tuple)
    assert tuple(node.kwargs["name"] for node in snapshot) == (
        "branch_before",
        "branch_root_container",
        "branch_after",
    )

    branch_root = snapshot[1]
    child_entries = branch_root.mounts["MountOrderedAA"][0].entries
    assert tuple(entry.node.kwargs["name"] for entry in child_entries) == (
        "branch_child_before",
        "branch_child_container",
        "branch_child_after",
    )
    grandchild_entries = child_entries[1].node.host_surfaces["MountNestedAB"].entries
    assert tuple(entry.node.kwargs["name"] for entry in grandchild_entries) == (
        "branch_grandchild",
    )


def test_toggle_stack_shape_renders_nested_containers_and_trailing_sibling() -> None:
    reset_shape_stores()
    backend = build_comprehensive_backend(
        module_name="example.generic_backend.comprehensive_shapes_toggle_stack_test"
    )
    namespace = load_basic_shapes_namespace(module_name="example.pyro_shapes.toggle_stack_test")
    shape_toggle_stack = namespace["shape_toggle_stack"]

    notify_shape_value(
        "STACK",
        ShapeToggleStack(
            outer=CallShape.capture(
                backend.pyro_func("BinAA01"),
                name="outer_container",
            ),
            outer_on=True,
            middle=CallShape.capture(
                backend.pyro_func("BinAB00"),
                name="middle_container",
            ),
            middle_on=True,
            inner=CallShape.capture(
                backend.pyro_func("BinAA01"),
                name="inner_container",
            ),
            inner_on=True,
            lead=(
                CallShape.capture(
                    backend.pyro_func("LeafAA00"),
                    name="lead_leaf",
                    label="Lead",
                ),
            ),
            tail=(
                CallShape.capture(
                    backend.pyro_func("LeafAA01"),
                    name="tail_leaf",
                    label="Tail",
                ),
            ),
            inner_children=(
                CallShape.capture(
                    backend.pyro_func("LeafAB00"),
                    name="inner_leaf_a",
                    label="Inner A",
                ),
                CallShape.capture(
                    backend.pyro_func("LeafAB01"),
                    name="inner_leaf_b",
                    label="Inner B",
                ),
            ),
        ),
    )

    harness = backend.context(shape_toggle_stack, "STACK")
    snapshot = run_pyro(harness.get())
    output_stem = scratch_test_output_stem("test_toggle_stack_shape_render0")
    dot_path, svg_path = write_snapshot_graph(snapshot, output_stem)
    context_dot_path, context_svg_path = write_render_context_graph(
        harness,
        output_stem.parent / "toggle_stack_context_overlay",
    )

    assert dot_path.exists()
    assert svg_path is not None
    assert svg_path.exists()
    assert context_dot_path.exists()
    assert context_svg_path is not None
    assert context_svg_path.exists()

    assert isinstance(snapshot, tuple)
    assert tuple(node.kwargs["name"] for node in snapshot) == (
        "lead_leaf",
        "outer_container",
        "tail_leaf",
    )

    outer_surface = snapshot[1].mounts["MountOrderedAA"][0].entries
    assert tuple(entry.node.kwargs["name"] for entry in outer_surface) == ("middle_container",)

    middle_surface = outer_surface[0].node.host_surfaces["MountNestedAB"].entries
    assert tuple(entry.node.kwargs["name"] for entry in middle_surface) == ("inner_container",)

    inner_surface = middle_surface[0].node.mounts["MountOrderedAA"][0].entries
    assert tuple(entry.node.kwargs["name"] for entry in inner_surface) == (
        "inner_leaf_a",
        "inner_leaf_b",
    )
