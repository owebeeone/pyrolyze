"""Author-facing state and effect helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, TypeVar, cast


T = TypeVar("T")


if TYPE_CHECKING:
    from pyrolyze.runtime import AppContextKey, ExternalStoreRef, PlainCallRuntimeContext, UseEffectRequest


def use_state(
    initial: T,
    *,
    __pyrolyze_ctx: PlainCallRuntimeContext = cast(Any, None),
) -> tuple[T, Callable[[T | Callable[[T], T]], None]]:
    if __pyrolyze_ctx is None:
        raise RuntimeError("use_state() requires a pyrolyze plain-call runtime context")

    value_key = "use_state.value"
    setter_key = "use_state.setter"
    value = cast(T, __pyrolyze_ctx.get_or_init_local(value_key, lambda: initial))

    def build_setter() -> Callable[[T | Callable[[T], T]], None]:
        def setter(next_value: T | Callable[[T], T]) -> None:
            current = cast(T, __pyrolyze_ctx.get_local(value_key, initial))
            resolved = next_value(current) if callable(next_value) else next_value
            if resolved != current:
                __pyrolyze_ctx.set_local(value_key, resolved)
                __pyrolyze_ctx.slot.invoke_dirty = True
                __pyrolyze_ctx.invalidate()

        return setter

    setter = cast(
        Callable[[T | Callable[[T], T]], None],
        __pyrolyze_ctx.get_or_init_local(setter_key, build_setter),
    )
    return value, setter


def use_effect(
    effect: Callable[[], Callable[[], None] | None],
    *,
    deps: list[Any] | tuple[Any, ...] | None = None,
    __pyrolyze_ctx: PlainCallRuntimeContext = cast(Any, None),
) -> UseEffectRequest:
    from pyrolyze.runtime import UseEffectRequest

    return UseEffectRequest(
        effect_fn=effect,
        deps=None if deps is None else tuple(deps),
    )


def use_mount(
    effect: Callable[[], Callable[[], None] | None] | Callable[[], None],
    *,
    __pyrolyze_ctx: PlainCallRuntimeContext = cast(Any, None),
) -> UseEffectRequest:
    from pyrolyze.runtime import UseEffectRequest

    return UseEffectRequest(
        effect_fn=cast(Callable[[], Callable[[], None] | None], effect),
        deps=(),
    )


def use_unmount(
    cleanup: Callable[[], None],
    *,
    __pyrolyze_ctx: PlainCallRuntimeContext = cast(Any, None),
) -> UseEffectRequest:
    from pyrolyze.runtime import UseEffectRequest

    def effect_fn() -> Callable[[], None]:
        return cleanup

    return UseEffectRequest(effect_fn=effect_fn, deps=())


def use_grip(source: ExternalStoreRef[T] | object) -> ExternalStoreRef[T]:
    from pyrolyze.runtime import ExternalStoreRef

    if isinstance(source, ExternalStoreRef):
        return source

    ref_method = getattr(source, "ref", None)
    if callable(ref_method):
        ref = ref_method()
        if isinstance(ref, ExternalStoreRef):
            return ref

    raise TypeError("use_grip() expects an ExternalStoreRef or an object with ref()")


def use_app_context(
    key: AppContextKey[T],
    *,
    __pyrolyze_ctx: PlainCallRuntimeContext = cast(Any, None),
) -> ExternalStoreRef[T]:
    from pyrolyze.runtime import AppContextKey

    if __pyrolyze_ctx is None:
        raise RuntimeError("use_app_context() requires a pyrolyze plain-call runtime context")
    if not isinstance(key, AppContextKey):
        raise TypeError("use_app_context() expects an AppContextKey")
    return __pyrolyze_ctx.authored_app_context_ref(key)


__all__ = [
    "use_effect",
    "use_app_context",
    "use_grip",
    "use_mount",
    "use_state",
    "use_unmount",
]
