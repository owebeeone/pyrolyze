"""Compiler bridge for explicit loop completion without changing legacy routes."""

from __future__ import annotations

from collections.abc import Iterable
from contextlib import AbstractContextManager, nullcontext
from typing import Any


def keyed_loop_scope(items: Iterable[Any]) -> AbstractContextManager[Iterable[Any]]:
    scope = getattr(items, "pass_scope", None)
    if scope is None:
        return nullcontext(items)
    return scope()
