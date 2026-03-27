"""Seeded replay helpers for generic-backend mutation fuzzing."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Any, Mapping, Sequence

from frozendict import frozendict

from .model import PyroNode


@dataclass(frozen=True, slots=True)
class FuzzReplayStep:
    arguments: frozendict[str, Any]


@dataclass(frozen=True, slots=True)
class FuzzReplayRecord:
    seed: int
    steps: tuple[FuzzReplayStep, ...]


@dataclass(frozen=True, slots=True)
class HostSurfaceReplayState:
    structural_mounts: frozendict[str, tuple[str, ...]]
    host_surface_orders: frozendict[str, tuple[str, ...]]
    host_surface_kinds: frozendict[str, tuple[str, ...]]


def generate_argument_fuzz_replay(
    *,
    seed: int,
    step_count: int,
    argument_space: Mapping[str, Sequence[Any]],
) -> FuzzReplayRecord:
    random = Random(seed)
    if step_count <= 0:
        raise ValueError("step_count must be positive")
    if not argument_space:
        raise ValueError("argument_space must not be empty")

    steps: list[FuzzReplayStep] = []
    ordered_names = tuple(argument_space)
    for _ in range(step_count):
        arguments = {
            name: random.choice(tuple(argument_space[name]))
            for name in ordered_names
        }
        steps.append(FuzzReplayStep(arguments=frozendict(arguments)))
    return FuzzReplayRecord(seed=seed, steps=tuple(steps))


def capture_host_surface_replay_state(node: PyroNode) -> HostSurfaceReplayState:
    structural_mounts = frozendict(
        {
            str(mount_name): tuple(
                _entry_display_name(entry.node)
                for bucket in buckets
                for entry in bucket.entries
            )
            for mount_name, buckets in node.mounts.items()
        }
    )
    host_surface_orders = frozendict(
        {
            str(surface_name): tuple(_entry_display_name(entry.node) for entry in surface.entries)
            for surface_name, surface in node.host_surfaces.items()
        }
    )
    host_surface_kinds = frozendict(
        {
            str(surface_name): tuple(entry.child_kind.value for entry in surface.entries)
            for surface_name, surface in node.host_surfaces.items()
        }
    )
    return HostSurfaceReplayState(
        structural_mounts=structural_mounts,
        host_surface_orders=host_surface_orders,
        host_surface_kinds=host_surface_kinds,
    )


def _entry_display_name(node: PyroNode) -> str:
    if "name" in node.kwargs:
        return str(node.kwargs["name"])
    if "text" in node.kwargs:
        return str(node.kwargs["text"])
    return node.node_type


__all__ = [
    "FuzzReplayRecord",
    "HostSurfaceReplayState",
    "FuzzReplayStep",
    "capture_host_surface_replay_state",
    "generate_argument_fuzz_replay",
]
