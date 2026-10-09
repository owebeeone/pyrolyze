"""Classify scope containers before construction on the private lifecycle route."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from typing import Any

from ._support import (
    _RuntimeCallSite,
    _ContainerCallHandle,
    _DirectiveCallHandle,
    _MountContainerCallHandle,
    _NativeContainerCallHandle,
    _PyrolyzeContainerCallHandle,
    _clean_dirty_state,
    _component_call_key,
    _container_runtime_context_param_name,
    _native_context_param_name,
    _resolve_runtime_component_func,
    _resolve_runtime_site_call,
)
from .context_base import ContextBaseStateMgr
from .keyed_loop_render import _KeyedLoopRenderCompletion, _enable_keyed_loop_render
from .render_attempt import _RenderAttempt
from .render_context import RenderContextStateMgr


@dataclass(eq=False, slots=True)
class _ContainerRenderCompletion(_KeyedLoopRenderCompletion):
    container_routing_enabled = True
    opaque_containers_enabled = False

    def require_container_host(self, host: object) -> None:
        self.require_resource_owner()
        if type(host) is not _DirectiveCallHandle:
            self.reject("mount helpers must return the runtime's directive scope")

    def _require_original(self, owner: _RenderAttempt) -> None:
        owner._require_open()
        owner._require_identity()
        if self.active is not owner or self._completing:
            error = RuntimeError("original container render is no longer active")
            owner.fail(error)
            raise error

    @contextmanager
    def _scope_handle(
        self, owner: _RenderAttempt, handle: AbstractContextManager[Any]
    ) -> Iterator[Any]:
        # Check before attempt_scope: a stale handle must not start a new render.
        self._require_original(owner)
        with self.attempt_scope():
            with handle as slot:
                self._require_original(owner)
                yield slot
                self._require_original(owner)

    def container_call(
        self,
        context: ContextBaseStateMgr,
        slot_id: Any,
        container_fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        parent: Any,
        dirty_state: Any,
        param_names: tuple[str, ...] | None,
        args_dirty: tuple[Any, ...] | None,
        kwargs_dirty: dict[str, Any] | None,
    ) -> AbstractContextManager[Any] | None:
        from pyrolyze.runtime.context_bare_refactor_lcm import (
            ContainerSlotContext,
            DirectiveSlotContext,
        )

        self.require_resource_owner()
        assert self.active is not None
        owner = self.active
        with self.attempt_scope():
            site = _RuntimeCallSite(context.resolve_slot_id(slot_id), parent)
            self._require_original(owner)
            func, raw_args, raw_kwargs, metadata = _resolve_runtime_site_call(
                site, container_fn, args, kwargs
            )
            self._require_original(owner)
            if func is None:
                context.omit_resolved_slot(site.slot_id)
                return None
            handle: (
                _ContainerCallHandle
                | _MountContainerCallHandle
                | _NativeContainerCallHandle
                | _PyrolyzeContainerCallHandle
            )
            mount_param = _container_runtime_context_param_name(func)
            if mount_param is not None:
                handle = _MountContainerCallHandle(
                    slot=None,
                    container_fn=func,
                    args=raw_args,
                    kwargs=raw_kwargs,
                    context_param=mount_param,
                )
                slot_type = DirectiveSlotContext
            else:
                component, receiver = _component_call_key(func)
                runtime_func = _resolve_runtime_component_func(
                    getattr(component, "_func", None)
                )
                if component is not None and runtime_func is not None:
                    handle = _PyrolyzeContainerCallHandle(
                        slot=None,
                        runtime_func=runtime_func,
                        bound_receiver=receiver,
                        args=raw_args,
                        kwargs=raw_kwargs,
                        dirty_state=dirty_state or _clean_dirty_state(None),
                        param_names=tuple(getattr(component, "param_names", ())),
                        dynamic_param_names=param_names,
                        dynamic_args_dirty=args_dirty,
                        dynamic_kwargs_dirty=kwargs_dirty,
                        packed_kwargs=bool(getattr(component, "packed_kwargs", False)),
                        packed_kwarg_param_names=tuple(
                            getattr(component, "packed_kwarg_param_names", ())
                        ),
                    )
                else:
                    native_param = _native_context_param_name(func)
                    if native_param is None:
                        if not self.opaque_containers_enabled:
                            self.reject(
                                "opaque container helpers are not admitted by the container proof"
                            )
                        handle = _ContainerCallHandle(
                            slot=None,
                            container_fn=func,
                            args=raw_args,
                            kwargs=raw_kwargs,
                            require_original=lambda: self._require_original(owner),
                        )
                    else:
                        handle = _NativeContainerCallHandle(
                            slot=None,
                            container_fn=func,
                            args=raw_args,
                            kwargs=raw_kwargs,
                            context_param=native_param,
                        )
                slot_type = ContainerSlotContext
            self._require_original(owner)
            slot = context.ensure_resolved_slot(
                site.slot_id, slot_type, parent_facade=parent
            )
            self._require_original(owner)
            slot._state_mgr._site_metadata = metadata
            handle.slot = slot
            return self._scope_handle(owner, handle)


def _enable_container_render(root: RenderContextStateMgr) -> None:
    _enable_keyed_loop_render(root)
    root._field_only_completion = _ContainerRenderCompletion(root)
