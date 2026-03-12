"""Runtime dispatcher for active hook context."""

from __future__ import annotations

from contextvars import ContextVar, Token
from typing import Any


_ACTIVE_RUNTIME: ContextVar[Any | None] = ContextVar("pyrolyze_active_runtime", default=None)



def set_active_runtime(runtime: Any) -> Token[Any | None]:
    return _ACTIVE_RUNTIME.set(runtime)



def reset_active_runtime(token: Token[Any | None]) -> None:
    _ACTIVE_RUNTIME.reset(token)



def get_active_runtime() -> Any:
    runtime = _ACTIVE_RUNTIME.get()
    if runtime is None:
        raise RuntimeError("PyRolyze hook called without an active component runtime.")
    return runtime


__all__ = ["get_active_runtime", "reset_active_runtime", "set_active_runtime"]
