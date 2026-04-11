from __future__ import annotations

from .context_base import ContextBaseStateMgr
from .slot_context import SlotContextStateMgr


class RerunnableSlotContextStateMgr(SlotContextStateMgr, ContextBaseStateMgr):
    def __init__(self, owner: object, **kwargs: object) -> None:
        super().__init__(
            owner,
            pass_scope_handle_cls=type(owner)._pass_scope_handle_cls,
            **kwargs,
        )
