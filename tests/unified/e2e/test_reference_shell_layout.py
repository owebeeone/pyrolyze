"""Phase 2.3: same reference shell advert graph for Qt, Tk, and DPG.

The @pyrolyze tree shape and ``mount_keys.*`` strings are identical across
backends; only the host widget kind and ``target=`` selectors differ. See
``dev-docs/ReferenceShellLayout.md``.
"""

from __future__ import annotations

from pyrolyze.api import PyrolyzeMountAdvertisement
from pyrolyze.compiler import emit_transformed_source, load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof
from pyrolyze.unified import mount_keys

# Identical advert sequence for every backend (keys + default flags).
_EXPECTED_DEFAULTS = (False, True, False)


def _expected_advertisements(
    menu_target: object,
    body_target: object,
    status_target: object,
) -> tuple[PyrolyzeMountAdvertisement, ...]:
    return (
        PyrolyzeMountAdvertisement(
            key=mount_keys.SHELL_MENU_BAR,
            selectors=(menu_target,),
            default=False,
        ),
        PyrolyzeMountAdvertisement(
            key=mount_keys.SHELL_BODY,
            selectors=(body_target,),
            default=True,
        ),
        PyrolyzeMountAdvertisement(
            key=mount_keys.SHELL_STATUS,
            selectors=(status_target,),
            default=False,
        ),
    )


def _assert_reference_shell_adverts(
    advertisements: tuple[PyrolyzeMountAdvertisement, ...],
    *,
    menu_target: object,
    body_target: object,
    status_target: object,
) -> None:
    assert [a.default for a in advertisements] == list(_EXPECTED_DEFAULTS)
    assert [a.key for a in advertisements] == [
        mount_keys.SHELL_MENU_BAR,
        mount_keys.SHELL_BODY,
        mount_keys.SHELL_STATUS,
    ]
    for adv in advertisements:
        assert adv.source_slot_id is not None
    assert advertisements == _expected_advertisements(menu_target, body_target, status_target)


def _run_transformed_shell(
    *,
    source: str,
    module_name: str,
    filename: str,
) -> tuple[tuple[PyrolyzeMountAdvertisement, ...], dict[str, object]]:
    transformed = emit_transformed_source(
        source,
        module_name=module_name,
        filename=filename,
    )
    assert ".call_plain(" in transformed
    assert "advertise_mount" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name=module_name,
        filename=filename,
    )
    reference_shell = namespace["reference_shell"]
    ctx = RenderContext()
    reference_shell._pyrolyze_meta._func(ctx, dirtyof())
    return ctx.debug_mount_advertisements(), namespace


_SOURCE_QT = """
from pyrolyze.api import UIElement, advertise_mount, call_native, pyrolyze
from pyrolyze.unified import mount_keys
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary

_m = PySide6UiLibrary.mounts

@pyrolyze
def host():
    call_native(UIElement)(kind="QWidget", props={})

@pyrolyze
def reference_shell():
    with host():
        advertise_mount(mount_keys.SHELL_MENU_BAR, target=_m.menu_bar, default=False)
        advertise_mount(mount_keys.SHELL_BODY, target=_m.central_widget, default=True)
        advertise_mount(mount_keys.SHELL_STATUS, target=_m.status_bar, default=False)
"""

_SOURCE_TK = """
from pyrolyze.api import MountSelector, UIElement, advertise_mount, call_native, pyrolyze
from pyrolyze.unified import mount_keys

_menu = MountSelector.named("ref_shell_tk_menu_bar")
_body = MountSelector.named("ref_shell_tk_body")
_status = MountSelector.named("ref_shell_tk_status")

@pyrolyze
def host():
    call_native(UIElement)(kind="ttk_Frame", props={})

@pyrolyze
def reference_shell():
    with host():
        advertise_mount(mount_keys.SHELL_MENU_BAR, target=_menu, default=False)
        advertise_mount(mount_keys.SHELL_BODY, target=_body, default=True)
        advertise_mount(mount_keys.SHELL_STATUS, target=_status, default=False)
"""

_SOURCE_DPG = """
from pyrolyze.api import MountSelector, UIElement, advertise_mount, call_native, pyrolyze
from pyrolyze.unified import mount_keys

_menu = MountSelector.named("ref_shell_dpg_menu_bar")
_body = MountSelector.named("ref_shell_dpg_body")
_status = MountSelector.named("ref_shell_dpg_status")

@pyrolyze
def host():
    call_native(UIElement)(kind="DpgWindow", props={"label": "ref_shell_e2e"})

@pyrolyze
def reference_shell():
    with host():
        advertise_mount(mount_keys.SHELL_MENU_BAR, target=_menu, default=False)
        advertise_mount(mount_keys.SHELL_BODY, target=_body, default=True)
        advertise_mount(mount_keys.SHELL_STATUS, target=_status, default=False)
"""


def test_reference_shell_layout_qt() -> None:
    from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary

    m = PySide6UiLibrary.mounts
    adverts, _ns = _run_transformed_shell(
        source=_SOURCE_QT,
        module_name="tests.unified.e2e.reference_shell.qt",
        filename="/virtual/tests/unified/e2e/reference_shell/qt.py",
    )
    _assert_reference_shell_adverts(
        adverts,
        menu_target=m.menu_bar,
        body_target=m.central_widget,
        status_target=m.status_bar,
    )


def test_reference_shell_layout_tk() -> None:
    adverts, ns = _run_transformed_shell(
        source=_SOURCE_TK,
        module_name="tests.unified.e2e.reference_shell.tk",
        filename="/virtual/tests/unified/e2e/reference_shell/tk.py",
    )
    _assert_reference_shell_adverts(
        adverts,
        menu_target=ns["_menu"],
        body_target=ns["_body"],
        status_target=ns["_status"],
    )


def test_reference_shell_layout_dpg() -> None:
    adverts, ns = _run_transformed_shell(
        source=_SOURCE_DPG,
        module_name="tests.unified.e2e.reference_shell.dpg",
        filename="/virtual/tests/unified/e2e/reference_shell/dpg.py",
    )
    _assert_reference_shell_adverts(
        adverts,
        menu_target=ns["_menu"],
        body_target=ns["_body"],
        status_target=ns["_status"],
    )
