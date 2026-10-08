"""Synchronous effects on the outer render decision; no async/mount activation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

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
from .effect_binding import _EffectBinding, _EffectResource
from .render_attempt import _raise_with_cleanup
from .render_context import RenderContextStateMgr
from .subscription_render import (
    _SubscriptionRenderCompletion,
    _enable_subscription_render,
)


def _enable_effect_render(root: RenderContextStateMgr) -> None:
    _enable_subscription_render(root)
    root._field_only_completion = _EffectRenderCompletion(root)


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

    def _complete(self, propagating: BaseException | None) -> None:
        from .slot_call_slot_context import SlotCallSlotContextStateMgr

        assert self.active is not None
        owner = self.active
        previous = {
            id(state): state.current._invocation.binding.resource
            for state in _graph_states(self.root, current=True)
            if isinstance(state, SlotCallSlotContextStateMgr)
            and type(state.current._invocation.binding) is _EffectBinding
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
                    if type(binding) is not _EffectBinding:
                        continue
                    old: _EffectResource | None = previous.get(id(state))
                    if old is not None and old.cleanup_failure is not None:
                        # Legacy replacement does not start after its own
                        # cleanup fails; that must not suppress other slots.
                        continue
                    try:
                        binding.resource.start()
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
