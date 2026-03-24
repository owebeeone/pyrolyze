from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest

from pyrolyze.api import UIElement
from pyrolyze.backends.mountable_engine import MountableEngine, MountedMountableNode, MountableNodeKey
from pyrolyze.testing import hydo

GENERATED_HYDO_LIBRARY_PATH = Path(__file__).resolve().parents[1] / "scratch" / "generated_hydo_library.py"

pytestmark = pytest.mark.skipif(
    not GENERATED_HYDO_LIBRARY_PATH.is_file(),
    reason="requires generated Hydo helper under scratch/",
)


def _load_generated_hydo_module():
    module_name = "generated_hydo_library_runtime_test"
    spec = importlib.util.spec_from_file_location(module_name, GENERATED_HYDO_LIBRARY_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(module_name, None)
    return module


def test_generated_hydo_engine_mounts_tree_from_generated_specs() -> None:
    module = _load_generated_hydo_module()
    engine = MountableEngine(module.HydoUiLibrary.MOUNTABLE_SPECS)

    app_root = module.HydoUiLibrary.UI_INTERFACE.build_element(
        "CHydoAppWidget",
        name="app-root",
        title="Workspace",
    )
    file_menu = module.HydoUiLibrary.UI_INTERFACE.build_element(
        "CHydoMenu",
        name="file-menu",
        title="File",
    )
    left_panel = module.HydoUiLibrary.UI_INTERFACE.build_element(
        "CHydoWidget",
        name="left-panel",
        title="Left",
    )
    element = UIElement(
        kind="HydoWindow",
        props={"name": "root-window", "title": "Root"},
        children=(
            UIElement(
                kind=app_root.kind,
                props=app_root.props,
                children=(left_panel, file_menu),
            ),
        ),
    )

    node = engine.mount(element, slot_id=("root", "window", 1), call_site_id=17)

    assert isinstance(node, MountedMountableNode)
    assert node.key == MountableNodeKey(slot_id=("root", "window", 1), call_site_id=17, kind="HydoWindow")
    assert isinstance(node.mountable, hydo.HydoWindow)
    assert len(node.child_nodes) == 1
    assert isinstance(node.child_nodes[0].mountable, hydo.HydoAppWidget)
    assert [type(child.mountable).__name__ for child in node.child_nodes[0].child_nodes] == [
        "HydoWidget",
        "HydoMenu",
    ]
    assert node.mountable.children == [node.child_nodes[0].mountable]
    assert node.mountable.operations[-1].method == "sync_children"


def test_generated_hydo_engine_updates_method_backed_props_and_reorders_children() -> None:
    module = _load_generated_hydo_module()
    engine = MountableEngine(module.HydoUiLibrary.MOUNTABLE_SPECS)

    first = module.HydoUiLibrary.UI_INTERFACE.build_element(
        "CHydoWidget",
        name="first",
        title="First",
    )
    second = module.HydoUiLibrary.UI_INTERFACE.build_element(
        "CHydoWidget",
        name="second",
        title="Second",
    )
    node = engine.mount(
        UIElement(
            kind="HydoWidget",
            props={
                "name": "root",
                "title": "Root",
                "minimum": 1,
                "maximum": 10,
            },
            children=(first, second),
        ),
        slot_id=("root", "widget", 1),
        call_site_id=31,
    )

    updated = engine.update(
        node,
        UIElement(
            kind="HydoWidget",
            props={
                "name": "root",
                "title": "Root+",
                "maximum": 12,
            },
            children=(second, first),
        ),
    )

    assert updated is node
    assert isinstance(node.mountable, hydo.HydoWidget)
    assert node.mountable.title == "Root+"
    assert node.mountable.range_values == (1, 12)
    assert [child.name for child in node.mountable.children] == ["second", "first"]
    assert node.effective_props["minimum"] == 1
    assert node.effective_props["maximum"] == 12
