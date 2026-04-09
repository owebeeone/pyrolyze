from __future__ import annotations

from typing import Any


def unavailable() -> None:
    raise NotImplementedError("context_bare_refactor state manager scaffold")


class StateMgrBase:
    def __init__(self, owner: Any) -> None:
        self.owner = owner

