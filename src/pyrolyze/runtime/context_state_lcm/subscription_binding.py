"""Separate render ownership from the Python lifetime of value snapshots.

Lifecycle's owned field holds a private ``_ResourceOwner`` using its normal
Python-reference lifetime. That wrapper adopts one explicit resource reference;
another real owner must retain its own reference. Public value bindings and store
notifications never retain the wrapper, so keeping a snapshot, resource, or
callback alive cannot keep an unselected subscription active.

The resource uses the existing explicit-refcount BindingBase, not a second
transaction engine. Abandoned candidate wrappers are released explicitly because
an exception traceback can retain constructor/evaluation locals. Release is
idempotent: later wrapper finalization cannot unsubscribe twice. Accepted wrappers
remain owned by lifecycle until replacement, removal, or graph collection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable
import weakref

from yidl_lifecycle.bindings_refcount import BindingBase as RefCountedBindingBase

from pyrolyze.runtime.slot_call_semantics import ExternalStoreRef, SlotCallBinding
from .resource_ownership import _ResourceOwner
from .override_lookup import _OverrideDrip, _OverrideRead, _OverrideReadReceipt

if TYPE_CHECKING:
    from .subscription_render import _SubscriptionRenderCompletion


@dataclass(eq=False, slots=True, weakref_slot=True)
class _StoreSubscription(RefCountedBindingBase):
    identity: object
    host_ref: weakref.ReferenceType[Any]
    completion_ref: weakref.ReferenceType[_SubscriptionRenderCompletion]
    unsubscribe: Callable[[], None] | None = field(default=None, init=False)
    revision: int = field(default=0, init=False)

    @classmethod
    def open(
        cls,
        completion: _SubscriptionRenderCompletion,
        host: Any,
        ref: ExternalStoreRef[Any],
    ) -> _ResourceOwner:
        subscription = cls(ref.identity, weakref.ref(host), weakref.ref(completion))
        owner = _ResourceOwner(subscription)
        target = weakref.ref(subscription)

        def notify() -> None:
            resource = target()
            if resource is not None and not resource.is_closed:
                receiver = resource.host_ref()
                if isinstance(resource.identity, _OverrideDrip) and receiver is not None:
                    # Reused resources keep the old callback, not the latest
                    # read. Only the published selection can acknowledge it.
                    resolve = getattr(receiver, "_published_slot_call_binding", None)
                    selected = None if resolve is None else resolve()
                    if (
                        type(selected) is _SubscriptionBinding
                        and selected.resource is resource
                        and selected.read_receipt is not None
                        and selected.read_receipt.acknowledges(resource.identity)
                    ):
                        return
                resource.revision += 1
                if receiver is not None:
                    receiver.mark_slot_call_refresh_only()

        try:
            unsubscribe = ref.subscribe(notify)
            if not callable(unsubscribe):
                error = TypeError(
                    "external store subscribe must return a cleanup callable"
                )
                completion.note_resource_cleanup_error(error)
                raise error
            subscription.unsubscribe = unsubscribe
            completion.require_resource_owner()
            completion.note_new_resource(owner)
        except BaseException:
            completion.release_resource(owner)
            raise
        return owner

    def _close(self) -> None:
        unsubscribe = self.unsubscribe
        self.unsubscribe = None
        if unsubscribe is not None:
            try:
                unsubscribe()
            except BaseException as error:
                completion = self.completion_ref()
                if completion is None:
                    raise
                completion.note_resource_cleanup_error(error)


@dataclass(eq=False, slots=True)
class _SubscriptionBinding(SlotCallBinding):
    resource: _StoreSubscription
    ref: ExternalStoreRef[Any]
    value: Any
    revision: int
    read_receipt: _OverrideReadReceipt | None = None

    @classmethod
    def bind(
        cls,
        completion: _SubscriptionRenderCompletion,
        host: Any,
        ref: ExternalStoreRef[Any],
        previous: SlotCallBinding | None,
    ) -> _SubscriptionBinding:
        completion.require_resource_owner()
        resource: _StoreSubscription | None = None
        if type(previous) is cls:
            selected = previous.resource
            reuse = not selected.is_closed and selected.identity == ref.identity
            completion.require_resource_owner()
            if reuse and selected.host_ref() is host:
                resource = selected
        owner: _ResourceOwner | None = None
        if resource is None:
            owner = _StoreSubscription.open(completion, host, ref)
            resource = owner.resource
            assert isinstance(resource, _StoreSubscription)
        try:
            revision = resource.revision
            value, receipt = (
                ref.get.read()
                if isinstance(ref.get, _OverrideRead)
                else (ref.get(), None)
            )
            completion.require_resource_owner()
            return cls(resource, ref, value, revision, receipt)
        except BaseException:
            if owner is not None:
                completion.release_resource(owner)
            raise

    def exposed_value(self) -> Any:
        return self.value

    def refreshed(
        self,
        completion: _SubscriptionRenderCompletion,
    ) -> tuple[_SubscriptionBinding, bool] | None:
        if self.resource.revision == self.revision:
            return None
        completion.require_resource_owner()
        revision = self.resource.revision
        value, receipt = (
            self.ref.get.read()
            if isinstance(self.ref.get, _OverrideRead)
            else (self.ref.get(), None)
        )
        completion.require_resource_owner()
        dirty = value != self.value
        completion.require_resource_owner()
        return type(self)(self.resource, self.ref, value, revision, receipt), dirty
