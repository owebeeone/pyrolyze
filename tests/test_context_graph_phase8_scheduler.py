from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pytest

from pyrolyze.api import UIElement
from pyrolyze.runtime.context import (
    ContextBase,
    DirtyStateContext,
    ExternalStoreRef,
    ModuleRegistry,
    RenderContext,
    SlotId,
    UseEffectAsyncRequest,
    dirtyof,
)


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.context_graph_phase8_scheduler")

_VALUE_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_BUTTON_SLOT = SlotId(_MODULE_ID, 2, line_no=11)
_HANDLER_SLOT = SlotId(_MODULE_ID, 3, line_no=12)
_ASYNC_SLOT = SlotId(_MODULE_ID, 4, line_no=20)


@dataclass(slots=True)
class _StoreProbe:
    value: str
    listeners: list[Callable[[], None]]

    def ref(self) -> ExternalStoreRef[str]:
        return ExternalStoreRef(
            identity="store",
            subscribe=self.subscribe,
            get=self.get,
        )

    def subscribe(self, listener: Callable[[], None]) -> Callable[[], None]:
        self.listeners.append(listener)

        def unsubscribe() -> None:
            self.listeners.remove(listener)

        return unsubscribe

    def get(self) -> str:
        return self.value

    def notify(self, value: str) -> None:
        self.value = value
        for listener in list(self.listeners):
            listener()


@dataclass(slots=True)
class _AsyncHandle:
    cancelled: bool = False

    def cancel(self) -> None:
        self.cancelled = True


def _pyr_button(ctx: ContextBase, label: str, *, on_press: object) -> None:
    ctx.call_native(
        UIElement,
        kind="button",
        props={"label": label, "on_press": on_press},
    )


def test_host_posting_dedupes_and_defers_rerun_until_posted_flush() -> None:
    ctx = RenderContext()
    posted: list[Callable[[], None]] = []
    log: list[tuple[str, str]] = []
    store = _StoreProbe("cold", [])

    def use_store() -> ExternalStoreRef[str]:
        return store.ref()

    def render(__pyr_dirty_state: DirtyStateContext) -> None:
        _ = __pyr_dirty_state
        with ctx.pass_scope():
            __pyr_value_dirty, value = ctx.call_plain(_VALUE_SLOT, use_store)
            log.append(("render", value))
            ctx.leaf_call(
                _BUTTON_SLOT,
                _pyr_button,
                "refresh",
                on_press=ctx.event_handler(
                    _HANDLER_SLOT,
                    dirty=False,
                    callback=lambda: (
                        store.notify("warm"),
                        store.notify("hot"),
                    ),
                ),
            )

    ctx.set_flush_poster(posted.append)
    ctx.mount(lambda: render(dirtyof()))
    first_ui = ctx.committed_ui()
    dispatch = first_ui[0].props["on_press"]
    assert callable(dispatch)

    log.clear()
    dispatch()

    assert log == []
    assert len(posted) == 1
    assert ctx.committed_ui() == first_ui

    posted.pop()()

    assert log == [("render", "hot")]
    assert posted == []


def test_deactivated_handler_raises_in_debug_and_noops_in_prod(monkeypatch: pytest.MonkeyPatch) -> None:
    ctx = RenderContext()

    def render(show: bool, __pyr_dirty_state: DirtyStateContext) -> Callable[..., None] | None:
        _ = __pyr_dirty_state
        with ctx.pass_scope():
            if show:
                return ctx.event_handler(
                    _HANDLER_SLOT,
                    dirty=True,
                    callback=lambda: None,
                )
        return None

    dispatch = render(True, dirtyof(show=True))
    assert dispatch is not None
    render(False, dirtyof(show=True))

    with pytest.raises(RuntimeError, match="inactive"):
        dispatch()

    monkeypatch.setenv("PYROLYZE_ENV", "prod")
    assert dispatch() is None


def test_committed_ui_exposes_non_debug_snapshot_api() -> None:
    ctx = RenderContext()

    with ctx.pass_scope():
        assert ctx.visit_slot_and_dirty(_BUTTON_SLOT) is True
        ctx.leaf_call(
            _BUTTON_SLOT,
            _pyr_button,
            "run",
            on_press=lambda: None,
        )

    committed = ctx.committed_ui()
    assert len(committed) == 1
    assert committed[0].kind == "button"
    assert committed[0].props["label"] == "run"
    assert callable(committed[0].props["on_press"])


def test_async_effect_completion_posts_invalidation_and_replacement_cancels_previous() -> None:
    ctx = RenderContext()
    posted: list[Callable[[], None]] = []
    starts: list[tuple[str, Callable[[], None], _AsyncHandle]] = []
    cleanups: list[str] = []
    renders: list[str] = []
    state = {"label": "alpha", "dirty": True}

    def register_async(label: str) -> UseEffectAsyncRequest:
        def start(on_complete: Callable[[], None]) -> _AsyncHandle:
            handle = _AsyncHandle()
            starts.append((label, on_complete, handle))
            return handle

        return UseEffectAsyncRequest(
            start=start,
            deps=(label,),
            cleanup=lambda: cleanups.append(label),
        )

    def render(label: str, __pyr_dirty_state: DirtyStateContext) -> None:
        _ = __pyr_dirty_state
        with ctx.pass_scope():
            renders.append(label)
            ctx.call_plain(_ASYNC_SLOT, register_async, label)

    def root_render() -> None:
        render(state["label"], dirtyof(label=state["dirty"]))
        state["dirty"] = False

    ctx.set_flush_poster(posted.append)
    ctx.mount(root_render)
    assert [entry[0] for entry in starts] == ["alpha"]

    state["label"] = "beta"
    state["dirty"] = True
    root_render()
    assert [entry[0] for entry in starts] == ["alpha", "beta"]
    assert starts[0][2].cancelled is True
    assert cleanups == ["alpha"]

    renders.clear()
    starts[-1][1]()

    assert renders == []
    assert len(posted) == 1

    posted.pop()()

    assert renders == ["beta"]
