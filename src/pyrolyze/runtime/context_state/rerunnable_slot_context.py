from __future__ import annotations

from .context_base import ContextBaseStateMgr
from .slot_context import SlotContextStateMgr


class RerunnableSlotContextStateMgr(SlotContextStateMgr, ContextBaseStateMgr):
    def __init__(self, owner: object, **kwargs: object) -> None:
        super().__init__(owner, **kwargs)
        self._children = {}
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
        self._pass_scope_handle_cls = type(owner)._pass_scope_handle_cls
