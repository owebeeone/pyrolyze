from __future__ import annotations

import os
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QGroupBox, QLabel, QLineEdit, QPushButton

from pyrolyze.api import UIElement
from pyrolyze.pyrolyze_pyside6 import (
    PyrolyzeWindow,
    create_window,
    render_ui_element,
    render_semantic_node,
    render_widget_binding,
    set_window_content,
)


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
