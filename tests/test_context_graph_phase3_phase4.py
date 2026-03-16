from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Callable, Generic, TypeVar

import pytest

from pyrolyze.runtime.context import (
    CompValue,
    DuplicateKeyError,
    ExternalStoreRef,
    ModuleRegistry,
    RenderContext,
    SlotId,
)


T = TypeVar("T")

module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.context_graph_phase3_phase4")

_SECTION_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_FIRST_BADGE_SLOT = SlotId(_MODULE_ID, 2, line_no=11)
_SECOND_BADGE_SLOT = SlotId(_MODULE_ID, 3, line_no=12)

_LOOP_SECTION_SLOT = SlotId(_MODULE_ID, 10, line_no=20)
_FOO_LOOP_SLOT = SlotId(_MODULE_ID, 11, line_no=21)
_BAR_LOOP_SLOT = SlotId(_MODULE_ID, 12, line_no=22)
_GRIP_SLOT = SlotId(_MODULE_ID, 13, line_no=23)
_VALUE_SLOT = SlotId(_MODULE_ID, 14, line_no=24)
_BADGE_SLOT = SlotId(_MODULE_ID, 15, line_no=25)


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


def _make_container_reorder_program(log: list[tuple[object, ...]]):
    @contextmanager
    def _section(title: str, *, accent: str):
        log.append(("section.enter", title, accent))
        try:
            yield
        finally:
            log.append(("section.exit", title, accent))

    def _badge(text: str, *, tone: str) -> None:
        log.append(("badge", text, tone))

    def _pyr_container_reorder(
        ctx: RenderContext,
        reverse: CompValue[bool],
    ) -> None:
        with ctx.pass_scope():
            if reverse.dirty or ctx.visit_slot_and_dirty(_SECTION_SLOT):
                with ctx.container_call(
                    _SECTION_SLOT,
                    _section,
                    ctx.literal("Stats"),
                    accent=ctx.literal("green"),
                ) as section_ctx:
                    ordered = (
                        ((_SECOND_BADGE_SLOT, "second"), (_FIRST_BADGE_SLOT, "first"))
                        if reverse.value
                        else ((_FIRST_BADGE_SLOT, "first"), (_SECOND_BADGE_SLOT, "second"))
                    )
                    for slot_id, label in ordered:
                        if reverse.dirty or section_ctx.visit_slot_and_dirty(slot_id):
                            section_ctx.leaf_call(
                                slot_id,
                                _badge,
                                ctx.literal(label),
                                tone=ctx.literal("info"),
                            )

    return _pyr_container_reorder


def _make_nested_keyed_program(
    log: list[tuple[object, ...]],
    resolve_store: Callable[[tuple[str, str]], _StoreProbe[str]],
):
    @contextmanager
    def _section(title: str, *, accent: str):
        log.append(("section.enter", title, accent))
        try:
            yield
        finally:
            log.append(("section.exit", title, accent))

    def identity_key(value: str) -> str:
        return value

    def make_grip(foo: str, bar: str) -> tuple[str, str]:
        log.append(("make_grip", foo, bar))
        return (foo, bar)

    def use_grip(grip: tuple[str, str]) -> ExternalStoreRef[str]:
        log.append(("use_grip", grip))
        return resolve_store(grip).ref()

    def _badge(text: str, *, tone: str) -> None:
        log.append(("badge", text, tone))

    def _pyr_nested_values(
        ctx: RenderContext,
        xs: CompValue[list[str]],
        ys: CompValue[list[str]],
    ) -> None:
        with ctx.pass_scope():
            if xs.dirty or ys.dirty or ctx.visit_slot_and_dirty(_LOOP_SECTION_SLOT):
                with ctx.container_call(
                    _LOOP_SECTION_SLOT,
                    _section,
                    ctx.literal("Nested"),
                    accent=ctx.literal("violet"),
                ) as section_ctx:
                    if xs.dirty or ys.dirty or section_ctx.visit_slot_and_dirty(_FOO_LOOP_SLOT):
                        for foo_item in section_ctx.keyed_loop(_FOO_LOOP_SLOT, xs, key_fn=identity_key):
                            foo = foo_item.current_value()

                            if foo.dirty or ys.dirty or foo_item.visit_slot_and_dirty(_BAR_LOOP_SLOT):
                                for bar_item in foo_item.keyed_loop(_BAR_LOOP_SLOT, ys, key_fn=identity_key):
                                    bar = bar_item.current_value()
                                    grip = bar_item.call_plain(_GRIP_SLOT, make_grip, foo, bar)
                                    value = bar_item.call_plain(_VALUE_SLOT, use_grip, grip)

                                    if value.dirty or bar_item.visit_slot_and_dirty(_BADGE_SLOT):
                                        bar_item.leaf_call(
                                            _BADGE_SLOT,
                                            bar_item.literal(_badge),
                                            value,
                                            tone=ctx.literal("neutral"),
                                        )

    return _pyr_nested_values


def test_container_children_follow_encounter_order_after_reorder() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    pyr_container_reorder = _make_container_reorder_program(log)

    pyr_container_reorder(ctx, CompValue(False, dirty=True))
    assert ctx.debug_children_of(_SECTION_SLOT) == (_FIRST_BADGE_SLOT, _SECOND_BADGE_SLOT)

    pyr_container_reorder(ctx, CompValue(True, dirty=True))

    assert ctx.debug_children_of(_SECTION_SLOT) == (_SECOND_BADGE_SLOT, _FIRST_BADGE_SLOT)
    assert log == [
        ("section.enter", "Stats", "green"),
        ("badge", "first", "info"),
        ("badge", "second", "info"),
        ("section.exit", "Stats", "green"),
        ("section.enter", "Stats", "green"),
        ("badge", "second", "info"),
        ("badge", "first", "info"),
        ("section.exit", "Stats", "green"),
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
        CompValue(["a", "b"], dirty=True),
        CompValue(["x", "y"], dirty=True),
    )

    assert ctx.debug_children_of(_LOOP_SECTION_SLOT) == (_FOO_LOOP_SLOT,)
    foo_items = ctx.debug_children_of(_FOO_LOOP_SLOT)
    assert foo_items == (
        SlotId(_MODULE_ID, 11, key_path=("a",), line_no=21),
        SlotId(_MODULE_ID, 11, key_path=("b",), line_no=21),
    )
    bar_loop_owner = SlotId(_MODULE_ID, 12, key_path=("a",), line_no=22)
    assert ctx.debug_children_of(foo_items[0]) == (bar_loop_owner,)
    assert ctx.debug_children_of(bar_loop_owner) == (
        SlotId(_MODULE_ID, 12, key_path=("a", "x"), line_no=22),
        SlotId(_MODULE_ID, 12, key_path=("a", "y"), line_no=22),
    )

    initial_use_grip_calls = [entry for entry in log if entry[:1] == ("use_grip",)]
    assert len(initial_use_grip_calls) == 4
    assert all(store.active_listener_count == 1 for store in stores.values())

    log.clear()
    pyr_nested_values(
        ctx,
        CompValue(["b", "a"], dirty=True),
        CompValue(["y", "x"], dirty=True),
    )

    assert [entry for entry in log if entry[:1] == ("use_grip",)] == []
    assert [entry for entry in log if entry[:1] == ("subscribe",)] == []
    assert [entry for entry in log if entry[:1] == ("unsubscribe",)] == []
    assert [entry for entry in log if entry[:1] == ("badge",)] == []
    assert ctx.debug_children_of(_FOO_LOOP_SLOT) == (
        SlotId(_MODULE_ID, 11, key_path=("b",), line_no=21),
        SlotId(_MODULE_ID, 11, key_path=("a",), line_no=21),
    )


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
        CompValue(["a", "b"], dirty=True),
        CompValue(["x", "y"], dirty=True),
    )
    log.clear()

    pyr_nested_values(
        ctx,
        CompValue(["a"], dirty=True),
        CompValue(["x"], dirty=True),
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
    assert ctx.debug_children_of(_FOO_LOOP_SLOT) == (
        SlotId(_MODULE_ID, 11, key_path=("a",), line_no=21),
    )


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
            CompValue(["a", "a"], dirty=True),
            CompValue(["x"], dirty=True),
        )
