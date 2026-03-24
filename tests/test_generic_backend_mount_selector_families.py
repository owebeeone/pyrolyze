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


def _selector_specs() -> tuple[NodeGenSpec, ...]:
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
            name="frame",
            base_name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            mounts=(
                MountSpec(
                    name="body",
                    accepted_base="node",
                    interface=MountInterfaceKind.SINGLE,
                    default=True,
                ),
            ),
        ),
        NodeGenSpec(
            name="columns",
            base_name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            mounts=(
                MountSpec(
                    name="slot",
                    accepted_base="node",
                    interface=MountInterfaceKind.KEYED,
                    params=(MountParam(name="index", annotation=TypeRef("int"), keyed=True),),
                ),
            ),
        ),
        NodeGenSpec(
            name="board",
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
                        MountParam(name="colour", annotation=TypeRef("str"), keyed=False),
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


def test_selector_family_zero_keyed_params_routes_to_single_bucket() -> None:
    backend = BuildPyroNodeBackend(_selector_specs(), module_name="example.generic_backend.selector.zero")
    body_selector = backend.selector_family("body")
    public_key = mount_key("body")

    namespace = _load_program(
        backend,
        "zero_panel",
        f"""
from pyrolyze.api import advertise_mount, mount
from {backend.module_name} import frame, text

@pyrolyze
def panel():
    with frame("root"):
        advertise_mount(PUBLIC, target=BODY, default=True)
        with mount(PUBLIC):
            text("leaf", "Leaf")
""",
        PUBLIC=public_key,
        BODY=body_selector,
    )

    snapshot = run_pyro(backend.context(namespace["panel"]).get())
    bucket = snapshot.mounts["body"][0]

    assert bucket.key.args == ()
    assert bucket.values.kwargs == {}
    assert bucket.entries[0].node.kwargs["text"] == "Leaf"


def test_selector_family_one_keyed_param_creates_distinct_buckets() -> None:
    backend = BuildPyroNodeBackend(_selector_specs(), module_name="example.generic_backend.selector.one")
    slot_selector = backend.selector_family("slot")

    namespace = _load_program(
        backend,
        "one_panel",
        f"""
from pyrolyze.api import advertise_mount, mount, mount_key
from {backend.module_name} import columns, text

def public_slot(index):
    return mount_key(("slot", index))

@pyrolyze
def panel():
    with columns("root"):
        advertise_mount(public_slot(0), target=SLOT(index=0))
        advertise_mount(public_slot(1), target=SLOT(index=1))
        with mount(public_slot(0)):
            text("left", "Left")
        with mount(public_slot(1)):
            text("right", "Right")
""",
        SLOT=slot_selector,
    )

    snapshot = run_pyro(backend.context(namespace["panel"]).get())
    buckets = {bucket.key.args: bucket.entries[0].node.kwargs["text"] for bucket in snapshot.mounts["slot"]}

    assert buckets == {
        (0,): "Left",
        (1,): "Right",
    }


def test_selector_family_multiple_keyed_params_keep_bucket_identity_separate() -> None:
    backend = BuildPyroNodeBackend(_selector_specs(), module_name="example.generic_backend.selector.multi")
    cell_selector = backend.selector_family("cell")

    namespace = _load_program(
        backend,
        "multi_panel",
        f"""
from pyrolyze.api import advertise_mount, mount, mount_key
from {backend.module_name} import board, text

def public_cell(name):
    return mount_key(("cell", name))

@pyrolyze
def panel():
    with board("root"):
        advertise_mount(public_cell("a"), target=CELL(row=0, column=0, colour="red"))
        advertise_mount(public_cell("b"), target=CELL(row=1, column=1, colour="blue"))
        with mount(public_cell("a")):
            text("a", "A")
        with mount(public_cell("b")):
            text("b", "B")
""",
        CELL=cell_selector,
    )

    snapshot = run_pyro(backend.context(namespace["panel"]).get())
    buckets = {
        bucket.key.args: (bucket.values.kwargs["colour"], bucket.entries[0].node.kwargs["text"])
        for bucket in snapshot.mounts["cell"]
    }

    assert buckets == {
        (0, 0): ("red", "A"),
        (1, 1): ("blue", "B"),
    }


def test_selector_family_non_key_values_can_change_without_key_drift() -> None:
    backend = BuildPyroNodeBackend(_selector_specs(), module_name="example.generic_backend.selector.values")
    cell_selector = backend.selector_family("cell")
    public_key = mount_key("main_cell")

    namespace = _load_program(
        backend,
        "values_panel",
        f"""
from pyrolyze.api import advertise_mount, mount
from {backend.module_name} import board, text

@pyrolyze
def panel(colour):
    with board("root"):
        advertise_mount(PUBLIC, target=CELL(row=0, column=0, colour=colour))
        with mount(PUBLIC):
            text("leaf", "Leaf")
""",
        PUBLIC=public_key,
        CELL=cell_selector,
    )

    ctx = backend.context(namespace["panel"], "red", initial_generation=10)
    first = run_pyro(ctx.get())
    second = run_pyro(ctx.run("blue").get())

    first_bucket = first.mounts["cell"][0]
    second_bucket = second.mounts["cell"][0]

    assert first_bucket.key.args == (0, 0)
    assert second_bucket.key.args == (0, 0)
    assert first_bucket.values.kwargs["colour"] == "red"
    assert second_bucket.values.kwargs["colour"] == "blue"
