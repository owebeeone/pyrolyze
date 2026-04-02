from __future__ import annotations

from dataclasses import dataclass
import inspect
from typing import Any, Callable, cast


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
        return


def runtime_context_param_name(
    func: Callable[..., Any],
    *,
    cache_attr_name: str,
    runtime_context_annotation: type[Any],
) -> str | None:
    cached = _read_callable_annotation_cache(func, cache_attr_name)
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
            if annotation is runtime_context_annotation or annotation_name == runtime_context_annotation.__name__:
                if found_name is not None:
                    raise TypeError("plain-call runtime context injection supports only one annotated parameter")
                found_name = parameter.name

    _write_callable_annotation_cache(func, cache_attr_name, found_name)
    return found_name


@dataclass(frozen=True, slots=True)
class PlainCallPreparedInvocation:
    raw_func: Callable[..., Any]
    raw_args: tuple[Any, ...]
    raw_kwargs: dict[str, Any]
    kwargs_items: tuple[tuple[str, Any], ...]
    schema: tuple[int, tuple[str, ...]]
    func_dirty: bool
    input_dirty: bool


@dataclass(frozen=True, slots=True)
class PlainCallStateSnapshot:
    invoke_dirty: bool
    function_identity: Any
    schema: tuple[int, tuple[str, ...]]
    last_args: tuple[Any, ...]
    last_kwargs: tuple[tuple[str, Any], ...]
    has_binding: bool


def prepare_plain_call(
    func: Any,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    *,
    unwrap: Callable[[Any], tuple[Any, bool]],
) -> PlainCallPreparedInvocation:
    raw_func, func_dirty = unwrap(func)
    normalized_args = tuple(unwrap(arg) for arg in args)
    normalized_kwargs = {key: unwrap(value) for key, value in kwargs.items()}

    raw_args = tuple(value for value, _ in normalized_args)
    raw_kwargs = {key: value for key, (value, _) in normalized_kwargs.items()}
    kwargs_items = tuple(sorted(raw_kwargs.items()))
    schema = (len(raw_args), tuple(sorted(raw_kwargs)))
    input_dirty = any(dirty for _, dirty in normalized_args) or any(dirty for _, dirty in normalized_kwargs.values())

    return PlainCallPreparedInvocation(
        raw_func=cast(Callable[..., Any], raw_func),
        raw_args=raw_args,
        raw_kwargs=raw_kwargs,
        kwargs_items=kwargs_items,
        schema=schema,
        func_dirty=func_dirty,
        input_dirty=input_dirty,
    )


def should_invoke_plain_call(
    state: PlainCallStateSnapshot,
    prepared: PlainCallPreparedInvocation,
) -> bool:
    return (
        state.invoke_dirty
        or prepared.func_dirty
        or prepared.input_dirty
        or not state.has_binding
        or state.function_identity is not prepared.raw_func
        or state.schema != prepared.schema
        or state.last_args != prepared.raw_args
        or state.last_kwargs != prepared.kwargs_items
    )


def call_with_optional_runtime_context(
    prepared: PlainCallPreparedInvocation,
    *,
    cache_attr_name: str,
    runtime_context_annotation: type[Any],
    runtime_context_factory: Callable[[], Any] | None = None,
) -> Any:
    call_kwargs = dict(prepared.raw_kwargs)
    if runtime_context_factory is not None:
        param_name = runtime_context_param_name(
            prepared.raw_func,
            cache_attr_name=cache_attr_name,
            runtime_context_annotation=runtime_context_annotation,
        )
        if param_name is not None and param_name not in call_kwargs:
            call_kwargs[param_name] = runtime_context_factory()
    return prepared.raw_func(*prepared.raw_args, **call_kwargs)
