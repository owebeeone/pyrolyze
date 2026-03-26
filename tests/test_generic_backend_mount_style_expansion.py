from __future__ import annotations

from pyrolyze.backends.model import MountReplayKind, TypeRef
from pyrolyze.testing.generic_backend import (
    BuildPyroNodeBackend,
    MountInterfaceKind,
    MountPointProfile,
    MountStyleVariant,
    MountVariantSpec,
    NodeGenSpec,
    ParamSpec,
)


def _expanded_specs() -> tuple[NodeGenSpec, ...]:
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
            name="host",
            base_name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            mounts=(
                MountVariantSpec(
                    name="child",
                    accepted_base="node",
                    profiles=(
                        MountPointProfile(
                            label="ordered_index",
                            style=MountStyleVariant(
                                label="ordered_index",
                                interface=MountInterfaceKind.ORDERED,
                                replay_kind=MountReplayKind.INDEX,
                            ),
                            mutation_policy="place_only",
                        ),
                        MountPointProfile(
                            label="tk_pack_surface",
                            style=MountStyleVariant(
                                label="ordered_sync_preferred",
                                interface=MountInterfaceKind.ORDERED,
                                replay_kind=MountReplayKind.NONE,
                                prefer_sync=True,
                            ),
                            mutation_policy="replay_then_sync",
                            small_delta_threshold=8,
                        ),
                    ),
                ),
            ),
        ),
    )


def test_mount_variant_specs_expand_into_concrete_mount_surfaces() -> None:
    backend = BuildPyroNodeBackend(
        _expanded_specs(),
        module_name="example.generic_backend.mount_style_expansion",
    )

    host_spec = next(spec for spec in backend.node_specs if spec.name == "host")

    assert tuple(mount.name for mount in host_spec.mounts) == (
        "child_ordered_index",
        "child_tk_pack_surface",
    )
    assert host_spec.mounts[0].style_label == "ordered_index"
    assert host_spec.mounts[0].profile_label == "ordered_index"
    assert host_spec.mounts[0].mutation_policy == "place_only"
    assert host_spec.mounts[1].style_label == "ordered_sync_preferred"
    assert host_spec.mounts[1].profile_label == "tk_pack_surface"
    assert host_spec.mounts[1].mutation_policy == "replay_then_sync"
    assert host_spec.mounts[1].small_delta_threshold == 8


def test_snapshot_exposes_style_and_profile_identity_for_expanded_mount_surface() -> None:
    backend = BuildPyroNodeBackend(
        _expanded_specs(),
        module_name="example.generic_backend.mount_style_expansion.snapshot",
    )

    host_type = backend.pyro_class("host")
    text_type = backend.pyro_class("text")
    root = host_type("root")
    child = text_type("first", "First")
    root.add_child_tk_pack_surface(child)

    snapshot = root.to_pyro_node()
    metadata = snapshot.mount_metadata["child_tk_pack_surface"]

    assert tuple(snapshot.mounts) == ("child_tk_pack_surface",)
    assert metadata["profile_label"] == "tk_pack_surface"
    assert metadata["style_label"] == "ordered_sync_preferred"
    assert metadata["interface"] == "ordered_mount"
    assert metadata["replay_kind"] == "none"
    assert metadata["prefer_sync"] is True
    assert metadata["mutation_policy"] == "replay_then_sync"
    assert metadata["small_delta_threshold"] == 8
