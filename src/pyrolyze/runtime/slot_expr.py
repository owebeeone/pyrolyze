from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import inspect
from typing import Any, Callable, Generic, TypeVar

from pyrolyze.api import PyrolyzeMountAdvertisement, PyrolyzeMountAdvertisementRequest

from .context import CompValue, PlainCallRuntimeContext
from .plain_call_core import (
    PlainCallStateSnapshot,
    call_with_optional_runtime_context,
    prepare_plain_call,
    should_invoke_plain_call,
)
from .dirt import DM
from .plain_call_semantics import (
    ExternalStoreRef,
    PlainCallBinding,
    PlainCallBindingHost,
    UseEffectAsyncRequest,
    UseEffectRequest,
    select_plain_call_handler,
)


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Args(Generic[T]):
    args: tuple[T, ...]
    kwds: dict[str, T]

    def call(self, func: Callable[..., Any]) -> Any:
        return func(*self.args, **self.kwds)

    @classmethod
    def capture(cls, *args: T, **kwds: T) -> Args[T]:
        return cls(tuple(args), dict(kwds))


def slot_params(*args: Any, **kwds: Any) -> Args[Any]:
    return Args.capture(*args, **kwds)


def slot_params_dirt(*args: Any, **kwds: Any) -> Args[Any]:
    return Args.capture(*args, **kwds)


class SlotExprLiteralContext(ABC):
    @abstractmethod
    def literal(self, value: T) -> CompValue[T]: ...


class SlotCallFunctionProvider(ABC):
    @abstractmethod
    def get_func(self, expr: SlotExpr) -> Callable[..., Any]: ...

    @abstractmethod
    def get_dirty(self, expr: SlotExpr) -> Any: ...


@dataclass(frozen=True, slots=True)
class LiteralFunctionProvider(SlotCallFunctionProvider):
    func: Callable[..., Any]

    def get_func(self, expr: SlotExpr) -> Callable[..., Any]:
        return self.func

    def get_dirty(self, expr: SlotExpr) -> Any:
        if expr.slot_ctx is None:
            raise RuntimeError("slot_expr requires apply_slot_context() before evaluate()")
        return expr.slot_ctx.literal(self.func).dirty


@dataclass(frozen=True, slots=True)
class LambdaFunctionProvider(SlotCallFunctionProvider):
    func_lambda: Callable[..., Callable[..., Any]]
    dirt_lambda: Callable[..., Any]

    def get_func(self, expr: SlotExpr) -> Callable[..., Any]:
        return expr._invoke_provider_builder(self.func_lambda, "slot_call function builder", callable_only=True)

    def get_dirty(self, expr: SlotExpr) -> Any:
        return expr._invoke_provider_builder(self.dirt_lambda, "slot_call function dirt builder")


def _structured_dirty_projection(*, previous: Any, current: Any, initialized: bool) -> Any:
    if not initialized:
        return _all_dirty_projection(current)
    if isinstance(current, tuple) and isinstance(previous, tuple) and len(current) == len(previous):
        return tuple(
            _structured_dirty_projection(previous=prev_item, current=current_item, initialized=True)
            for prev_item, current_item in zip(previous, current, strict=False)
        )
    if isinstance(current, list) and isinstance(previous, list) and len(current) == len(previous):
        return [
            _structured_dirty_projection(previous=prev_item, current=current_item, initialized=True)
            for prev_item, current_item in zip(previous, current, strict=False)
        ]
    if isinstance(current, dict) and isinstance(previous, dict) and current.keys() == previous.keys():
        return {
            key: _structured_dirty_projection(previous=previous[key], current=current[key], initialized=True)
            for key in current
        }
    return current != previous


def _all_dirty_projection(value: Any) -> Any:
    if isinstance(value, tuple):
        return tuple(_all_dirty_projection(item) for item in value)
    if isinstance(value, list):
        return [_all_dirty_projection(item) for item in value]
    if isinstance(value, dict):
        return {key: _all_dirty_projection(item) for key, item in value.items()}
    return True


def _signature_names(func: Callable[..., Any]) -> tuple[str, ...]:
    return tuple(inspect.signature(func).parameters)


@dataclass(slots=True)
class _SlotExprPlainCallHost:
    expr: SlotExpr
    slot_id: Any
    advertisement: PyrolyzeMountAdvertisement | None = None
    delegate: PlainCallBindingHost | None = None

    def queue_plain_call_invalidation(self) -> None:
        if self.delegate is not None:
            self.delegate.queue_plain_call_invalidation()
        return None

    def enqueue_plain_call_post_commit(self, callback: Callable[[], None]) -> None:
        if self.delegate is None:
            self.expr._staged_post_commit_callbacks.append(callback)
        else:
            self.expr._staged_post_commit_callbacks.append(lambda: self.delegate.enqueue_plain_call_post_commit(callback))

    def publish_plain_call_mount_advertisement(
        self,
        request: PyrolyzeMountAdvertisementRequest,
    ) -> PyrolyzeMountAdvertisement:
        if self.delegate is None:
            self.advertisement = PyrolyzeMountAdvertisement(
                key=request.key,
                selectors=request.selectors,
                default=request.default,
            )
        else:
            self.advertisement = self.delegate.publish_plain_call_mount_advertisement(request)
        return self.advertisement

    def withdraw_plain_call_mount_advertisement(self) -> None:
        if self.delegate is not None:
            self.delegate.withdraw_plain_call_mount_advertisement()
        self.advertisement = None


@dataclass(slots=True)
class _SlotExprRuntimeContextSlot:
    evaluator: SlotCallEvaluator
    _runtime_locals: dict[str, Any] = field(default_factory=dict)

    @property
    def slot_id(self) -> Any:
        return self.evaluator.slot_id

    def _mark_binding_dirty(self) -> None:
        self.evaluator.mark_invoke_dirty()

    @property
    def invoke_dirty(self) -> bool:
        return self.evaluator.invoke_dirty

    @invoke_dirty.setter
    def invoke_dirty(self, value: bool) -> None:
        if value:
            self.evaluator.mark_invoke_dirty()
        else:
            self.evaluator.invoke_dirty = False
            self.evaluator._staged_invoke_dirty = False

    @property
    def root_context(self) -> Any:
        slot_ctx = self.evaluator.expr.slot_ctx
        if slot_ctx is None or not hasattr(slot_ctx, "root_context"):
            raise RuntimeError("slot_expr runtime context requires slot_ctx.root_context for app-context access")
        return slot_ctx.root_context

    def get_authored_app_context(self, key: Any) -> Any:
        slot_ctx = self.evaluator.expr.slot_ctx
        if slot_ctx is None or not hasattr(slot_ctx, "get_authored_app_context"):
            raise RuntimeError("slot_expr runtime context requires authored app-context support on slot context")
        return slot_ctx.get_authored_app_context(key)

    def has_authored_app_context(self, key: Any) -> bool:
        slot_ctx = self.evaluator.expr.slot_ctx
        if slot_ctx is None or not hasattr(slot_ctx, "has_authored_app_context"):
            raise RuntimeError("slot_expr runtime context requires authored app-context support on slot context")
        return bool(slot_ctx.has_authored_app_context(key))

    def authored_app_context_ref(self, key: Any) -> ExternalStoreRef[Any]:
        slot_ctx = self.evaluator.expr.slot_ctx
        if slot_ctx is None or not hasattr(slot_ctx, "authored_app_context_ref"):
            raise RuntimeError("slot_expr runtime context requires authored app-context refs on slot context")
        return slot_ctx.authored_app_context_ref(key)


@dataclass(slots=True)
class SlotExpr:
    value_lambda: Callable[..., Any]
    dirty_lambda: Callable[..., Any]
    dm: DM | None = None
    slot_ctx: SlotExprLiteralContext | None = None
    evaluators: dict[str, SlotCallEvaluator] = field(default_factory=dict)
    evaluators_by_slot_id: dict[Any, SlotCallEvaluator] = field(default_factory=dict)
    host_factory: Callable[[Any], PlainCallBindingHost] | None = None
    _pass_id: int = 0
    _staged_post_commit_callbacks: list[Callable[[], None]] = field(default_factory=list)

    @classmethod
    def single_call(
        cls,
        func_provider: SlotCallFunctionProvider,
        args_lambda: Callable[..., Args[Any]],
        dirt_args_lambda: Callable[..., Args[Any]],
        *,
        call_id: str = "v1",
        slot_id: Any | None = None,
    ) -> SlotExpr:
        expr = cls(
            value_lambda=lambda v1: v1.eval(),
            dirty_lambda=lambda v1: v1.dirty(),
        )
        expr.slot_call(call_id, func_provider, args_lambda, dirt_args_lambda, slot_id=slot_id)
        return expr

    def slot_call(
        self,
        call_id: str,
        func_provider: SlotCallFunctionProvider,
        args_lambda: Callable[..., Args[Any]],
        dirt_args_lambda: Callable[..., Args[Any]],
        *,
        slot_id: Any | None = None,
    ) -> SlotExpr:
        resolved_slot_id = slot_id if slot_id is not None else ("slot_expr", call_id)
        existing = self.evaluators_by_slot_id.get(resolved_slot_id)
        if existing is None:
            existing = SlotCallEvaluator(
                call_id=call_id,
                slot_id=resolved_slot_id,
                _func_provider=func_provider,
                args_lambda=args_lambda,
                dirt_args_lambda=dirt_args_lambda,
                expr=self,
            )
            self.evaluators_by_slot_id[resolved_slot_id] = existing
        else:
            existing.call_id = call_id
            existing._func_provider = func_provider
            existing.args_lambda = args_lambda
            existing.dirt_args_lambda = dirt_args_lambda
        stale_names = [name for name, evaluator in self.evaluators.items() if evaluator is existing and name != call_id]
        for stale_name in stale_names:
            self.evaluators.pop(stale_name, None)
        self.evaluators[call_id] = existing
        return self

    def apply_dirt_sink(self, dm: DM) -> SlotExpr:
        self.dm = dm
        return self

    def apply_slot_context(self, slot_ctx: SlotExprLiteralContext) -> SlotExpr:
        self.slot_ctx = slot_ctx
        return self

    def apply_host_factory(self, host_factory: Callable[[Any], PlainCallBindingHost]) -> SlotExpr:
        self.host_factory = host_factory
        for evaluator in self.evaluators_by_slot_id.values():
            evaluator.host.delegate = host_factory(evaluator.slot_id)
        return self

    def evaluate(self, *names: str) -> Any:
        if self.dm is None:
            raise RuntimeError("slot_expr requires apply_dirt_sink() before evaluate()")
        if self.slot_ctx is None:
            raise RuntimeError("slot_expr requires apply_slot_context() before evaluate()")
        self._pass_id += 1
        for evaluator in self.evaluators_by_slot_id.values():
            evaluator.begin_pass(self._pass_id)
        try:
            value = self._invoke_expr(self.value_lambda)
            dirty = self._invoke_expr(self.dirty_lambda)
            if len(names) == 0:
                staged_result = (value, ())
            elif len(names) == 1:
                staged_result = (value, ((names[0], dirty),))
            else:
                unpacked_values = self._unpack_exact(names, value)
                unpacked_dirty = self._unpack_exact(names, dirty, label="dirty")
                staged_result = (
                    unpacked_values,
                    tuple(zip(names, unpacked_dirty, strict=True)),
                )
        except BaseException:
            for evaluator in self.evaluators_by_slot_id.values():
                evaluator.rollback_pass()
            self._staged_post_commit_callbacks.clear()
            raise

        for evaluator in self.evaluators_by_slot_id.values():
            evaluator.commit_pass()
        callbacks = tuple(self._staged_post_commit_callbacks)
        self._staged_post_commit_callbacks.clear()
        for callback in callbacks:
            callback()
        result_value, staged_bindings = staged_result
        for name, dirty_value in staged_bindings:
            setattr(self.dm.bind, name, dirty_value)
        return result_value

    def _invoke_expr(self, expr_lambda: Callable[..., Any]) -> Any:
        names = _signature_names(expr_lambda)
        args = [self.evaluators[name] for name in names]
        return expr_lambda(*args)

    def _invoke_provider_builder(
        self,
        builder: Callable[..., Any],
        error_message: str,
        *,
        callable_only: bool = False,
    ) -> Any:
        names = _signature_names(builder)
        args = [self.evaluators[name] for name in names]
        result = builder(*args)
        if callable_only and not callable(result):
            raise TypeError(f"{error_message} must return a callable")
        return result

    @staticmethod
    def _unpack_exact(names: tuple[str, ...], value: Any, *, label: str = "value") -> tuple[Any, ...]:
        if not isinstance(value, tuple):
            raise ValueError(f"{label} shape does not match target arity")
        if len(value) != len(names):
            raise ValueError(f"{label} shape does not match target arity")
        return value


@dataclass(slots=True)
class SlotCallEvaluator:
    call_id: str
    slot_id: Any
    _func_provider: SlotCallFunctionProvider
    args_lambda: Callable[..., Args[Any]]
    dirt_args_lambda: Callable[..., Args[Any]]
    expr: SlotExpr
    host: _SlotExprPlainCallHost = field(init=False)
    binding: PlainCallBinding | None = None
    function_identity: Any = None
    last_args: tuple[Any, ...] = ()
    last_kwargs: tuple[tuple[str, Any], ...] = ()
    _staged_binding: PlainCallBinding | None = None
    _staged_function_identity: Any = None
    _staged_last_args: tuple[Any, ...] = ()
    _staged_last_kwargs: tuple[tuple[str, Any], ...] = ()
    invoke_dirty: bool = False
    _pass_invoke_dirty: bool = False
    _staged_invoke_dirty: bool = False
    current_pass_id: int = -1
    _visited: bool = False
    _evaluated: bool = False
    _current_value: Any = None
    _current_dirty: Any = False
    _runtime_context_slot: _SlotExprRuntimeContextSlot | None = None

    def __post_init__(self) -> None:
        delegate = self.expr.host_factory(self.slot_id) if self.expr.host_factory is not None else None
        self.host = _SlotExprPlainCallHost(expr=self.expr, slot_id=self.slot_id, delegate=delegate)

    @property
    def func_provider(self) -> SlotCallFunctionProvider:
        return self._func_provider

    def begin_pass(self, pass_id: int) -> None:
        self.current_pass_id = pass_id
        self._visited = False
        self._evaluated = False
        self._current_value = None
        self._current_dirty = False
        self._pass_invoke_dirty = self.invoke_dirty
        self._staged_invoke_dirty = False
        self._staged_binding = self.binding
        self._staged_function_identity = self.function_identity
        self._staged_last_args = self.last_args
        self._staged_last_kwargs = self.last_kwargs

    def commit_pass(self) -> None:
        if self._visited:
            if self._staged_binding is not None:
                self._staged_binding.commit()
            self.binding = self._staged_binding
            self.function_identity = self._staged_function_identity
            self.last_args = self._staged_last_args
            self.last_kwargs = self._staged_last_kwargs
            self.invoke_dirty = self._staged_invoke_dirty
            return
        if self.binding is not None:
            self.binding.deactivate()
        self.binding = None
        self.function_identity = None
        self.last_args = ()
        self.last_kwargs = ()
        self.invoke_dirty = False

    def rollback_pass(self) -> None:
        if self._staged_binding is not None:
            self._staged_binding.rollback()
        self._staged_binding = self.binding
        self._staged_function_identity = self.function_identity
        self._staged_last_args = self.last_args
        self._staged_last_kwargs = self.last_kwargs
        self._visited = False
        self._evaluated = False
        self._current_value = None
        self._current_dirty = False
        self._staged_invoke_dirty = False

    def eval(self) -> Any:
        if self._evaluated:
            return self._current_value
        self._run_call()
        return self._current_value

    def dirty(self) -> Any:
        if self._evaluated:
            return self._current_dirty
        if self.binding is None:
            return False
        return self.expr.dm.clean_shape_like(self.binding.exposed_value()) if self.expr.dm is not None else False

    def _run_call(self) -> None:
        self._visited = True
        args_carrier = self._invoke_builder(self.args_lambda)
        dirt_carrier = self._invoke_builder(self.dirt_args_lambda)
        slot_ctx = self.expr.slot_ctx
        if slot_ctx is not None and hasattr(slot_ctx, "call_plain"):
            raw_func = self._func_provider.get_func(self.expr)
            func_dirty = self._is_dirty(self._func_provider.get_dirty(self.expr))
            result = slot_ctx.call_plain(
                self.slot_id,
                CompValue(raw_func, dirty=func_dirty),
                *tuple(
                    CompValue(value, dirty=self._is_dirty(dirty))
                    for value, dirty in zip(args_carrier.args, dirt_carrier.args, strict=False)
                ),
                **{
                    key: CompValue(raw_value, dirty=self._is_dirty(dirt_carrier.kwds.get(key, False)))
                    for key, raw_value in args_carrier.kwds.items()
                },
            )
            current_value = result.value
            current_dirty = result.dirty
            if isinstance(current_dirty, bool) and isinstance(current_value, (tuple, list, dict)):
                current_dirty = _all_dirty_projection(current_value) if current_dirty else (
                    self.expr.dm.clean_shape_like(current_value) if self.expr.dm is not None else False
                )
            self._current_value = current_value
            self._current_dirty = current_dirty
            self._evaluated = True
            return
        prepared = prepare_plain_call(
            CompValue(self._func_provider.get_func(self.expr), dirty=False),
            tuple(CompValue(value, dirty=self._is_dirty(dirty)) for value, dirty in zip(args_carrier.args, dirt_carrier.args, strict=False)),
            {
                key: CompValue(raw_value, dirty=self._is_dirty(dirt_carrier.kwds.get(key, False)))
                for key, raw_value in args_carrier.kwds.items()
            },
            unwrap=lambda value: (value.value, value.dirty) if isinstance(value, CompValue) else (value, False),
        )
        needs_invoke_without_func_dirt = should_invoke_plain_call(
            PlainCallStateSnapshot(
                invoke_dirty=self._pass_invoke_dirty,
                function_identity=self._staged_function_identity,
                schema=(len(self._staged_last_args), tuple(sorted(key for key, _ in self._staged_last_kwargs))),
                last_args=self._staged_last_args,
                last_kwargs=self._staged_last_kwargs,
                has_binding=self._staged_binding is not None,
            ),
            prepared,
        )
        should_invoke = needs_invoke_without_func_dirt
        if not should_invoke:
            should_invoke = self._is_dirty(self._func_provider.get_dirty(self.expr))
        if should_invoke:
            result = call_with_optional_runtime_context(
                prepared,
                cache_attr_name="_pyrolyze_plain_call_runtime_ctx_param",
                runtime_context_annotation=PlainCallRuntimeContext,
                runtime_context_factory=self._runtime_context_factory,
            )
            previous_binding = self._staged_binding
            previous_value = previous_binding.exposed_value() if previous_binding is not None else None
            initialized = previous_binding is not None
            handler = select_plain_call_handler(result)
            next_binding = handler.bind(self.host, result, previous_binding)
            if previous_binding is not None and next_binding is not previous_binding:
                previous_binding.deactivate()
            self._staged_binding = next_binding
            current_value = self._staged_binding.exposed_value()
            current_dirty = _structured_dirty_projection(
                previous=previous_value,
                current=current_value,
                initialized=initialized,
            )
            self._staged_function_identity = prepared.raw_func
            self._staged_last_args = prepared.raw_args
            self._staged_last_kwargs = prepared.kwargs_items
        else:
            assert self._staged_binding is not None
            refreshed = self._staged_binding.refresh()
            if refreshed is None:
                current_value = self._staged_binding.exposed_value()
                current_dirty = self.expr.dm.clean_shape_like(current_value) if self.expr.dm is not None else False
            else:
                current_value, current_dirty = refreshed
        self._current_value = current_value
        self._current_dirty = current_dirty
        self._evaluated = True

    def _invoke_builder(self, builder: Callable[..., Args[Any]]) -> Args[Any]:
        names = _signature_names(builder)
        args = [self.expr.evaluators[name] for name in names]
        result = builder(*args)
        if not isinstance(result, Args):
            raise TypeError("slot_call builders must return Args")
        return result

    def _is_dirty(self, value: Any) -> bool:
        if self.expr.dm is None:
            return bool(value)
        return self.expr.dm.is_dirty(value)

    def mark_invoke_dirty(self) -> None:
        self.invoke_dirty = True
        self._staged_invoke_dirty = True

    def _runtime_context_factory(self) -> PlainCallRuntimeContext:
        if self._runtime_context_slot is None:
            self._runtime_context_slot = _SlotExprRuntimeContextSlot(evaluator=self)
        return PlainCallRuntimeContext(self._runtime_context_slot)
