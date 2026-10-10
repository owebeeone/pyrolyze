"""Private plain slot-call values; external resource bindings stay gated."""

from __future__ import annotations

import json
from typing import Any

from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.context_lifecycle import SlotRuntimeContext
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted


def _id() -> Any:
    return runtime.SlotId(runtime.ModuleId("tests.slot_call_values"), 1)


def _selection(slot: Any) -> dict[str, Any]:
    state = slot
    return {
        "accepted": [
            slot.function_identity.__name__,
            list(slot.last_args),
            list(map(list, slot.last_kwargs)),
            slot.binding.exposed_value(),
        ],
        "candidate": [
            state._function_identity.__name__,
            list(state._last_args),
            list(map(list, state._last_kwargs)),
            state._binding.exposed_value(),
        ],
        "shape": [slot.schema[0], list(slot.schema[1])],
    }


def _private_values() -> dict[str, Any]:
    root = runtime.RenderContext()
    calls: list[list[Any]] = []
    injections: list[bool] = []
    slot: Any = None

    def source(value: int, *, offset: int = 1, ctx: SlotRuntimeContext) -> int:
        calls.append(["source", value, offset])
        injections.append(ctx.slot.parent is root)
        return value + offset

    def alternate(value: int, *, offset: int = 1) -> int:
        calls.append(["alternate", value, offset])
        return value + offset + 10

    def fail(value: int) -> None:
        calls.append(["fail", value])
        raise ValueError("slot-call failed")

    def evaluate(func: Any, value: int, **kwargs: Any) -> Any:
        nonlocal slot
        slot = root._ensure_slot(_id(), runtime.SlotCallSlotContext)
        return slot.evaluate(func, (value,), kwargs)

    with root.pass_scope():
        first = evaluate(source, 2, offset=1)
    state = slot
    facts = {
        row["field_name"]: row for row in state.__yidl_lifecycle_definition__["fields"]
    }
    result: dict[str, Any] = {
        "declarations": {
            "record_managed": facts["_invocation"]["field_kind"] == "managed",
            "record_identity": facts["_invocation"]["compare"] == "identity",
            "record_key": facts["_invocation"]["tx_key_key"] == PASS_TX_KEY,
            "configuration_const": facts["_slot_call_result_cls"]["field_kind"]
            == "const",
            "runtime_locals": facts["_runtime_locals"]["field_kind"] == "local_store",
            "same_manager": state._transaction_manager
            is root._transaction_manager,
        },
        "initial": _selection(slot),
        "initial_result": [first.dirty, first.value],
    }
    accepted = slot.binding
    with root.pass_scope():
        same = evaluate(source, 2, offset=1)
    result["unchanged"] = [same.dirty, same.value, slot.binding is accepted]
    with root.pass_scope():
        changed = evaluate(source, 4, offset=1)
        candidate = state._binding
        result["pending"] = _selection(slot)
        result["detached_binding"] = (
            candidate is not accepted and accepted.exposed_value() == 3
        )
        repeated = evaluate(source, 4, offset=1)
        result["candidate_elision"] = [
            repeated.dirty,
            repeated.value,
            state._binding is candidate,
        ]
        evaluate(source, 5, offset=1)
        evaluate(source, 4, offset=1)
        result["candidate_reselection"] = _selection(slot)
    result["published"] = _selection(slot)
    try:
        with root.pass_scope():
            evaluate(source, 6, offset=1)
            result["pending_failure"] = _selection(slot)
            raise ValueError("parent slot-call failed")
    except ValueError:
        pass
    result["discarded"] = _selection(slot)
    with root.pass_scope():
        evaluate(source, 6, offset=1)
    result["retry"] = _selection(slot)
    try:
        with root.pass_scope():
            try:
                evaluate(fail, 8)
            except ValueError:
                pass
    except RenderAttemptAborted as error:
        result["caught_failure"] = str(error.__cause__)
    result["after_caught_failure"] = _selection(slot)
    with root.pass_scope():
        evaluate(alternate, 6, offset=1)
    result["callable_change"] = _selection(slot)
    with root.pass_scope():
        shape = evaluate(alternate, 6)
    result["shape_change"] = _selection(slot)
    result["equal_value_dirty"] = shape.dirty
    with root.pass_scope():
        root._ensure_slot(_id(), runtime.SlotCallSlotContext)
        state._invoke_dirty = True
        forced = evaluate(alternate, 6)
    result["dirty_forced"] = [forced.dirty, forced.value]
    payload: list[int] = [1]
    with root.pass_scope():
        evaluate(lambda value: value, payload)
    result["shallow_retention"] = (
        slot.last_args[0] is payload and slot.binding.exposed_value() is payload
    )
    result["calls"] = calls
    result["runtime_injected"] = all(injections) and bool(injections)
    result["ready"] = root._field_only_completion.last.reuse_ready
    result["legacy_removed"] = not hasattr(state, "_legacy_invocation")
    return result




def characterize() -> dict[str, Any]:
    return {"private": _private_values()}


if __name__ == "__main__":
    print(json.dumps(characterize(), indent=2, sort_keys=True))
