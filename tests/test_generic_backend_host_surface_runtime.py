from __future__ import annotations

from pyrolyze.api import pyrolyze
from pyrolyze.backends.model import MountMutationPolicy, MountReplayKind, TypeRef
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.testing.generic_backend import (
    BuildPyroNodeBackend,
    HostPlacementChildKind,
    HostPlacementProfile,
    HostSurfaceStyle,
    MountInterfaceKind,
    MountPointProfile,
    MountStyleVariant,
    MountVariantSpec,
    NodeGenSpec,
    ParamSpec,
    run_pyro,
)


def _host_surface_backend() -> BuildPyroNodeBackend:
    return BuildPyroNodeBackend(
        (
            NodeGenSpec(
                name="node",
                constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            ),
            NodeGenSpec(
                name="text",
                base_name="node",
                host_child_kind=HostPlacementChildKind.WIDGET,
                constructor=(
                    ParamSpec(name="name", annotation=TypeRef("str")),
                    ParamSpec(name="text", annotation=TypeRef("str")),
                ),
            ),
            NodeGenSpec(
                name="row",
                base_name="node",
                host_child_kind=HostPlacementChildKind.NESTED_CONTAINER,
                constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
                mounts=(
                    MountVariantSpec(
                        name="child",
                        accepted_base="node",
                        default=True,
                        profiles=(
                            MountPointProfile(
                                label="nested_layout_surface",
                                style=MountStyleVariant(
                                    label="ordered_index",
                                    interface=MountInterfaceKind.ORDERED,
                                    replay_kind=MountReplayKind.INDEX,
                                ),
                                mutation_policy=MountMutationPolicy.PLACE_ONLY,
                                host_surface_style=HostSurfaceStyle(label="ordered_slots"),
                                host_placement_profile=HostPlacementProfile(
                                    label="nested_container_child",
                                    allowed_child_kinds=(
                                        HostPlacementChildKind.WIDGET,
                                        HostPlacementChildKind.NESTED_CONTAINER,
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            NodeGenSpec(
                name="host",
                base_name="node",
                constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
                mounts=(
                    MountVariantSpec(
                        name="child",
                        accepted_base="node",
                        default=True,
                        profiles=(
                            MountPointProfile(
                                label="nested_layout_surface",
                                style=MountStyleVariant(
                                    label="ordered_index",
                                    interface=MountInterfaceKind.ORDERED,
                                    replay_kind=MountReplayKind.INDEX,
                                ),
                                mutation_policy=MountMutationPolicy.PLACE_ONLY,
                                host_surface_style=HostSurfaceStyle(label="ordered_slots"),
                                host_placement_profile=HostPlacementProfile(
                                    label="nested_container_child",
                                    allowed_child_kinds=(
                                        HostPlacementChildKind.WIDGET,
                                        HostPlacementChildKind.NESTED_CONTAINER,
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
        module_name="example.generic_backend.host_surface_runtime",
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


def test_snapshot_represents_host_surface_order_separately_from_structural_mount_order() -> None:
    backend = _host_surface_backend()
    host_type = backend.pyro_class("host")
    row_type = backend.pyro_class("row")
    text_type = backend.pyro_class("text")

    root = host_type("root")
    top = text_type("top", "Top")
    row = row_type("controls")
    bottom = text_type("bottom", "Bottom")
    root.add_child_nested_layout_surface(top)
    root.add_child_nested_layout_surface(row)
    root.add_child_nested_layout_surface(bottom)

    snapshot = root.to_pyro_node()
    assert tuple(entry.node.kwargs["name"] for entry in snapshot.mounts["child_nested_layout_surface"][0].entries) == (
        "top",
        "controls",
        "bottom",
    )
    assert tuple(entry.node.kwargs["name"] for entry in snapshot.host_surfaces["child_nested_layout_surface"].entries) == (
        "top",
        "controls",
        "bottom",
    )
    assert tuple(entry.child_kind.value for entry in snapshot.host_surfaces["child_nested_layout_surface"].entries) == (
        "widget",
        "nested_container",
        "widget",
    )

    builder = snapshot.to_builder()
    surface = builder.host_surfaces["child_nested_layout_surface"]
    surface.entries[1], surface.entries[2] = surface.entries[2], surface.entries[1]
    shifted = builder.build()

    assert tuple(entry.node.kwargs["name"] for entry in shifted.mounts["child_nested_layout_surface"][0].entries) == (
        "top",
        "controls",
        "bottom",
    )
    assert tuple(entry.node.kwargs["name"] for entry in shifted.host_surfaces["child_nested_layout_surface"].entries) == (
        "top",
        "bottom",
        "controls",
    )
    assert tuple(entry.child_kind.value for entry in shifted.host_surfaces["child_nested_layout_surface"].entries) == (
        "widget",
        "widget",
        "nested_container",
    )


def test_empty_host_surface_cleans_up_with_sync_detach() -> None:
    backend = _host_surface_backend()
    host_type = backend.pyro_class("host")
    text_type = backend.pyro_class("text")

    root = host_type("root")
    child = text_type("only", "Only")
    root.add_child_nested_layout_surface(child)
    root.sync_child_nested_layout_surfaces(())

    snapshot = root.to_pyro_node()

    assert "child_nested_layout_surface" not in snapshot.mounts
    assert "child_nested_layout_surface" not in snapshot.host_surfaces
    assert any(
        operation.kind == "surface_sync" and operation.details["count"] == 0
        for operation in snapshot.host_surface_operations
    )


def test_host_surface_snapshot_and_operations_are_deterministic() -> None:
    backend = _host_surface_backend()
    host_type = backend.pyro_class("host")
    text_type = backend.pyro_class("text")

    root = host_type("root")
    first = text_type("first", "First")
    second = text_type("second", "Second")
    root.add_child_nested_layout_surface(first)
    root.insert_child_nested_layout_surface(0, second)

    snapshot = root.to_pyro_node()

    assert snapshot.host_surface_metadata["child_nested_layout_surface"]["host_surface_label"] == "ordered_slots"
    assert snapshot.host_surface_metadata["child_nested_layout_surface"]["host_allowed_child_kinds"] == (
        "widget",
        "nested_container",
    )
    assert tuple(entry.node.kwargs["name"] for entry in snapshot.host_surfaces["child_nested_layout_surface"].entries) == (
        "second",
        "first",
    )
    assert tuple(entry.child_kind.value for entry in snapshot.host_surfaces["child_nested_layout_surface"].entries) == (
        "widget",
        "widget",
    )
    assert [operation.kind for operation in snapshot.host_surface_operations] == [
        "surface_attach",
        "surface_attach",
        "surface_place_index",
    ]


def test_mixed_host_surface_retained_nested_row_stays_before_trailing_sibling_under_branch_churn() -> None:
    backend = _host_surface_backend()
    namespace = _load_program(
        backend,
        "branch_before",
        f"""
from {backend.module_name} import host, row, text

@pyrolyze
def panel(show_top):
    with host("root"):
        if show_top:
            text("top", "Top")
        else:
            text("top", "Top changed")
        text("page", "Page size: 50")
        with row("controls"):
            text("minus", "-")
            text("count", "Count")
            text("plus", "+")
        text("bottom", "Bottom")
""",
    )

    rerender_ctx = backend.context(namespace["panel"], True, initial_generation=0)
    _ = rerender_ctx.get()
    rerendered = run_pyro(rerender_ctx.run(False).get())
    fresh = run_pyro(backend.context(namespace["panel"], False, initial_generation=1).get())

    rerendered_structural = tuple(
        entry.node.kwargs["name"]
        for entry in rerendered.mounts["child_nested_layout_surface"][0].entries
    )
    rerendered_host = tuple(
        entry.node.kwargs["name"]
        for entry in rerendered.host_surfaces["child_nested_layout_surface"].entries
    )
    fresh_host = tuple(
        entry.node.kwargs["name"]
        for entry in fresh.host_surfaces["child_nested_layout_surface"].entries
    )

    assert rerendered_structural == ("top", "page", "controls", "bottom")
    assert rerendered_host == ("top", "page", "controls", "bottom")
    assert fresh_host == rerendered_host
    assert tuple(
        entry.child_kind.value
        for entry in rerendered.host_surfaces["child_nested_layout_surface"].entries
    ) == ("widget", "widget", "nested_container", "widget")
    assert rerendered_host.index("controls") < rerendered_host.index("bottom")
    assert rerendered.mount_metadata["child_nested_layout_surface"]["host_surface_label"] == "ordered_slots"
    assert rerendered.host_surface_metadata["child_nested_layout_surface"]["host_placement_profile_label"] == (
        "nested_container_child"
    )


def test_mixed_host_surface_retained_nested_row_stays_before_trailing_sibling_under_tail_branch_churn() -> None:
    backend = _host_surface_backend()
    namespace = _load_program(
        backend,
        "branch_after",
        f"""
from {backend.module_name} import host, row, text

@pyrolyze
def panel(show_bottom):
    with host("root"):
        text("top", "Top")
        text("page", "Page size: 50")
        with row("controls"):
            text("minus", "-")
            text("count", "Count")
            text("plus", "+")
        if show_bottom:
            text("bottom", "Bottom")
        else:
            text("bottom", "Bottom changed")
""",
    )

    rerender_ctx = backend.context(namespace["panel"], True, initial_generation=0)
    _ = rerender_ctx.get()
    rerendered = run_pyro(rerender_ctx.run(False).get())
    fresh = run_pyro(backend.context(namespace["panel"], False, initial_generation=1).get())

    rerendered_host = tuple(
        entry.node.kwargs["name"]
        for entry in rerendered.host_surfaces["child_nested_layout_surface"].entries
    )
    fresh_host = tuple(
        entry.node.kwargs["name"]
        for entry in fresh.host_surfaces["child_nested_layout_surface"].entries
    )

    assert rerendered_host == ("top", "page", "controls", "bottom")
    assert fresh_host == rerendered_host
    assert tuple(
        entry.child_kind.value
        for entry in rerendered.host_surfaces["child_nested_layout_surface"].entries
    ) == ("widget", "widget", "nested_container", "widget")
    assert rerendered_host.index("controls") < rerendered_host.index("bottom")
