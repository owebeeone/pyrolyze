"""Declarative spec model for the generic testing backend."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum

from pyrolyze.backends.model import MountMutationPolicy, MountReplayKind, TypeRef


class MountInterfaceKind(StrEnum):
    ORDERED = "ordered_mount"
    SINGLE = "single_mount"
    KEYED = "keyed_mount"


class HostPlacementChildKind(StrEnum):
    WIDGET = "widget"
    NESTED_CONTAINER = "nested_container"


@dataclass(frozen=True, slots=True)
class ParamSpec:
    name: str
    annotation: TypeRef | None = None
    default_repr: str | None = None
    affects_identity: bool = True


@dataclass(frozen=True, slots=True)
class MountParam:
    name: str
    annotation: TypeRef | None = None
    keyed: bool = False
    default_repr: str | None = None


@dataclass(frozen=True, slots=True)
class MountStyleVariant:
    label: str
    interface: MountInterfaceKind
    replay_kind: MountReplayKind = MountReplayKind.NONE
    prefer_sync: bool = False


@dataclass(frozen=True, slots=True)
class HostSurfaceStyle:
    label: str
    ordered: bool = True
    supports_anchor_before: bool = False
    keyed: bool = False


@dataclass(frozen=True, slots=True)
class HostPlacementProfile:
    label: str
    child_kind: HostPlacementChildKind = HostPlacementChildKind.WIDGET
    stable_slot_identity: bool = True
    separates_structure_from_placement: bool = True


@dataclass(frozen=True, slots=True)
class MountPointProfile:
    label: str
    style: MountStyleVariant
    mutation_policy: MountMutationPolicy | None = None
    small_delta_threshold: int | None = None
    host_surface_style: HostSurfaceStyle | None = None
    host_placement_profile: HostPlacementProfile | None = None


@dataclass(frozen=True, slots=True)
class MountSpec:
    name: str
    accepted_kind: str | None = None
    accepted_base: str | None = None
    interface: MountInterfaceKind = MountInterfaceKind.ORDERED
    params: tuple[MountParam, ...] = ()
    default: bool = False
    replay_kind: MountReplayKind = MountReplayKind.NONE
    prefer_sync: bool = False
    style_label: str | None = None
    profile_label: str | None = None
    mutation_policy: MountMutationPolicy | None = None
    small_delta_threshold: int | None = None
    host_surface_label: str | None = None
    host_surface_ordered: bool | None = None
    host_surface_supports_anchor_before: bool | None = None
    host_surface_keyed: bool | None = None
    host_placement_profile_label: str | None = None
    host_child_kind: HostPlacementChildKind | None = None
    host_stable_slot_identity: bool | None = None
    host_separates_structure_from_placement: bool | None = None


@dataclass(frozen=True, slots=True)
class MountVariantSpec:
    name: str
    accepted_kind: str | None = None
    accepted_base: str | None = None
    params: tuple[MountParam, ...] = ()
    default: bool = False
    profiles: tuple[MountPointProfile, ...] = ()


@dataclass(frozen=True, slots=True)
class NodeGenSpec:
    name: str
    base_name: str | None = None
    constructor: tuple[ParamSpec, ...] = ()
    mounts: tuple[MountSpec | MountVariantSpec, ...] = ()


def validate_node_specs(specs: tuple[NodeGenSpec, ...] | list[NodeGenSpec]) -> tuple[NodeGenSpec, ...]:
    validated = tuple(_expand_node_spec(spec) for spec in specs)
    names: dict[str, NodeGenSpec] = {}
    for spec in validated:
        if spec.name in names:
            raise ValueError(f"duplicate node spec name {spec.name!r}")
        names[spec.name] = spec

    for spec in validated:
        if spec.base_name is not None and spec.base_name not in names:
            raise ValueError(f"unknown base {spec.base_name!r} for node spec {spec.name!r}")

        param_names: set[str] = set()
        for param in spec.constructor:
            if param.name in param_names:
                raise ValueError(f"duplicate constructor param {param.name!r} on {spec.name!r}")
            param_names.add(param.name)

        mount_names: set[str] = set()
        default_count = 0
        for mount in spec.mounts:
            if mount.name in mount_names:
                raise ValueError(f"duplicate mount spec name {mount.name!r} on {spec.name!r}")
            mount_names.add(mount.name)
            if mount.default:
                default_count += 1
            if mount.accepted_kind is None and mount.accepted_base is None:
                raise ValueError(f"mount {mount.name!r} on {spec.name!r} is missing accepted type")
            if mount.accepted_kind is not None and mount.accepted_kind not in names:
                raise ValueError(
                    f"unknown accepted kind {mount.accepted_kind!r} for mount {mount.name!r} on {spec.name!r}"
                )
            if mount.accepted_base is not None and mount.accepted_base not in names:
                raise ValueError(
                    f"unknown accepted base {mount.accepted_base!r} for mount {mount.name!r} on {spec.name!r}"
                )
        if default_count > 1:
            raise ValueError(f"multiple default mounts on {spec.name!r}")

    return validated


def _expand_node_spec(spec: NodeGenSpec) -> NodeGenSpec:
    expanded_mounts: list[MountSpec] = []
    for mount in spec.mounts:
        if isinstance(mount, MountSpec):
            expanded_mounts.append(mount)
            continue
        if not mount.profiles:
            raise ValueError(f"mount variant {mount.name!r} on {spec.name!r} has no profiles")
        use_default = mount.default and len(mount.profiles) == 1
        for profile in mount.profiles:
            _validate_mount_profile(spec.name, mount.name, profile)
            expanded_mounts.append(
                MountSpec(
                    name=f"{mount.name}_{profile.label}",
                    accepted_kind=mount.accepted_kind,
                    accepted_base=mount.accepted_base,
                    interface=profile.style.interface,
                    params=mount.params,
                    default=use_default,
                    replay_kind=profile.style.replay_kind,
                    prefer_sync=profile.style.prefer_sync,
                    style_label=profile.style.label,
                    profile_label=profile.label,
                    mutation_policy=profile.mutation_policy,
                    small_delta_threshold=profile.small_delta_threshold,
                    host_surface_label=(
                        profile.host_surface_style.label
                        if profile.host_surface_style is not None
                        else None
                    ),
                    host_surface_ordered=(
                        profile.host_surface_style.ordered
                        if profile.host_surface_style is not None
                        else None
                    ),
                    host_surface_supports_anchor_before=(
                        profile.host_surface_style.supports_anchor_before
                        if profile.host_surface_style is not None
                        else None
                    ),
                    host_surface_keyed=(
                        profile.host_surface_style.keyed
                        if profile.host_surface_style is not None
                        else None
                    ),
                    host_placement_profile_label=(
                        profile.host_placement_profile.label
                        if profile.host_placement_profile is not None
                        else None
                    ),
                    host_child_kind=(
                        profile.host_placement_profile.child_kind
                        if profile.host_placement_profile is not None
                        else None
                    ),
                    host_stable_slot_identity=(
                        profile.host_placement_profile.stable_slot_identity
                        if profile.host_placement_profile is not None
                        else None
                    ),
                    host_separates_structure_from_placement=(
                        profile.host_placement_profile.separates_structure_from_placement
                        if profile.host_placement_profile is not None
                        else None
                    ),
                )
            )
    return replace(spec, mounts=tuple(expanded_mounts))


def _validate_mount_profile(node_name: str, mount_name: str, profile: MountPointProfile) -> None:
    if (profile.host_surface_style is None) != (profile.host_placement_profile is None):
        raise ValueError(
            f"mount variant {mount_name!r} on {node_name!r} must specify host surface style "
            "and host placement profile together"
        )
    host_surface = profile.host_surface_style
    host_placement = profile.host_placement_profile
    if host_surface is None or host_placement is None:
        return
    if host_surface.supports_anchor_before and profile.style.replay_kind is not MountReplayKind.ANCHOR_BEFORE:
        raise ValueError(
            f"mount variant {mount_name!r} on {node_name!r} declares anchor-before host "
            f"surface {host_surface.label!r} without an anchor-before replay style"
        )
    if host_surface.keyed and profile.style.interface is not MountInterfaceKind.KEYED:
        raise ValueError(
            f"mount variant {mount_name!r} on {node_name!r} declares keyed host surface "
            f"{host_surface.label!r} without a keyed mount style"
        )
    if host_placement.child_kind is HostPlacementChildKind.NESTED_CONTAINER:
        if not host_placement.stable_slot_identity:
            raise ValueError(
                f"mount variant {mount_name!r} on {node_name!r} declares nested-container "
                "placement without stable slot identity"
            )
        if not host_placement.separates_structure_from_placement:
            raise ValueError(
                f"mount variant {mount_name!r} on {node_name!r} declares nested-container "
                "placement without structural/placement separation"
            )


__all__ = [
    "HostPlacementChildKind",
    "HostPlacementProfile",
    "HostSurfaceStyle",
    "MountPointProfile",
    "MountInterfaceKind",
    "MountParam",
    "MountSpec",
    "MountStyleVariant",
    "MountVariantSpec",
    "NodeGenSpec",
    "ParamSpec",
    "validate_node_specs",
]
