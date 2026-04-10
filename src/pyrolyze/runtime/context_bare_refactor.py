"""Non-functional public API contract refactored around per-class state managers."""

from __future__ import annotations

__PYROLYZE_CONTEXT_IMPLEMENTATION__ = "bare"

import inspect
import logging
import os
from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Iterator, TypeVar, cast

from pyrolyze.api import (
    MountDirective,
    PyrolyzeMountAdvertisement,
    PyrolyzeMountAdvertisementRequest,
    SlotSelector,
    UIElement,
)

from .app_context import (
    APP_CONTEXT_MISSING,
    EMPTY_APP_CONTEXT_LOOKUP,
    GENERATION_TRACKER_KEY,
    AppContextKey,
    AppContextLookup,
    AppContextStore,
)
from .call_site_context import CallSiteContextManager
from .context_state import _support
from .context_state import (
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
from .function_arg_helpers import build_function_arg_dirty_map, pack_function_args
from .pyro_call import RuntimeSiteMetadata, resolve_runtime_pyro_call
from .slot_expr import SlotExprLiteralContext
from .slot_call_core import (
    SlotCallStateSnapshot,
    call_with_optional_runtime_context,
    commit_slot_call_invocation,
    prepare_slot_call,
    refresh_slot_call_binding,
    runtime_context_param_name,
    should_invoke_slot_call,
)
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
from .trace import TraceChannel, emit_trace, trace_enabled


T = TypeVar("T")


def _unavailable() -> None:
    raise NotImplementedError("context_bare_refactor is an interface-only scaffold")


class _StateDelegatingObject:
    _state_mgr_cls = ContextBaseStateMgr
    _state_mgr: Any
    _context_kind = ContextKind.SLOT

    def _init_state_mgr(self) -> None:
        self._state_mgr = self._state_mgr_cls(self)

    def _delegate(self, name: str, *args: Any, **kwargs: Any) -> Any:
        return getattr(self._state_mgr, name)(*args, **kwargs)

    def get_kind(self) -> ContextKind:
        return type(self)._context_kind


@dataclass(frozen=True, slots=True)
class DirtyStateContext:
    values: dict[str, bool]

    def get(self, name: str, default: bool = False) -> bool:
        return bool(self.values.get(name, default))

    def __getattr__(self, name: str) -> bool:
        return self.get(name)


def dirtyof(**values: bool) -> DirtyStateContext:
    return DirtyStateContext(values={key: bool(value) for key, value in values.items()})


def dirtyof_values(values: dict[str, Any]) -> DirtyStateContext:
    return DirtyStateContext(values={key: bool(value) for key, value in values.items()})


class SlotOwnershipError(RuntimeError):
    """Raised when a slot is visited through a context that does not own it."""


class DuplicateKeyError(RuntimeError):
    """Raised when a keyed loop encounters the same key more than once in one pass."""


class DuplicateMountAdvertisementError(RuntimeError):
    """Raised when one mount advert surface publishes an illegal public shape."""


class MountAdvertisementContextError(RuntimeError):
    """Raised when an advert is published outside a valid structural container."""


class AppContextOverrideStructureError(RuntimeError):
    """Raised when one retained app-context provider changes its fixed structure."""


@dataclass(frozen=True, slots=True)
class _SlotCallResult:
    dirty: Any
    value: Any

    def __iter__(self) -> Any:
        yield self.dirty
        yield self.value


@dataclass(frozen=True, slots=True)
class PendingEventHandlerBinding:
    slot_id: SlotId
    dirty: bool
    callback: Callable[..., Any]


@dataclass(frozen=True, slots=True)
class _CommittedUiEntry:
    generation_id: int
    element: UIElement | MountDirective


@dataclass(frozen=True, slots=True)
class SlotRuntimeContext:
    slot: "SlotCallSlotContext"

    def get_or_init_local(self, key: str, factory: Callable[[], T]) -> T:
        locals_map = self.slot._runtime_locals
        if key not in locals_map:
            locals_map[key] = factory()
        return cast(T, locals_map[key])

    def get_local(self, key: str, default: object | None = None) -> object | None:
        return self.slot._runtime_locals.get(key, default)

    def set_local(self, key: str, value: object) -> None:
        self.slot._runtime_locals[key] = value

    def invalidate(self) -> None:
        self.slot._mark_binding_dirty()

    def stable_local_id(self, key: str) -> tuple[SlotId, str]:
        return (self.slot.slot_id, key)

    def get_app_context(self, key: AppContextKey[T]) -> T:
        return self.slot.root_context._scheduler_root._app_context_store.get(key)

    def has_app_context(self, key: AppContextKey[Any]) -> bool:
        return self.slot.root_context._scheduler_root._app_context_store.has(key)

    def get_authored_app_context(self, key: AppContextKey[T]) -> T:
        return self.slot.get_authored_app_context(key)

    def has_authored_app_context(self, key: AppContextKey[Any]) -> bool:
        return self.slot.has_authored_app_context(key)

    def authored_app_context_ref(self, key: AppContextKey[T]) -> ExternalStoreRef[T]:
        return self.slot.authored_app_context_ref(key)

    def current_generation_id(self) -> int:
        tracker = self.get_app_context(GENERATION_TRACKER_KEY)
        return tracker.current()

    def current_slot_id(self) -> SlotId:
        return self.slot.slot_id


class ContainerCallRuntimeContext:
    slot: "DirectiveSlotContext"

    def __init__(self, slot: "DirectiveSlotContext") -> None:
        self.slot = slot

    def open_directive(self, *selectors: SlotSelector) -> Any:
        return _DirectiveCallHandle(
            slot=self.slot,
            directive_fn=_support.validate_mount_selectors,
            args=selectors,
            kwargs={},
        )


@dataclass(slots=True)
class _SlotExprHostSlotProxy:
    slot_id: SlotId
    parent: "ContextBase | None"
    render_context: "RenderContext"
    invoke_dirty: bool = False


@dataclass(slots=True)
class _ContextSlotExprHost:
    owner: "ContextBase"
    slot_id: SlotId
    _proxy: _SlotExprHostSlotProxy = field(init=False)

    def __post_init__(self) -> None:
        render_context = self.owner if isinstance(self.owner, RenderContext) else self.owner.root_context
        parent = None if isinstance(self.owner, RenderContext) else self.owner
        self._proxy = _SlotExprHostSlotProxy(
            slot_id=self.slot_id,
            parent=parent,
            render_context=render_context,
        )

    def queue_slot_call_invalidation(self) -> None:
        self._proxy.render_context._queue_invalidation_from(self._proxy, include_source=False)

    def mark_slot_call_refresh_only(self) -> None:
        self.queue_slot_call_invalidation()

    def enqueue_slot_call_post_commit(self, callback: Callable[[], None]) -> None:
        self._proxy.render_context._enqueue_post_commit(callback)

    def publish_slot_call_mount_advertisement(
        self,
        request: PyrolyzeMountAdvertisementRequest,
    ) -> PyrolyzeMountAdvertisement:
        return self._proxy.render_context._publish_mount_advertisement(self._proxy, request)

    def withdraw_slot_call_mount_advertisement(self) -> None:
        self._proxy.render_context._withdraw_mount_advertisement(self.slot_id)


def _dirty_state_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, tuple):
        return any(_dirty_state_truthy(item) for item in value)
    return bool(value)


def _unwrap(value: _SlotCallResult | Any) -> tuple[Any, bool]:
    if isinstance(value, _SlotCallResult):
        return value.value, _dirty_state_truthy(value.dirty)
    return value, False


def _project_dirty_state(dirty: bool, result_shape: object | None) -> Any:
    if result_shape is None:
        return dirty
    if isinstance(result_shape, tuple):
        return tuple(_project_dirty_state(dirty, item) for item in result_shape)
    return dirty


def _slot_site_path(node: object) -> SlotIdPath:
    slot_id = getattr(node, "slot_id", None)
    if not isinstance(slot_id, SlotId):
        return SlotIdPath.empty()
    parent = getattr(node, "parent", None)
    if isinstance(parent, ContextBase):
        parent_path = _native_emission_slot_identity(parent)
        if parent_path is not None:
            return parent_path.child(slot_id)
    return SlotIdPath((slot_id,))


def _resolve_runtime_site_call(
    node: object,
    func: Any,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> tuple[Any | None, tuple[Any, ...], dict[str, Any], tuple[RuntimeSiteMetadata[Any], ...]]:
    raw_func, _ = _unwrap(func)
    raw_args = tuple(_unwrap(arg)[0] for arg in args)
    raw_kwargs = {key: _unwrap(value)[0] for key, value in kwargs.items()}
    resolved = resolve_runtime_pyro_call(
        raw_func,
        raw_args,
        raw_kwargs,
        slot_path=_slot_site_path(node),
    )
    return resolved.func, tuple(resolved.args), dict(resolved.kwargs), tuple(resolved.metadata)


def _unwrap_native_value(value: Any) -> Any:
    if isinstance(value, _SlotCallResult):
        return _unwrap_native_value(value.value)
    if isinstance(value, dict):
        return {key: _unwrap_native_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_unwrap_native_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_unwrap_native_value(item) for item in value)
    return value


_NATIVE_CONTEXT_ANNOTATIONS = {
    "ContextBase",
    "ContainerSlotContext",
    "LeafSlotContext",
    "RenderContext",
}


def _native_context_param_name(func: Callable[..., Any]) -> str | None:
    found_name: str | None = None
    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):
        return None
    parameters = tuple(signature.parameters.values())
    if not parameters:
        return None
    first = parameters[0]
    annotation = first.annotation
    annotation_name = getattr(annotation, "__forward_arg__", annotation)
    if annotation_name in _NATIVE_CONTEXT_ANNOTATIONS:
        found_name = first.name
    elif isinstance(annotation, type) and issubclass(annotation, ContextBase):
        found_name = first.name
    return found_name


def _container_runtime_context_param_name(func: Callable[..., Any]) -> str | None:
    return runtime_context_param_name(
        func,
        cache_attr_name="_pyrolyze_container_runtime_ctx_param",
        runtime_context_annotation=ContainerCallRuntimeContext,
    )


_BOUND_METHOD_SELF_MISSING = object()


def _component_call_key(component: object) -> tuple[object, object]:
    underlying = getattr(component, "__func__", None)
    if underlying is not None:
        metadata = getattr(underlying, "_pyrolyze_meta", None)
        if metadata is not None:
            bound_self = getattr(component, "__self__", _BOUND_METHOD_SELF_MISSING)
            return metadata, bound_self

    metadata = getattr(component, "_pyrolyze_meta", None)
    if metadata is not None:
        return metadata, _BOUND_METHOD_SELF_MISSING

    return None, _BOUND_METHOD_SELF_MISSING


def _clean_dirty_state(previous: DirtyStateContext | None) -> DirtyStateContext:
    if previous is None:
        return dirtyof()
    return dirtyof(**{key: False for key in previous.values})


def _resolve_runtime_component_func(runtime_func: object) -> Callable[..., Any] | None:
    if isinstance(runtime_func, (classmethod, staticmethod)):
        candidate = runtime_func.__func__
        return candidate if callable(candidate) else None
    if callable(runtime_func):
        return cast("Callable[..., Any]", runtime_func)
    return None


def _native_emission_slot_identity(context: "ContextBase") -> SlotIdPath | None:
    current_slot_id = context.current_slot_id()
    owner_slot_path: list[SlotId] = []
    current: object | None = getattr(context, "render_context", None)
    if current is None:
        current = context
    while current is not None:
        owner_slot = getattr(current, "_owner_slot", None)
        if owner_slot is None:
            break
        slot_id = getattr(owner_slot, "slot_id", None)
        if isinstance(slot_id, SlotId):
            owner_slot_path.append(slot_id)
        current = getattr(owner_slot, "render_context", None)
    if owner_slot_path:
        owner_slot_path.reverse()
        if isinstance(current_slot_id, SlotId):
            owner_slot_path.append(current_slot_id)
        return SlotIdPath(tuple(owner_slot_path))
    if isinstance(current_slot_id, SlotId):
        return SlotIdPath((current_slot_id,))
    return None


def _bind_pending_event_plain_value(owner: "ContextBase", value: Any) -> Any:
    if isinstance(value, PendingEventHandlerBinding):
        return owner._materialize_pending_event_handler(value)
    return value


def _resolve_mount_advertisement_owner(parent: "ContextBase") -> "ContainerSlotContext | None":
    current: ContextBase | SlotContext | None = parent
    while current is not None:
        if isinstance(current, ContainerSlotContext):
            return current
        if isinstance(current, SlotContext):
            current = current.parent
            continue
        return None
    return None


@dataclass(slots=True)
class _PassScopeHandle:
    context: "ContextBase"
    activate: bool = True

    def __enter__(self) -> None:
        if self.activate:
            self.context.begin_pass()
        return None

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        if self.activate:
            if exc_type is None:
                self.context.end_pass()
            else:
                self.context.rollback_pass()
        return False


def _finish_context_pass(context: "ContextBase", *, commit: bool) -> None:
    if not commit:
        context.rollback_pass()
        return
    try:
        context.end_pass()
    except BaseException:
        if getattr(context, "_scope_active", False):
            context.rollback_pass()
        raise


class ContextBase(_StateDelegatingObject, SlotExprLiteralContext):
    _state_mgr_cls = ContextBaseStateMgr
    _pass_scope_handle_cls = _PassScopeHandle
    _generation_tracker_key_const = GENERATION_TRACKER_KEY
    _context_kind = ContextKind.SLOT
    _state_attr_names = {
        "_generation_tracker_key",
        "_render_context",
        "_children",
        "_scope_active",
        "_pass_child_order",
        "_pass_child_dirty",
        "_committed_ui",
        "_own_committed_ui",
        "_own_committed_ui_entries",
        "_pass_committed_ui",
        "_pass_own_committed_ui",
        "_pass_own_committed_ui_entries",
        "_staged_ui",
        "_staged_ui_entries",
        "_pass_committed_native_root",
    }
    render_context: "RenderContext"

    def __getattr__(self, name: str) -> Any:
        state_mgr = self.__dict__.get("_state_mgr")
        if state_mgr is not None and name in type(self)._state_attr_names:
            return getattr(state_mgr, name)
        raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        state_mgr = self.__dict__.get("_state_mgr")
        if state_mgr is not None and name in type(self)._state_attr_names:
            setattr(state_mgr, name, value)
            return
        object.__setattr__(self, name, value)

    def __init__(self, render_context: "RenderContext") -> None:
        self.render_context = render_context
        self._init_state_mgr()

    def _require_active_scope(self) -> None:
        if not self._scope_active:
            raise RuntimeError("scope is not active")

    def _begin_scope_pass(self) -> None:
        self._state_mgr.begin_pass()

    def _commit_scope_pass(self) -> None:
        self._state_mgr.end_pass()

    def _rollback_scope_pass(self) -> None:
        self._state_mgr.rollback_pass()

    def _runtime_key_path(self) -> tuple[Any, ...]:
        slot_id = getattr(self, "slot_id", None)
        if isinstance(slot_id, SlotId):
            return slot_id.key_path
        return ()

    def _resolve_slot_id(self, slot_id: SlotId) -> SlotId:
        runtime_key_path = self._runtime_key_path()
        return SlotId(
            module_id=slot_id.module_id,
            slot_index=slot_id.slot_index,
            key_path=runtime_key_path + slot_id.key_path,
            line_no=slot_id.line_no,
            is_top_level=slot_id.is_top_level,
        )

    def _ensure_slot(self, slot_id: SlotId, slot_type: type[T]) -> T:
        return self._ensure_resolved_slot(self._resolve_slot_id(slot_id), slot_type)

    def _ensure_resolved_slot(self, slot_id: SlotId, slot_type: type[T]) -> T:
        resolved_slot_id = slot_id
        existing = self.root_context._slots_by_id.get(resolved_slot_id)
        if existing is not None and existing.parent is not self:
            raise SlotOwnershipError(
                f"slot {resolved_slot_id!r} is owned by {type(existing.parent).__name__}, "
                f"not {type(self).__name__}"
            )
        if existing is not None and not isinstance(existing, slot_type):
            existing.deactivate()
            existing = None
        if existing is None:
            slot = slot_type(render_context=self.root_context, parent=self, slot_id=resolved_slot_id)
            self.root_context._slots_by_id[resolved_slot_id] = slot
            existing = slot
        self._children.pop(resolved_slot_id, None)
        self._children[resolved_slot_id] = existing
        existing.seen_in_pass = True
        return cast(T, existing)

    def _materialize_pending_event_handler(
        self,
        binding: PendingEventHandlerBinding,
    ) -> Callable[..., None]:
        slot = self._ensure_resolved_slot(binding.slot_id, EventHandlerSlotContext)
        return slot.stage_callback(callback=binding.callback, dirty=binding.dirty)

    def _build_committed_ui(self) -> tuple[UIElement | MountDirective, ...]:
        own_elements = self._own_committed_ui
        child_elements = tuple(
            element
            for child in self._children.values()
            if isinstance(child, ContextBase)
            for element in child._committed_ui
        )
        if isinstance(self, ContainerSlotContext) and (
            self.expects_native_root or self.committed_native_root
        ):
            if len(own_elements) != 1:
                raise RuntimeError("native container helpers must emit exactly one root UIElement")
            root = cast(UIElement, own_elements[0])
            if child_elements:
                root = UIElement(
                    kind=root.kind,
                    props=root.props,
                    children=child_elements,
                    call_site_id=root.call_site_id,
                    slot_id=root.slot_id,
                )
            return (root,)
        if own_elements:
            return own_elements + child_elements
        return child_elements

    def _refresh_committed_ui_from_children(self) -> None:
        self._committed_ui = self._build_committed_ui()
        parent = getattr(self, "parent", None)
        if isinstance(parent, ContextBase):
            parent._refresh_committed_ui_from_children()

    @property
    def root_context(self) -> "RenderContext":
        return self._delegate("root_context")

    def get_app_context(self, key: AppContextKey[T]) -> T:
        return self._delegate("get_app_context", key)

    def has_app_context(self, key: AppContextKey[Any]) -> bool:
        return self._delegate("has_app_context", key)

    def get_authored_app_context(self, key: AppContextKey[T]) -> T:
        return self._delegate("get_authored_app_context", key)

    def has_authored_app_context(self, key: AppContextKey[Any]) -> bool:
        return self._delegate("has_authored_app_context", key)

    def authored_app_context_ref(self, key: AppContextKey[T]) -> ExternalStoreRef[T]:
        return self._delegate("authored_app_context_ref", key)

    def current_generation_id(self) -> int:
        return self._delegate("current_generation_id")

    def current_slot_id(self) -> SlotId:
        return self._delegate("current_slot_id")

    def context_kind(self) -> ContextKind:
        return self._delegate("context_kind")

    def pass_scope(self) -> Any:
        return self._delegate("pass_scope")

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
        return self._delegate("slot_expr", slot_id, value_lambda, dirty_lambda)

    def visit_slot_and_dirty(self, slot_id: SlotId) -> bool:
        return self._delegate("visit_slot_and_dirty", slot_id)

    def keyed_loop(
        self,
        slot_id: SlotId,
        values: list[T],
        *,
        key_fn: Callable[[T], Any],
    ) -> Any:
        return self._delegate("keyed_loop", slot_id, values, key_fn=key_fn)

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
        return self._delegate(
            "container_call",
            slot_id,
            container_fn,
            *args,
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
        return self._delegate("open_directive", slot_id, directive_fn, *args, **kwargs)

    def open_app_context_override(
        self,
        slot_id: SlotId,
        keys: tuple[AppContextKey[Any], ...],
        *values: Any,
    ) -> Any:
        return self._delegate("open_app_context_override", slot_id, keys, *values)

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
        return self._delegate(
            "component_call",
            slot_id,
            component,
            *args,
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
        return self._delegate("event_handler", slot_id, dirty=dirty, callback=callback)

    def event_handler_binding(
        self,
        slot_id: SlotId,
        *,
        dirty: bool,
        callback: Callable[..., Any],
    ) -> Any:
        return self._delegate("event_handler_binding", slot_id, dirty=dirty, callback=callback)

    def call_native(self, factory: Callable[..., UIElement | None], *args: Any, **kwargs: Any) -> Any:
        return self._delegate("call_native", factory, *args, **kwargs)

    def _effective_authored_app_context_lookup(self) -> AppContextLookup:
        parent = getattr(self, "parent", None)
        if isinstance(parent, ContextBase):
            return parent._effective_authored_app_context_lookup()
        if isinstance(self, RenderContext):
            return self._authored_app_context_lookup
        return EMPTY_APP_CONTEXT_LOOKUP


class SlotContext(_StateDelegatingObject):
    _state_mgr_cls = SlotContextStateMgr
    _context_kind = ContextKind.SLOT
    render_context: "RenderContext"
    parent: ContextBase
    slot_id: SlotId
    invoke_dirty: bool
    seen_in_pass: bool

    def __init__(
        self,
        render_context: "RenderContext",
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        self.render_context = render_context
        self.parent = parent
        self.slot_id = slot_id
        self.invoke_dirty = invoke_dirty
        self.seen_in_pass = seen_in_pass
        self._init_state_mgr()
        render_context._slots_by_id[self.slot_id] = self
        parent._children[self.slot_id] = self

    def current_slot_id(self) -> SlotId:
        return self._delegate("current_slot_id")

    def current_generation_id(self) -> int:
        return self._delegate("current_generation_id")

    def context_kind(self) -> ContextKind:
        return self._delegate("context_kind")

    def visit_self_and_dirty(self) -> bool:
        return self._delegate("visit_self_and_dirty")

    def deactivate(self) -> None:
        self._delegate("deactivate")


class EventHandlerSlotContext(SlotContext):
    _state_mgr_cls = EventHandlerSlotContextStateMgr
    _context_kind = ContextKind.EVENT_HANDLER

    def __init__(
        self,
        render_context: "RenderContext",
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)
        self.committed_callback: Callable[..., Any] | None = None
        self.committed_key: object | None = None
        self.staged_callback: Callable[..., Any] | None = None
        self.staged_key: object | None = None
        self.dispatch: Callable[..., None] | None = None

    def stage_callback(
        self,
        *,
        callback: Callable[..., Any],
        dirty: bool,
    ) -> Callable[..., None]:
        return self._delegate("stage_callback", callback=callback, dirty=dirty)

    def commit_handler(self) -> None:
        self._delegate("commit_handler")

    def rollback_handler(self) -> None:
        self._delegate("rollback_handler")

    def deactivate(self) -> None:
        self._delegate("deactivate")


class RerunnableSlotContext(SlotContext, ContextBase):
    _state_mgr_cls = RerunnableSlotContextStateMgr

    def __init__(
        self,
        render_context: "RenderContext",
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        SlotContext.__init__(self, render_context, parent, slot_id, invoke_dirty, seen_in_pass)
        self._state_mgr.__post_init__()

    def __post_init__(self) -> None:
        self._delegate("__post_init__")


class SlotExprSlotContext(RerunnableSlotContext):
    _state_mgr_cls = SlotExprSlotContextStateMgr

    def __init__(
        self,
        render_context: "RenderContext",
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)
        self.call_site_context_manager = CallSiteContextManager()
        self._runtime_locals_by_slot_id: dict[Any, dict[str, Any]] = {}
        self._staged_call_site_ids: tuple[Any, ...] = ()
        self._staged_post_commit_callbacks: tuple[Callable[[], None], ...] = ()
        self._mount_advertisement_binding_type = PyrolyzeMountAdvertisementBinding

    def runtime_locals(self, slot_id: Any) -> dict[str, Any]:
        return self._delegate("runtime_locals", slot_id)

    def stage_slot_expr_pass(
        self,
        *,
        visited_call_site_ids: tuple[Any, ...],
        post_commit_callbacks: tuple[Callable[[], None], ...],
    ) -> None:
        self._delegate(
            "stage_slot_expr_pass",
            visited_call_site_ids=visited_call_site_ids,
            post_commit_callbacks=post_commit_callbacks,
        )

    def append_slot_expr_post_commit_callback(self, callback: Callable[[], None]) -> None:
        self._delegate("append_slot_expr_post_commit_callback", callback)

    def commit_binding(self) -> None:
        self._delegate("commit_binding")

    def rollback_binding(self) -> None:
        self._delegate("rollback_binding")

    def sync_committed_ui(self) -> None:
        self._delegate("sync_committed_ui")

    def deactivate(self) -> None:
        self._delegate("deactivate")


class SlotCallSlotContext(RerunnableSlotContext):
    _state_mgr_cls = SlotCallSlotContextStateMgr
    _context_kind = ContextKind.SLOT_CALL

    def __init__(
        self,
        render_context: "RenderContext",
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)
        self.function_identity: Any = None
        self.schema: tuple[int, tuple[str, ...]] = (0, ())
        self.last_args: tuple[Any, ...] = ()
        self.last_kwargs: tuple[tuple[str, Any], ...] = ()
        self.binding: SlotCallBinding | None = None
        self.site_metadata: tuple[RuntimeSiteMetadata[Any], ...] = ()
        self._runtime_locals: dict[str, Any] = {}
        self._slot_call_result_cls = _SlotCallResult

    def evaluate(
        self,
        func: Callable[..., T],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        result_shape: object | None = None,
    ) -> Any:
        return self._delegate("evaluate", func, args, kwargs, result_shape=result_shape)

    def queue_slot_call_invalidation(self) -> None:
        self._delegate("queue_slot_call_invalidation")

    def mark_slot_call_refresh_only(self) -> None:
        self._delegate("mark_slot_call_refresh_only")

    def enqueue_slot_call_post_commit(self, callback: Callable[[], None]) -> None:
        self._delegate("enqueue_slot_call_post_commit", callback)

    def publish_slot_call_mount_advertisement(
        self,
        request: PyrolyzeMountAdvertisementRequest,
    ) -> PyrolyzeMountAdvertisement:
        return self._delegate("publish_slot_call_mount_advertisement", request)

    def withdraw_slot_call_mount_advertisement(self) -> None:
        self._delegate("withdraw_slot_call_mount_advertisement")

    def _mark_binding_dirty(self) -> None:
        self._delegate("_mark_binding_dirty")

    def commit_binding(self) -> None:
        self._delegate("commit_binding")

    def rollback_binding(self) -> None:
        self._delegate("rollback_binding")

    def deactivate(self) -> None:
        self._delegate("deactivate")

    def _resolve_runtime_site_call(
        self,
        func: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> tuple[Any | None, tuple[Any, ...], dict[str, Any], tuple[RuntimeSiteMetadata[Any], ...]]:
        raw_func, _ = _unwrap(func)
        raw_args = tuple(_unwrap(arg)[0] for arg in args)
        raw_kwargs = {key: _unwrap(value)[0] for key, value in kwargs.items()}
        resolved = resolve_runtime_pyro_call(
            raw_func,
            raw_args,
            raw_kwargs,
            slot_path=SlotIdPath((self.slot_id,)),
        )
        return resolved.func, tuple(resolved.args), dict(resolved.kwargs), tuple(resolved.metadata)

    def _prepare_slot_call(
        self,
        func: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        return prepare_slot_call(func, args, kwargs, unwrap=_unwrap)

    def _should_invoke_slot_call(self, prepared: Any) -> bool:
        return should_invoke_slot_call(
            SlotCallStateSnapshot(
                invoke_dirty=self.invoke_dirty,
                function_identity=self.function_identity,
                schema=self.schema,
                last_args=self.last_args,
                last_kwargs=self.last_kwargs,
                has_binding=self.binding is not None,
            ),
            prepared,
        )

    def _call_with_optional_runtime_context(self, prepared: Any) -> Any:
        return call_with_optional_runtime_context(
            prepared,
            cache_attr_name="_pyrolyze_slot_runtime_ctx_param",
            runtime_context_annotation=SlotRuntimeContext,
            runtime_context_factory=lambda: SlotRuntimeContext(self),
        )

    def _commit_slot_call_invocation(self, prepared: Any, result: Any) -> dict[str, Any]:
        commit_result = commit_slot_call_invocation(
            host=self,
            prepared=prepared,
            previous_binding=self.binding,
            result=result,
        )
        return {
            "binding": commit_result.binding,
            "function_identity": commit_result.function_identity,
            "schema": commit_result.schema,
            "last_args": commit_result.last_args,
            "last_kwargs": commit_result.last_kwargs,
            "result_dirty": commit_result.result_dirty,
        }

    def _refresh_slot_call_binding(self, binding: SlotCallBinding) -> tuple[Any, bool] | None:
        return refresh_slot_call_binding(binding)

    def _project_dirty_state(self, dirty: bool, result_shape: object | None) -> Any:
        return _project_dirty_state(dirty, result_shape)

    def _build_committed_ui(self) -> tuple[object, ...]:
        binding = self.binding
        if isinstance(binding, PyrolyzeMountAdvertisementBinding):
            advertisement = binding.retained_advertisement()
            if advertisement is None:
                return ()
            return (advertisement,)
        return ()

    def _sync_binding_committed_ui(self) -> None:
        self._committed_ui = self._build_committed_ui()


class DirectiveSlotContext(SlotCallSlotContext):
    _state_mgr_cls = DirectiveSlotContextStateMgr

    def __init__(
        self,
        render_context: "RenderContext",
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)
        self.committed_selectors: tuple[SlotSelector, ...] = ()
        self._pass_committed_selectors: tuple[SlotSelector, ...] = ()
        self._slot_selector_type = SlotSelector

    def evaluate_directive(
        self,
        directive_fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> tuple[SlotSelector, ...]:
        return self._delegate("evaluate_directive", directive_fn, args, kwargs)

    def pending_selectors(self) -> tuple[SlotSelector, ...]:
        return self._delegate("pending_selectors")

    def has_pending_emitted_children(self) -> bool:
        return self._delegate("has_pending_emitted_children")

    def _begin_scope_pass(self) -> None:
        self._pass_committed_selectors = self.committed_selectors
        super()._begin_scope_pass()

    def _commit_scope_pass(self) -> None:
        self.committed_selectors = self.pending_selectors()
        super()._commit_scope_pass()
        self._pass_committed_selectors = ()

    def _rollback_scope_pass(self) -> None:
        super()._rollback_scope_pass()
        self.committed_selectors = self._pass_committed_selectors
        self._pass_committed_selectors = ()

    def _build_committed_ui(self) -> tuple[MountDirective, ...]:
        own_children = tuple(
            entry.element
            for entry in self._staged_ui_entries + []  # preserve list->tuple behavior in scaffold
            if hasattr(entry, "element")
        )
        nested_children = tuple(
            element
            for child in self._children.values()
            for element in getattr(child, "_committed_ui", ())
        )
        return (
            MountDirective(
                selectors=self.committed_selectors,
                children=own_children + nested_children,
                slot_id=self.slot_id,
            ),
        )


class AppContextOverrideSlotContext(RerunnableSlotContext):
    _state_mgr_cls = AppContextOverrideSlotContextStateMgr
    _context_kind = ContextKind.APP_CONTEXT_OVERRIDE

    def __init__(
        self,
        render_context: "RenderContext",
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)
        self._structure_error_cls = AppContextOverrideStructureError

    def stage_override(
        self,
        keys: tuple[AppContextKey[Any], ...],
        values: tuple[Any, ...],
    ) -> None:
        self._delegate("stage_override", keys, values)

    def _effective_authored_app_context_lookup(self) -> AppContextLookup:
        return self._state_mgr.effective_authored_app_context_lookup()

    def _begin_scope_pass(self) -> None:
        self._state_mgr.begin_scope_pass()

    def _commit_scope_pass(self) -> None:
        self._state_mgr.commit_scope_pass()

    def _rollback_scope_pass(self) -> None:
        self._state_mgr.rollback_scope_pass()

    def deactivate(self) -> None:
        self._delegate("deactivate")


class ContainerSlotContext(RerunnableSlotContext):
    _state_mgr_cls = ContainerSlotContextStateMgr
    _context_kind = ContextKind.CONTAINER

    def __init__(
        self,
        render_context: "RenderContext",
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)


class ComponentCallSlotContext(RerunnableSlotContext):
    _state_mgr_cls = ComponentCallSlotContextStateMgr
    _context_kind = ContextKind.COMPONENT_CALL

    def __init__(
        self,
        render_context: "RenderContext",
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)
        self._render_context_cls = RenderContext

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
        return self._delegate(
            "invoke",
            component,
            args,
            kwargs,
            dirty_state=dirty_state,
            _pyr_param_names=_pyr_param_names,
            _pyr_args_dirty=_pyr_args_dirty,
            _pyr_kwargs_dirty=_pyr_kwargs_dirty,
        )

    def commit_owned_event_handlers(self) -> None:
        self._delegate("commit_owned_event_handlers")

    def rollback_owned_event_handlers(self) -> None:
        self._delegate("rollback_owned_event_handlers")

    def deactivate(self) -> None:
        self._delegate("deactivate")


class KeyedLoopSlotContext(RerunnableSlotContext):
    _state_mgr_cls = KeyedLoopSlotContextStateMgr
    _context_kind = ContextKind.KEYED_LOOP


class LoopItemSlotContext(RerunnableSlotContext):
    _state_mgr_cls = LoopItemSlotContextStateMgr
    _context_kind = ContextKind.LOOP_ITEM
    _state_attr_names = ContextBase._state_attr_names | {
        "current",
        "current_dirty",
        "current_initialized",
    }

    def current_value(self) -> Any:
        return self._delegate("current_value")

    def update_current(self, value: Any) -> None:
        self._delegate("update_current", value)


class LeafSlotContext(RerunnableSlotContext):
    _state_mgr_cls = LeafSlotContextStateMgr
    _context_kind = ContextKind.LEAF

    def __init__(
        self,
        render_context: "RenderContext",
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        super().__init__(render_context, parent, slot_id, invoke_dirty, seen_in_pass)
        self.last_args: tuple[Any, ...] = ()
        self.last_kwargs: tuple[tuple[str, Any], ...] = ()

    def invoke(self, leaf_fn: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
        return self._delegate("invoke", leaf_fn, args, kwargs)

    def invoke_native(
        self,
        leaf_fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        context_param: str,
    ) -> Any:
        return self._delegate("invoke_native", leaf_fn, args, kwargs, context_param=context_param)


@dataclass(slots=True)
class _ContainerCallHandle(AbstractContextManager[ContainerSlotContext]):
    slot: ContainerSlotContext
    container_fn: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    _host_context: Any = None

    def __enter__(self) -> ContainerSlotContext:
        bound_args = tuple(_bind_pending_event_plain_value(self.slot, value) for value in self.args)
        bound_kwargs = {
            key: _bind_pending_event_plain_value(self.slot, value)
            for key, value in self.kwargs.items()
        }
        self._host_context = self.container_fn(*bound_args, **bound_kwargs)
        host_enter = getattr(self._host_context, "__enter__", None)
        if callable(host_enter):
            host_enter()
        self.slot._begin_scope_pass()
        return self.slot

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        suppress = False
        try:
            _finish_context_pass(self.slot, commit=exc_type is None)
        finally:
            host_exit = getattr(self._host_context, "__exit__", None)
            if callable(host_exit):
                suppress = bool(host_exit(exc_type, exc, tb))
        return suppress


@dataclass(slots=True)
class _DirectiveCallHandle(AbstractContextManager[DirectiveSlotContext]):
    slot: DirectiveSlotContext
    directive_fn: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]

    def __enter__(self) -> DirectiveSlotContext:
        self.slot._begin_scope_pass()
        try:
            self.slot.evaluate_directive(self.directive_fn, self.args, self.kwargs)
        except BaseException:
            self.slot._rollback_scope_pass()
            raise
        return self.slot

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        if exc_type is not None:
            _finish_context_pass(self.slot, commit=False)
            return False
        try:
            selectors = self.slot.pending_selectors()
            if (
                len(selectors) == 1
                and getattr(selectors[0], "kind", None) == "no_emit"
                and self.slot.has_pending_emitted_children()
            ):
                raise RuntimeError("mount(no_emit) does not allow emitted children")
            _finish_context_pass(self.slot, commit=True)
        except BaseException:
            if getattr(self.slot, "_scope_active", False):
                _finish_context_pass(self.slot, commit=False)
            raise
        return False


@dataclass(slots=True)
class _MountContainerCallHandle(AbstractContextManager[DirectiveSlotContext]):
    slot: DirectiveSlotContext
    container_fn: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    context_param: str
    _host_context: Any = None

    def __enter__(self) -> DirectiveSlotContext:
        bound_args = tuple(_bind_pending_event_plain_value(self.slot, value) for value in self.args)
        bound_kwargs = {
            key: _bind_pending_event_plain_value(self.slot, value)
            for key, value in self.kwargs.items()
        }
        if self.context_param not in bound_kwargs:
            bound_kwargs[self.context_param] = ContainerCallRuntimeContext(self.slot)
        self._host_context = self.container_fn(*bound_args, **bound_kwargs)
        host_enter = getattr(self._host_context, "__enter__", None)
        if not callable(host_enter):
            raise TypeError("mount() container helpers must return a context manager")
        entered = host_enter()
        if isinstance(entered, DirectiveSlotContext):
            return entered
        return self.slot

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        host_exit = getattr(self._host_context, "__exit__", None)
        if not callable(host_exit):
            raise RuntimeError("mount() container helper host context is missing __exit__")
        return bool(host_exit(exc_type, exc, tb))


@dataclass(slots=True)
class _AppContextOverrideHandle(AbstractContextManager[AppContextOverrideSlotContext]):
    slot: AppContextOverrideSlotContext
    keys: tuple[AppContextKey[Any], ...]
    values: tuple[Any, ...]

    def __enter__(self) -> AppContextOverrideSlotContext:
        self.slot.stage_override(self.keys, self.values)
        self.slot._begin_scope_pass()
        return self.slot

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        _finish_context_pass(self.slot, commit=exc_type is None)
        return False


@dataclass(slots=True)
class _NativeContainerCallHandle(AbstractContextManager[ContainerSlotContext]):
    slot: ContainerSlotContext
    container_fn: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    context_param: str

    def __enter__(self) -> ContainerSlotContext:
        self.slot.expects_native_root = True
        self.slot._begin_scope_pass()
        try:
            bound_args = tuple(_bind_pending_event_plain_value(self.slot, value) for value in self.args)
            bound_kwargs = {
                key: _bind_pending_event_plain_value(self.slot, value)
                for key, value in self.kwargs.items()
            }
            _ = self.context_param
            result = self.container_fn(self.slot, *bound_args, **bound_kwargs)
            if result is not None:
                raise TypeError("@pyrolyze functions must return None")
            if len(self.slot._staged_ui) != 1:
                raise RuntimeError("native container helpers must emit exactly one root UIElement")
        except BaseException:
            self.slot._rollback_scope_pass()
            self.slot.expects_native_root = False
            raise
        return self.slot

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        try:
            _finish_context_pass(self.slot, commit=exc_type is None)
        finally:
            self.slot.expects_native_root = False
        return False


@dataclass(slots=True)
class _PyrolyzeContainerCallHandle(AbstractContextManager[ContainerSlotContext]):
    slot: ContainerSlotContext
    runtime_func: Callable[..., Any]
    bound_receiver: object
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    dirty_state: DirtyStateContext
    param_names: tuple[str, ...] = ()
    dynamic_param_names: tuple[str, ...] | None = None
    dynamic_args_dirty: tuple[Any, ...] | None = None
    dynamic_kwargs_dirty: dict[str, Any] | None = None
    packed_kwargs: bool = False
    packed_kwarg_param_names: tuple[str, ...] = ()

    def __enter__(self) -> ContainerSlotContext:
        self.slot.expects_native_root = True
        self.slot._begin_scope_pass()
        try:
            dirty_state = self.dirty_state
            effective_param_names = self.dynamic_param_names or self.param_names
            if effective_param_names and not dirty_state.values:
                dirty_state = dirtyof_values(
                    build_function_arg_dirty_map(
                        effective_param_names,
                        self.dynamic_args_dirty or (),
                        self.dynamic_kwargs_dirty or {},
                    )
                )
            bound_args = tuple(_bind_pending_event_plain_value(self.slot, value) for value in self.args)
            bound_kwargs = {
                key: _bind_pending_event_plain_value(self.slot, value)
                for key, value in self.kwargs.items()
            }
            if self.packed_kwargs:
                packed_kwargs = pack_function_args(
                    self.packed_kwarg_param_names,
                    bound_args,
                    bound_kwargs,
                )
                if self.bound_receiver is _BOUND_METHOD_SELF_MISSING:
                    result = self.runtime_func(self.slot, dirty_state, **packed_kwargs)
                else:
                    result = self.runtime_func(self.bound_receiver, self.slot, dirty_state, **packed_kwargs)
            else:
                if self.bound_receiver is _BOUND_METHOD_SELF_MISSING:
                    result = self.runtime_func(self.slot, dirty_state, *bound_args, **bound_kwargs)
                else:
                    result = self.runtime_func(
                        self.bound_receiver,
                        self.slot,
                        dirty_state,
                        *bound_args,
                        **bound_kwargs,
                    )
            if result is not None:
                raise TypeError("@pyrolyze functions must return None")
            if len(self.slot._staged_ui) != 1:
                raise RuntimeError("native container helpers must emit exactly one root UIElement")
        except BaseException:
            self.slot._rollback_scope_pass()
            self.slot.expects_native_root = False
            raise
        return self.slot

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        try:
            _finish_context_pass(self.slot, commit=exc_type is None)
        finally:
            self.slot.expects_native_root = False
        return False


def _structured_dirty_projection(
    *,
    previous: Any,
    current: Any,
    initialized: bool,
) -> Any:
    if not initialized:
        return _all_dirty_projection(current)
    if isinstance(current, tuple) and isinstance(previous, tuple) and len(current) == len(previous):
        return tuple(
            _structured_dirty_projection(previous=prev_item, current=current_item, initialized=True)
            for prev_item, current_item in zip(previous, current, strict=False)
        )
    return current != previous


def _all_dirty_projection(value: Any) -> Any:
    if isinstance(value, tuple):
        return tuple(_all_dirty_projection(item) for item in value)
    return True


@dataclass(slots=True)
class _KeyedLoopIterable(Generic[T]):
    owner: KeyedLoopSlotContext
    values: tuple[T, ...]
    key_fn: Callable[[T], Any]

    def __iter__(self) -> Iterator[T]:
        self.owner._begin_scope_pass()
        seen_keys: set[Any] = set()
        try:
            for value in self.values:
                key = self.key_fn(value)
                if key in seen_keys:
                    raise DuplicateKeyError(f"duplicate key {key!r} for loop slot {self.owner.slot_id!r}")
                seen_keys.add(key)
                item_slot = SlotId(
                    module_id=self.owner.slot_id.module_id,
                    slot_index=self.owner.slot_id.slot_index,
                    key_path=(key,),
                    line_no=self.owner.slot_id.line_no,
                )
                item = self.owner._ensure_slot(item_slot, LoopItemSlotContext)
                item.update_current(value)
                yield item
        except BaseException:
            self.owner._rollback_scope_pass()
            raise
        else:
            self.owner._commit_scope_pass()


@dataclass(slots=True)
class _InvalidationScheduler:
    queue: list["RenderContext"] = field(default_factory=list)
    deferred: list["RenderContext"] = field(default_factory=list)
    active: list["RenderContext"] = field(default_factory=list)

    def request(self, boundary: "RenderContext") -> None:
        if self._is_blocked_by_active(boundary):
            self._merge_boundary(self.deferred, boundary)
            return
        self._merge_boundary(self.queue, boundary)

    def enter_active(self, boundary: "RenderContext") -> None:
        self.active.append(boundary)

    def exit_active(self, boundary: "RenderContext") -> None:
        if self.active and self.active[-1] is boundary:
            self.active.pop()
        else:
            self.active = [active for active in self.active if active is not boundary]
        self._promote_deferred()

    def pop_next(self) -> "RenderContext | None":
        if not self.queue:
            return None
        return self.queue.pop(0)

    def has_pending_work(self) -> bool:
        return bool(self.queue or self.deferred)

    def remove(self, boundary: "RenderContext") -> None:
        self.queue = [queued for queued in self.queue if queued is not boundary]
        self.deferred = [queued for queued in self.deferred if queued is not boundary]
        self.active = [active for active in self.active if active is not boundary]

    def _promote_deferred(self) -> None:
        remaining: list[RenderContext] = []
        for boundary in self.deferred:
            if self._is_blocked_by_active(boundary):
                remaining.append(boundary)
            else:
                self._merge_boundary(self.queue, boundary)
        self.deferred = remaining

    def _is_blocked_by_active(self, boundary: "RenderContext") -> bool:
        return any(active._is_ancestor_boundary_of(boundary) for active in self.active)

    def _merge_boundary(
        self,
        targets: list["RenderContext"],
        boundary: "RenderContext",
    ) -> None:
        if any(queued._is_ancestor_boundary_of(boundary) for queued in targets):
            return
        targets[:] = [queued for queued in targets if not boundary._is_ancestor_boundary_of(queued)]
        if any(queued is boundary for queued in targets):
            return
        targets.append(boundary)


class RenderContext(ContextBase):
    _state_mgr_cls = RenderContextStateMgr

    def __init__(
        self,
        *,
        owner_slot: ComponentCallSlotContext | None = None,
        scheduler_root: "RenderContext" | None = None,
        app_context_store: AppContextStore | None = None,
        authored_app_context_lookup: AppContextLookup | None = None,
    ) -> None:
        self._slots_by_id: dict[SlotId, SlotContext] = {}
        self._mount_advertisements_by_slot: dict[SlotId, PyrolyzeMountAdvertisement] = {}
        self._owner_slot = owner_slot
        self._mounted_callback: Callable[[], None] | None = None
        self._post_commit_callbacks: list[Callable[[], None]] = []
        self._queued_invalidations: list[object] = []
        self._flush_poster: Callable[[Callable[[], None]], None] | None = None
        self._flush_posted = False
        self._flush_running = False
        if scheduler_root is None:
            self._scheduler_root = self
            self._scheduler = _InvalidationScheduler()
            self._app_context_store = app_context_store or AppContextStore()
            self._authored_app_context_lookup = authored_app_context_lookup or EMPTY_APP_CONTEXT_LOOKUP
        else:
            self._scheduler_root = scheduler_root
            self._scheduler = scheduler_root._scheduler
            self._app_context_store = scheduler_root._app_context_store
            self._authored_app_context_lookup = (
                authored_app_context_lookup or scheduler_root._authored_app_context_lookup
            )
        ContextBase.__init__(self, self)

    def get_kind(self) -> ContextKind:
        if self._owner_slot is None:
            return ContextKind.RENDER_ROOT
        return ContextKind.COMPONENT_RENDER

    def pass_scope(self) -> Any:
        return self._delegate("pass_scope")

    def mount(self, callback: Callable[[], None]) -> None:
        self._delegate("mount", callback)

    def set_flush_poster(self, post: Callable[[Callable[[], None]], None]) -> None:
        self._delegate("set_flush_poster", post)

    def run_pending_invalidations(self) -> None:
        self._delegate("run_pending_invalidations")

    def _run_boundary(self) -> None:
        self._delegate("_run_boundary")

    def begin_pass(self) -> None:
        self._delegate("begin_pass")

    def end_pass(self) -> None:
        self._delegate("end_pass")

    def rollback_pass(self) -> None:
        self._delegate("rollback_pass")

    def debug_children_of(self, slot_id: SlotId | None = None) -> tuple[SlotId, ...]:
        return self._delegate("debug_children_of", slot_id)

    def debug_is_active(self, slot_id: SlotId) -> bool:
        return self._delegate("debug_is_active", slot_id)

    def debug_pending_boundaries(self) -> tuple[SlotId | None, ...]:
        return self._delegate("debug_pending_boundaries")

    def debug_mount_advertisements(self) -> tuple[PyrolyzeMountAdvertisement, ...]:
        return self._delegate("debug_mount_advertisements")

    def debug_ui(self, slot_id: SlotId | None = None) -> tuple[UIElement | MountDirective, ...]:
        return self._delegate("debug_ui", slot_id)

    def committed_ui(self) -> tuple[UIElement | MountDirective, ...]:
        return self._delegate("committed_ui")

    def _refresh_committed_ui_from_children(self) -> None:
        self._delegate("refresh_committed_ui_from_children")

    def walk_context_graph(self, listener: object) -> None:
        self._delegate("walk_context_graph", listener)

    def close_app_contexts(self) -> None:
        self._delegate("close_app_contexts")

    def _debug_boundary_id(self) -> SlotId | None:
        return self._delegate("_debug_boundary_id")

    def _is_ancestor_boundary_of(self, other: "RenderContext") -> bool:
        return self._delegate("_is_ancestor_boundary_of", other)

    def _remove_from_scheduler(self) -> None:
        self._delegate("_remove_from_scheduler")

    def _flush_post_commit(self) -> None:
        self._delegate("_flush_post_commit")

    def _post_flush_if_needed(self, *, was_pending: bool) -> None:
        self._delegate("_post_flush_if_needed", was_pending=was_pending)

    def _rebuild_mount_advertisement_surface(self) -> None:
        self._delegate("_rebuild_mount_advertisement_surface")

    def _queue_invalidation_from(self, slot: object, *, include_source: bool = True) -> None:
        boundary = getattr(slot, "render_context", self)
        scheduler_root = boundary._scheduler_root
        was_pending = scheduler_root._scheduler.has_pending_work()
        if include_source:
            slot.invoke_dirty = True

        current = slot.parent
        dirty_contexts = 0
        while isinstance(current, ContextBase):
            dirty_contexts += 1
            for child in current._children.values():
                child.invoke_dirty = True
            if isinstance(current, RenderContext):
                break
            current = current.parent

        owner_slot = getattr(boundary, "_owner_slot", None)
        if owner_slot is not None:
            owner_slot.invoke_dirty = True

        boundary._scheduler.request(boundary)
        if not any(queued is slot for queued in self._queued_invalidations):
            self._queued_invalidations.append(slot)
        scheduler_root._post_flush_if_needed(was_pending=was_pending)
        if trace_enabled(TraceChannel.INVALIDATION):
            emit_trace(
                TraceChannel.INVALIDATION,
                "queued",
                source_slot=getattr(slot, "slot_id", None),
                boundary=boundary._debug_boundary_id(),
                owner_slot=owner_slot.slot_id if owner_slot is not None else None,
                include_source=include_source,
                dirty_contexts=dirty_contexts,
                queued=tuple(item._debug_boundary_id() for item in boundary._scheduler.queue),
            )

    def _enqueue_post_commit(self, callback: Callable[[], None]) -> None:
        self._post_commit_callbacks.append(callback)

    def _publish_mount_advertisement(
        self,
        slot: SlotCallSlotContext,
        request: PyrolyzeMountAdvertisementRequest,
    ) -> PyrolyzeMountAdvertisement:
        parent = _resolve_mount_advertisement_owner(slot.parent)
        if parent is None:
            raise MountAdvertisementContextError(
                "advertise_mount() requires a native container owner"
            )
        if not (parent.expects_native_root or parent.committed_native_root):
            raise MountAdvertisementContextError(
                "advertise_mount() requires a native container node owner"
            )
        mount_owner_id = parent.current_slot_id()
        if mount_owner_id is None:
            raise MountAdvertisementContextError(
                "advertise_mount() could not resolve a container slot owner"
            )
        advertisement = PyrolyzeMountAdvertisement(
            key=request.key,
            selectors=request.selectors,
            default=request.default,
            source_slot_id=slot.slot_id,
            surface_owner_id=mount_owner_id,
            mount_owner_id=mount_owner_id,
        )
        return advertisement

    def _withdraw_mount_advertisement(self, slot_id: SlotId) -> None:
        if slot_id not in self._mount_advertisements_by_slot:
            return
        next_entries = dict(self._mount_advertisements_by_slot)
        next_entries.pop(slot_id, None)
        self._mount_advertisements_by_slot = next_entries


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
ContainerCallRuntimeContext = _support.ContainerCallRuntimeContext
_ContextSlotExprHost = _support._ContextSlotExprHost
_unwrap = _support._unwrap
_resolve_runtime_site_call = _support._resolve_runtime_site_call
_unwrap_native_value = _support._unwrap_native_value
_native_context_param_name = _support._native_context_param_name
_container_runtime_context_param_name = _support._container_runtime_context_param_name
_BOUND_METHOD_SELF_MISSING = _support._BOUND_METHOD_SELF_MISSING
_component_call_key = _support._component_call_key
_clean_dirty_state = _support._clean_dirty_state
_resolve_runtime_component_func = _support._resolve_runtime_component_func
_native_emission_slot_identity = _support._native_emission_slot_identity
_bind_pending_event_plain_value = _support._bind_pending_event_plain_value
_finish_context_pass = _support._finish_context_pass
_ContainerCallHandle = _support._ContainerCallHandle
_DirectiveCallHandle = _support._DirectiveCallHandle
_MountContainerCallHandle = _support._MountContainerCallHandle
_AppContextOverrideHandle = _support._AppContextOverrideHandle
_NativeContainerCallHandle = _support._NativeContainerCallHandle
_PyrolyzeContainerCallHandle = _support._PyrolyzeContainerCallHandle
_structured_dirty_projection = _support._structured_dirty_projection
_KeyedLoopIterable = _support._KeyedLoopIterable

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
    "RenderContext",
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
