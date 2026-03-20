from __future__ import annotations

import pytest

from pyrolyze.api import UIElement
from pyrolyze.runtime.context import ModuleRegistry, SlotId
from pyrolyze.runtime.ui_nodes import UiNodeId, normalize_ui_elements


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.ui_node_bindings")
_OWNER_SLOT = SlotId(_MODULE_ID, 1, line_no=10)


def test_normalize_ui_elements_splits_value_props_and_event_props() -> None:
    calls: list[object] = []

    def on_press() -> None:
        calls.append("press")

    def on_change(value: str) -> None:
        calls.append(value)

    specs = normalize_ui_elements(
        _OWNER_SLOT,
        (
            UIElement(
                kind="section",
                props={"title": "Toolbar", "accent": "cyan", "visible": True},
                children=(
                    UIElement(
                        kind="button",
                        props={
                            "label": "Run",
                            "enabled": False,
                            "visible": True,
                            "on_press": on_press,
                        },
                    ),
                    UIElement(
                        kind="text_field",
                        props={
                            "field_id": "display-name",
                            "label": "Display Name",
                            "value": "Ada",
                            "enabled": True,
                            "visible": True,
                            "on_change": on_change,
                        },
                    ),
                ),
            ),
        ),
    )

    assert len(specs) == 1
    section = specs[0]
    assert section.node_id == UiNodeId(owner_slot_id=_OWNER_SLOT, region_index=0)
    assert section.kind == "section"
    assert section.props == {"title": "Toolbar", "accent": "cyan", "visible": True}
    assert section.event_props == {}
    assert len(section.children) == 2

    button, text_field = section.children
    assert button.node_id == UiNodeId(owner_slot_id=_OWNER_SLOT, region_index=1)
    assert button.props == {"label": "Run", "enabled": False, "tone": "default", "visible": True}
    assert button.event_props == {"on_press": on_press}

    assert text_field.node_id == UiNodeId(owner_slot_id=_OWNER_SLOT, region_index=2)
    assert text_field.props == {
        "field_id": "display-name",
        "label": "Display Name",
        "value": "Ada",
        "enabled": True,
        "placeholder": None,
        "visible": True,
    }
    assert text_field.event_props == {"on_change": on_change, "on_submit": None}


def test_normalize_ui_elements_fills_missing_events_with_none() -> None:
    specs = normalize_ui_elements(
        _OWNER_SLOT,
        (
            UIElement(
                kind="button",
                props={"label": "Run", "enabled": True, "visible": True},
            ),
        ),
    )

    assert len(specs) == 1
    assert specs[0].event_props == {"on_press": None}


def test_normalize_ui_elements_rejects_unknown_props_and_non_v1_kinds() -> None:
    with pytest.raises(ValueError, match="unsupported prop"):
        normalize_ui_elements(
            _OWNER_SLOT,
            (
                UIElement(kind="badge", props={"text": "Ready", "label": "wrong", "visible": True}),
            ),
        )

    with pytest.raises(ValueError, match="unsupported UIElement kind"):
        normalize_ui_elements(
            _OWNER_SLOT,
            (
                UIElement(kind="column", props={"visible": True}),
            ),
        )


def test_normalize_ui_elements_uses_call_site_identity_for_stable_reorder_ids() -> None:
    first = normalize_ui_elements(
        _OWNER_SLOT,
        (
            UIElement(kind="badge", props={"text": "One", "visible": True}, call_site_id=1),
            UIElement(kind="badge", props={"text": "Two", "visible": True}, call_site_id=2),
        ),
    )
    second = normalize_ui_elements(
        _OWNER_SLOT,
        (
            UIElement(kind="badge", props={"text": "Two", "visible": True}, call_site_id=2),
            UIElement(kind="badge", props={"text": "One", "visible": True}, call_site_id=1),
        ),
    )

    assert first[0].node_id == second[1].node_id
    assert first[1].node_id == second[0].node_id


def test_normalize_ui_elements_distinguishes_duplicate_call_sites_by_runtime_slot() -> None:
    loop_slot_a = SlotId(_MODULE_ID, 7, key_path=("row-1",), line_no=20)
    loop_slot_b = SlotId(_MODULE_ID, 7, key_path=("row-2",), line_no=20)
    specs = normalize_ui_elements(
        _OWNER_SLOT,
        (
            UIElement(
                kind="badge",
                props={"text": "A", "visible": True},
                call_site_id=11,
                slot_id=loop_slot_a,
            ),
            UIElement(
                kind="badge",
                props={"text": "B", "visible": True},
                call_site_id=11,
                slot_id=loop_slot_b,
            ),
        ),
    )

    assert specs[0].node_id != specs[1].node_id


def test_normalize_ui_elements_distinguishes_duplicate_call_sites_by_slot_path() -> None:
    boundary_slot_a = SlotId(_MODULE_ID, 8, key_path=("counter-a",), line_no=30)
    boundary_slot_b = SlotId(_MODULE_ID, 8, key_path=("counter-b",), line_no=30)
    local_emit_slot = SlotId(_MODULE_ID, 1, key_path=(), line_no=31)
    specs = normalize_ui_elements(
        _OWNER_SLOT,
        (
            UIElement(
                kind="badge",
                props={"text": "A", "visible": True},
                call_site_id=3,
                slot_id=(boundary_slot_a, local_emit_slot),
            ),
            UIElement(
                kind="badge",
                props={"text": "B", "visible": True},
                call_site_id=3,
                slot_id=(boundary_slot_b, local_emit_slot),
            ),
        ),
    )

    assert specs[0].node_id != specs[1].node_id
