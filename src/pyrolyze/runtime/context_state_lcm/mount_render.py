"""Validate candidate mount surfaces before the shared outer publication."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from pyrolyze.api import PyrolyzeMountAdvertisement, PyrolyzeMountAdvertisementRequest
from pyrolyze.runtime.slot_call_semantics import (
    ExternalStoreHandler,
    PyrolyzeMountAdvertisementHandler,
    SlotCallBinding,
    SlotCallSemanticsHandler,
    SlotValueHandler,
    UseEffectAsyncHandler,
    UseEffectHandler,
    select_slot_call_handler,
)
from .async_effect_render import (
    _AsyncEffectRenderCompletion,
    _enable_async_effect_render,
)
from .callback_render import _graph_states
from .mount_binding import _MountAdvertisementBinding
from .render_context import RenderContextStateMgr
from ._support import _native_context_param_name


def _enable_mount_render(root: RenderContextStateMgr) -> None:
    _enable_async_effect_render(root)
    root._field_only_completion = _MountRenderCompletion(root)


@dataclass(eq=False, slots=True)
class _MountRenderCompletion(_AsyncEffectRenderCompletion):
    def require_container_call(self, func: Any) -> None:
        self.require_resource_owner()
        if _native_context_param_name(func) is None:
            self.reject("opaque container helpers are not admitted by the mount proof")
        self.require_resource_owner()

    def require_slot_type(self, slot_type: type[Any]) -> None:
        from pyrolyze.runtime.context_bare_refactor_lcm import ContainerSlotContext

        if slot_type is not ContainerSlotContext:
            super(_MountRenderCompletion, self).require_slot_type(slot_type)

    def require_slot_call_result(self, result: Any) -> SlotCallSemanticsHandler:
        handler = select_slot_call_handler(result)
        if type(handler) not in (
            SlotValueHandler,
            ExternalStoreHandler,
            UseEffectHandler,
            UseEffectAsyncHandler,
            PyrolyzeMountAdvertisementHandler,
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
        if type(handler) is PyrolyzeMountAdvertisementHandler:
            return _MountAdvertisementBinding.bind(
                self, host, cast(PyrolyzeMountAdvertisementRequest, result)
            )
        return super(_MountRenderCompletion, self).bind_slot_call_result(
            handler, host, result, previous
        )

    def _advertisements_for(
        self, render: RenderContextStateMgr, *, current: bool
    ) -> dict[Any, PyrolyzeMountAdvertisement]:
        from .slot_call_slot_context import SlotCallSlotContextStateMgr

        entries: dict[Any, PyrolyzeMountAdvertisement] = {}
        for state in _graph_states(render, current=current):
            if (
                not isinstance(state, SlotCallSlotContextStateMgr)
                or state._render_context_state_mgr is not render
            ):
                continue
            facade = state.current if current else state
            binding = facade._invocation.binding
            if type(binding) is _MountAdvertisementBinding:
                entries[state.current_slot_id()] = binding.advertisement
        return entries

    def committed_mount_advertisements(
        self, render: RenderContextStateMgr
    ) -> tuple[PyrolyzeMountAdvertisement, ...]:
        return tuple(self._advertisements_for(render, current=True).values())

    def _complete(self, propagating: BaseException | None) -> None:
        assert self.active is not None
        owner = self.active
        self._completing = True
        preparation_error: BaseException | None = None
        try:
            if owner.first_failure is None and not owner._scopes:
                owner._require_identity()
                for render in self.render_roots:
                    entries = self._advertisements_for(render, current=False)
                    for surface in {
                        advert.surface_owner_id for advert in entries.values()
                    }:
                        render._validate_mount_advertisement_surface(
                            entries, surface_owner_id=surface
                        )
                        # Key equality may execute user code and replace the
                        # transaction. Validate only for the original owner.
                        owner._require_open()
                        owner._require_identity()
        except BaseException as error:
            owner.fail(error)
            preparation_error = error
            if propagating is None:
                propagating = error
        super(_MountRenderCompletion, self)._complete(propagating)
        if preparation_error is not None:
            raise preparation_error
