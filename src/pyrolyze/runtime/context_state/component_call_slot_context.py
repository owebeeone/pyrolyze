from __future__ import annotations

from typing import Any, Callable

from ._support import (
    _BOUND_METHOD_SELF_MISSING,
    _bind_pending_event_plain_value,
    _clean_dirty_state,
    _component_call_key,
    _resolve_runtime_component_func,
    _unwrap,
    dirtyof_values,
)
from pyrolyze.runtime.function_arg_helpers import build_function_arg_dirty_map, pack_function_args

from .rerunnable_slot_context import RerunnableSlotContextStateMgr


class ComponentCallSlotContextStateMgr(RerunnableSlotContextStateMgr):
    def invoke(
        self,
        component: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        dirty_state: Any = None,
        _pyr_param_names: tuple[str, ...] | None = None,
        _pyr_args_dirty: tuple[Any, ...] | None = None,
        _pyr_kwargs_dirty: dict[str, Any] | None = None,
    ) -> Any:
        owner = self.owner

        raw_component, _ = _unwrap(component)
        metadata, bound_receiver = _component_call_key(raw_component)
        runtime_func = _resolve_runtime_component_func(getattr(metadata, "_func", None))
        if metadata is None or runtime_func is None:
            runtime_func = raw_component
            bound_receiver = _BOUND_METHOD_SELF_MISSING
            identity_key = raw_component
            param_names: tuple[str, ...] = ()
            packed_kwargs = False
            packed_kwarg_param_names: tuple[str, ...] = ()
        else:
            if bound_receiver is _BOUND_METHOD_SELF_MISSING:
                identity_key = raw_component
            else:
                underlying = getattr(raw_component, "__func__", None)
                identity_key = ("bound_component", id(bound_receiver), underlying)
            param_names = tuple(getattr(metadata, "param_names", ()))
            packed_kwargs = bool(getattr(metadata, "packed_kwargs", False))
            packed_kwarg_param_names = tuple(getattr(metadata, "packed_kwarg_param_names", ()))

        schema = (len(args), tuple(sorted(kwargs)))
        if (
            owner.child_context is None
            or owner.component_identity != identity_key
            or owner.schema != schema
        ):
            self._dispose_child_context()
            owner.child_context = owner._render_context_cls(
                owner_slot=owner,
                scheduler_root=owner.render_context._scheduler_root,
                authored_app_context_lookup=owner.parent._effective_authored_app_context_lookup(),
            )
            owner.component_identity = identity_key
            owner.schema = schema

        self._begin_owned_event_handler_pass()
        try:
            owner.last_runtime_func = runtime_func
            owner.last_bound_receiver = bound_receiver
            owner.param_names = param_names
            owner.packed_kwargs = packed_kwargs
            owner.packed_kwarg_param_names = packed_kwarg_param_names
            effective_param_names = _pyr_param_names or owner.param_names
            if dirty_state is None and effective_param_names:
                dirty_state = dirtyof_values(
                    build_function_arg_dirty_map(
                        effective_param_names,
                        _pyr_args_dirty or (),
                        _pyr_kwargs_dirty or {},
                    )
                )
            if dirty_state is None:
                owner.last_args = tuple(
                    _bind_pending_event_plain_value(owner, _unwrap(arg)[0])
                    for arg in args
                )
                owner.last_kwargs = {
                    key: _bind_pending_event_plain_value(owner, _unwrap(value)[0])
                    for key, value in kwargs.items()
                }
                owner.last_plain_args = ()
                owner.last_plain_kwargs = {}
                owner.last_dirty_state = None
                owner.pending_dirty_state = None
                owner.uses_dirty_state_api = False
            else:
                owner.last_plain_args = tuple(
                    _bind_pending_event_plain_value(owner, _unwrap(arg)[0])
                    for arg in args
                )
                owner.last_plain_kwargs = {
                    key: _bind_pending_event_plain_value(owner, _unwrap(value)[0])
                    for key, value in kwargs.items()
                }
                owner.last_dirty_state = dirty_state
                owner.pending_dirty_state = dirty_state
                owner.last_args = ()
                owner.last_kwargs = {}
                owner.uses_dirty_state_api = True
            owner.child_context._authored_app_context_lookup = owner.parent._effective_authored_app_context_lookup()
            owner.child_context._mounted_callback = self._rerun_child
            owner.child_context._run_boundary()
        except BaseException:
            self.rollback_owned_event_handlers()
            raise
        owner._committed_ui = owner.child_context._committed_ui
        return None

    def commit_owned_event_handlers(self) -> None:
        owner = self.owner
        if not owner._pass_owned_event_handler_order and not any(
            type(child).__name__ == "EventHandlerSlotContext" and child.seen_in_pass
            for child in owner._children.values()
        ):
            return
        unseen_slots = [
            slot_id
            for slot_id, child in owner._children.items()
            if type(child).__name__ == "EventHandlerSlotContext" and not child.seen_in_pass
        ]
        for slot_id in unseen_slots:
            child = owner._children.get(slot_id)
            if child is not None:
                child.deactivate()

        for child in owner._children.values():
            if type(child).__name__ == "EventHandlerSlotContext":
                child.commit_handler()

        owner._pass_owned_event_handler_order = ()

    def rollback_owned_event_handlers(self) -> None:
        owner = self.owner
        if not owner._pass_owned_event_handler_order and not any(
            type(child).__name__ == "EventHandlerSlotContext" and child.seen_in_pass
            for child in owner._children.values()
        ):
            return
        committed_ids = set(owner._pass_owned_event_handler_order)
        for slot_id, child in list(owner._children.items()):
            if type(child).__name__ != "EventHandlerSlotContext":
                continue
            if slot_id not in committed_ids:
                child.deactivate()
                continue
            child.rollback_handler()
            child.seen_in_pass = True
        owner._pass_owned_event_handler_order = ()

    def deactivate(self) -> None:
        self._dispose_child_context()
        super().deactivate()

    def __post_init__(self) -> None:
        super().__post_init__()
        owner = self.owner
        owner.component_identity = None
        owner.schema = (0, ())
        owner.child_context = None
        owner.last_runtime_func = None
        owner.last_bound_receiver = object()
        owner.last_args = ()
        owner.last_kwargs = {}
        owner.last_plain_args = ()
        owner.last_plain_kwargs = {}
        owner.last_dirty_state = None
        owner.pending_dirty_state = None
        owner.uses_dirty_state_api = False
        owner.packed_kwargs = False
        owner.packed_kwarg_param_names = ()
        owner.param_names = ()
        owner.site_metadata = ()
        owner._pass_owned_event_handler_order = ()

    def _begin_owned_event_handler_pass(self) -> None:
        owner = self.owner
        owner._pass_owned_event_handler_order = tuple(
            slot_id
            for slot_id, child in owner._children.items()
            if type(child).__name__ == "EventHandlerSlotContext"
        )
        for child in owner._children.values():
            if type(child).__name__ == "EventHandlerSlotContext":
                child.seen_in_pass = False

    def _rerun_child(self) -> None:
        owner = self.owner

        child_context = owner.child_context
        runtime_func = owner.last_runtime_func
        if child_context is None or runtime_func is None:
            raise RuntimeError("component child is not mounted")
        if owner.uses_dirty_state_api:
            dirty_state = owner.pending_dirty_state
            if dirty_state is None:
                dirty_state = _clean_dirty_state(owner.last_dirty_state)
            else:
                owner.pending_dirty_state = None
            if owner.packed_kwargs:
                packed_kwargs = pack_function_args(
                    owner.packed_kwarg_param_names,
                    owner.last_plain_args,
                    owner.last_plain_kwargs,
                )
                if owner.last_bound_receiver is _BOUND_METHOD_SELF_MISSING:
                    runtime_func(child_context, dirty_state, **packed_kwargs)
                else:
                    runtime_func(owner.last_bound_receiver, child_context, dirty_state, **packed_kwargs)
            elif owner.last_bound_receiver is _BOUND_METHOD_SELF_MISSING:
                runtime_func(child_context, dirty_state, *owner.last_plain_args, **owner.last_plain_kwargs)
            else:
                runtime_func(
                    owner.last_bound_receiver,
                    child_context,
                    dirty_state,
                    *owner.last_plain_args,
                    **owner.last_plain_kwargs,
                )
        elif owner.packed_kwargs:
            packed_kwargs = pack_function_args(
                owner.packed_kwarg_param_names,
                owner.last_args,
                owner.last_kwargs,
            )
            if owner.last_bound_receiver is _BOUND_METHOD_SELF_MISSING:
                runtime_func(child_context, **packed_kwargs)
            else:
                runtime_func(owner.last_bound_receiver, child_context, **packed_kwargs)
        elif owner.last_bound_receiver is _BOUND_METHOD_SELF_MISSING:
            runtime_func(child_context, *owner.last_args, **owner.last_kwargs)
        else:
            runtime_func(owner.last_bound_receiver, child_context, *owner.last_args, **owner.last_kwargs)
        owner._committed_ui = child_context._committed_ui
        if not owner.parent._scope_active:
            owner.parent._refresh_committed_ui_from_children()

    def _dispose_child_context(self) -> None:
        owner = self.owner
        child_context = owner.child_context
        if child_context is None:
            return
        child_context._remove_from_scheduler()
        for child in list(child_context._children.values()):
            child.deactivate()
        child_context._children.clear()
        child_context._slots_by_id.clear()
        child_context._mounted_callback = None
        owner.child_context = None
        owner.pending_dirty_state = None
        owner._committed_ui = ()
