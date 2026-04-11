from __future__ import annotations

import os
from typing import Any, Callable

from .slot_context import SlotContextStateMgr
from ._base import unavailable


class EventHandlerSlotContextStateMgr(SlotContextStateMgr):
    def __init__(self, owner: Any, **kwargs: Any) -> None:
        super().__init__(owner, **kwargs)
        self._committed_callback: Callable[..., Any] | None = None
        self._committed_key: object | None = None
        self._staged_callback: Callable[..., Any] | None = None
        self._staged_key: object | None = None
        self._dispatch: Callable[..., None] | None = None

    def stage_callback(self, *, callback: Callable[..., Any], dirty: bool) -> Callable[..., None]:
        callback_key = callback
        if dirty or self._committed_callback is None or self._committed_key != callback_key:
            self._staged_callback = callback
            self._staged_key = callback_key
        return self._dispatch_callable()

    def commit_handler(self) -> None:
        if self._staged_callback is None:
            return
        self._committed_callback = self._staged_callback
        self._committed_key = self._staged_key
        self._staged_callback = None
        self._staged_key = None

    def rollback_handler(self) -> None:
        self._staged_callback = None
        self._staged_key = None

    def deactivate(self) -> None:
        self._staged_callback = None
        self._staged_key = None
        self._committed_callback = None
        self._committed_key = None
        super().deactivate()

    def _dispatch_callable(self) -> Callable[..., None]:
        if self._dispatch is None:

            def dispatch(*args: Any, **kwargs: Any) -> None:
                callback = self._committed_callback
                if callback is None:
                    if os.environ.get("PYROLYZE_ENV") == "prod":
                        return
                    raise RuntimeError("event handler is inactive")
                callback(*args, **kwargs)

            self._dispatch = dispatch
        return self._dispatch
