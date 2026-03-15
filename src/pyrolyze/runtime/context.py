"""Phase 05A context graph runtime primitives."""

from __future__ import annotations

import inspect
from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar, cast


T = TypeVar("T")
S = TypeVar("S", bound="SlotContext")


@dataclass(frozen=True, slots=True)
class CompValue(Generic[T]):
    value: T
    dirty: bool = False


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


class SlotOwnershipError(RuntimeError):
    """Raised when a slot is visited through a context that does not own it."""


class DuplicateKeyError(RuntimeError):
    """Raised when a keyed loop encounters the same key more than once in one pass."""


def _unwrap(value: CompValue[Any] | Any) -> tuple[Any, bool]:
    if isinstance(value, CompValue):
        return value.value, value.dirty
    return value, False


def _wrap_comp_value(value: CompValue[T] | T) -> CompValue[T]:
    if isinstance(value, CompValue):
        return value
    return CompValue(value=value, dirty=False)


@dataclass(frozen=True, slots=True)
class UseEffectRequest:
    effect_fn: Callable[[], Callable[[], None] | None]
    deps: tuple[Any, ...] | None = None
    phase: str = "passive"


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


class PlainValueHandler(PlainCallSemanticsHandler):
    def can_handle(self, result: object) -> bool:
        return not isinstance(result, (ExternalStoreRef, UseEffectRequest))

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


_PLAIN_CALL_HANDLERS: tuple[PlainCallSemanticsHandler, ...] = (
    ExternalStoreHandler(),
    UseEffectHandler(),
    PlainValueHandler(),
)

_PLAIN_CALL_RUNTIME_CONTEXT_ATTR = "_pyrolyze_plain_call_runtime_ctx_param"


def _plain_call_runtime_context_param_name(func: Callable[..., Any]) -> str | None:
    cached = getattr(func, _PLAIN_CALL_RUNTIME_CONTEXT_ATTR, None)
    if cached is not None or hasattr(func, _PLAIN_CALL_RUNTIME_CONTEXT_ATTR):
        return cast(str | None, cached)

    signature = inspect.signature(func)
    found_name: str | None = None
    for parameter in signature.parameters.values():
        annotation = parameter.annotation
        annotation_name = getattr(annotation, "__forward_arg__", annotation)
        if annotation is PlainCallRuntimeContext or annotation_name == "PlainCallRuntimeContext":
            if found_name is not None:
                raise TypeError("plain-call runtime context injection supports only one annotated parameter")
            found_name = parameter.name

    setattr(func, _PLAIN_CALL_RUNTIME_CONTEXT_ATTR, found_name)
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

    @property
    def root_context(self) -> RenderContext:
        return self._render_context

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
        **kwargs: CompValue[Any] | Any,
    ) -> CompValue[T]:
        self._require_active_scope()
        slot = self._ensure_slot(slot_id, PlainCallSlotContext)
        return slot.evaluate(func, args, kwargs)

    def container_call(
        self,
        slot_id: SlotId,
        container_fn: CompValue[Callable[..., Any]] | Callable[..., Any],
        *args: CompValue[Any] | Any,
        **kwargs: CompValue[Any] | Any,
    ) -> _ContainerCallHandle:
        self._require_active_scope()
        slot = self._ensure_slot(slot_id, ContainerSlotContext)
        raw_container_fn, _ = _unwrap(container_fn)
        raw_args = tuple(_unwrap(arg)[0] for arg in args)
        raw_kwargs = {key: _unwrap(value)[0] for key, value in kwargs.items()}
        return _ContainerCallHandle(
            slot=slot,
            container_fn=cast(Callable[..., Any], raw_container_fn),
            args=raw_args,
            kwargs=raw_kwargs,
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
        raw_args = tuple(_unwrap(arg)[0] for arg in args)
        raw_kwargs = {key: _unwrap(value)[0] for key, value in kwargs.items()}
        return slot.invoke(cast(Callable[..., Any], raw_leaf_fn), raw_args, raw_kwargs)

    def component_call(
        self,
        slot_id: SlotId,
        component: CompValue[Callable[..., Any]] | Callable[..., Any],
        *args: CompValue[Any] | Any,
        **kwargs: CompValue[Any] | Any,
    ) -> None:
        self._require_active_scope()
        slot = self._ensure_slot(slot_id, ComponentCallSlotContext)
        slot.invoke(component, args, kwargs)

    def _begin_scope_pass(self) -> None:
        if self._scope_active:
            raise RuntimeError("scope already active")

        self._scope_active = True
        self._literal_index = 0
        self._pass_child_order = tuple(self._children.keys())
        self._pass_child_dirty = {
            slot_id: child.invoke_dirty for slot_id, child in self._children.items()
        }
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

        for child in self._children.values():
            child.invoke_dirty = False

        self._scope_active = False
        self._pass_child_order = ()
        self._pass_child_dirty = {}

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
            child.invoke_dirty = self._pass_child_dirty.get(slot_id, child.invoke_dirty)
            child.seen_in_pass = True

        restored_children: dict[SlotId, SlotContext] = {}
        for slot_id in self._pass_child_order:
            child = self._children.get(slot_id)
            if child is not None:
                restored_children[slot_id] = child
        self._children = restored_children

        self._scope_active = False
        self._pass_child_order = ()
        self._pass_child_dirty = {}

    def _ensure_slot(self, slot_id: SlotId, slot_type: type[S]) -> S:
        resolved_slot_id = self._resolve_slot_id(slot_id)
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

    def _require_active_scope(self) -> None:
        if not self._scope_active:
            raise RuntimeError("scope is not active")

    def _resolve_slot_id(self, slot_id: SlotId) -> SlotId:
        runtime_key_path = self._runtime_key_path()
        return SlotId(
            module_id=slot_id.module_id,
            slot_index=slot_id.slot_index,
            key_path=runtime_key_path + slot_id.key_path,
            line_no=slot_id.line_no,
        )

    def _runtime_key_path(self) -> tuple[Any, ...]:
        slot_id = getattr(self, "slot_id", None)
        if isinstance(slot_id, SlotId):
            return slot_id.key_path
        return ()


@dataclass(slots=True)
class SlotContext:
    render_context: RenderContext
    parent: ContextBase
    slot_id: SlotId
    invoke_dirty: bool = True
    seen_in_pass: bool = False

    def deactivate(self) -> None:
        if isinstance(self, ContextBase):
            for child in list(self._children.values()):
                child.deactivate()
            self._children.clear()

        self.render_context._slots_by_id.pop(self.slot_id, None)
        if self.parent._children.get(self.slot_id) is self:
            self.parent._children.pop(self.slot_id, None)


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
    ) -> CompValue[T]:
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
        return CompValue(value=cast(T, binding.exposed_value()), dirty=result_dirty)

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

    def rollback_binding(self) -> None:
        binding = self.binding
        if binding is not None:
            binding.rollback()

    def deactivate(self) -> None:
        binding = self.binding
        self.binding = None
        if binding is not None:
            binding.deactivate()
        super().deactivate()


@dataclass(slots=True)
class ContainerSlotContext(RerunnableSlotContext):
    pass


@dataclass(slots=True)
class ComponentCallSlotContext(RerunnableSlotContext):
    component_identity: Any = None
    schema: tuple[int, tuple[str, ...]] = (0, ())
    child_context: RenderContext | None = None
    last_runtime_func: Callable[..., Any] | None = None
    last_args: tuple[CompValue[Any], ...] = ()
    last_kwargs: dict[str, CompValue[Any]] = field(default_factory=dict)

    def invoke(
        self,
        component: CompValue[Callable[..., Any]] | Callable[..., Any],
        args: tuple[CompValue[Any] | Any, ...],
        kwargs: dict[str, CompValue[Any] | Any],
    ) -> None:
        raw_component, _ = _unwrap(component)
        metadata = getattr(raw_component, "_pyrolyze_meta", None)
        runtime_func = getattr(metadata, "_func", None)
        if metadata is None or not callable(runtime_func):
            raise TypeError("component_call expects a ComponentRef with _pyrolyze_meta._func")

        schema = (len(args), tuple(sorted(kwargs)))
        if (
            self.child_context is None
            or self.component_identity is not raw_component
            or self.schema != schema
        ):
            self._dispose_child_context()
            self.child_context = RenderContext(
                owner_slot=self,
                scheduler_root=self.render_context._scheduler_root,
            )
            self.component_identity = raw_component
            self.schema = schema

        normalized_args = tuple(_wrap_comp_value(arg) for arg in args)
        normalized_kwargs = {key: _wrap_comp_value(value) for key, value in kwargs.items()}
        self.last_runtime_func = runtime_func
        self.last_args = normalized_args
        self.last_kwargs = normalized_kwargs
        self.child_context._mounted_callback = self._rerun_child
        self.child_context._run_boundary()

    def _rerun_child(self) -> None:
        child_context = self.child_context
        runtime_func = self.last_runtime_func
        if child_context is None or runtime_func is None:
            raise RuntimeError("component child is not mounted")
        runtime_func(child_context, *self.last_args, **self.last_kwargs)

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

    def deactivate(self) -> None:
        self._dispose_child_context()
        super().deactivate()


@dataclass(slots=True)
class KeyedLoopSlotContext(RerunnableSlotContext):
    pass


@dataclass(slots=True)
class LoopItemSlotContext(RerunnableSlotContext):
    current: Any = None
    current_dirty: bool = True
    current_initialized: bool = False

    def current_value(self) -> CompValue[Any]:
        self._require_active_scope()
        return CompValue(value=self.current, dirty=self.current_dirty)

    def update_current(self, value: Any) -> None:
        self.current_dirty = (not self.current_initialized) or (value != self.current)
        self.current = value
        self.current_initialized = True


@dataclass(slots=True)
class LeafSlotContext(SlotContext):
    last_args: tuple[Any, ...] = ()
    last_kwargs: tuple[tuple[str, Any], ...] = ()

    def invoke(self, leaf_fn: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
        self.last_args = args
        self.last_kwargs = tuple(sorted(kwargs.items()))
        return leaf_fn(*args, **kwargs)


@dataclass(slots=True)
class _ContainerCallHandle(AbstractContextManager[ContainerSlotContext]):
    slot: ContainerSlotContext
    container_fn: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    _host_context: Any = None

    def __enter__(self) -> ContainerSlotContext:
        self._host_context = self.container_fn(*self.args, **self.kwargs)
        host_enter = getattr(self._host_context, "__enter__", None)
        if callable(host_enter):
            host_enter()

        self.slot._begin_scope_pass()
        return self.slot

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        suppress = False
        try:
            if exc_type is None:
                self.slot._commit_scope_pass()
            else:
                self.slot._rollback_scope_pass()
        finally:
            host_exit = getattr(self._host_context, "__exit__", None)
            if callable(host_exit):
                suppress = bool(host_exit(exc_type, exc, tb))
        return suppress


@dataclass(slots=True)
class _PassScopeHandle(AbstractContextManager[None]):
    context: RenderContext

    def __enter__(self) -> None:
        self.context.begin_pass()
        return None

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        if exc_type is None:
            self.context.end_pass()
        else:
            self.context.rollback_pass()
        return False


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
                item._begin_scope_pass()
                try:
                    yield item
                except BaseException:
                    item._rollback_scope_pass()
                    raise
                else:
                    item._commit_scope_pass()
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
    ) -> None:
        self._slots_by_id: dict[SlotId, SlotContext] = {}
        self._owner_slot = owner_slot
        self._mounted_callback: Callable[[], None] | None = None
        self._post_commit_callbacks: list[Callable[[], None]] = []
        if scheduler_root is None:
            self._scheduler_root = self
            self._scheduler = _InvalidationScheduler()
        else:
            self._scheduler_root = scheduler_root
            self._scheduler = scheduler_root._scheduler
        super().__init__(self)

    def pass_scope(self) -> _PassScopeHandle:
        return _PassScopeHandle(context=self)

    def mount(self, callback: Callable[[], None]) -> None:
        self._mounted_callback = callback
        self._run_boundary()

    def run_pending_invalidations(self) -> None:
        scheduler_root = self._scheduler_root
        scheduler = scheduler_root._scheduler
        while True:
            boundary = scheduler.pop_next()
            if boundary is None:
                break
            boundary._run_boundary()

    def begin_pass(self) -> None:
        self._begin_scope_pass()

    def end_pass(self) -> None:
        self._commit_scope_pass()
        self._flush_post_commit()

    def rollback_pass(self) -> None:
        self._rollback_scope_pass()
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

    def _run_boundary(self) -> None:
        callback = self._mounted_callback
        if callback is None:
            raise RuntimeError("render context is not mounted")

        scheduler_root = self._scheduler_root
        scheduler = scheduler_root._scheduler
        scheduler.enter_active(self)
        try:
            callback()
            self._clear_ancestor_dirty_path()
        finally:
            scheduler.exit_active(self)

    def _queue_invalidation_from(self, slot: SlotContext, *, include_source: bool = True) -> None:
        boundary = slot.render_context
        current: ContextBase | None = slot if include_source else slot.parent
        while True:
            if isinstance(current, SlotContext):
                current.invoke_dirty = True
                current = current.parent
                continue

            if isinstance(current, RenderContext):
                owner_slot = current._owner_slot
                if owner_slot is None:
                    break
                owner_slot.invoke_dirty = True
                current = owner_slot.parent
                continue

            break

        boundary._scheduler.request(boundary)

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

    def _clear_ancestor_dirty_path(self) -> None:
        current: ContextBase | None = self._owner_slot
        while current is not None:
            if isinstance(current, SlotContext):
                current.invoke_dirty = False
                current = current.parent
                continue

            if isinstance(current, RenderContext):
                owner_slot = current._owner_slot
                if owner_slot is None:
                    return
                current = owner_slot
                continue

            return

    def _enqueue_post_commit(self, callback: Callable[[], None]) -> None:
        self._post_commit_callbacks.append(callback)

    def _flush_post_commit(self) -> None:
        callbacks = self._post_commit_callbacks
        self._post_commit_callbacks = []
        for callback in callbacks:
            callback()


__all__ = [
    "CompValue",
    "ComponentCallSlotContext",
    "ContainerSlotContext",
    "DuplicateKeyError",
    "ExternalStoreBinding",
    "ExternalStoreRef",
    "KeyedLoopSlotContext",
    "LoopItemSlotContext",
    "ModuleId",
    "ModuleRegistry",
    "PlainCallRuntimeContext",
    "PlainCallSlotContext",
    "PlainValueBinding",
    "RenderContext",
    "RerunnableSlotContext",
    "SlotContext",
    "SlotId",
    "SlotOwnershipError",
    "UseEffectBinding",
    "UseEffectRequest",
    "module_registry",
]
