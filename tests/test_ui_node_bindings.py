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
    assert button.props == {"label": "Run", "enabled": False, "visible": True}
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
    assert text_field.event_props == {"on_change": on_change}


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
