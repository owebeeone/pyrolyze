from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from frozendict import frozendict
import pytest

pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtWidgets import QApplication, QPushButton, QSpinBox, QWidget

from pyrolyze.api import UIElement
from pyrolyze.backends.model import ChildPolicy, FillPolicy, MethodMode, TypeRef, UiMethodSpec, UiParamSpec, UiPropSpec, UiWidgetSpec
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


class _FakeRangeWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.range_calls: list[tuple[int, int]] = []

    def setRange(self, minimum: int, maximum: int) -> None:
        self.range_calls.append((minimum, maximum))


def test_method_specs_drive_grouped_updates_with_retained_effective_values(qapp: QApplication) -> None:
    del qapp
    fake_spec = UiWidgetSpec(
        kind="FakeRange",
        mounted_type_name="tests.fake.FakeRangeWidget",
        constructor_params=frozendict(),
        props=frozendict(
            {
                "minimum": UiPropSpec(name="minimum", annotation=TypeRef("int"), mode=PySide6UiLibrary.WIDGET_SPECS["QSpinBox"].props["minimum"].mode),
                "maximum": UiPropSpec(name="maximum", annotation=TypeRef("int"), mode=PySide6UiLibrary.WIDGET_SPECS["QSpinBox"].props["maximum"].mode),
            }
        ),
        methods=frozendict(
            {
                "setRange": UiMethodSpec(
                    name="setRange",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="minimum", annotation=TypeRef("int")),
                        UiParamSpec(name="maximum", annotation=TypeRef("int")),
                    ),
                    source_props=("minimum", "maximum"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=True,
                ),
            }
        ),
        child_policy=ChildPolicy.NONE,
    )
    engine = PySide6WidgetEngine({"FakeRange": fake_spec})
    engine._widget_types[fake_spec.mounted_type_name] = _FakeRangeWidget

    node = engine.mount(
        UIElement(kind="FakeRange", props={"minimum": 1, "maximum": 10}),
        slot_id=("root", "range", 1),
        call_site_id=23,
    )

    assert isinstance(node.widget, _FakeRangeWidget)
    assert node.widget.range_calls == [(1, 10)]

    updated = engine.update(
        node,
        UIElement(kind="FakeRange", props={"maximum": 12}),
    )

    assert updated is node
    assert updated.widget.range_calls == [(1, 10), (1, 12)]
    assert updated.effective_props == {"minimum": 1, "maximum": 12}


def test_generated_qspinbox_uses_learned_range_method_for_partial_updates(qapp: QApplication) -> None:
    del qapp
    engine = PySide6WidgetEngine(PySide6UiLibrary.WIDGET_SPECS)
    node = engine.mount(
        PySide6UiLibrary.UI_INTERFACE.build_element(
            "CQSpinBox",
            minimum=1,
            maximum=10,
            value=4,
        ),
        slot_id=("root", "spin", 1),
        call_site_id=31,
    )
    original_widget = node.widget

    assert isinstance(node.widget, QSpinBox)
    assert node.widget.minimum() == 1
    assert node.widget.maximum() == 10

    updated = engine.update(
        node,
        PySide6UiLibrary.UI_INTERFACE.build_element(
            "CQSpinBox",
            maximum=12,
        ),
    )

    assert updated is node
    assert updated.widget is original_widget
    assert updated.widget.minimum() == 1
    assert updated.widget.maximum() == 12
    assert updated.effective_props["minimum"] == 1
    assert updated.effective_props["maximum"] == 12
