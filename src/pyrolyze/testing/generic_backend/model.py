"""Immutable snapshot types for the generic testing backend."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from frozendict import frozendict

from .specs import HostPlacementChildKind


@dataclass(frozen=True, slots=True)
class PyroArgs:
    args: tuple[Any, ...] = ()
    kwargs: frozendict[str, Any] = frozendict()


@dataclass(frozen=True, slots=True)
class PyroMountEntry:
    placement_id: object
    node: PyroNode


@dataclass(frozen=True, slots=True)
class PyroMountOperation:
    mount_name: str
    kind: str
    details: frozendict[str, Any] = frozendict()


@dataclass(frozen=True, slots=True)
class PyroHostSurfaceEntry:
    placement_handle: object
    child_kind: HostPlacementChildKind
    node: PyroNode


@dataclass(frozen=True, slots=True)
class PyroHostSurfaceOperation:
    surface_name: str
    kind: str
    details: frozendict[str, Any] = frozendict()


@dataclass(frozen=True, slots=True)
class PyroHostSurface:
    surface_name: str
    entries: tuple[PyroHostSurfaceEntry, ...] = ()


@dataclass(frozen=True, slots=True)
class PyroMountBucket:
    key: PyroArgs
    values: PyroArgs
    entries: tuple[PyroMountEntry, ...] = ()

    def to_builder(self) -> PyroMountBucketBuilder:
        from .builders import PyroMountBucketBuilder

        return PyroMountBucketBuilder.from_bucket(self)


@dataclass(frozen=True, slots=True)
class PyroNode:
    node_type: str
    generation: int
    args: tuple[Any, ...] = ()
    kwargs: frozendict[str, Any] = frozendict()
    mounts: frozendict[object, tuple[PyroMountBucket, ...]] = frozendict()
    mount_metadata: frozendict[object, frozendict[str, Any]] = frozendict()
    mount_operations: tuple[PyroMountOperation, ...] = field(default=(), compare=False)
    host_surfaces: frozendict[object, PyroHostSurface] = frozendict()
    host_surface_metadata: frozendict[object, frozendict[str, Any]] = frozendict()
    host_surface_operations: tuple[PyroHostSurfaceOperation, ...] = field(default=(), compare=False)

    def to_builder(self) -> PyroNodeBuilder:
        from .builders import PyroNodeBuilder

        return PyroNodeBuilder.from_node(self)


from .builders import PyroHostSurfaceBuilder, PyroMountBucketBuilder, PyroNodeBuilder  # noqa: E402

__all__ = [
    "PyroArgs",
    "PyroHostSurface",
    "PyroHostSurfaceBuilder",
    "PyroHostSurfaceEntry",
    "PyroHostSurfaceOperation",
    "PyroMountBucket",
    "PyroMountEntry",
    "PyroMountOperation",
    "PyroNode",
]
