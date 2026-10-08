"""Detached effect requests; setup is a post-publication domain action.

The managed invocation carries the selected request. Its private owned wrapper
controls the resource, not incidental snapshot references. A new resource is
inert: discarding an unpublished request cannot run setup or the accepted
effect's cleanup. Dependency comparison happens during evaluation, before any
external action, and is fenced against replacement transaction tokens.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable
import weakref

from yidl_lifecycle.bindings_refcount import BindingBase

from pyrolyze.runtime.slot_call_semantics import SlotCallBinding, UseEffectRequest
from .resource_ownership import _ResourceOwner

if TYPE_CHECKING:
    from .effect_render import _EffectRenderCompletion


@dataclass(eq=False, slots=True)
class _EffectResource(BindingBase):
    effect_fn: Callable[[], Callable[[], None] | None] | None
    completion_ref: weakref.ReferenceType[_EffectRenderCompletion]
    cleanup: Callable[[], None] | None = field(default=None, init=False)
    started: bool = field(default=False, init=False)
    cleanup_failure: BaseException | None = field(default=None, init=False)

    def start(self) -> None:
        if self.is_closed or self.started:
            return
        effect, self.effect_fn = self.effect_fn, None
        assert effect is not None
        self.started = True
        cleanup = effect()
        if cleanup is not None and not callable(cleanup):
            raise TypeError("effect must return a cleanup callable or None")
        self.cleanup = cleanup

    def _close(self) -> None:
        self.effect_fn = None
        cleanup, self.cleanup = self.cleanup, None
        if cleanup is not None:
            try:
                cleanup()
            except BaseException as error:
                self.cleanup_failure = error
                completion = self.completion_ref()
                if completion is None:
                    raise
                completion.note_resource_cleanup_error(error)


@dataclass(frozen=True, slots=True)
class _EffectBinding(SlotCallBinding):
    request: UseEffectRequest
    resource: _EffectResource

    @classmethod
    def bind(
        cls,
        completion: _EffectRenderCompletion,
        request: UseEffectRequest,
        previous: SlotCallBinding | None,
    ) -> _EffectBinding:
        completion.require_resource_owner()
        reuse = (
            type(previous) is cls
            and not previous.resource.is_closed
            and previous.resource.started
            and request.deps is not None
            and request.deps == previous.request.deps
        )
        completion.require_resource_owner()
        if reuse:
            return cls(request, previous.resource)
        resource = _EffectResource(request.effect_fn, weakref.ref(completion))
        completion.note_new_resource(_ResourceOwner(resource))
        return cls(request, resource)

    def exposed_value(self) -> None:
        return None
