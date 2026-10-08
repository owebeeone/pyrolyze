"""Private plain-value slot-call admission; external resource routes stay gated."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from yidl_lifecycle.bindings import BindingBase

from .callback_render import _CallbackRenderCompletion, _enable_callback_render
from .render_context import RenderContextStateMgr
from pyrolyze.runtime.slot_call_semantics import (
    SlotValueHandler,
    SlotValueBinding,
    SlotCallBinding,
    SlotCallSemanticsHandler,
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

    def require_slot_call_result(self, result: Any) -> SlotCallSemanticsHandler:
        handler = select_slot_call_handler(result)
        if type(handler) is not SlotValueHandler:
            self.reject("external resource slot-call result is not admitted")
        return handler

    def bind_slot_call_result(
        self,
        handler: SlotCallSemanticsHandler,
        host: Any,
        result: Any,
        previous: SlotCallBinding | None,
    ) -> SlotCallBinding:
        detached = (
            SlotValueBinding(previous.exposed_value())
            if type(previous) is SlotValueBinding
            else None
        )
        return handler.bind(host, result, detached)

    def refresh_slot_call_selection(
        self,
        binding: SlotCallBinding,
    ) -> tuple[SlotCallBinding, bool] | None:
        return None

    def resource_owner_for(
        self, binding: SlotCallBinding, previous: BindingBase | None
    ) -> BindingBase | None:
        return None

    def discard_unstaged_selection(self, binding: SlotCallBinding, state: Any) -> None:
        pass
