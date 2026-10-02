from __future__ import annotations

from typing import Any, Self

from .lifecycle_adapter import const, managed_context

USE_OWNER = object()
USE_FACTORY = object()


def unavailable() -> None:
    raise NotImplementedError("context_bare_refactor state manager scaffold")


@managed_context
class StateMgrBase:
    owner: Any = const()

    @classmethod
    def create(cls, owner: Any, **kwargs: Any) -> Self:
        """Construct through the runtime's boundary-resolution entry point."""
        return cls(owner=owner, **kwargs)

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
