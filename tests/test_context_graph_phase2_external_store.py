from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime.context import (
    ExternalStoreBinding,
    ExternalStoreRef,
    SlotRuntimeContext,
    SlotValueBinding,
    RenderContext,
    dirtyof,
)
from tests.slot_expr_test_utils import ObservedCompiledContext


T = TypeVar("T")


def _compiled_reader(
    source: str,
    globals_dict: dict[str, Any],
    observed: list,
    *,
    binding_identity: bool = False,
):
    namespace = load_transformed_namespace(
        "from pyrolyze.api import pyrolyze, slotted\n" + source,
        module_name="tests.phase2_external_store.compiled_reader",
        globals_dict=globals_dict,
    )
    body = namespace["reader"]._pyrolyze_meta._func

    def render(ctx, state, *args):
        def observe(slot_id, call_slot, value, dirty):
            if binding_identity:
                observed.append((value, id(_binding_for(ctx)), dirty))
            else:
                observed.append((value, dirty))

        body(ObservedCompiledContext(ctx, observe), state, *args)

    return render


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

    return _compiled_reader(
        "@pyrolyze\ndef reader(grip_name):\n    value = slotted(use_grip, grip_name)\n",
        {"use_grip": use_grip}, observed,
    ), observed


def _make_switching_helper_program(log: list[tuple[object, ...]]):
    observed: list[tuple[str, bool]] = []

    return _compiled_reader(
        "@pyrolyze\ndef reader(helper, grip_name):\n    value = slotted(helper, grip_name)\n",
        {}, observed,
    ), observed


def _binding_for(ctx: RenderContext):
    bindings = []
    for slot in ctx._slots_by_id.values():
        manager = getattr(slot, "call_site_context_manager", None)
        if manager is not None:
            contexts = manager._current or manager._staged
            for context in contexts.values():
                if context.binding is not None:
                    bindings.append(getattr(context.binding, "binding", context.binding))
    assert len(bindings) == 1
    return bindings[0]


def _make_conditional_program(
    log: list[tuple[object, ...]],
    store: _StoreProbe[str],
):
    observed: list[tuple[str, bool]] = []

    def use_grip(grip_name: str) -> ExternalStoreRef[str]:
        log.append(("helper", grip_name))
        return store.ref()

    return _compiled_reader(
        "@pyrolyze\ndef reader(show, grip_name):\n"
        "    if show:\n        value = slotted(use_grip, grip_name)\n",
        {"use_grip": use_grip}, observed,
    ), observed


def test_external_store_notification_refreshes_via_get_without_helper_rerun() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    store = _StoreProbe(name="weather", initial_value="sunny", log=log)
    pyr_reader, observed = _make_external_reader_program(log, lambda _: store)

    pyr_reader(ctx, dirtyof(grip_name=True), "weather")

    assert observed == [("sunny", True)]
    assert log == [
        ("helper", "weather"),
        ("subscribe", "weather"),
        ("get", "weather", "sunny"),
    ]
    assert store.active_listener_count == 1
    assert isinstance(_binding_for(ctx), ExternalStoreBinding)

    pyr_reader(ctx, dirtyof(grip_name=False), "weather")

    assert observed == [("sunny", True), ("sunny", False)]
    assert log == [
        ("helper", "weather"),
        ("subscribe", "weather"),
        ("get", "weather", "sunny"),
    ]

    store.notify("rain")
    pyr_reader(ctx, dirtyof(grip_name=False), "weather")

    assert observed == [("sunny", True), ("sunny", False), ("rain", True)]
    assert log == [
        ("helper", "weather"),
        ("subscribe", "weather"),
        ("get", "weather", "sunny"),
        ("get", "weather", "rain"),
    ]

    pyr_reader(ctx, dirtyof(grip_name=False), "weather")

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

    pyr_reader(ctx, dirtyof(grip_name=True), "alpha")
    log.clear()

    pyr_reader(ctx, dirtyof(grip_name=True), "beta")

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

    pyr_reader(ctx, dirtyof(helper=True, grip_name=True), external_helper, "weather")
    assert store.active_listener_count == 1
    assert isinstance(_binding_for(ctx), ExternalStoreBinding)
    log.clear()

    pyr_reader(ctx, dirtyof(helper=True, grip_name=False), plain_helper, "weather")

    assert observed == [("sunny", True), ("plain:weather", True)]
    assert log == [
        ("plain_helper", "weather"),
        ("unsubscribe", "weather"),
    ]
    assert store.active_listener_count == 0
    assert isinstance(_binding_for(ctx), SlotValueBinding)


def test_slot_call_runtime_context_injects_slot_local_storage() -> None:
    ctx = RenderContext()
    observed: list[tuple[str, int, bool]] = []

    def helper(label: str, runtime: SlotRuntimeContext) -> str:
        sequence = runtime.get_or_init_local("sequence", lambda: 0)
        runtime.set_local("sequence", sequence + 1)
        return f"{label}:{sequence}"

    _pyr_reader = _compiled_reader(
        "@pyrolyze\ndef reader(label):\n    value = slotted(helper, label)\n",
        {"helper": helper}, observed, binding_identity=True,
    )

    _pyr_reader(ctx, dirtyof(label=True), "alpha")
    _pyr_reader(ctx, dirtyof(label=False), "alpha")
    _pyr_reader(ctx, dirtyof(label=True), "beta")

    assert observed == [
        ("alpha:0", observed[0][1], True),
        ("alpha:0", observed[0][1], False),
        ("beta:1", observed[0][1], True),
    ]
    assert isinstance(_binding_for(ctx), SlotValueBinding)


def test_plain_result_uses_plain_value_binding() -> None:
    ctx = RenderContext()
    observed: list[tuple[str, bool]] = []
    log: list[tuple[object, ...]] = []

    def plain_helper(name: str) -> str:
        log.append(("plain_helper", name))
        return f"plain:{name}"

    compiled_reader = _compiled_reader(
        "@pyrolyze\ndef reader(name):\n    value = slotted(plain_helper, name)\n",
        {"plain_helper": plain_helper}, observed,
    )

    def pyr_reader(name: str, state) -> None:
        compiled_reader(ctx, state, name)

    pyr_reader("weather", dirtyof(name=True))

    assert observed == [("plain:weather", True)]
    assert log == [("plain_helper", "weather")]
    assert isinstance(_binding_for(ctx), SlotValueBinding)

    pyr_reader("weather", dirtyof(name=False))

    assert observed == [("plain:weather", True), ("plain:weather", False)]
    assert log == [("plain_helper", "weather")]
    assert isinstance(_binding_for(ctx), SlotValueBinding)


def test_deactivating_an_external_slot_call_unsubscribes_the_store() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    store = _StoreProbe(name="weather", initial_value="sunny", log=log)
    pyr_conditional, observed = _make_conditional_program(log, store)

    pyr_conditional(
        ctx,
        dirtyof(show=True, grip_name=True),
        True,
        "weather",
    )

    assert observed == [("sunny", True)]
    assert store.active_listener_count == 1
    store_slots = tuple(ctx._slots_by_id)

    pyr_conditional(
        ctx,
        dirtyof(show=True, grip_name=False),
        False,
        "weather",
    )

    assert store.active_listener_count == 0
    assert all(not ctx.debug_is_active(slot_id) for slot_id in store_slots)
    assert log[-1] == ("unsubscribe", "weather")


def test_slot_call_accepts_builtin_function_without_attribute_cache_support() -> None:
    ctx = RenderContext()
    observed: list[tuple[int, bool]] = []

    _pyr_reader = _compiled_reader(
        "@pyrolyze\ndef reader():\n    value = slotted(len, [1, 2, 3])\n",
        {}, observed,
    )

    _pyr_reader(ctx, dirtyof())
    _pyr_reader(ctx, dirtyof())

    assert observed == [
        (3, True),
        (3, False),
    ]


def test_slot_call_tolerates_callable_with_invalid_signature_metadata() -> None:
    ctx = RenderContext()
    observed: list[tuple[int, bool]] = []

    class _NoAttrBadSignaturePlain:
        __slots__ = ()
        __signature__ = "invalid"

        def __call__(self, values: list[int]) -> int:
            return len(values)

    helper = _NoAttrBadSignaturePlain()

    _pyr_reader = _compiled_reader(
        "@pyrolyze\ndef reader():\n    value = slotted(helper, [1, 2, 3])\n",
        {"helper": helper}, observed,
    )

    _pyr_reader(ctx, dirtyof())
    _pyr_reader(ctx, dirtyof())

    assert observed == [
        (3, True),
        (3, False),
    ]
