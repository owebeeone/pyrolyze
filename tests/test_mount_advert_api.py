from __future__ import annotations

from pyrolyze.api import (
    MountSelector,
    PyrolyzeMountAdvertisement,
    PyrolyzeMountAdvertisementRequest,
    UIElement,
    advertise_mount,
)
from pyrolyze.compiler import emit_transformed_source, load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof


def test_advertise_mount_returns_public_request_shape() -> None:
    menu = MountSelector.named("menu")

    request = advertise_mount("body", menu, default=True)

    assert request == PyrolyzeMountAdvertisementRequest(
        key="body",
        selectors=(menu,),
        default=True,
    )


def test_imported_advertise_mount_lowers_to_call_plain_and_publishes() -> None:
    source = """
from pyrolyze.api import MountSelector, UIElement, advertise_mount, call_native, pyrolyze

menu = MountSelector.named("menu")

@pyrolyze
def section():
    call_native(UIElement)(kind="section", props={"title": "Wrapper"})

@pyrolyze
def panel():
    with section():
        advertise_mount("body", target=menu, default=True)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.mount_advert.panel",
        filename="/virtual/example/mount_advert/panel.py",
    )

    assert ".call_plain(" in transformed
    assert "advertise_mount" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.mount_advert.panel",
        filename="/virtual/example/mount_advert/panel.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof())

    advertisements = ctx.debug_mount_advertisements()
    assert advertisements == (
        PyrolyzeMountAdvertisement(
            key="body",
            selectors=(namespace["menu"],),
            default=True,
        ),
    )
    assert advertisements[0].source_slot_id is not None
    assert advertisements[0].surface_owner_id is not None
    assert ctx.debug_ui() == (
        UIElement(
            kind="section",
            props={"title": "Wrapper"},
            children=(advertisements[0],),
        ),
    )


def test_imported_return_typed_mount_advert_helper_is_detected_without_slotted_decorator() -> None:
    source = """
from pyrolyze.api import UIElement, call_native, pyrolyze
from pyrolyze_testsupport.imported_annotations import imported_advert_request, reset_logs, LOG

@pyrolyze
def section():
    call_native(UIElement)(kind="section", props={"title": "Wrapper"})

@pyrolyze
def panel():
    with section():
        imported_advert_request("body")
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.mount_advert.imported_request",
        filename="/virtual/example/mount_advert/imported_request.py",
    )

    assert ".call_plain(" in transformed
    assert "imported_advert_request" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.mount_advert.imported_request",
        filename="/virtual/example/mount_advert/imported_request.py",
    )
    panel = namespace["panel"]
    reset_logs = namespace["reset_logs"]
    reset_logs()
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof())

    assert namespace["LOG"] == [("advert_request", "body")]
    advertisements = ctx.debug_mount_advertisements()
    assert advertisements == (
        PyrolyzeMountAdvertisement(
            key="body",
            selectors=advertisements[0].selectors,
            default=False,
        ),
    )
    assert len(advertisements[0].selectors) == 1
    assert advertisements[0].selectors[0].name == "imported_menu"
    assert advertisements[0].surface_owner_id is not None
