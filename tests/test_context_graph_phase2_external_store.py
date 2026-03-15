from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar, cast

from pyrolyze.runtime.context import (
    CompValue,
    ExternalStoreRef,
    ModuleRegistry,
    RenderContext,
    SlotId,
)


T = TypeVar("T")

module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.context_graph_phase2_external_store")

_STORE_SLOT = SlotId(_MODULE_ID, 1, line_no=10)


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
        return ExternalStoreRef(
            identity=self.identity,
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

    def get(self) -> T:
        self.log.append(("get", self.name, self._value))
        return self._value

    def notify(self, value: T) -> None:
        self._value = value
        for listener in list(self._listeners):
            listener()

    @property
    def active_listener_count(self) -> int:
        return len(self._listeners)


def _make_external_reader_program(
    log: list[tuple[object, ...]],
    resolve_store: Callable[[str], _StoreProbe[str]],
):
    observed: list[tuple[str, bool]] = []

    def use_grip(grip_name: str) -> ExternalStoreRef[str]:
        log.append(("helper", grip_name))
        return resolve_store(grip_name).ref()

    def _pyr_reader(ctx: RenderContext, grip_name: CompValue[str]) -> None:
        with ctx.pass_scope():
            value = ctx.call_plain(
                _STORE_SLOT,
                ctx.literal(use_grip),
                grip_name,
            )
            observed.append((value.value, value.dirty))

    return _pyr_reader, observed


def _make_switching_helper_program(log: list[tuple[object, ...]]):
    observed: list[tuple[str, bool]] = []

    def _pyr_reader(
        ctx: RenderContext,
        helper: CompValue[Callable[[str], object]],
        grip_name: CompValue[str],
    ) -> None:
        with ctx.pass_scope():
            value = ctx.call_plain(
                _STORE_SLOT,
                cast(CompValue[Callable[..., str]], helper),
                grip_name,
            )
            observed.append((cast(str, value.value), value.dirty))

    return _pyr_reader, observed


def _make_conditional_program(
    log: list[tuple[object, ...]],
    store: _StoreProbe[str],
):
    observed: list[tuple[str, bool]] = []

    def use_grip(grip_name: str) -> ExternalStoreRef[str]:
        log.append(("helper", grip_name))
        return store.ref()

    def _pyr_conditional(
        ctx: RenderContext,
        show: CompValue[bool],
        grip_name: CompValue[str],
    ) -> None:
        with ctx.pass_scope():
            if show.value:
                value = ctx.call_plain(
                    _STORE_SLOT,
                    ctx.literal(use_grip),
                    grip_name,
                )
                observed.append((value.value, value.dirty))

    return _pyr_conditional, observed


def test_external_store_notification_refreshes_via_get_without_helper_rerun() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    store = _StoreProbe(name="weather", initial_value="sunny", log=log)
    pyr_reader, observed = _make_external_reader_program(log, lambda _: store)

    pyr_reader(ctx, CompValue("weather", dirty=True))

    assert observed == [("sunny", True)]
    assert log == [
        ("helper", "weather"),
        ("subscribe", "weather"),
        ("get", "weather", "sunny"),
    ]
    assert store.active_listener_count == 1

    pyr_reader(ctx, CompValue("weather", dirty=False))

    assert observed == [("sunny", True), ("sunny", False)]
    assert log == [
        ("helper", "weather"),
        ("subscribe", "weather"),
        ("get", "weather", "sunny"),
    ]

    store.notify("rain")
    pyr_reader(ctx, CompValue("weather", dirty=False))

    assert observed == [("sunny", True), ("sunny", False), ("rain", True)]
    assert log == [
        ("helper", "weather"),
        ("subscribe", "weather"),
        ("get", "weather", "sunny"),
        ("get", "weather", "rain"),
    ]

    pyr_reader(ctx, CompValue("weather", dirty=False))

    assert observed == [
        ("sunny", True),
        ("sunny", False),
        ("rain", True),
        ("rain", False),
    ]
    assert log == [
        ("helper", "weather"),
        ("subscribe", "weather"),
        ("get", "weather", "sunny"),
        ("get", "weather", "rain"),
    ]


def test_rebinding_external_store_subscribes_new_before_unsubscribing_old() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    alpha = _StoreProbe(name="alpha", initial_value="A", log=log)
    beta = _StoreProbe(name="beta", initial_value="B", log=log)
    stores = {"alpha": alpha, "beta": beta}
    pyr_reader, observed = _make_external_reader_program(log, stores.__getitem__)

    pyr_reader(ctx, CompValue("alpha", dirty=True))
    log.clear()

    pyr_reader(ctx, CompValue("beta", dirty=True))

    assert observed == [("A", True), ("B", True)]
    assert log == [
        ("helper", "beta"),
        ("subscribe", "beta"),
        ("unsubscribe", "alpha"),
        ("get", "beta", "B"),
    ]
    assert alpha.active_listener_count == 0
    assert beta.active_listener_count == 1


def test_switching_from_external_helper_to_plain_helper_unsubscribes_old_binding() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    store = _StoreProbe(name="weather", initial_value="sunny", log=log)
    pyr_reader, observed = _make_switching_helper_program(log)

    def external_helper(grip_name: str) -> ExternalStoreRef[str]:
        log.append(("external_helper", grip_name))
        return store.ref()

    def plain_helper(grip_name: str) -> str:
        log.append(("plain_helper", grip_name))
        return f"plain:{grip_name}"

    pyr_reader(
        ctx,
        CompValue(external_helper, dirty=True),
        CompValue("weather", dirty=True),
    )
    assert store.active_listener_count == 1
    log.clear()

    pyr_reader(
        ctx,
        CompValue(plain_helper, dirty=True),
        CompValue("weather", dirty=False),
    )

    assert observed == [("sunny", True), ("plain:weather", True)]
    assert log == [
        ("plain_helper", "weather"),
        ("unsubscribe", "weather"),
    ]
    assert store.active_listener_count == 0

    store.notify("storm")
    pyr_reader(
        ctx,
        CompValue(plain_helper, dirty=False),
        CompValue("weather", dirty=False),
    )

    assert observed == [("sunny", True), ("plain:weather", True), ("plain:weather", False)]
    assert log == [
        ("plain_helper", "weather"),
        ("unsubscribe", "weather"),
    ]


def test_deactivating_an_external_plain_call_unsubscribes_the_store() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    store = _StoreProbe(name="weather", initial_value="sunny", log=log)
    pyr_conditional, observed = _make_conditional_program(log, store)

    pyr_conditional(
        ctx,
        CompValue(True, dirty=True),
        CompValue("weather", dirty=True),
    )

    assert observed == [("sunny", True)]
    assert store.active_listener_count == 1

    pyr_conditional(
        ctx,
        CompValue(False, dirty=True),
        CompValue("weather", dirty=False),
    )

    assert store.active_listener_count == 0
    assert ctx.debug_is_active(_STORE_SLOT) is False
    assert log[-1] == ("unsubscribe", "weather")
