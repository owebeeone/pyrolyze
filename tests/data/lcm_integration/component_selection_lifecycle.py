"""Component selection and membership share the outer render decision."""

from __future__ import annotations

import json
from typing import Any

from pyrolyze.api import UIElement
from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.slot_call_semantics import ExternalStoreRef


def characterize() -> dict[str, Any]:
    _verify_argument_conversion()
    root = runtime.RenderContext()
    slot_id = runtime.SlotId(runtime.ModuleId("component-selection"), 1)
    result: dict[str, Any] = {}

    def render(context: Any, value: int) -> None:
        with context.pass_scope():
            leaf = context._ensure_slot(
                runtime.SlotId(runtime.ModuleId("component-selection"), 2),
                runtime.LeafSlotContext,
            )
            leaf.invoke_native(emit, (value,), {}, context_param="context")

    def emit(context: Any, value: int) -> None:
        context.call_native(UIElement, kind="text", props={"value": value}, children=())

    def values() -> list[int]:
        return [item.props["value"] for item in root.debug_ui()]

    with root.pass_scope():
        slot = root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
        slot.invoke(render, (1,), {})
        assert slot._call_args == (1,)
        assert slot.current._call_args == ()
        result["provisional"] = [
            slot.current._selection.child is None,
            slot_id not in root.current.children_state,
        ]
    child = slot.child_context
    result["accepted"] = [child is not None, values()]
    retained = slot.current._selection
    try:
        with root.pass_scope():
            reused = root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
            reused.invoke(render, (2,), {})
            assert slot._call_args == (2,)
            assert slot.current._call_args == (1,)
            result["during_retry"] = values()
            raise ValueError("discard")
    except ValueError:
        pass
    result["discard"] = [
        slot.child_context is child,
        slot.current._selection is retained,
        values(),
    ]
    assert slot.current._call_args == (1,)
    with root.pass_scope():
        reused = root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
        reused.invoke(render, (3,), {})
    assert slot.current._call_args == (3,)
    result["retry"] = [reused is slot, slot.child_context is child, values()]

    events: list[str] = []

    def resource_render(name: str) -> Any:
        def run(context: Any) -> None:
            with context.pass_scope():
                binding = context._ensure_slot(
                    runtime.SlotId(runtime.ModuleId("component-selection"), 3),
                    runtime.SlotCallSlotContext,
                )

                def subscribe(callback: Any) -> Any:
                    events.append("subscribe:" + name)
                    return lambda: events.append("unsubscribe:" + name)

                binding.evaluate(
                    lambda: ExternalStoreRef(name, subscribe, lambda: name), (), {}
                )

        return run

    with root.pass_scope():
        root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
        slot.invoke(resource_render("old"), (), {})
    old = slot.child_context
    candidate: Any = None
    try:
        with root.pass_scope():
            root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
            slot.invoke(resource_render("failed"), (), {})
            candidate = slot.child_context
            raise ValueError("discard replacement")
    except ValueError:
        pass
    result["resource_discard"] = [
        list(events),
        slot.child_context is old,
        candidate._mounted_callback is None,
        old._mounted_callback is not None,
    ]
    with root.pass_scope():
        root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
        slot.invoke(resource_render("superseded"), (), {})
        superseded = slot.child_context
        slot.invoke(resource_render("new"), (), {})
    new = slot.child_context
    result["replacement"] = [
        list(events),
        new is not old,
        old._mounted_callback is None,
        list(old.debug_ui()),
        superseded._mounted_callback is None,
    ]
    with root.pass_scope():
        pass
    result["omission"] = [
        list(events),
        slot.child_context is None,
        new._mounted_callback is None,
        values(),
    ]
    return result


def _verify_argument_conversion() -> None:
    root = runtime.RenderContext()
    observed: list[Any] = []
    converted = object()

    class Argument:
        def to_frozen(self) -> object:
            return converted

    def render(context: Any, argument: Any) -> None:
        with context.pass_scope():
            observed.append(argument)

    with root.pass_scope():
        slot = root._ensure_slot(
            runtime.SlotId(runtime.ModuleId("conversion"), 1),
            runtime.ComponentCallSlotContext,
        )
        slot.invoke(render, (Argument(),), {})
    assert observed == [converted]
    error = ValueError("conversion failed")

    class FailingArgument:
        def to_frozen(self) -> object:
            raise error

    try:
        with root.pass_scope():
            root._ensure_slot(slot.slot_id, runtime.ComponentCallSlotContext)
            slot.invoke(render, (FailingArgument(),), {})
    except ValueError as caught:
        assert caught is error
    else:
        raise AssertionError("failed conversion must propagate")
    assert slot.current._call_args[0] is converted
    assert observed == [converted]
    with root.pass_scope():
        root._ensure_slot(slot.slot_id, runtime.ComponentCallSlotContext)
        slot.invoke(render, (Argument(),), {})
    assert observed == [converted, converted]


if __name__ == "__main__":
    print(json.dumps(characterize(), sort_keys=True))
