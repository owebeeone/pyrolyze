"""DearPyGui runtime host protocol and test doubles (tag registry, staging, move_item)."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class DpgRuntimeHost(Protocol):
    """Subset of DearPyGui imperative operations owned by the backend host."""

    @property
    def staging_tag(self) -> int | str:
        """Hidden parent for items not yet attached under a real parent."""

    children_order: dict[int, list[int]]
    """Shadow of child ordering per parent (used by ``DpgContainerItem.place_child``)."""

    def allocate_tag(self, slot_id: Any | None = None) -> int | str:
        """Return a stable DearPyGui item tag (optionally keyed by PyRolyze ``slot_id``)."""

    def create_with_factory(
        self,
        factory_name: str,
        slot_id: Any | None = None,
        **kwargs: Any,
    ) -> int | str:
        """Create an item via ``add_*`` / ``draw_*`` ( DearPyGui ) or equivalent; return its tag."""

    def configure_item(self, item: int | str, **kwargs: Any) -> None:
        """Maps to ``dearpygui.configure_item``."""

    def set_value(self, item: int | str, value: Any) -> None:
        """Maps to ``dearpygui.set_value``."""

    def move_item(self, item: int | str, *, parent: int | str, before: int | str = 0) -> None:
        """Maps to ``dearpygui.move_item`` (``before=0`` appends)."""

    def delete_item(self, item: int | str) -> None:
        """Maps to ``dearpygui.delete_item``."""

    def get_config_value(self, item: int | str, key: str) -> Any:
        """Best-effort read-side shadow (tests; real host may query DearPyGui)."""

    def get_item_value(self, item: int | str) -> Any:
        """Shadow for ``get_value`` / internal value channel."""


_dpg_host_ctx: ContextVar[DpgRuntimeHost | None] = ContextVar("dpg_runtime_host", default=None)
_dpg_slot_ctx: ContextVar[Any | None] = ContextVar("dpg_slot_id", default=None)


def current_dpg_host() -> DpgRuntimeHost:
    host = _dpg_host_ctx.get()
    if host is None:
        msg = "No active DearPyGui runtime host (DpgMountableEngine.mount/update not entered?)"
        raise RuntimeError(msg)
    return host


def current_dpg_slot_id() -> Any | None:
    return _dpg_slot_ctx.get()


def dpg_host_token(host: DpgRuntimeHost | None):
    return _dpg_host_ctx.set(host)


def dpg_host_reset(token: Any) -> None:
    _dpg_host_ctx.reset(token)


def dpg_slot_token(slot_id: Any | None):
    return _dpg_slot_ctx.set(slot_id)


def dpg_slot_reset(token: Any) -> None:
    _dpg_slot_ctx.reset(token)


@dataclass
class RecordingDpgHost:
    """Records DearPyGui-like calls for adapter and mount tests."""

    staging_tag: int = 0
    _next_tag: int = 1
    operations: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    config_shadow: dict[int, dict[str, Any]] = field(default_factory=dict)
    value_shadow: dict[int, Any] = field(default_factory=dict)
    _tag_by_slot: dict[Any, int] = field(default_factory=dict)
    parent_of: dict[int, int] = field(default_factory=dict)
    children_order: dict[int, list[int]] = field(default_factory=dict)

    def allocate_tag(self, slot_id: Any | None = None) -> int:
        if slot_id is not None and slot_id in self._tag_by_slot:
            return self._tag_by_slot[slot_id]
        tag = self._next_tag
        self._next_tag += 1
        if slot_id is not None:
            self._tag_by_slot[slot_id] = tag
        self.children_order.setdefault(tag, [])
        return tag

    def create_with_factory(
        self,
        factory_name: str,
        slot_id: Any | None = None,
        **kwargs: Any,
    ) -> int:
        tag = self.allocate_tag(slot_id)
        rec = {"factory": factory_name, "tag": tag, **kwargs}
        self.operations.append(("create_with_factory", rec))
        bucket = self.config_shadow.setdefault(tag, {})
        bucket.update(kwargs)
        return tag

    def configure_item(self, item: int | str, **kwargs: Any) -> None:
        item_i = int(item) if isinstance(item, int) else item
        rec = {"item": item_i, **kwargs}
        self.operations.append(("configure_item", rec))
        bucket = self.config_shadow.setdefault(int(item_i), {})
        bucket.update(kwargs)

    def set_value(self, item: int | str, value: Any) -> None:
        item_i = int(item)
        self.operations.append(("set_value", {"item": item_i, "value": value}))
        self.value_shadow[item_i] = value

    def move_item(self, item: int | str, *, parent: int | str, before: int | str = 0) -> None:
        item_i = int(item)
        parent_i = int(parent)
        before_i = int(before) if before != 0 else 0
        self.operations.append(
            ("move_item", {"item": item_i, "parent": parent_i, "before": before_i})
        )
        old_parent = self.parent_of.get(item_i)
        if old_parent is not None:
            self.children_order[old_parent] = [c for c in self.children_order[old_parent] if c != item_i]
        self.parent_of[item_i] = parent_i
        order = [c for c in self.children_order.setdefault(parent_i, []) if c != item_i]
        if before_i == 0:
            order.append(item_i)
        else:
            idx = order.index(before_i) if before_i in order else len(order)
            order.insert(idx, item_i)
        self.children_order[parent_i] = order

    def delete_item(self, item: int | str) -> None:
        item_i = int(item)
        self.operations.append(("delete_item", {"item": item_i}))
        self.config_shadow.pop(item_i, None)
        self.value_shadow.pop(item_i, None)
        for sid, tag in list(self._tag_by_slot.items()):
            if tag == item_i:
                del self._tag_by_slot[sid]
        old = self.parent_of.pop(item_i, None)
        if old is not None:
            self.children_order[old] = [c for c in self.children_order[old] if c != item_i]

    def get_config_value(self, item: int | str, key: str) -> Any:
        return self.config_shadow.get(int(item), {}).get(key)

    def get_item_value(self, item: int | str) -> Any:
        return self.value_shadow.get(int(item))


__all__ = [
    "DpgRuntimeHost",
    "RecordingDpgHost",
    "current_dpg_host",
    "current_dpg_slot_id",
    "dpg_host_reset",
    "dpg_host_token",
    "dpg_slot_reset",
    "dpg_slot_token",
]
