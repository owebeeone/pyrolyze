"""Source-level API stubs and runtime-dispatched hooks for PyRolyze."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Generic, Iterable, TypeVar

from .runtime.dispatcher import get_active_runtime


T = TypeVar("T")
CleanupFn = Callable[[], Any]


@dataclass(frozen=True)
class KeyedIterable(Generic[T]):
    """Wrapper used by declarative source to signal keyed iteration semantics."""

    items: Iterable[T]
    key: Callable[[T], Any]


@dataclass(frozen=True)
class UIElement:
    """Placeholder UI node returned by declarative widget stubs."""

    kind: str
    props: dict[str, Any]



def keyed(items: Iterable[T], key: Callable[[T], Any]) -> KeyedIterable[T]:
    return KeyedIterable(items=items, key=key)



def pyrolyse(fn: Callable[..., T]) -> Callable[..., T]:
    return fn


def reactive_component(fn: Callable[..., T]) -> Callable[..., T]:
    return pyrolyse(fn)



def Label(*, text: str) -> UIElement:
    return UIElement(kind="Label", props={"text": text})



def use_state(initial: T) -> tuple[T, Callable[[T], None]]:
    runtime = get_active_runtime()
    return runtime.use_state(initial)



def use_effect(effect_fn: Callable[[], CleanupFn | None], deps: list[Any]) -> None:
    runtime = get_active_runtime()
    runtime.use_effect(effect_fn, deps=deps)



def use_effect_async(effect_fn: Callable[[], Awaitable[Any]], deps: list[Any]) -> None:
    runtime = get_active_runtime()
    hook = getattr(runtime, "use_effect_async", None)
    if hook is None:
        raise NotImplementedError(
            "use_effect_async is part of the v2 source contract but is not implemented in the runtime scaffold yet."
        )
    hook(effect_fn, deps=deps)



def use_mount(fn: Callable[[], Any]) -> None:
    runtime = get_active_runtime()
    runtime.use_mount(fn)



def use_unmount(fn: Callable[[], Any]) -> None:
    runtime = get_active_runtime()
    runtime.use_unmount(fn)



def use_external_store(
    subscribe: Callable[[Callable[[Any], None]], Callable[[], None]],
    get_snapshot: Callable[[], T | None],
    get_version: Callable[[], Any] | None = None,
    is_equal: Callable[[T | None, T | None], bool] | None = None,
) -> T | None:
    runtime = get_active_runtime()
    return runtime.use_external_store(
        subscribe=subscribe,
        get_snapshot=get_snapshot,
        get_version=get_version,
        is_equal=is_equal,
    )



def use_store(source: Any, ctx: Any | None = None, adapter: Any | None = None) -> Any:
    runtime = get_active_runtime()
    return runtime.use_store(source, ctx=ctx, adapter=adapter)



def use_grip(source: Any, ctx: Any | None = None) -> Any:
    """Compatibility hook that targets the generic store hook with a grip adapter hint."""

    return use_store(source, ctx=ctx, adapter="grip")


__all__ = [
    "KeyedIterable",
    "Label",
    "UIElement",
    "keyed",
    "pyrolyse",
    "reactive_component",
    "use_effect",
    "use_effect_async",
    "use_external_store",
    "use_grip",
    "use_mount",
    "use_state",
    "use_store",
    "use_unmount",
]
