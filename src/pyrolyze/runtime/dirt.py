from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _structural_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, tuple):
        return any(_structural_truthy(item) for item in value)
    if isinstance(value, list):
        return any(_structural_truthy(item) for item in value)
    if isinstance(value, dict):
        return any(_structural_truthy(item) for item in value.values())
    return bool(value)


def _clean_shape_like(value: Any) -> Any:
    if isinstance(value, tuple):
        return tuple(_clean_shape_like(item) for item in value)
    if isinstance(value, list):
        return [_clean_shape_like(item) for item in value]
    if isinstance(value, dict):
        return {key: _clean_shape_like(item) for key, item in value.items()}
    return False


class _DMBind:
    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        return True


@dataclass(frozen=True, slots=True)
class DM:
    bind: Any = field(default_factory=_DMBind)

    def lookup(self, name: str) -> Any:
        return getattr(self.bind, name, True)

    def is_dirty(self, dirty_value: Any) -> bool:
        return _structural_truthy(dirty_value)

    def clean_shape_like(self, value: Any) -> Any:
        return _clean_shape_like(value)
