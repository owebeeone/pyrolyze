from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import pytest
from textwrap import dedent
from typing import Callable

from pyrolyze.api import (
    CallFromNonPyrolyzeContext,
    ComponentMetadata,
    pyrolyze_component_ref,
)
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime.context import (
    DirtyStateContext,
    ExternalStoreRef,
    ModuleRegistry,
    RenderContext,
    SlotId,
    dirtyof,
)
from pyrolyze_testsupport import pyrolize_test_wrap
from tests.slot_expr_test_utils import eval_single_slot_expr


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


@dataclass(slots=True)
class _IntStoreProbe:
    name: str
    initial_value: int
    log: list[tuple[object, ...]]
    _value: int = field(init=False)
    _listeners: list[Callable[[], None]] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self._value = self.initial_value

    def ref(self) -> ExternalStoreRef[int]:
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

    def get(self) -> int:
        self.log.append(("get", self.name, self._value))
        return self._value

    def notify(self, value: int) -> None:
        self._value = value
        for listener in list(self._listeners):
            listener()

    @property
    def active_listener_count(self) -> int:
        return len(self._listeners)


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

    @pyrolize_test_wrap
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
            __pyr_location_dirty, location = eval_single_slot_expr(
                ctx,
                __pyr_dirty_state,
                _ROOT_STORE_SLOT,
                use_grip,
                "weather",
                result_name="location",
            )

            if __pyr_location_dirty or ctx.visit_slot_and_dirty(_ROOT_SECTION_SLOT):
                with ctx.container_call(
                    _ROOT_SECTION_SLOT,
                    _section,
                    "Weather",
                    accent="blue",
                ) as section_ctx:
                    if __pyr_location_dirty or section_ctx.visit_slot_and_dirty(_ROOT_BADGE_SLOT):
                        section_ctx.component_call(
                            _ROOT_BADGE_SLOT,
                            _badge,
                            location,
                            tone="info",
                            dirty_state=dirtyof(text=__pyr_location_dirty, tone=False),
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

    @pyrolize_test_wrap
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
            __pyr_value_dirty, value = eval_single_slot_expr(
                ctx,
                __pyr_dirty_state,
                _CHILD_STORE_SLOT,
                use_child_grip,
                "child",
                result_name="value",
            )

            if __pyr_value_dirty or ctx.visit_slot_and_dirty(_CHILD_BADGE_SLOT):
                ctx.component_call(
                    _CHILD_BADGE_SLOT,
                    _badge,
                    value,
                    tone="child",
                    dirty_state=dirtyof(text=__pyr_value_dirty, tone=False),
                )

    @pyrolyze_component_ref(ComponentMetadata("child_badge", __pyr_child_badge))
    def child_badge() -> None:
        raise CallFromNonPyrolyzeContext("child_badge")

    def _pyr_parent_panel(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
    ) -> None:
        with ctx.pass_scope():
            __pyr_parent_dirty, parent_value = eval_single_slot_expr(
                ctx,
                __pyr_dirty_state,
                _ROOT_STORE_SLOT,
                use_parent_grip,
                "parent",
                result_name="parent_value",
            )

            if __pyr_parent_dirty or ctx.visit_slot_and_dirty(_ROOT_SECTION_SLOT):
                with ctx.container_call(
                    _ROOT_SECTION_SLOT,
                    _section,
                    "Parent",
                    accent="green",
                ) as section_ctx:
                    if __pyr_parent_dirty or section_ctx.visit_slot_and_dirty(_ROOT_BADGE_SLOT):
                        section_ctx.component_call(
                            _ROOT_BADGE_SLOT,
                            _badge,
                            parent_value,
                            tone="parent",
                            dirty_state=dirtyof(text=__pyr_parent_dirty, tone=False),
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
    @pyrolize_test_wrap
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
            __pyr_value_dirty, value = eval_single_slot_expr(
                ctx,
                __pyr_dirty_state,
                _LEFT_STORE_SLOT,
                use_left_grip,
                "left",
                result_name="value",
            )
            if __pyr_value_dirty or ctx.visit_slot_and_dirty(_LEFT_BADGE_SLOT):
                ctx.component_call(
                    _LEFT_BADGE_SLOT,
                    _badge,
                    value,
                    tone="left",
                    dirty_state=dirtyof(text=__pyr_value_dirty, tone=False),
                )

    @pyrolyze_component_ref(ComponentMetadata("left_badge", __pyr_left_badge))
    def left_badge() -> None:
        raise CallFromNonPyrolyzeContext("left_badge")

    def __pyr_right_badge(
        ctx: RenderContext,
        __pyr_dirty_state: DirtyStateContext,
    ) -> None:
        with ctx.pass_scope():
            __pyr_value_dirty, value = eval_single_slot_expr(
                ctx,
                __pyr_dirty_state,
                _RIGHT_STORE_SLOT,
                use_right_grip,
                "right",
                result_name="value",
            )
            if __pyr_value_dirty or ctx.visit_slot_and_dirty(_RIGHT_BADGE_SLOT):
                ctx.component_call(
                    _RIGHT_BADGE_SLOT,
                    _badge,
                    value,
                    tone="right",
                    dirty_state=dirtyof(text=__pyr_value_dirty, tone=False),
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


def test_compiled_three_external_store_sum_notification_queues_rerender_and_updates_total() -> None:
    source = dedent("""
        from pyrolyze.api import pyrolyze, pyrolyze_slotted
        from tests.external_store_test_utils import StoreProbe

        LOG = []
        TOTALS = []

        STORES = {
            "A": StoreProbe("A", 1, LOG),
            "B": StoreProbe("B", 2, LOG),
            "C": StoreProbe("C", 3, LOG),
        }

        def notify(key, value):
            STORES[key].notify(value)

        @pyrolyze_slotted
        def use_grip(key):
            return STORES[key].ref()

        @pyrolyze
        def panel():
            total = use_grip("A") + use_grip("B") + use_grip("C")
            TOTALS.append(total)
    """)

    namespace = load_transformed_namespace(
        source,
        module_name="tests.phase5a.compiled_three_external_store_sum",
        filename="/virtual/tests/phase5a/compiled_three_external_store_sum.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    ctx.mount(lambda: panel._pyrolyze_meta._func(ctx, dirtyof()))

    assert namespace["TOTALS"] == [6]
    assert ctx.debug_pending_boundaries() == ()

    namespace["LOG"].clear()
    namespace["notify"]("A", 10)

    assert ctx.debug_pending_boundaries() == (None,)

    ctx.run_pending_invalidations()

    assert namespace["TOTALS"] == [6, 15]
    assert ctx.debug_pending_boundaries() == ()
    assert ("get", "A", 10) in namespace["LOG"]
    assert ("helper", "A") not in namespace["LOG"]


def test_compiled_slotted_helper_switches_between_external_store_and_constant_and_reconnects() -> None:
    source = dedent("""
        from typing import Any, cast

        from pyrolyze.api import pyrolyze, pyrolyze_slotted
        from pyrolyze.runtime import SlotRuntimeContext
        from tests.external_store_test_utils import StoreProbe

        LOG = []
        VALUES = []

        STORE_A = StoreProbe("A", 5, LOG)

        def notify(key, value):
            if key != "A":
                raise AssertionError(key)
            STORE_A.notify(value)

        @pyrolyze_slotted
        def use_grip(key):
            if key != "A":
                raise AssertionError(key)
            return STORE_A.ref()

        @pyrolyze_slotted
        def const_or_value(select: bool, runtime: SlotRuntimeContext = cast(Any, None)):
            LOG.append(("const_or_value", select, runtime is not None))
            if select:
                return use_grip("A")
            return 10

        @pyrolyze
        def panel(select: bool):
            value = const_or_value(select)
            VALUES.append(value)
    """)

    namespace = load_transformed_namespace(
        source,
        module_name="tests.phase5a.compiled_const_or_value",
        filename="/virtual/tests/phase5a/compiled_const_or_value.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()
    current_select = True
    current_dirty = True

    def render() -> None:
        panel._pyrolyze_meta._func(ctx, dirtyof(select=current_dirty), current_select)

    ctx.mount(render)

    assert namespace["VALUES"] == [5]
    assert len(namespace["STORE_A"].listeners) == 1

    namespace["LOG"].clear()
    current_select = False
    current_dirty = True
    ctx._run_boundary()
    current_dirty = False

    assert namespace["VALUES"] == [5, 10]
    assert len(namespace["STORE_A"].listeners) == 0
    assert ("unsubscribe", "A") in namespace["LOG"]
    assert ctx.debug_pending_boundaries() == ()

    namespace["LOG"].clear()
    namespace["notify"]("A", 9)
    assert ctx.debug_pending_boundaries() == ()
    assert namespace["VALUES"] == [5, 10]

    namespace["LOG"].clear()
    current_select = True
    current_dirty = True
    ctx._run_boundary()
    current_dirty = False

    assert namespace["VALUES"] == [5, 10, 9]
    assert len(namespace["STORE_A"].listeners) == 1
    assert ("subscribe", "A") in namespace["LOG"]

    namespace["LOG"].clear()
    namespace["notify"]("A", 11)
    assert ctx.debug_pending_boundaries() == (None,)
    ctx.run_pending_invalidations()
    assert namespace["VALUES"] == [5, 10, 9, 11]


def test_compiled_nested_external_store_chain_rebinds_only_when_downstream_key_changes() -> None:
    source = dedent("""
        from pyrolyze.api import pyrolyze, pyrolyze_slotted
        from tests.external_store_test_utils import StoreProbe

        LOG = []
        VALUES = []

        STORES = {
            "A": StoreProbe("A", "B", LOG),
            "B": StoreProbe("B", "D", LOG),
            "C": StoreProbe("C", "D", LOG),
            "D": StoreProbe("D", 1, LOG),
            "E": StoreProbe("E", 2, LOG),
        }

        def notify(key, value):
            STORES[key].notify(value)

        @pyrolyze_slotted
        def use_grip(key):
            LOG.append(("helper", key))
            return STORES[key].ref()

        @pyrolyze
        def panel():
            value = use_grip(use_grip(use_grip("A")))
            VALUES.append(value)
    """)

    namespace = load_transformed_namespace(
        source,
        module_name="tests.phase5a.compiled_nested_external_store_chain",
        filename="/virtual/tests/phase5a/compiled_nested_external_store_chain.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    ctx.mount(lambda: panel._pyrolyze_meta._func(ctx, dirtyof()))

    assert namespace["VALUES"] == [1]
    assert len(namespace["STORES"]["A"].listeners) == 1
    assert len(namespace["STORES"]["B"].listeners) == 1
    assert len(namespace["STORES"]["C"].listeners) == 0
    assert len(namespace["STORES"]["D"].listeners) == 1
    assert len(namespace["STORES"]["E"].listeners) == 0

    namespace["LOG"].clear()
    namespace["notify"]("A", "C")

    assert ctx.debug_pending_boundaries() == (None,)
    ctx.run_pending_invalidations()

    assert namespace["VALUES"] == [1, 1]
    assert ("get", "A", "C") in namespace["LOG"]
    assert ("helper", "C") in namespace["LOG"]
    assert ("subscribe", "C") in namespace["LOG"]
    assert ("unsubscribe", "B") in namespace["LOG"]
    assert ("helper", "D") not in namespace["LOG"]
    assert ("subscribe", "D") not in namespace["LOG"]
    assert ("unsubscribe", "D") not in namespace["LOG"]
    assert len(namespace["STORES"]["A"].listeners) == 1
    assert len(namespace["STORES"]["B"].listeners) == 0
    assert len(namespace["STORES"]["C"].listeners) == 1
    assert len(namespace["STORES"]["D"].listeners) == 1
    assert len(namespace["STORES"]["E"].listeners) == 0

    namespace["LOG"].clear()
    namespace["notify"]("C", "E")

    assert ctx.debug_pending_boundaries() == (None,)
    ctx.run_pending_invalidations()

    assert namespace["VALUES"] == [1, 1, 2]
    assert ("get", "C", "E") in namespace["LOG"]
    assert ("helper", "E") in namespace["LOG"]
    assert ("subscribe", "E") in namespace["LOG"]
    assert ("unsubscribe", "D") in namespace["LOG"]
    assert ("helper", "C") not in namespace["LOG"]
    assert ("subscribe", "C") not in namespace["LOG"]
    assert ("unsubscribe", "C") not in namespace["LOG"]
    assert len(namespace["STORES"]["A"].listeners) == 1
    assert len(namespace["STORES"]["B"].listeners) == 0
    assert len(namespace["STORES"]["C"].listeners) == 1
    assert len(namespace["STORES"]["D"].listeners) == 0
    assert len(namespace["STORES"]["E"].listeners) == 1


def test_compiled_additional_nested_store_value_expressions() -> None:
    source = dedent("""
        from pyrolyze.api import pyrolyze, pyrolyze_slotted
        from tests.external_store_test_utils import StoreProbe

        LOG = []
        SUMS = []
        SHARED = []
        SWITCHED = []
        TUPLES = []

        STORES = {
            "A": StoreProbe("A", "D", LOG),
            "B": StoreProbe("B", "E", LOG),
            "C": StoreProbe("C", 4, LOG),
            "D": StoreProbe("D", 1, LOG),
            "E": StoreProbe("E", 2, LOG),
            "PAIR": StoreProbe("PAIR", ("D", "E"), LOG),
        }

        def notify(key, value):
            STORES[key].notify(value)

        @pyrolyze_slotted
        def use_grip(key):
            LOG.append(("helper", key))
            return STORES[key].ref()

        @pyrolyze
        def panel_nested_sum():
            v = use_grip(use_grip("A")) + use_grip(use_grip("B"))
            SUMS.append(v)

        @pyrolyze
        def panel_shared_inner():
            k = use_grip("A")
            v = use_grip(k) + use_grip(k)
            SHARED.append(v)

        @pyrolyze
        def panel_switch(flag: bool):
            k = use_grip("A")
            current = use_grip(k)
            v = 10 if flag else current
            SWITCHED.append(v)

        @pyrolyze
        def panel_tuple_keys():
            left_key, right_key = use_grip("PAIR")
            total = use_grip(left_key) + use_grip(right_key)
            TUPLES.append(total)
    """)

    def load_namespace():
        return load_transformed_namespace(
            source,
            module_name="tests.phase5a.compiled_additional_nested_store_values",
            filename="/virtual/tests/phase5a/compiled_additional_nested_store_values.py",
        )

    namespace = load_namespace()
    ctx = RenderContext()
    ctx.mount(lambda: namespace["panel_nested_sum"]._pyrolyze_meta._func(ctx, dirtyof()))
    assert namespace["SUMS"] == [3]
    namespace["LOG"].clear()
    namespace["notify"]("D", 10)
    assert ctx.debug_pending_boundaries() == (None,)
    ctx.run_pending_invalidations()
    assert namespace["SUMS"] == [3, 12]
    assert ("get", "D", 10) in namespace["LOG"]

    namespace = load_namespace()
    ctx = RenderContext()
    namespace["LOG"].clear()
    ctx.mount(lambda: namespace["panel_shared_inner"]._pyrolyze_meta._func(ctx, dirtyof()))
    assert namespace["SHARED"] == [2]
    assert len(namespace["STORES"]["A"].listeners) == 1
    assert len(namespace["STORES"]["D"].listeners) == 2
    namespace["notify"]("A", "E")
    assert ctx.debug_pending_boundaries() == (None,)
    ctx.run_pending_invalidations()
    assert namespace["SHARED"] == [2, 4]
    assert len(namespace["STORES"]["D"].listeners) == 0
    assert len(namespace["STORES"]["E"].listeners) == 2

    namespace = load_namespace()
    ctx = RenderContext()
    current_flag = False
    current_dirty = True

    def render_switch() -> None:
        namespace["panel_switch"]._pyrolyze_meta._func(ctx, dirtyof(flag=current_dirty), current_flag)

    namespace["LOG"].clear()
    ctx.mount(render_switch)
    current_dirty = False
    assert namespace["SWITCHED"] == [1]
    assert len(namespace["STORES"]["A"].listeners) == 1
    assert len(namespace["STORES"]["D"].listeners) == 1
    current_flag = True
    current_dirty = True
    ctx._run_boundary()
    current_dirty = False
    assert namespace["SWITCHED"] == [1, 10]
    assert len(namespace["STORES"]["A"].listeners) == 1
    assert len(namespace["STORES"]["D"].listeners) == 1
    current_flag = False
    current_dirty = True
    ctx._run_boundary()
    current_dirty = False
    assert namespace["SWITCHED"] == [1, 10, 1]
    assert len(namespace["STORES"]["A"].listeners) == 1
    assert len(namespace["STORES"]["D"].listeners) == 1

    namespace = load_namespace()
    ctx = RenderContext()
    namespace["LOG"].clear()
    ctx.mount(lambda: namespace["panel_tuple_keys"]._pyrolyze_meta._func(ctx, dirtyof()))
    assert namespace["TUPLES"] == [3]
    namespace["notify"]("PAIR", ("E", "E"))
    assert ctx.debug_pending_boundaries() == (None,)
    ctx.run_pending_invalidations()
    assert namespace["TUPLES"] == [3, 4]
    assert len(namespace["STORES"]["D"].listeners) == 0
    assert len(namespace["STORES"]["E"].listeners) >= 2


def test_compiled_conditional_nested_store_value_expression_original_form() -> None:
    source = dedent("""
        from pyrolyze.api import pyrolyze, pyrolyze_slotted
        from tests.external_store_test_utils import StoreProbe

        SWITCHED = []
        LOG = []

        STORES = {
            "A": StoreProbe("A", "D", LOG),
            "D": StoreProbe("D", 1, LOG),
        }

        @pyrolyze_slotted
        def use_grip(key):
            return STORES[key].ref()

        @pyrolyze
        def panel_switch(flag: bool):
            k = use_grip("A")
            v = 10 if flag else use_grip(k)
            SWITCHED.append(v)
    """)

    namespace = load_transformed_namespace(
        source,
        module_name="tests.phase5a.compiled_conditional_nested_store_original_form",
        filename="/virtual/tests/phase5a/compiled_conditional_nested_store_original_form.py",
    )
    ctx = RenderContext()
    namespace["panel_switch"]._pyrolyze_meta._func(ctx, dirtyof(flag=True), False)
    assert namespace["SWITCHED"] == [1]


def test_compiled_store_returned_slot_callables_via_annotated_locals() -> None:
    source = dedent("""
        from pyrolyze.api import SlotCallable, pyrolyze, pyrolyze_slotted
        from tests.external_store_test_utils import StoreProbe

        LOG = []
        DIRECT = []
        NESTED = []
        COMBINED = []
        MIXED = []

        @pyrolyze_slotted
        def add_one(x: int) -> int:
            LOG.append(("add_one", x))
            return x + 1

        @pyrolyze_slotted
        def double(x: int) -> int:
            LOG.append(("double", x))
            return x * 2

        STORES = {
            "F": StoreProbe("F", add_one, LOG),
            "G": StoreProbe("G", double, LOG),
            "FKEY": StoreProbe("FKEY", "F", LOG),
            "A": StoreProbe("A", "D", LOG),
            "D": StoreProbe("D", 1, LOG),
            "X": StoreProbe("X", 2, LOG),
            "C": StoreProbe("C", 3, LOG),
        }

        def notify(key, value):
            STORES[key].notify(value)

        @pyrolyze_slotted
        def use_grip(key):
            LOG.append(("helper", key))
            return STORES[key].ref()

        @pyrolyze
        def panel_direct(x: int):
            f: SlotCallable[[int], int] = use_grip("F")
            v = f(x)
            DIRECT.append(v)

        @pyrolyze
        def panel_nested(x: int):
            fkey = use_grip("FKEY")
            f: SlotCallable[[int], int] = use_grip(fkey)
            v = f(x)
            NESTED.append(v)

        @pyrolyze
        def panel_combined(x: int, y: int):
            f: SlotCallable[[int], int] = use_grip("F")
            g: SlotCallable[[int], int] = use_grip("G")
            v = f(x) + g(y)
            COMBINED.append(v)

        @pyrolyze
        def panel_mixed(x: int):
            a = use_grip(use_grip("A"))
            f: SlotCallable[[int], int] = use_grip("F")
            v = a + f(use_grip("X")) + use_grip("C")
            MIXED.append(v)
    """)

    def load_namespace():
        return load_transformed_namespace(
            source,
            module_name="tests.phase5a.compiled_store_returned_slot_callables",
            filename="/virtual/tests/phase5a/compiled_store_returned_slot_callables.py",
        )

    namespace = load_namespace()
    ctx = RenderContext()
    current_x = 4
    current_dirty = True

    def render_direct() -> None:
        namespace["panel_direct"]._pyrolyze_meta._func(ctx, dirtyof(x=current_dirty), current_x)

    ctx.mount(render_direct)
    current_dirty = False
    assert namespace["DIRECT"] == [5]
    namespace["notify"]("F", namespace["double"])
    assert ctx.debug_pending_boundaries() == (None,)
    ctx.run_pending_invalidations()
    assert namespace["DIRECT"] == [5, 8]

    namespace = load_namespace()
    ctx = RenderContext()
    current_x = 4
    current_dirty = True

    def render_nested() -> None:
        namespace["panel_nested"]._pyrolyze_meta._func(ctx, dirtyof(x=current_dirty), current_x)

    ctx.mount(render_nested)
    current_dirty = False
    assert namespace["NESTED"] == [5]
    namespace["notify"]("FKEY", "G")
    assert ctx.debug_pending_boundaries() == (None,)
    ctx.run_pending_invalidations()
    assert namespace["NESTED"] == [5, 8]

    namespace = load_namespace()
    ctx = RenderContext()
    current_x = 2
    current_y = 3
    current_dirty = True

    def render_combined() -> None:
        namespace["panel_combined"]._pyrolyze_meta._func(
            ctx,
            dirtyof(x=current_dirty, y=current_dirty),
            current_x,
            current_y,
        )

    ctx.mount(render_combined)
    current_dirty = False
    assert namespace["COMBINED"] == [9]
    namespace["notify"]("F", namespace["add_one"])
    namespace["notify"]("G", namespace["add_one"])
    ctx.run_pending_invalidations()
    assert namespace["COMBINED"] == [9, 7]

    namespace = load_namespace()
    ctx = RenderContext()
    current_x = 10
    current_dirty = True

    def render_mixed() -> None:
        namespace["panel_mixed"]._pyrolyze_meta._func(ctx, dirtyof(x=current_dirty), current_x)

    ctx.mount(render_mixed)
    current_dirty = False
    assert namespace["MIXED"] == [7]
    namespace["notify"]("X", 4)
    assert ctx.debug_pending_boundaries() == (None,)
    ctx.run_pending_invalidations()
    assert namespace["MIXED"] == [7, 9]


def test_compiled_store_returned_componentrefs_via_annotated_locals_in_container_form() -> None:
    source = dedent("""
        from pyrolyze.api import ComponentRef, UIElement, call_native, pyrolyze, pyrolyze_slotted
        from tests.external_store_test_utils import StoreProbe

        LOG = []

        @pyrolyze
        def leaf() -> None:
            call_native(UIElement)(kind="leaf", props={})

        @pyrolyze
        def section_a(title: str) -> None:
            call_native(UIElement)(kind="section_a", props={"title": title})

        @pyrolyze
        def section_b(title: str) -> None:
            call_native(UIElement)(kind="section_b", props={"title": title})

        STORES = {
            "CONTAINER": StoreProbe("CONTAINER", section_a, LOG),
            "CKEY": StoreProbe("CKEY", "CA", LOG),
            "CA": StoreProbe("CA", section_a, LOG),
            "CB": StoreProbe("CB", section_b, LOG),
        }

        def notify(key, value):
            STORES[key].notify(value)

        @pyrolyze_slotted
        def use_grip(key):
            LOG.append(("helper", key))
            return STORES[key].ref()

        @pyrolyze
        def panel_direct(title: str):
            c: ComponentRef[[str]] = use_grip("CONTAINER")
            with c(title):
                leaf()

        @pyrolyze
        def panel_nested(title: str):
            ckey = use_grip("CKEY")
            c: ComponentRef[[str]] = use_grip(ckey)
            with c(title):
                leaf()
    """)

    namespace = load_transformed_namespace(
        source,
        module_name="tests.phase5a.compiled_store_returned_componentrefs",
        filename="/virtual/tests/phase5a/compiled_store_returned_componentrefs.py",
    )

    def top_kind(ctx: RenderContext) -> str:
        ui = ctx.debug_ui()
        assert len(ui) == 1
        return ui[0].kind

    ctx = RenderContext()
    current_title = "Hello"
    current_dirty = True

    def render_direct() -> None:
        namespace["panel_direct"]._pyrolyze_meta._func(ctx, dirtyof(title=current_dirty), current_title)

    ctx.mount(render_direct)
    current_dirty = False
    assert top_kind(ctx) == "section_a"
    namespace["notify"]("CONTAINER", namespace["section_b"])
    assert ctx.debug_pending_boundaries() == (None,)
    ctx.run_pending_invalidations()
    assert top_kind(ctx) == "section_b"

    ctx = RenderContext()
    current_title = "Hi"
    current_dirty = True

    def render_nested() -> None:
        namespace["panel_nested"]._pyrolyze_meta._func(ctx, dirtyof(title=current_dirty), current_title)

    ctx.mount(render_nested)
    current_dirty = False
    assert top_kind(ctx) == "section_a"
    namespace["notify"]("CKEY", "CB")
    assert ctx.debug_pending_boundaries() == (None,)
    ctx.run_pending_invalidations()
    assert top_kind(ctx) == "section_b"
