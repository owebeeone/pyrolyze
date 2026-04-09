from __future__ import annotations

from typing import Any

from .context_base import _context_kind
from ._base import StateMgrBase, unavailable


class SlotContextStateMgr(StateMgrBase):
    def current_slot_id(self) -> Any:
        return self.owner.slot_id

    def current_generation_id(self) -> int:
        return self.owner.render_context.current_generation_id()

    def context_kind(self) -> str:
        return _context_kind(self.owner)

    def visit_self_and_dirty(self) -> bool:
        owner = self.owner
        if not hasattr(owner, "_require_active_scope"):
            raise RuntimeError("slot is not a structural context")
        owner._require_active_scope()
        return owner.invoke_dirty

    def deactivate(self) -> None:
        owner = self.owner
        if hasattr(owner, "_children"):
            for child in list(owner._children.values()):
                child.deactivate()
            owner._children.clear()

        owner.render_context._slots_by_id.pop(owner.slot_id, None)
        if owner.parent._children.get(owner.slot_id) is owner:
            owner.parent._children.pop(owner.slot_id, None)
