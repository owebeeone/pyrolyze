from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Generic, TypeVar

import pytest

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime.context import (
    DuplicateKeyError,
    ExternalStoreRef,
    RenderContext,
    dirtyof,
)


T = TypeVar("T")


@dataclass(slots=True)
class _StoreProbe(Generic[T]):
    name: str
    initial_value: T
    log: list[tuple[object, ...]]
    identity: object = field(default_factory=object)
    _value: T = field(init=False)
    _listeners: list[Callable[[], None]] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self._value = self.initial_value

    def ref(self) -> ExternalStoreRef[T]:
        return ExternalStoreRef(identity=self.identity, subscribe=self.subscribe, get=self.get)

    def subscribe(self, listener: Callable[[], None]) -> Callable[[], None]:
        self.log.append(("subscribe", self.name))
        self._listeners.append(listener)
        active = True

        def unsubscribe() -> None:
            nonlocal active
            if not active:
                return
            active = False
            self.log.append(("unsubscribe", self.name))
            self._listeners.remove(listener)

        return unsubscribe

    def get(self) -> T:
        self.log.append(("get", self.name, self._value))
        return self._value

    @property
    def active_listener_count(self) -> int:
        return len(self._listeners)


def _compile_graph_program(
    log: list[tuple[object, ...]],
    body: str,
    *,
    globals_dict: dict[str, object] | None = None,
) -> Callable[..., None]:
    source = '''
from pyrolyze.api import UIElement, call_native, component, keyed, pyrolyze, slotted
from pyrolyze.runtime.context import ContextBase

def section(ctx: ContextBase):
    ctx.call_native(UIElement, kind="section", props={})

@pyrolyze
def badge(text, *, tone):
    LOG.append(("badge", text, tone))
    call_native(UIElement)(kind="badge", props={"text": text, "tone": tone})
''' + body
    namespace = load_transformed_namespace(
        source,
        module_name="tests.context_graph_phase3_phase4.compiled",
        globals_dict={"LOG": log, **(globals_dict or {})},
    )
    return namespace["panel"]._pyrolyze_meta._func


def _make_container_reorder_program(log: list[tuple[object, ...]]) -> Callable[..., None]:
    return _compile_graph_program(log, '''
@pyrolyze
def panel(reverse):
    with component(section):
        for label in keyed(("second", "first") if reverse else ("first", "second"), key=lambda value: value):
            badge(label, tone="info")
''')


def _make_nested_keyed_program(
    log: list[tuple[object, ...]],
    resolve_store: Callable[[tuple[str, str]], _StoreProbe[str]],
) -> Callable[..., None]:
    def make_grip(foo: str, bar: str) -> tuple[str, str]:
        log.append(("make_grip", foo, bar))
        return (foo, bar)

    def use_grip(grip: tuple[str, str]) -> ExternalStoreRef[str]:
        log.append(("use_grip", grip))
        return resolve_store(grip).ref()

    return _compile_graph_program(log, '''
@pyrolyze
def panel(xs, ys):
    with component(section):
        for foo in keyed(xs, key=lambda value: value):
            for bar in keyed(ys, key=lambda value: value):
                grip = slotted(make_grip, foo, bar)
                value = slotted(use_grip, grip)
                badge(value, tone="neutral")
''', globals_dict={"make_grip": make_grip, "use_grip": use_grip})


def test_container_children_follow_encounter_order_after_reorder() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    pyr_container_reorder = _make_container_reorder_program(log)

    pyr_container_reorder(ctx, dirtyof(reverse=True), False)
    section = ctx.debug_children_of()[0]
    loop = ctx.debug_children_of(section)[0]
    initial_items = ctx.debug_children_of(loop)
    assert [item.key_path for item in initial_items] == [("first",), ("second",)]
    initial_ui = ctx.committed_ui()[0]
    assert [child.props["text"] for child in initial_ui.children] == ["first", "second"]

    pyr_container_reorder(ctx, dirtyof(reverse=True), True)

    assert ctx.debug_children_of(loop) == tuple(reversed(initial_items))
    assert [child.props["text"] for child in ctx.committed_ui()[0].children] == ["second", "first"]
    assert log == [
        ("badge", "first", "info"),
        ("badge", "second", "info"),
    ]


def test_nested_keyed_loops_reuse_contexts_on_reorder_and_preserve_subscriptions() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    stores = {
        ("a", "x"): _StoreProbe(name="a:x", initial_value="ax", log=log),
        ("a", "y"): _StoreProbe(name="a:y", initial_value="ay", log=log),
        ("b", "x"): _StoreProbe(name="b:x", initial_value="bx", log=log),
        ("b", "y"): _StoreProbe(name="b:y", initial_value="by", log=log),
    }
    pyr_nested_values = _make_nested_keyed_program(log, stores.__getitem__)

    pyr_nested_values(
        ctx,
        dirtyof(xs=True, ys=True),
        ["a", "b"],
        ["x", "y"],
    )

    section = ctx.debug_children_of()[0]
    foo_loop = ctx.debug_children_of(section)[0]
    foo_items = ctx.debug_children_of(foo_loop)
    assert [item.key_path for item in foo_items] == [("a",), ("b",)]
    bar_loop_owner = ctx.debug_children_of(foo_items[0])[0]
    assert ctx.debug_children_of(foo_items[0]) == (bar_loop_owner,)
    bar_items = ctx.debug_children_of(bar_loop_owner)
    assert [item.key_path for item in bar_items] == [("a", "x"), ("a", "y")]

    initial_use_grip_calls = [entry for entry in log if entry[:1] == ("use_grip",)]
    assert len(initial_use_grip_calls) == 4
    assert all(store.active_listener_count == 1 for store in stores.values())

    log.clear()
    pyr_nested_values(
        ctx,
        dirtyof(xs=True, ys=True),
        ["b", "a"],
        ["y", "x"],
    )

    assert [entry for entry in log if entry[:1] == ("use_grip",)] == []
    assert [entry for entry in log if entry[:1] == ("subscribe",)] == []
    assert [entry for entry in log if entry[:1] == ("unsubscribe",)] == []
    assert [entry for entry in log if entry[:1] == ("badge",)] == []
    assert ctx.debug_children_of(foo_loop) == tuple(reversed(foo_items))
    assert ctx.debug_children_of(bar_loop_owner) == tuple(reversed(bar_items))


def test_keyed_loop_deactivates_removed_item_subtrees_and_unsubscribes() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    stores = {
        ("a", "x"): _StoreProbe(name="a:x", initial_value="ax", log=log),
        ("a", "y"): _StoreProbe(name="a:y", initial_value="ay", log=log),
        ("b", "x"): _StoreProbe(name="b:x", initial_value="bx", log=log),
        ("b", "y"): _StoreProbe(name="b:y", initial_value="by", log=log),
    }
    pyr_nested_values = _make_nested_keyed_program(log, stores.__getitem__)

    pyr_nested_values(
        ctx,
        dirtyof(xs=True, ys=True),
        ["a", "b"],
        ["x", "y"],
    )
    section = ctx.debug_children_of()[0]
    foo_loop = ctx.debug_children_of(section)[0]
    retained_item = ctx.debug_children_of(foo_loop)[0]
    log.clear()

    pyr_nested_values(
        ctx,
        dirtyof(xs=True, ys=True),
        ["a"],
        ["x"],
    )

    assert stores[("a", "x")].active_listener_count == 1
    assert stores[("a", "y")].active_listener_count == 0
    assert stores[("b", "x")].active_listener_count == 0
    assert stores[("b", "y")].active_listener_count == 0
    assert [entry for entry in log if entry[:1] == ("unsubscribe",)] == [
        ("unsubscribe", "a:y"),
        ("unsubscribe", "b:x"),
        ("unsubscribe", "b:y"),
    ]
    assert ctx.debug_children_of(foo_loop) == (retained_item,)


def test_duplicate_keys_raise_runtime_error() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    stores = {
        ("a", "x"): _StoreProbe(name="a:x", initial_value="ax", log=log),
    }
    pyr_nested_values = _make_nested_keyed_program(log, stores.__getitem__)

    with pytest.raises(DuplicateKeyError):
        pyr_nested_values(
            ctx,
            dirtyof(xs=True, ys=True),
            ["a", "a"],
            ["x"],
        )
