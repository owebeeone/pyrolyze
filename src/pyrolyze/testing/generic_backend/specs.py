"""Declarative spec model for the generic testing backend."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from pyrolyze.backends.model import TypeRef


class MountInterfaceKind(StrEnum):
    ORDERED = "ordered_mount"
    SINGLE = "single_mount"
    KEYED = "keyed_mount"


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
class MountSpec:
    name: str
    accepted_kind: str | None = None
    accepted_base: str | None = None
    interface: MountInterfaceKind = MountInterfaceKind.ORDERED
    params: tuple[MountParam, ...] = ()
    default: bool = False


@dataclass(frozen=True, slots=True)
class NodeGenSpec:
    name: str
    base_name: str | None = None
    constructor: tuple[ParamSpec, ...] = ()
    mounts: tuple[MountSpec, ...] = ()


def validate_node_specs(specs: tuple[NodeGenSpec, ...] | list[NodeGenSpec]) -> tuple[NodeGenSpec, ...]:
    validated = tuple(specs)
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


__all__ = [
    "MountInterfaceKind",
    "MountParam",
    "MountSpec",
    "NodeGenSpec",
    "ParamSpec",
    "validate_node_specs",
]
