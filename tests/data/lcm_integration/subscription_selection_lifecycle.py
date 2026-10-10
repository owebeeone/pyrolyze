"""Outer-render subscription ownership and actual cleanup events."""

from __future__ import annotations

from dataclasses import dataclass, field
import gc
import json
from typing import Any, Callable
import weakref

from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.slot_call_semantics import ExternalStoreRef


@dataclass
class Store:
    name: str
    value: int
    events: list[list[Any]]
    callbacks: list[Callable[[], None]] = field(default_factory=list)

    def subscribe(self, callback: Callable[[], None]) -> Callable[[], None]:
        self.events.append(["subscribe", self.name])
        self.callbacks.append(callback)

        def unsubscribe() -> None:
            self.events.append(["unsubscribe", self.name])
            self.callbacks.remove(callback)

        return unsubscribe

    def get(self) -> int:
        self.events.append(["get", self.name, self.value])
        return self.value

    def ref(self) -> ExternalStoreRef[int]:
        return ExternalStoreRef(self.name, self.subscribe, self.get)

    def notify(self, value: int) -> None:
        self.value = value
        for callback in tuple(self.callbacks):
            callback()


def _id() -> Any:
    return runtime.SlotId(runtime.ModuleId("tests.subscription_selection"), 1)


def _source(ref: ExternalStoreRef[int]) -> ExternalStoreRef[int]:
    return ref


def characterize() -> dict[str, Any]:
    events: list[list[Any]] = []
    a, b, c = (
        Store(name, value, events) for name, value in (("a", 1), ("b", 3), ("c", 4))
    )
    root = runtime.RenderContext()
    slot: Any = None

    def evaluate(store: Store) -> Any:
        nonlocal slot
        slot = root._ensure_slot(_id(), runtime.SlotCallSlotContext)
        return slot.evaluate(_source, (store.ref(),), {})

    result: dict[str, Any] = {}
    with root.pass_scope():
        evaluate(a)
        result["pending_accepted"] = slot._binding_owner.is_accepted
    facts = {
        row["field_name"]: row
        for row in slot.__yidl_lifecycle_definition__["fields"]
    }
    result["owned"] = facts["_binding_owner"]["field_kind"] == "owned"
    result["initial"] = [
        slot.binding.exposed_value(),
        slot.current._binding_owner.is_accepted,
    ]

    a.notify(2)
    try:
        with root.pass_scope():
            refreshed = evaluate(a)
            result["pending_refresh"] = [slot.binding.exposed_value(), refreshed.value]
            raise ValueError("parent failed")
    except ValueError:
        pass
    result["failed_refresh"] = [slot.binding.exposed_value(), len(a.callbacks)]
    with root.pass_scope():
        refreshed = evaluate(a)
    result["retried_refresh"] = [refreshed.value, slot.binding.exposed_value()]

    try:
        with root.pass_scope():
            evaluate(b)
            result["pending_replacement"] = [
                slot.binding.exposed_value(),
                len(a.callbacks),
                len(b.callbacks),
            ]
            raise ValueError("replace failed")
    except ValueError:
        pass
    result["failed_replacement"] = [
        slot.binding.exposed_value(),
        len(a.callbacks),
        len(b.callbacks),
    ]
    with root.pass_scope():
        evaluate(b)
    result["committed_replacement"] = [
        slot.binding.exposed_value(),
        len(a.callbacks),
        len(b.callbacks),
    ]

    retained = slot.binding
    with root.pass_scope():
        slot._invoke_dirty = True
        evaluate(b)
    result["same_subscription"] = slot.binding.resource is retained.resource
    with root.pass_scope():
        evaluate(c)
    result["retained_old"] = [len(b.callbacks), len(c.callbacks)]
    del retained
    result["released_old"] = [len(b.callbacks), len(c.callbacks)]
    with root.pass_scope():
        pass
    result["omitted"] = [slot.binding is None, len(c.callbacks)]

    with root.pass_scope():
        evaluate(a)
    try:
        with root.pass_scope():
            slot.deactivate()
            raise ValueError("remove failed")
    except ValueError:
        pass
    result["failed_removal"] = [slot.binding.exposed_value(), len(a.callbacks)]
    with root.pass_scope():
        slot.deactivate()
    result["explicit_removal"] = [slot.binding is None, len(a.callbacks)]
    result["ready"] = root._field_only_completion.last.reuse_ready
    result["events"] = events

    live = Store("live", 5, [])
    graph = runtime.RenderContext()
    with graph.pass_scope():
        child = graph._ensure_slot(_id(), runtime.SlotCallSlotContext)
        child.evaluate(_source, (live.ref(),), {})
    graph_ref = weakref.ref(graph)
    del graph, child
    gc.collect()
    result["no_store_graph_cycle"] = graph_ref() is None and not live.callbacks
    result["collection_events"] = live.events
    return result


if __name__ == "__main__":
    print(json.dumps(characterize(), indent=2, sort_keys=True))
