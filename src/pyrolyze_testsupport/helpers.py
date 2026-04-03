from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar, cast

from pyrolyze.api import (
    CallFromNonPyrolyzeContext,
    ComponentMetadata,
    ComponentRef,
    pyrolyze_component_ref,
)


F = TypeVar("F", bound=Callable[..., None])


def pyrolize_test_wrap(fn: F) -> ComponentRef[Any]:
    """Wrap a plain test helper as a minimal ComponentRef-like callable.

    The decorated callable keeps the original public signature for compiler
    introspection, while the attached runtime implementation accepts the extra
    ``(ctx, dirty_state, ...)`` parameters and forwards only user arguments to
    the original function.
    """

    @wraps(fn)
    def runtime_impl(__pyr_ctx: object, __pyr_dirty_state: object, *args: Any, **kwargs: Any) -> None:
        _ = (__pyr_ctx, __pyr_dirty_state)
        fn(*args, **kwargs)

    return cast(
        ComponentRef[Any],
        pyrolyze_component_ref(ComponentMetadata(fn.__name__, runtime_impl))(fn),
    )


def pyrolize_test_native(fn: F) -> ComponentRef[Any]:
    """Wrap a ctx-taking test helper as a minimal intrinsic native callable.

    The original helper must accept the current runtime context as its first
    positional argument. The attached runtime implementation forwards the
    current context plus user arguments while dropping the ``dirty_state``
    parameter.
    """

    @wraps(fn)
    def runtime_impl(__pyr_ctx: object, __pyr_dirty_state: object, *args: Any, **kwargs: Any) -> None:
        _ = __pyr_dirty_state
        with __pyr_ctx.pass_scope():
            fn(__pyr_ctx, *args, **kwargs)

    return cast(
        ComponentRef[Any],
        pyrolyze_component_ref(ComponentMetadata(fn.__name__, runtime_impl))(fn),
    )


__all__ = ["pyrolize_test_wrap", "pyrolize_test_native"]
