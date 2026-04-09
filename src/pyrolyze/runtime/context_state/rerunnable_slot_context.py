from __future__ import annotations

from .context_base import ContextBaseStateMgr
from .slot_context import SlotContextStateMgr


class RerunnableSlotContextStateMgr(SlotContextStateMgr, ContextBaseStateMgr):
    def __post_init__(self) -> None:
        self._render_context = self.owner.render_context
        self._children = {}
        self._literal_initialized = []
        self._literal_index = 0
        self._scope_active = False
        self._pass_child_order = ()
        self._pass_child_dirty = {}
        self._committed_ui = ()
        self._own_committed_ui = ()
        self._own_committed_ui_entries = ()
        self._pass_committed_ui = ()
        self._pass_own_committed_ui = ()
        self._pass_own_committed_ui_entries = ()
        self._staged_ui = []
        self._staged_ui_entries = []
