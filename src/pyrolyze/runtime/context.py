"""Context propagation primitives for component subtree state."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator


@dataclass(frozen=True)
class ContextKey:
    default: Any



def create_context(default: Any) -> ContextKey:
    return ContextKey(default=default)


@dataclass
class ContextRuntime:
    """Stack-based provider runtime with nearest-provider resolution."""

    _stacks: dict[ContextKey, list[Any]] = field(default_factory=dict)

    @contextmanager
    def provider(self, context: ContextKey, value: Any) -> Iterator[None]:
        stack = self._stacks.setdefault(context, [])
        stack.append(value)
        try:
            yield
        finally:
            stack.pop()
            if not stack:
                self._stacks.pop(context, None)

    def use_context(self, context: ContextKey) -> Any:
        stack = self._stacks.get(context)
        if not stack:
            return context.default
        return stack[-1]


__all__ = ["ContextKey", "ContextRuntime", "create_context"]
