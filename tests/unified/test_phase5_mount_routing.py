"""Phase 5.3: mount key adverts route ``mount_key(...)`` to native selectors (engine-level).

Qt uses ``QMainWindow`` + ``mounts.central_widget``. Tk uses ``ttk.Frame`` and advert
targets must name real mount points (here ``pack``). DPG uses ``DpgWindow`` +
``standard`` under ``RecordingDpgHost``.
"""

from __future__ import annotations

from pyrolyze.api import (
    MountDirective,
    MountSelector,
    PyrolyzeMountAdvertisement,
    UIElement,
    mount_key,
)
from pyrolyze.backends.dearpygui.generated_library import DearPyGuiUiLibrary
from pyrolyze.backends.mountable_engine import MountableEngine
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary
from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary
from pyrolyze.unified import mount_keys


def test_phase5_qt_mount_routing_resolves_shell_body_to_central_widget(qapplication: object) -> None:
    _ = qapplication
    eng = MountableEngine(PySide6UiLibrary.WIDGET_SPECS)
    m = PySide6UiLibrary.mounts
    advert = PyrolyzeMountAdvertisement(
        key=mount_keys.SHELL_BODY,
        selectors=(m.central_widget,),
        default=True,
    )
    button = UIElement(kind="QPushButton", props={"text": "Smoke"})
    mount_directive = MountDirective(
        selectors=(mount_key(mount_keys.SHELL_BODY),),
        children=(button,),
    )
    root = UIElement(kind="QMainWindow", props={}, children=(advert, mount_directive))
    node = eng.mount(root, slot_id=("phase5", "qt", 1), call_site_id=901)
    assert len(node.child_nodes) == 1
    assert node.child_nodes[0].element.kind == "QPushButton"


def test_phase5_tk_mount_routing_resolves_shell_body_to_pack(tk_root: object) -> None:
    _ = tk_root
    eng = MountableEngine(TkinterUiLibrary.WIDGET_SPECS)
    pack_target = MountSelector.named("pack")
    advert = PyrolyzeMountAdvertisement(
        key=mount_keys.SHELL_BODY,
        selectors=(pack_target,),
        default=True,
    )
    button = UIElement(kind="ttk_Button", props={"text": "Smoke"})
    mount_directive = MountDirective(
        selectors=(mount_key(mount_keys.SHELL_BODY),),
        children=(button,),
    )
    root = UIElement(kind="ttk_Frame", props={}, children=(advert, mount_directive))
    node = eng.mount(root, slot_id=("phase5", "tk", 1), call_site_id=902)
    assert len(node.child_nodes) == 1
    assert node.child_nodes[0].element.kind == "ttk_Button"


def test_phase5_dpg_mount_routing_resolves_shell_body_to_standard(recording_dpg_host: object) -> None:
    _ = recording_dpg_host
    eng = MountableEngine(DearPyGuiUiLibrary.WIDGET_SPECS)
    standard = MountSelector.named("standard")
    advert = PyrolyzeMountAdvertisement(
        key=mount_keys.SHELL_BODY,
        selectors=(standard,),
        default=True,
    )
    button = UIElement(kind="DpgButton", props={"label": "Smoke"})
    mount_directive = MountDirective(
        selectors=(mount_key(mount_keys.SHELL_BODY),),
        children=(button,),
    )
    root = UIElement(kind="DpgWindow", props={"label": "phase5"}, children=(advert, mount_directive))
    node = eng.mount(root, slot_id=("phase5", "dpg", 1), call_site_id=903)
    assert len(node.child_nodes) == 1
    assert node.child_nodes[0].element.kind == "DpgButton"
