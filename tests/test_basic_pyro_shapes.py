from __future__ import annotations

from pyrolyze.testing.comprehensive_backend import (
    build_comprehensive_backend,
    write_render_context_graph,
)
from pyrolyze.testing.generic_backend import run_pyro

from tests.basic_pyro_shapes import (
    CallShape,
    ShapeBasic,
    ShapeRoot,
    load_basic_shapes_namespace,
    notify_shape_value,
    reset_shape_stores,
    scratch_test_output_stem,
    write_snapshot_graph,
)


def test_basic_shape_module_renders_recursive_shapes_from_external_shape_store() -> None:
    reset_shape_stores()
    backend = build_comprehensive_backend(
        module_name="example.generic_backend.comprehensive_shapes_test"
    )
    namespace = load_basic_shapes_namespace(module_name="example.pyro_shapes.basic_test")
    shape_basic = namespace["shape_basic"]
    shape_root = namespace["shape_root"]

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
                label="Nested Child",
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
