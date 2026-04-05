from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ModuleId:
    canonical_name: str


@dataclass(slots=True)
class ModuleRegistry:
    _modules: dict[str, ModuleId] = field(default_factory=dict)

    def module_id(self, canonical_name: str) -> ModuleId:
        module_id = self._modules.get(canonical_name)
        if module_id is None:
            module_id = ModuleId(canonical_name=canonical_name)
            self._modules[canonical_name] = module_id
        return module_id


module_registry = ModuleRegistry()


@dataclass(frozen=True, slots=True)
class SlotId:
    module_id: ModuleId
    slot_index: int
    key_path: tuple[Any, ...] = ()
    line_no: int | None = field(default=None, compare=False, hash=False)
    is_top_level: bool = field(default=False, compare=False, hash=False)


@dataclass(frozen=True, slots=True)
class SlotIdPath:
    items: tuple[SlotId, ...] = ()

    @classmethod
    def empty(cls) -> "SlotIdPath":
        return cls(())

    def child(self, slot_id: SlotId | None) -> "SlotIdPath":
        if slot_id is None:
            return self
        return SlotIdPath((*self.items, slot_id))

    def as_key(self) -> tuple[SlotId, ...]:
        return self.items


__all__ = [
    "ModuleId",
    "ModuleRegistry",
    "SlotId",
    "SlotIdPath",
    "module_registry",
]
