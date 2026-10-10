"""Async expression admission reuses effect delivery and weak resource hosts."""

from __future__ import annotations

from dataclasses import dataclass

from pyrolyze.runtime.slot_call_semantics import (
    ExternalStoreHandler,
    SlotCallSemanticsHandler,
    SlotValueHandler,
    UseEffectAsyncHandler,
    UseEffectHandler,
)
from .effect_expr_render import _EffectExprRenderCompletion




@dataclass(eq=False, slots=True)
class _AsyncEffectExprRenderCompletion(_EffectExprRenderCompletion):
    def require_expression_handler(self, handler: SlotCallSemanticsHandler) -> None:
        if type(handler) not in (
            SlotValueHandler,
            ExternalStoreHandler,
            UseEffectHandler,
            UseEffectAsyncHandler,
        ):
            self.reject("resource expression results are not admitted")
