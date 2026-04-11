from __future__ import annotations

from typing import Any

from pyrolyze.runtime.slot_kinds import ContextKind
from ._base import StateMgrBase, unavailable


class SlotContextStateMgr(StateMgrBase):
    def __init__(
        self,
        owner: Any,
        *,
        render_context_state_mgr: Any,
        parent_state_mgr: Any,
        slot_id: Any,
        invoke_dirty: bool,
        seen_in_pass: bool,
    ) -> None:
        super().__init__(owner, render_context_state_mgr=render_context_state_mgr)
        self._render_context_state_mgr = render_context_state_mgr
        self._parent_state_mgr = parent_state_mgr
        self._slot_id = slot_id
        self._invoke_dirty = invoke_dirty
        self._seen_in_pass = seen_in_pass
        self._site_metadata: tuple[Any, ...] = ()
        self._context_kind = type(owner)._context_kind
        self.attach_to_graph()

    def attach_to_graph(self) -> None:
        self._render_context_state_mgr.register_slot_state_mgr(self)
        self._parent_state_mgr.register_child_state_mgr(self._slot_id, self)

    def current_slot_id(self) -> Any:
        return self._slot_id

    def current_generation_id(self) -> int:
        return self._render_context_state_mgr.current_generation_id()

    def context_kind(self) -> ContextKind:
        return self._context_kind

    def visit_self_and_dirty(self) -> bool:
        self.require_active_scope()
        return self._invoke_dirty

    def deactivate(self) -> None:
        for child_state_mgr in list(self.children_by_slot_id().values()):
            child_state_mgr.deactivate()
        self.children_by_slot_id().clear()

        self._render_context_state_mgr.unregister_slot(self._slot_id)
        parent_children = self._parent_state_mgr.children_by_slot_id()
        if parent_children.get(self._slot_id) is self:
            parent_children.pop(self._slot_id, None)
