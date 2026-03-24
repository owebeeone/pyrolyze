"""Phase 05A context graph runtime primitives."""

from __future__ import annotations

import inspect
import logging
import os
from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Iterator, Protocol, TypeVar, cast

from pyrolyze.api import (
    MountDirective,
    PyrolyzeMountAdvertisement,
    PyrolyzeMountAdvertisementRequest,
    SlotSelector,
    UIElement,
)

from .app_context import (
    EMPTY_APP_CONTEXT_LOOKUP,
    AppContextKey,
    AppContextLookup,
    AppContextStore,
    GENERATION_TRACKER_KEY,
    OverlayAppContextLookup,
)
from .trace import TraceChannel, emit_trace, trace_enabled


T = TypeVar("T")
S = TypeVar("S", bound="SlotContext")


@dataclass(frozen=True, slots=True)
class CompValue(Generic[T]):
    value: T
    dirty: bool = False


@dataclass(frozen=True, slots=True)
class DirtyStateContext:
    values: dict[str, bool]

    def get(self, name: str, default: bool = False) -> bool:
        return bool(self.values.get(name, default))

    def __getattr__(self, name: str) -> bool:
        return self.get(name)


def dirtyof(**values: bool) -> DirtyStateContext:
    return DirtyStateContext(values={key: bool(value) for key, value in values.items()})


@dataclass(frozen=True, slots=True)
class PlainCallResult(Generic[T]):
    dirty: Any
    value: T

    def __iter__(self) -> Iterator[Any]:
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
class ExternalStoreRef(Generic[T]):
    identity: object
    subscribe: Callable[[Callable[[], None]], Callable[[], None]]
    get: Callable[[], T]


@dataclass(frozen=True, slots=True)
class ModuleId:
    canonical_name: str


@dataclass(slots=True)
class ModuleRegistry:
    _modules: dict[str, ModuleId] = field(default_factory=dict)

    def module_id(self, canonical_name: str) -> ModuleId:
        module_id = self._modules.get(canonical_name)
        if module_id is None:
            module_id = ModuleId(canonical_name=canonical_name)
            self._modules[canonical_name] = module_id
        return module_id


module_registry = ModuleRegistry()


@dataclass(frozen=True, slots=True)
class SlotId:
    module_id: ModuleId
    slot_index: int
    key_path: tuple[Any, ...] = ()
    line_no: int | None = field(default=None, compare=False, hash=False)
    is_top_level: bool = field(default=False, compare=False, hash=False)


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


def _dirty_state_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, tuple):
        return any(_dirty_state_truthy(item) for item in value)
    return bool(value)


def _unwrap(value: PlainCallResult[Any] | CompValue[Any] | Any) -> tuple[Any, bool]:
    if isinstance(value, CompValue):
        return value.value, value.dirty
    if isinstance(value, PlainCallResult):
        return value.value, _dirty_state_truthy(value.dirty)
    return value, False


def _wrap_comp_value(value: PlainCallResult[T] | CompValue[T] | T) -> CompValue[T]:
    if isinstance(value, CompValue):
        return value
    if isinstance(value, PlainCallResult):
        return CompValue(value=value.value, dirty=_dirty_state_truthy(value.dirty))
    return CompValue(value=value, dirty=False)


def _unwrap_native_value(value: Any) -> Any:
    if isinstance(value, CompValue):
        return _unwrap_native_value(value.value)
    if isinstance(value, PlainCallResult):
        return _unwrap_native_value(value.value)
    if isinstance(value, dict):
        return {key: _unwrap_native_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_unwrap_native_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_unwrap_native_value(item) for item in value)
    return value


def _project_dirty_state(dirty: bool, result_shape: object | None) -> Any:
    if result_shape is None or result_shape == "scalar":
        return dirty
    if (
        isinstance(result_shape, tuple)
        and len(result_shape) == 2
        and result_shape[0] == "tuple"
        and isinstance(result_shape[1], int)
    ):
        return tuple(dirty for _ in range(result_shape[1]))
    raise TypeError(f"unsupported result_shape {result_shape!r}")


def _resolve_mount_advertisement_owner(parent: ContextBase) -> ContainerSlotContext | None:
    current: ContextBase | SlotContext | None = parent
    while current is not None:
        if isinstance(current, ContainerSlotContext):
            return current
        if isinstance(current, SlotContext):
            current = current.parent
            continue
        return None
    return None


@dataclass(frozen=True, slots=True)
class UseEffectRequest:
    effect_fn: Callable[[], Callable[[], None] | None]
    deps: tuple[Any, ...] | None = None
    phase: str = "passive"


class AsyncEffectHandle(Protocol):
    def cancel(self) -> None: ...


@dataclass(frozen=True, slots=True)
class UseEffectAsyncRequest:
    start: Callable[[Callable[[], None]], AsyncEffectHandle | None]
    deps: tuple[Any, ...] | None = None
    cleanup: Callable[[], None] | None = None


@dataclass(frozen=True, slots=True)
class PlainCallRuntimeContext:
    slot: PlainCallSlotContext

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

    def current_generation_id(self) -> int:
        tracker = self.get_app_context(GENERATION_TRACKER_KEY)
        return tracker.current()

    def current_slot_id(self) -> SlotId:
        return self.slot.slot_id


class PlainCallBinding:
    def exposed_value(self) -> Any:
        raise NotImplementedError

    def refresh(self) -> tuple[Any, bool] | None:
        return None

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None

    def deactivate(self) -> None:
        return None


@dataclass(slots=True)
class PlainValueBinding(PlainCallBinding):
    value: Any

    def exposed_value(self) -> Any:
        return self.value

    def rebind(self, value: Any) -> None:
        self.value = value


@dataclass(slots=True)
class ExternalStoreBinding(PlainCallBinding):
    slot: PlainCallSlotContext
    ref: ExternalStoreRef[Any]
    value: Any = None
    initialized: bool = False
    dirty: bool = False
    unsubscribe: Callable[[], None] | None = None

    @classmethod
    def bind(
        cls,
        slot: PlainCallSlotContext,
        ref: ExternalStoreRef[Any],
    ) -> ExternalStoreBinding:
        binding = cls(slot=slot, ref=ref)
        binding._subscribe(ref)
        binding._update_from_get()
        return binding

    def exposed_value(self) -> Any:
        return self.value

    def refresh(self) -> tuple[Any, bool] | None:
        if not self.dirty:
            return None
        dirty = self._update_from_get()
        self.dirty = False
        return self.value, dirty

    def rebind(self, ref: ExternalStoreRef[Any]) -> None:
        if self.ref.identity == ref.identity:
            self.ref = ref
        else:
            next_unsubscribe = ref.subscribe(self._mark_dirty)
            previous_unsubscribe = self.unsubscribe
            self.ref = ref
            self.unsubscribe = next_unsubscribe
            if previous_unsubscribe is not None:
                previous_unsubscribe()
        self._update_from_get()

    def deactivate(self) -> None:
        previous_unsubscribe = self.unsubscribe
        self.unsubscribe = None
        self.dirty = False
        if previous_unsubscribe is not None:
            previous_unsubscribe()

    def _subscribe(self, ref: ExternalStoreRef[Any]) -> None:
        self.unsubscribe = ref.subscribe(self._mark_dirty)

    def _mark_dirty(self) -> None:
        self.dirty = True
        self.slot.render_context._queue_invalidation_from(self.slot, include_source=False)

    def _update_from_get(self) -> bool:
        next_value = self.ref.get()
        dirty = (not self.initialized) or (next_value != self.value)
        self.value = next_value
        self.initialized = True
        return dirty


_EFFECT_DEPS_UNSET = object()


@dataclass(slots=True)
class UseEffectBinding(PlainCallBinding):
    slot: PlainCallSlotContext
    request: UseEffectRequest | None = None
    cleanup: Callable[[], None] | None = None
    deps: object = _EFFECT_DEPS_UNSET
    staged_request: UseEffectRequest | None = None

    @classmethod
    def bind(
        cls,
        slot: PlainCallSlotContext,
        request: UseEffectRequest,
    ) -> UseEffectBinding:
        binding = cls(slot=slot)
        binding.stage(request)
        return binding

    def exposed_value(self) -> None:
        return None

    def stage(self, request: UseEffectRequest) -> None:
        self.staged_request = request

    def commit(self) -> None:
        request = self.staged_request
        if request is None:
            return

        self.staged_request = None
        should_run = self._should_run(request)
        self.request = request
        self.deps = request.deps
        if should_run:
            self.slot.render_context._enqueue_post_commit(
                self._make_post_commit_callback(request)
            )

    def rollback(self) -> None:
        self.staged_request = None

    def deactivate(self) -> None:
        self.staged_request = None
        cleanup = self.cleanup
        self.cleanup = None
        self.request = None
        self.deps = _EFFECT_DEPS_UNSET
        if cleanup is not None:
            cleanup()

    def _should_run(self, request: UseEffectRequest) -> bool:
        if self.request is None:
            return True
        if request.deps is None:
            return True
        return self.deps is _EFFECT_DEPS_UNSET or request.deps != self.deps

    def _make_post_commit_callback(
        self,
        request: UseEffectRequest,
    ) -> Callable[[], None]:
        def run_effect() -> None:
            cleanup = self.cleanup
            if cleanup is not None:
                self.cleanup = None
                cleanup()

            next_cleanup = request.effect_fn()
            if next_cleanup is not None and not callable(next_cleanup):
                raise TypeError("effect must return a cleanup callable or None")
            self.cleanup = cast(Callable[[], None] | None, next_cleanup)

        return run_effect


@dataclass(slots=True)
class UseEffectAsyncBinding(PlainCallBinding):
    slot: PlainCallSlotContext
    request: UseEffectAsyncRequest | None = None
    deps: object = _EFFECT_DEPS_UNSET
    staged_request: UseEffectAsyncRequest | None = None
    handle: AsyncEffectHandle | None = None
    active_token: object | None = None
    cleanup: Callable[[], None] | None = None

    @classmethod
    def bind(
        cls,
        slot: PlainCallSlotContext,
        request: UseEffectAsyncRequest,
    ) -> UseEffectAsyncBinding:
        binding = cls(slot=slot)
        binding.stage(request)
        return binding

    def exposed_value(self) -> None:
        return None

    def stage(self, request: UseEffectAsyncRequest) -> None:
        self.staged_request = request

    def commit(self) -> None:
        request = self.staged_request
        if request is None:
            return

        self.staged_request = None
        should_run = self._should_run(request)
        self.request = request
        self.deps = request.deps
        if should_run:
            self.slot.render_context._enqueue_post_commit(
                self._make_post_commit_callback(request)
            )

    def rollback(self) -> None:
        self.staged_request = None

    def deactivate(self) -> None:
        self.staged_request = None
        self.request = None
        self.deps = _EFFECT_DEPS_UNSET
        self._teardown_active()

    def _should_run(self, request: UseEffectAsyncRequest) -> bool:
        if self.request is None:
            return True
        if request.deps is None:
            return True
        return self.deps is _EFFECT_DEPS_UNSET or request.deps != self.deps

    def _make_post_commit_callback(
        self,
        request: UseEffectAsyncRequest,
    ) -> Callable[[], None]:
        def start_effect() -> None:
            self._teardown_active()
            self.cleanup = request.cleanup
            token = object()
            self.active_token = token

            def on_complete() -> None:
                if self.active_token is not token:
                    return
                self.handle = None
                self.slot.render_context._queue_invalidation_from(
                    self.slot,
                    include_source=False,
                )

            self.handle = request.start(on_complete)

        return start_effect

    def _teardown_active(self) -> None:
        handle = self.handle
        self.handle = None
        self.active_token = None
        if handle is not None:
            handle.cancel()
        cleanup = self.cleanup
        self.cleanup = None
        if cleanup is not None:
            cleanup()


class PlainCallSemanticsHandler:
    def can_handle(self, result: object) -> bool:
        raise NotImplementedError

    def bind(
        self,
        slot: PlainCallSlotContext,
        result: object,
        previous: PlainCallBinding | None,
    ) -> PlainCallBinding:
        raise NotImplementedError


class ExternalStoreHandler(PlainCallSemanticsHandler):
    def can_handle(self, result: object) -> bool:
        return isinstance(result, ExternalStoreRef)

    def bind(
        self,
        slot: PlainCallSlotContext,
        result: object,
        previous: PlainCallBinding | None,
    ) -> PlainCallBinding:
        ref = cast(ExternalStoreRef[Any], result)
        if isinstance(previous, ExternalStoreBinding):
            previous.rebind(ref)
            return previous
        return ExternalStoreBinding.bind(slot, ref)


@dataclass(slots=True)
class PyrolyzeMountAdvertisementBinding(PlainCallBinding):
    slot: PlainCallSlotContext
    request: PyrolyzeMountAdvertisementRequest | None = None
    staged_request: PyrolyzeMountAdvertisementRequest | None = None
    advertisement: PyrolyzeMountAdvertisement | None = None

    @classmethod
    def bind(
        cls,
        slot: PlainCallSlotContext,
        request: PyrolyzeMountAdvertisementRequest,
    ) -> PyrolyzeMountAdvertisementBinding:
        binding = cls(slot=slot)
        binding.stage(request)
        return binding

    def exposed_value(self) -> PyrolyzeMountAdvertisementRequest | None:
        if self.staged_request is not None:
            return self.staged_request
        return self.request

    def stage(self, request: PyrolyzeMountAdvertisementRequest) -> None:
        self.staged_request = request

    def commit(self) -> None:
        request = self.staged_request
        if request is None:
            return
        self.advertisement = self.slot.render_context._publish_mount_advertisement(
            self.slot,
            request,
        )
        self.request = request
        self.staged_request = None

    def rollback(self) -> None:
        self.staged_request = None

    def deactivate(self) -> None:
        self.staged_request = None
        self.request = None
        self.advertisement = None
        self.slot.render_context._withdraw_mount_advertisement(self.slot.slot_id)

    def retained_advertisement(self) -> PyrolyzeMountAdvertisement | None:
        return self.advertisement


class PyrolyzeMountAdvertisementHandler(PlainCallSemanticsHandler):
    def can_handle(self, result: object) -> bool:
        return isinstance(result, PyrolyzeMountAdvertisementRequest)

    def bind(
        self,
        slot: PlainCallSlotContext,
        result: object,
        previous: PlainCallBinding | None,
    ) -> PlainCallBinding:
        request = cast(PyrolyzeMountAdvertisementRequest, result)
        if isinstance(previous, PyrolyzeMountAdvertisementBinding):
            previous.stage(request)
            return previous
        return PyrolyzeMountAdvertisementBinding.bind(slot, request)


class PlainValueHandler(PlainCallSemanticsHandler):
    def can_handle(self, result: object) -> bool:
        return not isinstance(
            result,
            (
                ExternalStoreRef,
                PyrolyzeMountAdvertisementRequest,
                UseEffectRequest,
                UseEffectAsyncRequest,
            ),
        )

    def bind(
        self,
        slot: PlainCallSlotContext,
        result: object,
        previous: PlainCallBinding | None,
    ) -> PlainCallBinding:
        if isinstance(previous, PlainValueBinding):
            previous.rebind(result)
            return previous
        return PlainValueBinding(value=result)


class UseEffectHandler(PlainCallSemanticsHandler):
    def can_handle(self, result: object) -> bool:
        return isinstance(result, UseEffectRequest)

    def bind(
        self,
        slot: PlainCallSlotContext,
        result: object,
        previous: PlainCallBinding | None,
    ) -> PlainCallBinding:
        request = cast(UseEffectRequest, result)
        if isinstance(previous, UseEffectBinding):
            previous.stage(request)
            return previous
        return UseEffectBinding.bind(slot, request)


class UseEffectAsyncHandler(PlainCallSemanticsHandler):
    def can_handle(self, result: object) -> bool:
        return isinstance(result, UseEffectAsyncRequest)

    def bind(
        self,
        slot: PlainCallSlotContext,
        result: object,
        previous: PlainCallBinding | None,
    ) -> PlainCallBinding:
        request = cast(UseEffectAsyncRequest, result)
        if isinstance(previous, UseEffectAsyncBinding):
            previous.stage(request)
            return previous
        return UseEffectAsyncBinding.bind(slot, request)


_PLAIN_CALL_HANDLERS: tuple[PlainCallSemanticsHandler, ...] = (
    ExternalStoreHandler(),
    PyrolyzeMountAdvertisementHandler(),
    UseEffectAsyncHandler(),
    UseEffectHandler(),
    PlainValueHandler(),
)

_PLAIN_CALL_RUNTIME_CONTEXT_ATTR = "_pyrolyze_plain_call_runtime_ctx_param"
_CALLABLE_CACHE_MISSING = object()


def _read_callable_annotation_cache(func: Callable[..., Any], attr_name: str) -> object:
    try:
        return getattr(func, attr_name)
    except AttributeError:
        return _CALLABLE_CACHE_MISSING


def _write_callable_annotation_cache(
    func: Callable[..., Any],
    attr_name: str,
    value: str | None,
) -> None:
    try:
        setattr(func, attr_name, value)
    except (AttributeError, TypeError):
        # Builtins/C-backed callables can reject attribute writes.
        return


def _plain_call_runtime_context_param_name(func: Callable[..., Any]) -> str | None:
    cached = _read_callable_annotation_cache(func, _PLAIN_CALL_RUNTIME_CONTEXT_ATTR)
    if cached is not _CALLABLE_CACHE_MISSING:
        return cast(str | None, cached)

    found_name: str | None = None
    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):
        found_name = None
    else:
        for parameter in signature.parameters.values():
            annotation = parameter.annotation
            annotation_name = getattr(annotation, "__forward_arg__", annotation)
            if annotation is PlainCallRuntimeContext or annotation_name == "PlainCallRuntimeContext":
                if found_name is not None:
                    raise TypeError("plain-call runtime context injection supports only one annotated parameter")
                found_name = parameter.name

    _write_callable_annotation_cache(func, _PLAIN_CALL_RUNTIME_CONTEXT_ATTR, found_name)
    return found_name


def _select_plain_call_handler(result: object) -> PlainCallSemanticsHandler:
    matches = [handler for handler in _PLAIN_CALL_HANDLERS if handler.can_handle(result)]
    if len(matches) != 1:
        raise TypeError(f"plain-call result matched {len(matches)} handlers instead of exactly one")
    return matches[0]


@dataclass(slots=True)
class _InvalidationScheduler:
    queue: list[RenderContext] = field(default_factory=list)
    deferred: list[RenderContext] = field(default_factory=list)
    active: list[RenderContext] = field(default_factory=list)

    def request(self, boundary: RenderContext) -> None:
        if self._is_blocked_by_active(boundary):
            self._merge_boundary(self.deferred, boundary)
            return
        self._merge_boundary(self.queue, boundary)

    def enter_active(self, boundary: RenderContext) -> None:
        self.active.append(boundary)

    def exit_active(self, boundary: RenderContext) -> None:
        if self.active and self.active[-1] is boundary:
            self.active.pop()
        else:
            self.active = [active for active in self.active if active is not boundary]
        self._promote_deferred()

    def pop_next(self) -> RenderContext | None:
        if not self.queue:
            return None
        return self.queue.pop(0)

    def has_pending_work(self) -> bool:
        return bool(self.queue or self.deferred)

    def remove(self, boundary: RenderContext) -> None:
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

    def _is_blocked_by_active(self, boundary: RenderContext) -> bool:
        return any(active._is_ancestor_boundary_of(boundary) for active in self.active)

    def _merge_boundary(
        self,
        targets: list[RenderContext],
        boundary: RenderContext,
    ) -> None:
        if any(queued._is_ancestor_boundary_of(boundary) for queued in targets):
            return

        targets[:] = [
            queued for queued in targets if not boundary._is_ancestor_boundary_of(queued)
        ]
        if any(queued is boundary for queued in targets):
            return
        targets.append(boundary)


class ContextBase:
    def __init__(self, render_context: RenderContext) -> None:
        self._render_context = render_context
        self._children: dict[SlotId, SlotContext] = {}
        self._literal_initialized: list[bool] = []
        self._literal_index = 0
        self._scope_active = False
        self._pass_child_order: tuple[SlotId, ...] = ()
        self._pass_child_dirty: dict[SlotId, bool] = {}
        self._committed_ui: tuple[UIElement | MountDirective, ...] = ()
        self._own_committed_ui: tuple[UIElement | MountDirective, ...] = ()
        self._own_committed_ui_entries: tuple[_CommittedUiEntry, ...] = ()
        self._pass_committed_ui: tuple[UIElement | MountDirective, ...] = ()
        self._pass_own_committed_ui: tuple[UIElement | MountDirective, ...] = ()
        self._pass_own_committed_ui_entries: tuple[_CommittedUiEntry, ...] = ()
        self._staged_ui: list[UIElement | MountDirective] = []
        self._staged_ui_entries: list[_CommittedUiEntry] = []

    @property
    def root_context(self) -> RenderContext:
        return self._render_context

    def get_app_context(self, key: AppContextKey[T]) -> T:
        return self.root_context._scheduler_root._app_context_store.get(key)

    def has_app_context(self, key: AppContextKey[Any]) -> bool:
        return self.root_context._scheduler_root._app_context_store.has(key)

    def get_authored_app_context(self, key: AppContextKey[T]) -> T:
        return self._effective_authored_app_context_lookup().get(key)

    def has_authored_app_context(self, key: AppContextKey[Any]) -> bool:
        return self._effective_authored_app_context_lookup().has(key)

    def current_generation_id(self) -> int:
        tracker = self.get_app_context(GENERATION_TRACKER_KEY)
        return tracker.current()

    def current_slot_id(self) -> SlotId | None:
        slot_id = getattr(self, "slot_id", None)
        return slot_id if isinstance(slot_id, SlotId) else None

    def _effective_authored_app_context_lookup(self) -> AppContextLookup:
        parent = getattr(self, "parent", None)
        if isinstance(parent, ContextBase):
            return parent._effective_authored_app_context_lookup()
        if isinstance(self, RenderContext):
            return self._authored_app_context_lookup
        return EMPTY_APP_CONTEXT_LOOKUP

    def context_kind(self) -> str:
        return _context_kind(self)

    def pass_scope(self) -> _PassScopeHandle:
        return _PassScopeHandle(context=self, activate=not self._scope_active)

    def begin_pass(self) -> None:
        self._begin_scope_pass()

    def end_pass(self) -> None:
        self._commit_scope_pass()

    def rollback_pass(self) -> None:
        self._rollback_scope_pass()

    def literal(self, value: T) -> CompValue[T]:
        self._require_active_scope()

        literal_index = self._literal_index
        self._literal_index += 1

        if literal_index == len(self._literal_initialized):
            self._literal_initialized.append(True)
            return CompValue(value=value, dirty=True)

        return CompValue(value=value, dirty=False)

    def visit_slot_and_dirty(self, slot_id: SlotId) -> bool:
        self._require_active_scope()
        slot = self._ensure_slot(slot_id, SlotContext)
        return slot.invoke_dirty

    def keyed_loop(
        self,
        slot_id: SlotId,
        values: CompValue[list[T]] | list[T],
        *,
        key_fn: Callable[[T], Any],
    ) -> _KeyedLoopIterable[T]:
        self._require_active_scope()
        loop_slot = self._ensure_slot(slot_id, KeyedLoopSlotContext)
        raw_values, _ = _unwrap(values)
        return _KeyedLoopIterable(
            owner=loop_slot,
            values=tuple(cast(list[T], raw_values)),
            key_fn=key_fn,
        )

    def call_plain(
        self,
        slot_id: SlotId,
        func: CompValue[Callable[..., T]] | Callable[..., T],
        *args: CompValue[Any] | Any,
        result_shape: object | None = None,
        **kwargs: CompValue[Any] | Any,
    ) -> PlainCallResult[T]:
        self._require_active_scope()
        slot = self._ensure_slot(slot_id, PlainCallSlotContext)
        return slot.evaluate(func, args, kwargs, result_shape=result_shape)

    def container_call(
        self,
        slot_id: SlotId,
        container_fn: CompValue[Callable[..., Any]] | Callable[..., Any],
        *args: CompValue[Any] | Any,
        dirty_state: DirtyStateContext | None = None,
        **kwargs: CompValue[Any] | Any,
    ) -> _ContainerCallHandle:
        self._require_active_scope()
        slot = self._ensure_slot(slot_id, ContainerSlotContext)
        raw_container_fn, _ = _unwrap(container_fn)
        metadata, bound_receiver = _component_call_key(raw_container_fn)
        runtime_func = _resolve_runtime_component_func(getattr(metadata, "_func", None))
        if metadata is not None and runtime_func is not None:
            raw_args = tuple(_unwrap(arg)[0] for arg in args)
            raw_kwargs = {key: _unwrap(value)[0] for key, value in kwargs.items()}
            return _PyrolyzeContainerCallHandle(
                slot=slot,
                runtime_func=runtime_func,
                bound_receiver=bound_receiver,
                args=raw_args,
                kwargs=raw_kwargs,
                dirty_state=dirty_state or dirtyof(),
                packed_kwargs=bool(getattr(metadata, "packed_kwargs", False)),
                packed_kwarg_param_names=tuple(getattr(metadata, "packed_kwarg_param_names", ())),
            )
        native_context_param = _native_context_param_name(cast(Callable[..., Any], raw_container_fn))
        if native_context_param is not None:
            raw_args = tuple(_unwrap(arg)[0] for arg in args)
            raw_kwargs = {key: _unwrap(value)[0] for key, value in kwargs.items()}
            return _NativeContainerCallHandle(
                slot=slot,
                container_fn=cast(Callable[..., Any], raw_container_fn),
                args=raw_args,
                kwargs=raw_kwargs,
                context_param=native_context_param,
            )
        raw_args = tuple(_unwrap(arg)[0] for arg in args)
        raw_kwargs = {key: _unwrap(value)[0] for key, value in kwargs.items()}
        return _ContainerCallHandle(
            slot=slot,
            container_fn=cast(Callable[..., Any], raw_container_fn),
            args=raw_args,
            kwargs=raw_kwargs,
        )

    def open_directive(
        self,
        slot_id: SlotId,
        directive_fn: CompValue[Callable[..., Any]] | Callable[..., Any],
        *args: CompValue[Any] | Any,
        **kwargs: CompValue[Any] | Any,
    ) -> _DirectiveCallHandle:
        self._require_active_scope()
        slot = self._ensure_slot(slot_id, DirectiveSlotContext)
        return _DirectiveCallHandle(
            slot=slot,
            directive_fn=directive_fn,
            args=args,
            kwargs=kwargs,
        )

    def open_app_context_override(
        self,
        slot_id: SlotId,
        keys: tuple[AppContextKey[Any], ...],
        *values: Any,
    ) -> _AppContextOverrideHandle:
        self._require_active_scope()
        slot = self._ensure_slot(slot_id, AppContextOverrideSlotContext)
        return _AppContextOverrideHandle(
            slot=slot,
            keys=keys,
            values=values,
        )

    def leaf_call(
        self,
        slot_id: SlotId,
        leaf_fn: CompValue[Callable[..., Any]] | Callable[..., Any],
        *args: CompValue[Any] | Any,
        **kwargs: CompValue[Any] | Any,
    ) -> Any:
        self._require_active_scope()
        slot = self._ensure_slot(slot_id, LeafSlotContext)
        raw_leaf_fn, _ = _unwrap(leaf_fn)
        native_context_param = _native_context_param_name(cast(Callable[..., Any], raw_leaf_fn))
        if native_context_param is not None:
            raw_args = tuple(_unwrap(arg)[0] for arg in args)
            raw_kwargs = {key: _unwrap(value)[0] for key, value in kwargs.items()}
            return slot.invoke_native(
                cast(Callable[..., Any], raw_leaf_fn),
                raw_args,
                raw_kwargs,
                context_param=native_context_param,
            )
        raw_args = tuple(_unwrap(arg)[0] for arg in args)
        raw_kwargs = {key: _unwrap(value)[0] for key, value in kwargs.items()}
        return slot.invoke(cast(Callable[..., Any], raw_leaf_fn), raw_args, raw_kwargs)

    def component_call(
        self,
        slot_id: SlotId,
        component: CompValue[Callable[..., Any]] | Callable[..., Any],
        *args: CompValue[Any] | Any,
        dirty_state: DirtyStateContext | None = None,
        **kwargs: CompValue[Any] | Any,
    ) -> None:
        self._require_active_scope()
        slot = self._ensure_slot(slot_id, ComponentCallSlotContext)
        slot.invoke(component, args, kwargs, dirty_state=dirty_state)

    def event_handler(
        self,
        slot_id: SlotId,
        *,
        dirty: bool,
        callback: Callable[..., Any],
    ) -> Callable[..., None]:
        self._require_active_scope()
        slot = self._ensure_slot(slot_id, EventHandlerSlotContext)
        return slot.stage_callback(callback=callback, dirty=dirty)

    def event_handler_binding(
        self,
        slot_id: SlotId,
        *,
        dirty: bool,
        callback: Callable[..., Any],
    ) -> PendingEventHandlerBinding:
        self._require_active_scope()
        return PendingEventHandlerBinding(
            slot_id=self._resolve_slot_id(slot_id),
            dirty=dirty,
            callback=callback,
        )

    def _begin_scope_pass(self) -> None:
        if self._scope_active:
            raise RuntimeError("scope already active")

        self._scope_active = True
        self._literal_index = 0
        self._pass_child_order = tuple(self._children.keys())
        self._pass_child_dirty = {
            slot_id: child.invoke_dirty for slot_id, child in self._children.items()
        }
        self._pass_committed_ui = self._committed_ui
        self._pass_own_committed_ui = self._own_committed_ui
        self._pass_own_committed_ui_entries = self._own_committed_ui_entries
        if isinstance(self, ContainerSlotContext):
            self._pass_committed_native_root = self.committed_native_root
        self._staged_ui = []
        self._staged_ui_entries = []
        for child in self._children.values():
            child.seen_in_pass = False

    def _commit_scope_pass(self) -> None:
        if not self._scope_active:
            raise RuntimeError("scope is not active")

        unseen_slots = [slot_id for slot_id, child in self._children.items() if not child.seen_in_pass]
        for slot_id in unseen_slots:
            child = self._children.get(slot_id)
            if child is not None:
                child.deactivate()

        for child in self._children.values():
            if isinstance(child, PlainCallSlotContext):
                child.commit_binding()
            elif isinstance(child, EventHandlerSlotContext):
                child.commit_handler()
            elif isinstance(child, ComponentCallSlotContext):
                child.commit_owned_event_handlers()

        self._own_committed_ui_entries = tuple(self._staged_ui_entries)
        self._own_committed_ui = tuple(entry.element for entry in self._own_committed_ui_entries)
        self._committed_ui = self._build_committed_ui()
        if isinstance(self, ContainerSlotContext):
            self.committed_native_root = self.expects_native_root

        for child in self._children.values():
            child.invoke_dirty = False

        self._scope_active = False
        self._pass_child_order = ()
        self._pass_child_dirty = {}
        self._pass_committed_ui = ()
        self._pass_own_committed_ui = ()
        self._pass_own_committed_ui_entries = ()
        self._staged_ui = []
        self._staged_ui_entries = []

    def _rollback_scope_pass(self) -> None:
        if not self._scope_active:
            raise RuntimeError("scope is not active")

        committed_ids = set(self._pass_child_order)
        for slot_id, child in list(self._children.items()):
            if slot_id not in committed_ids:
                child.deactivate()
                continue

            if isinstance(child, PlainCallSlotContext):
                child.rollback_binding()
            elif isinstance(child, EventHandlerSlotContext):
                child.rollback_handler()
            elif isinstance(child, ComponentCallSlotContext):
                child.rollback_owned_event_handlers()
            child.invoke_dirty = self._pass_child_dirty.get(slot_id, child.invoke_dirty)
            child.seen_in_pass = True

        restored_children: dict[SlotId, SlotContext] = {}
        for slot_id in self._pass_child_order:
            child = self._children.get(slot_id)
            if child is not None:
                restored_children[slot_id] = child
        self._children = restored_children
        self._committed_ui = self._pass_committed_ui
        self._own_committed_ui = self._pass_own_committed_ui
        self._own_committed_ui_entries = self._pass_own_committed_ui_entries
        if isinstance(self, ContainerSlotContext):
            self.committed_native_root = self._pass_committed_native_root

        self._scope_active = False
        self._pass_child_order = ()
        self._pass_child_dirty = {}
        self._pass_committed_ui = ()
        self._pass_own_committed_ui = ()
        self._pass_own_committed_ui_entries = ()
        self._staged_ui = []
        self._staged_ui_entries = []

    def _ensure_slot(self, slot_id: SlotId, slot_type: type[S]) -> S:
        resolved_slot_id = self._resolve_slot_id(slot_id)
        return self._ensure_resolved_slot(resolved_slot_id, slot_type)

    def _ensure_resolved_slot(self, slot_id: SlotId, slot_type: type[S]) -> S:
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
        return cast(S, existing)

    def _materialize_pending_event_handler(
        self,
        binding: PendingEventHandlerBinding,
    ) -> Callable[..., None]:
        slot = self._ensure_resolved_slot(binding.slot_id, EventHandlerSlotContext)
        return slot.stage_callback(callback=binding.callback, dirty=binding.dirty)

    def _require_active_scope(self) -> None:
        if not self._scope_active:
            raise RuntimeError("scope is not active")

    def call_native(
        self,
        factory: Callable[..., UIElement | None],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._require_active_scope()

        raw_args = tuple(_unwrap_native_value(arg) for arg in args)
        raw_kwargs = {key: _unwrap_native_value(value) for key, value in kwargs.items()}
        call_site_id = raw_kwargs.pop("__pyr_call_site_id", None)
        result = factory(*raw_args, **raw_kwargs)
        if result is None:
            return
        if isinstance(result, UIElement):
            source_slot_id = _native_emission_slot_identity(self)
            normalized_call_site_id = (
                result.call_site_id if call_site_id is None else cast(int | str, call_site_id)
            )
            normalized_slot_id = (
                result.slot_id
                if result.slot_id is not None
                else source_slot_id
            )
            if (
                result.call_site_id != normalized_call_site_id
                or result.slot_id != normalized_slot_id
            ):
                result = UIElement(
                    kind=result.kind,
                    props=result.props,
                    children=result.children,
                    call_site_id=normalized_call_site_id,
                    slot_id=normalized_slot_id,
                )
            self._staged_ui.append(result)
            self._staged_ui_entries.append(
                _CommittedUiEntry(
                    generation_id=self.current_generation_id(),
                    element=result,
                )
            )
            return
        if os.environ.get("PYROLYZE_ENV") == "prod":
            logging.getLogger(__name__).warning(
                "call_native ignored unsupported result type %s",
                type(result).__name__,
            )
            return
        raise TypeError("call_native factory must return UIElement or None")

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
            root = own_elements[0]
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

    def _resolve_slot_id(self, slot_id: SlotId) -> SlotId:
        runtime_key_path = self._runtime_key_path()
        return SlotId(
            module_id=slot_id.module_id,
            slot_index=slot_id.slot_index,
            key_path=runtime_key_path + slot_id.key_path,
            line_no=slot_id.line_no,
            is_top_level=slot_id.is_top_level,
        )

    def _runtime_key_path(self) -> tuple[Any, ...]:
        slot_id = getattr(self, "slot_id", None)
        if isinstance(slot_id, SlotId):
            return slot_id.key_path
        return ()

    def _refresh_committed_ui_from_children(self) -> None:
        self._committed_ui = self._build_committed_ui()
        parent = getattr(self, "parent", None)
        if isinstance(parent, ContextBase):
            parent._refresh_committed_ui_from_children()

_NATIVE_CONTEXT_PARAM_ATTR = "_pyrolyze_native_context_param"
_NATIVE_CONTEXT_ANNOTATIONS = {
    "ContextBase",
    "ContainerSlotContext",
    "LeafSlotContext",
    "RenderContext",
}

_BOUND_METHOD_SELF_MISSING = object()


def _native_context_param_name(func: Callable[..., Any]) -> str | None:
    cached = _read_callable_annotation_cache(func, _NATIVE_CONTEXT_PARAM_ATTR)
    if cached is not _CALLABLE_CACHE_MISSING:
        return cast(str | None, cached)

    found_name: str | None = None
    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):
        found_name = None
    else:
        parameters = tuple(signature.parameters.values())
        if parameters:
            first = parameters[0]
            annotation = first.annotation
            annotation_name = getattr(annotation, "__forward_arg__", annotation)
            if annotation_name in _NATIVE_CONTEXT_ANNOTATIONS:
                found_name = first.name
            elif isinstance(annotation, type) and issubclass(annotation, ContextBase):
                found_name = first.name

    _write_callable_annotation_cache(func, _NATIVE_CONTEXT_PARAM_ATTR, found_name)
    return found_name


def _callback_key(callback: Callable[..., Any]) -> object:
    bound_self = getattr(callback, "__self__", _BOUND_METHOD_SELF_MISSING)
    bound_func = getattr(callback, "__func__", None)
    if bound_self is not _BOUND_METHOD_SELF_MISSING and callable(bound_func):
        return ("bound_method", id(bound_self), bound_func)
    return callback


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


def _pack_component_kwargs(
    param_names: tuple[str, ...],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    if len(args) > len(param_names):
        raise TypeError("too many positional arguments for packed component call")
    packed = {param_names[index]: value for index, value in enumerate(args)}
    for key, value in kwargs.items():
        if key in packed:
            raise TypeError(f"multiple values for argument {key!r}")
        packed[key] = value
    return packed


def _resolve_runtime_component_func(runtime_func: object) -> Callable[..., Any] | None:
    if isinstance(runtime_func, (classmethod, staticmethod)):
        candidate = runtime_func.__func__
        return candidate if callable(candidate) else None
    return cast(Callable[..., Any] | None, runtime_func if callable(runtime_func) else None)


def _native_emission_slot_identity(context: ContextBase) -> object | None:
    current_slot_id = context.current_slot_id()
    # Emissions from nested component boundaries can share the same local slot
    # identity (for example repeated helper trees), so include owner boundaries.
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
        return tuple(owner_slot_path)
    if isinstance(current_slot_id, SlotId):
        return current_slot_id
    return None


def _bind_pending_event_plain_value(owner: ContextBase, value: Any) -> Any:
    if isinstance(value, PendingEventHandlerBinding):
        return owner._materialize_pending_event_handler(value)
    return value


def _bind_pending_event_comp_value(owner: ContextBase, value: CompValue[Any]) -> CompValue[Any]:
    if isinstance(value.value, PendingEventHandlerBinding):
        return CompValue(
            value=owner._materialize_pending_event_handler(value.value),
            dirty=value.dirty,
        )
    return value


@dataclass(slots=True)
class SlotContext:
    render_context: RenderContext
    parent: ContextBase
    slot_id: SlotId
    invoke_dirty: bool = True
    seen_in_pass: bool = False

    def current_slot_id(self) -> SlotId:
        return self.slot_id

    def current_generation_id(self) -> int:
        return self.render_context.current_generation_id()

    def context_kind(self) -> str:
        return _context_kind(self)

    def visit_self_and_dirty(self) -> bool:
        if not isinstance(self, ContextBase):
            raise RuntimeError("slot is not a structural context")
        self._require_active_scope()
        return self.invoke_dirty

    def deactivate(self) -> None:
        if isinstance(self, ContextBase):
            for child in list(self._children.values()):
                child.deactivate()
            self._children.clear()

        self.render_context._slots_by_id.pop(self.slot_id, None)
        if self.parent._children.get(self.slot_id) is self:
            self.parent._children.pop(self.slot_id, None)


@dataclass(slots=True)
class EventHandlerSlotContext(SlotContext):
    committed_callback: Callable[..., Any] | None = None
    committed_key: object | None = None
    staged_callback: Callable[..., Any] | None = None
    staged_key: object | None = None
    dispatch: Callable[..., None] | None = None

    def stage_callback(
        self,
        *,
        callback: Callable[..., Any],
        dirty: bool,
    ) -> Callable[..., None]:
        callback_key = _callback_key(callback)
        if dirty or self.committed_callback is None or self.committed_key != callback_key:
            self.staged_callback = callback
            self.staged_key = callback_key
        return self._dispatch_callable()

    def commit_handler(self) -> None:
        if self.staged_callback is None:
            return
        self.committed_callback = self.staged_callback
        self.committed_key = self.staged_key
        self.staged_callback = None
        self.staged_key = None

    def rollback_handler(self) -> None:
        self.staged_callback = None
        self.staged_key = None

    def deactivate(self) -> None:
        self.staged_callback = None
        self.staged_key = None
        self.committed_callback = None
        self.committed_key = None
        super(EventHandlerSlotContext, self).deactivate()

    def _dispatch_callable(self) -> Callable[..., None]:
        if self.dispatch is None:
            def dispatch(*args: Any, **kwargs: Any) -> None:
                callback = self.committed_callback
                if callback is None:
                    if os.environ.get("PYROLYZE_ENV") == "prod":
                        return
                    raise RuntimeError("event handler is inactive")
                callback(*args, **kwargs)

            self.dispatch = dispatch
        return self.dispatch


@dataclass(slots=True)
class RerunnableSlotContext(SlotContext, ContextBase):
    def __post_init__(self) -> None:
        ContextBase.__init__(self, self.render_context)


@dataclass(slots=True)
class PlainCallSlotContext(RerunnableSlotContext):
    function_identity: Any = None
    schema: tuple[int, tuple[str, ...]] = (0, ())
    last_args: tuple[Any, ...] = ()
    last_kwargs: tuple[tuple[str, Any], ...] = ()
    binding: PlainCallBinding | None = None
    _runtime_locals: dict[str, Any] = field(default_factory=dict)

    def evaluate(
        self,
        func: CompValue[Callable[..., T]] | Callable[..., T],
        args: tuple[CompValue[Any] | Any, ...],
        kwargs: dict[str, CompValue[Any] | Any],
        *,
        result_shape: object | None = None,
    ) -> PlainCallResult[T]:
        raw_func, func_dirty = _unwrap(func)
        normalized_args = tuple(_unwrap(arg) for arg in args)
        normalized_kwargs = {key: _unwrap(value) for key, value in kwargs.items()}

        raw_args = tuple(value for value, _ in normalized_args)
        raw_kwargs = {key: value for key, (value, _) in normalized_kwargs.items()}
        kwargs_items = tuple(sorted(raw_kwargs.items()))
        schema = (len(raw_args), tuple(sorted(raw_kwargs)))

        should_invoke = (
            self.invoke_dirty
            or func_dirty
            or any(dirty for _, dirty in normalized_args)
            or any(dirty for _, dirty in normalized_kwargs.values())
            or self.binding is None
            or self.function_identity is not raw_func
            or self.schema != schema
            or self.last_args != raw_args
            or self.last_kwargs != kwargs_items
        )

        if should_invoke:
            call_kwargs = dict(raw_kwargs)
            runtime_context_param = _plain_call_runtime_context_param_name(cast(Callable[..., Any], raw_func))
            if runtime_context_param is not None and runtime_context_param not in call_kwargs:
                call_kwargs[runtime_context_param] = PlainCallRuntimeContext(self)

            next_result = cast(Callable[..., T], raw_func)(*raw_args, **call_kwargs)
            result_dirty = self._commit_evaluated_result(next_result)
            self.function_identity = raw_func
            self.schema = schema
            self.last_args = raw_args
            self.last_kwargs = kwargs_items
        else:
            result_dirty = False
            binding = self.binding
            if binding is not None:
                refreshed = binding.refresh()
                if refreshed is not None:
                    _, result_dirty = refreshed

        binding = self.binding
        if binding is None:
            raise RuntimeError("plain-call slot has no binding after evaluation")
        return PlainCallResult(
            dirty=_project_dirty_state(result_dirty, result_shape),
            value=cast(T, binding.exposed_value()),
        )

    def _commit_evaluated_result(self, next_result: T) -> bool:
        previous_binding = self.binding
        previous_value = previous_binding.exposed_value() if previous_binding is not None else object()
        handler = _select_plain_call_handler(next_result)
        next_binding = handler.bind(self, next_result, previous_binding)
        next_value = next_binding.exposed_value()
        result_dirty = previous_binding is None or (next_value != previous_value)

        if previous_binding is not None and next_binding is not previous_binding:
            previous_binding.deactivate()

        self.binding = next_binding
        return result_dirty

    def _mark_binding_dirty(self) -> None:
        self.render_context._queue_invalidation_from(self, include_source=False)

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
        super(PlainCallSlotContext, self).deactivate()

    def _build_committed_ui(self) -> tuple[object, ...]:
        binding = self.binding
        if isinstance(binding, PyrolyzeMountAdvertisementBinding):
            advertisement = binding.retained_advertisement()
            if advertisement is None:
                return ()
            return (advertisement,)
        return super(PlainCallSlotContext, self)._build_committed_ui()

    def _sync_binding_committed_ui(self) -> None:
        self._committed_ui = self._build_committed_ui()


@dataclass(slots=True)
class DirectiveSlotContext(PlainCallSlotContext):
    committed_selectors: tuple[SlotSelector, ...] = ()
    _pass_committed_selectors: tuple[SlotSelector, ...] = ()

    def evaluate_directive(
        self,
        directive_fn: CompValue[Callable[..., Any]] | Callable[..., Any],
        args: tuple[CompValue[Any] | Any, ...],
        kwargs: dict[str, CompValue[Any] | Any],
    ) -> tuple[SlotSelector, ...]:
        result = self.evaluate(directive_fn, args, kwargs)
        selectors = tuple(result.value)
        for selector in selectors:
            if not isinstance(selector, SlotSelector):
                raise TypeError("mount directive evaluator must return SlotSelector values")
        return selectors

    def pending_selectors(self) -> tuple[SlotSelector, ...]:
        binding = self.binding
        if binding is None:
            return self.committed_selectors
        selectors = tuple(binding.exposed_value())
        for selector in selectors:
            if not isinstance(selector, SlotSelector):
                raise TypeError("mount directive evaluator must return SlotSelector values")
        return selectors

    def has_pending_emitted_children(self) -> bool:
        if self._staged_ui_entries:
            return True
        return any(
            isinstance(child, ContextBase) and bool(child._committed_ui)
            for child in self._children.values()
        )

    def _begin_scope_pass(self) -> None:
        self._pass_committed_selectors = self.committed_selectors
        super(DirectiveSlotContext, self)._begin_scope_pass()

    def _commit_scope_pass(self) -> None:
        self.committed_selectors = self.pending_selectors()
        super(DirectiveSlotContext, self)._commit_scope_pass()
        self._pass_committed_selectors = ()

    def _rollback_scope_pass(self) -> None:
        super(DirectiveSlotContext, self)._rollback_scope_pass()
        self.committed_selectors = self._pass_committed_selectors
        self._pass_committed_selectors = ()

    def _build_committed_ui(self) -> tuple[MountDirective, ...]:
        own_children = tuple(entry.element for entry in self._own_committed_ui_entries)
        nested_children = tuple(
            element
            for child in self._children.values()
            if isinstance(child, ContextBase)
            for element in child._committed_ui
        )
        return (
            MountDirective(
                selectors=self.committed_selectors,
                children=own_children + nested_children,
                slot_id=self.slot_id,
            ),
        )


def _empty_authored_app_context_lookup() -> AppContextLookup:
    return EMPTY_APP_CONTEXT_LOOKUP


@dataclass(slots=True)
class AppContextOverrideSlotContext(RerunnableSlotContext):
    declared_keys: tuple[AppContextKey[Any], ...] = ()
    committed_values: tuple[Any, ...] = ()
    _committed_lookup: AppContextLookup = field(default_factory=_empty_authored_app_context_lookup)
    _pass_committed_values: tuple[Any, ...] = ()
    _pass_committed_lookup: AppContextLookup = field(default_factory=_empty_authored_app_context_lookup)
    _pending_values: tuple[Any, ...] = ()
    _pending_lookup: AppContextLookup = field(default_factory=_empty_authored_app_context_lookup)
    _pending_initialized: bool = False

    def stage_override(
        self,
        keys: tuple[AppContextKey[Any], ...],
        values: tuple[Any, ...],
    ) -> None:
        self._validate_override(keys, values)
        if self.declared_keys and self.declared_keys != keys:
            raise AppContextOverrideStructureError(
                "app_context_override fixed keys cannot change at one slot"
            )
        if not self.declared_keys:
            self.declared_keys = keys
        self._pending_values = values
        self._pending_lookup = OverlayAppContextLookup(
            parent=self.parent._effective_authored_app_context_lookup(),
            values={key: value for key, value in zip(keys, values, strict=True)},
        )
        self._pending_initialized = True

    def _effective_authored_app_context_lookup(self) -> AppContextLookup:
        if self._scope_active and self._pending_initialized:
            return self._pending_lookup
        if self.declared_keys:
            return self._committed_lookup
        return super()._effective_authored_app_context_lookup()

    def _begin_scope_pass(self) -> None:
        self._pass_committed_values = self.committed_values
        self._pass_committed_lookup = self._committed_lookup
        super(AppContextOverrideSlotContext, self)._begin_scope_pass()

    def _commit_scope_pass(self) -> None:
        if not self._pending_initialized:
            raise RuntimeError("app_context_override slot was not staged")
        self.committed_values = self._pending_values
        self._committed_lookup = self._pending_lookup
        super(AppContextOverrideSlotContext, self)._commit_scope_pass()
        self._pending_values = ()
        self._pending_lookup = EMPTY_APP_CONTEXT_LOOKUP
        self._pending_initialized = False
        self._pass_committed_values = ()
        self._pass_committed_lookup = EMPTY_APP_CONTEXT_LOOKUP

    def _rollback_scope_pass(self) -> None:
        super(AppContextOverrideSlotContext, self)._rollback_scope_pass()
        self.committed_values = self._pass_committed_values
        self._committed_lookup = self._pass_committed_lookup
        self._pending_values = ()
        self._pending_lookup = EMPTY_APP_CONTEXT_LOOKUP
        self._pending_initialized = False
        self._pass_committed_values = ()
        self._pass_committed_lookup = EMPTY_APP_CONTEXT_LOOKUP

    def deactivate(self) -> None:
        self._pending_values = ()
        self._pending_lookup = EMPTY_APP_CONTEXT_LOOKUP
        self._pending_initialized = False
        super(AppContextOverrideSlotContext, self).deactivate()

    def _validate_override(
        self,
        keys: tuple[AppContextKey[Any], ...],
        values: tuple[Any, ...],
    ) -> None:
        if not keys:
            raise AppContextOverrideStructureError("app_context_override requires at least one key")
        if len(keys) != len(values):
            raise AppContextOverrideStructureError(
                "app_context_override key/value arity must match"
            )
        seen: set[AppContextKey[Any]] = set()
        for key in keys:
            if not isinstance(key, AppContextKey):
                raise AppContextOverrideStructureError(
                    "app_context_override keys must be AppContextKey instances"
                )
            if key in seen:
                raise AppContextOverrideStructureError(
                    f"app_context_override duplicate key {key.debug_name!r}"
                )
            seen.add(key)


@dataclass(slots=True)
class ContainerSlotContext(RerunnableSlotContext):
    expects_native_root: bool = False
    committed_native_root: bool = False
    _pass_committed_native_root: bool = False


@dataclass(slots=True)
class ComponentCallSlotContext(RerunnableSlotContext):
    component_identity: Any = None
    schema: tuple[int, tuple[str, ...]] = (0, ())
    child_context: RenderContext | None = None
    last_runtime_func: Callable[..., Any] | None = None
    last_bound_receiver: object = _BOUND_METHOD_SELF_MISSING
    last_args: tuple[CompValue[Any], ...] = ()
    last_kwargs: dict[str, CompValue[Any]] = field(default_factory=dict)
    last_plain_args: tuple[Any, ...] = ()
    last_plain_kwargs: dict[str, Any] = field(default_factory=dict)
    last_dirty_state: DirtyStateContext | None = None
    pending_dirty_state: DirtyStateContext | None = None
    uses_dirty_state_api: bool = False
    packed_kwargs: bool = False
    packed_kwarg_param_names: tuple[str, ...] = ()
    _pass_owned_event_handler_order: tuple[SlotId, ...] = ()

    def invoke(
        self,
        component: CompValue[Callable[..., Any]] | Callable[..., Any],
        args: tuple[CompValue[Any] | Any, ...],
        kwargs: dict[str, CompValue[Any] | Any],
        *,
        dirty_state: DirtyStateContext | None = None,
    ) -> None:
        raw_component, _ = _unwrap(component)
        metadata, bound_receiver = _component_call_key(raw_component)
        runtime_func = _resolve_runtime_component_func(getattr(metadata, "_func", None))
        if metadata is None or runtime_func is None:
            raise TypeError("component_call expects a ComponentRef with _pyrolyze_meta._func")

        if bound_receiver is _BOUND_METHOD_SELF_MISSING:
            identity_key = raw_component
        else:
            underlying = getattr(raw_component, "__func__", None)
            identity_key = ("bound_component", id(bound_receiver), underlying)

        schema = (len(args), tuple(sorted(kwargs)))
        if (
            self.child_context is None
            or self.component_identity != identity_key
            or self.schema != schema
        ):
            self._dispose_child_context()
            self.child_context = RenderContext(
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
            self.packed_kwargs = bool(getattr(metadata, "packed_kwargs", False))
            self.packed_kwarg_param_names = tuple(
                getattr(metadata, "packed_kwarg_param_names", ())
            )
            if dirty_state is None:
                normalized_args = tuple(
                    _bind_pending_event_comp_value(self, _wrap_comp_value(arg))
                    for arg in args
                )
                normalized_kwargs = {
                    key: _bind_pending_event_comp_value(self, _wrap_comp_value(value))
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
                self.last_plain_args = tuple(
                    _bind_pending_event_plain_value(self, _unwrap(arg)[0])
                    for arg in args
                )
                self.last_plain_kwargs = {
                    key: _bind_pending_event_plain_value(self, _unwrap(value)[0])
                    for key, value in kwargs.items()
                }
                self.last_dirty_state = dirty_state
                self.pending_dirty_state = dirty_state
                self.last_args = ()
                self.last_kwargs = {}
                self.uses_dirty_state_api = True
            self.child_context._authored_app_context_lookup = (
                self.parent._effective_authored_app_context_lookup()
            )
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
                dirty_state = _clean_dirty_state(self.last_dirty_state)
            else:
                self.pending_dirty_state = None
            if self.packed_kwargs:
                packed_kwargs = _pack_component_kwargs(
                    self.packed_kwarg_param_names,
                    self.last_plain_args,
                    self.last_plain_kwargs,
                )
                if self.last_bound_receiver is _BOUND_METHOD_SELF_MISSING:
                    runtime_func(
                        child_context,
                        dirty_state,
                        **packed_kwargs,
                    )
                else:
                    runtime_func(
                        self.last_bound_receiver,
                        child_context,
                        dirty_state,
                        **packed_kwargs,
                    )
                self._committed_ui = child_context._committed_ui
                if not self.parent._scope_active:
                    self.parent._refresh_committed_ui_from_children()
                return
            if self.last_bound_receiver is _BOUND_METHOD_SELF_MISSING:
                runtime_func(
                    child_context,
                    dirty_state,
                    *self.last_plain_args,
                    **self.last_plain_kwargs,
                )
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
            packed_kwargs = _pack_component_kwargs(
                self.packed_kwarg_param_names,
                self.last_args,
                self.last_kwargs,
            )
            if self.last_bound_receiver is _BOUND_METHOD_SELF_MISSING:
                runtime_func(child_context, **packed_kwargs)
            else:
                runtime_func(
                    self.last_bound_receiver,
                    child_context,
                    **packed_kwargs,
                )
            self._committed_ui = child_context._committed_ui
            if not self.parent._scope_active:
                self.parent._refresh_committed_ui_from_children()
            return

        if self.last_bound_receiver is _BOUND_METHOD_SELF_MISSING:
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
        super(ComponentCallSlotContext, self).deactivate()


@dataclass(slots=True)
class KeyedLoopSlotContext(RerunnableSlotContext):
    pass


@dataclass(slots=True)
class LoopItemSlotContext(RerunnableSlotContext):
    current: Any = None
    current_dirty: Any = True
    current_initialized: bool = False

    def current_value(self) -> PlainCallResult[Any]:
        self._require_active_scope()
        return PlainCallResult(dirty=self.current_dirty, value=self.current)

    def update_current(self, value: Any) -> None:
        self.current_dirty = _structured_dirty_projection(
            previous=self.current,
            current=value,
            initialized=self.current_initialized,
        )
        self.current = value
        self.current_initialized = True


@dataclass(slots=True)
class LeafSlotContext(RerunnableSlotContext):
    last_args: tuple[Any, ...] = ()
    last_kwargs: tuple[tuple[str, Any], ...] = ()

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
    directive_fn: CompValue[Callable[..., Any]] | Callable[..., Any]
    args: tuple[CompValue[Any] | Any, ...]
    kwargs: dict[str, CompValue[Any] | Any]

    def __enter__(self) -> DirectiveSlotContext:
        self.slot._begin_scope_pass()
        try:
            self.slot.evaluate_directive(
                self.directive_fn,
                self.args,
                self.kwargs,
            )
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
    packed_kwargs: bool = False
    packed_kwarg_param_names: tuple[str, ...] = ()

    def __enter__(self) -> ContainerSlotContext:
        self.slot.expects_native_root = True
        self.slot._begin_scope_pass()
        try:
            bound_args = tuple(_bind_pending_event_plain_value(self.slot, value) for value in self.args)
            bound_kwargs = {
                key: _bind_pending_event_plain_value(self.slot, value)
                for key, value in self.kwargs.items()
            }
            if self.packed_kwargs:
                packed_kwargs = _pack_component_kwargs(
                    self.packed_kwarg_param_names,
                    bound_args,
                    bound_kwargs,
                )
                if self.bound_receiver is _BOUND_METHOD_SELF_MISSING:
                    result = self.runtime_func(
                        self.slot,
                        self.dirty_state,
                        **packed_kwargs,
                    )
                else:
                    result = self.runtime_func(
                        self.bound_receiver,
                        self.slot,
                        self.dirty_state,
                        **packed_kwargs,
                    )
            else:
                if self.bound_receiver is _BOUND_METHOD_SELF_MISSING:
                    result = self.runtime_func(
                        self.slot,
                        self.dirty_state,
                        *bound_args,
                        **bound_kwargs,
                    )
                else:
                    result = self.runtime_func(
                        self.bound_receiver,
                        self.slot,
                        self.dirty_state,
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


@dataclass(slots=True)
class _PassScopeHandle(AbstractContextManager[None]):
    context: ContextBase
    activate: bool = True

    def __enter__(self) -> None:
        if self.activate:
            self.context.begin_pass()
        return None

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        if self.activate:
            _finish_context_pass(self.context, commit=exc_type is None)
        return False


def _finish_context_pass(context: ContextBase, *, commit: bool) -> None:
    if not commit:
        context.rollback_pass()
        return
    try:
        context.end_pass()
    except BaseException:
        if getattr(context, "_scope_active", False):
            context.rollback_pass()
        raise


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

    def __iter__(self):
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


class RenderContext(ContextBase):
    def __init__(
        self,
        *,
        owner_slot: ComponentCallSlotContext | None = None,
        scheduler_root: RenderContext | None = None,
        app_context_store: AppContextStore | None = None,
        authored_app_context_lookup: AppContextLookup | None = None,
    ) -> None:
        self._slots_by_id: dict[SlotId, SlotContext] = {}
        self._mount_advertisements_by_slot: dict[SlotId, PyrolyzeMountAdvertisement] = {}
        self._owner_slot = owner_slot
        self._mounted_callback: Callable[[], None] | None = None
        self._post_commit_callbacks: list[Callable[[], None]] = []
        self._flush_poster: Callable[[Callable[[], None]], None] | None = None
        self._flush_posted = False
        self._flush_running = False
        if scheduler_root is None:
            self._scheduler_root = self
            self._scheduler = _InvalidationScheduler()
            self._app_context_store = app_context_store or AppContextStore()
            self._authored_app_context_lookup = (
                authored_app_context_lookup or EMPTY_APP_CONTEXT_LOOKUP
            )
        else:
            self._scheduler_root = scheduler_root
            self._scheduler = scheduler_root._scheduler
            self._app_context_store = scheduler_root._app_context_store
            self._authored_app_context_lookup = (
                authored_app_context_lookup or scheduler_root._authored_app_context_lookup
            )
        super().__init__(self)

    def pass_scope(self) -> _PassScopeHandle:
        return _PassScopeHandle(context=self, activate=not self._scope_active)

    def mount(self, callback: Callable[[], None]) -> None:
        self._mounted_callback = callback
        self._run_boundary()

    def set_flush_poster(self, post: Callable[[Callable[[], None]], None]) -> None:
        self._scheduler_root._flush_poster = post

    def run_pending_invalidations(self) -> None:
        scheduler_root = self._scheduler_root
        scheduler = scheduler_root._scheduler
        if scheduler_root._flush_running:
            return
        if trace_enabled(TraceChannel.FLUSH):
            emit_trace(
                TraceChannel.FLUSH,
                "start",
                queued=tuple(boundary._debug_boundary_id() for boundary in scheduler.queue),
            )
        scheduler_root._flush_posted = False
        scheduler_root._flush_running = True
        try:
            while True:
                boundary = scheduler.pop_next()
                if boundary is None:
                    break
                boundary._run_boundary()
        finally:
            scheduler_root._flush_running = False
        if scheduler_root._scheduler.has_pending_work():
            scheduler_root._post_flush_if_needed(was_pending=False)
        if trace_enabled(TraceChannel.FLUSH):
            emit_trace(
                TraceChannel.FLUSH,
                "end",
                queued=tuple(boundary._debug_boundary_id() for boundary in scheduler_root._scheduler.queue),
            )

    def begin_pass(self) -> None:
        self._begin_scope_pass()

    def end_pass(self) -> None:
        self._commit_scope_pass()
        self._rebuild_mount_advertisement_surface()
        self._flush_post_commit()

    def rollback_pass(self) -> None:
        self._rollback_scope_pass()
        self._rebuild_mount_advertisement_surface()
        self._post_commit_callbacks.clear()

    def debug_children_of(self, slot_id: SlotId | None = None) -> tuple[SlotId, ...]:
        if slot_id is None:
            owner: ContextBase = self
        else:
            slot = self._slots_by_id.get(slot_id)
            if slot is None or not isinstance(slot, ContextBase):
                return ()
            owner = slot
        return tuple(owner._children.keys())

    def debug_is_active(self, slot_id: SlotId) -> bool:
        return slot_id in self._slots_by_id

    def debug_pending_boundaries(self) -> tuple[SlotId | None, ...]:
        scheduler_root = self._scheduler_root
        return tuple(boundary._debug_boundary_id() for boundary in scheduler_root._scheduler.queue)

    def debug_mount_advertisements(self) -> tuple[PyrolyzeMountAdvertisement, ...]:
        return tuple(self._mount_advertisements_by_slot.values())

    def debug_ui(self, slot_id: SlotId | None = None) -> tuple[UIElement | MountDirective, ...]:
        if slot_id is None:
            owner: ContextBase = self
        else:
            slot = self._slots_by_id.get(slot_id)
            if slot is None or not isinstance(slot, ContextBase):
                return ()
            owner = slot
        return owner._committed_ui

    def committed_ui(self) -> tuple[UIElement | MountDirective, ...]:
        return self._committed_ui

    def _refresh_committed_ui_from_children(self) -> None:
        self._committed_ui = self._build_committed_ui()
        owner_slot = self._owner_slot
        if owner_slot is None:
            return
        owner_slot._committed_ui = self._committed_ui
        owner_slot.parent._refresh_committed_ui_from_children()

    def walk_context_graph(self, listener: object) -> None:
        from pyrolyze.visitor import walk_context_graph

        walk_context_graph(self, listener)

    def close_app_contexts(self) -> None:
        self._scheduler_root._app_context_store.close_all()

    def _run_boundary(self) -> None:
        callback = self._mounted_callback
        if callback is None:
            raise RuntimeError("render context is not mounted")

        scheduler_root = self._scheduler_root
        scheduler = scheduler_root._scheduler
        is_outermost_boundary = not scheduler.active
        if is_outermost_boundary:
            scheduler_root._app_context_store.get(GENERATION_TRACKER_KEY).begin()
        scheduler.enter_active(self)
        if trace_enabled(TraceChannel.BOUNDARY):
            emit_trace(
                TraceChannel.BOUNDARY,
                "start",
                boundary=self._debug_boundary_id(),
                queued=tuple(boundary._debug_boundary_id() for boundary in scheduler.queue),
            )
        try:
            callback()
            if is_outermost_boundary:
                scheduler_root._app_context_store.get(GENERATION_TRACKER_KEY).commit()
        except BaseException:
            if trace_enabled(TraceChannel.BOUNDARY):
                emit_trace(
                    TraceChannel.BOUNDARY,
                    "error",
                    boundary=self._debug_boundary_id(),
                )
            if is_outermost_boundary:
                scheduler_root._app_context_store.get(GENERATION_TRACKER_KEY).rollback()
            raise
        finally:
            scheduler.exit_active(self)
            if trace_enabled(TraceChannel.BOUNDARY):
                emit_trace(
                    TraceChannel.BOUNDARY,
                    "end",
                    boundary=self._debug_boundary_id(),
                )

    def _queue_invalidation_from(self, slot: SlotContext, *, include_source: bool = True) -> None:
        boundary = slot.render_context
        scheduler_root = boundary._scheduler_root
        was_pending = scheduler_root._scheduler.has_pending_work()
        if include_source:
            slot.invoke_dirty = True

        current: ContextBase | None = slot.parent
        dirty_contexts = 0
        while isinstance(current, ContextBase):
            dirty_contexts += 1
            for child in current._children.values():
                child.invoke_dirty = True
            if isinstance(current, RenderContext):
                break
            current = current.parent

        owner_slot = boundary._owner_slot
        if owner_slot is not None:
            owner_slot.invoke_dirty = True

        boundary._scheduler.request(boundary)
        scheduler_root._post_flush_if_needed(was_pending=was_pending)
        if trace_enabled(TraceChannel.INVALIDATION):
            emit_trace(
                TraceChannel.INVALIDATION,
                "queued",
                source_slot=slot.slot_id,
                boundary=boundary._debug_boundary_id(),
                owner_slot=owner_slot.slot_id if owner_slot is not None else None,
                include_source=include_source,
                dirty_contexts=dirty_contexts,
                queued=tuple(item._debug_boundary_id() for item in boundary._scheduler.queue),
            )

    def _debug_boundary_id(self) -> SlotId | None:
        owner_slot = self._owner_slot
        if owner_slot is None:
            return None
        return owner_slot.slot_id

    def _is_ancestor_boundary_of(self, other: RenderContext) -> bool:
        current: RenderContext | None = other
        while current is not None:
            if current is self:
                return True
            owner_slot = current._owner_slot
            current = owner_slot.render_context if owner_slot is not None else None
        return False

    def _remove_from_scheduler(self) -> None:
        self._scheduler.remove(self)

    def _enqueue_post_commit(self, callback: Callable[[], None]) -> None:
        self._post_commit_callbacks.append(callback)

    def _flush_post_commit(self) -> None:
        callbacks = self._post_commit_callbacks
        self._post_commit_callbacks = []
        for callback in callbacks:
            callback()

    def _post_flush_if_needed(self, *, was_pending: bool) -> None:
        scheduler_root = self._scheduler_root
        if scheduler_root._flush_poster is None:
            return
        if was_pending or not scheduler_root._scheduler.has_pending_work():
            return
        if scheduler_root._flush_posted or scheduler_root._flush_running:
            return
        scheduler_root._flush_posted = True
        scheduler_root._flush_poster(scheduler_root.run_pending_invalidations)

    def _publish_mount_advertisement(
        self,
        slot: PlainCallSlotContext,
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

    def _validate_mount_advertisement_surface(
        self,
        advertisements_by_slot: dict[SlotId, PyrolyzeMountAdvertisement],
        *,
        surface_owner_id: SlotId | None,
    ) -> None:
        surface_entries = [
            advertisement
            for advertisement in advertisements_by_slot.values()
            if advertisement.surface_owner_id == surface_owner_id
        ]
        seen_keys: list[object] = []
        seen_default = False
        for advertisement in surface_entries:
            if any(advertisement.key == existing_key for existing_key in seen_keys):
                raise DuplicateMountAdvertisementError(
                    f"duplicate mount advertisement key {advertisement.key!r}"
                )
            seen_keys.append(advertisement.key)
            if advertisement.default:
                if seen_default:
                    raise DuplicateMountAdvertisementError(
                        "duplicate default mount advertisement"
                    )
                seen_default = True

    def _rebuild_mount_advertisement_surface(self) -> None:
        next_entries: dict[SlotId, PyrolyzeMountAdvertisement] = {}
        for slot_id, slot in self._slots_by_id.items():
            if not isinstance(slot, PlainCallSlotContext):
                continue
            binding = slot.binding
            if not isinstance(binding, PyrolyzeMountAdvertisementBinding):
                continue
            advertisement = binding.retained_advertisement()
            if advertisement is None:
                continue
            next_entries[slot_id] = advertisement

        for surface_owner_id in {
            advertisement.surface_owner_id for advertisement in next_entries.values()
        }:
            self._validate_mount_advertisement_surface(
                next_entries,
                surface_owner_id=surface_owner_id,
            )

        self._mount_advertisements_by_slot = next_entries


def _context_kind(context: object) -> str:
    if isinstance(context, RenderContext):
        return "render_root" if context._owner_slot is None else "component_render"
    if isinstance(context, AppContextOverrideSlotContext):
        return "app_context_override"
    if isinstance(context, ContainerSlotContext):
        return "container"
    if isinstance(context, PlainCallSlotContext):
        return "plain_call"
    if isinstance(context, ComponentCallSlotContext):
        return "component_call"
    if isinstance(context, KeyedLoopSlotContext):
        return "keyed_loop"
    if isinstance(context, LoopItemSlotContext):
        return "loop_item"
    if isinstance(context, EventHandlerSlotContext):
        return "event_handler"
    if isinstance(context, LeafSlotContext):
        return "leaf"
    if isinstance(context, SlotContext):
        return "slot"
    return type(context).__name__


__all__ = [
    "AppContextOverrideSlotContext",
    "AppContextOverrideStructureError",
    "CompValue",
    "ComponentCallSlotContext",
    "ContextBase",
    "ContainerSlotContext",
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
    "PlainCallResult",
    "PlainCallRuntimeContext",
    "PlainCallSlotContext",
    "PlainValueBinding",
    "PyrolyzeMountAdvertisementBinding",
    "RenderContext",
    "RerunnableSlotContext",
    "SlotContext",
    "SlotId",
    "SlotOwnershipError",
    "UseEffectBinding",
    "UseEffectAsyncBinding",
    "UseEffectAsyncRequest",
    "UseEffectRequest",
    "dirtyof",
    "module_registry",
]
