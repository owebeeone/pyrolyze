"""Synchronous expression effects reuse render-owned resource selection.

Field publication precedes external setup. The expression collection retires old
ownership first; failed cleanup suppresses only that call site's replacement.
Independent setup actions drain even when an earlier action raises.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator

from pyrolyze.runtime.slot_call_semantics import (
    ExternalStoreHandler,
    SlotCallSemanticsHandler,
    SlotValueHandler,
    UseEffectHandler,
)
from .callback_render import _graph_states
from .effect_render import _EffectDeliveryResource
from .render_attempt import _raise_with_cleanup
from .render_context import RenderContextStateMgr
from .slot_expr_slot_context import SlotExprSlotContextStateMgr
from .subscription_expr_render import (
    _SubscriptionExprRenderCompletion,
    _enable_subscription_expr_render,
)


def _enable_effect_expr_render(root: RenderContextStateMgr) -> None:
    _enable_subscription_expr_render(root)
    root._field_only_completion = _EffectExprRenderCompletion(root)


@dataclass(eq=False, slots=True)
class _EffectExprRenderCompletion(_SubscriptionExprRenderCompletion):
    def require_expression_handler(self, handler: SlotCallSemanticsHandler) -> None:
        if type(handler) not in (
            SlotValueHandler,
            ExternalStoreHandler,
            UseEffectHandler,
        ):
            self.reject("resource expression results are not admitted")

    def _expression_effects(
        self,
    ) -> Iterator[tuple[tuple[int, Any], _EffectDeliveryResource]]:
        for state in _graph_states(self.root, current=True):
            if not isinstance(state, SlotExprSlotContextStateMgr):
                continue
            collection = state._call_site_context_manager._pass_context.current.contexts
            for slot_id, context in collection.contexts.items():
                wrapped = context.binding
                if wrapped is None:
                    continue
                resource = self.delivery_resource_for(wrapped.binding)
                if resource is not None:
                    yield (id(state), slot_id), resource

    def _complete(self, propagating: BaseException | None) -> None:
        owner = self.active
        assert owner is not None
        previous = dict(self._expression_effects())
        failure: BaseException | None = None
        try:
            super(_EffectExprRenderCompletion, self)._complete(propagating)
        except BaseException as error:
            failure = error
        errors: list[BaseException] = []
        self._completing = True
        try:
            if owner.published is True:
                for identity, resource in tuple(self._expression_effects()):
                    old = previous.get(identity)
                    if old is not None and old.cleanup_failure is not None:
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
            raise BaseExceptionGroup("expression effect delivery failed", errors)
        if failure is not None:
            raise failure
