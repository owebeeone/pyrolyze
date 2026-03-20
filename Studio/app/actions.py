from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommandAction:
    command_id: str


@dataclass(frozen=True, slots=True)
class ExplorerSelectAction:
    path: str
    is_dir: bool


@dataclass(frozen=True, slots=True)
class SetRootAction:
    path: str
