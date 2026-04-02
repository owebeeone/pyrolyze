from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import inspect
from typing import Any, Callable, Generic, TypeVar

from pyrolyze.api import PyrolyzeMountAdvertisement, PyrolyzeMountAdvertisementRequest

from .context import CompValue
from .dirt import DM
from .plain_call_semantics import (
    ExternalStoreRef,
    PlainCallBinding,
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
    call_id: str
    advertisement: PyrolyzeMountAdvertisement | None = None

    def queue_plain_call_invalidation(self) -> None:
        return None

    def enqueue_plain_call_post_commit(self, callback: Callable[[], None]) -> None:
        self.expr._staged_post_commit_callbacks.append(callback)

    def publish_plain_call_mount_advertisement(
        self,
        request: PyrolyzeMountAdvertisementRequest,
    ) -> PyrolyzeMountAdvertisement:
        self.advertisement = PyrolyzeMountAdvertisement(
            key=request.key,
            selectors=request.selectors,
            default=request.default,
        )
        return self.advertisement

    def withdraw_plain_call_mount_advertisement(self) -> None:
        self.advertisement = None


@dataclass(slots=True)
class SlotExpr:
    value_lambda: Callable[..., Any]
    dirty_lambda: Callable[..., Any]
    dm: DM | None = None
    slot_ctx: SlotExprLiteralContext | None = None
    evaluators: dict[str, SlotCallEvaluator] = field(default_factory=dict)
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
    ) -> SlotExpr:
        expr = cls(
            value_lambda=lambda v1: v1.eval(),
            dirty_lambda=lambda v1: v1.dirty(),
        )
        expr.slot_call(call_id, func_provider, args_lambda, dirt_args_lambda)
        return expr

    def slot_call(
        self,
        call_id: str,
        func_provider: SlotCallFunctionProvider,
        args_lambda: Callable[..., Args[Any]],
        dirt_args_lambda: Callable[..., Args[Any]],
    ) -> SlotExpr:
        self.evaluators[call_id] = SlotCallEvaluator(
            call_id=call_id,
            _func_provider=func_provider,
            args_lambda=args_lambda,
            dirt_args_lambda=dirt_args_lambda,
            expr=self,
        )
        return self

    def apply_dirt_sink(self, dm: DM) -> SlotExpr:
        self.dm = dm
        return self

    def apply_slot_context(self, slot_ctx: SlotExprLiteralContext) -> SlotExpr:
        self.slot_ctx = slot_ctx
        return self

    def evaluate(self, *names: str) -> Any:
        if self.dm is None:
            raise RuntimeError("slot_expr requires apply_dirt_sink() before evaluate()")
        if self.slot_ctx is None:
            raise RuntimeError("slot_expr requires apply_slot_context() before evaluate()")
        self._pass_id += 1
        for evaluator in self.evaluators.values():
            evaluator.begin_pass(self._pass_id)
        try:
            value = self._invoke_expr(self.value_lambda)
            dirty = self._invoke_expr(self.dirty_lambda)
            if len(names) == 0:
                raise ValueError("evaluate() requires at least one binding name")
            if len(names) == 1:
                staged_result = (value, ((names[0], dirty),))
            else:
                unpacked_values = self._unpack_exact(names, value)
                unpacked_dirty = self._unpack_exact(names, dirty, label="dirty")
                staged_result = (
                    unpacked_values,
                    tuple(zip(names, unpacked_dirty, strict=True)),
                )
        except BaseException:
            for evaluator in self.evaluators.values():
                evaluator.rollback_pass()
            self._staged_post_commit_callbacks.clear()
            raise

        for evaluator in self.evaluators.values():
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
    current_pass_id: int = -1
    _visited: bool = False
    _evaluated: bool = False
    _current_value: Any = None
    _current_dirty: Any = False

    def __post_init__(self) -> None:
        self.host = _SlotExprPlainCallHost(expr=self.expr, call_id=self.call_id)

    @property
    def func_provider(self) -> SlotCallFunctionProvider:
        return self._func_provider

    def begin_pass(self, pass_id: int) -> None:
        self.current_pass_id = pass_id
        self._visited = False
        self._evaluated = False
        self._current_value = None
        self._current_dirty = False
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
            return
        if self.binding is not None:
            self.binding.deactivate()
        self.binding = None
        self.function_identity = None
        self.last_args = ()
        self.last_kwargs = ()

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
        raw_func = self._func_provider.get_func(self.expr)
        args_carrier = self._invoke_builder(self.args_lambda)
        dirt_carrier = self._invoke_builder(self.dirt_args_lambda)
        raw_args = args_carrier.args
        raw_kwargs = args_carrier.kwds
        kwargs_items = tuple(sorted(raw_kwargs.items()))
        input_dirty = any(self._is_dirty(value) for value in dirt_carrier.args) or any(
            self._is_dirty(value) for value in dirt_carrier.kwds.values()
        )
        func_identity_changed = self._staged_function_identity is not raw_func
        args_changed = self._staged_last_args != raw_args
        kwargs_changed = self._staged_last_kwargs != kwargs_items
        needs_invoke_without_func_dirt = (
            self._staged_binding is None
            or func_identity_changed
            or args_changed
            or kwargs_changed
            or input_dirty
        )
        func_dirty = False
        if not needs_invoke_without_func_dirt:
            func_dirty = self._is_dirty(self._func_provider.get_dirty(self.expr))
        should_invoke = (
            needs_invoke_without_func_dirt
            or func_dirty
        )
        if should_invoke:
            result = args_carrier.call(raw_func)
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
            self._staged_function_identity = raw_func
            self._staged_last_args = raw_args
            self._staged_last_kwargs = kwargs_items
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
