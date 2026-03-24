from __future__ import annotations

import pytest

from pyrolyze.api import mount_key, pyrolyze
from pyrolyze.backends.model import TypeRef
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.testing.generic_backend import (
    BuildPyroNodeBackend,
    MountInterfaceKind,
    MountParam,
    MountSpec,
    NodeGenSpec,
    ParamSpec,
    PyrolyzeMountCompatibilityError,
    run_pyro,
)


def _advert_specs() -> tuple[NodeGenSpec, ...]:
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
            name="menu",
            base_name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
        ),
        NodeGenSpec(
            name="row",
            base_name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            mounts=(
                MountSpec(
                    name="child",
                    accepted_base="node",
                    interface=MountInterfaceKind.ORDERED,
                    default=True,
                ),
            ),
        ),
        NodeGenSpec(
            name="text_row",
            base_name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            mounts=(
                MountSpec(
                    name="child",
                    accepted_kind="text",
                    interface=MountInterfaceKind.ORDERED,
                    default=True,
                ),
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


def _load_program(backend: BuildPyroNodeBackend, module_suffix: str, source: str, **globals_dict: object) -> dict[str, object]:
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


def _child_texts(snapshot) -> tuple[str, ...]:
    return tuple(
        entry.node.kwargs.get("text", entry.node.kwargs.get("name"))
        for entry in snapshot.mounts["child"][0].entries
    )


def _grid_cells(snapshot) -> dict[tuple[object, ...], tuple[str, int]]:
    return {
        bucket.key.args: (
            bucket.entries[0].node.kwargs["text"],
            bucket.entries[0].node.generation,
        )
        for bucket in snapshot.mounts["cell"]
    }


def test_generic_backend_readable_advert_routing_inserts_consumer_children_at_anchor() -> None:
    backend = BuildPyroNodeBackend(_advert_specs(), module_name="example.generic_backend.advert_readable")
    child_selector = backend.selector_family("child")

    namespace = _load_program(
        backend,
        "readable_panel",
        f"""
from pyrolyze.api import advertise_mount, mount, mount_key
from {backend.module_name} import row, text

PUBLIC = mount_key("body")

@pyrolyze
def panel():
    with row("root"):
        text("hello", "hello")
        advertise_mount(PUBLIC, target=CHILD, default=True)
        with mount(PUBLIC):
            text("inserted", "inserted")
        text("world", "world")
""",
        CHILD=child_selector,
    )

    snapshot = run_pyro(backend.context(namespace["panel"]).get())

    assert _child_texts(snapshot) == ("hello", "inserted", "world")


def test_generic_backend_public_key_rename_keeps_translated_graph_identical() -> None:
    backend = BuildPyroNodeBackend(_advert_specs(), module_name="example.generic_backend.advert_rename")
    child_selector = backend.selector_family("child")
    key_a = mount_key("slot_a")
    key_b = mount_key("slot_b")

    namespace = _load_program(
        backend,
        "rename_panel",
        f"""
from pyrolyze.api import advertise_mount, mount
from {backend.module_name} import row, text

@pyrolyze
def panel(public_key):
    with row("root"):
        text("hello", "hello")
        advertise_mount(public_key, target=CHILD, default=True)
        with mount(public_key):
            text("inserted", "inserted")
        text("world", "world")
""",
        CHILD=child_selector,
    )

    ctx = backend.context(namespace["panel"], key_a, initial_generation=10)
    first = run_pyro(ctx.get())
    second = run_pyro(ctx.run(key_b).get())

    assert first == second
    assert _child_texts(second) == ("hello", "inserted", "world")


def test_generic_backend_keyed_grid_rotation_moves_buckets_without_remounting_children() -> None:
    backend = BuildPyroNodeBackend(_advert_specs(), module_name="example.generic_backend.advert_grid")
    cell_selector = backend.selector_family("cell")
    positions_1 = ((0, 0), (0, 1), (1, 0), (1, 1))
    positions_2 = ((0, 1), (1, 0), (1, 1), (0, 0))

    namespace = _load_program(
        backend,
        "grid_panel",
        f"""
from pyrolyze.api import advertise_mount, keyed, mount, mount_key
from {backend.module_name} import grid, text

def public_cell(index):
    return mount_key(("cell", index))

@pyrolyze
def panel(positions):
    with grid("board"):
        for item in keyed(tuple(enumerate(positions)), key=lambda pair: pair[1]):
            index, position = item
            advertise_mount(
                public_cell(index),
                target=CELL(row=position[0], column=position[1]),
            )
        with mount(public_cell(0)):
            text("cell-0", "Cell 0")
        with mount(public_cell(1)):
            text("cell-1", "Cell 1")
        with mount(public_cell(2)):
            text("cell-2", "Cell 2")
        with mount(public_cell(3)):
            text("cell-3", "Cell 3")
""",
        CELL=cell_selector,
    )

    ctx = backend.context(namespace["panel"], positions_1, initial_generation=0)
    first = run_pyro(ctx.get())
    second = run_pyro(ctx.run(positions_2).get())

    assert _grid_cells(first) == {
        (0, 0): ("Cell 0", 0),
        (0, 1): ("Cell 1", 0),
        (1, 0): ("Cell 2", 0),
        (1, 1): ("Cell 3", 0),
    }
    assert _grid_cells(second) == {
        (0, 0): ("Cell 3", 0),
        (0, 1): ("Cell 0", 0),
        (1, 0): ("Cell 1", 0),
        (1, 1): ("Cell 2", 0),
    }
    assert second.generation == 1


def test_generic_backend_advert_routed_incompatible_child_raises_from_generated_inserter() -> None:
    backend = BuildPyroNodeBackend(_advert_specs(), module_name="example.generic_backend.advert_incompat")
    child_selector = backend.selector_family("child")
    public_key = mount_key("body")

    namespace = _load_program(
        backend,
        "compat_panel",
        f"""
from pyrolyze.api import advertise_mount, mount
from {backend.module_name} import menu, text_row

@pyrolyze
def panel():
    with text_row("root"):
        advertise_mount(PUBLIC, target=CHILD, default=True)
        with mount(PUBLIC):
            menu("menu")
""",
        PUBLIC=public_key,
        CHILD=child_selector,
    )

    with pytest.raises(PyrolyzeMountCompatibilityError, match="text_row"):
        backend.context(namespace["panel"]).get()
