"""Expression advertisements are candidate data, not external resources.

The borrowed collection and its managed UI anchors publish together. Surface
validation includes ordinary slot calls and expression calls before publication;
scoped keys prevent separate expression collections from overwriting each other.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pyrolyze.api import PyrolyzeMountAdvertisement
from pyrolyze.runtime.slot_call_semantics import (
    ExternalStoreHandler,
    PyrolyzeMountAdvertisementHandler,
    SlotCallSemanticsHandler,
    SlotValueHandler,
    UseEffectAsyncHandler,
    UseEffectHandler,
)
from pyrolyze.runtime.slot_identity import SlotIdPath
from .async_effect_expr_render import (
    _AsyncEffectExprRenderCompletion,
    _enable_async_effect_expr_render,
)
from .callback_render import _graph_states
from .mount_binding import _MountAdvertisementBinding
from .render_context import RenderContextStateMgr
from .slot_expr_slot_context import SlotExprSlotContextStateMgr
from .subscription_expr_render import _SubscriptionExpressionExecution


@dataclass(eq=False, slots=True)
class _MountExpressionExecution(_SubscriptionExpressionExecution):
    def finish_evaluation(self) -> None:
        super(_MountExpressionExecution, self).finish_evaluation()
        collection = self.state._call_site_context_manager._pass_context.contexts
        anchors = tuple(
            context.binding.binding.advertisement
            for context in collection.contexts.values()
            if context.binding is not None
            and type(context.binding.binding) is _MountAdvertisementBinding
        )
        self.require_active()
        self.state.own_ui_state = anchors
        self.require_active()


def _enable_mount_expr_render(root: RenderContextStateMgr) -> None:
    _enable_async_effect_expr_render(root)
    root._field_only_completion = _MountExprRenderCompletion(root)


@dataclass(eq=False, slots=True)
class _MountExprRenderCompletion(_AsyncEffectExprRenderCompletion):
    def require_expression_handler(self, handler: SlotCallSemanticsHandler) -> None:
        if type(handler) not in (
            SlotValueHandler,
            ExternalStoreHandler,
            UseEffectHandler,
            UseEffectAsyncHandler,
            PyrolyzeMountAdvertisementHandler,
        ):
            self.reject("resource expression results are not admitted")

    def expression_execution(
        self, state: SlotExprSlotContextStateMgr
    ) -> _MountExpressionExecution:
        execution = super(_MountExprRenderCompletion, self).expression_execution(state)
        return _MountExpressionExecution(self, state, execution.owner)

    def _advertisements_for(
        self, render: RenderContextStateMgr, *, current: bool
    ) -> dict[Any, PyrolyzeMountAdvertisement]:
        entries = super(_MountExprRenderCompletion, self)._advertisements_for(
            render, current=current
        )
        for state in _graph_states(render, current=current, render_local=True):
            if (
                not isinstance(state, SlotExprSlotContextStateMgr)
                or state._render_context_state_mgr is not render
            ):
                continue
            context = state._call_site_context_manager._pass_context
            collection = context.current.contexts if current else context.contexts
            for slot_id, call_site in collection.contexts.items():
                wrapped = call_site.binding
                if (
                    wrapped is not None
                    and type(wrapped.binding) is _MountAdvertisementBinding
                ):
                    entries[SlotIdPath((state.current_slot_id(), slot_id))] = (
                        wrapped.binding.advertisement
                    )
        return entries
