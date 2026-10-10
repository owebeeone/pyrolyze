"""Bounded leaf invocation target; resource routes remain privately gated."""

from __future__ import annotations

import json
from typing import Any

from pyrolyze.api import UIElement
from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted


def _root() -> Any:
    root = runtime.RenderContext()
    return root


def _id() -> Any:
    return runtime.SlotId(runtime.ModuleId("tests.invocation_values"), 1)


def _arguments(leaf: Any) -> dict[str, Any]:
    state = leaf
    return {
        "accepted": [list(leaf.last_args), list(map(list, leaf.last_kwargs))],
        "candidate": [list(state._last_args), list(map(list, state._last_kwargs))],
    }


def _native_invocations() -> dict[str, Any]:
    root = _root()
    calls: list[str] = []

    def emit(context: Any, value: str, *, suffix: str, fail: bool = False) -> None:
        calls.append(value)
        context.call_native(
            UIElement, kind="text", props={"value": value + suffix}, children=()
        )
        if fail:
            raise ValueError("leaf invocation failed")

    def invoke(value: str, *, fail: bool = False) -> Any:
        leaf = root._ensure_slot(_id(), runtime.LeafSlotContext)
        leaf.invoke_native(
            emit, (value,), {"suffix": "!", "fail": fail}, context_param="context"
        )
        return leaf

    with root.pass_scope():
        leaf = invoke("A")
    state = leaf
    manager = root._transaction_manager
    facts = {
        fact["field_name"]: fact
        for fact in state.__yidl_lifecycle_definition__["fields"]
    }
    result: dict[str, Any] = {
        "declarations": {
            "candidate_managed": facts["_invocation"]["field_kind"] == "managed",
            "candidate_key": facts["_invocation"]["tx_key_key"] == PASS_TX_KEY,
            "candidate_identity": facts["_invocation"]["compare"] == "identity",
            "compatibility_removed": "_legacy_invocation" not in facts,
            "same_manager": state._transaction_manager is manager,
        },
        "initial": _arguments(leaf),
    }
    with root.pass_scope():
        token = manager.active_transaction_for(PASS_TX_KEY)
        invoke("B")
        result["pending_success"] = {
            **_arguments(leaf),
            "local_released": not state.is_scope_active(),
            "original_token": manager.active_transaction_for(PASS_TX_KEY) is token,
        }
    result["published"] = _arguments(leaf)
    try:
        with root.pass_scope():
            invoke("C")
            result["before_parent_failure"] = _arguments(leaf)
            raise ValueError("parent invocation failed")
    except ValueError as error:
        result["parent_error"] = str(error)
    result["after_parent_failure"] = _arguments(leaf)
    try:
        with root.pass_scope():
            try:
                invoke("D", fail=True)
            except ValueError as error:
                result["caught_child"] = str(error)
            result["after_child_catch"] = _arguments(leaf)
    except RenderAttemptAborted as error:
        result["outer_abort"] = str(error.__cause__)
    result["after_child_failure"] = _arguments(leaf)
    with root.pass_scope():
        invoke("C")
    with root.pass_scope():
        invoke("C")
    result["retry"] = _arguments(leaf)
    result["calls_without_leaf_elision"] = calls
    result["ui"] = [element.props["value"] for element in root.debug_ui()]
    result["ready"] = (
        manager.active_transaction_for(PASS_TX_KEY) is None
        and root._field_only_completion.last.reuse_ready
    )
    return result


def _plain_invocations() -> dict[str, Any]:
    root = _root()
    with root.pass_scope():
        leaf = root._ensure_slot(_id(), runtime.LeafSlotContext)
        first = leaf.invoke(lambda value, *, flag: value + flag, (1,), {"flag": 2})
    result: dict[str, Any] = {"initial_result": first, "initial": _arguments(leaf)}
    try:
        with root.pass_scope():
            root._ensure_slot(_id(), runtime.LeafSlotContext)
            result["candidate_result"] = leaf.invoke(
                lambda value, *, flag: value + flag, (3,), {"flag": 4}
            )
            result["pending"] = _arguments(leaf)
            raise ValueError("plain parent failed")
    except ValueError:
        pass
    result["discarded"] = _arguments(leaf)
    result["standalone_result"] = leaf.invoke(
        lambda value, *, flag: value + flag, (5,), {"flag": 6}
    )
    result["standalone"] = _arguments(leaf)
    payload: list[int] = [1]
    leaf.invoke(lambda value: None, (payload,), {})
    result["shallow_retention"] = leaf.last_args[0] is payload
    return result




def characterize() -> dict[str, Any]:
    return {
        "native": _native_invocations(),
        "plain": _plain_invocations(),
    }


if __name__ == "__main__":
    print(json.dumps(characterize(), indent=2, sort_keys=True))
