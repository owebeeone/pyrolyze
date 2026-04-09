from __future__ import annotations

import inspect
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
    validate_mount_selectors,
)

from ..function_arg_helpers import build_function_arg_dirty_map, pack_function_args
from ..pyro_call import RuntimeSiteMetadata, resolve_runtime_pyro_call
from ..slot_call_core import runtime_context_param_name
from ..slot_identity import SlotId, SlotIdPath


T = TypeVar("T")


@dataclass(slots=True)
class _RefactorClassRegistry:
    context_base_cls: type[Any] | None = None
    render_context_cls: type[Any] | None = None
    slot_context_cls: type[Any] | None = None
    event_handler_slot_context_cls: type[Any] | None = None
    slot_expr_slot_context_cls: type[Any] | None = None
    slot_call_slot_context_cls: type[Any] | None = None
    directive_slot_context_cls: type[Any] | None = None
    app_context_override_slot_context_cls: type[Any] | None = None
    container_slot_context_cls: type[Any] | None = None
    component_call_slot_context_cls: type[Any] | None = None
    keyed_loop_slot_context_cls: type[Any] | None = None
    loop_item_slot_context_cls: type[Any] | None = None


REFRACTOR_CLASSES = _RefactorClassRegistry()


@dataclass(slots=True)
class _RefactorRuntimeRegistry:
    walk_context_graph: Callable[[Any, Any], None] | None = None


REFRACTOR_RUNTIME = _RefactorRuntimeRegistry()


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


@dataclass(slots=True)
class _SlotExprHostSlotProxy:
    slot_id: SlotId
    parent: Any
    render_context: Any
    invoke_dirty: bool = False


@dataclass(slots=True)
class _ContextSlotExprHost:
    owner: Any
    slot_id: SlotId
    _proxy: _SlotExprHostSlotProxy = field(init=False)

    def __post_init__(self) -> None:
        render_context_cls = REFRACTOR_CLASSES.render_context_cls
        is_render_context = render_context_cls is not None and isinstance(self.owner, render_context_cls)
        render_context = self.owner if is_render_context else self.owner.root_context
        parent = None if is_render_context else self.owner
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
    context_base_cls = REFRACTOR_CLASSES.context_base_cls
    if context_base_cls is not None and isinstance(parent, context_base_cls):
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
    elif isinstance(annotation, type) and getattr(annotation, "__name__", None) in _NATIVE_CONTEXT_ANNOTATIONS:
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


def _native_emission_slot_identity(context: Any) -> SlotIdPath | None:
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


def _bind_pending_event_plain_value(owner: Any, value: Any) -> Any:
    if isinstance(value, PendingEventHandlerBinding):
        return owner._materialize_pending_event_handler(value)
    return value


def _resolve_mount_advertisement_owner(parent: Any) -> Any:
    current: Any = parent
    slot_context_cls = REFRACTOR_CLASSES.slot_context_cls
    container_slot_context_cls = REFRACTOR_CLASSES.container_slot_context_cls
    while current is not None:
        if container_slot_context_cls is not None and isinstance(current, container_slot_context_cls):
            return current
        if slot_context_cls is not None and isinstance(current, slot_context_cls):
            current = current.parent
            continue
        return None
    return None


def _finish_context_pass(context: Any, *, commit: bool) -> None:
    if not commit:
        context.rollback_pass()
        return
    try:
        context.end_pass()
    except BaseException:
        if getattr(context, "_scope_active", False):
            context.rollback_pass()
        raise


class ContainerCallRuntimeContext:
    slot: Any

    def __init__(self, slot: Any) -> None:
        self.slot = slot

    def open_directive(self, *selectors: SlotSelector) -> Any:
        return _DirectiveCallHandle(
            slot=self.slot,
            directive_fn=validate_mount_selectors,
            args=selectors,
            kwargs={},
        )


@dataclass(slots=True)
class _ContainerCallHandle(AbstractContextManager[Any]):
    slot: Any
    container_fn: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    _host_context: Any = None

    def __enter__(self) -> Any:
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
class _DirectiveCallHandle(AbstractContextManager[Any]):
    slot: Any
    directive_fn: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]

    def __enter__(self) -> Any:
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
class _MountContainerCallHandle(AbstractContextManager[Any]):
    slot: Any
    container_fn: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    context_param: str
    _host_context: Any = None

    def __enter__(self) -> Any:
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
        directive_slot_context_cls = REFRACTOR_CLASSES.directive_slot_context_cls
        if directive_slot_context_cls is not None and isinstance(entered, directive_slot_context_cls):
            return entered
        return self.slot

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        host_exit = getattr(self._host_context, "__exit__", None)
        if not callable(host_exit):
            raise RuntimeError("mount() container helper host context is missing __exit__")
        return bool(host_exit(exc_type, exc, tb))


@dataclass(slots=True)
class _AppContextOverrideHandle(AbstractContextManager[Any]):
    slot: Any
    keys: tuple[Any, ...]
    values: tuple[Any, ...]

    def __enter__(self) -> Any:
        self.slot.stage_override(self.keys, self.values)
        self.slot._begin_scope_pass()
        return self.slot

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        _finish_context_pass(self.slot, commit=exc_type is None)
        return False


@dataclass(slots=True)
class _NativeContainerCallHandle(AbstractContextManager[Any]):
    slot: Any
    container_fn: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    context_param: str

    def __enter__(self) -> Any:
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
class _PyrolyzeContainerCallHandle(AbstractContextManager[Any]):
    slot: Any
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

    def __enter__(self) -> Any:
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
    owner: Any
    values: tuple[T, ...]
    key_fn: Callable[[T], Any]

    def __iter__(self) -> Iterator[T]:
        loop_item_slot_context_cls = REFRACTOR_CLASSES.loop_item_slot_context_cls
        if loop_item_slot_context_cls is None:
            raise RuntimeError("loop item slot context class is not configured")
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
                item = self.owner._ensure_slot(item_slot, loop_item_slot_context_cls)
                item.update_current(value)
                yield item
        except BaseException:
            self.owner._rollback_scope_pass()
            raise
        else:
            self.owner._commit_scope_pass()
