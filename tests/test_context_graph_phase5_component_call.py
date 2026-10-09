from __future__ import annotations

from dataclasses import replace
from typing import Callable

import pytest

from pyrolyze.api import (
    CallFromNonPyrolyzeContext,
    ComponentRef,
    pyrolyze_component_ref,
)
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime.context import DirtyStateContext, ModuleRegistry, RenderContext, SlotId, dirtyof
from pyrolyze.runtime.context_lifecycle import RenderContext as LifecycleRenderContext


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.context_graph_phase5_component_call")

_DIRECT_COMPONENT_SLOT = SlotId(_MODULE_ID, 8, line_no=40)
_DIRECT_CONTAINER_SLOT = SlotId(_MODULE_ID, 9, line_no=41)


def _observe_dirty(
    component: ComponentRef[[str]],
    observe: Callable[[str, DirtyStateContext], None],
) -> ComponentRef[[str]]:
    """Observe runtime inputs without reproducing the generated component body."""
    metadata = component._pyrolyze_meta

    def run(ctx: RenderContext, state: DirtyStateContext, value: str) -> None:
        observe(value, state)
        metadata._func(ctx, state, value)

    def observed(value: str) -> None:
        raise CallFromNonPyrolyzeContext(metadata.name)

    return pyrolyze_component_ref(replace(metadata, _func=run))(observed)


def _make_component_program(log: list[tuple[object, ...]]) -> dict[str, Callable[..., None]]:
    namespace = load_transformed_namespace(
        '''
from pyrolyze.api import UIElement, call_native, pyrolyze

@pyrolyze
def badge(text, *, tone):
    LOG.append(("badge", text, tone))
    call_native(UIElement)(kind="badge", props={"text": text, "tone": tone})

@pyrolyze
def neutral_badge(text):
    badge(text, tone="neutral")

@pyrolyze
def info_badge(text):
    badge(text, tone="info")
''',
        module_name="tests.context_graph_phase5_component_call.forwarding",
        globals_dict={"LOG": log},
    )

    def direct_component(
        ctx: RenderContext,
        state: DirtyStateContext,
        component: ComponentRef[[str]],
        text: str,
        refresh: int,
    ) -> None:
        # Force dispatch independently of the forwarded argument's dirty flag.
        with ctx.pass_scope():
            ctx.component_call(
                _DIRECT_COMPONENT_SLOT, component, text, dirty_state=dirtyof(text=state.text)
            )

    return {
        "direct_component": direct_component,
        "neutral_badge": _observe_dirty(
            namespace["neutral_badge"],
            lambda text, state: log.append(("render", "neutral", text, state.text)),
        ),
        "info_badge": _observe_dirty(
            namespace["info_badge"],
            lambda text, state: log.append(("render", "info", text, state.text)),
        ),
    }


def _make_compiled_badge_panel(log: list[tuple[object, ...]]) -> Callable[..., None]:
    namespace = load_transformed_namespace(
        '''
from pyrolyze.api import ComponentRef, UIElement, call_native, component, pyrolyze, slotted
from pyrolyze.runtime.context import ContextBase

def section(ctx: ContextBase, title, *, accent):
    LOG.append(("section", title, accent))
    ctx.call_native(UIElement, kind="section", props={"title": title, "accent": accent})

@pyrolyze
def neutral_badge(text):
    LOG.append(("render", "neutral", text))
    call_native(UIElement)(kind="badge", props={"text": text, "tone": "neutral"})

@pyrolyze
def info_badge(text):
    LOG.append(("render", "info", text))
    call_native(UIElement)(kind="badge", props={"text": text, "tone": "info"})

def pick_badge(kind: str) -> ComponentRef[[str]]:
    return info_badge if kind == "info" else neutral_badge

@pyrolyze
def badge_panel(kind, text):
    chosen = slotted(pick_badge, kind)
    fallback = slotted(pick_badge, "neutral")
    with component(section, "Badges", accent="slate"):
        component(chosen, text)
        component(fallback, "fallback")
''',
        module_name="tests.context_graph_phase5_component_call.compiled",
        globals_dict={"LOG": log},
    )
    return namespace["badge_panel"]._pyrolyze_meta._func


def test_component_call_mounts_child_component_from_helper_returned_component_ref() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    render = _make_compiled_badge_panel(log)

    render(
        ctx,
        dirtyof(kind=True, text=True),
        "info",
        "Hello",
    )

    assert log == [
        ("section", "Badges", "slate"),
        ("render", "info", "Hello"),
        ("render", "neutral", "fallback"),
    ]
    published = ctx.committed_ui()[0]
    assert [(child.props["text"], child.props["tone"]) for child in published.children] == [
        ("Hello", "info"), ("fallback", "neutral"),
    ]

    render(
        ctx,
        dirtyof(kind=False, text=False),
        "info",
        "Hello",
    )

    assert log == [
        ("section", "Badges", "slate"),
        ("render", "info", "Hello"),
        ("render", "neutral", "fallback"),
    ]
    assert ctx.committed_ui()[0] is published


def test_component_call_rerenders_existing_child_context_when_identity_is_stable() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    program = _make_component_program(log)

    program["direct_component"](
        ctx,
        dirtyof(component=True, text=True, refresh=True),
        program["neutral_badge"],
        "Hello",
        1,
    )
    log.clear()

    program["direct_component"](
        ctx,
        dirtyof(component=False, text=False, refresh=True),
        program["neutral_badge"],
        "Hello",
        1,
    )

    assert log == [
        ("render", "neutral", "Hello", False),
    ]


def test_component_call_replaces_child_context_when_component_identity_changes() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    program = _make_component_program(log)

    program["direct_component"](
        ctx,
        dirtyof(component=True, text=True, refresh=True),
        program["neutral_badge"],
        "Hello",
        1,
    )
    log.clear()

    program["direct_component"](
        ctx,
        dirtyof(component=True, text=False, refresh=True),
        program["info_badge"],
        "Hello",
        2,
    )

    assert log == [
        ("render", "info", "Hello", False),
        ("badge", "Hello", "info"),
    ]

    log.clear()
    program["direct_component"](
        ctx,
        dirtyof(component=True, text=False, refresh=True),
        program["neutral_badge"],
        "Hello",
        3,
    )

    assert log == [
        ("render", "neutral", "Hello", False),
        ("badge", "Hello", "neutral"),
    ]


def test_component_call_rejects_undecorated_callable() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    program = _make_component_program(log)

    def not_a_component(text: str) -> None:
        log.append(("plain", text))

    with pytest.raises(TypeError, match="ComponentRef"):
        program["direct_component"](
            ctx,
            dirtyof(component=True, text=True, refresh=True),
            not_a_component,
            "Hello",
            1,
        )


def _make_container_component_program(log: list[tuple[object, ...]]) -> dict[str, Callable[..., None]]:
    namespace = load_transformed_namespace(
        '''
from pyrolyze.api import PyrolyzeHandler, UIElement, call_native, pyrolyze

@pyrolyze
def neutral_box(title):
    call_native(UIElement)(kind="box", props={"title": title, "tone": "neutral"})

@pyrolyze
def info_box(title):
    call_native(UIElement)(kind="box", props={"title": title, "tone": "info"})

def button_element(label, *, on_press: PyrolyzeHandler[[], None]):
    return UIElement(kind="button", props={"label": label, "on_press": on_press})

@pyrolyze
def button_box(label):
    call_native(button_element)(label, on_press=lambda: LOG.append(("press", label)))
''',
        module_name="tests.context_graph_phase5_component_call.container_forwarding",
        globals_dict={"LOG": log},
    )

    def render_container(
        ctx: RenderContext,
        state: DirtyStateContext,
        component: ComponentRef[[str]],
        title: str,
        refresh: int,
    ) -> None:
        with ctx.pass_scope():
            with ctx.container_call(
                _DIRECT_CONTAINER_SLOT, component, title, dirty_state=dirtyof(title=state.title)
            ):
                log.append(("body", title))

    return {
        "render_container": render_container,
        "neutral_box": _observe_dirty(
            namespace["neutral_box"],
            lambda title, state: log.append(("render-container", "neutral", title, state.title)),
        ),
        "info_box": _observe_dirty(
            namespace["info_box"],
            lambda title, state: log.append(("render-container", "info", title, state.title)),
        ),
        "button_box": namespace["button_box"],
    }


def test_container_component_ref_rerenders_with_stable_identity() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    program = _make_container_component_program(log)

    program["render_container"](
        ctx,
        dirtyof(component=True, title=True, refresh=True),
        program["neutral_box"],
        "Hello",
        1,
    )
    log.clear()

    program["render_container"](
        ctx,
        dirtyof(component=False, title=False, refresh=True),
        program["neutral_box"],
        "Hello",
        2,
    )

    assert log == [
        ("render-container", "neutral", "Hello", False),
        ("body", "Hello"),
    ]


def test_container_component_ref_replaces_runtime_when_identity_changes() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    program = _make_container_component_program(log)

    program["render_container"](
        ctx,
        dirtyof(component=True, title=True, refresh=True),
        program["neutral_box"],
        "Hello",
        1,
    )
    log.clear()

    program["render_container"](
        ctx,
        dirtyof(component=True, title=False, refresh=True),
        program["info_box"],
        "Hello",
        2,
    )

    assert log == [
        ("render-container", "info", "Hello", False),
        ("body", "Hello"),
    ]


def test_container_component_ref_rolls_back_failed_pass() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []

    namespace = load_transformed_namespace(
        '''
from pyrolyze.api import UIElement, call_native, pyrolyze

@pyrolyze
def ok_box(title):
    call_native(UIElement)(kind="box", props={"title": title})

@pyrolyze
def fail_box(title):
    call_native(UIElement)(kind="box", props={"title": "bad"})
    raise RuntimeError("boom")
''',
        module_name="tests.context_graph_phase5_component_call.rollback",
    )
    ok_box = namespace["ok_box"]
    fail_box = _observe_dirty(
        namespace["fail_box"],
        lambda title, state: log.append(("fail", state.title)),
    )

    def render(component: ComponentRef[[str]], title: str, state: DirtyStateContext) -> None:
        with ctx.pass_scope():
            with ctx.container_call(
                _DIRECT_CONTAINER_SLOT,
                component,
                title,
                dirty_state=dirtyof(title=state.title),
            ):
                pass

    render(ok_box, "good", dirtyof(component=True, title=True))
    committed = ctx.committed_ui()

    with pytest.raises(RuntimeError, match="boom"):
        render(fail_box, "bad", dirtyof(component=True, title=True))

    assert ctx.committed_ui() == committed
    assert ctx.committed_ui()[0] is committed[0]
    assert log == [("fail", True)]
    render(ok_box, "retry", dirtyof(component=True, title=True))
    assert ctx.committed_ui()[0].props["title"] == "retry"


def test_container_component_ref_retains_event_handler_callback_identity() -> None:
    ctx = RenderContext()
    log: list[tuple[object, ...]] = []
    program = _make_container_component_program(log)

    program["render_container"](
        ctx,
        dirtyof(component=True, title=True, refresh=True),
        program["button_box"],
        "Alpha",
        1,
    )
    (button_node,) = ctx.committed_ui()
    dispatch = button_node.props["on_press"]
    assert callable(dispatch)

    dispatch()
    assert log == [("body", "Alpha"), ("press", "Alpha")]

    log.clear()
    program["render_container"](
        ctx,
        dirtyof(component=False, title=True, refresh=True),
        program["button_box"],
        "Beta",
        2,
    )
    (updated_button_node,) = ctx.committed_ui()
    updated_dispatch = updated_button_node.props["on_press"]

    assert updated_dispatch is dispatch
    dispatch()
    assert log == [("body", "Beta"), ("press", "Beta")]


def test_compiled_native_handler_update_rolls_back_with_outer_render() -> None:
    ctx = LifecycleRenderContext()
    log: list[tuple[object, ...]] = []
    program = _make_container_component_program(log)
    program["render_container"](
        ctx, dirtyof(component=True, title=True, refresh=True),
        program["button_box"], "Beta", 1,
    )
    updated_button_node = ctx.committed_ui()[0]
    dispatch = updated_button_node.props["on_press"]
    log.clear()
    with pytest.raises(RuntimeError, match="abort callback update"):
        with ctx.pass_scope():
            program["render_container"](
                ctx, dirtyof(component=False, title=True, refresh=True),
                program["button_box"], "Gamma", 3,
            )
            raise RuntimeError("abort callback update")
    dispatch()
    assert log == [("body", "Gamma"), ("press", "Beta")]
    assert ctx.committed_ui()[0] is updated_button_node
