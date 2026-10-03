from __future__ import annotations

from contextlib import nullcontext
from typing import Any, Self

from pyrolyze.runtime.slot_kinds import ContextKind
from ._base import StateMgrBase
from .context_base import ContextBaseStateMgr


class SlotContextStateMgr(StateMgrBase):
    @classmethod
    def create(cls, owner: Any, **kwargs: Any) -> Self:
        state = super().create(owner=owner, **kwargs)
        state.attach_to_graph()
        return state

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

    def _deactivate_write_scope(self) -> Any:
        if isinstance(self, ContextBaseStateMgr):
            return self.publish_write_scope()
        render_context_state_mgr = getattr(self, "_render_context_state_mgr", None)
        if render_context_state_mgr is not None and hasattr(render_context_state_mgr, "publish_write_scope"):
            return render_context_state_mgr.publish_write_scope()
        return nullcontext()

    def deactivate(self) -> None:
        with self._deactivate_write_scope():
            for child_state_mgr in list(self.children_by_slot_id().values()):
                child_state_mgr.deactivate()
            self.children_state = {}

            self._render_context_state_mgr.unregister_slot(self._slot_id)
            parent_children = dict(self._parent_state_mgr.children_by_slot_id())
            if parent_children.get(self._slot_id) is self:
                parent_children.pop(self._slot_id, None)
                self._parent_state_mgr.children_state = parent_children
