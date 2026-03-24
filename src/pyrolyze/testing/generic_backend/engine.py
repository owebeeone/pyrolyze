"""Thin MountableEngine wrapper for the generic testing backend."""

from __future__ import annotations

from typing import Any, Mapping

from frozendict import frozendict

from pyrolyze.backends.model import (
    ChildPolicy,
    MountParamSpec,
    MountPointSpec,
    TypeRef,
    UiWidgetSpec as UiMountableSpec,
)
from pyrolyze.backends.mountable_engine import MountableEngine, MountedMountableNode

from .model import PyroNode
from .runtime import (
    GeneratedPyroMountable,
    build_runtime_types,
    generic_backend_runtime_context,
)
from .specs import MountInterfaceKind, MountSpec, NodeGenSpec, validate_node_specs


class PyroNodeEngine(MountableEngine):
    def __init__(
        self,
        node_specs: tuple[NodeGenSpec, ...] | list[NodeGenSpec],
        *,
        initial_generation: int = 0,
        strict_compatibility: bool = True,
    ) -> None:
        self._node_specs = validate_node_specs(node_specs)
        self._runtime_types = build_runtime_types(self._node_specs)
        self._current_generation = initial_generation
        self._strict_compatibility = strict_compatibility
        super().__init__(_build_node_specs(self._node_specs))

    @property
    def current_generation(self) -> int:
        return self._current_generation

    def mount(
        self,
        element: Any,
        *,
        slot_id: Any | None = None,
        call_site_id: int | str | None = None,
        generation: int | None = None,
    ) -> MountedMountableNode:
        if generation is not None:
            self._current_generation = generation
        with generic_backend_runtime_context(
            generation=self._current_generation,
            strict_compatibility=self._strict_compatibility,
        ):
            return super().mount(element, slot_id=slot_id, call_site_id=call_site_id)

    def update(
        self,
        node: MountedMountableNode,
        element: Any,
        *,
        slot_id: Any | None = None,
        call_site_id: int | str | None = None,
        generation: int | None = None,
    ) -> MountedMountableNode:
        if generation is not None:
            self._current_generation = generation
        with generic_backend_runtime_context(
            generation=self._current_generation,
            strict_compatibility=self._strict_compatibility,
        ):
            return super().update(
                node,
                element,
                slot_id=slot_id,
                call_site_id=call_site_id,
            )

    def snapshot(self, node: MountedMountableNode) -> PyroNode:
        mountable = node.mountable
        if not isinstance(mountable, GeneratedPyroMountable):
            raise TypeError(f"expected GeneratedPyroMountable, got {type(mountable)!r}")
        return mountable.to_pyro_node()

    def _mountable_type_for(self, spec: UiMountableSpec) -> type[object]:
        return self._runtime_types[spec.kind]


def _build_node_specs(
    node_specs: tuple[NodeGenSpec, ...],
) -> Mapping[str, UiMountableSpec]:
    spec_map = {spec.name: spec for spec in node_specs}
    return frozendict({spec.name: _build_node_spec(spec, spec_map) for spec in node_specs})


def _build_node_spec(
    spec: NodeGenSpec,
    spec_map: Mapping[str, NodeGenSpec],
) -> UiMountableSpec:
    mount_points = frozendict({mount.name: _build_mount_point(mount, spec_map) for mount in spec.mounts})
    default_mount = next((mount.name for mount in spec.mounts if mount.default), None)
    child_policy = _child_policy_for(spec.mounts)
    return UiMountableSpec(
        kind=spec.name,
        mounted_type_name=spec.name,
        constructor_params=frozendict(
            {
                param.name: _build_constructor_param(param)
                for param in spec.constructor
            }
        ),
        props=frozendict(),
        methods=frozendict(),
        child_policy=child_policy,
        mount_points=mount_points,
        default_child_mount_point_name=default_mount,
        default_attach_mount_point_names=(() if default_mount is None else (default_mount,)),
    )


def _build_constructor_param(param: Any) -> Any:
    from pyrolyze.backends.model import UiParamSpec

    return UiParamSpec(
        name=param.name,
        annotation=param.annotation,
        default_repr=param.default_repr,
    )


def _build_mount_point(
    mount: MountSpec,
    spec_map: Mapping[str, NodeGenSpec],
) -> MountPointSpec:
    params = tuple(
        MountParamSpec(
            name=param.name,
            annotation=param.annotation,
            keyed=param.keyed,
            default_repr=param.default_repr,
        )
        for param in mount.params
    )
    accepted_expr = _accepted_expr_for_mount(mount, spec_map)
    if accepted_expr is None:
        raise ValueError(f"mount {mount.name!r} is missing an accepted type")
    if mount.interface is MountInterfaceKind.ORDERED:
        return MountPointSpec(
            name=mount.name,
            accepted_produced_type=TypeRef(accepted_expr),
            params=params,
            max_children=None,
            sync_method_name=f"sync_{_pluralize(mount.name)}",
            place_method_name=f"insert_{mount.name}",
            append_method_name=f"add_{mount.name}",
            detach_method_name=f"detach_{mount.name}",
        )
    return MountPointSpec(
        name=mount.name,
        accepted_produced_type=TypeRef(accepted_expr),
        params=params,
        max_children=1,
        apply_method_name=f"set_{mount.name}",
    )


def _child_policy_for(mounts: tuple[MountSpec, ...]) -> ChildPolicy:
    if not mounts:
        return ChildPolicy.NONE
    if any(mount.interface is MountInterfaceKind.ORDERED for mount in mounts):
        return ChildPolicy.ORDERED
    return ChildPolicy.SINGLE


def _pluralize(name: str) -> str:
    if name.endswith("s"):
        return name
    return f"{name}s"


def _accepted_expr_for_mount(
    mount: MountSpec,
    spec_map: Mapping[str, NodeGenSpec],
) -> str | None:
    if mount.accepted_base is not None:
        return mount.accepted_base
    if mount.accepted_kind is None:
        return None
    accepted_spec = spec_map[mount.accepted_kind]
    if accepted_spec.base_name is not None:
        return accepted_spec.base_name
    return mount.accepted_kind


__all__ = ["PyroNodeEngine"]
