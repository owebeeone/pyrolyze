"""Inert async requests owned through the existing private resource wrapper.

External operations retain only a weak completion callback, not graph ownership.
Closing the resource fences callbacks before cancel/cleanup (which can call back
or raise). A value snapshot can keep this resource alive, but cannot keep its
operation active once lifecycle releases the private owner.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable
import weakref

from yidl_lifecycle.bindings_refcount import BindingBase

from pyrolyze.runtime.slot_call_semantics import (
    AsyncEffectHandle,
    SlotCallBinding,
    UseEffectAsyncRequest,
)
from .resource_ownership import _ResourceOwner

if TYPE_CHECKING:
    from .async_effect_render import _AsyncEffectRenderCompletion


@dataclass(eq=False, slots=True, weakref_slot=True)
class _AsyncEffectResource(BindingBase):
    start_fn: Callable[[Callable[[], None]], AsyncEffectHandle | None] | None
    host_ref: weakref.ReferenceType[Any]
    completion_ref: weakref.ReferenceType[_AsyncEffectRenderCompletion]
    request_cleanup: Callable[[], None] | None
    cleanup: Callable[[], None] | None = field(default=None, init=False)
    handle: AsyncEffectHandle | None = field(default=None, init=False)
    active_token: object | None = field(default=None, init=False)
    started: bool = field(default=False, init=False)
    completed: bool = field(default=False, init=False)
    cleanup_failure: BaseException | None = field(default=None, init=False)

    def start(self) -> None:
        if self.is_closed or self.started:
            return
        start, self.start_fn = self.start_fn, None
        assert start is not None
        self.started = True
        self.cleanup, self.request_cleanup = self.request_cleanup, None
        token = self.active_token = object()
        target = weakref.ref(self)

        def on_complete() -> None:
            resource = target()
            if (
                resource is None
                or resource.is_closed
                or resource.active_token is not token
            ):
                return
            resource.completed = True
            resource.handle = None
            host = resource.host_ref()
            if host is not None:
                host.queue_slot_call_invalidation()

        try:
            handle = start(on_complete)
        except BaseException:
            self.active_token = None
            raise
        # Completion is permitted during start. Do not resurrect its finished
        # handle when the start function subsequently returns.
        if not self.completed:
            self.handle = handle

    def _close(self) -> None:
        self.active_token = None
        self.start_fn = None
        self.request_cleanup = None
        handle, self.handle = self.handle, None
        cleanup, self.cleanup = self.cleanup, None
        errors: list[BaseException] = []
        if handle is not None:
            try:
                handle.cancel()
            except BaseException as error:
                errors.append(error)
        if cleanup is not None:
            try:
                cleanup()
            except BaseException as error:
                errors.append(error)
        if errors:
            self.cleanup_failure = errors[0]
            completion = self.completion_ref()
            if completion is not None:
                for error in errors:
                    completion.note_resource_cleanup_error(error)
            elif len(errors) == 1:
                raise errors[0]
            else:
                raise BaseExceptionGroup("async effect cleanup failed", errors)


@dataclass(frozen=True, slots=True)
class _AsyncEffectBinding(SlotCallBinding):
    request: UseEffectAsyncRequest
    resource: _AsyncEffectResource

    @classmethod
    def bind(
        cls,
        completion: _AsyncEffectRenderCompletion,
        host: Any,
        request: UseEffectAsyncRequest,
        previous: SlotCallBinding | None,
    ) -> _AsyncEffectBinding:
        completion.require_resource_owner()
        reuse = (
            type(previous) is cls
            and not previous.resource.is_closed
            and previous.resource.started
            and previous.resource.host_ref() is host
            and request.deps is not None
            and request.deps == previous.request.deps
        )
        completion.require_resource_owner()
        if reuse:
            return cls(request, previous.resource)
        resource = _AsyncEffectResource(
            request.start, weakref.ref(host), weakref.ref(completion), request.cleanup
        )
        completion.note_new_resource(_ResourceOwner(resource))
        return cls(request, resource)

    def exposed_value(self) -> None:
        return None
