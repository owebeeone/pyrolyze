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
    run_pyro,
)


LEFT = mount_key("left")
RIGHT = mount_key("right")


def _branch_specs() -> tuple[NodeGenSpec, ...]:
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


def _build_branch_program(backend: BuildPyroNodeBackend) -> dict[str, object]:
    child_selector = backend.selector_family("child")
    return _load_program(
        backend,
        "branch_panel",
        f"""
from pyrolyze.api import advertise_mount, mount
from {backend.module_name} import row, text

@pyrolyze
def panel(show_provider, show_left, show_right, reverse_consumers):
    with row("root"):
        text("before", "before")
        if show_provider:
            advertise_mount(LEFT, target=CHILD)
            text("middle", "middle")
            advertise_mount(RIGHT, target=CHILD)
        else:
            text("middle", "middle")
        text("after", "after")

        if reverse_consumers:
            if show_right:
                with mount(RIGHT):
                    text("right-a", "Right A")
                    text("right-b", "Right B")
            if show_left:
                with mount(LEFT):
                    text("left-a", "Left A")
                    text("left-b", "Left B")
        else:
            if show_left:
                with mount(LEFT):
                    text("left-a", "Left A")
                    text("left-b", "Left B")
            if show_right:
                with mount(RIGHT):
                    text("right-a", "Right A")
                    text("right-b", "Right B")
""",
        LEFT=LEFT,
        RIGHT=RIGHT,
        CHILD=child_selector,
    )


def test_branching_two_sibling_advert_branches_route_to_separate_anchors() -> None:
    backend = BuildPyroNodeBackend(_branch_specs(), module_name="example.generic_backend.branching.basic")
    namespace = _build_branch_program(backend)

    snapshot = run_pyro(backend.context(namespace["panel"], True, True, True, False).get())

    assert _child_texts(snapshot) == (
        "before",
        "Left A",
        "Left B",
        "middle",
        "Right A",
        "Right B",
        "after",
    )


def test_branching_one_branch_can_disappear_while_the_other_remains() -> None:
    backend = BuildPyroNodeBackend(_branch_specs(), module_name="example.generic_backend.branching.one_removed")
    namespace = _build_branch_program(backend)

    rerender_ctx = backend.context(namespace["panel"], True, True, True, False, initial_generation=0)
    _ = rerender_ctx.get()
    rerendered = run_pyro(rerender_ctx.run(True, True, False, False).get())

    fresh = run_pyro(backend.context(namespace["panel"], True, True, False, False, initial_generation=1).get())

    assert _child_texts(rerendered) == _child_texts(fresh)
    assert _child_texts(rerendered) == (
        "before",
        "Left A",
        "Left B",
        "middle",
        "after",
    )


def test_branching_provider_and_consumers_can_disappear_without_zombies() -> None:
    backend = BuildPyroNodeBackend(_branch_specs(), module_name="example.generic_backend.branching.provider_removed")
    namespace = _build_branch_program(backend)

    rerender_ctx = backend.context(namespace["panel"], True, True, True, False, initial_generation=0)
    _ = rerender_ctx.get()
    rerendered = run_pyro(rerender_ctx.run(False, False, False, False).get())

    fresh = run_pyro(backend.context(namespace["panel"], False, False, False, False, initial_generation=1).get())

    assert _child_texts(rerendered) == _child_texts(fresh)
    assert _child_texts(rerendered) == ("before", "middle", "after")


def test_branching_reordering_consumer_blocks_does_not_change_anchor_placement() -> None:
    backend = BuildPyroNodeBackend(_branch_specs(), module_name="example.generic_backend.branching.reorder")
    namespace = _build_branch_program(backend)

    first = run_pyro(backend.context(namespace["panel"], True, True, True, False, initial_generation=10).get())
    second = run_pyro(backend.context(namespace["panel"], True, True, True, True, initial_generation=10).get())

    assert first == second
    assert _child_texts(second) == (
        "before",
        "Left A",
        "Left B",
        "middle",
        "Right A",
        "Right B",
        "after",
    )
