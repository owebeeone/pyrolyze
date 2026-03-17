from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Callable

from pyrolyze.api import (
    CallFromNonPyrolyzeContext,
    ComponentMetadata,
    pyrolyze_component_ref,
)
from pyrolyze.runtime.context import (
    DirtyStateContext,
    ExternalStoreRef,
    ModuleRegistry,
    RenderContext,
    SlotId,
    dirtyof,
)


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.context_graph_phase5a_invalidation_kernel")

_ROOT_STORE_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_ROOT_SECTION_SLOT = SlotId(_MODULE_ID, 2, line_no=11)
_ROOT_BADGE_SLOT = SlotId(_MODULE_ID, 3, line_no=12)
_CHILD_COMPONENT_SLOT = SlotId(_MODULE_ID, 4, line_no=20)
_CHILD_STORE_SLOT = SlotId(_MODULE_ID, 5, line_no=21)
_CHILD_BADGE_SLOT = SlotId(_MODULE_ID, 6, line_no=22)
_LEFT_COMPONENT_SLOT = SlotId(_MODULE_ID, 7, line_no=30)
_RIGHT_COMPONENT_SLOT = SlotId(_MODULE_ID, 8, line_no=31)
_LEFT_STORE_SLOT = SlotId(_MODULE_ID, 9, line_no=32)
_RIGHT_STORE_SLOT = SlotId(_MODULE_ID, 10, line_no=33)
_LEFT_BADGE_SLOT = SlotId(_MODULE_ID, 11, line_no=34)
_RIGHT_BADGE_SLOT = SlotId(_MODULE_ID, 12, line_no=35)


@dataclass(slots=True)
class _StoreProbe:
    name: str
    initial_value: str
    log: list[tuple[object, ...]]
    _value: str = field(init=False)
    _listeners: list[Callable[[], None]] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self._value = self.initial_value

    def ref(self) -> ExternalStoreRef[str]:
        return ExternalStoreRef(
            identity=self.name,
            subscribe=self.subscribe,
            get=self.get,
        )

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

    def get(self) -> str:
        self.log.append(("get", self.name, self._value))
        return self._value

    def notify(self, value: str) -> None:
        self._value = value
        for listener in list(self._listeners):
            listener()


def _make_weather_program(
    log: list[tuple[object, ...]],
    store: _StoreProbe,
    *,
    on_badge: Callable[[str], None] | None = None,
) -> Callable[[RenderContext], None]:
    @contextmanager
    def _section(title: str, *, accent: str):
        log.append(("section.enter", title, accent))
        try:
            yield
        finally:
            log.append(("section.exit", title, accent))

    def _badge(text: str, *, tone: str) -> None:
        log.append(("badge", text, tone))
        if on_badge is not None:
            on_badge(text)

    def use_grip(grip_name: str) -> ExternalStoreRef[str]:
        log.append(("helper", grip_name))
        return store.ref()

    def _pyr_weather_panel(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
    ) -> None:
        with ctx.pass_scope():
            __pyr_location_dirty, location = ctx.call_plain(
                _ROOT_STORE_SLOT,
                use_grip,
                "weather",
            )

            if __pyr_location_dirty or ctx.visit_slot_and_dirty(_ROOT_SECTION_SLOT):
                with ctx.container_call(
                    _ROOT_SECTION_SLOT,
                    _section,
                    "Weather",
                    accent="blue",
                ) as section_ctx:
                    if __pyr_location_dirty or section_ctx.visit_slot_and_dirty(_ROOT_BADGE_SLOT):
                        section_ctx.leaf_call(
                            _ROOT_BADGE_SLOT,
                            _badge,
                            location,
                            tone="info",
                        )

    return lambda ctx: _pyr_weather_panel(ctx, dirtyof())


def _make_parent_child_program(
    log: list[tuple[object, ...]],
    parent_store: _StoreProbe,
    child_store: _StoreProbe,
) -> Callable[[RenderContext], None]:
    @contextmanager
    def _section(title: str, *, accent: str):
        log.append(("section.enter", title, accent))
        try:
            yield
        finally:
            log.append(("section.exit", title, accent))

    def _badge(text: str, *, tone: str) -> None:
        log.append(("badge", text, tone))

    def use_parent_grip(grip_name: str) -> ExternalStoreRef[str]:
        log.append(("parent.helper", grip_name))
        return parent_store.ref()

    def use_child_grip(grip_name: str) -> ExternalStoreRef[str]:
        log.append(("child.helper", grip_name))
        return child_store.ref()

    def __pyr_child_badge(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
    ) -> None:
        with ctx.pass_scope():
            __pyr_value_dirty, value = ctx.call_plain(
                _CHILD_STORE_SLOT,
                use_child_grip,
                "child",
            )

            if __pyr_value_dirty or ctx.visit_slot_and_dirty(_CHILD_BADGE_SLOT):
                ctx.leaf_call(
                    _CHILD_BADGE_SLOT,
                    _badge,
                    value,
                    tone="child",
                )

    @pyrolyze_component_ref(ComponentMetadata("child_badge", __pyr_child_badge))
    def child_badge() -> None:
        raise CallFromNonPyrolyzeContext("child_badge")

    def _pyr_parent_panel(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
    ) -> None:
        with ctx.pass_scope():
            __pyr_parent_dirty, parent_value = ctx.call_plain(
                _ROOT_STORE_SLOT,
                use_parent_grip,
                "parent",
            )

            if __pyr_parent_dirty or ctx.visit_slot_and_dirty(_ROOT_SECTION_SLOT):
                with ctx.container_call(
                    _ROOT_SECTION_SLOT,
                    _section,
                    "Parent",
                    accent="green",
                ) as section_ctx:
                    if __pyr_parent_dirty or section_ctx.visit_slot_and_dirty(_ROOT_BADGE_SLOT):
                        section_ctx.leaf_call(
                            _ROOT_BADGE_SLOT,
                            _badge,
                            parent_value,
                            tone="parent",
                        )

                    if section_ctx.visit_slot_and_dirty(_CHILD_COMPONENT_SLOT):
                        section_ctx.component_call(
                            _CHILD_COMPONENT_SLOT,
                            child_badge,
                            dirty_state=dirtyof(),
                        )

    return lambda ctx: _pyr_parent_panel(ctx, dirtyof())


def _make_sibling_component_program(
    log: list[tuple[object, ...]],
    left_store: _StoreProbe,
    right_store: _StoreProbe,
) -> Callable[[RenderContext], None]:
    def _badge(text: str, *, tone: str) -> None:
        log.append(("badge", text, tone))

    def use_left_grip(grip_name: str) -> ExternalStoreRef[str]:
        log.append(("left.helper", grip_name))
        return left_store.ref()

    def use_right_grip(grip_name: str) -> ExternalStoreRef[str]:
        log.append(("right.helper", grip_name))
        return right_store.ref()

    def __pyr_left_badge(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
    ) -> None:
        with ctx.pass_scope():
            __pyr_value_dirty, value = ctx.call_plain(
                _LEFT_STORE_SLOT,
                use_left_grip,
                "left",
            )
            if __pyr_value_dirty or ctx.visit_slot_and_dirty(_LEFT_BADGE_SLOT):
                ctx.leaf_call(
                    _LEFT_BADGE_SLOT,
                    _badge,
                    value,
                    tone="left",
                )

    @pyrolyze_component_ref(ComponentMetadata("left_badge", __pyr_left_badge))
    def left_badge() -> None:
        raise CallFromNonPyrolyzeContext("left_badge")

    def __pyr_right_badge(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
    ) -> None:
        with ctx.pass_scope():
            __pyr_value_dirty, value = ctx.call_plain(
                _RIGHT_STORE_SLOT,
                use_right_grip,
                "right",
            )
            if __pyr_value_dirty or ctx.visit_slot_and_dirty(_RIGHT_BADGE_SLOT):
                ctx.leaf_call(
                    _RIGHT_BADGE_SLOT,
                    _badge,
                    value,
                    tone="right",
                )

    @pyrolyze_component_ref(ComponentMetadata("right_badge", __pyr_right_badge))
    def right_badge() -> None:
        raise CallFromNonPyrolyzeContext("right_badge")

    def _pyr_siblings(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
    ) -> None:
        with ctx.pass_scope():
            if ctx.visit_slot_and_dirty(_LEFT_COMPONENT_SLOT):
                ctx.component_call(
                    _LEFT_COMPONENT_SLOT,
                    left_badge,
                    dirty_state=dirtyof(),
                )

            if ctx.visit_slot_and_dirty(_RIGHT_COMPONENT_SLOT):
                ctx.component_call(
                    _RIGHT_COMPONENT_SLOT,
                    right_badge,
                    dirty_state=dirtyof(),
                )

    return lambda ctx: _pyr_siblings(ctx, dirtyof())


def test_external_store_notification_queues_mounted_root_once_and_reruns_on_drain() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    store = _StoreProbe("weather", "sunny", log)
    program = _make_weather_program(log, store)

    ctx.mount(lambda: program(ctx))
    log.clear()

    store.notify("rain")
    store.notify("wind")

    assert ctx.debug_pending_boundaries() == (None,)

    ctx.run_pending_invalidations()

    assert log == [
        ("get", "weather", "wind"),
        ("section.enter", "Weather", "blue"),
        ("badge", "wind", "info"),
        ("section.exit", "Weather", "blue"),
    ]
    assert ctx.debug_pending_boundaries() == ()


def test_invalidation_during_active_pass_coalesces_to_one_follow_up_rerun() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    store = _StoreProbe("weather", "sunny", log)
    triggered = False

    def on_badge(text: str) -> None:
        nonlocal triggered
        if text != "rain" or triggered:
            return
        triggered = True
        store.notify("storm")
        store.notify("storm")

    program = _make_weather_program(log, store, on_badge=on_badge)

    ctx.mount(lambda: program(ctx))
    log.clear()

    store.notify("rain")
    ctx.run_pending_invalidations()

    assert log == [
        ("get", "weather", "rain"),
        ("section.enter", "Weather", "blue"),
        ("badge", "rain", "info"),
        ("section.exit", "Weather", "blue"),
        ("get", "weather", "storm"),
        ("section.enter", "Weather", "blue"),
        ("badge", "storm", "info"),
        ("section.exit", "Weather", "blue"),
    ]
    assert ctx.debug_pending_boundaries() == ()


def test_child_component_invalidation_reruns_only_child_component_boundary() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    parent_store = _StoreProbe("parent", "P1", log)
    child_store = _StoreProbe("child", "C1", log)
    program = _make_parent_child_program(log, parent_store, child_store)

    ctx.mount(lambda: program(ctx))
    log.clear()

    child_store.notify("C2")

    assert ctx.debug_pending_boundaries() == (_CHILD_COMPONENT_SLOT,)

    ctx.run_pending_invalidations()

    assert log == [
        ("get", "child", "C2"),
        ("badge", "C2", "child"),
    ]
    assert ctx.debug_pending_boundaries() == ()


def test_queued_ancestor_root_elides_queued_child_component_boundary() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    parent_store = _StoreProbe("parent", "P1", log)
    child_store = _StoreProbe("child", "C1", log)
    program = _make_parent_child_program(log, parent_store, child_store)

    ctx.mount(lambda: program(ctx))
    log.clear()

    child_store.notify("C2")
    assert ctx.debug_pending_boundaries() == (_CHILD_COMPONENT_SLOT,)

    parent_store.notify("P2")
    assert ctx.debug_pending_boundaries() == (None,)

    ctx.run_pending_invalidations()

    assert log == [
        ("get", "parent", "P2"),
        ("section.enter", "Parent", "green"),
        ("badge", "P2", "parent"),
        ("get", "child", "C2"),
        ("badge", "C2", "child"),
        ("section.exit", "Parent", "green"),
    ]
    assert ctx.debug_pending_boundaries() == ()


def test_sibling_component_invalidations_are_deduplicated_fifo() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    left_store = _StoreProbe("left", "L1", log)
    right_store = _StoreProbe("right", "R1", log)
    program = _make_sibling_component_program(log, left_store, right_store)

    ctx.mount(lambda: program(ctx))
    log.clear()

    right_store.notify("R2")
    left_store.notify("L2")
    right_store.notify("R3")

    assert ctx.debug_pending_boundaries() == (_RIGHT_COMPONENT_SLOT, _LEFT_COMPONENT_SLOT)

    ctx.run_pending_invalidations()

    assert log == [
        ("get", "right", "R3"),
        ("badge", "R3", "right"),
        ("get", "left", "L2"),
        ("badge", "L2", "left"),
    ]
    assert ctx.debug_pending_boundaries() == ()
