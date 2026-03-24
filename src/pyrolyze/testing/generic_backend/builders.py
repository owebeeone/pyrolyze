"""Mutable builder helpers for generic backend snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from frozendict import frozendict

from .model import PyroArgs, PyroMountBucket, PyroMountEntry, PyroNode


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
class PyroNodeBuilder:
    node_type: str
    generation: int
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    mounts: dict[object, list[PyroMountBucketBuilder]] = field(default_factory=dict)

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
        )


__all__ = [
    "PyroMountBucketBuilder",
    "PyroMountEntryBuilder",
    "PyroNodeBuilder",
]
