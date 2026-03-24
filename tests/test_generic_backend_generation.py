from __future__ import annotations

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
    run_pyro,
)


def _row_specs() -> tuple[NodeGenSpec, ...]:
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
    )


def _grid_specs() -> tuple[NodeGenSpec, ...]:
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


def _row_panel_program(backend: BuildPyroNodeBackend) -> dict[str, object]:
    child_selector = backend.selector_family("child")
    return _load_program(
        backend,
        "row_panel",
        f"""
from pyrolyze.api import advertise_mount, mount
from {backend.module_name} import row, text

@pyrolyze
def panel(label):
    with row("root"):
        text("before", "before")
        advertise_mount(PUBLIC, target=CHILD, default=True)
        with mount(PUBLIC):
            text("leaf", label)
        text("after", "after")
""",
        PUBLIC=mount_key("body"),
        CHILD=child_selector,
    )


def _grid_panel_program(backend: BuildPyroNodeBackend) -> dict[str, object]:
    cell_selector = backend.selector_family("cell")
    return _load_program(
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
        for index in keyed((0, 1, 2, 3), key=lambda value: value):
            with mount(public_cell(index)):
                text(f"cell-{{index}}", f"Cell {{index}}")
""",
        CELL=cell_selector,
    )


def test_generation_initial_render_defaults_to_zero() -> None:
    backend = BuildPyroNodeBackend(_row_specs(), module_name="example.generic_backend.generation.initial")
    namespace = _row_panel_program(backend)

    snapshot = run_pyro(backend.context(namespace["panel"], "hello").get())

    assert snapshot.generation == 0
    assert [entry.node.generation for entry in snapshot.mounts["child"][0].entries] == [0, 0, 0]


def test_generation_run_auto_increments_and_explicit_override_are_respected() -> None:
    backend = BuildPyroNodeBackend(_row_specs(), module_name="example.generic_backend.generation.override")
    namespace = _row_panel_program(backend)

    ctx = backend.context(namespace["panel"], "hello", initial_generation=10)

    first = run_pyro(ctx.get())
    second = run_pyro(ctx.run("changed").get())
    third = run_pyro(ctx.run("again", generation=25).get())

    assert ctx.generation == 25
    assert first.generation == 10
    assert second.generation == 11
    assert third.generation == 25


def test_generation_unchanged_rerender_keeps_prior_generations() -> None:
    backend = BuildPyroNodeBackend(_row_specs(), module_name="example.generic_backend.generation.unchanged")
    namespace = _row_panel_program(backend)

    ctx = backend.context(namespace["panel"], "same", initial_generation=10)
    first = run_pyro(ctx.get())
    second = run_pyro(ctx.run("same").get())

    assert second.generation == 10
    assert [entry.node.generation for entry in second.mounts["child"][0].entries] == [10, 10, 10]
    assert first == second


def test_generation_changed_child_updates_only_changed_path() -> None:
    backend = BuildPyroNodeBackend(_row_specs(), module_name="example.generic_backend.generation.changed")
    namespace = _row_panel_program(backend)

    ctx = backend.context(namespace["panel"], "same", initial_generation=10)
    _ = run_pyro(ctx.get())
    second = run_pyro(ctx.run("changed").get())

    assert second.generation == 11
    assert [entry.node.generation for entry in second.mounts["child"][0].entries] == [10, 11, 10]
    assert [entry.node.kwargs["text"] for entry in second.mounts["child"][0].entries] == [
        "before",
        "changed",
        "after",
    ]


def test_generation_keyed_relocation_updates_container_but_retains_child_generations() -> None:
    backend = BuildPyroNodeBackend(_grid_specs(), module_name="example.generic_backend.generation.rotation")
    namespace = _grid_panel_program(backend)
    positions = ((0, 0), (0, 1), (1, 0), (1, 1))
    rotated = ((0, 1), (1, 0), (1, 1), (0, 0))

    ctx = backend.context(namespace["panel"], positions, initial_generation=0)
    _ = run_pyro(ctx.get())
    second = run_pyro(ctx.run(rotated).get())

    assert second.generation == 1
    assert {
        bucket.key.args: (bucket.entries[0].node.kwargs["text"], bucket.entries[0].node.generation)
        for bucket in second.mounts["cell"]
    } == {
        (0, 0): ("Cell 3", 0),
        (0, 1): ("Cell 0", 0),
        (1, 0): ("Cell 1", 0),
        (1, 1): ("Cell 2", 0),
    }
