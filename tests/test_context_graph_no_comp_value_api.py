from __future__ import annotations

from contextlib import contextmanager

import pytest

from pyrolyze.api import CallFromNonPyrolyzeContext, ComponentMetadata, pyrolyze_component_ref
from pyrolyze.runtime.context import DirtyStateContext, ModuleRegistry, RenderContext, SlotId, dirtyof


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.context_graph_no_comp_value_api")

_TITLE_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_PAIR_SLOT = SlotId(_MODULE_ID, 2, line_no=20)
_EVENT_SLOT = SlotId(_MODULE_ID, 3, line_no=30)
_EVENT_SLOT_2 = SlotId(_MODULE_ID, 4, line_no=31)
_EVENT_SLOT_3 = SlotId(_MODULE_ID, 5, line_no=32)
_COMPONENT_SLOT = SlotId(_MODULE_ID, 6, line_no=40)
_CHILD_STORE_SLOT = SlotId(_MODULE_ID, 7, line_no=41)
_INSTANCE_COMPONENT_SLOT = SlotId(_MODULE_ID, 8, line_no=50)
_CLASS_COMPONENT_SLOT = SlotId(_MODULE_ID, 9, line_no=51)
_STATIC_COMPONENT_SLOT = SlotId(_MODULE_ID, 10, line_no=52)


def test_dirty_state_context_supports_named_lookup() -> None:
    state = dirtyof(name=True, step=False)

    assert isinstance(state, DirtyStateContext)
    assert state.name is True
    assert state.step is False
    assert state.get("missing") is False


def test_call_plain_returns_dirty_and_plain_value_for_plain_inputs() -> None:
    ctx = RenderContext()
    observed: list[tuple[str, bool]] = []
    log: list[tuple[object, ...]] = []

    def format_title(name: str) -> str:
        log.append(("format_title", name))
        return f"Hello {name}"

    def render(name: str, __pyr_dirty_state: DirtyStateContext) -> None:
        with ctx.pass_scope():
            __pyr_title_dirty, title = ctx.call_plain(_TITLE_SLOT, format_title, name)
            observed.append((title, __pyr_title_dirty))

    render("Ada", dirtyof(name=True))
    render("Ada", dirtyof(name=False))
    render("Bea", dirtyof(name=True))

    assert observed == [
        ("Hello Ada", True),
        ("Hello Ada", False),
        ("Hello Bea", True),
    ]
    assert log == [
        ("format_title", "Ada"),
        ("format_title", "Bea"),
    ]


def test_call_plain_supports_tuple_shaped_dirty_projection() -> None:
    ctx = RenderContext()
    observed: list[tuple[tuple[bool, bool], tuple[str, str]]] = []
    log: list[tuple[object, ...]] = []

    def make_pair(label: str) -> tuple[str, str]:
        log.append(("make_pair", label))
        return (label.upper(), f"set:{label}")

    def render(label: str, __pyr_dirty_state: DirtyStateContext) -> None:
        with ctx.pass_scope():
            (__pyr_value_dirty, __pyr_setter_dirty), pair = ctx.call_plain(
                _PAIR_SLOT,
                make_pair,
                label,
                result_shape=("tuple", 2),
            )
            observed.append(((__pyr_value_dirty, __pyr_setter_dirty), pair))

    render("alpha", dirtyof(label=True))
    render("alpha", dirtyof(label=False))
    render("beta", dirtyof(label=True))

    assert observed == [
        ((True, True), ("ALPHA", "set:alpha")),
        ((False, False), ("ALPHA", "set:alpha")),
        ((True, True), ("BETA", "set:beta")),
    ]
    assert log == [
        ("make_pair", "alpha"),
        ("make_pair", "beta"),
    ]


def test_event_handler_commits_latest_callback_and_rolls_back_failed_pass() -> None:
    ctx = RenderContext()
    log: list[str] = []
    dispatches: list[object] = []

    def render(label: str, __pyr_dirty_state: DirtyStateContext, *, fail: bool = False) -> None:
        with ctx.pass_scope():
            dispatch = ctx.event_handler(
                _EVENT_SLOT,
                dirty=__pyr_dirty_state.label,
                callback=lambda: log.append(label),
            )
            dispatches.append(dispatch)
            if fail:
                raise RuntimeError("boom")

    render("alpha", dirtyof(label=True))
    first_dispatch = dispatches[-1]
    first_dispatch()
    assert log == ["alpha"]

    with pytest.raises(RuntimeError, match="boom"):
        render("beta", dirtyof(label=True), fail=True)

    second_dispatch = dispatches[-1]
    assert second_dispatch is first_dispatch
    first_dispatch()
    assert log == ["alpha", "alpha"]

    render("gamma", dirtyof(label=True))
    third_dispatch = dispatches[-1]
    assert third_dispatch is first_dispatch
    first_dispatch()
    assert log == ["alpha", "alpha", "gamma"]


def test_event_handler_supports_bound_instance_class_and_static_methods() -> None:
    ctx = RenderContext()
    log: list[str] = []

    class Recorder:
        class_log = log

        def __init__(self, label: str) -> None:
            self.label = label

        def instance_handler(self) -> None:
            self.class_log.append(f"instance:{self.label}")

        @classmethod
        def class_handler(cls) -> None:
            cls.class_log.append("class")

        @staticmethod
        def static_handler() -> None:
            log.append("static")

    rec1 = Recorder("one")
    rec2 = Recorder("two")

    dispatches: list[object] = []

    def render(recorder: Recorder, __pyr_dirty_state: DirtyStateContext) -> None:
        with ctx.pass_scope():
            dispatches.append(
                ctx.event_handler(
                    _EVENT_SLOT,
                    dirty=__pyr_dirty_state.recorder,
                    callback=recorder.instance_handler,
                )
            )
            dispatches.append(
                ctx.event_handler(
                    _EVENT_SLOT_2,
                    dirty=__pyr_dirty_state.recorder,
                    callback=Recorder.class_handler,
                )
            )
            dispatches.append(
                ctx.event_handler(
                    _EVENT_SLOT_3,
                    dirty=__pyr_dirty_state.recorder,
                    callback=recorder.static_handler,
                )
            )

    render(rec1, dirtyof(recorder=True))
    instance_dispatch, class_dispatch, static_dispatch = dispatches[-3:]
    instance_dispatch()
    class_dispatch()
    static_dispatch()

    assert log == ["instance:one", "class", "static"]

    render(rec2, dirtyof(recorder=True))
    next_instance_dispatch, next_class_dispatch, next_static_dispatch = dispatches[-3:]
    assert next_instance_dispatch is instance_dispatch
    assert next_class_dispatch is class_dispatch
    assert next_static_dispatch is static_dispatch

    instance_dispatch()
    class_dispatch()
    static_dispatch()

    assert log == [
        "instance:one",
        "class",
        "static",
        "instance:two",
        "class",
        "static",
    ]


def test_component_call_passes_dirty_state_and_uses_clean_parent_dirtiness_on_child_rerun() -> None:
    ctx = RenderContext()
    log: list[tuple[str, object]] = []
    listeners: list[callable] = []
    store_value = {"value": "cold"}

    def subscribe(listener):
        listeners.append(listener)

        def unsubscribe() -> None:
            listeners.remove(listener)

        return unsubscribe

    def get() -> str:
        return store_value["value"]

    def use_store() -> object:
        from pyrolyze.runtime.context import ExternalStoreRef

        return ExternalStoreRef(identity="weather", subscribe=subscribe, get=get)

    def __pyr_child(child_ctx: RenderContext, __pyr_dirty_state: DirtyStateContext, name: str) -> None:
        with child_ctx.pass_scope():
            log.append(("render", name))
            log.append(("name_dirty", __pyr_dirty_state.name))
            __pyr_store_dirty, value = child_ctx.call_plain(_CHILD_STORE_SLOT, use_store)
            log.append(("store", value))
            log.append(("store_dirty", __pyr_store_dirty))

    @pyrolyze_component_ref(ComponentMetadata("child", __pyr_child))
    def child(name: str) -> None:
        raise CallFromNonPyrolyzeContext("child")

    def render(name: str, __pyr_dirty_state: DirtyStateContext) -> None:
        with ctx.pass_scope():
            ctx.component_call(
                _COMPONENT_SLOT,
                child,
                name,
                dirty_state=dirtyof(name=__pyr_dirty_state.name),
            )

    render("Ada", dirtyof(name=True))
    assert log == [
        ("render", "Ada"),
        ("name_dirty", True),
        ("store", "cold"),
        ("store_dirty", True),
    ]

    log.clear()
    store_value["value"] = "warm"
    listeners[0]()
    ctx.run_pending_invalidations()

    assert log == [
        ("render", "Ada"),
        ("name_dirty", False),
        ("store", "warm"),
        ("store_dirty", True),
    ]


def test_component_call_supports_bound_instance_class_and_static_component_refs() -> None:
    ctx = RenderContext()
    log: list[tuple[str, object]] = []

    class Panel:
        def __init__(self, prefix: str) -> None:
            self.prefix = prefix

        def __pyr_instance(self, child_ctx: RenderContext, __pyr_dirty_state: DirtyStateContext, label: str) -> None:
            with child_ctx.pass_scope():
                log.append(("instance", self.prefix, label, __pyr_dirty_state.label))

        @classmethod
        def __pyr_class(cls, child_ctx: RenderContext, __pyr_dirty_state: DirtyStateContext, label: str) -> None:
            with child_ctx.pass_scope():
                log.append(("class", cls.__name__, label, __pyr_dirty_state.label))

        @staticmethod
        def __pyr_static(child_ctx: RenderContext, __pyr_dirty_state: DirtyStateContext, label: str) -> None:
            with child_ctx.pass_scope():
                log.append(("static", label, __pyr_dirty_state.label))

        @pyrolyze_component_ref(ComponentMetadata("instance_panel", __pyr_instance))
        def instance_panel(self, label: str) -> None:
            raise CallFromNonPyrolyzeContext("instance_panel")

        @classmethod
        @pyrolyze_component_ref(ComponentMetadata("class_panel", __pyr_class))
        def class_panel(cls, label: str) -> None:
            raise CallFromNonPyrolyzeContext("class_panel")

        @staticmethod
        @pyrolyze_component_ref(ComponentMetadata("static_panel", __pyr_static))
        def static_panel(label: str) -> None:
            raise CallFromNonPyrolyzeContext("static_panel")

    panel = Panel("P")

    def render(label: str, __pyr_dirty_state: DirtyStateContext) -> None:
        with ctx.pass_scope():
            ctx.component_call(
                _INSTANCE_COMPONENT_SLOT,
                panel.instance_panel,
                label,
                dirty_state=dirtyof(label=__pyr_dirty_state.label),
            )
            ctx.component_call(
                _CLASS_COMPONENT_SLOT,
                Panel.class_panel,
                label,
                dirty_state=dirtyof(label=__pyr_dirty_state.label),
            )
            ctx.component_call(
                _STATIC_COMPONENT_SLOT,
                Panel.static_panel,
                label,
                dirty_state=dirtyof(label=__pyr_dirty_state.label),
            )

    render("alpha", dirtyof(label=True))
    render("alpha", dirtyof(label=False))
    render("beta", dirtyof(label=True))

    assert log == [
        ("instance", "P", "alpha", True),
        ("class", "Panel", "alpha", True),
        ("static", "alpha", True),
        ("instance", "P", "alpha", False),
        ("class", "Panel", "alpha", False),
        ("static", "alpha", False),
        ("instance", "P", "beta", True),
        ("class", "Panel", "beta", True),
        ("static", "beta", True),
    ]
