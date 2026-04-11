from __future__ import annotations

from typing import Any

from pyrolyze.lifecycle import const, managed_context

USE_OWNER = object()
USE_FACTORY = object()


def unavailable() -> None:
    raise NotImplementedError("context_bare_refactor state manager scaffold")


@managed_context
class StateMgrBase:
    owner: Any = const()

    def _owner_facade(self) -> Any:
        return object.__getattribute__(self, "owner")

    def _resolve_owner_arg(self, value: Any) -> Any:
        return self._owner_facade() if value is USE_OWNER else value

    def children_by_slot_id(self) -> dict[Any, Any]:
        return {}

    def iter_children(self) -> tuple[Any, ...]:
        return tuple()

    def committed_ui(self) -> tuple[Any, ...]:
        return ()

    def own_committed_ui(self) -> tuple[Any, ...]:
        return ()

    def own_committed_ui_entries(self) -> tuple[Any, ...]:
        return ()

    def parent_context(self) -> Any | None:
        return None
