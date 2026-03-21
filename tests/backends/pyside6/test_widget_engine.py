from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from pyrolyze.backends.pyside6.engine import MountedWidgetNode, PySide6WidgetEngine, WidgetNodeKey
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_mount_builds_widget_from_generated_uielement(qapp: QApplication) -> None:
    del qapp
    engine = PySide6WidgetEngine(PySide6UiLibrary.WIDGET_SPECS)
    element = PySide6UiLibrary.UI_INTERFACE.build_element(
        "CQPushButton",
        text="Save",
        flat=True,
        enabled=False,
    )

    node = engine.mount(element, slot_id=("root", "button", 1), call_site_id=17)

    assert isinstance(node, MountedWidgetNode)
    assert node.key == WidgetNodeKey(slot_id=("root", "button", 1), call_site_id=17, kind="QPushButton")
    assert isinstance(node.widget, QPushButton)
    assert node.widget.text() == "Save"
    assert node.widget.isFlat() is True
    assert node.widget.isEnabled() is False
    assert node.effective_props == {"text": "Save", "flat": True, "enabled": False}


def test_update_reuses_widget_and_retains_omitted_effective_props(qapp: QApplication) -> None:
    del qapp
    engine = PySide6WidgetEngine(PySide6UiLibrary.WIDGET_SPECS)
    node = engine.mount(
        PySide6UiLibrary.UI_INTERFACE.build_element(
            "CQPushButton",
            text="Save",
            flat=True,
            enabled=False,
        ),
        slot_id=("root", "button", 1),
        call_site_id=17,
    )
    original_widget = node.widget

    updated = engine.update(
        node,
        PySide6UiLibrary.UI_INTERFACE.build_element(
            "CQPushButton",
            text="Run",
        ),
    )

    assert updated is node
    assert updated.widget is original_widget
    assert updated.widget.text() == "Run"
    assert updated.widget.isFlat() is True
    assert updated.widget.isEnabled() is False
    assert updated.effective_props == {"text": "Run", "flat": True, "enabled": False}


def test_update_remounts_when_create_only_remount_prop_changes(qapp: QApplication) -> None:
    del qapp
    engine = PySide6WidgetEngine(PySide6UiLibrary.WIDGET_SPECS)
    parent_a = QWidget()
    parent_b = QWidget()
    node = engine.mount(
        PySide6UiLibrary.UI_INTERFACE.build_element(
            "CQPushButton",
            text="Save",
            parent=parent_a,
        ),
        slot_id=("root", "button", 1),
        call_site_id=17,
    )
    original_widget = node.widget

    updated = engine.update(
        node,
        PySide6UiLibrary.UI_INTERFACE.build_element(
            "CQPushButton",
            text="Save",
            parent=parent_b,
        ),
    )

    assert updated is node
    assert updated.key == WidgetNodeKey(slot_id=("root", "button", 1), call_site_id=17, kind="QPushButton")
    assert updated.widget is not original_widget
    assert updated.widget.parentWidget() is parent_b
    assert updated.effective_props == {"text": "Save", "parent": parent_b}
