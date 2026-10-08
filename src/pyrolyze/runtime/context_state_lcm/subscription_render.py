"""Private subscription completion; effects and mounts remain on legacy routes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

from yidl_lifecycle.bindings import BindingBase
from yidl_lifecycle.bindings_refcount import BindingBase as RefCountedBindingBase

from pyrolyze.runtime.slot_call_semantics import (
    ExternalStoreHandler,
    ExternalStoreRef,
    SlotCallBinding,
    SlotCallSemanticsHandler,
    SlotValueHandler,
    select_slot_call_handler,
)
from .callback_render import _graph_states
from .render_attempt import _raise_with_cleanup
from .render_context import RenderContextStateMgr
from .slot_call_render import _SlotCallRenderCompletion, _enable_slot_call_render
from .resource_ownership import _ResourceOwner
from .subscription_binding import _SubscriptionBinding


def _enable_subscription_render(root: RenderContextStateMgr) -> None:
    _enable_slot_call_render(root)
    root._field_only_completion = _SubscriptionRenderCompletion(root)


@dataclass(eq=False, slots=True, weakref_slot=True)
class _SubscriptionRenderCompletion(_SlotCallRenderCompletion):
    _new_resource_owners: dict[int, _ResourceOwner] = field(
        default_factory=dict, init=False
    )
    _resource_cleanup_errors: list[BaseException] = field(
        default_factory=list, init=False
    )

    def require_slot_call_result(self, result: Any) -> SlotCallSemanticsHandler:
        handler = select_slot_call_handler(result)
        if type(handler) not in (SlotValueHandler, ExternalStoreHandler):
            self.reject("external resource slot-call result is not admitted")
        return handler

    def require_resource_owner(self) -> None:
        if self.active is None or self._completing:
            self.reject("resource selection requires an active render")
        self.active._require_open()
        self.active._require_identity()

    def note_new_resource(self, owner: _ResourceOwner) -> None:
        assert owner.resource is not None
        self._new_resource_owners[id(owner.resource)] = owner

    def release_resource(self, owner: _ResourceOwner) -> None:
        completing = self._completing
        self._completing = True
        try:
            owner.release()
        finally:
            self._completing = completing

    def note_resource_cleanup_error(self, error: BaseException) -> None:
        self._resource_cleanup_errors.append(error)
        self._cleanup_failure = error

    def bind_slot_call_result(
        self,
        handler: SlotCallSemanticsHandler,
        host: Any,
        result: Any,
        previous: SlotCallBinding | None,
    ) -> SlotCallBinding:
        self.require_resource_owner()
        if type(handler) is ExternalStoreHandler:
            return _SubscriptionBinding.bind(
                self, host, cast(ExternalStoreRef[Any], result), previous
            )
        return super(_SubscriptionRenderCompletion, self).bind_slot_call_result(
            handler, host, result, previous
        )

    def refresh_slot_call_selection(
        self,
        binding: SlotCallBinding,
    ) -> tuple[SlotCallBinding, bool] | None:
        if type(binding) is _SubscriptionBinding:
            return binding.refreshed(self)
        return None

    def resource_for(self, binding: SlotCallBinding) -> RefCountedBindingBase | None:
        return binding.resource if type(binding) is _SubscriptionBinding else None

    def resource_owner_for(
        self, binding: SlotCallBinding, previous: BindingBase | None
    ) -> BindingBase | None:
        resource = self.resource_for(binding)
        if resource is None:
            return None
        if type(previous) is _ResourceOwner and previous.resource is resource:
            return previous
        return self._new_resource_owners[id(resource)]

    def discard_unstaged_selection(self, binding: SlotCallBinding, state: Any) -> None:
        resource = self.resource_for(binding)
        if resource is None:
            return
        owner = self._new_resource_owners.get(id(resource))
        if (
            owner is None
            or owner is state.current._binding_owner
            or owner is state._binding_owner
        ):
            return
        # A comparison/projection can lose the original token before any field
        # owns this wrapper. Its cleanup is safe even with unknown publication;
        # do not release a wrapper that made it into current or working storage.
        self.release_resource(owner)
        self._new_resource_owners.pop(id(resource))

    def _complete(self, propagating: BaseException | None) -> None:
        from .slot_call_slot_context import SlotCallSlotContextStateMgr

        assert self.active is not None
        owner = self.active
        known = {
            id(state): state
            for state in _graph_states(self.root, current=True)
            if isinstance(state, SlotCallSlotContextStateMgr)
        }
        for render in self.render_roots:
            for state in render._slots_by_id.values():
                if isinstance(state, SlotCallSlotContextStateMgr):
                    known[id(state)] = state
        failure: BaseException | None = None
        try:
            if owner.first_failure is None and not owner._scopes:
                owner._require_identity()
                candidates = {
                    id(state) for state in _graph_states(self.root, current=False)
                }
                for identity, state in known.items():
                    if identity not in candidates:
                        state._stage_slot_call_retirement()
        except BaseException as error:
            owner.fail(error)
            if propagating is None:
                propagating = error
            failure = error
        try:
            super(_SubscriptionRenderCompletion, self)._complete(propagating)
        except BaseException as error:
            failure = error
        self._completing = True
        try:
            if owner.published is not None:
                retained = {
                    id(state.current._binding_owner) for state in known.values()
                }
                pending, self._new_resource_owners = self._new_resource_owners, {}
                for subscription in pending.values():
                    if not owner.published or id(subscription) not in retained:
                        self.release_resource(subscription)
                pending.clear()
        finally:
            self._completing = False
        # Unknown publication retains handles as quarantined evidence, not undo.
        errors, self._resource_cleanup_errors = (
            self._resource_cleanup_errors,
            [],
        )
        if errors:
            primary = failure if failure is not None else propagating
            if primary is not None:
                _raise_with_cleanup(primary, errors)
            if len(errors) == 1:
                raise errors[0]
            raise BaseExceptionGroup("resource cleanup failed", errors)
        if failure is not None:
            raise failure
