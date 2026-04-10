from __future__ import annotations

from typing import Any

from pyrolyze.lifecycle import const, managed_context


def unavailable() -> None:
    raise NotImplementedError("context_bare_refactor state manager scaffold")


@managed_context
class StateMgrBase:
    owner: Any = const()
