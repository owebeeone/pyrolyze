from __future__ import annotations

from typing import Any

from .rerunnable_slot_context import RerunnableSlotContextStateMgr
from ._support import _SlotCallResult, _structured_dirty_projection


class LoopItemSlotContextStateMgr(RerunnableSlotContextStateMgr):
    def __init__(self, owner: object, **kwargs: object) -> None:
        super().__init__(owner, **kwargs)
        self.current = None
        self.current_dirty = True
        self.current_initialized = False

    def current_value(self) -> Any:
        self.require_active_scope()
        return _SlotCallResult(
            dirty=self.current_dirty,
            value=self.current,
        )

    def update_current(self, value: Any) -> None:
        self.current_dirty = _structured_dirty_projection(
            previous=self.current,
            current=value,
            initialized=self.current_initialized,
        )
        self.current = value
        self.current_initialized = True
