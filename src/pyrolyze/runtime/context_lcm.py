"""Lifecycle-backed context runtime overrides."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from pyrolyze.lifecycle import TransactionManager, local_store, managed, managed_context, transient

from . import context_original as _base
from .call_site_context import CallSiteContextManager

for _name, _value in vars(_base).items():
    if _name.startswith("_") and _name != "__all__":
        continue
    globals()[_name] = _value


@managed_context
class _EventHandlerSlotState:
    committed_callback: Callable[..., Any] | None = managed(default=None, compare="identity")
    committed_key: object | None = managed(default=None, compare="identity")
    staged_callback: Callable[..., Any] | None = transient(default=None)
    staged_key: object | None = transient(default=None)
    dispatch: Callable[..., None] | None = local_store(default=None)


@managed_context
class _LeafSlotState:
    last_args: tuple[Any, ...] = local_store(default_factory=tuple)
    last_kwargs: tuple[tuple[str, Any], ...] = local_store(default_factory=tuple)


@managed_context
class _ContainerSlotState:
    expects_native_root: bool = local_store(default=False)
    committed_native_root: bool = managed(default=False)
    site_metadata: tuple[_base.RuntimeSiteMetadata[Any], ...] = local_store(default_factory=tuple)


@managed_context
class _SlotExprSlotState:
    call_site_context_manager: CallSiteContextManager = local_store(default_factory=CallSiteContextManager)
    runtime_locals_by_slot_id: dict[Any, dict[str, Any]] = local_store(default_factory=dict)
    staged_call_site_ids: tuple[Any, ...] = transient(default_factory=tuple)
    staged_post_commit_callbacks: tuple[Callable[[], None], ...] = transient(default_factory=tuple)


@managed_context
class _SlotCallSlotState:
    function_identity: Any = local_store(default=None)
    schema: tuple[int, tuple[str, ...]] = local_store(default=(0, ()))
    last_args: tuple[Any, ...] = local_store(default_factory=tuple)
    last_kwargs: tuple[tuple[str, Any], ...] = local_store(default_factory=tuple)
    binding: _base.SlotCallBinding | None = local_store(default=None)
    site_metadata: tuple[_base.RuntimeSiteMetadata[Any], ...] = local_store(default_factory=tuple)
    runtime_locals: dict[str, Any] = local_store(default_factory=dict)


@managed_context
class _ComponentCallSlotState:
    component_identity: Any = local_store(default=None)
    schema: tuple[int, tuple[str, ...]] = local_store(default=(0, ()))
    child_context: _base.RenderContext | None = local_store(default=None)
    last_runtime_func: Callable[..., Any] | None = local_store(default=None)
    last_bound_receiver: object = local_store(default=_base._BOUND_METHOD_SELF_MISSING)
    last_args: tuple[Any, ...] = local_store(default_factory=tuple)
    last_kwargs: dict[str, Any] = local_store(default_factory=dict)
    last_plain_args: tuple[Any, ...] = local_store(default_factory=tuple)
    last_plain_kwargs: dict[str, Any] = local_store(default_factory=dict)
    last_dirty_state: _base.DirtyStateContext | None = local_store(default=None)
    pending_dirty_state: _base.DirtyStateContext | None = local_store(default=None)
    uses_dirty_state_api: bool = local_store(default=False)
    packed_kwargs: bool = local_store(default=False)
    packed_kwarg_param_names: tuple[str, ...] = local_store(default_factory=tuple)
    param_names: tuple[str, ...] = local_store(default_factory=tuple)
    site_metadata: tuple[_base.RuntimeSiteMetadata[Any], ...] = local_store(default_factory=tuple)
    pass_owned_event_handler_order: tuple[_base.SlotId, ...] = local_store(default_factory=tuple)


@managed_context
class _AppContextOverrideSlotState:
    declared_keys: tuple[_base.AppContextKey[Any], ...] = local_store(default_factory=tuple)
    committed_values: tuple[Any, ...] = local_store(default_factory=tuple)
    committed_key_states: dict[_base.AppContextKey[Any], _base._CommittedAppContextOverrideKeyState] = local_store(default_factory=dict)
    committed_lookup: _base.AppContextLookup = local_store(default_factory=_base._empty_authored_app_context_lookup)
    pass_committed_values: tuple[Any, ...] = local_store(default_factory=tuple)
    pass_committed_lookup: _base.AppContextLookup = local_store(default_factory=_base._empty_authored_app_context_lookup)
    pending_values: tuple[Any, ...] = local_store(default_factory=tuple)
    pending_lookup: _base.AppContextLookup = local_store(default_factory=_base._empty_authored_app_context_lookup)
    pending_initialized: bool = local_store(default=False)


class _LifecycleSlotMixin:
    _lcm_fields: tuple[str, ...] = ()
    _lcm_field_map: dict[str, str] = {}

    def _lcm_sync(self) -> None:
        state = object.__getattribute__(self, "_lcm_state")
        for name in self._lcm_fields:
            object.__setattr__(self, name, getattr(state, self._lcm_field_map.get(name, name)))

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        fields = type(self)._lcm_fields
        state = getattr(self, "_lcm_state", None)
        if state is not None and name in fields:
            state_name = self._lcm_field_map.get(name, name)
            setattr(state, state_name, value)
            object.__setattr__(self, name, getattr(state, state_name))
            return
        object.__setattr__(self, name, value)


@dataclass(slots=True)
class EventHandlerSlotContext(_LifecycleSlotMixin, _base.EventHandlerSlotContext):
    _lcm_txm: TransactionManager = field(init=False, repr=False)
    _lcm_state: _EventHandlerSlotState = field(init=False, repr=False)

    _lcm_fields = (
        "committed_callback",
        "committed_key",
        "staged_callback",
        "staged_key",
        "dispatch",
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "_lcm_txm", TransactionManager())
        object.__setattr__(
            self,
            "_lcm_state",
            _EventHandlerSlotState(
                transaction_manager=self._lcm_txm,
                committed_callback=self.committed_callback,
                committed_key=self.committed_key,
                dispatch=self.dispatch,
            ),
        )
        self._lcm_sync()

    def stage_callback(
        self,
        *,
        callback: Callable[..., Any],
        dirty: bool,
    ) -> Callable[..., None]:
        callback_key = _base._callback_key(callback)
        if dirty or self.committed_callback is None or self.committed_key != callback_key:
            if self._lcm_txm.active_transaction is None:
                self._lcm_txm.begin()
            self.staged_callback = callback
            self.staged_key = callback_key
        return self._dispatch_callable()

    def commit_handler(self) -> None:
        if self.staged_callback is None:
            return
        if self._lcm_txm.active_transaction is None:
            self._lcm_txm.begin()
        self.committed_callback = self.staged_callback
        self.committed_key = self.staged_key
        self._lcm_txm.commit()
        self._lcm_sync()

    def rollback_handler(self) -> None:
        if self._lcm_txm.active_transaction is not None:
            self._lcm_txm.rollback()
        self._lcm_sync()

    def deactivate(self) -> None:
        dispatch = self.dispatch
        if self._lcm_txm.active_transaction is not None:
            self._lcm_txm.rollback()
        object.__setattr__(self, "_lcm_txm", TransactionManager())
        object.__setattr__(
            self,
            "_lcm_state",
            _EventHandlerSlotState(
                transaction_manager=self._lcm_txm,
                dispatch=dispatch,
            ),
        )
        self._lcm_sync()
        _base.SlotContext.deactivate(self)

    def _dispatch_callable(self) -> Callable[..., None]:
        if self.dispatch is None:

            def dispatch(*args: Any, **kwargs: Any) -> None:
                callback = self.committed_callback
                if callback is None:
                    if _base.os.environ.get("PYROLYZE_ENV") == "prod":
                        return
                    raise RuntimeError("event handler is inactive")
                callback(*args, **kwargs)

            self.dispatch = dispatch
        return self.dispatch


@dataclass(slots=True)
class LeafSlotContext(_LifecycleSlotMixin, _base.LeafSlotContext):
    _lcm_state: _LeafSlotState = field(init=False, repr=False)

    _lcm_fields = (
        "last_args",
        "last_kwargs",
    )

    def __post_init__(self) -> None:
        _base.RerunnableSlotContext.__post_init__(self)
        object.__setattr__(
            self,
            "_lcm_state",
            _LeafSlotState(
                last_args=self.last_args,
                last_kwargs=self.last_kwargs,
            ),
        )
        self._lcm_sync()

    def invoke(self, leaf_fn: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
        self.last_args = args
        self.last_kwargs = tuple(sorted(kwargs.items()))
        return leaf_fn(*args, **kwargs)

    def invoke_native(
        self,
        leaf_fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        context_param: str,
    ) -> Any:
        self.last_args = args
        self.last_kwargs = tuple(sorted(kwargs.items()))
        self._begin_scope_pass()
        try:
            _ = context_param
            result = leaf_fn(self, *args, **kwargs)
            if result is not None:
                raise TypeError("@pyrolyze functions must return None")
        except BaseException:
            self._rollback_scope_pass()
            raise
        self._commit_scope_pass()
        return None


@dataclass(slots=True)
class ContainerSlotContext(_LifecycleSlotMixin, _base.ContainerSlotContext):
    _lcm_txm: TransactionManager = field(init=False, repr=False)
    _lcm_state: _ContainerSlotState = field(init=False, repr=False)

    _lcm_fields = (
        "expects_native_root",
        "committed_native_root",
        "site_metadata",
    )

    def __post_init__(self) -> None:
        _base.RerunnableSlotContext.__post_init__(self)
        object.__setattr__(self, "_lcm_txm", TransactionManager())
        object.__setattr__(
            self,
            "_lcm_state",
            _ContainerSlotState(
                transaction_manager=self._lcm_txm,
                expects_native_root=self.expects_native_root,
                committed_native_root=self.committed_native_root,
                site_metadata=self.site_metadata,
            ),
        )
        self._lcm_sync()

    def _begin_scope_pass(self) -> None:
        self._lcm_txm.begin()
        _base.ContextBase._begin_scope_pass(self)

    def _commit_scope_pass(self) -> None:
        try:
            _base.ContextBase._commit_scope_pass(self)
            self._lcm_txm.commit()
        finally:
            self._lcm_sync()

    def _rollback_scope_pass(self) -> None:
        try:
            _base.ContextBase._rollback_scope_pass(self)
        finally:
            self._lcm_txm.rollback()
            self._lcm_sync()


@dataclass(slots=True)
class SlotExprSlotContext(_LifecycleSlotMixin, _base.SlotExprSlotContext):
    _lcm_state: _SlotExprSlotState = field(init=False, repr=False)

    _lcm_fields = (
        "call_site_context_manager",
        "_runtime_locals_by_slot_id",
        "_staged_call_site_ids",
        "_staged_post_commit_callbacks",
    )
    _lcm_field_map = {
        "_runtime_locals_by_slot_id": "runtime_locals_by_slot_id",
        "_staged_call_site_ids": "staged_call_site_ids",
        "_staged_post_commit_callbacks": "staged_post_commit_callbacks",
    }

    def __post_init__(self) -> None:
        _base.RerunnableSlotContext.__post_init__(self)
        object.__setattr__(
            self,
            "_lcm_state",
            _SlotExprSlotState(
                call_site_context_manager=self.call_site_context_manager,
                runtime_locals_by_slot_id=self._runtime_locals_by_slot_id,
                staged_call_site_ids=self._staged_call_site_ids,
                staged_post_commit_callbacks=self._staged_post_commit_callbacks,
            ),
        )
        self._lcm_sync()

    def runtime_locals(self, slot_id: Any) -> dict[str, Any]:
        return self._runtime_locals_by_slot_id.setdefault(slot_id, {})

    def stage_slot_expr_pass(
        self,
        *,
        visited_call_site_ids: tuple[Any, ...],
        post_commit_callbacks: tuple[Callable[[], None], ...],
    ) -> None:
        merged_ids = list(self._staged_call_site_ids)
        for slot_id in visited_call_site_ids:
            if slot_id not in merged_ids:
                merged_ids.append(slot_id)
        self._staged_call_site_ids = tuple(merged_ids)
        if post_commit_callbacks:
            self._staged_post_commit_callbacks += post_commit_callbacks

    def append_slot_expr_post_commit_callback(self, callback: Callable[[], None]) -> None:
        self._staged_post_commit_callbacks += (callback,)

    def commit_binding(self) -> None:
        for call_site_id in self._staged_call_site_ids:
            call_site_context = self.call_site_context_manager.get_visible(call_site_id)
            binding = call_site_context.binding if call_site_context is not None else None
            commit = getattr(binding, "commit", None)
            if callable(commit):
                commit()
        self.call_site_context_manager.commit_pass()
        self.sync_committed_ui()
        callbacks = self._staged_post_commit_callbacks
        self._staged_call_site_ids = ()
        self._staged_post_commit_callbacks = ()
        for callback in callbacks:
            callback()

    def rollback_binding(self) -> None:
        for call_site_id in self._staged_call_site_ids:
            call_site_context = self.call_site_context_manager.get_visible(call_site_id)
            binding = call_site_context.binding if call_site_context is not None else None
            rollback = getattr(binding, "rollback", None)
            if callable(rollback):
                rollback()
        self.call_site_context_manager.rollback_pass()
        self.sync_committed_ui()
        self._staged_call_site_ids = ()
        self._staged_post_commit_callbacks = ()

    def sync_committed_ui(self) -> None:
        advertisements: list[_base.PyrolyzeMountAdvertisement] = []
        for call_site_context in self.call_site_context_manager.iter_current():
            binding = call_site_context.binding
            wrapped_binding = getattr(binding, "binding", None) if binding is not None else None
            if not isinstance(wrapped_binding, _base.PyrolyzeMountAdvertisementBinding):
                continue
            advertisement = wrapped_binding.retained_advertisement()
            if advertisement is not None:
                advertisements.append(advertisement)
        self._committed_ui = tuple(advertisements)

    def deactivate(self) -> None:
        self._staged_call_site_ids = ()
        self._staged_post_commit_callbacks = ()
        self.call_site_context_manager.close_all()
        self._runtime_locals_by_slot_id.clear()
        self._committed_ui = ()
        _base.SlotContext.deactivate(self)


@dataclass(slots=True)
class SlotCallSlotContext(_LifecycleSlotMixin, _base.SlotCallSlotContext):
    _lcm_state: _SlotCallSlotState = field(init=False, repr=False)

    _lcm_fields = (
        "function_identity",
        "schema",
        "last_args",
        "last_kwargs",
        "binding",
        "site_metadata",
        "_runtime_locals",
    )
    _lcm_field_map = {
        "_runtime_locals": "runtime_locals",
    }

    def __post_init__(self) -> None:
        _base.RerunnableSlotContext.__post_init__(self)
        object.__setattr__(
            self,
            "_lcm_state",
            _SlotCallSlotState(
                function_identity=self.function_identity,
                schema=self.schema,
                last_args=self.last_args,
                last_kwargs=self.last_kwargs,
                binding=self.binding,
                site_metadata=self.site_metadata,
                runtime_locals=self._runtime_locals,
            ),
        )
        self._lcm_sync()

    def evaluate(
        self,
        func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        result_shape: object | None = None,
    ) -> _base._SlotCallResult[Any]:
        resolved_func, resolved_args, resolved_kwargs, site_metadata = _base._resolve_runtime_site_call(
            self,
            func,
            args,
            kwargs,
        )
        self.site_metadata = site_metadata
        if resolved_func is None:
            raise RuntimeError("slot-call resolved to no callable target")
        prepared = _base.prepare_slot_call(resolved_func, resolved_args, resolved_kwargs, unwrap=_base._unwrap)
        should_invoke = _base.should_invoke_slot_call(
            _base.SlotCallStateSnapshot(
                invoke_dirty=self.invoke_dirty,
                function_identity=self.function_identity,
                schema=self.schema,
                last_args=self.last_args,
                last_kwargs=self.last_kwargs,
                has_binding=self.binding is not None,
            ),
            prepared,
        )

        if should_invoke:
            next_result = _base.call_with_optional_runtime_context(
                prepared,
                cache_attr_name="_pyrolyze_slot_runtime_ctx_param",
                runtime_context_annotation=_base.SlotRuntimeContext,
                runtime_context_factory=lambda: _base.SlotRuntimeContext(self),
            )
            commit_result = _base.commit_slot_call_invocation(
                host=self,
                prepared=prepared,
                previous_binding=self.binding,
                result=next_result,
            )
            self.binding = commit_result.binding
            self.function_identity = commit_result.function_identity
            self.schema = commit_result.schema
            self.last_args = commit_result.last_args
            self.last_kwargs = commit_result.last_kwargs
            result_dirty = commit_result.result_dirty
        else:
            result_dirty = False
            binding = self.binding
            if binding is not None:
                refreshed = _base.refresh_slot_call_binding(binding)
                if refreshed is not None:
                    _, result_dirty = refreshed

        binding = self.binding
        if binding is None:
            raise RuntimeError("slot-call slot has no binding after evaluation")
        return _base._SlotCallResult(
            dirty=_base._project_dirty_state(result_dirty, result_shape),
            value=binding.exposed_value(),
        )

    def queue_slot_call_invalidation(self) -> None:
        self.render_context._queue_invalidation_from(self, include_source=False)

    def mark_slot_call_refresh_only(self) -> None:
        self.queue_slot_call_invalidation()

    def enqueue_slot_call_post_commit(self, callback: Callable[[], None]) -> None:
        self.render_context._enqueue_post_commit(callback)

    def publish_slot_call_mount_advertisement(
        self,
        request: _base.PyrolyzeMountAdvertisementRequest,
    ) -> _base.PyrolyzeMountAdvertisement:
        return self.render_context._publish_mount_advertisement(self, request)

    def withdraw_slot_call_mount_advertisement(self) -> None:
        self.render_context._withdraw_mount_advertisement(self.slot_id)

    def _mark_binding_dirty(self) -> None:
        self.queue_slot_call_invalidation()

    def _build_committed_ui(self) -> tuple[object, ...]:
        binding = self.binding
        if isinstance(binding, _base.PyrolyzeMountAdvertisementBinding):
            advertisement = binding.retained_advertisement()
            if advertisement is None:
                return ()
            return (advertisement,)
        return _base.ContextBase._build_committed_ui(self)

    def commit_binding(self) -> None:
        binding = self.binding
        if binding is not None:
            binding.commit()
        self._sync_binding_committed_ui()

    def rollback_binding(self) -> None:
        binding = self.binding
        if binding is not None:
            binding.rollback()
        self._sync_binding_committed_ui()

    def deactivate(self) -> None:
        binding = self.binding
        self.binding = None
        if binding is not None:
            binding.deactivate()
        self._committed_ui = ()
        _base.SlotContext.deactivate(self)


@dataclass(slots=True)
class ComponentCallSlotContext(_LifecycleSlotMixin, _base.ComponentCallSlotContext):
    _lcm_state: _ComponentCallSlotState = field(init=False, repr=False)

    _lcm_fields = (
        "component_identity",
        "schema",
        "child_context",
        "last_runtime_func",
        "last_bound_receiver",
        "last_args",
        "last_kwargs",
        "last_plain_args",
        "last_plain_kwargs",
        "last_dirty_state",
        "pending_dirty_state",
        "uses_dirty_state_api",
        "packed_kwargs",
        "packed_kwarg_param_names",
        "param_names",
        "site_metadata",
        "_pass_owned_event_handler_order",
    )
    _lcm_field_map = {
        "_pass_owned_event_handler_order": "pass_owned_event_handler_order",
    }

    def __post_init__(self) -> None:
        _base.RerunnableSlotContext.__post_init__(self)
        object.__setattr__(
            self,
            "_lcm_state",
            _ComponentCallSlotState(
                component_identity=self.component_identity,
                schema=self.schema,
                child_context=self.child_context,
                last_runtime_func=self.last_runtime_func,
                last_bound_receiver=self.last_bound_receiver,
                last_args=self.last_args,
                last_kwargs=self.last_kwargs,
                last_plain_args=self.last_plain_args,
                last_plain_kwargs=self.last_plain_kwargs,
                last_dirty_state=self.last_dirty_state,
                pending_dirty_state=self.pending_dirty_state,
                uses_dirty_state_api=self.uses_dirty_state_api,
                packed_kwargs=self.packed_kwargs,
                packed_kwarg_param_names=self.packed_kwarg_param_names,
                param_names=self.param_names,
                site_metadata=self.site_metadata,
                pass_owned_event_handler_order=self._pass_owned_event_handler_order,
            ),
        )
        self._lcm_sync()

    def invoke(
        self,
        component: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        dirty_state: _base.DirtyStateContext | None = None,
        _pyr_param_names: tuple[str, ...] | None = None,
        _pyr_args_dirty: tuple[Any, ...] | None = None,
        _pyr_kwargs_dirty: dict[str, Any] | None = None,
    ) -> None:
        raw_component, _ = _base._unwrap(component)
        metadata, bound_receiver = _base._component_call_key(raw_component)
        runtime_func = _base._resolve_runtime_component_func(getattr(metadata, "_func", None))
        if metadata is None or runtime_func is None:
            raise TypeError("component_call expects a ComponentRef with _pyrolyze_meta._func")

        if bound_receiver is _base._BOUND_METHOD_SELF_MISSING:
            identity_key = raw_component
        else:
            underlying = getattr(raw_component, "__func__", None)
            identity_key = ("bound_component", id(bound_receiver), underlying)

        schema = (len(args), tuple(sorted(kwargs)))
        if self.child_context is None or self.component_identity != identity_key or self.schema != schema:
            self._dispose_child_context()
            self.child_context = _base.RenderContext(
                owner_slot=self,
                scheduler_root=self.render_context._scheduler_root,
                authored_app_context_lookup=self.parent._effective_authored_app_context_lookup(),
            )
            self.component_identity = identity_key
            self.schema = schema

        self._begin_owned_event_handler_pass()
        try:
            self.last_runtime_func = runtime_func
            self.last_bound_receiver = bound_receiver
            self.param_names = tuple(getattr(metadata, "param_names", ()))
            self.packed_kwargs = bool(getattr(metadata, "packed_kwargs", False))
            self.packed_kwarg_param_names = tuple(getattr(metadata, "packed_kwarg_param_names", ()))
            effective_param_names = _pyr_param_names or self.param_names
            if dirty_state is None and effective_param_names:
                dirty_state = _base.dirtyof_values(
                    _base.build_function_arg_dirty_map(
                        effective_param_names,
                        _pyr_args_dirty or (),
                        _pyr_kwargs_dirty or {},
                    )
                )
            if dirty_state is None:
                normalized_args = tuple(_base._bind_pending_event_plain_value(self, _base._unwrap(arg)[0]) for arg in args)
                normalized_kwargs = {
                    key: _base._bind_pending_event_plain_value(self, _base._unwrap(value)[0])
                    for key, value in kwargs.items()
                }
                self.last_args = normalized_args
                self.last_kwargs = normalized_kwargs
                self.last_plain_args = ()
                self.last_plain_kwargs = {}
                self.last_dirty_state = None
                self.pending_dirty_state = None
                self.uses_dirty_state_api = False
            else:
                self.last_plain_args = tuple(_base._bind_pending_event_plain_value(self, _base._unwrap(arg)[0]) for arg in args)
                self.last_plain_kwargs = {
                    key: _base._bind_pending_event_plain_value(self, _base._unwrap(value)[0])
                    for key, value in kwargs.items()
                }
                self.last_dirty_state = dirty_state
                self.pending_dirty_state = dirty_state
                self.last_args = ()
                self.last_kwargs = {}
                self.uses_dirty_state_api = True
            self.child_context._authored_app_context_lookup = self.parent._effective_authored_app_context_lookup()
            self.child_context._mounted_callback = self._rerun_child
            self.child_context._run_boundary()
        except BaseException:
            self.rollback_owned_event_handlers()
            raise
        self._committed_ui = self.child_context._committed_ui

    def _begin_owned_event_handler_pass(self) -> None:
        self._pass_owned_event_handler_order = tuple(
            slot_id
            for slot_id, child in self._children.items()
            if isinstance(child, EventHandlerSlotContext)
        )
        for child in self._children.values():
            if isinstance(child, EventHandlerSlotContext):
                child.seen_in_pass = False

    def commit_owned_event_handlers(self) -> None:
        if not self._pass_owned_event_handler_order and not any(
            isinstance(child, EventHandlerSlotContext) and child.seen_in_pass
            for child in self._children.values()
        ):
            return
        unseen_slots = [
            slot_id
            for slot_id, child in self._children.items()
            if isinstance(child, EventHandlerSlotContext) and not child.seen_in_pass
        ]
        for slot_id in unseen_slots:
            child = self._children.get(slot_id)
            if child is not None:
                child.deactivate()

        for child in self._children.values():
            if isinstance(child, EventHandlerSlotContext):
                child.commit_handler()

        self._pass_owned_event_handler_order = ()

    def rollback_owned_event_handlers(self) -> None:
        if not self._pass_owned_event_handler_order and not any(
            isinstance(child, EventHandlerSlotContext) and child.seen_in_pass
            for child in self._children.values()
        ):
            return
        committed_ids = set(self._pass_owned_event_handler_order)
        for slot_id, child in list(self._children.items()):
            if not isinstance(child, EventHandlerSlotContext):
                continue
            if slot_id not in committed_ids:
                child.deactivate()
                continue
            child.rollback_handler()
            child.seen_in_pass = True
        self._pass_owned_event_handler_order = ()

    def _rerun_child(self) -> None:
        child_context = self.child_context
        runtime_func = self.last_runtime_func
        if child_context is None or runtime_func is None:
            raise RuntimeError("component child is not mounted")
        if self.uses_dirty_state_api:
            dirty_state = self.pending_dirty_state
            if dirty_state is None:
                dirty_state = _base._clean_dirty_state(self.last_dirty_state)
            else:
                self.pending_dirty_state = None
            if self.packed_kwargs:
                packed_kwargs = _base.pack_function_args(
                    self.packed_kwarg_param_names,
                    self.last_plain_args,
                    self.last_plain_kwargs,
                )
                if self.last_bound_receiver is _base._BOUND_METHOD_SELF_MISSING:
                    runtime_func(child_context, dirty_state, **packed_kwargs)
                else:
                    runtime_func(self.last_bound_receiver, child_context, dirty_state, **packed_kwargs)
                self._committed_ui = child_context._committed_ui
                if not self.parent._scope_active:
                    self.parent._refresh_committed_ui_from_children()
                return
            if self.last_bound_receiver is _base._BOUND_METHOD_SELF_MISSING:
                runtime_func(child_context, dirty_state, *self.last_plain_args, **self.last_plain_kwargs)
            else:
                runtime_func(
                    self.last_bound_receiver,
                    child_context,
                    dirty_state,
                    *self.last_plain_args,
                    **self.last_plain_kwargs,
                )
            self._committed_ui = child_context._committed_ui
            if not self.parent._scope_active:
                self.parent._refresh_committed_ui_from_children()
            return

        if self.packed_kwargs:
            packed_kwargs = _base.pack_function_args(
                self.packed_kwarg_param_names,
                self.last_args,
                self.last_kwargs,
            )
            if self.last_bound_receiver is _base._BOUND_METHOD_SELF_MISSING:
                runtime_func(child_context, **packed_kwargs)
            else:
                runtime_func(self.last_bound_receiver, child_context, **packed_kwargs)
            self._committed_ui = child_context._committed_ui
            if not self.parent._scope_active:
                self.parent._refresh_committed_ui_from_children()
            return

        if self.last_bound_receiver is _base._BOUND_METHOD_SELF_MISSING:
            runtime_func(child_context, *self.last_args, **self.last_kwargs)
        else:
            runtime_func(
                self.last_bound_receiver,
                child_context,
                *self.last_args,
                **self.last_kwargs,
            )
        self._committed_ui = child_context._committed_ui
        if not self.parent._scope_active:
            self.parent._refresh_committed_ui_from_children()

    def _dispose_child_context(self) -> None:
        child_context = self.child_context
        if child_context is None:
            return
        child_context._remove_from_scheduler()
        for child in list(child_context._children.values()):
            child.deactivate()
        child_context._children.clear()
        child_context._slots_by_id.clear()
        child_context._mounted_callback = None
        self.child_context = None
        self.pending_dirty_state = None
        self._committed_ui = ()

    def deactivate(self) -> None:
        self._dispose_child_context()
        _base.SlotContext.deactivate(self)


@dataclass(slots=True)
class AppContextOverrideSlotContext(_LifecycleSlotMixin, _base.AppContextOverrideSlotContext):
    _lcm_state: _AppContextOverrideSlotState = field(init=False, repr=False)

    _lcm_fields = (
        "declared_keys",
        "committed_values",
        "_committed_key_states",
        "_committed_lookup",
        "_pass_committed_values",
        "_pass_committed_lookup",
        "_pending_values",
        "_pending_lookup",
        "_pending_initialized",
    )
    _lcm_field_map = {
        "_committed_key_states": "committed_key_states",
        "_committed_lookup": "committed_lookup",
        "_pass_committed_values": "pass_committed_values",
        "_pass_committed_lookup": "pass_committed_lookup",
        "_pending_values": "pending_values",
        "_pending_lookup": "pending_lookup",
        "_pending_initialized": "pending_initialized",
    }

    def __post_init__(self) -> None:
        _base.RerunnableSlotContext.__post_init__(self)
        object.__setattr__(
            self,
            "_lcm_state",
            _AppContextOverrideSlotState(
                declared_keys=self.declared_keys,
                committed_values=self.committed_values,
                committed_key_states=self._committed_key_states,
                committed_lookup=self._committed_lookup,
                pass_committed_values=self._pass_committed_values,
                pass_committed_lookup=self._pass_committed_lookup,
                pending_values=self._pending_values,
                pending_lookup=self._pending_lookup,
                pending_initialized=self._pending_initialized,
            ),
        )
        self._lcm_sync()

    def stage_override(
        self,
        keys: tuple[_base.AppContextKey[Any], ...],
        values: tuple[Any, ...],
    ) -> None:
        self._validate_override(keys, values)
        if self.declared_keys and self.declared_keys != keys:
            raise _base.AppContextOverrideStructureError(
                "app_context_override fixed keys cannot change at one slot"
            )
        if not self.declared_keys:
            self.declared_keys = keys
        self._apply_pending_values(values)
        self._pending_values = values
        self._pending_lookup = _base.OverlayAppContextLookup(
            parent=_base._ParentAuthoredAppContextLookup(self.parent),
            drips={key: self._committed_key_states[key].drip for key in keys},
        )
        self._pending_initialized = True

    def _effective_authored_app_context_lookup(self) -> _base.AppContextLookup:
        if self._scope_active and self._pending_initialized:
            return self._pending_lookup
        if self.declared_keys:
            return self._committed_lookup
        return _base.ContextBase._effective_authored_app_context_lookup(self)

    def _begin_scope_pass(self) -> None:
        self._pass_committed_values = self.committed_values
        self._pass_committed_lookup = self._committed_lookup
        _base.ContextBase._begin_scope_pass(self)

    def _commit_scope_pass(self) -> None:
        if not self._pending_initialized:
            raise RuntimeError("app_context_override slot was not staged")
        self.committed_values = self._pending_values
        self._committed_lookup = _base.OverlayAppContextLookup(
            parent=_base._ParentAuthoredAppContextLookup(self.parent),
            drips={key: self._committed_key_states[key].drip for key in self.declared_keys},
        )
        _base.ContextBase._commit_scope_pass(self)
        self._pending_values = ()
        self._pending_lookup = _base.EMPTY_APP_CONTEXT_LOOKUP
        self._pending_initialized = False
        self._pass_committed_values = ()
        self._pass_committed_lookup = _base.EMPTY_APP_CONTEXT_LOOKUP

    def _rollback_scope_pass(self) -> None:
        _base.ContextBase._rollback_scope_pass(self)
        self.committed_values = self._pass_committed_values
        self._committed_lookup = self._pass_committed_lookup
        if self.declared_keys and len(self._pass_committed_values) == len(self.declared_keys):
            self._apply_values(self._pass_committed_values)
        elif not self._pass_committed_values:
            for state in self._committed_key_states.values():
                state.deactivate()
        self._pending_values = ()
        self._pending_lookup = _base.EMPTY_APP_CONTEXT_LOOKUP
        self._pending_initialized = False
        self._pass_committed_values = ()
        self._pass_committed_lookup = _base.EMPTY_APP_CONTEXT_LOOKUP

    def deactivate(self) -> None:
        for state in self._committed_key_states.values():
            state.deactivate()
        self._committed_key_states = {}
        self._pending_values = ()
        self._pending_lookup = _base.EMPTY_APP_CONTEXT_LOOKUP
        self._pending_initialized = False
        _base.SlotContext.deactivate(self)

    def _apply_pending_values(self, values: tuple[Any, ...]) -> None:
        self._apply_values(values)

    def _apply_values(self, values: tuple[Any, ...]) -> None:
        parent_lookup = self.parent._effective_authored_app_context_lookup()
        for key, value in zip(self.declared_keys, values, strict=True):
            state = self._committed_key_states.get(key)
            if state is None:
                state = _base._CommittedAppContextOverrideKeyState(key=key)
                self._committed_key_states[key] = state
            if value is None:
                state.sync_parent(parent_lookup.resolve_drip(key))
            else:
                state.sync_value(value)


_base.EventHandlerSlotContext = EventHandlerSlotContext
_base.ContainerSlotContext = ContainerSlotContext
_base.LeafSlotContext = LeafSlotContext
_base.SlotExprSlotContext = SlotExprSlotContext
_base.SlotCallSlotContext = SlotCallSlotContext
_base.ComponentCallSlotContext = ComponentCallSlotContext
_base.AppContextOverrideSlotContext = AppContextOverrideSlotContext

globals()["EventHandlerSlotContext"] = EventHandlerSlotContext
globals()["ContainerSlotContext"] = ContainerSlotContext
globals()["LeafSlotContext"] = LeafSlotContext
globals()["SlotExprSlotContext"] = SlotExprSlotContext
globals()["SlotCallSlotContext"] = SlotCallSlotContext
globals()["ComponentCallSlotContext"] = ComponentCallSlotContext
globals()["AppContextOverrideSlotContext"] = AppContextOverrideSlotContext

__PYROLYZE_CONTEXT_IMPLEMENTATION__ = "lcm"
