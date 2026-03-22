from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from frozendict import frozendict
import pytest

pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtWidgets import QApplication, QBoxLayout, QFormLayout, QMainWindow, QMenuBar, QPushButton, QSpinBox, QWidget

from pyrolyze.api import MISSING, MountDirective, UIElement
from pyrolyze.backends.model import ChildPolicy, FillPolicy, MethodMode, TypeRef, UiMethodSpec, UiParamSpec, UiPropSpec, UiWidgetSpec
from pyrolyze.backends.pyside6.engine import MountedWidgetNode, PySide6WidgetEngine, WidgetNodeKey
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    return QApplication.instance() or QApplication([])


class _BrokenQtPropertyWidget(QWidget):
    def property(self, name: str):  # type: ignore[override]
        raise RuntimeError(f"cannot convert {name}")


def test_read_current_prop_value_returns_missing_when_qt_property_read_raises(qapp: QApplication) -> None:
    del qapp
    engine = PySide6WidgetEngine(PySide6UiLibrary.WIDGET_SPECS)

    value = engine._read_current_prop_value(
        _BrokenQtPropertyWidget(),
        PySide6UiLibrary.WIDGET_SPECS["QWidget"],
        "contextMenuPolicy",
    )

    assert value is MISSING


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


def test_mount_infers_default_layout_mount_from_generated_children(qapp: QApplication) -> None:
    del qapp
    engine = PySide6WidgetEngine(PySide6UiLibrary.WIDGET_SPECS)
    assert PySide6UiLibrary.WIDGET_SPECS["QWidget"].default_child_mount_point_name == "layout"

    node = engine.mount(
        UIElement(
            kind="QWidget",
            props={"objectName": "root"},
            children=(
                UIElement(
                    kind="QBoxLayout",
                    props={"arg__1": QBoxLayout.Direction.TopToBottom},
                    children=(
                        UIElement(
                            kind="QPushButton",
                            props={"text": "Save"},
                        ),
                    ),
                ),
            ),
        ),
        slot_id=("root", "widget", 1),
        call_site_id=41,
    )

    assert isinstance(node.widget, QWidget)
    layout = node.widget.layout()
    assert isinstance(layout, QBoxLayout)
    assert layout.count() == 1
    item = layout.itemAt(0)
    assert item is not None
    child_widget = item.widget()
    assert isinstance(child_widget, QPushButton)
    assert child_widget.text() == "Save"


def test_update_preserves_layout_and_sibling_widgets_when_leaf_prop_changes(qapp: QApplication) -> None:
    del qapp
    engine = PySide6WidgetEngine(PySide6UiLibrary.WIDGET_SPECS)
    node = engine.mount(
        UIElement(
            kind="QWidget",
            props={"objectName": "root"},
            children=(
                UIElement(
                    kind="QBoxLayout",
                    props={"arg__1": QBoxLayout.Direction.TopToBottom},
                    children=(
                        UIElement(kind="QPushButton", props={"text": "Keep"}),
                        UIElement(kind="QPushButton", props={"text": "Change"}),
                    ),
                ),
            ),
        ),
        slot_id=("root", "widget", 3),
        call_site_id=43,
    )

    assert node._mountable_node is not None
    layout_node = node._mountable_node.child_nodes[0]
    first_button_node = layout_node.child_nodes[0]
    second_button_node = layout_node.child_nodes[1]
    original_layout = layout_node.mountable
    original_first_button = first_button_node.mountable
    original_second_button = second_button_node.mountable

    updated = engine.update(
        node,
        UIElement(
            kind="QWidget",
            props={"objectName": "root"},
            children=(
                UIElement(
                    kind="QBoxLayout",
                    props={"arg__1": QBoxLayout.Direction.TopToBottom},
                    children=(
                        UIElement(kind="QPushButton", props={"text": "Keep"}),
                        UIElement(kind="QPushButton", props={"text": "Changed"}),
                    ),
                ),
            ),
        ),
    )

    assert updated is node
    assert node._mountable_node is not None
    assert node._mountable_node.child_nodes[0].mountable is original_layout
    assert node._mountable_node.child_nodes[0].child_nodes[0].mountable is original_first_button
    assert node._mountable_node.child_nodes[0].child_nodes[1].mountable is original_second_button
    changed_button = node._mountable_node.child_nodes[0].child_nodes[1].mountable
    assert isinstance(changed_button, QPushButton)
    assert changed_button.text() == "Changed"


def test_mount_raises_when_unspecified_child_has_no_compatible_default_attach_path(qapp: QApplication) -> None:
    del qapp
    engine = PySide6WidgetEngine(PySide6UiLibrary.WIDGET_SPECS)

    with pytest.raises(ValueError) as excinfo:
        engine.mount(
            UIElement(
                kind="QWidget",
                props={"objectName": "root"},
                children=(
                    UIElement(
                        kind="QPushButton",
                        props={"text": "Save"},
                    ),
                ),
            ),
            slot_id=("root", "widget", 2),
            call_site_id=42,
        )

    message = str(excinfo.value)
    assert "Cannot attach child kind 'QPushButton' to parent 'QWidget'" in message
    assert "Default attach mount points" in message
    assert "layout" in message
    assert "PySide6.QtWidgets.QLayout" in message


def test_mount_error_explains_when_explicit_mount_is_required(qapp: QApplication) -> None:
    del qapp
    engine = PySide6WidgetEngine(PySide6UiLibrary.WIDGET_SPECS)

    with pytest.raises(ValueError) as excinfo:
        engine.mount(
            UIElement(
                kind="QFormLayout",
                props={},
                children=(
                    UIElement(
                        kind="QPushButton",
                        props={"text": "Save"},
                    ),
                ),
            ),
            slot_id=("root", "form", 1),
            call_site_id=44,
        )

    message = str(excinfo.value)
    assert "Cannot attach child kind 'QPushButton' to parent 'QFormLayout'" in message
    assert "explicit mount is required" in message
    assert "widget" in message
    assert "row" in message
    assert "role" in message


def test_mount_infers_default_main_window_mounts_from_generated_children(qapp: QApplication) -> None:
    del qapp
    engine = PySide6WidgetEngine(PySide6UiLibrary.WIDGET_SPECS)

    node = engine.mount(
        UIElement(
            kind="QMainWindow",
            props={"windowTitle": "Workspace"},
            children=(
                UIElement(
                    kind="QMenuBar",
                    props={"objectName": "main-menu"},
                ),
                UIElement(
                    kind="QWidget",
                    props={"objectName": "central"},
                ),
            ),
        ),
        slot_id=("root", "window", 1),
        call_site_id=43,
    )

    assert isinstance(node.widget, QMainWindow)
    menu_bar = node.widget.menuBar()
    assert isinstance(menu_bar, QMenuBar)
    assert menu_bar.objectName() == "main-menu"
    central = node.widget.centralWidget()
    assert isinstance(central, QWidget)
    assert central.objectName() == "central"


def test_mount_honors_explicit_generated_menu_bar_selector(qapp: QApplication) -> None:
    del qapp
    engine = PySide6WidgetEngine(PySide6UiLibrary.WIDGET_SPECS)

    node = engine.mount(
        UIElement(
            kind="QMainWindow",
            props={"windowTitle": "Workspace"},
            children=(
                MountDirective(
                    selectors=(PySide6UiLibrary.mounts.menu_bar,),
                    children=(
                        UIElement(
                            kind="QMenuBar",
                            props={"objectName": "main-menu"},
                        ),
                    ),
                ),
                UIElement(
                    kind="QWidget",
                    props={"objectName": "central"},
                ),
            ),
        ),
        slot_id=("root", "window", 9),
        call_site_id=49,
    )

    assert isinstance(node.widget, QMainWindow)
    menu_bar = node.widget.menuBar()
    assert isinstance(menu_bar, QMenuBar)
    assert menu_bar.objectName() == "main-menu"
    central = node.widget.centralWidget()
    assert isinstance(central, QWidget)
    assert central.objectName() == "central"


def test_update_detaches_removed_default_main_window_mounts(qapp: QApplication) -> None:
    del qapp
    engine = PySide6WidgetEngine(PySide6UiLibrary.WIDGET_SPECS)

    node = engine.mount(
        UIElement(
            kind="QMainWindow",
            props={"windowTitle": "Workspace"},
            children=(
                UIElement(
                    kind="QMenuBar",
                    props={"objectName": "main-menu"},
                ),
                UIElement(
                    kind="QWidget",
                    props={"objectName": "central"},
                ),
            ),
        ),
        slot_id=("root", "window", 2),
        call_site_id=44,
    )

    assert isinstance(node.widget, QMainWindow)
    original_menu_bar = node.widget.menuBar()
    assert isinstance(original_menu_bar, QMenuBar)
    assert isinstance(node.widget.centralWidget(), QWidget)

    engine.update(
        node,
        UIElement(
            kind="QMainWindow",
            props={"windowTitle": "Workspace"},
            children=(),
        ),
    )

    assert node.widget.centralWidget() is None
    replacement_menu_bar = node.widget.menuBar()
    assert replacement_menu_bar is not original_menu_bar
    assert replacement_menu_bar.objectName() != "main-menu"
