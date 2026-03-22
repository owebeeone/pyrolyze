from __future__ import annotations

from pyrolyze.api import MountDirective
from pyrolyze.compiler import emit_transformed_source, load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof


def test_mount_with_lowers_to_open_directive_and_emits_mount_directive_tree() -> None:
    source = """
from pyrolyze.api import MountSelector, UIElement, call_native, default, mount, pyrolyze

menu = MountSelector.named("menu")
corner = MountSelector.named("corner_widget")

@pyrolyze
def badge(text):
    call_native(UIElement)(kind="badge", props={"text": text})

@pyrolyze
def panel(show_inner):
    with mount(menu, default):
        badge("File")
        if show_inner:
            with mount(corner(corner="top_left")):
                badge("Edit")
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.mount.panel",
        filename="/virtual/example/mount/panel.py",
    )

    assert "with __pyr_ctx.open_directive(" in transformed
    assert "__pyr_validate_mount_selectors" in transformed
    assert transformed.count("open_directive(") == 2
    assert ".container_call(" not in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.mount.panel",
        filename="/virtual/example/mount/panel.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(show_inner=True), True)

    ui_element = namespace["UIElement"]
    menu = namespace["menu"]
    corner = namespace["corner"]
    default = namespace["default"]

    assert ctx.debug_ui() == (
        MountDirective(
            selectors=(menu, default),
            children=(
                ui_element(kind="badge", props={"text": "File"}),
                MountDirective(
                    selectors=(corner(corner="top_left"),),
                    children=(ui_element(kind="badge", props={"text": "Edit"}),),
                ),
            ),
        ),
    )


def test_mount_with_supports_dynamic_selector_splats() -> None:
    source = """
from pyrolyze.api import MountSelector, UIElement, call_native, mount, pyrolyze

menu = MountSelector.named("menu")
widget = MountSelector.named("widget")

@pyrolyze
def badge(text):
    call_native(UIElement)(kind="badge", props={"text": text})

@pyrolyze
def panel(sels):
    with mount(*sels):
        badge("File")
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.mount.splat_panel",
        filename="/virtual/example/mount/splat_panel.py",
    )

    assert "open_directive(" in transformed
    assert "*sels" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.mount.splat_panel",
        filename="/virtual/example/mount/splat_panel.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()
    panel._pyrolyze_meta._func(ctx, dirtyof(sels=True), (namespace["menu"], namespace["widget"]))

    ui_element = namespace["UIElement"]

    assert ctx.debug_ui() == (
        MountDirective(
            selectors=(namespace["menu"], namespace["widget"]),
            children=(ui_element(kind="badge", props={"text": "File"}),),
        ),
    )
