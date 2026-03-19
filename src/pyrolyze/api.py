"""Public source-level API surface for the greenfield prototype."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any, Callable, Generic, Iterable, ParamSpec, Protocol, TypeVar, cast


T = TypeVar("T")
P = ParamSpec("P")

# This module is the author-facing source contract that examples and transformed
# source import from; it is intentionally separate from runtime implementation.

@dataclass(frozen=True, slots=True)
class KeyedIterable(Generic[T]):
    """Wrapper used by declarative source to signal keyed iteration semantics."""

    items: Iterable[T]
    key: Callable[[T], Any]


@dataclass(frozen=True, slots=True)
class UIElement:
    """Placeholder UI node returned by declarative widget stubs."""

    kind: str
    props: dict[str, Any]
    children: tuple["UIElement", ...] = ()


class CallFromNonPyrolyzeContext(RuntimeError):
    """Raised when a source-surface ref is called outside component execution."""


@dataclass(frozen=True, slots=True)
class ComponentMetadata(Generic[P]):
    """Metadata attached to public component-ref symbols."""

    name: str
    _func: Callable[..., None]


class ComponentRef(Protocol[P]):
    """Callable typing surface for component refs exposed to user code."""

    _pyrolyze_meta: ComponentMetadata[P]

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None: ...


@dataclass(frozen=True, slots=True)
class PyrolyzeEventParam:
    """Marker attached to event-boundary callback parameters."""


@dataclass(frozen=True, slots=True)
class PyrolyzeSlottedParam:
    """Marker attached to slotted-helper callable annotations."""



def keyed(items: Iterable[T], key: Callable[[T], Any]) -> KeyedIterable[T]:
    return KeyedIterable(items=items, key=key)



def pyrolyse(fn: Callable[..., T]) -> Callable[..., T]:
    return fn


def reactive_component(fn: Callable[..., T]) -> Callable[..., T]:
    return pyrolyse(fn)


def pyrolyze_slotted(fn: Callable[..., T]) -> Callable[..., T]:
    setattr(fn, "_pyrolyze_slotted", True)
    return fn


def pyrolyze_component_ref(
    meta: ComponentMetadata[P],
) -> Callable[[Callable[P, None]], ComponentRef[P]]:
    def decorate(fn: Callable[P, None]) -> ComponentRef[P]:
        setattr(fn, "_pyrolyze_meta", meta)
        return cast(ComponentRef[P], fn)

    return decorate


def call_native(factory: Callable[P, UIElement | None]) -> Callable[P, None]:
    def emit(*args: P.args, **kwargs: P.kwargs) -> None:
        raise CallFromNonPyrolyzeContext(
            "call_native() may only be used inside a transformed @pyrolyse function"
        )

    setattr(emit, "_pyrolyze_call_native_factory", factory)
    return cast(Callable[P, None], emit)


def Label(*, text: str) -> UIElement:
    return UIElement(kind="Label", props={"text": text})


type PyrolyteHandler[**P, T] = Annotated[Callable[P, T], PyrolyzeEventParam()]
type SlotCallable[**P, T] = Annotated[Callable[P, T], PyrolyzeSlottedParam()]


from .hooks import use_effect, use_grip, use_mount, use_state, use_unmount


__all__ = [
    "CallFromNonPyrolyzeContext",
    "call_native",
    "ComponentMetadata",
    "ComponentRef",
    "KeyedIterable",
    "Label",
    "PyrolyteHandler",
    "PyrolyzeEventParam",
    "PyrolyzeSlottedParam",
    "SlotCallable",
    "UIElement",
    "keyed",
    "pyrolyze_component_ref",
    "pyrolyze_slotted",
    "pyrolyse",
    "reactive_component",
    "use_effect",
    "use_grip",
    "use_mount",
    "use_state",
    "use_unmount",
]
