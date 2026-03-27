"""Mutable builder helpers for generic backend snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from frozendict import frozendict

from .model import (
    PyroArgs,
    PyroHostSurface,
    PyroHostSurfaceEntry,
    PyroHostSurfaceOperation,
    PyroMountBucket,
    PyroMountEntry,
    PyroMountOperation,
    PyroNode,
)


@dataclass(slots=True)
class PyroMountEntryBuilder:
    placement_id: object
    node: PyroNode

    @classmethod
    def from_entry(cls, entry: PyroMountEntry) -> PyroMountEntryBuilder:
        return cls(placement_id=entry.placement_id, node=entry.node)

    def build(self) -> PyroMountEntry:
        return PyroMountEntry(placement_id=self.placement_id, node=self.node)


@dataclass(slots=True)
class PyroMountBucketBuilder:
    key: PyroArgs
    values: PyroArgs
    entries: list[PyroMountEntryBuilder] = field(default_factory=list)

    @classmethod
    def from_bucket(cls, bucket: PyroMountBucket) -> PyroMountBucketBuilder:
        return cls(
            key=bucket.key,
            values=bucket.values,
            entries=[PyroMountEntryBuilder.from_entry(entry) for entry in bucket.entries],
        )

    def build(self) -> PyroMountBucket:
        return PyroMountBucket(
            key=self.key,
            values=self.values,
            entries=tuple(entry.build() for entry in self.entries),
        )


@dataclass(slots=True)
class PyroHostSurfaceEntryBuilder:
    placement_handle: object
    child_kind: object
    node: PyroNode

    @classmethod
    def from_entry(cls, entry: PyroHostSurfaceEntry) -> PyroHostSurfaceEntryBuilder:
        return cls(
            placement_handle=entry.placement_handle,
            child_kind=entry.child_kind,
            node=entry.node,
        )

    def build(self) -> PyroHostSurfaceEntry:
        return PyroHostSurfaceEntry(
            placement_handle=self.placement_handle,
            child_kind=self.child_kind,
            node=self.node,
        )


@dataclass(slots=True)
class PyroHostSurfaceBuilder:
    surface_name: str
    entries: list[PyroHostSurfaceEntryBuilder] = field(default_factory=list)

    @classmethod
    def from_surface(cls, surface: PyroHostSurface) -> PyroHostSurfaceBuilder:
        return cls(
            surface_name=surface.surface_name,
            entries=[PyroHostSurfaceEntryBuilder.from_entry(entry) for entry in surface.entries],
        )

    def build(self) -> PyroHostSurface:
        return PyroHostSurface(
            surface_name=self.surface_name,
            entries=tuple(entry.build() for entry in self.entries),
        )


@dataclass(slots=True)
class PyroNodeBuilder:
    node_type: str
    generation: int
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    mounts: dict[object, list[PyroMountBucketBuilder]] = field(default_factory=dict)
    mount_metadata: dict[object, dict[str, Any]] = field(default_factory=dict)
    mount_operations: list[PyroMountOperation] = field(default_factory=list)
    host_surfaces: dict[object, PyroHostSurfaceBuilder] = field(default_factory=dict)
    host_surface_metadata: dict[object, dict[str, Any]] = field(default_factory=dict)
    host_surface_operations: list[PyroHostSurfaceOperation] = field(default_factory=list)

    @classmethod
    def from_node(cls, node: PyroNode) -> PyroNodeBuilder:
        return cls(
            node_type=node.node_type,
            generation=node.generation,
            args=list(node.args),
            kwargs=dict(node.kwargs),
            mounts={
                mount_name: [PyroMountBucketBuilder.from_bucket(bucket) for bucket in buckets]
                for mount_name, buckets in node.mounts.items()
            },
            mount_metadata={mount_name: dict(metadata) for mount_name, metadata in node.mount_metadata.items()},
            mount_operations=list(node.mount_operations),
            host_surfaces={
                surface_name: PyroHostSurfaceBuilder.from_surface(surface)
                for surface_name, surface in node.host_surfaces.items()
            },
            host_surface_metadata={
                surface_name: dict(metadata)
                for surface_name, metadata in node.host_surface_metadata.items()
            },
            host_surface_operations=list(node.host_surface_operations),
        )

    def build(self) -> PyroNode:
        return PyroNode(
            node_type=self.node_type,
            generation=self.generation,
            args=tuple(self.args),
            kwargs=frozendict(self.kwargs),
            mounts=frozendict(
                {
                    mount_name: tuple(bucket.build() for bucket in buckets)
                    for mount_name, buckets in self.mounts.items()
                }
            ),
            mount_metadata=frozendict(
                {
                    mount_name: frozendict(metadata)
                    for mount_name, metadata in self.mount_metadata.items()
                }
            ),
            mount_operations=tuple(self.mount_operations),
            host_surfaces=frozendict(
                {
                    surface_name: surface.build()
                    for surface_name, surface in self.host_surfaces.items()
                }
            ),
            host_surface_metadata=frozendict(
                {
                    surface_name: frozendict(metadata)
                    for surface_name, metadata in self.host_surface_metadata.items()
                }
            ),
            host_surface_operations=tuple(self.host_surface_operations),
        )


__all__ = [
    "PyroHostSurfaceBuilder",
    "PyroHostSurfaceEntryBuilder",
    "PyroMountBucketBuilder",
    "PyroMountEntryBuilder",
    "PyroNodeBuilder",
]
