"""Non-functional public API contract for the runtime context surface.

This module intentionally exposes only the practical public interface of
``pyrolyze.runtime.context``. It is a scaffold for redesign work, not a working
runtime implementation.
"""

from __future__ import annotations

__PYROLYZE_CONTEXT_IMPLEMENTATION__ = "bare"

from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar, cast

from pyrolyze.api import (
    MountDirective,
    PyrolyzeMountAdvertisement,
    PyrolyzeMountAdvertisementRequest,
    SlotSelector,
    UIElement,
)

from .app_context import (
    GENERATION_TRACKER_KEY,
    AppContextKey,
    AppContextLookup,
    AppContextStore,
)
from .slot_call_semantics import (
    ExternalStoreBinding,
    ExternalStoreRef,
    PyrolyzeMountAdvertisementBinding,
    SlotValueBinding,
    UseEffectAsyncBinding,
    UseEffectAsyncRequest,
    UseEffectBinding,
    UseEffectRequest,
)
from .slot_kinds import ContextKind
from .slot_identity import ModuleId, ModuleRegistry, SlotId, SlotIdPath, module_registry


T = TypeVar("T")


def _unavailable() -> None:
    raise NotImplementedError("context_bare is an interface-only scaffold")


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
        _ = selectors
        _unavailable()


class ContextBase:
    _context_kind = ContextKind.SLOT
    render_context: "RenderContext"

    def __init__(self, render_context: "RenderContext") -> None:
        self.render_context = render_context

    @property
    def root_context(self) -> "RenderContext":
        _unavailable()

    def get_app_context(self, key: AppContextKey[T]) -> T:
        _ = key
        _unavailable()

    def has_app_context(self, key: AppContextKey[Any]) -> bool:
        _ = key
        _unavailable()

    def get_authored_app_context(self, key: AppContextKey[T]) -> T:
        _ = key
        _unavailable()

    def has_authored_app_context(self, key: AppContextKey[Any]) -> bool:
        _ = key
        _unavailable()

    def authored_app_context_ref(self, key: AppContextKey[T]) -> ExternalStoreRef[T]:
        _ = key
        _unavailable()

    def current_generation_id(self) -> int:
        _unavailable()

    def current_slot_id(self) -> SlotId:
        _unavailable()

    def context_kind(self) -> ContextKind:
        return self.get_kind()

    def get_kind(self) -> ContextKind:
        return type(self)._context_kind

    def pass_scope(self) -> Any:
        _unavailable()

    def begin_pass(self) -> None:
        _unavailable()

    def end_pass(self) -> None:
        _unavailable()

    def rollback_pass(self) -> None:
        _unavailable()

    def slot_expr(
        self,
        slot_id: SlotId,
        value_lambda: Callable[..., Any],
        dirty_lambda: Callable[..., Any],
    ) -> Any:
        _ = (slot_id, value_lambda, dirty_lambda)
        _unavailable()

    def visit_slot_and_dirty(self, slot_id: SlotId) -> bool:
        _ = slot_id
        _unavailable()

    def keyed_loop(
        self,
        slot_id: SlotId,
        values: list[T],
        *,
        key_fn: Callable[[T], Any],
    ) -> Any:
        _ = (slot_id, values, key_fn)
        _unavailable()

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
        _ = (
            slot_id,
            container_fn,
            args,
            dirty_state,
            _pyr_param_names,
            _pyr_args_dirty,
            _pyr_kwargs_dirty,
            kwargs,
        )
        _unavailable()

    def open_directive(
        self,
        slot_id: SlotId,
        directive_fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        _ = (slot_id, directive_fn, args, kwargs)
        _unavailable()

    def open_app_context_override(
        self,
        slot_id: SlotId,
        keys: tuple[AppContextKey[Any], ...],
        *values: Any,
    ) -> Any:
        _ = (slot_id, keys, values)
        _unavailable()

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
        _ = (
            slot_id,
            component,
            args,
            dirty_state,
            _pyr_param_names,
            _pyr_args_dirty,
            _pyr_kwargs_dirty,
            kwargs,
        )
        _unavailable()

    def event_handler(
        self,
        slot_id: SlotId,
        *,
        dirty: bool,
        callback: Callable[..., Any],
    ) -> Any:
        _ = (slot_id, dirty, callback)
        _unavailable()

    def event_handler_binding(
        self,
        slot_id: SlotId,
        *,
        dirty: bool,
        callback: Callable[..., Any],
    ) -> Any:
        _ = (slot_id, dirty, callback)
        _unavailable()

    def call_native(self, factory: Callable[..., UIElement | None], *args: Any, **kwargs: Any) -> Any:
        _ = (factory, args, kwargs)
        _unavailable()


class SlotContext:
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

    def current_slot_id(self) -> SlotId:
        return self.slot_id

    def current_generation_id(self) -> int:
        _unavailable()

    def context_kind(self) -> ContextKind:
        return self.get_kind()

    def get_kind(self) -> ContextKind:
        return type(self)._context_kind

    def visit_self_and_dirty(self) -> bool:
        _unavailable()

    def deactivate(self) -> None:
        _unavailable()


class EventHandlerSlotContext(SlotContext):
    _context_kind = ContextKind.EVENT_HANDLER
    def stage_callback(
        self,
        *,
        callback: Callable[..., Any],
        dirty: bool,
    ) -> Callable[..., None]:
        _ = (callback, dirty)
        _unavailable()

    def commit_handler(self) -> None:
        _unavailable()

    def rollback_handler(self) -> None:
        _unavailable()

    def deactivate(self) -> None:
        _unavailable()


class RerunnableSlotContext(SlotContext, ContextBase):
    def __post_init__(self) -> None:
        _unavailable()


class SlotExprSlotContext(RerunnableSlotContext):
    def runtime_locals(self, slot_id: Any) -> dict[str, Any]:
        _ = slot_id
        _unavailable()

    def stage_slot_expr_pass(
        self,
        *,
        visited_call_site_ids: tuple[Any, ...],
        post_commit_callbacks: tuple[Callable[[], None], ...],
    ) -> None:
        _ = (visited_call_site_ids, post_commit_callbacks)
        _unavailable()

    def append_slot_expr_post_commit_callback(self, callback: Callable[[], None]) -> None:
        _ = callback
        _unavailable()

    def commit_binding(self) -> None:
        _unavailable()

    def rollback_binding(self) -> None:
        _unavailable()

    def sync_committed_ui(self) -> None:
        _unavailable()

    def deactivate(self) -> None:
        _unavailable()


class SlotCallSlotContext(RerunnableSlotContext):
    _context_kind = ContextKind.SLOT_CALL
    def evaluate(
        self,
        func: Callable[..., T],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        result_shape: object | None = None,
    ) -> Any:
        _ = (func, args, kwargs, result_shape)
        _unavailable()

    def queue_slot_call_invalidation(self) -> None:
        _unavailable()

    def mark_slot_call_refresh_only(self) -> None:
        _unavailable()

    def enqueue_slot_call_post_commit(self, callback: Callable[[], None]) -> None:
        _ = callback
        _unavailable()

    def publish_slot_call_mount_advertisement(
        self,
        request: PyrolyzeMountAdvertisementRequest,
    ) -> PyrolyzeMountAdvertisement:
        _ = request
        _unavailable()

    def withdraw_slot_call_mount_advertisement(self) -> None:
        _unavailable()

    def commit_binding(self) -> None:
        _unavailable()

    def rollback_binding(self) -> None:
        _unavailable()

    def deactivate(self) -> None:
        _unavailable()


class DirectiveSlotContext(SlotCallSlotContext):
    def evaluate_directive(
        self,
        directive_fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> tuple[SlotSelector, ...]:
        _ = (directive_fn, args, kwargs)
        _unavailable()

    def pending_selectors(self) -> tuple[SlotSelector, ...]:
        _unavailable()

    def has_pending_emitted_children(self) -> bool:
        _unavailable()


class AppContextOverrideSlotContext(RerunnableSlotContext):
    _context_kind = ContextKind.APP_CONTEXT_OVERRIDE
    def stage_override(
        self,
        keys: tuple[AppContextKey[Any], ...],
        values: tuple[Any, ...],
    ) -> None:
        _ = (keys, values)
        _unavailable()


class ContainerSlotContext(RerunnableSlotContext):
    _context_kind = ContextKind.CONTAINER
    pass


class ComponentCallSlotContext(RerunnableSlotContext):
    _context_kind = ContextKind.COMPONENT_CALL
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
        _ = (
            component,
            args,
            kwargs,
            dirty_state,
            _pyr_param_names,
            _pyr_args_dirty,
            _pyr_kwargs_dirty,
        )
        _unavailable()

    def commit_owned_event_handlers(self) -> None:
        _unavailable()

    def rollback_owned_event_handlers(self) -> None:
        _unavailable()

    def deactivate(self) -> None:
        _unavailable()


class KeyedLoopSlotContext(RerunnableSlotContext):
    _context_kind = ContextKind.KEYED_LOOP
    pass


class LoopItemSlotContext(RerunnableSlotContext):
    _context_kind = ContextKind.LOOP_ITEM
    def current_value(self) -> Any:
        _unavailable()

    def update_current(self, value: Any) -> None:
        _ = value
        _unavailable()


class LeafSlotContext(RerunnableSlotContext):
    _context_kind = ContextKind.LEAF
    def invoke(self, leaf_fn: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
        _ = (leaf_fn, args, kwargs)
        _unavailable()

    def invoke_native(
        self,
        leaf_fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        context_param: str,
    ) -> Any:
        _ = (leaf_fn, args, kwargs, context_param)
        _unavailable()


class RenderContext(ContextBase):
    def get_kind(self) -> ContextKind:
        if self._owner_slot is None:
            return ContextKind.RENDER_ROOT
        return ContextKind.COMPONENT_RENDER
    def __init__(
        self,
        *,
        owner_slot: ComponentCallSlotContext | None = None,
        scheduler_root: "RenderContext" | None = None,
        app_context_store: AppContextStore | None = None,
        authored_app_context_lookup: AppContextLookup | None = None,
    ) -> None:
        _ = (owner_slot, scheduler_root, app_context_store, authored_app_context_lookup)
        super().__init__(self)

    def pass_scope(self) -> Any:
        _unavailable()

    def mount(self, callback: Callable[[], None]) -> None:
        _ = callback
        _unavailable()

    def set_flush_poster(self, post: Callable[[Callable[[], None]], None]) -> None:
        _ = post
        _unavailable()

    def run_pending_invalidations(self) -> None:
        _unavailable()

    def begin_pass(self) -> None:
        _unavailable()

    def end_pass(self) -> None:
        _unavailable()

    def rollback_pass(self) -> None:
        _unavailable()

    def debug_children_of(self, slot_id: SlotId | None = None) -> tuple[SlotId, ...]:
        _ = slot_id
        _unavailable()

    def debug_is_active(self, slot_id: SlotId) -> bool:
        _ = slot_id
        _unavailable()

    def debug_pending_boundaries(self) -> tuple[SlotId | None, ...]:
        _unavailable()

    def debug_mount_advertisements(self) -> tuple[PyrolyzeMountAdvertisement, ...]:
        _unavailable()

    def debug_ui(self, slot_id: SlotId | None = None) -> tuple[UIElement | MountDirective, ...]:
        _ = slot_id
        _unavailable()

    def committed_ui(self) -> tuple[UIElement | MountDirective, ...]:
        _unavailable()

    def walk_context_graph(self, listener: object) -> None:
        _ = listener
        _unavailable()

    def close_app_contexts(self) -> None:
        _unavailable()


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
