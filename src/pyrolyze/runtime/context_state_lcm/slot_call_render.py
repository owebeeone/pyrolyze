"""Private plain-value slot-call admission; external resource routes stay gated."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .callback_render import _CallbackRenderCompletion, _enable_callback_render
from .render_context import RenderContextStateMgr
from pyrolyze.runtime.slot_call_semantics import (
    SlotValueHandler,
    select_slot_call_handler,
)


def _enable_slot_call_render(root: RenderContextStateMgr) -> None:
    _enable_callback_render(root)
    root._field_only_completion = _SlotCallRenderCompletion(root)


@dataclass(eq=False, slots=True)
class _SlotCallRenderCompletion(_CallbackRenderCompletion):
    def require_slot_type(self, slot_type: type[Any]) -> None:
        from pyrolyze.runtime.context_bare_refactor_lcm import SlotCallSlotContext

        if slot_type is not SlotCallSlotContext:
            super(_SlotCallRenderCompletion, self).require_slot_type(slot_type)

    def require_slot_call_result(self, result: Any) -> SlotValueHandler:
        handler = select_slot_call_handler(result)
        if type(handler) is not SlotValueHandler:
            self.reject("external resource slot-call result is not admitted")
        return handler
