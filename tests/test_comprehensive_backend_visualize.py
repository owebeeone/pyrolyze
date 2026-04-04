from __future__ import annotations

from pyrolyze.testing.comprehensive_backend import (
    build_comprehensive_backend,
    render_context_to_dot,
    write_render_context_graph,
)

from tests.basic_pyro_shapes import (
    CallShape,
    ShapeBasic,
    ShapeRoot,
    load_basic_shapes_namespace,
    notify_shape_value,
    reset_shape_stores,
)


def test_render_context_visualizer_writes_slot_and_render_overlay(tmp_path) -> None:
    reset_shape_stores()
    backend = build_comprehensive_backend(
        module_name="example.generic_backend.comprehensive_visualize_test"
    )
    namespace = load_basic_shapes_namespace(module_name="example.pyro_shapes.visualize_test")
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
    harness.get()

    dot = render_context_to_dot(harness)
    dot_path, svg_path = write_render_context_graph(harness, tmp_path / "context_overlay")

    assert 'color="black"' in dot
    assert 'color="#1d4ed8"' in dot
    assert "#d9f7be" in dot
    assert "root_container" in dot
    assert "nested_container" in dot
    assert dot_path.exists()
    assert svg_path is None or svg_path.exists()

