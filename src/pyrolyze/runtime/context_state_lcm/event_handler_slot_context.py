from __future__ import annotations

import os
from typing import Any, Callable

from .context_base import PASS_TX_KEY
from .field_only_render import _field_only_completion
from .lifecycle_adapter import local_store, managed, managed_context
from .slot_context import SlotContextStateMgr
from ._support import _BOUND_METHOD_SELF_MISSING


def _callback_key(callback: Callable[..., Any]) -> object:
    receiver = getattr(callback, "__self__", _BOUND_METHOD_SELF_MISSING)
    function = getattr(callback, "__func__", None)
    if receiver is not _BOUND_METHOD_SELF_MISSING and callable(function):
        return ("bound_method", id(receiver), function)
    return callback


@managed_context
class EventHandlerSlotContextStateMgr(SlotContextStateMgr):
    _callback: Callable[..., Any] | None = managed(
        default=None, init=False, compare="identity", tx_key=PASS_TX_KEY
    )
    _callback_key: object | None = managed(
        default=None, init=False, compare="identity", tx_key=PASS_TX_KEY
    )
    _dispatch: Callable[..., None] | None = local_store(default=None)

    def stage_callback(
        self, *, callback: Callable[..., Any], dirty: bool
    ) -> Callable[..., None]:
        completion = _field_only_completion(self)
        if completion is not None:
            if completion.active is None or completion._completing:
                completion.reject(
                    "callback selection requires an active render execution"
                )
            completion.active._require_open()
            completion.active._require_identity()
        elif self._transaction_manager.active_transaction_for(PASS_TX_KEY) is None:
            raise RuntimeError("scope is not active")
        callback_key = _callback_key(callback)
        current = self.current
        if dirty or current._callback is None or current._callback_key != callback_key:
            self._callback = callback
            self._callback_key = callback_key
        return self._dispatch_callable()

    def _stage_retirement(self) -> None:
        self._callback = None
        self._callback_key = None

    def deactivate(self) -> None:
        completion = _field_only_completion(self)
        if completion is not None:
            completion.require_retirement_allowed(self)
        with self._deactivate_write_scope():
            if completion is not None:
                assert completion.active is not None
                completion.active._require_identity()
            self._stage_retirement()
            parent = self._parent_state_mgr
            children = dict(parent.children_state)
            if children.get(self._slot_id) is self:
                children.pop(self._slot_id)
                parent.children_state = children
            if (
                completion is None
                and self._render_context_state_mgr._slots_by_id.get(self._slot_id)
                is self
            ):
                self._render_context_state_mgr.unregister_slot(self._slot_id)

    def _dispatch_callable(self) -> Callable[..., None]:
        if self._dispatch is None:

            def dispatch(*args: Any, **kwargs: Any) -> None:
                callback = self.current._callback
                if callback is None:
                    if os.environ.get("PYROLYZE_ENV") == "prod":
                        return
                    raise RuntimeError("event handler is inactive")
                callback(*args, **kwargs)

            self._dispatch = dispatch
        return self._dispatch
