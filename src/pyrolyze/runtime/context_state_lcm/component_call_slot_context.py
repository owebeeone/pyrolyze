from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable

from pyrolyze.freezable import freezable_dataclass, frozen_dataclass
from .lifecycle_adapter import const, local_store, managed, managed_context
from pyrolyze.runtime.slot_kinds import ContextKind

from ._base import USE_FACTORY, USE_OWNER, _copy_parent_state_mgr, _copy_slot_id
from ._support import REFRACTOR_CLASSES
from ._support import (
    _BOUND_METHOD_SELF_MISSING,
    _bind_pending_event_plain_value,
    _clean_dirty_state,
    _component_call_key,
    _resolve_runtime_component_func,
    _unwrap,
    dirtyof_values,
    DirtyStateContext,
)
from pyrolyze.runtime.function_arg_helpers import build_function_arg_dirty_map, pack_function_args

from .context_base import PASS_TX_KEY
from .field_only_render import _field_only_completion
from .rerunnable_slot_context import RerunnableSlotContextStateMgr


@freezable_dataclass(frozen_type="FrozenComponentCallInvocationState")
class ComponentCallInvocationState:
    runtime_func: Callable[..., Any] | None = None
    bound_receiver: object = _BOUND_METHOD_SELF_MISSING
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] | None = None
    author_args: tuple[Any, ...] = ()
    author_kwargs: dict[str, Any] | None = None
    dirty_state: DirtyStateContext | None = None
    pending_dirty_state: DirtyStateContext | None = None
    uses_dirty_state_api: bool = False
    packed_kwargs: bool = False
    packed_kwarg_param_names: tuple[str, ...] = ()
    param_names: tuple[str, ...] = ()


@frozen_dataclass(mutable_type=ComponentCallInvocationState)
class FrozenComponentCallInvocationState:
    pass


@managed_context
class ComponentCallSlotContextStateMgr(RerunnableSlotContextStateMgr):
    _parent_state_mgr: Any = const(init=False, default_factory=_copy_parent_state_mgr)
    _slot_id: Any = const(init=False, default_factory=_copy_slot_id)
    _component_identity: Any = local_store(default=None)
    _schema: tuple[int, tuple[str, ...]] = local_store(default=(0, ()))
    _child_context_state_mgr: Any = local_store(default=None)
    _pass_owned_event_handler_order: tuple[Any, ...] = local_store(default_factory=tuple)
    _call_state: FrozenComponentCallInvocationState = managed(
        default_factory=FrozenComponentCallInvocationState,
        init=False,
        tx_key=PASS_TX_KEY,
    )

    def invoke(
        self,
        component: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        owner_slot_facade: Any = USE_OWNER,
        scheduler_root_facade: Any = USE_OWNER,
        render_context_factory: Callable[..., Any] | object = USE_FACTORY,
        dirty_state: DirtyStateContext | None = None,
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
            completion = _field_only_completion(self)
            if completion is not None and self._child_context_state_mgr is not None:
                completion.reject("component replacement is not admitted by SC2")
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
        completion = _field_only_completion(self)
        invocation_owner = None if completion is None else completion.active
        try:
            effective_param_names = _pyr_param_names or param_names
            if dirty_state is None and effective_param_names:
                dirty_state = dirtyof_values(
                    build_function_arg_dirty_map(
                        effective_param_names,
                        _pyr_args_dirty or (),
                        _pyr_kwargs_dirty or {},
                    )
                )
            if dirty_state is None:
                args_for_rerun = tuple(
                    _bind_pending_event_plain_value(self, _unwrap(arg)[0])
                    for arg in args
                )
                kwargs_for_rerun = {
                    key: _bind_pending_event_plain_value(self, _unwrap(value)[0])
                    for key, value in kwargs.items()
                }
                self._call_state = ComponentCallInvocationState(
                    runtime_func=runtime_func,
                    bound_receiver=bound_receiver,
                    args=args_for_rerun,
                    kwargs=kwargs_for_rerun,
                    author_args=(),
                    author_kwargs={},
                    dirty_state=None,
                    pending_dirty_state=None,
                    uses_dirty_state_api=False,
                    packed_kwargs=packed_kwargs,
                    packed_kwarg_param_names=packed_kwarg_param_names,
                    param_names=param_names,
                ).to_frozen()
            else:
                author_args = tuple(
                    _bind_pending_event_plain_value(self, _unwrap(arg)[0])
                    for arg in args
                )
                author_kwargs = {
                    key: _bind_pending_event_plain_value(self, _unwrap(value)[0])
                    for key, value in kwargs.items()
                }
                self._call_state = ComponentCallInvocationState(
                    runtime_func=runtime_func,
                    bound_receiver=bound_receiver,
                    args=(),
                    kwargs={},
                    author_args=author_args,
                    author_kwargs=author_kwargs,
                    dirty_state=dirty_state,
                    pending_dirty_state=dirty_state,
                    uses_dirty_state_api=True,
                    packed_kwargs=packed_kwargs,
                    packed_kwarg_param_names=packed_kwarg_param_names,
                    param_names=param_names,
                ).to_frozen()
            child_context = self._child_context_state_mgr.owner
            self._child_context_state_mgr._authored_app_context_lookup = (
                self._parent_state_mgr.effective_authored_app_context_lookup()
            )
            self._child_context_state_mgr._mounted_callback = self._rerun_child
            child_context._run_boundary()
        except BaseException as error:
            if invocation_owner is not None:
                invocation_owner.fail(error)
            self.rollback_owned_event_handlers()
            raise
        self.ui_state = self._child_context_state_mgr.ui_state
        return None

    def commit_owned_event_handlers(self) -> None:
        if not self._pass_owned_event_handler_order and not any(
            child.context_kind() == ContextKind.EVENT_HANDLER and child._seen_in_pass
            for child in self.children_state.values()
        ):
            return
        unseen_slots = [
            slot_id
            for slot_id, child in self.children_state.items()
            if child.context_kind() == ContextKind.EVENT_HANDLER and not child._seen_in_pass
        ]
        for slot_id in unseen_slots:
            child = self.children_state.get(slot_id)
            if child is not None:
                child.deactivate()

        self._pass_owned_event_handler_order = ()

    def rollback_owned_event_handlers(self) -> None:
        if _field_only_completion(self) is not None:
            return
        if not self._pass_owned_event_handler_order and not any(
            child.context_kind() == ContextKind.EVENT_HANDLER and child._seen_in_pass
            for child in self.children_state.values()
        ):
            return
        committed_ids = set(self._pass_owned_event_handler_order)
        for slot_id, child in list(self.children_state.items()):
            if child.context_kind() != ContextKind.EVENT_HANDLER:
                continue
            if slot_id not in committed_ids:
                child.deactivate()
                continue
            child._discard_selection()
            child._seen_in_pass = True
        self._pass_owned_event_handler_order = ()

    def deactivate(self) -> None:
        completion = _field_only_completion(self)
        if completion is not None:
            completion.require_retirement_allowed(self)
        with self.publish_write_scope():
            self._dispose_child_context()
            super().deactivate()

    def _begin_owned_event_handler_pass(self) -> None:
        completion = _field_only_completion(self)
        if completion is not None:
            completion.note_owned_event_handler_pass(self)
        self._pass_owned_event_handler_order = tuple(
            slot_id
            for slot_id, child in self.children_state.items()
            if child.context_kind() == ContextKind.EVENT_HANDLER
        )
        for child in self.children_state.values():
            if child.context_kind() == ContextKind.EVENT_HANDLER:
                child._seen_in_pass = False

    def _rerun_child(self) -> None:
        child_context = None if self._child_context_state_mgr is None else self._child_context_state_mgr.owner
        call_state = self._call_state
        runtime_func = call_state.runtime_func
        if child_context is None or runtime_func is None:
            raise RuntimeError("component child is not mounted")
        refresh_parent = not self._parent_state_mgr.is_scope_active()
        with self.publish_write_scope():
            if call_state.uses_dirty_state_api:
                dirty_state = call_state.pending_dirty_state
                if dirty_state is None:
                    dirty_state = _clean_dirty_state(call_state.dirty_state)
                else:
                    self._call_state = replace(call_state, pending_dirty_state=None)
                    call_state = self._call_state
                if call_state.packed_kwargs:
                    packed_kwargs = pack_function_args(
                        call_state.packed_kwarg_param_names,
                        call_state.author_args,
                        call_state.author_kwargs or {},
                    )
                    if call_state.bound_receiver is _BOUND_METHOD_SELF_MISSING:
                        runtime_func(child_context, dirty_state, **packed_kwargs)
                    else:
                        runtime_func(call_state.bound_receiver, child_context, dirty_state, **packed_kwargs)
                elif call_state.bound_receiver is _BOUND_METHOD_SELF_MISSING:
                    runtime_func(
                        child_context,
                        dirty_state,
                        *call_state.author_args,
                        **(call_state.author_kwargs or {}),
                    )
                else:
                    runtime_func(
                        call_state.bound_receiver,
                        child_context,
                        dirty_state,
                        *call_state.author_args,
                        **(call_state.author_kwargs or {}),
                    )
            elif call_state.packed_kwargs:
                packed_kwargs = pack_function_args(
                    call_state.packed_kwarg_param_names,
                    call_state.args,
                    call_state.kwargs or {},
                )
                if call_state.bound_receiver is _BOUND_METHOD_SELF_MISSING:
                    runtime_func(child_context, **packed_kwargs)
                else:
                    runtime_func(call_state.bound_receiver, child_context, **packed_kwargs)
            elif call_state.bound_receiver is _BOUND_METHOD_SELF_MISSING:
                runtime_func(child_context, *call_state.args, **(call_state.kwargs or {}))
            else:
                runtime_func(
                    call_state.bound_receiver,
                    child_context,
                    *call_state.args,
                    **(call_state.kwargs or {}),
                )
            self.ui_state = child_context._state_mgr.ui_state
            if refresh_parent:
                self._parent_state_mgr.refresh_committed_ui_from_children()

    def _dispose_child_context(self) -> None:
        child_context = None if self._child_context_state_mgr is None else self._child_context_state_mgr.owner
        if child_context is None:
            return
        completion = _field_only_completion(self)
        if completion is not None:
            completion.require_retirement_allowed(self)
        child_context._remove_from_scheduler()
        with child_context._state_mgr.publish_write_scope():
            for child in list(child_context._state_mgr.children_state.values()):
                child.deactivate()
            child_context._state_mgr.children_state = {}
            child_context._state_mgr.clear_registered_slots()
        child_context._state_mgr._mounted_callback = None
        self._child_context_state_mgr = None
        self._call_state = replace(self._call_state, pending_dirty_state=None)
        self.ui_state = ()
