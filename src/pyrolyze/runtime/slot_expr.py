from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import inspect
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from pyrolyze.api import PyrolyzeMountAdvertisement, PyrolyzeMountAdvertisementRequest

from .call_site_context import (
    CallSiteArgs,
    CallSiteBindingBase,
    CallSiteContext,
    CallSiteContextManager,
    CallSiteInvokeState,
)
from .slot_call_core import (
    SlotCallStateSnapshot,
    call_with_optional_runtime_context,
    commit_slot_call_invocation,
    prepare_slot_call,
    refresh_slot_call_binding,
    should_invoke_slot_call,
)
from .dirt import DM
from .slot_call_semantics import (
    ExternalStoreRef,
    SlotCallBinding,
    SlotCallBindingHost,
    UseEffectAsyncRequest,
    UseEffectRequest,
)
from .pyro_call import RuntimeSiteMetadata, resolve_runtime_pyro_call
from .slot_identity import SlotIdPath

if TYPE_CHECKING:
    from .context import SlotRuntimeContext


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
    def lit_dirty(self, value: T) -> bool: ...


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
        return expr.slot_ctx.lit_dirty(self.func)


@dataclass(frozen=True, slots=True)
class LambdaFunctionProvider(SlotCallFunctionProvider):
    func_lambda: Callable[..., Callable[..., Any]]
    dirt_lambda: Callable[..., Any]

    def get_func(self, expr: SlotExpr) -> Callable[..., Any]:
        return expr._invoke_provider_builder(self.func_lambda, "slot_call function builder", callable_only=True)

    def get_dirty(self, expr: SlotExpr) -> Any:
        return expr._invoke_provider_builder(self.dirt_lambda, "slot_call function dirt builder")


@dataclass(frozen=True, slots=True)
class _PreparedDirtyValue:
    value: Any
    dirty: bool


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
class _SlotExprSlotCallHost:
    expr: SlotExpr
    slot_id: Any
    evaluator: SlotCallEvaluator
    advertisement: PyrolyzeMountAdvertisement | None = None
    delegate: SlotCallBindingHost | None = None

    def queue_slot_call_invalidation(self) -> None:
        if self.delegate is not None:
            self.delegate.queue_slot_call_invalidation()
        return None

    def mark_slot_call_refresh_only(self) -> None:
        self.evaluator.mark_invoke_get()
        if self.delegate is not None:
            self.delegate.mark_slot_call_refresh_only()

    def enqueue_slot_call_post_commit(self, callback: Callable[[], None]) -> None:
        if self.expr.lifecycle_slot_ctx is not None:
            if self.delegate is None:
                self.expr.lifecycle_slot_ctx.append_slot_expr_post_commit_callback(callback)
            else:
                self.expr.lifecycle_slot_ctx.append_slot_expr_post_commit_callback(
                    lambda: self.delegate.enqueue_slot_call_post_commit(callback)
                )
            return
        if self.delegate is None:
            self.expr._staged_post_commit_callbacks.append(callback)
        else:
            self.expr._staged_post_commit_callbacks.append(lambda: self.delegate.enqueue_slot_call_post_commit(callback))

    def publish_slot_call_mount_advertisement(
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
            self.advertisement = self.delegate.publish_slot_call_mount_advertisement(request)
        return self.advertisement

    def withdraw_slot_call_mount_advertisement(self) -> None:
        if self.delegate is not None:
            self.delegate.withdraw_slot_call_mount_advertisement()
        self.advertisement = None


@dataclass(slots=True, eq=False)
class _SlotExprCallSiteBinding(CallSiteBindingBase):
    binding: SlotCallBinding

    def attach_host(self, host: SlotCallBindingHost) -> None:
        if hasattr(self.binding, "host"):
            setattr(self.binding, "host", host)

    def exposed_value(self) -> Any:
        return self.binding.exposed_value()

    def refresh(self) -> tuple[Any, bool] | None:
        return self.binding.refresh()

    def commit(self) -> None:
        self.binding.commit()

    def rollback(self) -> None:
        self.binding.rollback()

    def close(self) -> None:
        self.binding.deactivate()


@dataclass(slots=True)
class _SlotExprRuntimeContextSlot:
    evaluator: SlotCallEvaluator

    @property
    def slot_id(self) -> Any:
        return self.evaluator.slot_id

    @property
    def _runtime_locals(self) -> dict[str, Any]:
        return self.evaluator.expr.runtime_locals(self.slot_id)

    def _pass_is_active(self) -> bool:
        return self.evaluator.expr._pass_active and self.evaluator.current_pass_id == self.evaluator.expr._pass_id

    def _current_context(self) -> CallSiteContext | None:
        return self.evaluator.expr.call_site_context_manager.get_current(self.slot_id)

    def _set_persisted_invoke_dirty(self, value: bool) -> None:
        current_context = self._current_context()
        if current_context is None:
            return
        if value:
            current_context.mark_invoke_dirty()
        else:
            current_context.clear_invoke_dirty()

    def _mark_binding_dirty(self) -> None:
        if self._pass_is_active():
            self.evaluator.mark_invoke_dirty()
            return
        self._set_persisted_invoke_dirty(True)
        host_factory = self.evaluator.expr.host_factory
        if host_factory is not None:
            host_factory(self.slot_id).queue_slot_call_invalidation()

    @property
    def invoke_dirty(self) -> bool:
        if self._pass_is_active():
            return self.evaluator.current_invoke_dirty
        current_context = self._current_context()
        return current_context is not None and current_context.invoke_state.value is CallSiteInvokeState.DIRTY_SET

    @invoke_dirty.setter
    def invoke_dirty(self, value: bool) -> None:
        if self._pass_is_active():
            if value:
                self.evaluator.mark_invoke_dirty()
            else:
                self.evaluator.clear_invoke_dirty()
            return
        self._set_persisted_invoke_dirty(value)

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
    host_factory: Callable[[Any], SlotCallBindingHost] | None = None
    call_site_context_manager: CallSiteContextManager = field(default_factory=CallSiteContextManager)
    runtime_locals_provider: Callable[[Any], dict[str, Any]] | None = None
    committed_ui_sync: Callable[[], None] | None = None
    lifecycle_slot_ctx: Any | None = None
    _pass_id: int = 0
    _pass_active: bool = False
    _staged_post_commit_callbacks: list[Callable[[], None]] = field(default_factory=list)
    _runtime_locals_by_slot_id: dict[Any, dict[str, Any]] = field(default_factory=dict)

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

    def apply_host_factory(self, host_factory: Callable[[Any], SlotCallBindingHost]) -> SlotExpr:
        self.host_factory = host_factory
        for evaluator in self.evaluators_by_slot_id.values():
            evaluator.host.delegate = host_factory(evaluator.slot_id)
        return self

    def apply_call_site_context_manager(self, manager: CallSiteContextManager) -> SlotExpr:
        self.call_site_context_manager = manager
        return self

    def apply_runtime_locals_provider(self, provider: Callable[[Any], dict[str, Any]]) -> SlotExpr:
        self.runtime_locals_provider = provider
        return self

    def apply_committed_ui_sync(self, sync: Callable[[], None]) -> SlotExpr:
        self.committed_ui_sync = sync
        return self

    def apply_lifecycle_slot_context(self, slot_ctx: Any) -> SlotExpr:
        self.lifecycle_slot_ctx = slot_ctx
        return self

    def evaluate(self, *names: str) -> Any:
        if self.dm is None:
            raise RuntimeError("slot_expr requires apply_dirt_sink() before evaluate()")
        if self.slot_ctx is None:
            raise RuntimeError("slot_expr requires apply_slot_context() before evaluate()")
        self._pass_id += 1
        try:
            self._pass_active = True
            self.call_site_context_manager.begin_pass()
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
                self.call_site_context_manager.rollback_pass()
                if self.committed_ui_sync is not None:
                    self.committed_ui_sync()
                self._staged_post_commit_callbacks.clear()
                raise

            if self.lifecycle_slot_ctx is None:
                for evaluator in self.evaluators_by_slot_id.values():
                    evaluator.commit_pass()
                self.call_site_context_manager.commit_pass()
                if self.committed_ui_sync is not None:
                    self.committed_ui_sync()
                callbacks = tuple(self._staged_post_commit_callbacks)
                self._staged_post_commit_callbacks.clear()
                for callback in callbacks:
                    callback()
            else:
                self.lifecycle_slot_ctx.stage_slot_expr_pass(
                    visited_call_site_ids=tuple(
                        evaluator.slot_id
                        for evaluator in self.evaluators_by_slot_id.values()
                        if evaluator._visited
                    ),
                    post_commit_callbacks=tuple(self._staged_post_commit_callbacks),
                )
                self._staged_post_commit_callbacks.clear()
            result_value, staged_bindings = staged_result
            for name, dirty_value in staged_bindings:
                setattr(self.dm.bind, name, dirty_value)
            return result_value
        finally:
            self._pass_active = False

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

    def runtime_locals(self, slot_id: Any) -> dict[str, Any]:
        if self.runtime_locals_provider is not None:
            return self.runtime_locals_provider(slot_id)
        return self._runtime_locals_by_slot_id.setdefault(slot_id, {})

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
    host: _SlotExprSlotCallHost = field(init=False)
    current_pass_id: int = -1
    _visited: bool = False
    _evaluated: bool = False
    _current_value: Any = None
    _current_dirty: Any = False
    _current_context: CallSiteContext | None = None
    _staged_context: CallSiteContext | None = None
    _pass_invoke_state: CallSiteInvokeState = CallSiteInvokeState.NOT_SET
    _next_invoke_state: CallSiteInvokeState = CallSiteInvokeState.NOT_SET
    _pass_binding: _SlotExprCallSiteBinding | None = None
    _rollback_binding: _SlotExprCallSiteBinding | None = None
    _runtime_context_slot: _SlotExprRuntimeContextSlot | None = None

    def __post_init__(self) -> None:
        delegate = self.expr.host_factory(self.slot_id) if self.expr.host_factory is not None else None
        self.host = _SlotExprSlotCallHost(expr=self.expr, slot_id=self.slot_id, evaluator=self, delegate=delegate)

    @property
    def func_provider(self) -> SlotCallFunctionProvider:
        return self._func_provider

    def begin_pass(self, pass_id: int) -> None:
        self.current_pass_id = pass_id
        self._visited = False
        self._evaluated = False
        self._current_value = None
        self._current_dirty = False
        self._current_context = self.expr.call_site_context_manager.get_current(self.slot_id)
        self._staged_context = None
        self._pass_invoke_state = max(
            self._current_context.invoke_state.value if self._current_context is not None else CallSiteInvokeState.NOT_SET,
            self._next_invoke_state,
        )
        self._next_invoke_state = CallSiteInvokeState.NOT_SET
        self._pass_binding = self._binding_from_context(self._current_context)
        if self._pass_binding is not None:
            self._pass_binding.attach_host(self.host)
        self._rollback_binding = self._pass_binding

    def commit_pass(self) -> None:
        if self._visited and self._pass_binding is not None:
            self._pass_binding.commit()

    def rollback_pass(self) -> None:
        if self._rollback_binding is not None:
            self._rollback_binding.rollback()
        self._visited = False
        self._evaluated = False
        self._current_value = None
        self._current_dirty = False
        self._staged_context = None

    def eval(self) -> Any:
        if self._evaluated:
            return self._current_value
        self._run_call()
        return self._current_value

    def dirty(self) -> Any:
        if self._evaluated:
            return self._current_dirty
        binding = self._binding_from_context(self._current_context)
        if binding is None:
            return False
        return self.expr.dm.clean_shape_like(binding.exposed_value()) if self.expr.dm is not None else False

    def _run_call(self) -> None:
        self._visited = True
        self.expr.call_site_context_manager.mark_visited(self.slot_id)
        current_binding = self._binding_from_context(self._current_context)
        if self._pass_invoke_state is CallSiteInvokeState.GET_SET and current_binding is not None:
            self._preserve_dependencies_for_refresh()
            previous_value = current_binding.exposed_value()
            refreshed = refresh_slot_call_binding(current_binding.binding)
            if refreshed is None:
                current_value = current_binding.exposed_value()
                current_dirty = self.expr.dm.clean_shape_like(current_value) if self.expr.dm is not None else False
            else:
                current_value, refreshed_dirty = refreshed
                current_dirty = (
                    _structured_dirty_projection(
                        previous=previous_value,
                        current=current_value,
                        initialized=True,
                    )
                    if refreshed_dirty
                    else (self.expr.dm.clean_shape_like(current_value) if self.expr.dm is not None else False)
                )
            if self._current_context is not None:
                self._current_context.invoke_state.value = self._next_invoke_state
            self._current_value = current_value
            self._current_dirty = current_dirty
            self._evaluated = True
            return

        args_carrier = self._invoke_builder(self.args_lambda)
        dirt_carrier = self._invoke_builder(self.dirt_args_lambda)
        func = self._func_provider.get_func(self.expr)
        func_dirty = self._is_dirty(self._func_provider.get_dirty(self.expr))
        resolved_call = resolve_runtime_pyro_call(
            func,
            args_carrier.args,
            args_carrier.kwds,
            slot_path=SlotIdPath((self.slot_id,)),
        )
        if resolved_call.func is None:
            raise RuntimeError("slot_expr call resolved to no callable target")
        last_args = CallSiteArgs.capture(*resolved_call.args, **dict(resolved_call.kwargs))
        prepared = prepare_slot_call(
            _PreparedDirtyValue(resolved_call.func, dirty=func_dirty),
            tuple(
                _PreparedDirtyValue(
                    value,
                    dirty=self._is_dirty(
                        dirt_carrier.args[index] if index < len(dirt_carrier.args) else False
                    ),
                )
                for index, value in enumerate(resolved_call.args)
            ),
            {
                key: _PreparedDirtyValue(raw_value, dirty=self._is_dirty(dirt_carrier.kwds.get(key, False)))
                for key, raw_value in resolved_call.kwargs.items()
            },
            unwrap=lambda value: (value.value, value.dirty) if isinstance(value, _PreparedDirtyValue) else (value, False),
        )
        needs_invoke_without_func_dirt = should_invoke_slot_call(
            SlotCallStateSnapshot(
                invoke_dirty=self._pass_invoke_state is CallSiteInvokeState.DIRTY_SET,
                function_identity=self._current_context.function_identity if self._current_context is not None else None,
                schema=(len(self._current_context.last_args.args), tuple(sorted(key for key, _ in self._current_context.last_args.kwargs))) if self._current_context is not None else (0, ()),
                last_args=self._current_context.last_args.args if self._current_context is not None else (),
                last_kwargs=self._current_context.last_args.kwargs if self._current_context is not None else (),
                has_binding=current_binding is not None,
            ),
            prepared,
        )
        should_invoke = needs_invoke_without_func_dirt or func_dirty
        if should_invoke:
            result = call_with_optional_runtime_context(
                prepared,
                cache_attr_name="_pyrolyze_slot_runtime_ctx_param",
                # Import locally so context depends on slot_expr, not the reverse.
                runtime_context_annotation=__import__(
                    "pyrolyze.runtime.context", fromlist=["SlotRuntimeContext"]
                ).SlotRuntimeContext,
                runtime_context_factory=self._runtime_context_factory,
            )
            previous_binding = current_binding.binding if current_binding is not None else None
            previous_value = previous_binding.exposed_value() if previous_binding is not None else None
            initialized = previous_binding is not None
            commit_result = commit_slot_call_invocation(
                host=self.host,
                prepared=prepared,
                previous_binding=previous_binding,
                result=result,
            )
            next_binding = current_binding if current_binding is not None and current_binding.binding is commit_result.binding else _SlotExprCallSiteBinding(binding=commit_result.binding)
            current_value = commit_result.current_value
            current_dirty = _structured_dirty_projection(
                previous=previous_value,
                current=current_value,
                initialized=initialized,
            )
            self._pass_binding = next_binding
            self._rollback_binding = next_binding
            self._staged_context = self._next_context(
                binding=next_binding,
                function_identity=commit_result.function_identity,
                last_args=last_args,
                site_metadata=resolved_call.metadata,
                invoke_state=self._next_invoke_state,
            )
        else:
            assert current_binding is not None
            previous_value = current_binding.exposed_value()
            refreshed = refresh_slot_call_binding(current_binding.binding)
            if refreshed is None:
                current_value = current_binding.exposed_value()
                current_dirty = self.expr.dm.clean_shape_like(current_value) if self.expr.dm is not None else False
            else:
                current_value, refreshed_dirty = refreshed
                current_dirty = (
                    _structured_dirty_projection(
                        previous=previous_value,
                        current=current_value,
                        initialized=True,
                    )
                    if refreshed_dirty
                    else (self.expr.dm.clean_shape_like(current_value) if self.expr.dm is not None else False)
                )
            self._pass_binding = current_binding
            if self._current_context is not None:
                self._current_context.invoke_state.value = self._next_invoke_state
        self._current_value = current_value
        self._current_dirty = current_dirty
        self._evaluated = True
        if self._staged_context is not None:
            self.expr.call_site_context_manager.stage(self.slot_id, self._staged_context)

    def _preserve_dependencies_for_refresh(self) -> None:
        self._mark_dependencies_visited(set())

    def _mark_dependencies_visited(self, seen: set[Any]) -> None:
        if self.slot_id in seen:
            return
        seen.add(self.slot_id)
        for name in self._dependency_names():
            dependency = self.expr.evaluators[name]
            dependency._visited = True
            self.expr.call_site_context_manager.mark_visited(dependency.slot_id)
            dependency._mark_dependencies_visited(seen)

    def _dependency_names(self) -> tuple[str, ...]:
        names: list[str] = []
        names.extend(_signature_names(self.args_lambda))
        names.extend(_signature_names(self.dirt_args_lambda))
        func_provider = self._func_provider
        if isinstance(func_provider, LambdaFunctionProvider):
            names.extend(_signature_names(func_provider.func_lambda))
            names.extend(_signature_names(func_provider.dirt_lambda))
        return tuple(dict.fromkeys(names))

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
        self._next_invoke_state = CallSiteInvokeState.DIRTY_SET
        if self._staged_context is not None:
            self._staged_context.mark_invoke_dirty()
            return
        if self._current_context is not None:
            self._current_context.mark_invoke_dirty()
            return
        current_context = self.expr.call_site_context_manager.get_current(self.slot_id)
        if current_context is not None:
            current_context.mark_invoke_dirty()

    def mark_invoke_get(self) -> None:
        if self._next_invoke_state is CallSiteInvokeState.NOT_SET:
            self._next_invoke_state = CallSiteInvokeState.GET_SET
        if self._staged_context is not None:
            self._staged_context.mark_invoke_get()
            return
        if self._current_context is not None:
            self._current_context.mark_invoke_get()
            return
        current_context = self.expr.call_site_context_manager.get_current(self.slot_id)
        if current_context is not None:
            current_context.mark_invoke_get()

    def clear_invoke_dirty(self) -> None:
        if self._pass_invoke_state is CallSiteInvokeState.DIRTY_SET:
            self._pass_invoke_state = CallSiteInvokeState.NOT_SET
        if self._next_invoke_state is CallSiteInvokeState.DIRTY_SET:
            self._next_invoke_state = CallSiteInvokeState.NOT_SET

    @property
    def current_invoke_dirty(self) -> bool:
        return (
            self._pass_invoke_state is CallSiteInvokeState.DIRTY_SET
            or self._next_invoke_state is CallSiteInvokeState.DIRTY_SET
        )

    @property
    def binding(self) -> SlotCallBinding | None:
        context = (
            self._staged_context
            if self._staged_context is not None
            else self.expr.call_site_context_manager.get_current(self.slot_id)
        )
        wrapped_binding = self._binding_from_context(context)
        if wrapped_binding is None:
            return None
        return wrapped_binding.binding

    def _runtime_context_factory(self) -> SlotRuntimeContext:
        from .context import SlotRuntimeContext

        if self._runtime_context_slot is None:
            self._runtime_context_slot = _SlotExprRuntimeContextSlot(evaluator=self)
        return SlotRuntimeContext(self._runtime_context_slot)

    def _binding_from_context(self, context: CallSiteContext | None) -> _SlotExprCallSiteBinding | None:
        if context is None:
            return None
        binding = context.binding
        if binding is None:
            return None
        if not isinstance(binding, _SlotExprCallSiteBinding):
            raise TypeError("slot_expr requires _SlotExprCallSiteBinding for call-site contexts")
        return binding

    def _next_context(
        self,
        *,
        binding: _SlotExprCallSiteBinding | None,
        function_identity: Any,
        last_args: CallSiteArgs,
        site_metadata: tuple[RuntimeSiteMetadata[Any], ...] = (),
        invoke_state: CallSiteInvokeState,
    ) -> CallSiteContext:
        if self._current_context is None:
            return CallSiteContext(
                binding=binding,
                function_identity=function_identity,
                last_args=last_args,
                site_metadata=site_metadata,
                invoke_state_value=invoke_state,
            )
        if (
            self._current_context.binding is binding
            and self._current_context.function_identity is function_identity
            and self._current_context.last_args == last_args
            and self._current_context.site_metadata == site_metadata
        ):
            next_context = self._current_context
        elif self._current_context.binding is binding:
            next_context = self._current_context.replace(
                function_identity=function_identity,
                last_args=last_args,
                site_metadata=site_metadata,
            )
        else:
            next_context = self._current_context.replace(
                binding=binding,
                function_identity=function_identity,
                last_args=last_args,
                site_metadata=site_metadata,
            )
        next_context.invoke_state.value = invoke_state
        return next_context
