"""Synchronous effect selection and delivery on the outer render decision."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, cast

from yidl_lifecycle.bindings_refcount import BindingBase

from pyrolyze.runtime.slot_call_semantics import (
    ExternalStoreHandler,
    SlotCallBinding,
    SlotCallSemanticsHandler,
    SlotValueHandler,
    UseEffectHandler,
    UseEffectRequest,
    select_slot_call_handler,
)
from .callback_render import _graph_states
from .effect_binding import _EffectBinding
from .render_attempt import _raise_with_cleanup
from .subscription_render import _SubscriptionRenderCompletion


class _EffectDeliveryResource(Protocol):
    cleanup_failure: BaseException | None

    def start(self) -> None: ...




@dataclass(eq=False, slots=True)
class _EffectRenderCompletion(_SubscriptionRenderCompletion):
    def require_slot_call_result(self, result: Any) -> SlotCallSemanticsHandler:
        handler = select_slot_call_handler(result)
        if type(handler) not in (
            SlotValueHandler,
            ExternalStoreHandler,
            UseEffectHandler,
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
        if type(handler) is UseEffectHandler:
            return _EffectBinding.bind(self, cast(UseEffectRequest, result), previous)
        return super(_EffectRenderCompletion, self).bind_slot_call_result(
            handler, host, result, previous
        )

    def resource_for(self, binding: SlotCallBinding) -> BindingBase | None:
        if type(binding) is _EffectBinding:
            return binding.resource
        return super(_EffectRenderCompletion, self).resource_for(binding)

    def delivery_resource_for(
        self, binding: SlotCallBinding | None
    ) -> _EffectDeliveryResource | None:
        return binding.resource if type(binding) is _EffectBinding else None

    def _complete(self, propagating: BaseException | None) -> None:
        from .slot_call_slot_context import SlotCallSlotContextStateMgr

        assert self.active is not None
        owner = self.active
        previous = {
            id(state): resource
            for state in _graph_states(self.root, current=True)
            if isinstance(state, SlotCallSlotContextStateMgr)
            and (
                resource := self.delivery_resource_for(
                    state.current._invocation.binding
                )
            )
            is not None
        }
        failure: BaseException | None = None
        try:
            super(_EffectRenderCompletion, self)._complete(propagating)
        except BaseException as error:
            failure = error
        errors: list[BaseException] = []
        self._completing = True
        try:
            # Publication and generation are already finalized. Never start
            # provisional/uncertain effects, and never undo published fields
            # because setup fails. Drain independent actions, preserving errors.
            if owner.published is True:
                for state in _graph_states(self.root, current=True):
                    if not isinstance(state, SlotCallSlotContextStateMgr):
                        continue
                    binding = state.current._invocation.binding
                    resource = self.delivery_resource_for(binding)
                    if resource is None:
                        continue
                    old = previous.get(id(state))
                    if old is not None and old.cleanup_failure is not None:
                        # Legacy replacement does not start after its own
                        # cleanup fails; that must not suppress other slots.
                        continue
                    try:
                        resource.start()
                    except BaseException as error:
                        errors.append(error)
                        self._cleanup_failure = error
        finally:
            self._completing = False
        if errors:
            if failure is not None:
                _raise_with_cleanup(failure, errors)
            if len(errors) == 1:
                raise errors[0]
            raise BaseExceptionGroup("effect delivery failed", errors)
        if failure is not None:
            raise failure
