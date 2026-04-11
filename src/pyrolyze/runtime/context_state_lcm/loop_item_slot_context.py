from __future__ import annotations

from typing import Any

from .rerunnable_slot_context import RerunnableSlotContextStateMgr
from ._support import _SlotCallResult, _structured_dirty_projection


class LoopItemSlotContextStateMgr(RerunnableSlotContextStateMgr):
    def __init__(self, owner: object, **kwargs: object) -> None:
        super().__init__(owner, **kwargs)
        self._current_value = None
        self._current_dirty = True
        self._current_initialized = False

    def current_value(self) -> Any:
        self.require_active_scope()
        return _SlotCallResult(
            dirty=self._current_dirty,
            value=self._current_value,
        )

    def update_current(self, value: Any) -> None:
        self._current_dirty = _structured_dirty_projection(
            previous=self._current_value,
            current=value,
            initialized=self._current_initialized,
        )
        self._current_value = value
        self._current_initialized = True
