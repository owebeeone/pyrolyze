from __future__ import annotations

from pyrolyze.api import (
    MountDirective,
    MountSelector,
    PyrolyzeMountAdvertisement,
    UIElement,
    default,
    mount_key,
)
from pyrolyze.backends.mountable_engine import MountableEngine, MountedMountableNode
from pyrolyze.testing.hydo import HYDO_MOUNTABLE_SPECS


def _engine() -> MountableEngine:
    return MountableEngine(HYDO_MOUNTABLE_SPECS)


def _mount_state_snapshot(node: MountedMountableNode) -> tuple[tuple[object, ...], ...]:
    return tuple(
        sorted(
            (
                instance_key,
                state.mount_point.name,
                tuple(sorted(state.values.items())),
                tuple(ref.node_id for ref in state.objects),
            )
            for instance_key, state in node.mount_states.items()
        )
    )


def _mountable_snapshot(mountable: object) -> tuple[tuple[str, object], ...]:
    snapshot: dict[str, object] = {
        "type": type(mountable).__name__,
        "name": getattr(mountable, "name", None),
        "title": getattr(mountable, "title", None),
    }
    if hasattr(mountable, "children"):
        snapshot["children"] = tuple(child.name for child in getattr(mountable, "children"))
    if hasattr(mountable, "menus"):
        snapshot["menus"] = tuple(child.name for child in getattr(mountable, "menus"))
    if hasattr(mountable, "widgets"):
        snapshot["widgets"] = tuple(child.name for child in getattr(mountable, "widgets"))
    if hasattr(mountable, "corner_widgets"):
        snapshot["corner_widgets"] = tuple(
            sorted((key, value.name) for key, value in getattr(mountable, "corner_widgets").items())
        )
    if hasattr(mountable, "cells"):
        snapshot["cells"] = tuple(
            sorted((key, value.name) for key, value in getattr(mountable, "cells").items())
        )
    if hasattr(mountable, "layout"):
        layout = getattr(mountable, "layout")
        snapshot["layout"] = None if layout is None else layout.name
    if hasattr(mountable, "main_widget"):
        main_widget = getattr(mountable, "main_widget")
        snapshot["main_widget"] = None if main_widget is None else main_widget.name
    if hasattr(mountable, "title_bar_widget"):
        title_bar_widget = getattr(mountable, "title_bar_widget")
        snapshot["title_bar_widget"] = None if title_bar_widget is None else title_bar_widget.name
    return tuple(sorted(snapshot.items()))


def _graph_snapshot(node: MountedMountableNode) -> tuple[object, ...]:
    return (
        node.key.slot_id,
        node.key.call_site_id,
        node.element.kind,
        tuple(sorted(node.effective_props.items())),
        _mount_state_snapshot(node),
        _mountable_snapshot(node.mountable),
        tuple(_graph_snapshot(child) for child in node.child_nodes),
    )


def _corner_wrapper_tree(public_key) -> UIElement:
    return UIElement(
        kind="HydoWidget",
        props={"name": "wrapper", "title": "Wrapper"},
        children=(
            UIElement(kind="HydoWidget", props={"name": "body", "title": "Body"}),
            PyrolyzeMountAdvertisement(
                key=public_key,
                selectors=(MountSelector.named("corner_widget")(corner="top_left"),),
            ),
            MountDirective(
                selectors=(public_key,),
                children=(UIElement(kind="HydoWidget", props={"name": "corner", "title": "Corner"}),),
            ),
        ),
    )


def test_hydo_mount_advert_rerender_with_identical_input_keeps_exact_graph_snapshot() -> None:
    engine = _engine()
    key = mount_key("corner_slot")
    element = _corner_wrapper_tree(key)

    node = engine.mount(element, slot_id=("root", "corner", 1), call_site_id=11)
    first_snapshot = _graph_snapshot(node)

    engine.update(node, element)
    second_snapshot = _graph_snapshot(node)

    assert first_snapshot == second_snapshot
    assert node.mountable.children[0].name == "body"
    assert node.mountable.corner_widgets["top_left"].name == "corner"


def test_hydo_mount_advert_public_key_rename_keeps_translated_graph_identical() -> None:
    engine = _engine()
    first = _corner_wrapper_tree(mount_key("corner_a"))
    second = _corner_wrapper_tree(mount_key("corner_b"))

    node = engine.mount(first, slot_id=("root", "corner", 2), call_site_id=12)
    first_snapshot = _graph_snapshot(node)

    engine.update(node, second)
    second_snapshot = _graph_snapshot(node)

    assert first_snapshot == second_snapshot


def test_hydo_mount_advert_default_routes_default_selector_to_anchor_target() -> None:
    engine = _engine()
    element = UIElement(
        kind="HydoWidget",
        props={"name": "wrapper", "title": "Wrapper"},
        children=(
            UIElement(kind="HydoWidget", props={"name": "body", "title": "Body"}),
            PyrolyzeMountAdvertisement(
                key=mount_key("default_corner"),
                selectors=(MountSelector.named("corner_widget")(corner="top_left"),),
                default=True,
            ),
            MountDirective(
                selectors=(default,),
                children=(UIElement(kind="HydoWidget", props={"name": "corner", "title": "Corner"}),),
            ),
        ),
    )

    node = engine.mount(element, slot_id=("root", "corner", 3), call_site_id=13)

    assert node.mountable.children[0].name == "body"
    assert node.mountable.corner_widgets["top_left"].name == "corner"


def test_hydo_mount_advert_removal_detaches_routed_mount_without_ghost_state() -> None:
    engine = _engine()
    key = mount_key("corner_slot")
    node = engine.mount(
        _corner_wrapper_tree(key),
        slot_id=("root", "corner", 4),
        call_site_id=14,
    )

    engine.update(
        node,
        UIElement(
            kind="HydoWidget",
            props={"name": "wrapper", "title": "Wrapper"},
            children=(UIElement(kind="HydoWidget", props={"name": "body", "title": "Body"}),),
        ),
    )

    assert [child.name for child in node.mountable.children] == ["body"]
    assert all(value is None for value in node.mountable.corner_widgets.values())
    assert len(node.child_nodes) == 1
    assert all(state.mount_point.name != "corner_widget" for state in node.mount_states.values())


def test_hydo_mount_advert_preserves_consumer_order_within_one_anchor_bucket() -> None:
    engine = _engine()
    menu_bucket = mount_key("menu_bucket")
    element = UIElement(
        kind="HydoMenu",
        props={"name": "root-menu", "title": "Root"},
        children=(
            PyrolyzeMountAdvertisement(
                key=menu_bucket,
                selectors=(MountSelector.named("menu"),),
            ),
            MountDirective(
                selectors=(menu_bucket,),
                children=(UIElement(kind="HydoMenu", props={"name": "alpha", "title": "Alpha"}),),
            ),
            MountDirective(
                selectors=(menu_bucket,),
                children=(UIElement(kind="HydoMenu", props={"name": "beta", "title": "Beta"}),),
            ),
        ),
    )

    node = engine.mount(element, slot_id=("root", "menu", 1), call_site_id=21)

    assert [menu.name for menu in node.mountable.menus] == ["alpha", "beta"]
