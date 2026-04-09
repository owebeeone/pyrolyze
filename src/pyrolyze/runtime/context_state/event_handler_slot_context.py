from __future__ import annotations

import os
from typing import Any, Callable

from .slot_context import SlotContextStateMgr
from ._base import unavailable


class EventHandlerSlotContextStateMgr(SlotContextStateMgr):
    def stage_callback(self, *, callback: Callable[..., Any], dirty: bool) -> Callable[..., None]:
        callback_key = callback
        owner = self.owner
        if dirty or owner.committed_callback is None or owner.committed_key != callback_key:
            owner.staged_callback = callback
            owner.staged_key = callback_key
        return self._dispatch_callable()

    def commit_handler(self) -> None:
        owner = self.owner
        if owner.staged_callback is None:
            return
        owner.committed_callback = owner.staged_callback
        owner.committed_key = owner.staged_key
        owner.staged_callback = None
        owner.staged_key = None

    def rollback_handler(self) -> None:
        owner = self.owner
        owner.staged_callback = None
        owner.staged_key = None

    def deactivate(self) -> None:
        owner = self.owner
        owner.staged_callback = None
        owner.staged_key = None
        owner.committed_callback = None
        owner.committed_key = None
        super().deactivate()

    def _dispatch_callable(self) -> Callable[..., None]:
        owner = self.owner
        if owner.dispatch is None:

            def dispatch(*args: Any, **kwargs: Any) -> None:
                callback = owner.committed_callback
                if callback is None:
                    if os.environ.get("PYROLYZE_ENV") == "prod":
                        return
                    raise RuntimeError("event handler is inactive")
                callback(*args, **kwargs)

            owner.dispatch = dispatch
        return owner.dispatch
