from __future__ import annotations

from .context_base import ContextBaseStateMgr
from .slot_context import SlotContextStateMgr


class RerunnableSlotContextStateMgr(SlotContextStateMgr, ContextBaseStateMgr):
    pass
