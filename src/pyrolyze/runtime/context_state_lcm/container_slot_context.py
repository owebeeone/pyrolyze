from __future__ import annotations

from .rerunnable_slot_context import RerunnableSlotContextStateMgr


class ContainerSlotContextStateMgr(RerunnableSlotContextStateMgr):
    def __init__(self, owner: object, **kwargs: object) -> None:
        super().__init__(owner=owner, **kwargs)
        self._expects_native_root = False
        self._committed_native_root = False
