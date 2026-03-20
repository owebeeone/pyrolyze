from __future__ import annotations

from pyrolyze.runtime.context import ModuleRegistry, SlotId
from pyrolyze.runtime.ui_nodes import normalize_ui_inputs

from Studio.runtime_ext import studio_descriptors, studio_elements


def _owner_slot() -> SlotId:
    registry = ModuleRegistry()
    return SlotId(registry.module_id("tests.studio.runtime_ext"), 1)


def test_custom_kind_set_matches_expected_v1_studio_nodes() -> None:
    assert studio_descriptors.STUDIO_CUSTOM_KINDS == (
        "studio_splitter",
        "studio_tabs",
        "studio_tab_page",
        "studio_toolbar",
        "studio_tree_view",
        "studio_status_strip",
        "studio_overlay_canvas",
        "studio_screenshot_canvas",
    )


def test_studio_registry_includes_base_and_custom_kinds() -> None:
    registry = studio_descriptors.build_studio_registry(include_base=True)
    # Base kind from frozen v1
    assert registry.descriptor_for("section").kind == "section"
    # Studio custom kind
    assert registry.descriptor_for("studio_splitter").kind == "studio_splitter"
    assert registry.descriptor_for("studio_tree_view").kind == "studio_tree_view"


def test_custom_descriptor_normalization_accepts_splitter_mapping() -> None:
    owner_slot = _owner_slot()
    registry = studio_descriptors.build_studio_registry(include_base=True)
    specs = normalize_ui_inputs(
        owner_slot,
        (
            {
                "kind": "studio_splitter",
                "props": {
                    "splitter_id": "workspace:main",
                    "orientation": "horizontal",
                    "visible": True,
                },
                "children": (
                    {"kind": "section", "props": {"title": "Left", "accent": "blue"}},
                    {"kind": "section", "props": {"title": "Right", "accent": "green"}},
                ),
            },
        ),
        registry=registry,
    )

    assert len(specs) == 1
    splitter = specs[0]
    assert splitter.kind == "studio_splitter"
    assert splitter.props["splitter_id"] == "workspace:main"
    assert splitter.props["orientation"] == "horizontal"
    assert splitter.props["visible"] is True
    assert len(splitter.children) == 2


def test_studio_element_component_refs_are_exposed() -> None:
    refs = (
        studio_elements.studio_splitter,
        studio_elements.studio_tabs,
        studio_elements.studio_tab_page,
        studio_elements.studio_toolbar,
        studio_elements.studio_tree_view,
        studio_elements.studio_status_strip,
        studio_elements.studio_overlay_canvas,
        studio_elements.studio_screenshot_canvas,
    )
    for ref in refs:
        assert hasattr(ref, "_pyrolyze_meta")
