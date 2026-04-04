#@pyrolyze

from __future__ import annotations

from dataclasses import dataclass

from pyrolyze.backends.model import MountMutationPolicy, MountReplayKind, TypeRef
from pyrolyze.testing.generic_backend import (
    BuildPyroNodeBackend,
    HostPlacementChildKind,
    HostPlacementProfile,
    HostSurfaceReconcileMode,
    HostSurfaceStyle,
    MountInterfaceKind,
    MountParam,
    MountPointProfile,
    MountSpec,
    MountStyleVariant,
    NodeGenSpec,
    ParamSpec,
)


@dataclass(frozen=True, slots=True)
class ComprehensiveBackendShape:
    base_type_count: int = 4
    leaves_per_base: int = 2
    bins_per_base: int = 2
    n_str: int = 0
    n_int: int = 0


_ROOT = "Node"
_MOUNT_ROTATION = ("Single", "Ordered", "Nested", "Keyed")


def _base_suffix(index: int) -> str:
    first = index // 26
    second = index % 26
    return f"{chr(ord('A') + first)}{chr(ord('A') + second)}"


def _base_name(index: int) -> str:
    return f"Base{_base_suffix(index)}"


def _leaf_name(base_index: int, leaf_index: int) -> str:
    return f"Leaf{_base_suffix(base_index)}{leaf_index:02d}"


def _bin_name(base_index: int, bin_index: int) -> str:
    return f"Bin{_base_suffix(base_index)}{bin_index:02d}"


def _mount_name(kind: str, base_index: int) -> str:
    return f"Mount{kind}{_base_suffix(base_index)}"


def _is_leaf_name(name: str) -> bool:
    return name.startswith("Leaf")


def _is_bin_name(name: str) -> bool:
    return name.startswith("Bin")


def _scalar_params(shape: ComprehensiveBackendShape) -> tuple[ParamSpec, ...]:
    params: list[ParamSpec] = []
    for index in range(shape.n_int):
        suffix = chr(ord("a") + index)
        params.append(ParamSpec(name=f"fint_{suffix}", annotation=TypeRef("int")))
    for index in range(shape.n_str):
        suffix = chr(ord("a") + index)
        params.append(ParamSpec(name=f"fstr_{suffix}", annotation=TypeRef("str")))
    return tuple(params)


def _single_mount_spec(base_index: int) -> MountSpec:
    name = _mount_name("Single", base_index)
    return MountSpec(
        name=name,
        accepted_base=_ROOT,
        interface=MountInterfaceKind.SINGLE,
        default=True,
        replay_kind=MountReplayKind.NONE,
        mutation_policy=MountMutationPolicy.REPLAY_THEN_SYNC,
    )


def _ordered_mount_spec(base_index: int) -> MountSpec:
    name = _mount_name("Ordered", base_index)
    return MountSpec(
        name=name,
        accepted_base=_ROOT,
        interface=MountInterfaceKind.ORDERED,
        default=True,
        replay_kind=MountReplayKind.INDEX,
        mutation_policy=MountMutationPolicy.PLACE_ONLY,
    )


def _nested_mount_spec(base_index: int) -> MountSpec:
    name = _mount_name("Nested", base_index)
    return MountSpec(
        name=name,
        accepted_base=_ROOT,
        interface=MountInterfaceKind.ORDERED,
        default=True,
        replay_kind=MountReplayKind.INDEX,
        mutation_policy=MountMutationPolicy.PLACE_ONLY,
        host_surface_label=name,
        host_surface_ordered=True,
        host_surface_reconcile_mode=HostSurfaceReconcileMode.REFERENCE,
        host_placement_profile_label=f"{name}Placement",
        host_allowed_child_kinds=(
            HostPlacementChildKind.WIDGET,
            HostPlacementChildKind.NESTED_CONTAINER,
        ),
        host_stable_slot_identity=True,
        host_separates_structure_from_placement=True,
    )


def _keyed_mount_spec(base_index: int) -> MountSpec:
    name = _mount_name("Keyed", base_index)
    return MountSpec(
        name=name,
        accepted_base=_ROOT,
        interface=MountInterfaceKind.KEYED,
        default=True,
        params=(MountParam(name="index", annotation=TypeRef("int"), keyed=True),),
        replay_kind=MountReplayKind.NONE,
        mutation_policy=MountMutationPolicy.REPLAY_THEN_SYNC,
        host_surface_label=name,
        host_surface_ordered=True,
        host_surface_keyed=True,
        host_placement_profile_label=f"{name}Placement",
        host_allowed_child_kinds=(HostPlacementChildKind.WIDGET,),
        host_stable_slot_identity=True,
        host_separates_structure_from_placement=True,
    )


def _mount_spec_for_rotation(base_index: int, rotation_index: int) -> MountSpec:
    kind = _MOUNT_ROTATION[rotation_index % len(_MOUNT_ROTATION)]
    if kind == "Single":
        return _single_mount_spec(base_index)
    if kind == "Ordered":
        return _ordered_mount_spec(base_index)
    if kind == "Nested":
        return _nested_mount_spec(base_index)
    return _keyed_mount_spec(base_index)


def comprehensive_node_specs(
    *,
    shape: ComprehensiveBackendShape = ComprehensiveBackendShape(),
) -> tuple[NodeGenSpec, ...]:
    scalar_params = _scalar_params(shape)
    specs: list[NodeGenSpec] = [
        NodeGenSpec(
            name=_ROOT,
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")), *scalar_params),
        )
    ]

    rotation_index = 0
    for base_index in range(shape.base_type_count):
        base_name = _base_name(base_index)
        specs.append(
            NodeGenSpec(
                name=base_name,
                base_name=_ROOT,
                constructor=(ParamSpec(name="name", annotation=TypeRef("str")), *scalar_params),
            )
        )

        for leaf_index in range(shape.leaves_per_base):
            specs.append(
                NodeGenSpec(
                    name=_leaf_name(base_index, leaf_index),
                    base_name=base_name,
                    host_child_kind=HostPlacementChildKind.WIDGET,
                    constructor=(
                        ParamSpec(name="name", annotation=TypeRef("str")),
                        ParamSpec(name="label", annotation=TypeRef("str")),
                        *scalar_params,
                    ),
                )
            )

        for bin_index in range(shape.bins_per_base):
            specs.append(
                NodeGenSpec(
                    name=_bin_name(base_index, bin_index),
                    base_name=base_name,
                    host_child_kind=HostPlacementChildKind.NESTED_CONTAINER,
                    constructor=(ParamSpec(name="name", annotation=TypeRef("str")), *scalar_params),
                    mounts=(_mount_spec_for_rotation(base_index, rotation_index),),
                )
            )
            rotation_index += 1

    return tuple(specs)


def build_comprehensive_backend(
    *,
    module_name: str = "example.generic_backend.comprehensive",
    shape: ComprehensiveBackendShape = ComprehensiveBackendShape(),
) -> BuildPyroNodeBackend:
    return BuildPyroNodeBackend(comprehensive_node_specs(shape=shape), module_name=module_name)


def allowed_child_type_names_for_mount(
    mount_name: str,
    *,
    shape: ComprehensiveBackendShape = ComprehensiveBackendShape(),
) -> tuple[str, ...]:
    specs = comprehensive_node_specs(shape=shape)
    by_name = {spec.name: spec for spec in specs}
    mount = next((mount for spec in specs for mount in spec.mounts if mount.name == mount_name), None)
    if mount is None:
        raise KeyError(f"unknown mount {mount_name!r}")

    accepted_names: list[str] = []
    accepted_kind = mount.accepted_kind
    accepted_base = mount.accepted_base
    allowed_child_kinds = mount.host_allowed_child_kinds

    def is_descendant_of(name: str, base_name: str) -> bool:
        current = by_name.get(name)
        while current is not None and current.base_name is not None:
            if current.base_name == base_name:
                return True
            current = by_name.get(current.base_name)
        return False

    for spec in specs:
        if spec.name == _ROOT:
            continue
        if accepted_kind is not None and spec.name != accepted_kind:
            continue
        if accepted_base is not None and spec.name != accepted_base and not is_descendant_of(spec.name, accepted_base):
            continue
        if allowed_child_kinds:
            host_kind = spec.host_child_kind
            if host_kind is None:
                host_kind = (
                    HostPlacementChildKind.WIDGET
                    if _is_leaf_name(spec.name)
                    else HostPlacementChildKind.NESTED_CONTAINER
                    if _is_bin_name(spec.name)
                    else None
                )
            if host_kind not in allowed_child_kinds:
                continue
        accepted_names.append(spec.name)

    return tuple(accepted_names)


def selector_family_names(
    *,
    shape: ComprehensiveBackendShape = ComprehensiveBackendShape(),
) -> tuple[str, ...]:
    backend = build_comprehensive_backend(
        module_name="example.generic_backend.comprehensive_names",
        shape=shape,
    )
    return tuple(sorted(backend._selector_families))


def mount_profile_names(
    *,
    shape: ComprehensiveBackendShape = ComprehensiveBackendShape(),
) -> tuple[str, ...]:
    return selector_family_names(shape=shape)


__all__ = [
    "ComprehensiveBackendShape",
    "allowed_child_type_names_for_mount",
    "build_comprehensive_backend",
    "comprehensive_node_specs",
    "mount_profile_names",
    "selector_family_names",
]
