from __future__ import annotations

from abc import ABC
from collections.abc import Callable, Hashable, Mapping
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from pyrolyze.api import ComponentMetadata, resolve_intrinsic_component_cast_call

from .slot_identity import SlotIdPath


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class RuntimeSiteMetadata(Generic[T]):
    key: Hashable
    value: T


@dataclass(frozen=True, slots=True)
class ResolvedPyrolyzeCall:
    func: Callable[..., Any] | None
    args: tuple[Any, ...] = ()
    kwargs: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ResolvedRuntimePyroCall:
    func: Callable[..., Any] | None
    args: tuple[Any, ...] = ()
    kwargs: Mapping[str, Any] = field(default_factory=dict)
    metadata: tuple[RuntimeSiteMetadata[Any], ...] = ()


@dataclass(frozen=True, slots=True)
class PyrolyzeWrap(ABC):
    func: Callable[..., Any] | None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self.func is None:
            raise TypeError(f"{type(self).__name__} has no callable target")
        return self.func(*args, **kwargs)

    def resolve(
        self,
        *,
        args: tuple[Any, ...],
        kwargs: Mapping[str, Any]
    ) -> ResolvedPyrolyzeCall:
        return ResolvedPyrolyzeCall(
            func=self.func,
            args=args,
            kwargs=kwargs
        )
    
    def site_metadata(self, *, slot_path: SlotIdPath) -> tuple[RuntimeSiteMetadata[Any], ...]:
        return ()


@dataclass(frozen=True, slots=True)
class PyrolyzeComponentWrap(PyrolyzeWrap):
    _pyrolyze_meta: ComponentMetadata[Any] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "_pyrolyze_meta",
            ComponentMetadata(
                type(self).__name__,
                self.func,
            ),
        )


@dataclass(frozen=True, slots=True)
class PyrolyzeSlottedWrap(PyrolyzeWrap):
    _pyrolyze_slotted: bool = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_pyrolyze_slotted", True)


def resolve_runtime_pyro_call(
    func: Any,
    args: tuple[Any, ...],
    kwargs: Mapping[str, Any],
    *,
    slot_path: SlotIdPath,
) -> ResolvedRuntimePyroCall:
    current_func: Any = func
    current_args = tuple(args)
    current_kwargs = dict(kwargs)
    collected_metadata: list[RuntimeSiteMetadata[Any]] = []

    while True:
        current_func, current_args, current_kwargs = resolve_intrinsic_component_cast_call(
            current_func,
            current_args,
            current_kwargs,
        )
        if not isinstance(current_func, PyrolyzeWrap):
            return ResolvedRuntimePyroCall(
                func=current_func,
                args=current_args,
                kwargs=current_kwargs,
                metadata=tuple(collected_metadata),
            )
        collected_metadata.extend(current_func.site_metadata(slot_path=slot_path))
        resolved = current_func.resolve(args=current_args, kwargs=current_kwargs)
        current_func = resolved.func
        current_args = tuple(resolved.args)
        current_kwargs = dict(resolved.kwargs)



__all__ = [
    "PyrolyzeWrap",
    "PyrolyzeComponentWrap",
    "ResolvedPyrolyzeCall",
    "ResolvedRuntimePyroCall",
    "RuntimeSiteMetadata",
    "PyrolyzeSlottedWrap",
    "resolve_runtime_pyro_call",
]
