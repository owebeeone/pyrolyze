from __future__ import annotations

from dataclasses import dataclass, field
import inspect
from typing import Any, Callable, Generic, Protocol, TypeVar

from pyrolyze.api import PyrolyzeMountAdvertisementRequest

from .context import CompValue, ExternalStoreRef, UseEffectAsyncRequest, UseEffectRequest
from .dirt import DM


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


class SlotExprLiteralContext(Protocol):
    def literal(self, value: T) -> CompValue[T]: ...


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


class _SlotCallBinding:
    def exposed_value(self) -> Any:
        raise NotImplementedError

    def refresh(self) -> tuple[Any, Any] | None:
        return None

    def rebind(self, result: Any) -> None:
        raise NotImplementedError


@dataclass(slots=True)
class _PlainValueBinding(_SlotCallBinding):
    value: Any

    def exposed_value(self) -> Any:
        return self.value

    def rebind(self, result: Any) -> None:
        self.value = result


@dataclass(slots=True)
class _ExternalStoreBinding(_SlotCallBinding):
    ref: ExternalStoreRef[Any]
    value: Any = None
    initialized: bool = False

    @classmethod
    def bind(cls, ref: ExternalStoreRef[Any]) -> _ExternalStoreBinding:
        binding = cls(ref=ref)
        binding._update_from_get()
        return binding

    def exposed_value(self) -> Any:
        return self.value

    def refresh(self) -> tuple[Any, Any] | None:
        next_dirty = self._update_from_get()
        return self.value, next_dirty

    def rebind(self, result: Any) -> None:
        ref = result
        if self.ref.identity != ref.identity:
            self.ref = ref
        self._update_from_get()

    def _update_from_get(self) -> Any:
        next_value = self.ref.get()
        dirty = _structured_dirty_projection(
            previous=self.value,
            current=next_value,
            initialized=self.initialized,
        )
        self.value = next_value
        self.initialized = True
        return dirty


@dataclass(slots=True)
class _UseEffectBinding(_SlotCallBinding):
    request: UseEffectRequest | UseEffectAsyncRequest | None = None

    def exposed_value(self) -> None:
        return None

    def rebind(self, result: Any) -> None:
        self.request = result


@dataclass(slots=True)
class _MountAdvertBinding(_SlotCallBinding):
    request: PyrolyzeMountAdvertisementRequest | None = None

    def exposed_value(self) -> Any:
        return self.request

    def rebind(self, result: Any) -> None:
        self.request = result


def _bind_result(result: Any, previous: _SlotCallBinding | None) -> _SlotCallBinding:
    if isinstance(result, ExternalStoreRef):
        if isinstance(previous, _ExternalStoreBinding):
            previous.rebind(result)
            return previous
        return _ExternalStoreBinding.bind(result)
    if isinstance(result, (UseEffectRequest, UseEffectAsyncRequest)):
        if isinstance(previous, _UseEffectBinding):
            previous.rebind(result)
            return previous
        return _UseEffectBinding(request=result)
    if isinstance(result, PyrolyzeMountAdvertisementRequest):
        if isinstance(previous, _MountAdvertBinding):
            previous.rebind(result)
            return previous
        return _MountAdvertBinding(request=result)
    if isinstance(previous, _PlainValueBinding):
        previous.rebind(result)
        return previous
    return _PlainValueBinding(value=result)


def _signature_names(func: Callable[..., Any]) -> tuple[str, ...]:
    return tuple(inspect.signature(func).parameters)


@dataclass(slots=True)
class SlotExpr:
    value_lambda: Callable[..., Any]
    dirty_lambda: Callable[..., Any]
    dm: DM | None = None
    slot_ctx: SlotExprLiteralContext | None = None
    evaluators: dict[str, SlotCallEvaluator] = field(default_factory=dict)
    _pass_id: int = 0

    @classmethod
    def single_call(
        cls,
        func: Callable[..., Any],
        args_lambda: Callable[..., Args[Any]],
        dirt_args_lambda: Callable[..., Args[Any]],
        *,
        call_id: str = "v1",
    ) -> SlotExpr:
        expr = cls(
            value_lambda=lambda v1: v1.eval(),
            dirty_lambda=lambda v1: v1.dirty(),
        )
        expr.slot_call(call_id, func, args_lambda, dirt_args_lambda)
        return expr

    def slot_call(
        self,
        call_id: str,
        func: Callable[..., Any],
        args_lambda: Callable[..., Args[Any]],
        dirt_args_lambda: Callable[..., Args[Any]],
    ) -> SlotExpr:
        self.evaluators[call_id] = SlotCallEvaluator(
            call_id=call_id,
            func=func,
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
        value = self._invoke_expr(self.value_lambda)
        dirty = self._invoke_expr(self.dirty_lambda)
        if len(names) == 0:
            raise ValueError("evaluate() requires at least one binding name")
        if len(names) == 1:
            setattr(self.dm.bind, names[0], dirty)
            return value
        unpacked_values = self._unpack_exact(names, value)
        unpacked_dirty = self._unpack_exact(names, dirty, label="dirty")
        for name, dirty_value in zip(names, unpacked_dirty, strict=True):
            setattr(self.dm.bind, name, dirty_value)
        return unpacked_values

    def _invoke_expr(self, expr_lambda: Callable[..., Any]) -> Any:
        names = _signature_names(expr_lambda)
        args = [self.evaluators[name] for name in names]
        return expr_lambda(*args)

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
    func: Callable[..., Any]
    args_lambda: Callable[..., Args[Any]]
    dirt_args_lambda: Callable[..., Args[Any]]
    expr: SlotExpr
    binding: _SlotCallBinding | None = None
    function_identity: Any = None
    last_args: tuple[Any, ...] = ()
    last_kwargs: tuple[tuple[str, Any], ...] = ()
    current_pass_id: int = -1
    _evaluated: bool = False
    _current_value: Any = None
    _current_dirty: Any = False

    def begin_pass(self, pass_id: int) -> None:
        self.current_pass_id = pass_id
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
        args_carrier = self._invoke_builder(self.args_lambda)
        dirt_carrier = self._invoke_builder(self.dirt_args_lambda)
        raw_args = args_carrier.args
        raw_kwargs = args_carrier.kwds
        kwargs_items = tuple(sorted(raw_kwargs.items()))
        input_dirty = any(self._is_dirty(value) for value in dirt_carrier.args) or any(
            self._is_dirty(value) for value in dirt_carrier.kwds.values()
        )
        should_invoke = (
            self.binding is None
            or self.function_identity is not self.func
            or self.last_args != raw_args
            or self.last_kwargs != kwargs_items
            or input_dirty
        )
        if should_invoke:
            result = args_carrier.call(self.func)
            previous_binding = self.binding
            previous_value = previous_binding.exposed_value() if previous_binding is not None else None
            initialized = previous_binding is not None
            self.binding = _bind_result(result, previous_binding)
            current_value = self.binding.exposed_value()
            current_dirty = _structured_dirty_projection(
                previous=previous_value,
                current=current_value,
                initialized=initialized,
            )
            self.function_identity = self.func
            self.last_args = raw_args
            self.last_kwargs = kwargs_items
        else:
            assert self.binding is not None
            refreshed = self.binding.refresh()
            if refreshed is None:
                current_value = self.binding.exposed_value()
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
