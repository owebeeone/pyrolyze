"""Public source-level API surface for the greenfield prototype."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, Iterable, TypeVar


T = TypeVar("T")

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



def keyed(items: Iterable[T], key: Callable[[T], Any]) -> KeyedIterable[T]:
    return KeyedIterable(items=items, key=key)



def pyrolyse(fn: Callable[..., T]) -> Callable[..., T]:
    return fn


def reactive_component(fn: Callable[..., T]) -> Callable[..., T]:
    return pyrolyse(fn)



def Label(*, text: str) -> UIElement:
    return UIElement(kind="Label", props={"text": text})


__all__ = [
    "KeyedIterable",
    "Label",
    "UIElement",
    "keyed",
    "pyrolyse",
    "reactive_component",
]
