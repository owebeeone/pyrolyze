from __future__ import annotations

from pyrolyze.api import UIElement
from pyrolyze.backends.model import ChildPolicy, MethodMode, MountParamSpec, MountPointSpec, TypeRef
from pyrolyze.testing.hydo import (
    HYDO_MOUNTABLE_SPECS,
    HydoAppWidget,
    HydoMenu,
    HydoMountableEngine,
    HydoMountedNode,
    HydoWidget,
    HydoWindow,
)


def test_mount_point_spec_builds_instance_keys_from_keyed_params() -> None:
    spec = MountPointSpec(
        name="corner_widget",
        accepted_produced_type=TypeRef("HydoWidget"),
        params=(
            MountParamSpec(name="corner", annotation=TypeRef("str"), keyed=True),
            MountParamSpec(name="weight", annotation=TypeRef("int"), keyed=False),
        ),
        max_children=1,
    )

    assert spec.instance_key({"corner": "top_left", "weight": 3}) == ("corner_widget", "top_left")


def test_hydo_mountable_specs_expose_standard_and_explicit_mount_points() -> None:
    window_spec = HYDO_MOUNTABLE_SPECS["HydoWindow"]
    widget_spec = HYDO_MOUNTABLE_SPECS["HydoWidget"]
    layout_spec = HYDO_MOUNTABLE_SPECS["HydoGridLayout"]
    menu_spec = HYDO_MOUNTABLE_SPECS["HydoMenu"]

    assert window_spec.child_policy is ChildPolicy.ORDERED
    assert "standard" in window_spec.mount_points
    assert "main_widget" in window_spec.mount_points
    assert "title_bar_widget" in window_spec.mount_points
    assert widget_spec.mount_points["layout"].max_children == 1
    assert widget_spec.mount_points["corner_widget"].params[0].keyed is True
    assert layout_spec.mount_points["cell_widget"].params[0].keyed is True
    assert layout_spec.mount_points["cell_widget"].params[1].keyed is True
    assert menu_spec.mount_points["menu"].max_children is None
    assert menu_spec.methods["setRange"].mode is MethodMode.CREATE_UPDATE


def test_hydo_mountable_engine_mounts_standard_child_hierarchy() -> None:
    engine = HydoMountableEngine(HYDO_MOUNTABLE_SPECS)
    element = UIElement(
        kind="HydoWindow",
        props={"name": "root-window", "title": "Root"},
        children=(
            UIElement(
                kind="HydoAppWidget",
                props={"name": "app-root", "title": "Workspace"},
                children=(
                    UIElement(kind="HydoWidget", props={"name": "left-panel", "title": "Left"}),
                    UIElement(
                        kind="HydoMenu",
                        props={"name": "file-menu", "title": "File"},
                        children=(
                            UIElement(kind="HydoMenu", props={"name": "recent-menu", "title": "Recent"}),
                        ),
                    ),
                ),
            ),
        ),
    )

    node = engine.mount(element, slot_id=("root", 1), call_site_id=11)

    assert isinstance(node, HydoMountedNode)
    assert isinstance(node.mountable, HydoWindow)
    assert len(node.child_nodes) == 1
    assert isinstance(node.child_nodes[0].mountable, HydoAppWidget)
    assert [type(child.mountable).__name__ for child in node.child_nodes[0].child_nodes] == [
        "HydoWidget",
        "HydoMenu",
    ]
    assert isinstance(node.child_nodes[0].child_nodes[1].mountable, HydoMenu)
    assert len(node.child_nodes[0].child_nodes[1].child_nodes) == 1
    assert node.mountable.children == [node.child_nodes[0].mountable]
    assert node.mountable.operations[-1].method == "sync_children"


def test_hydo_mountable_engine_updates_standard_children_with_sync() -> None:
    engine = HydoMountableEngine(HYDO_MOUNTABLE_SPECS)
    node = engine.mount(
        UIElement(
            kind="HydoWidget",
            props={"name": "root", "title": "Root"},
            children=(
                UIElement(kind="HydoWidget", props={"name": "first", "title": "First"}),
                UIElement(kind="HydoWidget", props={"name": "second", "title": "Second"}),
            ),
        ),
        slot_id=("root", 2),
        call_site_id=22,
    )

    updated = engine.update(
        node,
        UIElement(
            kind="HydoWidget",
            props={"name": "root", "title": "Root+"},
            children=(
                UIElement(kind="HydoWidget", props={"name": "second", "title": "Second"}),
                UIElement(kind="HydoWidget", props={"name": "first", "title": "First"}),
                UIElement(kind="HydoWidget", props={"name": "third", "title": "Third"}),
            ),
        ),
    )

    assert updated is node
    assert isinstance(node.mountable, HydoWidget)
    assert node.mountable.title == "Root+"
    assert [child.name for child in node.mountable.children] == ["second", "first", "third"]
    assert node.mountable.operations[-1].method == "sync_children"
