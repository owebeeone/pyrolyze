from __future__ import annotations

from typing import Any, Callable

from pyrolyze.runtime.slot_kinds import ContextKind

from ._base import USE_FACTORY, USE_OWNER
from ._support import REFRACTOR_CLASSES
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
    def __init__(self, owner: object, **kwargs: object) -> None:
        super().__init__(owner, **kwargs)
        self._component_identity: Any = None
        self._schema: tuple[int, tuple[str, ...]] = (0, ())
        self._child_context_state_mgr: Any = None
        self._last_runtime_func: Callable[..., Any] | None = None
        self._last_bound_receiver: object = object()
        self._last_args: tuple[Any, ...] = ()
        self._last_kwargs: dict[str, Any] = {}
        self._last_plain_args: tuple[Any, ...] = ()
        self._last_plain_kwargs: dict[str, Any] = {}
        self._last_dirty_state: Any = None
        self._pending_dirty_state: Any = None
        self._uses_dirty_state_api = False
        self._packed_kwargs = False
        self._packed_kwarg_param_names: tuple[str, ...] = ()
        self._param_names: tuple[str, ...] = ()
        self._site_metadata: tuple[Any, ...] = ()
        self._pass_owned_event_handler_order: tuple[Any, ...] = ()

    def invoke(
        self,
        component: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        owner_slot_facade: Any = USE_OWNER,
        scheduler_root_facade: Any = USE_OWNER,
        render_context_factory: Callable[..., Any] | object = USE_FACTORY,
        dirty_state: Any = None,
        _pyr_param_names: tuple[str, ...] | None = None,
        _pyr_args_dirty: tuple[Any, ...] | None = None,
        _pyr_kwargs_dirty: dict[str, Any] | None = None,
    ) -> Any:
        owner_slot_facade = self._resolve_owner_arg(owner_slot_facade)
        scheduler_root_facade = self._resolve_owner_arg(scheduler_root_facade)
        if render_context_factory is USE_FACTORY:
            render_context_cls = REFRACTOR_CLASSES.render_context_cls
            if render_context_cls is None:
                raise RuntimeError("render context class is not configured")
            render_context_factory = render_context_cls
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
        if self._child_context_state_mgr is None or self._component_identity != identity_key or self._schema != schema:
            self._dispose_child_context()
            child_context = render_context_factory(
                owner_slot=owner_slot_facade,
                scheduler_root=scheduler_root_facade,
                authored_app_context_lookup=self._parent_state_mgr.effective_authored_app_context_lookup(),
            )
            self._child_context_state_mgr = child_context._state_mgr
            self._component_identity = identity_key
            self._schema = schema

        self._begin_owned_event_handler_pass()
        try:
            self._last_runtime_func = runtime_func
            self._last_bound_receiver = bound_receiver
            self._param_names = param_names
            self._packed_kwargs = packed_kwargs
            self._packed_kwarg_param_names = packed_kwarg_param_names
            effective_param_names = _pyr_param_names or self._param_names
            if dirty_state is None and effective_param_names:
                dirty_state = dirtyof_values(
                    build_function_arg_dirty_map(
                        effective_param_names,
                        _pyr_args_dirty or (),
                        _pyr_kwargs_dirty or {},
                    )
                )
            if dirty_state is None:
                self._last_args = tuple(
                    _bind_pending_event_plain_value(self, _unwrap(arg)[0])
                    for arg in args
                )
                self._last_kwargs = {
                    key: _bind_pending_event_plain_value(self, _unwrap(value)[0])
                    for key, value in kwargs.items()
                }
                self._last_plain_args = ()
                self._last_plain_kwargs = {}
                self._last_dirty_state = None
                self._pending_dirty_state = None
                self._uses_dirty_state_api = False
            else:
                self._last_plain_args = tuple(
                    _bind_pending_event_plain_value(self, _unwrap(arg)[0])
                    for arg in args
                )
                self._last_plain_kwargs = {
                    key: _bind_pending_event_plain_value(self, _unwrap(value)[0])
                    for key, value in kwargs.items()
                }
                self._last_dirty_state = dirty_state
                self._pending_dirty_state = dirty_state
                self._last_args = ()
                self._last_kwargs = {}
                self._uses_dirty_state_api = True
            child_context = self._child_context_state_mgr.owner
            self._child_context_state_mgr._authored_app_context_lookup = (
                self._parent_state_mgr.effective_authored_app_context_lookup()
            )
            self._child_context_state_mgr._mounted_callback = self._rerun_child
            child_context._run_boundary()
        except BaseException:
            self.rollback_owned_event_handlers()
            raise
        self._committed_ui = self._child_context_state_mgr._committed_ui
        return None

    def commit_owned_event_handlers(self) -> None:
        if not self._pass_owned_event_handler_order and not any(
            child.context_kind() == ContextKind.EVENT_HANDLER and child._seen_in_pass
            for child in self._children.values()
        ):
            return
        unseen_slots = [
            slot_id
            for slot_id, child in self._children.items()
            if child.context_kind() == ContextKind.EVENT_HANDLER and not child._seen_in_pass
        ]
        for slot_id in unseen_slots:
            child = self._children.get(slot_id)
            if child is not None:
                child.deactivate()

        for child in self._children.values():
            if child.context_kind() == ContextKind.EVENT_HANDLER:
                child.commit_handler()

        self._pass_owned_event_handler_order = ()

    def rollback_owned_event_handlers(self) -> None:
        if not self._pass_owned_event_handler_order and not any(
            child.context_kind() == ContextKind.EVENT_HANDLER and child._seen_in_pass
            for child in self._children.values()
        ):
            return
        committed_ids = set(self._pass_owned_event_handler_order)
        for slot_id, child in list(self._children.items()):
            if child.context_kind() != ContextKind.EVENT_HANDLER:
                continue
            if slot_id not in committed_ids:
                child.deactivate()
                continue
            child.rollback_handler()
            child._seen_in_pass = True
        self._pass_owned_event_handler_order = ()

    def deactivate(self) -> None:
        self._dispose_child_context()
        super().deactivate()

    def _begin_owned_event_handler_pass(self) -> None:
        self._pass_owned_event_handler_order = tuple(
            slot_id
            for slot_id, child in self._children.items()
            if child.context_kind() == ContextKind.EVENT_HANDLER
        )
        for child in self._children.values():
            if child.context_kind() == ContextKind.EVENT_HANDLER:
                child._seen_in_pass = False

    def _rerun_child(self) -> None:
        child_context = None if self._child_context_state_mgr is None else self._child_context_state_mgr.owner
        runtime_func = self._last_runtime_func
        if child_context is None or runtime_func is None:
            raise RuntimeError("component child is not mounted")
        if self._uses_dirty_state_api:
            dirty_state = self._pending_dirty_state
            if dirty_state is None:
                dirty_state = _clean_dirty_state(self._last_dirty_state)
            else:
                self._pending_dirty_state = None
            if self._packed_kwargs:
                packed_kwargs = pack_function_args(
                    self._packed_kwarg_param_names,
                    self._last_plain_args,
                    self._last_plain_kwargs,
                )
                if self._last_bound_receiver is _BOUND_METHOD_SELF_MISSING:
                    runtime_func(child_context, dirty_state, **packed_kwargs)
                else:
                    runtime_func(self._last_bound_receiver, child_context, dirty_state, **packed_kwargs)
            elif self._last_bound_receiver is _BOUND_METHOD_SELF_MISSING:
                runtime_func(child_context, dirty_state, *self._last_plain_args, **self._last_plain_kwargs)
            else:
                runtime_func(
                    self._last_bound_receiver,
                    child_context,
                    dirty_state,
                    *self._last_plain_args,
                    **self._last_plain_kwargs,
                )
        elif self._packed_kwargs:
            packed_kwargs = pack_function_args(
                self._packed_kwarg_param_names,
                self._last_args,
                self._last_kwargs,
            )
            if self._last_bound_receiver is _BOUND_METHOD_SELF_MISSING:
                runtime_func(child_context, **packed_kwargs)
            else:
                runtime_func(self._last_bound_receiver, child_context, **packed_kwargs)
        elif self._last_bound_receiver is _BOUND_METHOD_SELF_MISSING:
            runtime_func(child_context, *self._last_args, **self._last_kwargs)
        else:
            runtime_func(self._last_bound_receiver, child_context, *self._last_args, **self._last_kwargs)
        self._committed_ui = child_context._state_mgr._committed_ui
        if not self._parent_state_mgr.is_scope_active():
            self._parent_state_mgr.refresh_committed_ui_from_children()

    def _dispose_child_context(self) -> None:
        child_context = None if self._child_context_state_mgr is None else self._child_context_state_mgr.owner
        if child_context is None:
            return
        child_context._remove_from_scheduler()
        for child in list(child_context._state_mgr._children.values()):
            child.deactivate()
        child_context._state_mgr._children.clear()
        child_context._state_mgr.clear_registered_slots()
        child_context._state_mgr._mounted_callback = None
        self._child_context_state_mgr = None
        self._pending_dirty_state = None
        self._committed_ui = ()
