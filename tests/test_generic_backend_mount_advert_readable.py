from __future__ import annotations

from pyrolyze.api import mount_key, pyrolyze
from pyrolyze.backends.model import TypeRef
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.testing.generic_backend import (
    BuildPyroNodeBackend,
    MountInterfaceKind,
    MountSpec,
    NodeGenSpec,
    ParamSpec,
    PyroUiElement,
    PyroUiMountAdvertisement,
    PyroUiMountDirective,
    run_pyro,
    run_pyro_ui,
)


def _readable_specs() -> tuple[NodeGenSpec, ...]:
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


def test_readable_named_anchor_routes_children_into_obvious_gap() -> None:
    backend = BuildPyroNodeBackend(_readable_specs(), module_name="example.generic_backend.readable.named")
    child_selector = backend.selector_family("child")
    public_key = mount_key("body")

    namespace = _load_program(
        backend,
        "named_panel",
        f"""
from pyrolyze.api import advertise_mount, mount
from {backend.module_name} import row, text

@pyrolyze
def panel():
    with row("root"):
        text("hello", "hello")
        advertise_mount(PUBLIC, target=CHILD)
        with mount(PUBLIC):
            text("inserted", "inserted")
        text("world", "world")
""",
        PUBLIC=public_key,
        CHILD=child_selector,
    )

    ctx = backend.context(namespace["panel"])
    ui = run_pyro_ui(ctx.get())
    graph = run_pyro(ctx.get())

    assert _child_texts(graph) == ("hello", "inserted", "world")
    assert isinstance(ui, PyroUiElement)
    assert ui.kind == "row"
    assert isinstance(ui.children[1], PyroUiMountAdvertisement)
    assert ui.children[1].key == public_key
    assert ui.children[1].selectors == (child_selector,)
    assert isinstance(ui.children[2], PyroUiMountDirective)


def test_readable_default_advert_routes_mount_default_to_the_anchor() -> None:
    backend = BuildPyroNodeBackend(_readable_specs(), module_name="example.generic_backend.readable.default")
    child_selector = backend.selector_family("child")

    namespace = _load_program(
        backend,
        "default_panel",
        f"""
from pyrolyze.api import advertise_mount, default, mount
from {backend.module_name} import row, text

@pyrolyze
def panel():
    with row("root"):
        text("before", "before")
        advertise_mount("body", target=CHILD, default=True)
        with mount(default):
            text("middle", "middle")
        text("after", "after")
""",
        CHILD=child_selector,
    )

    ctx = backend.context(namespace["panel"])
    ui = run_pyro_ui(ctx.get())
    graph = run_pyro(ctx.get())

    assert _child_texts(graph) == ("before", "middle", "after")
    assert isinstance(ui, PyroUiElement)
    assert isinstance(ui.children[1], PyroUiMountAdvertisement)
    assert ui.children[1].default is True
    assert ui.children[1].selectors == (child_selector,)
    assert isinstance(ui.children[2], PyroUiMountDirective)


def test_readable_two_advert_anchors_preserve_order_per_anchor() -> None:
    backend = BuildPyroNodeBackend(_readable_specs(), module_name="example.generic_backend.readable.double")
    child_selector = backend.selector_family("child")
    first_key = mount_key("first")
    second_key = mount_key("second")

    namespace = _load_program(
        backend,
        "double_panel",
        f"""
from pyrolyze.api import advertise_mount, mount
from {backend.module_name} import row, text

@pyrolyze
def panel():
    with row("root"):
        text("intro", "intro")
        advertise_mount(FIRST, target=CHILD)
        text("middle", "middle")
        advertise_mount(SECOND, target=CHILD)
        text("outro", "outro")
        with mount(FIRST):
            text("a", "A")
            text("b", "B")
        with mount(SECOND):
            text("x", "X")
            text("y", "Y")
""",
        FIRST=first_key,
        SECOND=second_key,
        CHILD=child_selector,
    )

    snapshot = run_pyro(backend.context(namespace["panel"]).get())

    assert _child_texts(snapshot) == ("intro", "A", "B", "middle", "X", "Y", "outro")


def test_readable_same_input_rerender_keeps_exact_graph_snapshot() -> None:
    backend = BuildPyroNodeBackend(_readable_specs(), module_name="example.generic_backend.readable.rerender")
    child_selector = backend.selector_family("child")
    public_key = mount_key("body")

    namespace = _load_program(
        backend,
        "rerender_panel",
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
        PUBLIC=public_key,
        CHILD=child_selector,
    )

    ctx = backend.context(namespace["panel"], "same", initial_generation=10)
    first = run_pyro(ctx.get())
    second = run_pyro(ctx.run("same").get())

    assert first == second
    assert _child_texts(second) == ("before", "same", "after")
