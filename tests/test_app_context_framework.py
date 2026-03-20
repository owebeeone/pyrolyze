from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pytest

from pyrolyze.api import CallFromNonPyrolyzeContext, ComponentMetadata, pyrolyze_component_ref
from pyrolyze.runtime import (
    AppContextKey,
    AppContextStore,
    ContextBase,
    DirtyStateContext,
    ExternalStoreRef,
    ModuleRegistry,
    PlainCallRuntimeContext,
    RenderContext,
    SlotId,
    dirtyof,
)


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.app_context_framework")

_PLAIN_WRITE_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_PLAIN_READ_SLOT = SlotId(_MODULE_ID, 2, line_no=11)
_NATIVE_SLOT = SlotId(_MODULE_ID, 3, line_no=12)
_COMPONENT_SLOT = SlotId(_MODULE_ID, 4, line_no=13)
_STORE_SLOT = SlotId(_MODULE_ID, 5, line_no=14)


@dataclass(slots=True)
class SharedState:
    values: list[str] = field(default_factory=list)


@dataclass(slots=True)
class _StoreProbe:
    value: str
    listeners: list[Callable[[], None]] = field(default_factory=list)

    def ref(self) -> ExternalStoreRef[str]:
        return ExternalStoreRef(identity=self, subscribe=self.subscribe, get=self.get)

    def subscribe(self, listener: Callable[[], None]) -> Callable[[], None]:
        self.listeners.append(listener)

        def unsubscribe() -> None:
            self.listeners.remove(listener)

        return unsubscribe

    def get(self) -> str:
        return self.value


def test_app_context_store_is_identity_based_and_lazy() -> None:
    log: list[tuple[str, str, object | None]] = []

    def first_factory(host_app: object | None) -> dict[str, str]:
        log.append(("factory", "first", host_app))
        return {"value": "first"}

    def second_factory(host_app: object | None) -> dict[str, str]:
        log.append(("factory", "second", host_app))
        return {"value": "second"}

    first = AppContextKey("shared.debug", factory=first_factory)
    second = AppContextKey("shared.debug", factory=second_factory)
    store = AppContextStore(host_app="HOST")

    assert store.has(first) is False
    assert store.has(second) is False

    first_value = store.get(first)
    second_value = store.get(second)

    assert first_value == {"value": "first"}
    assert second_value == {"value": "second"}
    assert first_value is store.get(first)
    assert second_value is store.get(second)
    assert first_value is not second_value
    assert log == [
        ("factory", "first", "HOST"),
        ("factory", "second", "HOST"),
    ]


def test_app_context_store_closes_in_reverse_creation_order() -> None:
    log: list[tuple[str, str]] = []

    first = AppContextKey(
        "first",
        factory=lambda _host: "alpha",
        close=lambda value: log.append(("close", value)),
    )
    second = AppContextKey(
        "second",
        factory=lambda _host: "beta",
        close=lambda value: log.append(("close", value)),
    )

    store = AppContextStore()
    assert store.get(first) == "alpha"
    assert store.get(second) == "beta"

    store.close_all()
    store.close_all()

    assert log == [
        ("close", "beta"),
        ("close", "alpha"),
    ]

    with pytest.raises(RuntimeError, match="closed"):
        store.get(first)


def test_app_context_store_caches_none_values_and_closes_once() -> None:
    log: list[tuple[str, object | None]] = []

    key = AppContextKey(
        "none",
        factory=lambda host: log.append(("factory", host)) or None,
        close=lambda value: log.append(("close", value)),
    )
    store = AppContextStore(host_app="HOST")

    assert store.has(key) is False
    assert store.get(key) is None
    assert store.has(key) is True
    assert store.get(key) is None

    store.close_all()
    store.close_all()

    assert log == [
        ("factory", "HOST"),
        ("close", None),
    ]


def test_plain_native_and_child_component_contexts_share_app_context() -> None:
    key = AppContextKey("shared.state", factory=lambda host_app: SharedState(values=[f"host:{host_app}"]))

    def remember(value: str, *, __pyrolyze_ctx: PlainCallRuntimeContext) -> int:
        shared = __pyrolyze_ctx.get_app_context(key)
        shared.values.append(f"plain:{value}")
        return len(shared.values)

    def snapshot(*, __pyrolyze_ctx: PlainCallRuntimeContext) -> tuple[str, ...]:
        return tuple(__pyrolyze_ctx.get_app_context(key).values)

    def mark_native(ctx: ContextBase, value: str) -> None:
        ctx.get_app_context(key).values.append(f"native:{value}")

    def __pyr_child(child_ctx: RenderContext, __pyr_dirty_state: DirtyStateContext, label: str) -> None:
        _ = __pyr_dirty_state
        with child_ctx.pass_scope():
            child_ctx.get_app_context(key).values.append(f"child:{label}")

    @pyrolyze_component_ref(ComponentMetadata("child", __pyr_child))
    def child(label: str) -> None:
        raise CallFromNonPyrolyzeContext("child")

    ctx = RenderContext(app_context_store=AppContextStore(host_app="APP"))

    with ctx.pass_scope():
        __pyr_count_dirty, count = ctx.call_plain(_PLAIN_WRITE_SLOT, remember, "alpha")
        _ = __pyr_count_dirty
        ctx.leaf_call(_NATIVE_SLOT, mark_native, "beta")
        ctx.component_call(
            _COMPONENT_SLOT,
            child,
            "gamma",
            dirty_state=dirtyof(label=True),
        )
        __pyr_values_dirty, values = ctx.call_plain(_PLAIN_READ_SLOT, snapshot)
        _ = __pyr_values_dirty

    assert count == 2
    assert values == (
        "host:APP",
        "plain:alpha",
        "native:beta",
        "child:gamma",
    )
    assert ctx.get_app_context(key).values == list(values)


def test_generation_tracker_is_shared_and_advances_on_committed_boundary_reruns() -> None:
    store = _StoreProbe(value="cold")
    log: list[tuple[str, object]] = []

    def use_store() -> ExternalStoreRef[str]:
        return store.ref()

    def __pyr_child(child_ctx: RenderContext, __pyr_dirty_state: DirtyStateContext) -> None:
        _ = __pyr_dirty_state
        with child_ctx.pass_scope():
            log.append(("generation", child_ctx.current_generation_id()))
            __pyr_store_dirty, value = child_ctx.call_plain(_STORE_SLOT, use_store)
            _ = __pyr_store_dirty
            log.append(("value", value))

    @pyrolyze_component_ref(ComponentMetadata("child", __pyr_child))
    def child() -> None:
        raise CallFromNonPyrolyzeContext("child")

    ctx = RenderContext()

    def render() -> None:
        with ctx.pass_scope():
            ctx.component_call(_COMPONENT_SLOT, child, dirty_state=dirtyof())

    ctx.mount(render)

    assert ctx.current_generation_id() == 1
    assert log == [
        ("generation", 1),
        ("value", "cold"),
    ]

    store.value = "warm"
    store.listeners[0]()
    ctx.run_pending_invalidations()

    assert ctx.current_generation_id() == 2
    assert log == [
        ("generation", 1),
        ("value", "cold"),
        ("generation", 2),
        ("value", "warm"),
    ]
