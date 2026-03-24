"""Immutable snapshot types for the generic testing backend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from frozendict import frozendict


@dataclass(frozen=True, slots=True)
class PyroArgs:
    args: tuple[Any, ...] = ()
    kwargs: frozendict[str, Any] = frozendict()


@dataclass(frozen=True, slots=True)
class PyroMountEntry:
    placement_id: object
    node: PyroNode


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

    def to_builder(self) -> PyroNodeBuilder:
        from .builders import PyroNodeBuilder

        return PyroNodeBuilder.from_node(self)


from .builders import PyroMountBucketBuilder, PyroNodeBuilder  # noqa: E402

__all__ = [
    "PyroArgs",
    "PyroMountBucket",
    "PyroMountEntry",
    "PyroNode",
]
