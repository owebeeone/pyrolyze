from __future__ import annotations

from pyrolyze.api import pyrolyze
from pyrolyze.backends.model import TypeRef
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.testing.generic_backend import (
    BuildPyroNodeBackend,
    MountInterfaceKind,
    MountParam,
    MountSpec,
    NodeGenSpec,
    ParamSpec,
    run_pyro,
)


def _rotation_specs() -> tuple[NodeGenSpec, ...]:
    return (
        NodeGenSpec(
            name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
        ),
        NodeGenSpec(
            name="text",
            base_name="node",
            constructor=(
                ParamSpec(name="name", annotation=TypeRef("str")),
                ParamSpec(name="text", annotation=TypeRef("str")),
            ),
        ),
        NodeGenSpec(
            name="grid",
            base_name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            mounts=(
                MountSpec(
                    name="cell",
                    accepted_base="node",
                    interface=MountInterfaceKind.KEYED,
                    params=(
                        MountParam(name="row", annotation=TypeRef("int"), keyed=True),
                        MountParam(name="column", annotation=TypeRef("int"), keyed=True),
                    ),
                ),
            ),
        ),
    )


def _load_program(
    backend: BuildPyroNodeBackend,
    module_suffix: str,
    source: str,
    **globals_dict: object,
) -> dict[str, object]:
    backend.source_namespace()
    return load_transformed_namespace(
        source,
        module_name=f"{backend.module_name}.{module_suffix}",
        filename=f"/virtual/{backend.module_name.replace('.', '/')}/{module_suffix}.py",
        globals_dict={
            "pyrolyze": pyrolyze,
            **globals_dict,
        },
    )


def _grid_cells(snapshot: object) -> dict[tuple[object, ...], str]:
    node = run_pyro(snapshot)
    return {
        bucket.key.args: bucket.entries[0].node.kwargs["text"]
        for bucket in node.mounts["cell"]
    }


def _build_rotation_program(backend: BuildPyroNodeBackend) -> dict[str, object]:
    cell_selector = backend.selector_family("cell")
    return _load_program(
        backend,
        "rotation_panel",
        f"""
from pyrolyze.api import advertise_mount, keyed, mount, mount_key
from {backend.module_name} import grid, text

def public_cell(index):
    return mount_key(("cell", index))

@pyrolyze
def panel(positions, active_indices):
    with grid("board"):
        for item in keyed(tuple(enumerate(positions)), key=lambda pair: pair[1]):
            index, position = item
            if index in active_indices:
                advertise_mount(
                    public_cell(index),
                    target=CELL(row=position[0], column=position[1]),
                )
        for index in keyed(tuple(active_indices), key=lambda value: value):
            with mount(public_cell(index)):
                text(f"cell-{{index}}", f"Cell {{index}}")
""",
        CELL=cell_selector,
    )


def test_rotation_one_step_relocates_cell_buckets() -> None:
    backend = BuildPyroNodeBackend(_rotation_specs(), module_name="example.generic_backend.rotation.one")
    namespace = _build_rotation_program(backend)
    positions = ((0, 0), (0, 1), (1, 0), (1, 1))
    rotated = ((0, 1), (1, 0), (1, 1), (0, 0))

    ctx = backend.context(namespace["panel"], positions, (0, 1, 2, 3), initial_generation=0)
    first = run_pyro(ctx.get())
    second = run_pyro(ctx.run(rotated, (0, 1, 2, 3)).get())

    assert _grid_cells(first) == {
        (0, 0): "Cell 0",
        (0, 1): "Cell 1",
        (1, 0): "Cell 2",
        (1, 1): "Cell 3",
    }
    assert _grid_cells(second) == {
        (0, 0): "Cell 3",
        (0, 1): "Cell 0",
        (1, 0): "Cell 1",
        (1, 1): "Cell 2",
    }


def test_rotation_reverse_order_relocates_cells_cleanly() -> None:
    backend = BuildPyroNodeBackend(_rotation_specs(), module_name="example.generic_backend.rotation.reverse")
    namespace = _build_rotation_program(backend)
    positions = ((0, 0), (0, 1), (1, 0), (1, 1))
    reversed_positions = tuple(reversed(positions))

    ctx = backend.context(namespace["panel"], positions, (0, 1, 2, 3), initial_generation=0)
    second = run_pyro(ctx.run(reversed_positions, (0, 1, 2, 3)).get())

    assert _grid_cells(second) == {
        (0, 0): "Cell 3",
        (0, 1): "Cell 2",
        (1, 0): "Cell 1",
        (1, 1): "Cell 0",
    }


def test_rotation_equivalent_rerender_keeps_exact_graph() -> None:
    backend = BuildPyroNodeBackend(_rotation_specs(), module_name="example.generic_backend.rotation.same")
    namespace = _build_rotation_program(backend)
    positions = ((0, 0), (0, 1), (1, 0), (1, 1))

    ctx = backend.context(namespace["panel"], positions, (0, 1, 2, 3), initial_generation=10)
    first = run_pyro(ctx.get())
    second = run_pyro(ctx.run(positions, (0, 1, 2, 3)).get())

    assert first == second


def test_rotation_sparse_active_set_matches_fresh_render_of_final_shape() -> None:
    backend = BuildPyroNodeBackend(_rotation_specs(), module_name="example.generic_backend.rotation.sparse")
    namespace = _build_rotation_program(backend)
    positions = ((0, 0), (0, 1), (1, 0), (1, 1))
    sparse_active = (0, 2)

    rerender_ctx = backend.context(namespace["panel"], positions, (0, 1, 2, 3), initial_generation=0)
    _ = rerender_ctx.get()
    rerendered = run_pyro(rerender_ctx.run(positions, sparse_active).get())

    fresh_ctx = backend.context(namespace["panel"], positions, sparse_active, initial_generation=1)
    fresh = run_pyro(fresh_ctx.get())

    assert _grid_cells(rerendered) == _grid_cells(fresh)
    assert _grid_cells(rerendered) == {
        (0, 0): "Cell 0",
        (1, 0): "Cell 2",
    }
