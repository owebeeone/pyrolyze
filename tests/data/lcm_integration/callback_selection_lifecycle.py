"""Bounded callback selection on the private outer-render completion route."""

from __future__ import annotations

import json
from typing import Any

from callback_selection import observe as reference_observe
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.callback_render import _enable_callback_render
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted


def _root() -> Any:
    root = runtime.RenderContext()
    _enable_callback_render(root._state_mgr)
    return root


def _slot(index: int = 1) -> Any:
    return runtime.SlotId(runtime.ModuleId("tests.callback_lifecycle"), index)


def _generation(root: Any) -> int:
    state = root._state_mgr
    return state.get_app_context(state._generation_tracker_key).committed_generation_id


def _call(dispatch: Any) -> str | None:
    try:
        dispatch()
    except RuntimeError as error:
        assert str(error) == "event handler is inactive"
        return str(error)
    return None


def _membership() -> dict[str, Any]:
    root = _root()
    calls: list[str] = []
    callback = lambda: calls.append("A")
    with root.pass_scope():
        dispatch = root.event_handler(_slot(), callback=callback, dirty=False)
        assert _call(dispatch) == "event handler is inactive"
    state = root._slots_by_id[_slot()]._state_mgr
    facts = {
        fact["field_name"]: fact
        for fact in state.__yidl_lifecycle_definition__["fields"]
    }
    assert facts["_callback"]["field_kind"] == "managed"
    assert facts["_callback"]["tx_key_key"] == PASS_TX_KEY
    assert facts["_callback"]["compare"] == "identity"
    assert facts["_dispatch"]["field_kind"] == "local_store"
    assert state._transaction_manager is root._state_mgr._transaction_manager
    assert not hasattr(state, "_committed_callback")
    assert not hasattr(state, "commit_handler")
    assert root.debug_ui() == ()
    result: dict[str, Any] = {"initial_generation": _generation(root)}
    try:
        with root.pass_scope():
            root._slots_by_id[_slot()].deactivate()
            dispatch()
            assert root.debug_is_active(_slot())
            raise ValueError("failed removal")
    except ValueError:
        pass
    dispatch()
    assert root.debug_is_active(_slot())
    result["failed_removal"] = {"calls": list(calls), "generation": _generation(root)}
    with root.pass_scope():
        dispatch()
        assert root.debug_is_active(_slot())
    assert not root.debug_is_active(_slot())
    assert _call(dispatch) == "event handler is inactive"
    result["omitted"] = {"calls": list(calls), "generation": _generation(root)}
    fresh: Any = None
    try:
        with root.pass_scope():
            fresh = root.event_handler(
                _slot(2), callback=lambda: calls.append("new"), dirty=False
            )
            raise ValueError("failed new handler")
    except ValueError:
        pass
    assert _call(fresh) == "event handler is inactive"
    assert not root.debug_is_active(_slot(2))
    with root.pass_scope():
        omitted_new = root.event_handler(
            _slot(3), callback=lambda: calls.append("omitted"), dirty=False
        )
        root._slots_by_id[_slot(3)].deactivate()
    assert _call(omitted_new) == "event handler is inactive"
    assert not root.debug_is_active(_slot(3))
    result["new_discarded_or_removed"] = True
    with root.pass_scope():
        replacement = root.event_handler(
            _slot(), callback=lambda: calls.append("replacement"), dirty=False
        )
        state.owner.deactivate()
    replacement()
    assert calls[-1] == "replacement"
    assert root.debug_is_active(_slot())
    assert _call(dispatch) == "event handler is inactive"
    result["stale_removal_preserved_replacement"] = True
    return result


class _EqualCallable:
    def __init__(self, name: str, calls: list[str]) -> None:
        self.name = name
        self.calls = calls

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _EqualCallable)

    def __call__(self) -> None:
        self.calls.append(self.name)


def _dirty_selection() -> list[str]:
    root = _root()
    calls: list[str] = []
    first, second = _EqualCallable("A", calls), _EqualCallable("B", calls)
    with root.pass_scope():
        dispatch = root.event_handler(_slot(), callback=first, dirty=False)
    with root.pass_scope():
        assert root.event_handler(_slot(), callback=second, dirty=False) is dispatch
    dispatch()
    with root.pass_scope():
        assert root.event_handler(_slot(), callback=second, dirty=True) is dispatch
        dispatch()
    dispatch()
    assert calls == ["A", "A", "B"]
    assert root._slots_by_id[_slot()].committed_key is second
    return calls


def _nested() -> dict[str, Any]:
    root = _root()
    calls: list[str] = []
    held: list[Any] = []

    def child(context: Any, name: str, fail: bool) -> None:
        with context.pass_scope():
            dispatch = context.event_handler(
                _slot(), callback=lambda: calls.append(name), dirty=True
            )
            held.append(dispatch)
            if fail:
                raise ValueError("child failed")

    with root.pass_scope():
        component = root._ensure_slot(_slot(10), runtime.ComponentCallSlotContext)
        component.invoke(child, ("A", False), {})
    dispatch = held[-1]
    dispatch()
    try:
        with root.pass_scope():
            same = root._ensure_slot(_slot(10), runtime.ComponentCallSlotContext)
            same.invoke(child, ("B", False), {})
            assert held[-1] is dispatch
            dispatch()
            raise ValueError("parent failed")
    except ValueError:
        pass
    dispatch()
    try:
        with root.pass_scope():
            same = root._ensure_slot(_slot(10), runtime.ComponentCallSlotContext)
            try:
                same.invoke(child, ("C", True), {})
            except ValueError:
                pass
    except RenderAttemptAborted:
        pass
    else:
        raise AssertionError("caught child failure must abort the outer attempt")
    dispatch()
    with root.pass_scope():
        same = root._ensure_slot(_slot(10), runtime.ComponentCallSlotContext)
        same.invoke(child, ("D", False), {})
        dispatch()
    dispatch()
    assert calls == ["A", "A", "A", "A", "A", "D"]
    assert (
        component.child_context._state_mgr._transaction_manager
        is root._state_mgr._transaction_manager
    )
    return {"calls": calls, "generation": _generation(root), "shared_manager": True}


def _owned() -> dict[str, Any]:
    root = _root()
    calls: list[str] = []
    held: list[Any] = []

    def child(context: Any, handler: Any) -> None:
        with context.pass_scope():
            if handler is not None:
                held.append(handler)

    def invoke(include: bool) -> None:
        handler = (
            root.event_handler_binding(
                _slot(), callback=lambda: calls.append("owned"), dirty=True
            )
            if include
            else None
        )
        component = root._ensure_slot(_slot(10), runtime.ComponentCallSlotContext)
        component.invoke(child, (handler,), {})

    with root.pass_scope():
        invoke(True)
        root.event_handler(_slot(2), callback=lambda: None, dirty=False)
    dispatch = held[-1]
    dispatch()
    try:
        with root.pass_scope():
            invoke(False)
            root.event_handler(_slot(2), callback=lambda: None, dirty=False)
            dispatch()
            raise ValueError("failed owned removal")
    except ValueError:
        pass
    dispatch()
    assert root.debug_is_active(_slot())
    component = root._slots_by_id[_slot(10)]
    component.child_context._run_boundary()
    dispatch()
    root._slots_by_id[_slot(2)].deactivate()
    dispatch()
    assert root.debug_is_active(_slot())
    with root.pass_scope():
        assert (
            root._ensure_slot(_slot(10), runtime.ComponentCallSlotContext) is component
        )
    dispatch()
    state = component._state_mgr
    assert state._pass_owned_event_handler_order == ()
    assert root._slots_by_id[_slot()]._state_mgr._seen_in_pass
    with root.pass_scope():
        invoke(False)
        dispatch()
    assert _call(dispatch) == "event handler is inactive"
    assert not root.debug_is_active(_slot())
    assert calls == ["owned"] * 7
    return {"calls": calls, "generation": _generation(root), "removed": True}


def _reselect_retired() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for equal in (False, True):
        for fail in (False, True):
            root = _root()
            calls: list[str] = []
            first = _EqualCallable("A", calls)
            selected = _EqualCallable("B", calls) if equal else first
            with root.pass_scope():
                dispatch = root.event_handler(_slot(), callback=first, dirty=False)
            try:
                with root.pass_scope():
                    root._slots_by_id[_slot()].deactivate()
                    assert (
                        root.event_handler(_slot(), callback=selected, dirty=False)
                        is dispatch
                    )
                    dispatch()
                    if fail:
                        raise ValueError("failed reselection")
            except ValueError:
                pass
            dispatch()
            assert root.debug_is_active(_slot())
            assert calls == ["A", "B" if equal and not fail else "A"]
            assert root._slots_by_id[_slot()].committed_callback is (
                first if fail else selected
            )
            results.append({"equal": equal, "failed": fail, "calls": calls})
    return results


def observe() -> dict[str, Any]:
    reference = reference_observe(_root)
    assert reference["bound_success"]["calls"] == ["A", "A", "A", "B"]
    assert reference["repeated_success"]["calls"] == ["A", "A", "A", "B"]
    assert reference["bound_failure"]["calls"] == ["A", "A", "A", "A"]
    return {
        "reference": reference,
        "dirty_equal_callables": _dirty_selection(),
        "membership": _membership(),
        "nested": _nested(),
        "owned": _owned(),
        "retirement_reselection": _reselect_retired(),
    }


if __name__ == "__main__":
    print(json.dumps(observe(), indent=2, sort_keys=True))
