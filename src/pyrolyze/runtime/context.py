"""Phase 02 context graph runtime primitives."""

from __future__ import annotations

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


def _unwrap(value: CompValue[Any] | Any) -> tuple[Any, bool]:
    if isinstance(value, CompValue):
        return value.value, value.dirty
    return value, False


class ContextBase:
    def __init__(self, render_context: RenderContext) -> None:
        self._render_context = render_context
        self._children: dict[SlotId, SlotContext] = {}
        self._literal_initialized: list[bool] = []
        self._literal_index = 0
        self._scope_active = False

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
        container_fn: Callable[..., Any],
        *args: CompValue[Any] | Any,
        **kwargs: CompValue[Any] | Any,
    ) -> _ContainerCallHandle:
        self._require_active_scope()
        slot = self._ensure_slot(slot_id, ContainerSlotContext)
        raw_args = tuple(_unwrap(arg)[0] for arg in args)
        raw_kwargs = {key: _unwrap(value)[0] for key, value in kwargs.items()}
        return _ContainerCallHandle(slot=slot, container_fn=container_fn, args=raw_args, kwargs=raw_kwargs)

    def leaf_call(
        self,
        slot_id: SlotId,
        leaf_fn: Callable[..., Any],
        *args: CompValue[Any] | Any,
        **kwargs: CompValue[Any] | Any,
    ) -> Any:
        self._require_active_scope()
        slot = self._ensure_slot(slot_id, LeafSlotContext)
        raw_args = tuple(_unwrap(arg)[0] for arg in args)
        raw_kwargs = {key: _unwrap(value)[0] for key, value in kwargs.items()}
        return slot.invoke(leaf_fn, raw_args, raw_kwargs)

    def _begin_scope_pass(self) -> None:
        if self._scope_active:
            raise RuntimeError("scope already active")

        self._scope_active = True
        self._literal_index = 0
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
            child.invoke_dirty = False

        self._scope_active = False

    def _ensure_slot(self, slot_id: SlotId, slot_type: type[S]) -> S:
        existing = self.root_context._slots_by_id.get(slot_id)
        if existing is not None and existing.parent is not self:
            raise SlotOwnershipError(
                f"slot {slot_id!r} is owned by {type(existing.parent).__name__}, "
                f"not {type(self).__name__}"
            )

        if existing is not None and not isinstance(existing, slot_type):
            existing.deactivate()
            existing = None

        if existing is None:
            slot = slot_type(render_context=self.root_context, parent=self, slot_id=slot_id)
            self._children[slot_id] = slot
            self.root_context._slots_by_id[slot_id] = slot
            existing = slot
        else:
            self._children[slot_id] = existing

        existing.seen_in_pass = True
        return cast(S, existing)

    def _require_active_scope(self) -> None:
        if not self._scope_active:
            raise RuntimeError("scope is not active")


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
    result: Any = None
    initialized: bool = False
    external_dirty: bool = False
    external_ref: ExternalStoreRef[Any] | None = None
    external_unsubscribe: Callable[[], None] | None = None

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
            or not self.initialized
            or self.function_identity is not raw_func
            or self.schema != schema
            or self.last_args != raw_args
            or self.last_kwargs != kwargs_items
        )

        if should_invoke:
            next_result = cast(Callable[..., T], raw_func)(*raw_args, **raw_kwargs)
            result_dirty = self._commit_evaluated_result(next_result)
            self.function_identity = raw_func
            self.schema = schema
            self.last_args = raw_args
            self.last_kwargs = kwargs_items
        elif self.external_dirty and self.external_ref is not None:
            next_result = self.external_ref.get()
            result_dirty = (not self.initialized) or (next_result != self.result)
            self.result = next_result
            self.initialized = True
        else:
            result_dirty = False

        self.external_dirty = False
        return CompValue(value=cast(T, self.result), dirty=result_dirty)

    def _commit_evaluated_result(self, next_result: T) -> bool:
        if isinstance(next_result, ExternalStoreRef):
            self._bind_external_ref(next_result)
            current_value = next_result.get()
            result_dirty = (not self.initialized) or (current_value != self.result)
            self.result = current_value
            self.initialized = True
            return result_dirty

        result_dirty = (not self.initialized) or (next_result != self.result)
        self._clear_external_binding()
        self.result = next_result
        self.initialized = True
        return result_dirty

    def _bind_external_ref(self, ref: ExternalStoreRef[Any]) -> None:
        current_ref = self.external_ref
        if current_ref is not None and current_ref.identity == ref.identity:
            self.external_ref = ref
            return

        next_unsubscribe = ref.subscribe(self._mark_external_dirty)
        previous_unsubscribe = self.external_unsubscribe

        self.external_ref = ref
        self.external_unsubscribe = next_unsubscribe

        if previous_unsubscribe is not None:
            previous_unsubscribe()

    def _clear_external_binding(self) -> None:
        previous_unsubscribe = self.external_unsubscribe
        self.external_ref = None
        self.external_unsubscribe = None
        self.external_dirty = False
        if previous_unsubscribe is not None:
            previous_unsubscribe()

    def _mark_external_dirty(self) -> None:
        self.external_dirty = True

    def deactivate(self) -> None:
        self._clear_external_binding()
        super().deactivate()


@dataclass(slots=True)
class ContainerSlotContext(RerunnableSlotContext):
    pass


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
            self.slot._commit_scope_pass()
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
        self.context.end_pass()
        return False


class RenderContext(ContextBase):
    def __init__(self) -> None:
        self._slots_by_id: dict[SlotId, SlotContext] = {}
        super().__init__(self)

    def pass_scope(self) -> _PassScopeHandle:
        return _PassScopeHandle(context=self)

    def begin_pass(self) -> None:
        self._begin_scope_pass()

    def end_pass(self) -> None:
        self._commit_scope_pass()

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


__all__ = [
    "CompValue",
    "ContainerSlotContext",
    "ExternalStoreRef",
    "ModuleId",
    "ModuleRegistry",
    "PlainCallSlotContext",
    "RenderContext",
    "RerunnableSlotContext",
    "SlotContext",
    "SlotId",
    "SlotOwnershipError",
    "module_registry",
]
