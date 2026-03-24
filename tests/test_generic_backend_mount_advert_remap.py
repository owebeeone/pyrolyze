from __future__ import annotations

from dataclasses import dataclass

from pyrolyze.api import mount_key, pyrolyze
from pyrolyze.backends.model import TypeRef
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.testing.generic_backend import (
    BuildPyroNodeBackend,
    MountInterfaceKind,
    MountSpec,
    NodeGenSpec,
    ParamSpec,
    run_pyro,
)


def _remap_specs() -> tuple[NodeGenSpec, ...]:
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


def _child_texts(snapshot: object) -> tuple[str, ...]:
    node = run_pyro(snapshot)
    return tuple(
        entry.node.kwargs.get("text", entry.node.kwargs.get("name"))
        for entry in node.mounts["child"][0].entries
    )


def test_remap_renaming_public_key_with_same_target_keeps_graph_identical() -> None:
    backend = BuildPyroNodeBackend(_remap_specs(), module_name="example.generic_backend.remap.rename")
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
        text("before", "before")
        advertise_mount(public_key, target=CHILD, default=True)
        with mount(public_key):
            text("middle", "middle")
        text("after", "after")
""",
        CHILD=child_selector,
    )

    ctx = backend.context(namespace["panel"], key_a, initial_generation=10)
    first = run_pyro(ctx.get())
    second = run_pyro(ctx.run(key_b).get())

    assert first == second
    assert _child_texts(second) == ("before", "middle", "after")


@dataclass(frozen=True, slots=True)
class _CallerKey:
    family: str
    index: int


def test_remap_caller_provided_key_object_routes_cleanly() -> None:
    backend = BuildPyroNodeBackend(_remap_specs(), module_name="example.generic_backend.remap.caller")
    child_selector = backend.selector_family("child")
    public_key = _CallerKey("body", 1)

    namespace = _load_program(
        backend,
        "caller_panel",
        f"""
from pyrolyze.api import advertise_mount, mount, mount_key
from {backend.module_name} import row, text

def public_selector(key_obj):
    return mount_key((key_obj.family, key_obj.index))

@pyrolyze
def panel(key_obj):
    public_key = public_selector(key_obj)
    with row("root"):
        text("before", "before")
        advertise_mount(public_key, target=CHILD, default=True)
        with mount(public_key):
            text("middle", "middle")
        text("after", "after")
""",
        CHILD=child_selector,
    )

    snapshot = run_pyro(backend.context(namespace["panel"], public_key).get())

    assert _child_texts(snapshot) == ("before", "middle", "after")


def test_remap_recreated_equal_key_family_values_do_not_change_graph() -> None:
    backend = BuildPyroNodeBackend(_remap_specs(), module_name="example.generic_backend.remap.recreated")
    child_selector = backend.selector_family("child")

    namespace = _load_program(
        backend,
        "recreated_panel",
        f"""
from pyrolyze.api import advertise_mount, mount, mount_key
from {backend.module_name} import row, text

def build_public_key(label):
    return mount_key(("slot", label.lower()))

@pyrolyze
def panel(label):
    public_key = build_public_key(label)
    with row("root"):
        text("before", "before")
        advertise_mount(public_key, target=CHILD, default=True)
        with mount(build_public_key(label)):
            text("middle", "middle")
        text("after", "after")
""",
        CHILD=child_selector,
    )

    ctx = backend.context(namespace["panel"], "Body", initial_generation=20)
    first = run_pyro(ctx.get())
    second = run_pyro(ctx.run("Body").get())

    assert first == second
    assert _child_texts(second) == ("before", "middle", "after")
