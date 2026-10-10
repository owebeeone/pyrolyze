#@pyrolyze

"""Generated UI interface stubs for discovered widgets."""

from __future__ import annotations

import PySide6

from typing import Any, ClassVar

from frozendict import frozendict

from pyrolyze.api import MISSING, MissingType, MountSelector, PyrolyzeHandler, UIElement, call_native, pyrolyze, ui_interface
from pyrolyze.backends.model import (
    AccessorKind,
    ChildPolicy,
    EventPayloadPolicy,
    FillPolicy,
    MethodMode,
    MountReplayKind,
    MountParamSpec,
    MountPointSpec,
    PropMode,
    TypeRef,
    UiEventSpec,
    UiInterface,
    UiInterfaceEntry,
    UiMethodSpec,
    UiParamSpec,
    UiPropSpec,
    UiWidgetSpec,
)


@ui_interface
class PySide6UiLibrary:
    ROOT_MODULE: ClassVar[str] = "PySide6"

    UI_INTERFACE: ClassVar[UiInterface] = UiInterface(
        name="PySide6UiLibrary",
        owner=None,
        entries=frozendict({
            "CQBoxLayout": UiInterfaceEntry(public_name="CQBoxLayout", kind="QBoxLayout"),
            "CQFormLayout": UiInterfaceEntry(public_name="CQFormLayout", kind="QFormLayout"),
            "CQGridLayout": UiInterfaceEntry(public_name="CQGridLayout", kind="QGridLayout"),
            "CQHBoxLayout": UiInterfaceEntry(public_name="CQHBoxLayout", kind="QHBoxLayout"),
        }),
    )

    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({
        'QBoxLayout': UiWidgetSpec(
            kind="QBoxLayout",
            mounted_type_name="PySide6.QtWidgets.QBoxLayout",
            constructor_params=frozendict({
                "arg__1": UiParamSpec(name="arg__1", annotation=TypeRef(expr='PySide6.QtWidgets.QBoxLayout.Direction'), default_repr=None),
                "parent": UiParamSpec(name="parent", annotation=TypeRef(expr='PySide6.QtWidgets.QWidget | None'), default_repr='...'),
            }),
            props=frozendict({
                "arg__1": UiPropSpec(name="arg__1", annotation=TypeRef(expr='PySide6.QtWidgets.QBoxLayout.Direction'), mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='arg__1', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "parent": UiPropSpec(name="parent", annotation=TypeRef(expr='PySide6.QtWidgets.QWidget | None'), mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='parent', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "contentsMargins": UiPropSpec(name="contentsMargins", annotation=TypeRef(expr='QMargins'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "horizontalSizeConstraint": UiPropSpec(name="horizontalSizeConstraint", annotation=TypeRef(expr='QLayout::SizeConstraint'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "objectName": UiPropSpec(name="objectName", annotation=TypeRef(expr='QString'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "sizeConstraint": UiPropSpec(name="sizeConstraint", annotation=TypeRef(expr='QLayout::SizeConstraint'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "spacing": UiPropSpec(name="spacing", annotation=TypeRef(expr='int'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "verticalSizeConstraint": UiPropSpec(name="verticalSizeConstraint", annotation=TypeRef(expr='QLayout::SizeConstraint'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
            }),
            methods=frozendict({
                "setAlignment": UiMethodSpec(
                    name="setAlignment",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="alignment", annotation=TypeRef(expr='PySide6.QtCore.Qt.AlignmentFlag'), default_repr=None),
                    ),
                    source_props=("alignment",),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setContentsMargins": UiMethodSpec(
                    name="setContentsMargins",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="left", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="top", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="right", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="bottom", annotation=TypeRef(expr='int'), default_repr=None),
                    ),
                    source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setStretch": UiMethodSpec(
                    name="setStretch",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="index", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="stretch", annotation=TypeRef(expr='int'), default_repr=None),
                    ),
                    source_props=("stretch_index", "stretch_stretch"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            events=frozendict({
            }),
            mount_points=frozendict({
                "layout": MountPointSpec(
                    name="layout",
                    accepted_produced_type=TypeRef(expr='PySide6.QtWidgets.QLayout'),
                    params=(
                        MountParamSpec(name="stretch", annotation=TypeRef(expr='int | None'), keyed=False, default_repr='...'),
                    ),
                    min_children=0,
                    max_children=None,
                    apply_method_name=None,
                    sync_method_name=None,
                    place_method_name='insertLayout',
                    append_method_name='addLayout',
                    detach_method_name='removeItem',
                    replay_kind=MountReplayKind.INDEX,
                    prefer_sync=False,
                ),
                "menu_bar": MountPointSpec(
                    name="menu_bar",
                    accepted_produced_type=TypeRef(expr='PySide6.QtWidgets.QMenuBar'),
                    params=(
                    ),
                    min_children=0,
                    max_children=1,
                    apply_method_name='setMenuBar',
                    sync_method_name=None,
                    place_method_name=None,
                    append_method_name=None,
                    detach_method_name=None,
                    replay_kind=MountReplayKind.NONE,
                    prefer_sync=False,
                ),
                "widget": MountPointSpec(
                    name="widget",
                    accepted_produced_type=TypeRef(expr='PySide6.QtWidgets.QWidget'),
                    params=(
                        MountParamSpec(name="stretch", annotation=TypeRef(expr='int | None'), keyed=False, default_repr='...'),
                        MountParamSpec(name="alignment", annotation=TypeRef(expr='PySide6.QtCore.Qt.AlignmentFlag'), keyed=False, default_repr='...'),
                    ),
                    min_children=0,
                    max_children=None,
                    apply_method_name=None,
                    sync_method_name=None,
                    place_method_name='insertWidget',
                    append_method_name='addWidget',
                    detach_method_name='removeWidget',
                    replay_kind=MountReplayKind.INDEX,
                    prefer_sync=False,
                ),
            }),
            default_child_mount_point_name='layout',
            default_attach_mount_point_names=('menu_bar', 'widget', 'layout'),
            child_policy=ChildPolicy.NONE,
        ),
        'QFormLayout': UiWidgetSpec(
            kind="QFormLayout",
            mounted_type_name="PySide6.QtWidgets.QFormLayout",
            constructor_params=frozendict({
                "parent": UiParamSpec(name="parent", annotation=TypeRef(expr='PySide6.QtWidgets.QWidget | None'), default_repr='...'),
                "fieldGrowthPolicy": UiParamSpec(name="fieldGrowthPolicy", annotation=TypeRef(expr='PySide6.QtWidgets.QFormLayout.FieldGrowthPolicy | None'), default_repr='...'),
                "rowWrapPolicy": UiParamSpec(name="rowWrapPolicy", annotation=TypeRef(expr='PySide6.QtWidgets.QFormLayout.RowWrapPolicy | None'), default_repr='...'),
                "labelAlignment": UiParamSpec(name="labelAlignment", annotation=TypeRef(expr='PySide6.QtCore.Qt.AlignmentFlag | None'), default_repr='...'),
                "formAlignment": UiParamSpec(name="formAlignment", annotation=TypeRef(expr='PySide6.QtCore.Qt.AlignmentFlag | None'), default_repr='...'),
                "horizontalSpacing": UiParamSpec(name="horizontalSpacing", annotation=TypeRef(expr='int | None'), default_repr='...'),
                "verticalSpacing": UiParamSpec(name="verticalSpacing", annotation=TypeRef(expr='int | None'), default_repr='...'),
            }),
            props=frozendict({
                "parent": UiPropSpec(name="parent", annotation=TypeRef(expr='PySide6.QtWidgets.QWidget | None'), mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='parent', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "fieldGrowthPolicy": UiPropSpec(name="fieldGrowthPolicy", annotation=TypeRef(expr='PySide6.QtWidgets.QFormLayout.FieldGrowthPolicy | None'), mode=PropMode.CREATE_UPDATE, constructor_name='fieldGrowthPolicy', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "rowWrapPolicy": UiPropSpec(name="rowWrapPolicy", annotation=TypeRef(expr='PySide6.QtWidgets.QFormLayout.RowWrapPolicy | None'), mode=PropMode.CREATE_UPDATE, constructor_name='rowWrapPolicy', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "labelAlignment": UiPropSpec(name="labelAlignment", annotation=TypeRef(expr='PySide6.QtCore.Qt.AlignmentFlag | None'), mode=PropMode.CREATE_UPDATE, constructor_name='labelAlignment', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "formAlignment": UiPropSpec(name="formAlignment", annotation=TypeRef(expr='PySide6.QtCore.Qt.AlignmentFlag | None'), mode=PropMode.CREATE_UPDATE, constructor_name='formAlignment', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "horizontalSpacing": UiPropSpec(name="horizontalSpacing", annotation=TypeRef(expr='int | None'), mode=PropMode.CREATE_UPDATE, constructor_name='horizontalSpacing', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "verticalSpacing": UiPropSpec(name="verticalSpacing", annotation=TypeRef(expr='int | None'), mode=PropMode.CREATE_UPDATE, constructor_name='verticalSpacing', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "contentsMargins": UiPropSpec(name="contentsMargins", annotation=TypeRef(expr='QMargins'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "horizontalSizeConstraint": UiPropSpec(name="horizontalSizeConstraint", annotation=TypeRef(expr='QLayout::SizeConstraint'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "objectName": UiPropSpec(name="objectName", annotation=TypeRef(expr='QString'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "sizeConstraint": UiPropSpec(name="sizeConstraint", annotation=TypeRef(expr='QLayout::SizeConstraint'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "spacing": UiPropSpec(name="spacing", annotation=TypeRef(expr='int'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "verticalSizeConstraint": UiPropSpec(name="verticalSizeConstraint", annotation=TypeRef(expr='QLayout::SizeConstraint'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
            }),
            methods=frozendict({
                "setAlignment": UiMethodSpec(
                    name="setAlignment",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="alignment", annotation=TypeRef(expr='PySide6.QtCore.Qt.AlignmentFlag'), default_repr=None),
                    ),
                    source_props=("alignment",),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setContentsMargins": UiMethodSpec(
                    name="setContentsMargins",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="left", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="top", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="right", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="bottom", annotation=TypeRef(expr='int'), default_repr=None),
                    ),
                    source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setGeometry": UiMethodSpec(
                    name="setGeometry",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="rect", annotation=TypeRef(expr='PySide6.QtCore.QRect'), default_repr=None),
                    ),
                    source_props=("geometry",),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setRowVisible": UiMethodSpec(
                    name="setRowVisible",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="row", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="on", annotation=TypeRef(expr='bool'), default_repr=None),
                    ),
                    source_props=("row_visible_row", "row_visible_on"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            events=frozendict({
            }),
            mount_points=frozendict({
                "layout": MountPointSpec(
                    name="layout",
                    accepted_produced_type=TypeRef(expr='PySide6.QtWidgets.QLayout'),
                    params=(
                        MountParamSpec(name="row", annotation=TypeRef(expr='int'), keyed=True, default_repr=None),
                        MountParamSpec(name="role", annotation=TypeRef(expr='PySide6.QtWidgets.QFormLayout.ItemRole'), keyed=True, default_repr=None),
                    ),
                    min_children=0,
                    max_children=1,
                    apply_method_name='setLayout',
                    sync_method_name=None,
                    place_method_name=None,
                    append_method_name=None,
                    detach_method_name=None,
                    replay_kind=MountReplayKind.NONE,
                    prefer_sync=False,
                ),
                "menu_bar": MountPointSpec(
                    name="menu_bar",
                    accepted_produced_type=TypeRef(expr='PySide6.QtWidgets.QMenuBar'),
                    params=(
                    ),
                    min_children=0,
                    max_children=1,
                    apply_method_name='setMenuBar',
                    sync_method_name=None,
                    place_method_name=None,
                    append_method_name=None,
                    detach_method_name=None,
                    replay_kind=MountReplayKind.NONE,
                    prefer_sync=False,
                ),
                "widget": MountPointSpec(
                    name="widget",
                    accepted_produced_type=TypeRef(expr='PySide6.QtWidgets.QWidget'),
                    params=(
                        MountParamSpec(name="row", annotation=TypeRef(expr='int'), keyed=True, default_repr=None),
                        MountParamSpec(name="role", annotation=TypeRef(expr='PySide6.QtWidgets.QFormLayout.ItemRole'), keyed=True, default_repr=None),
                    ),
                    min_children=0,
                    max_children=1,
                    apply_method_name='setWidget',
                    sync_method_name=None,
                    place_method_name=None,
                    append_method_name=None,
                    detach_method_name=None,
                    replay_kind=MountReplayKind.NONE,
                    prefer_sync=False,
                ),
            }),
            default_child_mount_point_name='layout',
            default_attach_mount_point_names=('menu_bar',),
            child_policy=ChildPolicy.NONE,
        ),
        'QGridLayout': UiWidgetSpec(
            kind="QGridLayout",
            mounted_type_name="PySide6.QtWidgets.QGridLayout",
            constructor_params=frozendict({
                "parent": UiParamSpec(name="parent", annotation=TypeRef(expr='PySide6.QtWidgets.QWidget | None'), default_repr='...'),
            }),
            props=frozendict({
                "parent": UiPropSpec(name="parent", annotation=TypeRef(expr='PySide6.QtWidgets.QWidget | None'), mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='parent', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "contentsMargins": UiPropSpec(name="contentsMargins", annotation=TypeRef(expr='QMargins'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "horizontalSizeConstraint": UiPropSpec(name="horizontalSizeConstraint", annotation=TypeRef(expr='QLayout::SizeConstraint'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "objectName": UiPropSpec(name="objectName", annotation=TypeRef(expr='QString'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "sizeConstraint": UiPropSpec(name="sizeConstraint", annotation=TypeRef(expr='QLayout::SizeConstraint'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "spacing": UiPropSpec(name="spacing", annotation=TypeRef(expr='int'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "verticalSizeConstraint": UiPropSpec(name="verticalSizeConstraint", annotation=TypeRef(expr='QLayout::SizeConstraint'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
            }),
            methods=frozendict({
                "setAlignment": UiMethodSpec(
                    name="setAlignment",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="alignment", annotation=TypeRef(expr='PySide6.QtCore.Qt.AlignmentFlag'), default_repr=None),
                    ),
                    source_props=("alignment",),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setColumnMinimumWidth": UiMethodSpec(
                    name="setColumnMinimumWidth",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="column", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="minSize", annotation=TypeRef(expr='int'), default_repr=None),
                    ),
                    source_props=("column_minimum_width_column", "column_minimum_width_min_size"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setColumnStretch": UiMethodSpec(
                    name="setColumnStretch",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="column", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="stretch", annotation=TypeRef(expr='int'), default_repr=None),
                    ),
                    source_props=("column_stretch_column", "column_stretch_stretch"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setContentsMargins": UiMethodSpec(
                    name="setContentsMargins",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="left", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="top", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="right", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="bottom", annotation=TypeRef(expr='int'), default_repr=None),
                    ),
                    source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setDefaultPositioning": UiMethodSpec(
                    name="setDefaultPositioning",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="n", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="orient", annotation=TypeRef(expr='PySide6.QtCore.Qt.Orientation'), default_repr=None),
                    ),
                    source_props=("default_positioning_n", "default_positioning_orient"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setHorizontalSpacing": UiMethodSpec(
                    name="setHorizontalSpacing",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="spacing", annotation=TypeRef(expr='int'), default_repr=None),
                    ),
                    source_props=("horizontalSpacing",),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setRowMinimumHeight": UiMethodSpec(
                    name="setRowMinimumHeight",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="row", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="minSize", annotation=TypeRef(expr='int'), default_repr=None),
                    ),
                    source_props=("row_minimum_height_row", "row_minimum_height_min_size"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setRowStretch": UiMethodSpec(
                    name="setRowStretch",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="row", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="stretch", annotation=TypeRef(expr='int'), default_repr=None),
                    ),
                    source_props=("row_stretch_row", "row_stretch_stretch"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setVerticalSpacing": UiMethodSpec(
                    name="setVerticalSpacing",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="spacing", annotation=TypeRef(expr='int'), default_repr=None),
                    ),
                    source_props=("verticalSpacing",),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            events=frozendict({
            }),
            mount_points=frozendict({
                "layout": MountPointSpec(
                    name="layout",
                    accepted_produced_type=TypeRef(expr='PySide6.QtWidgets.QLayout'),
                    params=(
                        MountParamSpec(name="row", annotation=TypeRef(expr='int'), keyed=True, default_repr=None),
                        MountParamSpec(name="column", annotation=TypeRef(expr='int'), keyed=True, default_repr=None),
                        MountParamSpec(name="rowSpan", annotation=TypeRef(expr='int'), keyed=False, default_repr=None),
                        MountParamSpec(name="columnSpan", annotation=TypeRef(expr='int'), keyed=False, default_repr=None),
                        MountParamSpec(name="alignment", annotation=TypeRef(expr='PySide6.QtCore.Qt.AlignmentFlag'), keyed=False, default_repr='...'),
                    ),
                    min_children=0,
                    max_children=1,
                    apply_method_name='addLayout',
                    sync_method_name=None,
                    place_method_name=None,
                    append_method_name=None,
                    detach_method_name='removeItem',
                    replay_kind=MountReplayKind.NONE,
                    prefer_sync=True,
                ),
                "menu_bar": MountPointSpec(
                    name="menu_bar",
                    accepted_produced_type=TypeRef(expr='PySide6.QtWidgets.QMenuBar'),
                    params=(
                    ),
                    min_children=0,
                    max_children=1,
                    apply_method_name='setMenuBar',
                    sync_method_name=None,
                    place_method_name=None,
                    append_method_name=None,
                    detach_method_name=None,
                    replay_kind=MountReplayKind.NONE,
                    prefer_sync=False,
                ),
                "widget": MountPointSpec(
                    name="widget",
                    accepted_produced_type=TypeRef(expr='PySide6.QtWidgets.QWidget'),
                    params=(
                        MountParamSpec(name="row", annotation=TypeRef(expr='int'), keyed=True, default_repr=None),
                        MountParamSpec(name="column", annotation=TypeRef(expr='int'), keyed=True, default_repr=None),
                        MountParamSpec(name="rowSpan", annotation=TypeRef(expr='int'), keyed=False, default_repr=None),
                        MountParamSpec(name="columnSpan", annotation=TypeRef(expr='int'), keyed=False, default_repr=None),
                        MountParamSpec(name="alignment", annotation=TypeRef(expr='PySide6.QtCore.Qt.AlignmentFlag'), keyed=False, default_repr='...'),
                    ),
                    min_children=0,
                    max_children=1,
                    apply_method_name='addWidget',
                    sync_method_name=None,
                    place_method_name=None,
                    append_method_name=None,
                    detach_method_name='removeWidget',
                    replay_kind=MountReplayKind.NONE,
                    prefer_sync=True,
                ),
            }),
            default_child_mount_point_name='layout',
            default_attach_mount_point_names=('menu_bar',),
            child_policy=ChildPolicy.NONE,
        ),
        'QHBoxLayout': UiWidgetSpec(
            kind="QHBoxLayout",
            mounted_type_name="PySide6.QtWidgets.QHBoxLayout",
            constructor_params=frozendict({
                "parent": UiParamSpec(name="parent", annotation=TypeRef(expr='PySide6.QtWidgets.QWidget'), default_repr=None),
            }),
            props=frozendict({
                "parent": UiPropSpec(name="parent", annotation=TypeRef(expr='PySide6.QtWidgets.QWidget'), mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='parent', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "contentsMargins": UiPropSpec(name="contentsMargins", annotation=TypeRef(expr='QMargins'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "horizontalSizeConstraint": UiPropSpec(name="horizontalSizeConstraint", annotation=TypeRef(expr='QLayout::SizeConstraint'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "objectName": UiPropSpec(name="objectName", annotation=TypeRef(expr='QString'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "sizeConstraint": UiPropSpec(name="sizeConstraint", annotation=TypeRef(expr='QLayout::SizeConstraint'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "spacing": UiPropSpec(name="spacing", annotation=TypeRef(expr='int'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "verticalSizeConstraint": UiPropSpec(name="verticalSizeConstraint", annotation=TypeRef(expr='QLayout::SizeConstraint'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
            }),
            methods=frozendict({
                "setAlignment": UiMethodSpec(
                    name="setAlignment",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="alignment", annotation=TypeRef(expr='PySide6.QtCore.Qt.AlignmentFlag'), default_repr=None),
                    ),
                    source_props=("alignment",),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setContentsMargins": UiMethodSpec(
                    name="setContentsMargins",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="left", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="top", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="right", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="bottom", annotation=TypeRef(expr='int'), default_repr=None),
                    ),
                    source_props=("contents_margins_left", "contents_margins_top", "contents_margins_right", "contents_margins_bottom"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setStretch": UiMethodSpec(
                    name="setStretch",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="index", annotation=TypeRef(expr='int'), default_repr=None),
                        UiParamSpec(name="stretch", annotation=TypeRef(expr='int'), default_repr=None),
                    ),
                    source_props=("stretch_index", "stretch_stretch"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            events=frozendict({
            }),
            mount_points=frozendict({
                "layout": MountPointSpec(
                    name="layout",
                    accepted_produced_type=TypeRef(expr='PySide6.QtWidgets.QLayout'),
                    params=(
                        MountParamSpec(name="stretch", annotation=TypeRef(expr='int | None'), keyed=False, default_repr='...'),
                    ),
                    min_children=0,
                    max_children=None,
                    apply_method_name=None,
                    sync_method_name=None,
                    place_method_name='insertLayout',
                    append_method_name='addLayout',
                    detach_method_name='removeItem',
                    replay_kind=MountReplayKind.INDEX,
                    prefer_sync=False,
                ),
                "menu_bar": MountPointSpec(
                    name="menu_bar",
                    accepted_produced_type=TypeRef(expr='PySide6.QtWidgets.QMenuBar'),
                    params=(
                    ),
                    min_children=0,
                    max_children=1,
                    apply_method_name='setMenuBar',
                    sync_method_name=None,
                    place_method_name=None,
                    append_method_name=None,
                    detach_method_name=None,
                    replay_kind=MountReplayKind.NONE,
                    prefer_sync=False,
                ),
                "widget": MountPointSpec(
                    name="widget",
                    accepted_produced_type=TypeRef(expr='PySide6.QtWidgets.QWidget'),
                    params=(
                        MountParamSpec(name="stretch", annotation=TypeRef(expr='int | None'), keyed=False, default_repr='...'),
                        MountParamSpec(name="alignment", annotation=TypeRef(expr='PySide6.QtCore.Qt.AlignmentFlag'), keyed=False, default_repr='...'),
                    ),
                    min_children=0,
                    max_children=None,
                    apply_method_name=None,
                    sync_method_name=None,
                    place_method_name='insertWidget',
                    append_method_name='addWidget',
                    detach_method_name='removeWidget',
                    replay_kind=MountReplayKind.INDEX,
                    prefer_sync=False,
                ),
            }),
            default_child_mount_point_name='layout',
            default_attach_mount_point_names=('menu_bar', 'widget', 'layout'),
            child_policy=ChildPolicy.NONE,
        ),
    })

    class mounts:
        layout = MountSelector.named("layout")
        menu_bar = MountSelector.named("menu_bar")
        widget = MountSelector.named("widget")

    QT_PROPERTY_GETTER: ClassVar[str] = "property"
    QT_PROPERTY_SETTER: ClassVar[str] = "setProperty"

    @classmethod
    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
        return UIElement(kind=kind, props=dict(kwds))

    @classmethod
    @pyrolyze
    def CQBoxLayout(
        cls,
        arg__1: PySide6.QtWidgets.QBoxLayout.Direction,
        parent: PySide6.QtWidgets.QWidget | None = ...,
        *,
        contentsMargins: Any | MissingType = MISSING,
        horizontalSizeConstraint: Any | MissingType = MISSING,
        objectName: str | MissingType = MISSING,
        sizeConstraint: Any | MissingType = MISSING,
        spacing: int | MissingType = MISSING,
        verticalSizeConstraint: Any | MissingType = MISSING,
        alignment: PySide6.QtCore.Qt.AlignmentFlag | MissingType = MISSING,
        contents_margins_left: int | MissingType = MISSING,
        contents_margins_top: int | MissingType = MISSING,
        contents_margins_right: int | MissingType = MISSING,
        contents_margins_bottom: int | MissingType = MISSING,
        stretch_index: int | MissingType = MISSING,
        stretch_stretch: int | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="QBoxLayout",
            arg__1=arg__1,
            parent=parent,
            contentsMargins=contentsMargins,
            horizontalSizeConstraint=horizontalSizeConstraint,
            objectName=objectName,
            sizeConstraint=sizeConstraint,
            spacing=spacing,
            verticalSizeConstraint=verticalSizeConstraint,
            alignment=alignment,
            contents_margins_left=contents_margins_left,
            contents_margins_top=contents_margins_top,
            contents_margins_right=contents_margins_right,
            contents_margins_bottom=contents_margins_bottom,
            stretch_index=stretch_index,
            stretch_stretch=stretch_stretch,
        )

    @classmethod
    @pyrolyze
    def CQFormLayout(
        cls,
        parent: PySide6.QtWidgets.QWidget | None = ...,
        *,
        fieldGrowthPolicy: PySide6.QtWidgets.QFormLayout.FieldGrowthPolicy | None = ...,
        rowWrapPolicy: PySide6.QtWidgets.QFormLayout.RowWrapPolicy | None = ...,
        labelAlignment: PySide6.QtCore.Qt.AlignmentFlag | None = ...,
        formAlignment: PySide6.QtCore.Qt.AlignmentFlag | None = ...,
        horizontalSpacing: int | None = ...,
        verticalSpacing: int | None = ...,
        contentsMargins: Any | MissingType = MISSING,
        horizontalSizeConstraint: Any | MissingType = MISSING,
        objectName: str | MissingType = MISSING,
        sizeConstraint: Any | MissingType = MISSING,
        spacing: int | MissingType = MISSING,
        verticalSizeConstraint: Any | MissingType = MISSING,
        alignment: PySide6.QtCore.Qt.AlignmentFlag | MissingType = MISSING,
        contents_margins_left: int | MissingType = MISSING,
        contents_margins_top: int | MissingType = MISSING,
        contents_margins_right: int | MissingType = MISSING,
        contents_margins_bottom: int | MissingType = MISSING,
        geometry: PySide6.QtCore.QRect | MissingType = MISSING,
        row_visible_row: int | MissingType = MISSING,
        row_visible_on: bool | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="QFormLayout",
            parent=parent,
            fieldGrowthPolicy=fieldGrowthPolicy,
            rowWrapPolicy=rowWrapPolicy,
            labelAlignment=labelAlignment,
            formAlignment=formAlignment,
            horizontalSpacing=horizontalSpacing,
            verticalSpacing=verticalSpacing,
            contentsMargins=contentsMargins,
            horizontalSizeConstraint=horizontalSizeConstraint,
            objectName=objectName,
            sizeConstraint=sizeConstraint,
            spacing=spacing,
            verticalSizeConstraint=verticalSizeConstraint,
            alignment=alignment,
            contents_margins_left=contents_margins_left,
            contents_margins_top=contents_margins_top,
            contents_margins_right=contents_margins_right,
            contents_margins_bottom=contents_margins_bottom,
            geometry=geometry,
            row_visible_row=row_visible_row,
            row_visible_on=row_visible_on,
        )

    @classmethod
    @pyrolyze
    def CQGridLayout(
        cls,
        parent: PySide6.QtWidgets.QWidget | None = ...,
        *,
        contentsMargins: Any | MissingType = MISSING,
        horizontalSizeConstraint: Any | MissingType = MISSING,
        objectName: str | MissingType = MISSING,
        sizeConstraint: Any | MissingType = MISSING,
        spacing: int | MissingType = MISSING,
        verticalSizeConstraint: Any | MissingType = MISSING,
        alignment: PySide6.QtCore.Qt.AlignmentFlag | MissingType = MISSING,
        column_minimum_width_column: int | MissingType = MISSING,
        column_minimum_width_min_size: int | MissingType = MISSING,
        column_stretch_column: int | MissingType = MISSING,
        column_stretch_stretch: int | MissingType = MISSING,
        contents_margins_left: int | MissingType = MISSING,
        contents_margins_top: int | MissingType = MISSING,
        contents_margins_right: int | MissingType = MISSING,
        contents_margins_bottom: int | MissingType = MISSING,
        default_positioning_n: int | MissingType = MISSING,
        default_positioning_orient: PySide6.QtCore.Qt.Orientation | MissingType = MISSING,
        horizontalSpacing: int | MissingType = MISSING,
        row_minimum_height_row: int | MissingType = MISSING,
        row_minimum_height_min_size: int | MissingType = MISSING,
        row_stretch_row: int | MissingType = MISSING,
        row_stretch_stretch: int | MissingType = MISSING,
        verticalSpacing: int | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="QGridLayout",
            parent=parent,
            contentsMargins=contentsMargins,
            horizontalSizeConstraint=horizontalSizeConstraint,
            objectName=objectName,
            sizeConstraint=sizeConstraint,
            spacing=spacing,
            verticalSizeConstraint=verticalSizeConstraint,
            alignment=alignment,
            column_minimum_width_column=column_minimum_width_column,
            column_minimum_width_min_size=column_minimum_width_min_size,
            column_stretch_column=column_stretch_column,
            column_stretch_stretch=column_stretch_stretch,
            contents_margins_left=contents_margins_left,
            contents_margins_top=contents_margins_top,
            contents_margins_right=contents_margins_right,
            contents_margins_bottom=contents_margins_bottom,
            default_positioning_n=default_positioning_n,
            default_positioning_orient=default_positioning_orient,
            horizontalSpacing=horizontalSpacing,
            row_minimum_height_row=row_minimum_height_row,
            row_minimum_height_min_size=row_minimum_height_min_size,
            row_stretch_row=row_stretch_row,
            row_stretch_stretch=row_stretch_stretch,
            verticalSpacing=verticalSpacing,
        )

    @classmethod
    @pyrolyze
    def CQHBoxLayout(
        cls,
        parent: PySide6.QtWidgets.QWidget | None = ...,
        *,
        contentsMargins: Any | MissingType = MISSING,
        horizontalSizeConstraint: Any | MissingType = MISSING,
        objectName: str | MissingType = MISSING,
        sizeConstraint: Any | MissingType = MISSING,
        spacing: int | MissingType = MISSING,
        verticalSizeConstraint: Any | MissingType = MISSING,
        alignment: PySide6.QtCore.Qt.AlignmentFlag | MissingType = MISSING,
        contents_margins_left: int | MissingType = MISSING,
        contents_margins_top: int | MissingType = MISSING,
        contents_margins_right: int | MissingType = MISSING,
        contents_margins_bottom: int | MissingType = MISSING,
        stretch_index: int | MissingType = MISSING,
        stretch_stretch: int | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="QHBoxLayout",
            parent=parent,
            contentsMargins=contentsMargins,
            horizontalSizeConstraint=horizontalSizeConstraint,
            objectName=objectName,
            sizeConstraint=sizeConstraint,
            spacing=spacing,
            verticalSizeConstraint=verticalSizeConstraint,
            alignment=alignment,
            contents_margins_left=contents_margins_left,
            contents_margins_top=contents_margins_top,
            contents_margins_right=contents_margins_right,
            contents_margins_bottom=contents_margins_bottom,
            stretch_index=stretch_index,
            stretch_stretch=stretch_stretch,
        )

GENERATION = '838d675e072d719e784fa29c8a8c31fa1ca08824f0fa486530ca58fbefcf477d'
