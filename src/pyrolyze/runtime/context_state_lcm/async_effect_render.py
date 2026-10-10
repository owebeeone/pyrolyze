"""Async-effect admission, sharing synchronous completion and ownership."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from yidl_lifecycle.bindings_refcount import BindingBase

from pyrolyze.runtime.slot_call_semantics import (
    ExternalStoreHandler,
    SlotCallBinding,
    SlotCallSemanticsHandler,
    SlotValueHandler,
    UseEffectAsyncHandler,
    UseEffectAsyncRequest,
    UseEffectHandler,
    select_slot_call_handler,
)
from .async_effect_binding import _AsyncEffectBinding
from .effect_render import _EffectDeliveryResource, _EffectRenderCompletion




@dataclass(eq=False, slots=True)
class _AsyncEffectRenderCompletion(_EffectRenderCompletion):
    def require_slot_call_result(self, result: Any) -> SlotCallSemanticsHandler:
        handler = select_slot_call_handler(result)
        if type(handler) not in (
            SlotValueHandler,
            ExternalStoreHandler,
            UseEffectHandler,
            UseEffectAsyncHandler,
        ):
            self.reject("external resource slot-call result is not admitted")
        return handler

    def bind_slot_call_result(
        self,
        handler: SlotCallSemanticsHandler,
        host: Any,
        result: Any,
        previous: SlotCallBinding | None,
    ) -> SlotCallBinding:
        if type(handler) is UseEffectAsyncHandler:
            return _AsyncEffectBinding.bind(
                self, host, cast(UseEffectAsyncRequest, result), previous
            )
        return super(_AsyncEffectRenderCompletion, self).bind_slot_call_result(
            handler, host, result, previous
        )

    def resource_for(self, binding: SlotCallBinding) -> BindingBase | None:
        if type(binding) is _AsyncEffectBinding:
            return binding.resource
        return super(_AsyncEffectRenderCompletion, self).resource_for(binding)

    def delivery_resource_for(
        self, binding: SlotCallBinding | None
    ) -> _EffectDeliveryResource | None:
        if type(binding) is _AsyncEffectBinding:
            return binding.resource
        return super(_AsyncEffectRenderCompletion, self).delivery_resource_for(binding)
