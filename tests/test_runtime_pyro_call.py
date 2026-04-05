from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass

from pyrolyze.api import (
    MountDirective,
    UIElement,
    component,
    default,
    mount,
    pyrolyze_slotted,
    slotted,
)
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import (
    ContextBase,
    ModuleRegistry,
    PyrolyzeComponentWrap,
    PyrolyzeSlottedWrap,
    RenderContext,
    RuntimeSiteMetadata,
    SlotId,
    SlotIdPath,
    dirtyof,
)
from pyrolyze.visitor import capture_context_graph
from tests.slot_expr_test_utils import eval_single_slot_expr


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.runtime_pyro_call")
_COMPONENT_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_COMPONENT_SLOT_2 = SlotId(_MODULE_ID, 2, line_no=11)
_PLAIN_CONTAINER_SLOT = SlotId(_MODULE_ID, 3, line_no=12)
_NATIVE_CONTAINER_SLOT = SlotId(_MODULE_ID, 4, line_no=13)
_PYRO_CONTAINER_SLOT = SlotId(_MODULE_ID, 5, line_no=14)
_MOUNT_CONTAINER_SLOT = SlotId(_MODULE_ID, 6, line_no=15)
_SLOTTED_SLOT = SlotId(_MODULE_ID, 7, line_no=16)


@dataclass(frozen=True, slots=True)
class _TaggedComponentCall(PyrolyzeComponentWrap):
    tag: str

    def site_metadata(self, *, slot_path: SlotIdPath) -> tuple[RuntimeSiteMetadata[str], ...]:
        return (
            RuntimeSiteMetadata(key="tag", value=self.tag),
            RuntimeSiteMetadata(key="depth", value=str(len(slot_path.items))),
        )


@dataclass(frozen=True, slots=True)
class _TaggedSlottedCall(PyrolyzeSlottedWrap):
    tag: str

    def site_metadata(self, *, slot_path: SlotIdPath) -> tuple[RuntimeSiteMetadata[str], ...]:
        return (
            RuntimeSiteMetadata(key="tag", value=self.tag),
            RuntimeSiteMetadata(key="depth", value=str(len(slot_path.items))),
        )


def test_pyrolyze_wrap_metadata_surface_remains_available() -> None:
    def target(*args: object, **kwargs: object) -> tuple[tuple[object, ...], dict[str, object]]:
        return args, dict(kwargs)

    component_call = _TaggedComponentCall(func=target, tag="component-site")
    slotted_call = _TaggedSlottedCall(func=target, tag="slotted-site")

    resolved = component_call.resolve(args=("callsite",), kwargs={"right": 2})
    metadata = slotted_call.site_metadata(slot_path=SlotIdPath.empty())

    assert resolved.func is target
    assert resolved.args == ("callsite",)
    assert dict(resolved.kwargs) == {"right": 2}
    assert component_call._pyrolyze_meta is not None
    assert component_call._pyrolyze_meta._func is target
    assert slotted_call._pyrolyze_slotted is True
    assert metadata == (
        RuntimeSiteMetadata(key="tag", value="slotted-site"),
        RuntimeSiteMetadata(key="depth", value="0"),
    )


def test_component_intrinsic_cast_supports_component_and_container_lowerings() -> None:
    events: list[tuple[object, ...]] = []

    @contextmanager
    def plain_section(title: str):
        events.append(("plain.enter", title))
        try:
            yield
        finally:
            events.append(("plain.exit", title))

    def native_section(ctx: ContextBase, title: str) -> None:
        ctx.call_native(UIElement, kind="native_section", props={"title": title})

    source = """
from pyrolyze.api import UIElement, call_native, pyrolyze

@pyrolyze
def badge(text):
    call_native(UIElement)(kind="badge", props={"text": text})

@pyrolyze
def shell(title):
    call_native(UIElement)(kind="shell", props={"title": title})
"""
    namespace = load_transformed_namespace(
        source,
        module_name="example.runtime_pyro_call.component",
        filename="/virtual/example/runtime_pyro_call/component.py",
    )
    badge = namespace["badge"]
    shell = namespace["shell"]
    ctx = RenderContext()

    with ctx.pass_scope():
        ctx.component_call(
            _COMPONENT_SLOT,
            component,
            badge,
            "Hello",
            dirty_state=dirtyof(text=True),
        )
        ctx.component_call(
            _COMPONENT_SLOT_2,
            component,
            component,
            badge,
            "World",
            dirty_state=dirtyof(text=True),
        )
        with ctx.container_call(_PLAIN_CONTAINER_SLOT, component, plain_section, "Plain"):
            events.append(("plain.body",))
        with ctx.container_call(_NATIVE_CONTAINER_SLOT, component, native_section, "Native"):
            pass
        with ctx.container_call(_PYRO_CONTAINER_SLOT, component, shell, "Shell"):
            pass
        with ctx.container_call(_MOUNT_CONTAINER_SLOT, component, mount, default) as mount_ctx:
            mount_ctx.call_native(UIElement, kind="mounted", props={"title": "Mounted"})
        assert ctx.container_call(_PLAIN_CONTAINER_SLOT, component, None, "Skipped") is None

    assert events == [
        ("plain.enter", "Plain"),
        ("plain.body",),
        ("plain.exit", "Plain"),
    ]
    assert ctx.debug_ui() == (
        UIElement(kind="badge", props={"text": "Hello"}),
        UIElement(kind="badge", props={"text": "World"}),
        UIElement(kind="native_section", props={"title": "Native"}),
        UIElement(kind="shell", props={"title": "Shell"}),
        MountDirective(selectors=(default,), children=(UIElement(kind="mounted", props={"title": "Mounted"}),)),
    )


def test_slotted_intrinsic_cast_supports_slot_call_lowering() -> None:
    @pyrolyze_slotted
    def format_title(name: str) -> str:
        return f"Hello {name}"

    ctx = RenderContext()
    with ctx.pass_scope():
        dirty, value = eval_single_slot_expr(
            ctx,
            dirtyof(),
            _SLOTTED_SLOT,
            slotted,
            format_title,
            "Ada",
            result_name="title",
        )

    assert dirty is True
    assert value == "Hello Ada"


def test_transformed_source_can_use_component_and_slotted_intrinsics_without_compiler_changes() -> None:
    source = """
from pyrolyze.api import UIElement, call_native, component, pyrolyze, pyrolyze_slotted, slotted

@pyrolyze
def badge(text):
    call_native(UIElement)(kind="badge", props={"text": text})

@pyrolyze
def section(title):
    call_native(UIElement)(kind="section", props={"title": title})

@pyrolyze_slotted
def format_title(name):
    return f"Hello {name}"

@pyrolyze
def panel(name):
    title = slotted(format_title, name)
    component(badge, title)
    with component(section, title):
        component(badge, title + " inner")
"""
    namespace = load_transformed_namespace(
        source,
        module_name="example.runtime_pyro_call.intrinsics",
        filename="/virtual/example/runtime_pyro_call/intrinsics.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    with ctx.pass_scope():
        panel._pyrolyze_meta._func(ctx, dirtyof(name=True), "Ada")

    assert ctx.debug_ui() == (
        UIElement(kind="badge", props={"text": "Hello Ada"}),
        UIElement(
            kind="section",
            props={"title": "Hello Ada"},
            children=(UIElement(kind="badge", props={"text": "Hello Ada inner"}),),
        ),
    )


def test_runtime_site_metadata_is_captured_on_component_container_and_slot_call_sites() -> None:
    source = """
from pyrolyze.api import UIElement, call_native, pyrolyze

@pyrolyze
def badge(text):
    call_native(UIElement)(kind="badge", props={"text": text})
"""
    namespace = load_transformed_namespace(
        source,
        module_name="example.runtime_pyro_call.metadata",
        filename="/virtual/example/runtime_pyro_call/metadata.py",
    )
    badge = namespace["badge"]

    @contextmanager
    def plain_section(title: str):
        yield

    @pyrolyze_slotted
    def format_title(name: str) -> str:
        return f"Hello {name}"

    component_wrap = _TaggedComponentCall(func=badge, tag="component-site")
    container_wrap = _TaggedComponentCall(func=plain_section, tag="container-site")
    slotted_wrap = _TaggedSlottedCall(func=format_title, tag="slot-site")

    ctx = RenderContext()
    with ctx.pass_scope():
        ctx.component_call(_COMPONENT_SLOT, component, component_wrap, "Hello", dirty_state=dirtyof(text=True))
        with ctx.container_call(_PLAIN_CONTAINER_SLOT, component, container_wrap, "Wrapper"):
            pass
        dirty, value = eval_single_slot_expr(
            ctx,
            dirtyof(),
            _SLOTTED_SLOT,
            slotted,
            slotted_wrap,
            "Ada",
            result_name="title",
        )

    assert dirty is True
    assert value == "Hello Ada"

    graph = capture_context_graph(ctx)

    captured_by_slot: dict[SlotId, tuple[RuntimeSiteMetadata[object], ...]] = {}

    def walk(node) -> None:
        for entry in node.site_metadata:
            captured_by_slot[entry.slot_id] = entry.metadata
        for child in node.children:
            walk(child)

    walk(graph.root)

    assert captured_by_slot[_COMPONENT_SLOT] == (
        RuntimeSiteMetadata(key="tag", value="component-site"),
        RuntimeSiteMetadata(key="depth", value="1"),
    )
    assert captured_by_slot[_PLAIN_CONTAINER_SLOT] == (
        RuntimeSiteMetadata(key="tag", value="container-site"),
        RuntimeSiteMetadata(key="depth", value="1"),
    )
    assert captured_by_slot[_SLOTTED_SLOT] == (
        RuntimeSiteMetadata(key="tag", value="slot-site"),
        RuntimeSiteMetadata(key="depth", value="1"),
    )
