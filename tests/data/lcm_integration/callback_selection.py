"""Record reference callback selection without approving baseline bug fixes."""

from __future__ import annotations

import json
from typing import Any

from pyrolyze.runtime import context as runtime


def _slot(index: int) -> runtime.SlotId:
    return runtime.SlotId(runtime.ModuleId("tests.lcm_callback_selection"), index)


def _repeated_selection(fail: bool) -> dict[str, Any]:
    root = runtime.RenderContext()
    calls: list[str] = []

    def first() -> None:
        calls.append("A")

    def second() -> None:
        calls.append("B")

    with root.pass_scope():
        dispatch = root.event_handler(_slot(1), callback=first, dirty=False)
    dispatch()

    stable = True
    try:
        with root.pass_scope():
            stable &= root.event_handler(_slot(1), callback=second, dirty=False) is dispatch
            dispatch()
            stable &= root.event_handler(_slot(1), callback=first, dirty=False) is dispatch
            dispatch()
            if fail:
                raise ValueError("failed callback selection")
    except ValueError:
        if not fail:
            raise
    dispatch()
    return {"calls": calls, "stable_dispatch": stable}


class _EqualReceiver:
    def __init__(self, name: str, calls: list[str]) -> None:
        self.name = name
        self.calls = calls

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _EqualReceiver)

    def handle(self) -> None:
        self.calls.append(self.name)


def _bound_selection(fail: bool) -> dict[str, Any]:
    root = runtime.RenderContext()
    calls: list[str] = []
    first = _EqualReceiver("A", calls)
    second = _EqualReceiver("B", calls)
    with root.pass_scope():
        dispatch = root.event_handler(_slot(2), callback=first.handle, dirty=False)
    dispatch()

    stable = True
    try:
        with root.pass_scope():
            stable &= root.event_handler(_slot(2), callback=second.handle, dirty=False) is dispatch
            dispatch()
            stable &= root.event_handler(_slot(2), callback=second.handle, dirty=False) is dispatch
            dispatch()
            if fail:
                raise ValueError("failed callback selection")
    except ValueError:
        if not fail:
            raise
    dispatch()
    return {"calls": calls, "stable_dispatch": stable}


def observe() -> dict[str, Any]:
    return {
        "repeated_success": _repeated_selection(False),
        "repeated_failure": _repeated_selection(True),
        "bound_success": _bound_selection(False),
        "bound_failure": _bound_selection(True),
    }


if __name__ == "__main__":
    print(json.dumps(observe(), indent=2, sort_keys=True))
