"""Public facade layer refactored around per-class state managers."""

from __future__ import annotations

__PYROLYZE_CONTEXT_IMPLEMENTATION__ = "bare_refactor"

from typing import Any, Callable, TypeVar

from pyrolyze.api import (
    MountDirective,
    PyrolyzeMountAdvertisement,
    PyrolyzeMountAdvertisementRequest,
    SlotSelector,
    UIElement,
)

from .app_context import (
    EMPTY_APP_CONTEXT_LOOKUP,
    GENERATION_TRACKER_KEY,
    AppContextKey,
    AppContextLookup,
    AppContextStore,
)
from .call_site_context import CallSiteContextManager
from .context_state_lcm import _support
from .context_state_lcm import (
    AppContextOverrideSlotContextStateMgr,
    ComponentCallSlotContextStateMgr,
    ContainerSlotContextStateMgr,
    ContextBaseStateMgr,
    DirectiveSlotContextStateMgr,
    EventHandlerSlotContextStateMgr,
    KeyedLoopSlotContextStateMgr,
    LeafSlotContextStateMgr,
    LoopItemSlotContextStateMgr,
    RenderContextStateMgr,
    RerunnableSlotContextStateMgr,
    SlotCallSlotContextStateMgr,
    SlotContextStateMgr,
    SlotExprSlotContextStateMgr,
)
from .pyro_call import RuntimeSiteMetadata
from .slot_expr import SlotExprLiteralContext
from .slot_call_semantics import (
    ExternalStoreBinding,
    ExternalStoreRef,
    PyrolyzeMountAdvertisementBinding,
    SlotCallBinding,
    SlotValueBinding,
    UseEffectAsyncBinding,
    UseEffectAsyncRequest,
    UseEffectBinding,
    UseEffectRequest,
)
from .slot_kinds import ContextKind
from .slot_identity import ModuleId, ModuleRegistry, SlotId, SlotIdPath, module_registry


T = TypeVar("T")
TESTING_ONLY = property


class _StateDelegatingObject:
    _state_mgr_cls = ContextBaseStateMgr
    _state_mgr: ContextBaseStateMgr
    _context_kind = ContextKind.SLOT

    def _init_state_mgr(self, *args: Any, **kwargs: Any) -> None:
        self._state_mgr = self._state_mgr_cls(self, *args, **kwargs)

    def get_kind(self) -> ContextKind:
        return self._state_mgr.context_kind()


DirtyStateContext = _support.DirtyStateContext
dirtyof = _support.dirtyof
dirtyof_values = _support.dirtyof_values
SlotOwnershipError = _support.SlotOwnershipError
DuplicateKeyError = _support.DuplicateKeyError
DuplicateMountAdvertisementError = _support.DuplicateMountAdvertisementError
MountAdvertisementContextError = _support.MountAdvertisementContextError
AppContextOverrideStructureError = _support.AppContextOverrideStructureError
_SlotCallResult = _support._SlotCallResult
PendingEventHandlerBinding = _support.PendingEventHandlerBinding
_CommittedUiEntry = _support._CommittedUiEntry
SlotRuntimeContext = _support.SlotRuntimeContext
ContainerCallRuntimeContext = _support.ContainerCallRuntimeContext
_PassScopeHandle = _support._PassScopeHandle
_InvalidationScheduler = _support._InvalidationScheduler


class ContextBase(_StateDelegatingObject, SlotExprLiteralContext):
    _state_mgr_cls = ContextBaseStateMgr
    _pass_scope_handle_cls = _PassScopeHandle
    _generation_tracker_key_const = GENERATION_TRACKER_KEY
    _context_kind = ContextKind.SLOT
    render_context: RenderContext

    def __init__(self, render_context: RenderContext) -> None:
        self._init_state_mgr(
            render_context_state_mgr=(
                render_context._state_mgr if hasattr(render_context, "_state_mgr") else None
            )
        )

    @property
    def render_context(self) -> RenderContext:
        render_context_state_mgr = self._state_mgr._render_context_state_mgr
        return self if render_context_state_mgr is None else render_context_state_mgr.owner

    def _require_active_scope(self) -> None:
        self._state_mgr.require_active_scope()

    def _begin_scope_pass(self) -> None:
        self._state_mgr.begin_pass()

    def _commit_scope_pass(self) -> None:
        self._state_mgr.end_pass()

    def _rollback_scope_pass(self) -> None:
        self._state_mgr.rollback_pass()

    def _runtime_key_path(self) -> tuple[Any, ...]:
        return self._state_mgr.runtime_key_path()

    def _resolve_slot_id(self, slot_id: SlotId) -> SlotId:
        return self._state_mgr.resolve_slot_id(slot_id)

    def _ensure_slot(self, slot_id: SlotId, slot_type: type[T]) -> T:
        return self._state_mgr.ensure_slot(slot_id, slot_type, parent_facade=self)

    def _ensure_resolved_slot(self, slot_id: SlotId, slot_type: type[T]) -> T:
        return self._state_mgr.ensure_resolved_slot(slot_id, slot_type, parent_facade=self)

    def _materialize_pending_event_handler(
        self,
        binding: PendingEventHandlerBinding,
    ) -> Callable[..., None]:
        return self._state_mgr.materialize_pending_event_handler(binding, parent_facade=self)

    def _build_committed_ui(self) -> tuple[UIElement | MountDirective, ...]:
        return self._state_mgr.build_committed_ui()

    def _refresh_committed_ui_from_children(self) -> None:
        self._state_mgr.refresh_committed_ui_from_children()

    @property
    def root_context(self) -> RenderContext:
        render_context_state_mgr = self._state_mgr._render_context_state_mgr
        return self if render_context_state_mgr is None else render_context_state_mgr.owner

    def get_app_context(self, key: AppContextKey[T]) -> T:
        return self._state_mgr.get_app_context(key)

    def has_app_context(self, key: AppContextKey[Any]) -> bool:
        return self._state_mgr.has_app_context(key)

    def get_authored_app_context(self, key: AppContextKey[T]) -> T:
        return self._state_mgr.get_authored_app_context(key)

    def has_authored_app_context(self, key: AppContextKey[Any]) -> bool:
        return self._state_mgr.has_authored_app_context(key)

    def authored_app_context_ref(self, key: AppContextKey[T]) -> ExternalStoreRef[T]:
        return self._state_mgr.authored_app_context_ref(key)

    def current_generation_id(self) -> int:
        return self._state_mgr.current_generation_id()

    def current_slot_id(self) -> SlotId:
        return self._state_mgr.current_slot_id()

    def context_kind(self) -> ContextKind:
        return self._state_mgr.context_kind()

    def iter_children(self) -> tuple[ContextBase | SlotContext, ...]:
        return self._state_mgr.iter_children()

    def own_committed_ui(self) -> tuple[UIElement | MountDirective, ...]:
        return self._state_mgr.own_committed_ui()

    def own_committed_ui_entries(self) -> tuple[_CommittedUiEntry, ...]:
        return self._state_mgr.own_committed_ui_entries()

    def pass_scope(self) -> _PassScopeHandle:
        return self._state_mgr.pass_scope()

    def begin_pass(self) -> None:
        self._begin_scope_pass()

    def end_pass(self) -> None:
        self._commit_scope_pass()

    def rollback_pass(self) -> None:
        self._rollback_scope_pass()

    def slot_expr(
        self,
        slot_id: SlotId,
        value_lambda: Callable[..., Any],
        dirty_lambda: Callable[..., Any],
    ) -> Any:
        return self._state_mgr.slot_expr(
            slot_id,
            value_lambda,
            dirty_lambda,
            slot_context_facade=self,
        )

    def visit_slot_and_dirty(self, slot_id: SlotId) -> bool:
        return self._state_mgr.visit_slot_and_dirty(slot_id, parent_facade=self)

    def keyed_loop(
        self,
        slot_id: SlotId,
        values: list[T],
        *,
        key_fn: Callable[[T], Any],
    ) -> Any:
        return self._state_mgr.keyed_loop(slot_id, values, key_fn=key_fn, parent_facade=self)

    def container_call(
        self,
        slot_id: SlotId,
        container_fn: Callable[..., Any],
        *args: Any,
        dirty_state: DirtyStateContext | None = None,
        _pyr_param_names: tuple[str, ...] | None = None,
        _pyr_args_dirty: tuple[Any, ...] | None = None,
        _pyr_kwargs_dirty: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        return self._state_mgr.container_call(
            slot_id,
            container_fn,
            *args,
            parent_facade=self,
            dirty_state=dirty_state,
            _pyr_param_names=_pyr_param_names,
            _pyr_args_dirty=_pyr_args_dirty,
            _pyr_kwargs_dirty=_pyr_kwargs_dirty,
            **kwargs,
        )

    def open_directive(
        self,
        slot_id: SlotId,
        directive_fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return self._state_mgr.open_directive(
            slot_id,
            directive_fn,
            *args,
            parent_facade=self,
            **kwargs,
        )

    def open_app_context_override(
        self,
        slot_id: SlotId,
        keys: tuple[AppContextKey[Any], ...],
        *values: Any,
    ) -> Any:
        return self._state_mgr.open_app_context_override(
            slot_id,
            keys,
            *values,
            parent_facade=self,
        )

    def component_call(
        self,
        slot_id: SlotId,
        component: Callable[..., Any],
        *args: Any,
        dirty_state: DirtyStateContext | None = None,
        _pyr_param_names: tuple[str, ...] | None = None,
        _pyr_args_dirty: tuple[Any, ...] | None = None,
        _pyr_kwargs_dirty: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        return self._state_mgr.component_call(
            slot_id,
            component,
            *args,
            parent_facade=self,
            dirty_state=dirty_state,
            _pyr_param_names=_pyr_param_names,
            _pyr_args_dirty=_pyr_args_dirty,
            _pyr_kwargs_dirty=_pyr_kwargs_dirty,
            **kwargs,
        )

    def event_handler(
        self,
        slot_id: SlotId,
        *,
        dirty: bool,
        callback: Callable[..., Any],
    ) -> Any:
        return self._state_mgr.event_handler(
            slot_id,
            dirty=dirty,
            callback=callback,
            parent_facade=self,
        )

    def event_handler_binding(
        self,
        slot_id: SlotId,
        *,
        dirty: bool,
        callback: Callable[..., Any],
    ) -> Any:
        return self._state_mgr.event_handler_binding(slot_id, dirty=dirty, callback=callback)

    def call_native(self, factory: Callable[..., UIElement | None], *args: Any, **kwargs: Any) -> Any:
        return self._state_mgr.call_native(factory, *args, __pyr_context_facade=self, **kwargs)

    def _effective_authored_app_context_lookup(self) -> AppContextLookup:
        return self._state_mgr.effective_authored_app_context_lookup()


class SlotContext(_StateDelegatingObject):
    _state_mgr_cls = SlotContextStateMgr
    _context_kind = ContextKind.SLOT
    render_context: RenderContext
    parent: ContextBase
    slot_id: SlotId
    invoke_dirty: bool
    seen_in_pass: bool

    def __init__(
        self,
        render_context: RenderContext,
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        self._init_state_mgr(
            render_context_state_mgr=render_context._state_mgr,
            parent_state_mgr=parent._state_mgr,
            slot_id=slot_id,
            invoke_dirty=invoke_dirty,
            seen_in_pass=seen_in_pass,
        )

    @property
    def render_context(self) -> RenderContext:
        return self._state_mgr._render_context_state_mgr.owner

    @render_context.setter
    def render_context(self, value: RenderContext) -> None:
        self._state_mgr._render_context_state_mgr = value._state_mgr

    @property
    def parent(self) -> ContextBase:
        return self._state_mgr._parent_state_mgr.owner

    @parent.setter
    def parent(self, value: ContextBase) -> None:
        self._state_mgr._parent_state_mgr = value._state_mgr

    @property
    def slot_id(self) -> SlotId:
        return self._state_mgr._slot_id

    @slot_id.setter
    def slot_id(self, value: SlotId) -> None:
        self._state_mgr._slot_id = value

    @property
    def invoke_dirty(self) -> bool:
        return self._state_mgr._invoke_dirty

    @invoke_dirty.setter
    def invoke_dirty(self, value: bool) -> None:
        self._state_mgr._invoke_dirty = value

    @property
    def seen_in_pass(self) -> bool:
        return self._state_mgr._seen_in_pass

    @seen_in_pass.setter
    def seen_in_pass(self, value: bool) -> None:
        self._state_mgr._seen_in_pass = value

    @property
    def site_metadata(self) -> tuple[RuntimeSiteMetadata[Any], ...]:
        return self._state_mgr._site_metadata

    @site_metadata.setter
    def site_metadata(self, value: tuple[RuntimeSiteMetadata[Any], ...]) -> None:
        self._state_mgr._site_metadata = value

    def current_slot_id(self) -> SlotId:
        return self._state_mgr.current_slot_id()

    def current_generation_id(self) -> int:
        return self._state_mgr.current_generation_id()

    def context_kind(self) -> ContextKind:
        return self._state_mgr.context_kind()

    def visit_self_and_dirty(self) -> bool:
        return self._state_mgr.visit_self_and_dirty()

    def deactivate(self) -> None:
        self._state_mgr.deactivate()


class EventHandlerSlotContext(SlotContext):
    _state_mgr_cls = EventHandlerSlotContextStateMgr
    _context_kind = ContextKind.EVENT_HANDLER

    def __init__(
        self,
        render_context: RenderContext,
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)

    @property
    def committed_callback(self) -> Callable[..., Any] | None:
        return self._state_mgr._committed_callback

    @property
    def committed_key(self) -> object | None:
        return self._state_mgr._committed_key

    @property
    def staged_callback(self) -> Callable[..., Any] | None:
        return self._state_mgr._staged_callback

    @property
    def staged_key(self) -> object | None:
        return self._state_mgr._staged_key

    @property
    def dispatch(self) -> Callable[..., None] | None:
        return self._state_mgr._dispatch

    def stage_callback(
        self,
        *,
        callback: Callable[..., Any],
        dirty: bool,
    ) -> Callable[..., None]:
        return self._state_mgr.stage_callback(callback=callback, dirty=dirty)

    def commit_handler(self) -> None:
        self._state_mgr.commit_handler()

    def rollback_handler(self) -> None:
        self._state_mgr.rollback_handler()

    def deactivate(self) -> None:
        self._state_mgr.deactivate()


class RerunnableSlotContext(SlotContext, ContextBase):
    _state_mgr_cls = RerunnableSlotContextStateMgr

    def __init__(
        self,
        render_context: RenderContext,
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        SlotContext.__init__(self, render_context, parent, slot_id, invoke_dirty, seen_in_pass)


class SlotExprSlotContext(RerunnableSlotContext):
    _state_mgr_cls = SlotExprSlotContextStateMgr

    def __init__(
        self,
        render_context: RenderContext,
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)

    @property
    def call_site_context_manager(self) -> CallSiteContextManager:
        return self._state_mgr._call_site_context_manager

    @TESTING_ONLY
    def _runtime_locals_by_slot_id(self) -> dict[Any, dict[str, Any]]:
        return self._state_mgr._runtime_locals_by_slot_id

    @TESTING_ONLY
    def _staged_call_site_ids(self) -> tuple[Any, ...]:
        return self._state_mgr._staged_call_site_ids

    @TESTING_ONLY
    def _staged_post_commit_callbacks(self) -> tuple[Callable[[], None], ...]:
        return self._state_mgr._staged_post_commit_callbacks

    def runtime_locals(self, slot_id: Any) -> dict[str, Any]:
        return self._state_mgr.runtime_locals(slot_id)

    def stage_slot_expr_pass(
        self,
        *,
        visited_call_site_ids: tuple[Any, ...],
        post_commit_callbacks: tuple[Callable[[], None], ...],
    ) -> None:
        self._state_mgr.stage_slot_expr_pass(
            visited_call_site_ids=visited_call_site_ids,
            post_commit_callbacks=post_commit_callbacks,
        )

    def append_slot_expr_post_commit_callback(self, callback: Callable[[], None]) -> None:
        self._state_mgr.append_slot_expr_post_commit_callback(callback)

    def commit_binding(self) -> None:
        self._state_mgr.commit_binding()

    def rollback_binding(self) -> None:
        self._state_mgr.rollback_binding()

    def sync_committed_ui(self) -> None:
        self._state_mgr.sync_committed_ui()

    def deactivate(self) -> None:
        self._state_mgr.deactivate()


class SlotCallSlotContext(RerunnableSlotContext):
    _state_mgr_cls = SlotCallSlotContextStateMgr
    _context_kind = ContextKind.SLOT_CALL
    _slot_call_result_cls = _SlotCallResult
    _slot_runtime_context_cls = SlotRuntimeContext

    def __init__(
        self,
        render_context: RenderContext,
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)

    @property
    def function_identity(self) -> Any:
        return self._state_mgr._function_identity

    @property
    def schema(self) -> tuple[int, tuple[str, ...]]:
        return self._state_mgr._schema

    @property
    def last_args(self) -> tuple[Any, ...]:
        return self._state_mgr._last_args

    @property
    def last_kwargs(self) -> tuple[tuple[str, Any], ...]:
        return self._state_mgr._last_kwargs

    @property
    def binding(self) -> SlotCallBinding | None:
        return self._state_mgr._binding

    @property
    def site_metadata(self) -> tuple[RuntimeSiteMetadata[Any], ...]:
        return self._state_mgr._site_metadata

    @property
    def _runtime_locals(self) -> dict[str, Any]:
        return self._state_mgr._runtime_locals

    def evaluate(
        self,
        func: Callable[..., T],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        result_shape: object | None = None,
    ) -> Any:
        return self._state_mgr.evaluate(
            func,
            args,
            kwargs,
            result_shape=result_shape,
            host=self,
            runtime_context_factory=lambda: self._slot_runtime_context_cls(self),
        )

    def queue_slot_call_invalidation(self) -> None:
        self._state_mgr.queue_slot_call_invalidation(self)

    def mark_slot_call_refresh_only(self) -> None:
        self._state_mgr.queue_slot_call_invalidation(self)

    def enqueue_slot_call_post_commit(self, callback: Callable[[], None]) -> None:
        self._state_mgr.enqueue_slot_call_post_commit(callback)

    def publish_slot_call_mount_advertisement(
        self,
        request: PyrolyzeMountAdvertisementRequest,
    ) -> PyrolyzeMountAdvertisement:
        return self._state_mgr.publish_slot_call_mount_advertisement(request, host=self)

    def withdraw_slot_call_mount_advertisement(self) -> None:
        self._state_mgr.withdraw_slot_call_mount_advertisement()

    def _mark_binding_dirty(self) -> None:
        self._state_mgr.queue_slot_call_invalidation(self)

    def commit_binding(self) -> None:
        self._state_mgr.commit_binding()

    def rollback_binding(self) -> None:
        self._state_mgr.rollback_binding()

    def deactivate(self) -> None:
        self._state_mgr.deactivate()

    def _resolve_runtime_site_call(
        self,
        func: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> tuple[Any | None, tuple[Any, ...], dict[str, Any], tuple[RuntimeSiteMetadata[Any], ...]]:
        return self._state_mgr.resolve_runtime_site_call(func, args, kwargs, host=self)

    def _prepare_slot_call(
        self,
        func: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        return self._state_mgr.prepare_slot_call(func, args, kwargs)

    def _should_invoke_slot_call(self, prepared: Any) -> bool:
        return self._state_mgr.should_invoke_slot_call(prepared)

    def _call_with_optional_runtime_context(self, prepared: Any) -> Any:
        return self._state_mgr.call_with_optional_runtime_context(
            prepared,
            runtime_context_factory=lambda: self._slot_runtime_context_cls(self),
        )

    def _commit_slot_call_invocation(self, prepared: Any, result: Any) -> dict[str, Any]:
        return self._state_mgr.commit_slot_call_invocation(self, prepared, result)

    def _refresh_slot_call_binding(self, binding: SlotCallBinding) -> tuple[Any, bool] | None:
        return self._state_mgr.refresh_slot_call_binding(binding)

    def _project_dirty_state(self, dirty: bool, result_shape: object | None) -> Any:
        return self._state_mgr.project_dirty_state(dirty, result_shape)

    def _build_committed_ui(self) -> tuple[object, ...]:
        return self._state_mgr.build_committed_ui()

    def _sync_binding_committed_ui(self) -> None:
        self._state_mgr.sync_binding_committed_ui()


class DirectiveSlotContext(SlotCallSlotContext):
    _state_mgr_cls = DirectiveSlotContextStateMgr

    def __init__(
        self,
        render_context: RenderContext,
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)

    @property
    def committed_selectors(self) -> tuple[SlotSelector, ...]:
        return self._state_mgr._committed_selectors

    def evaluate_directive(
        self,
        directive_fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> tuple[SlotSelector, ...]:
        return self._state_mgr.evaluate_directive(
            directive_fn,
            args,
            kwargs,
            host=self,
            runtime_context_factory=lambda: self._slot_runtime_context_cls(self),
        )

    def pending_selectors(self) -> tuple[SlotSelector, ...]:
        return self._state_mgr.pending_selectors()

    def has_pending_emitted_children(self) -> bool:
        return self._state_mgr.has_pending_emitted_children()

    def _begin_scope_pass(self) -> None:
        self._state_mgr.begin_scope_pass()

    def _commit_scope_pass(self) -> None:
        self._state_mgr.commit_scope_pass()

    def _rollback_scope_pass(self) -> None:
        self._state_mgr.rollback_scope_pass()

    def _build_committed_ui(self) -> tuple[MountDirective, ...]:
        return self._state_mgr.build_committed_ui()


class AppContextOverrideSlotContext(RerunnableSlotContext):
    _state_mgr_cls = AppContextOverrideSlotContextStateMgr
    _context_kind = ContextKind.APP_CONTEXT_OVERRIDE
    _structure_error_cls = AppContextOverrideStructureError

    def __init__(
        self,
        render_context: RenderContext,
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)

    @TESTING_ONLY
    def committed_values(self) -> tuple[Any, ...]:
        return self._state_mgr._committed_values

    @TESTING_ONLY
    def _committed_key_states(self) -> dict[Any, Any]:
        return self._state_mgr._committed_key_states

    @TESTING_ONLY
    def _pending_values(self) -> tuple[Any, ...]:
        return self._state_mgr._pending_values

    @TESTING_ONLY
    def _pending_initialized(self) -> bool:
        return self._state_mgr._pending_initialized

    def stage_override(
        self,
        keys: tuple[AppContextKey[Any], ...],
        values: tuple[Any, ...],
    ) -> None:
        self._state_mgr.stage_override(keys, values)

    def _effective_authored_app_context_lookup(self) -> AppContextLookup:
        return self._state_mgr.effective_authored_app_context_lookup()

    def _begin_scope_pass(self) -> None:
        self._state_mgr.begin_scope_pass()

    def _commit_scope_pass(self) -> None:
        self._state_mgr.commit_scope_pass()

    def _rollback_scope_pass(self) -> None:
        self._state_mgr.rollback_scope_pass()

    def deactivate(self) -> None:
        self._state_mgr.deactivate()


class ContainerSlotContext(RerunnableSlotContext):
    _state_mgr_cls = ContainerSlotContextStateMgr
    _context_kind = ContextKind.CONTAINER

    def __init__(
        self,
        render_context: RenderContext,
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)

    @property
    def expects_native_root(self) -> bool:
        return self._state_mgr._expects_native_root

    @expects_native_root.setter
    def expects_native_root(self, value: bool) -> None:
        self._state_mgr._expects_native_root = value

    @property
    def committed_native_root(self) -> bool:
        return self._state_mgr._committed_native_root

    @committed_native_root.setter
    def committed_native_root(self, value: bool) -> None:
        self._state_mgr._committed_native_root = value


class ComponentCallSlotContext(RerunnableSlotContext):
    _state_mgr_cls = ComponentCallSlotContextStateMgr
    _context_kind = ContextKind.COMPONENT_CALL

    def __init__(
        self,
        render_context: RenderContext,
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)

    @property
    def child_context(self) -> RenderContext | None:
        child_state_mgr = self._state_mgr._child_context_state_mgr
        return None if child_state_mgr is None else child_state_mgr.owner

    def invoke(
        self,
        component: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        dirty_state: DirtyStateContext | None = None,
        _pyr_param_names: tuple[str, ...] | None = None,
        _pyr_args_dirty: tuple[Any, ...] | None = None,
        _pyr_kwargs_dirty: dict[str, Any] | None = None,
    ) -> Any:
        return self._state_mgr.invoke(
            component,
            args,
            kwargs,
            owner_slot_facade=self,
            scheduler_root_facade=self.render_context._state_mgr._scheduler_root_state_mgr.owner,
            render_context_factory=type(self.render_context),
            dirty_state=dirty_state,
            _pyr_param_names=_pyr_param_names,
            _pyr_args_dirty=_pyr_args_dirty,
            _pyr_kwargs_dirty=_pyr_kwargs_dirty,
        )

    def commit_owned_event_handlers(self) -> None:
        self._state_mgr.commit_owned_event_handlers()

    def rollback_owned_event_handlers(self) -> None:
        self._state_mgr.rollback_owned_event_handlers()

    def deactivate(self) -> None:
        self._state_mgr.deactivate()


class KeyedLoopSlotContext(RerunnableSlotContext):
    _state_mgr_cls = KeyedLoopSlotContextStateMgr
    _context_kind = ContextKind.KEYED_LOOP


class LoopItemSlotContext(RerunnableSlotContext):
    _state_mgr_cls = LoopItemSlotContextStateMgr
    _context_kind = ContextKind.LOOP_ITEM

    def current_value(self) -> Any:
        return self._state_mgr.current_value()

    def update_current(self, value: Any) -> None:
        self._state_mgr.update_current(value)


class LeafSlotContext(RerunnableSlotContext):
    _state_mgr_cls = LeafSlotContextStateMgr
    _context_kind = ContextKind.LEAF

    def __init__(
        self,
        render_context: RenderContext,
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)

    @property
    def last_args(self) -> tuple[Any, ...]:
        return self._state_mgr._last_args

    @property
    def last_kwargs(self) -> tuple[tuple[str, Any], ...]:
        return self._state_mgr._last_kwargs

    def invoke(self, leaf_fn: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
        return self._state_mgr.invoke(leaf_fn, args, kwargs)

    def invoke_native(
        self,
        leaf_fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        context_param: str,
    ) -> Any:
        return self._state_mgr.invoke_native(
            leaf_fn,
            args,
            kwargs,
            context_param=context_param,
            context_facade=self,
        )


class RenderContext(ContextBase):
    _state_mgr_cls = RenderContextStateMgr
    _context_kind_cls = ContextKind
    _mount_advertisement_cls = PyrolyzeMountAdvertisement

    @staticmethod
    def _scheduler_factory() -> _InvalidationScheduler:
        return _InvalidationScheduler()

    def __init__(
        self,
        *,
        owner_slot: ComponentCallSlotContext | None = None,
        scheduler_root: RenderContext | None = None,
        app_context_store: AppContextStore | None = None,
        authored_app_context_lookup: AppContextLookup | None = None,
    ) -> None:
        self._init_state_mgr(
            owner_slot_state_mgr=(None if owner_slot is None else owner_slot._state_mgr),
            scheduler_root_state_mgr=(None if scheduler_root is None else scheduler_root._state_mgr),
            app_context_store=(app_context_store or AppContextStore()) if scheduler_root is None else None,
            authored_app_context_lookup=(
                (authored_app_context_lookup or EMPTY_APP_CONTEXT_LOOKUP)
                if scheduler_root is None
                else authored_app_context_lookup
            ),
        )

    @TESTING_ONLY
    def _slots_by_id(self) -> dict[SlotId, SlotContext]:
        return {
            slot_id: slot_state_mgr.owner
            for slot_id, slot_state_mgr in self._state_mgr._slots_by_id.items()
        }

    @TESTING_ONLY
    def _queued_invalidations(self) -> list[object]:
        return [
            queued.owner if hasattr(queued, "owner") else queued
            for queued in self._state_mgr._queued_invalidations
        ]

    @TESTING_ONLY
    def _post_commit_callbacks(self) -> list[Callable[[], None]]:
        return list(self._state_mgr._post_commit_callbacks)

    @TESTING_ONLY
    def _scheduler_root(self) -> RenderContext:
        return self._state_mgr._scheduler_root_state_mgr.owner

    @TESTING_ONLY
    def _app_context_store(self) -> AppContextStore:
        return self._state_mgr._app_context_store

    @TESTING_ONLY
    def _authored_app_context_lookup(self) -> AppContextLookup:
        return self._state_mgr._authored_app_context_lookup

    @TESTING_ONLY
    def _owner_slot(self) -> ComponentCallSlotContext | None:
        owner_slot_state_mgr = self._state_mgr._owner_slot_state_mgr
        return None if owner_slot_state_mgr is None else owner_slot_state_mgr.owner

    def pass_scope(self) -> _PassScopeHandle:
        return self._state_mgr.pass_scope()

    def mount(self, callback: Callable[[], None]) -> None:
        self._state_mgr.mount(self, callback)

    def set_flush_poster(self, post: Callable[[Callable[[], None]], None]) -> None:
        self._state_mgr.set_flush_poster(post)

    def run_pending_invalidations(self) -> None:
        self._state_mgr.run_pending_invalidations()

    def _run_boundary(self) -> None:
        self._state_mgr._run_boundary(self)

    def begin_pass(self) -> None:
        self._state_mgr.begin_pass()

    def end_pass(self) -> None:
        self._state_mgr.end_pass()

    def rollback_pass(self) -> None:
        self._state_mgr.rollback_pass()

    def debug_children_of(self, slot_id: SlotId | None = None) -> tuple[SlotId, ...]:
        return self._state_mgr.debug_children_of(slot_id)

    def debug_is_active(self, slot_id: SlotId) -> bool:
        return self._state_mgr.debug_is_active(slot_id)

    def debug_pending_boundaries(self) -> tuple[SlotId | None, ...]:
        return self._state_mgr.debug_pending_boundaries()

    def debug_mount_advertisements(self) -> tuple[PyrolyzeMountAdvertisement, ...]:
        return self._state_mgr.debug_mount_advertisements()

    def debug_ui(self, slot_id: SlotId | None = None) -> tuple[UIElement | MountDirective, ...]:
        return self._state_mgr.debug_ui(slot_id)

    def committed_ui(self) -> tuple[UIElement | MountDirective, ...]:
        return self._state_mgr.committed_ui()

    def _refresh_committed_ui_from_children(self) -> None:
        self._state_mgr.refresh_committed_ui_from_children()

    def walk_context_graph(self, listener: object) -> None:
        self._state_mgr.walk_context_graph(self, listener)

    def close_app_contexts(self) -> None:
        self._state_mgr.close_app_contexts()

    def _debug_boundary_id(self) -> SlotId | None:
        return self._state_mgr._debug_boundary_id()

    def _is_ancestor_boundary_of(self, other: RenderContext) -> bool:
        return self._state_mgr._is_ancestor_boundary_of(other)

    def _remove_from_scheduler(self) -> None:
        self._state_mgr._remove_from_scheduler(self)

    def _flush_post_commit(self) -> None:
        self._state_mgr._flush_post_commit()

    def _post_flush_if_needed(self, *, was_pending: bool) -> None:
        self._state_mgr._post_flush_if_needed(was_pending=was_pending)

    def _rebuild_mount_advertisement_surface(self) -> None:
        self._state_mgr._rebuild_mount_advertisement_surface()

    def _queue_invalidation_from(self, slot: object, *, include_source: bool = True) -> None:
        self._state_mgr.queue_invalidation_from(slot, include_source=include_source)

    def _enqueue_post_commit(self, callback: Callable[[], None]) -> None:
        self._state_mgr.enqueue_post_commit(callback)

    def _publish_mount_advertisement(
        self,
        slot: SlotCallSlotContext,
        request: PyrolyzeMountAdvertisementRequest,
    ) -> PyrolyzeMountAdvertisement:
        return self._state_mgr.publish_mount_advertisement(slot, request)

    def _withdraw_mount_advertisement(self, slot_id: SlotId) -> None:
        self._state_mgr.withdraw_mount_advertisement(slot_id)

_support.REFRACTOR_CLASSES.context_base_cls = ContextBase
_support.REFRACTOR_CLASSES.render_context_cls = RenderContext
_support.REFRACTOR_CLASSES.slot_context_cls = SlotContext
_support.REFRACTOR_CLASSES.event_handler_slot_context_cls = EventHandlerSlotContext
_support.REFRACTOR_CLASSES.slot_expr_slot_context_cls = SlotExprSlotContext
_support.REFRACTOR_CLASSES.slot_call_slot_context_cls = SlotCallSlotContext
_support.REFRACTOR_CLASSES.directive_slot_context_cls = DirectiveSlotContext
_support.REFRACTOR_CLASSES.app_context_override_slot_context_cls = AppContextOverrideSlotContext
_support.REFRACTOR_CLASSES.container_slot_context_cls = ContainerSlotContext
_support.REFRACTOR_CLASSES.component_call_slot_context_cls = ComponentCallSlotContext
_support.REFRACTOR_CLASSES.keyed_loop_slot_context_cls = KeyedLoopSlotContext
_support.REFRACTOR_CLASSES.loop_item_slot_context_cls = LoopItemSlotContext


__all__ = [
    "AppContextKey",
    "AppContextLookup",
    "AppContextOverrideSlotContext",
    "AppContextOverrideStructureError",
    "AppContextStore",
    "ComponentCallSlotContext",
    "ContainerCallRuntimeContext",
    "ContainerSlotContext",
    "ContextBase",
    "DirtyStateContext",
    "DuplicateKeyError",
    "DuplicateMountAdvertisementError",
    "EventHandlerSlotContext",
    "ExternalStoreBinding",
    "ExternalStoreRef",
    "KeyedLoopSlotContext",
    "LeafSlotContext",
    "LoopItemSlotContext",
    "ModuleId",
    "ModuleRegistry",
    "MountAdvertisementContextError",
    "PyrolyzeMountAdvertisementBinding",
    RenderContext,
    "RerunnableSlotContext",
    "SlotCallSlotContext",
    "SlotContext",
    "SlotExprSlotContext",
    "SlotId",
    "SlotIdPath",
    "SlotOwnershipError",
    "SlotRuntimeContext",
    "SlotValueBinding",
    "UseEffectAsyncBinding",
    "UseEffectAsyncRequest",
    "UseEffectBinding",
    "UseEffectRequest",
    "dirtyof",
    "dirtyof_values",
    "module_registry",
]
