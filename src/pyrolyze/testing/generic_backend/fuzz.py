"""Seeded replay helpers for generic-backend mutation fuzzing."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Any, Mapping, Sequence

from frozendict import frozendict


@dataclass(frozen=True, slots=True)
class FuzzReplayStep:
    arguments: frozendict[str, Any]


@dataclass(frozen=True, slots=True)
class FuzzReplayRecord:
    seed: int
    steps: tuple[FuzzReplayStep, ...]


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


__all__ = [
    "FuzzReplayRecord",
    "FuzzReplayStep",
    "generate_argument_fuzz_replay",
]
