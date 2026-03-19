from __future__ import annotations

from dataclasses import dataclass

import pytest

from pyrolyze.api import UIElement
from pyrolyze.pyrolyze_tkinter import (
    create_window,
    reconcile_window_content,
    render_ui_element,
    render_semantic_node,
    tkinter_available,
)


@dataclass(frozen=True)
class _SlotRef:
    owner: str
    slot_kind: str
    index: int


def _semantic_badge(*, owner: str, index: int, text: str) -> dict[str, object]:
    return {
        "kind": "badge",
        "slot_id": _SlotRef(owner=owner, slot_kind="widget", index=index),
        "values": {"text": text, "tone": "info"},
    }


def _semantic_button(*, owner: str, index: int, label: str) -> dict[str, object]:
    return {
        "kind": "button",
        "slot_id": _SlotRef(owner=owner, slot_kind="widget", index=index),
        "values": {"label": label, "enabled": True, "tone": "default"},
    }


def test_tkinter_available_reports_host_support_as_bool() -> None:
    assert isinstance(tkinter_available(), bool)


@pytest.mark.skipif(not tkinter_available(), reason="Tk root unavailable in this environment")
def test_render_ui_element_builds_tk_button_from_frozen_v1_schema() -> None:
    widget = render_ui_element(
        UIElement(
            kind="button",
            props={"label": "Run", "enabled": False, "visible": True},
        )
    )

    assert str(widget.cget("text")) == "Run"
    assert str(widget.cget("state")) == "disabled"


@pytest.mark.skipif(not tkinter_available(), reason="Tk root unavailable in this environment")
def test_render_semantic_node_builds_tk_select_field_widget() -> None:
    widget = render_semantic_node(
        {
            "kind": "select_field",
            "field_id": "location",
            "slot_id": _SlotRef(owner="weather", slot_kind="widget", index=1),
            "values": {
                "label": "Location",
                "value": "Berlin",
                "options": ("Berlin", "Paris"),
                "enabled": True,
            },
        }
    )

    combo = next(
        child for child in widget.winfo_children() if child.winfo_class() in {"TCombobox", "Combobox"}
    )

    assert str(combo.get()) == "Berlin"
    assert tuple(combo.cget("values")) == ("Berlin", "Paris")


@pytest.mark.skipif(not tkinter_available(), reason="Tk root unavailable in this environment")
def test_reconcile_window_content_updates_badge_in_place() -> None:
    host = create_window("Retained Badge")

    reconcile_window_content(host, [_semantic_badge(owner="root", index=1, text="One")])
    first_widget = host.content_frame.winfo_children()[0]

    reconcile_window_content(host, [_semantic_badge(owner="root", index=1, text="Two")])
    second_widget = host.content_frame.winfo_children()[0]

    assert second_widget is first_widget
    assert str(second_widget.cget("text")) == "Two"

    host.close()


@pytest.mark.skipif(not tkinter_available(), reason="Tk root unavailable in this environment")
def test_reconcile_window_content_reorders_reused_widgets() -> None:
    host = create_window("Retained Reorder")
    first_nodes = [
        _semantic_button(owner="root", index=1, label="One"),
        _semantic_button(owner="root", index=2, label="Two"),
    ]

    reconcile_window_content(host, first_nodes)
    first_widget, second_widget = tuple(host.content_frame.pack_slaves())

    reconcile_window_content(host, list(reversed(first_nodes)))

    assert tuple(host.content_frame.pack_slaves()) == (second_widget, first_widget)

    host.close()
