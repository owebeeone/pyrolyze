from __future__ import annotations

import os
from dataclasses import dataclass
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QComboBox, QGroupBox, QLabel, QLineEdit, QPushButton

from pyrolyze.api import UIElement
from pyrolyze.pyrolyze_pyside6 import (
    PyrolyzeWindow,
    create_window,
    reconcile_window_content,
    render_ui_element,
    render_semantic_node,
    render_widget_binding,
    set_window_content,
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


def test_create_window_builds_reusable_window_host() -> None:
    host = create_window("PyRolyze Demo")

    assert isinstance(host, PyrolyzeWindow)
    assert host.window.windowTitle() == "PyRolyze Demo"
    assert host.content_layout.count() == 0

    host.close()


def test_render_semantic_node_builds_nested_section_widgets() -> None:
    widget = render_semantic_node(
        {
            "kind": "section",
            "values": {"title": "Account Settings", "accent": "blue"},
            "children": (
                {
                    "kind": "badge",
                    "values": {"text": "Ready to save", "tone": "success"},
                },
            ),
        }
    )

    assert isinstance(widget, QGroupBox)
    assert widget.title() == "Account Settings"
    assert widget.findChild(QLabel).text() == "Ready to save"


def test_render_ui_element_builds_widgets_from_frozen_v1_schema() -> None:
    widget = render_ui_element(
        UIElement(
            kind="section",
            props={"title": "Account Settings", "accent": "blue", "visible": True},
            children=(
                UIElement(
                    kind="badge",
                    props={"text": "Ready to save", "tone": "success", "visible": True},
                ),
                UIElement(
                    kind="button",
                    props={"label": "Run", "enabled": False, "visible": True},
                ),
            ),
        )
    )

    assert isinstance(widget, QGroupBox)
    assert widget.title() == "Account Settings"
    labels = widget.findChildren(QLabel)
    assert any(label.text() == "Ready to save" for label in labels)
    buttons = widget.findChildren(QPushButton)
    assert len(buttons) == 1
    assert buttons[0].text() == "Run"
    assert buttons[0].isEnabled() is False


def test_render_ui_element_wires_text_field_change_events() -> None:
    calls: list[object] = []

    widget = render_ui_element(
        UIElement(
            kind="text_field",
            props={
                "field_id": "focus-filter",
                "label": "Focus Filter",
                "value": "cache",
                "on_change": lambda value: calls.append(value),
                "enabled": True,
                "visible": True,
            },
        ),
        on_after_event=lambda: calls.append("rerender"),
    )

    line_edit = widget.findChild(QLineEdit)

    assert line_edit is not None
    line_edit.setText("queue")

    assert calls == ["queue", "rerender"]


def test_render_widget_binding_wires_text_changed_events() -> None:
    calls: list[object] = []
    binding = SimpleNamespace(
        runtime_kind="TextField",
        properties={
            "field_id": "focus-filter",
            "label": "Focus Filter",
            "value": "cache",
        },
        events={
            "textChanged": SimpleNamespace(
                callback=lambda value: calls.append(value),
            )
        },
    )

    widget = render_widget_binding(binding, on_after_event=lambda: calls.append("rerender"))
    line_edit = widget.findChild(QLineEdit)

    assert line_edit is not None
    line_edit.setText("queue")

    assert calls == ["queue", "rerender"]


def test_set_window_content_replaces_previous_widgets() -> None:
    host = create_window("Replace Content")

    set_window_content(host, [render_semantic_node({"kind": "badge", "values": {"text": "One", "tone": "info"}})])
    assert host.content_layout.count() == 1

    set_window_content(host, [render_semantic_node({"kind": "badge", "values": {"text": "Two", "tone": "info"}})])
    assert host.content_layout.count() == 1
    assert host.content_layout.itemAt(0).widget().findChild(QLabel) is None

    host.close()


def test_render_semantic_node_builds_select_field_widget() -> None:
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

    combo = widget.findChild(QComboBox)

    assert combo is not None
    assert combo.currentText() == "Berlin"
    assert combo.count() == 2


def test_reconcile_window_content_updates_badge_in_place() -> None:
    host = create_window("Retained Badge")

    reconcile_window_content(host, [_semantic_badge(owner="root", index=1, text="One")])
    first_widget = host.content_layout.itemAt(0).widget()

    reconcile_window_content(host, [_semantic_badge(owner="root", index=1, text="Two")])
    second_widget = host.content_layout.itemAt(0).widget()

    assert second_widget is first_widget
    assert isinstance(second_widget, QLabel)
    assert second_widget.text() == "Two"

    host.close()


def test_reconcile_window_content_reorders_reused_widgets() -> None:
    host = create_window("Retained Reorder")
    first_nodes = [
        _semantic_button(owner="root", index=1, label="One"),
        _semantic_button(owner="root", index=2, label="Two"),
    ]

    reconcile_window_content(host, first_nodes)
    first_widget = host.content_layout.itemAt(0).widget()
    second_widget = host.content_layout.itemAt(1).widget()

    reconcile_window_content(host, list(reversed(first_nodes)))

    assert host.content_layout.itemAt(0).widget() is second_widget
    assert host.content_layout.itemAt(1).widget() is first_widget

    host.close()
