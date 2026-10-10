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
        if completion is None:
            raise RuntimeError("render completion is not configured")
        if completion.active is None or completion._completing:
            completion.reject("callback selection requires an active render execution")
        with completion.attempt_scope():
            owner = completion.active
            assert owner is not None
            owner._require_open()
            owner._require_identity()
            callback_key = _callback_key(callback)
            current = self.current
            select = bool(
                dirty
                or self._callback is None
                or current._callback is None
                or current._callback_key != callback_key
            )
            # Callback properties/equality may execute user code and replace authority.
            if owner is not None:
                owner._require_open()
                owner._require_identity()
                if completion.active is not owner or completion._completing:
                    completion.reject("callback selection lost its render owner")
            if select:
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
