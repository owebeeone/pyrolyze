from __future__ import annotations

from typing import Sequence

from pyrolyze.runtime.ui_nodes import (
    ChildPolicy,
    FROZEN_V1_REGISTRY,
    NodeRole,
    UiEventSpec,
    UiNodeDescriptor,
    UiNodeDescriptorRegistry,
    UiPropSpec,
)


STUDIO_CUSTOM_KINDS: tuple[str, ...] = (
    "studio_splitter",
    "studio_tabs",
    "studio_tab_page",
    "studio_toolbar",
    "studio_tree_view",
    "studio_status_strip",
    "studio_overlay_canvas",
    "studio_screenshot_canvas",
)


def _descriptor(
    *,
    kind: str,
    role: NodeRole,
    child_policy: ChildPolicy,
    props: Sequence[UiPropSpec],
    events: Sequence[UiEventSpec] = (),
) -> UiNodeDescriptor:
    return UiNodeDescriptor(
        kind=kind,
        role=role,
        child_policy=child_policy,
        props={prop.name: prop for prop in props},
        events={event.name: event for event in events},
    )


def studio_custom_descriptors() -> dict[str, UiNodeDescriptor]:
    return {
        "studio_splitter": _descriptor(
            kind="studio_splitter",
            role="container",
            child_policy="ordered",
            props=(
                UiPropSpec("splitter_id", required=True, affects_identity=True),
                UiPropSpec("orientation", required=True),
                UiPropSpec("sizes", default=()),
                UiPropSpec("handle_width", default=7),
                UiPropSpec("visible", default=True),
            ),
            events=(UiEventSpec("on_splitter_moved", payload_shape="value"),),
        ),
        "studio_tabs": _descriptor(
            kind="studio_tabs",
            role="container",
            child_policy="ordered",
            props=(
                UiPropSpec("tabs_id", required=True, affects_identity=True),
                UiPropSpec("movable", default=False),
                UiPropSpec("closable", default=False),
                UiPropSpec("current_index", default=0),
                UiPropSpec("visible", default=True),
            ),
            events=(
                UiEventSpec("on_current_changed", payload_shape="value"),
                UiEventSpec("on_tab_close", payload_shape="value"),
            ),
        ),
        "studio_tab_page": _descriptor(
            kind="studio_tab_page",
            role="container",
            child_policy="ordered",
            props=(
                UiPropSpec("page_id", required=True, affects_identity=True),
                UiPropSpec("title", required=True),
                UiPropSpec("closable", default=False),
                UiPropSpec("visible", default=True),
            ),
        ),
        "studio_toolbar": _descriptor(
            kind="studio_toolbar",
            role="container",
            child_policy="ordered",
            props=(
                UiPropSpec("toolbar_id", required=True, affects_identity=True),
                UiPropSpec("title", default=""),
                UiPropSpec("visible", default=True),
            ),
        ),
        "studio_tree_view": _descriptor(
            kind="studio_tree_view",
            role="input",
            child_policy="none",
            props=(
                UiPropSpec("tree_id", required=True, affects_identity=True),
                UiPropSpec("root_path", required=True),
                UiPropSpec("show_hidden", default=False),
                UiPropSpec("visible", default=True),
            ),
            events=(
                UiEventSpec("on_selected", payload_shape="text"),
                UiEventSpec("on_activated", payload_shape="text"),
            ),
        ),
        "studio_status_strip": _descriptor(
            kind="studio_status_strip",
            role="leaf",
            child_policy="none",
            props=(
                UiPropSpec("strip_id", required=True, affects_identity=True),
                UiPropSpec("status_message", default="Ready"),
                UiPropSpec("encoding", default="UTF-8"),
                UiPropSpec("line_col", default="Ln 1, Col 1"),
                UiPropSpec("indent_mode", default="Spaces: 4"),
                UiPropSpec("visible", default=True),
            ),
        ),
        "studio_overlay_canvas": _descriptor(
            kind="studio_overlay_canvas",
            role="leaf",
            child_policy="none",
            props=(
                UiPropSpec("overlay_id", required=True, affects_identity=True),
                UiPropSpec("target_rect", default=None),
                UiPropSpec("highlight_color", default="#ff0000"),
                UiPropSpec("visible", default=True),
            ),
        ),
        "studio_screenshot_canvas": _descriptor(
            kind="studio_screenshot_canvas",
            role="input",
            child_policy="none",
            props=(
                UiPropSpec("canvas_id", required=True, affects_identity=True),
                UiPropSpec("has_image", default=False),
                UiPropSpec("stroke_color", default="#ff0000"),
                UiPropSpec("stroke_width", default=2),
                UiPropSpec("visible", default=True),
            ),
            events=(UiEventSpec("on_draw_changed", payload_shape="value"),),
        ),
    }


def build_studio_registry(*, include_base: bool = True) -> UiNodeDescriptorRegistry:
    descriptors: dict[str, UiNodeDescriptor] = {}
    if include_base:
        descriptors.update(FROZEN_V1_REGISTRY.descriptors)
    descriptors.update(studio_custom_descriptors())
    return UiNodeDescriptorRegistry(descriptors=descriptors)


STUDIO_REGISTRY = build_studio_registry(include_base=True)


__all__ = [
    "STUDIO_CUSTOM_KINDS",
    "STUDIO_REGISTRY",
    "build_studio_registry",
    "studio_custom_descriptors",
]
