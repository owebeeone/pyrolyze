"""App-scoped context storage for runtime helpers and test tooling."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar, cast


T = TypeVar("T")
_APP_CONTEXT_MISSING = object()


@dataclass(frozen=True, slots=True, eq=False)
class AppContextKey(Generic[T]):
    debug_name: str
    factory: Callable[[object | None], T]
    close: Callable[[T], None] | None = field(default=None, compare=False, hash=False)


@dataclass(slots=True)
class AppContextStore:
    host_app: object | None = None
    _values: dict[AppContextKey[Any], object] = field(default_factory=dict, init=False)
    _creation_order: list[AppContextKey[Any]] = field(default_factory=list, init=False)
    _closed: bool = field(default=False, init=False)

    def get(self, key: AppContextKey[T]) -> T:
        if self._closed:
            raise RuntimeError("app context store is closed")
        existing = self._values.get(key, _APP_CONTEXT_MISSING)
        if existing is not _APP_CONTEXT_MISSING:
            return cast(T, existing)
        created = key.factory(self.host_app)
        self._values[key] = created
        self._creation_order.append(key)
        return created

    def has(self, key: AppContextKey[Any]) -> bool:
        return key in self._values

    def close_all(self) -> None:
        if self._closed:
            return
        self._closed = True
        for key in reversed(self._creation_order):
            close = key.close
            if close is None:
                continue
            close(cast(Any, self._values[key]))


@dataclass(slots=True)
class GenerationTracker:
    committed_generation_id: int = 0
    active_generation_id: int | None = None

    def begin(self) -> int:
        if self.active_generation_id is None:
            self.active_generation_id = self.committed_generation_id + 1
        return self.active_generation_id

    def commit(self) -> int:
        active = self.active_generation_id
        if active is None:
            return self.committed_generation_id
        self.committed_generation_id = active
        self.active_generation_id = None
        return self.committed_generation_id

    def rollback(self) -> int:
        self.active_generation_id = None
        return self.committed_generation_id

    def current(self) -> int:
        active = self.active_generation_id
        if active is not None:
            return active
        return self.committed_generation_id


GENERATION_TRACKER_KEY = AppContextKey(
    "pyrolyze.generation",
    factory=lambda _host_app: GenerationTracker(),
)


__all__ = [
    "AppContextKey",
    "AppContextStore",
    "GENERATION_TRACKER_KEY",
    "GenerationTracker",
]
