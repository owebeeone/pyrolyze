"""Subscription expression proof; effects and mount expressions stay excluded.

Each call-site binding owns a private wrapper around one explicit resource
reference. Collection retirement releases it even if a public snapshot survives.
The completion's opening reference is separate and drains through the existing
subscription completion path. Notification targets retain only weak graph links.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import weakref

from pyrolyze.runtime.slot_call_semantics import (
    ExternalStoreHandler,
    SlotCallBinding,
    SlotCallBindingHost,
    SlotCallSemanticsHandler,
    SlotValueHandler,
    UseEffectAsyncHandler,
    select_slot_call_handler,
)
from pyrolyze.runtime.slot_expr import _SlotExprCallSiteBinding
from .async_effect_binding import _AsyncEffectBinding
from .resource_ownership import _ResourceOwner
from .render_attempt import _raise_with_cleanup
from .render_context import RenderContextStateMgr
from .slot_expr_render import (
    _ExpressionExecution,
    _SlotExprRenderCompletion,
    _enable_slot_expr_render,
)
from .slot_expr_slot_context import SlotExprSlotContextStateMgr
from .subscription_binding import _SubscriptionBinding


@dataclass(eq=False, slots=True, weakref_slot=True)
class _ExpressionResourceHost:
    state_ref: weakref.ReferenceType[SlotExprSlotContextStateMgr]
    slot_id: Any

    def _published_slot_call_binding(self) -> SlotCallBinding | None:
        state = self.state_ref()
        if state is None:
            return None
        context = state._call_site_context_manager.get_current(self.slot_id)
        if context is None or context.is_closed or context.binding is None:
            return None
        return context.binding.binding

    def queue_slot_call_invalidation(self) -> None:
        state = self.state_ref()
        if state is None:
            return
        manager = state._call_site_context_manager
        for context in (
            manager.get_current(self.slot_id),
            manager.get_visible(self.slot_id),
        ):
            if context is not None and not context.is_closed:
                context.mark_invoke_dirty()
        from ._support import _ContextSlotExprHost

        _ContextSlotExprHost(state, self.slot_id).queue_slot_call_invalidation()

    def mark_slot_call_refresh_only(self) -> None:
        state = self.state_ref()
        if state is None:
            return
        manager = state._call_site_context_manager
        for context in (
            manager.get_current(self.slot_id),
            manager.get_visible(self.slot_id),
        ):
            if context is not None and not context.is_closed:
                context.mark_invoke_get()
        from ._support import _ContextSlotExprHost

        _ContextSlotExprHost(state, self.slot_id).mark_slot_call_refresh_only()


@dataclass(eq=False, slots=True)
class _ExpressionResourceCallSiteBinding(_SlotExprCallSiteBinding):
    resource_owner: _ResourceOwner
    notification_host: _ExpressionResourceHost | None
    completion_ref: weakref.ReferenceType[_SubscriptionExprRenderCompletion]

    def _close(self) -> None:
        completion = self.completion_ref()
        if completion is None:
            self.resource_owner.release()
        else:
            completion.release_resource(self.resource_owner)


@dataclass(eq=False, slots=True)
class _SubscriptionExpressionExecution(_ExpressionExecution):
    completion: _SubscriptionExprRenderCompletion

    def bind_result(
        self, host: SlotCallBindingHost, result: Any, previous: SlotCallBinding | None
    ) -> SlotCallBinding:
        self.require_active()
        handler = select_slot_call_handler(result)
        self.require_active()
        self.completion.require_expression_handler(handler)
        if type(handler) in (ExternalStoreHandler, UseEffectAsyncHandler):
            target = (
                previous.resource.host_ref()
                if type(previous) in (_SubscriptionBinding, _AsyncEffectBinding)
                else None
            )
            if target is None:
                target = _ExpressionResourceHost(weakref.ref(self.state), host.slot_id)
            binding = self.completion.bind_slot_call_result(
                handler, target, result, previous
            )
            self.require_active()
            # Kept through wrapping, including a failing value projection.
            self.completion._notification_hosts[id(binding)] = target
            return binding
        binding = self.completion.bind_slot_call_result(handler, host, result, previous)
        self.require_active()
        return binding

    def wrap_binding(self, binding: SlotCallBinding) -> _SlotExprCallSiteBinding:
        self.require_active()
        resource = self.completion.resource_for(binding)
        if resource is None:
            return super(_SubscriptionExpressionExecution, self).wrap_binding(binding)
        target = (
            binding.resource.host_ref()
            if type(binding) in (_SubscriptionBinding, _AsyncEffectBinding)
            else None
        )
        wrapper = _ExpressionResourceCallSiteBinding(
            binding=binding,
            resource_owner=_ResourceOwner.retain(resource),
            notification_host=target,
            completion_ref=weakref.ref(self.completion),
        )
        self.completion._expression_resource_bindings[id(wrapper)] = wrapper
        return wrapper

    def refresh_binding(
        self, binding: _SlotExprCallSiteBinding
    ) -> tuple[_SlotExprCallSiteBinding, bool] | None:
        self.require_active()
        refreshed = self.completion.refresh_slot_call_selection(binding.binding)
        self.require_active()
        if refreshed is None:
            return None
        selected, dirty = refreshed
        return self.wrap_binding(selected), dirty


def _enable_subscription_expr_render(root: RenderContextStateMgr) -> None:
    _enable_slot_expr_render(root)
    root._field_only_completion = _SubscriptionExprRenderCompletion(root)


@dataclass(eq=False, slots=True)
class _SubscriptionExprRenderCompletion(_SlotExprRenderCompletion):
    _expression_resource_bindings: dict[int, _ExpressionResourceCallSiteBinding] = (
        field(default_factory=dict, init=False)
    )
    _notification_hosts: dict[int, _ExpressionResourceHost] = field(
        default_factory=dict, init=False
    )

    def require_expression_handler(self, handler: SlotCallSemanticsHandler) -> None:
        if type(handler) not in (SlotValueHandler, ExternalStoreHandler):
            self.reject("resource expression results are not admitted")

    def expression_execution(
        self, state: SlotExprSlotContextStateMgr
    ) -> _SubscriptionExpressionExecution:
        execution = super(_SubscriptionExprRenderCompletion, self).expression_execution(
            state
        )
        return _SubscriptionExpressionExecution(self, state, execution.owner)

    def _complete(self, propagating: BaseException | None) -> None:
        owner = self.active
        assert owner is not None
        states = dict(self._expression_states)
        failure: BaseException | None = None
        try:
            super(_SubscriptionExprRenderCompletion, self)._complete(propagating)
        except BaseException as error:
            failure = error
        self._completing = True
        try:
            if owner.published is not None:
                retained = {
                    id(context.binding)
                    for state in states.values()
                    for context in state._call_site_context_manager.iter_current()
                }
                for identity, binding in self._expression_resource_bindings.items():
                    if identity not in retained:
                        self.release_resource(binding.resource_owner)
                self._expression_resource_bindings.clear()
                self._notification_hosts.clear()
        finally:
            self._completing = False
        errors, self._resource_cleanup_errors = self._resource_cleanup_errors, []
        if errors:
            if failure is not None:
                _raise_with_cleanup(failure, errors)
            if len(errors) == 1:
                raise errors[0]
            raise BaseExceptionGroup("expression subscription cleanup failed", errors)
        if failure is not None:
            raise failure
