from __future__ import annotations

from pyrolyze.backends.model import MountMutationPolicy, MountReplayKind, TypeRef
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
                                    child_kind=HostPlacementChildKind.NESTED_CONTAINER,
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
                                    child_kind=HostPlacementChildKind.NESTED_CONTAINER,
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
        module_name="example.generic_backend.host_surface_runtime",
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
    assert tuple(entry.node.kwargs["name"] for entry in snapshot.host_surfaces["child_nested_layout_surface"].entries) == (
        "second",
        "first",
    )
    assert [operation.kind for operation in snapshot.host_surface_operations] == [
        "surface_attach",
        "surface_attach",
        "surface_place_index",
    ]
