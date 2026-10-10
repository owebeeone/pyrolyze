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
            "CQLayout": UiInterfaceEntry(public_name="CQLayout", kind="QLayout"),
            "CQStackedLayout": UiInterfaceEntry(public_name="CQStackedLayout", kind="QStackedLayout"),
            "CQVBoxLayout": UiInterfaceEntry(public_name="CQVBoxLayout", kind="QVBoxLayout"),
        }),
    )

    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({
        'QLayout': UiWidgetSpec(
            kind="QLayout",
            mounted_type_name="PySide6.QtWidgets.QLayout",
            constructor_params=frozendict({
                "parent": UiParamSpec(name="parent", annotation=TypeRef(expr='PySide6.QtWidgets.QWidget | None'), default_repr='...'),
                "spacing": UiParamSpec(name="spacing", annotation=TypeRef(expr='int | None'), default_repr='...'),
                "contentsMargins": UiParamSpec(name="contentsMargins", annotation=TypeRef(expr='PySide6.QtCore.QMargins | None'), default_repr='...'),
                "sizeConstraint": UiParamSpec(name="sizeConstraint", annotation=TypeRef(expr='PySide6.QtWidgets.QLayout.SizeConstraint | None'), default_repr='...'),
                "horizontalSizeConstraint": UiParamSpec(name="horizontalSizeConstraint", annotation=TypeRef(expr='PySide6.QtWidgets.QLayout.SizeConstraint | None'), default_repr='...'),
                "verticalSizeConstraint": UiParamSpec(name="verticalSizeConstraint", annotation=TypeRef(expr='PySide6.QtWidgets.QLayout.SizeConstraint | None'), default_repr='...'),
            }),
            props=frozendict({
                "parent": UiPropSpec(name="parent", annotation=TypeRef(expr='PySide6.QtWidgets.QWidget | None'), mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='parent', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "spacing": UiPropSpec(name="spacing", annotation=TypeRef(expr='int | None'), mode=PropMode.CREATE_UPDATE, constructor_name='spacing', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "contentsMargins": UiPropSpec(name="contentsMargins", annotation=TypeRef(expr='PySide6.QtCore.QMargins | None'), mode=PropMode.CREATE_UPDATE, constructor_name='contentsMargins', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "sizeConstraint": UiPropSpec(name="sizeConstraint", annotation=TypeRef(expr='PySide6.QtWidgets.QLayout.SizeConstraint | None'), mode=PropMode.CREATE_UPDATE, constructor_name='sizeConstraint', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "horizontalSizeConstraint": UiPropSpec(name="horizontalSizeConstraint", annotation=TypeRef(expr='PySide6.QtWidgets.QLayout.SizeConstraint | None'), mode=PropMode.CREATE_UPDATE, constructor_name='horizontalSizeConstraint', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "verticalSizeConstraint": UiPropSpec(name="verticalSizeConstraint", annotation=TypeRef(expr='PySide6.QtWidgets.QLayout.SizeConstraint | None'), mode=PropMode.CREATE_UPDATE, constructor_name='verticalSizeConstraint', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "objectName": UiPropSpec(name="objectName", annotation=TypeRef(expr='QString'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
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
            }),
            events=frozendict({
            }),
            mount_points=frozendict({
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
            }),
            default_child_mount_point_name='menu_bar',
            default_attach_mount_point_names=('menu_bar',),
            child_policy=ChildPolicy.NONE,
        ),
        'QStackedLayout': UiWidgetSpec(
            kind="QStackedLayout",
            mounted_type_name="PySide6.QtWidgets.QStackedLayout",
            constructor_params=frozendict({
                "parentLayout": UiParamSpec(name="parentLayout", annotation=TypeRef(expr='PySide6.QtWidgets.QLayout'), default_repr=None),
                "currentIndex": UiParamSpec(name="currentIndex", annotation=TypeRef(expr='int | None'), default_repr='...'),
                "stackingMode": UiParamSpec(name="stackingMode", annotation=TypeRef(expr='PySide6.QtWidgets.QStackedLayout.StackingMode | None'), default_repr='...'),
                "parent": UiParamSpec(name="parent", annotation=TypeRef(expr='PySide6.QtWidgets.QWidget'), default_repr=None),
            }),
            props=frozendict({
                "parentLayout": UiPropSpec(name="parentLayout", annotation=TypeRef(expr='PySide6.QtWidgets.QLayout'), mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='parentLayout', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "currentIndex": UiPropSpec(name="currentIndex", annotation=TypeRef(expr='int | None'), mode=PropMode.CREATE_UPDATE, constructor_name='currentIndex', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "stackingMode": UiPropSpec(name="stackingMode", annotation=TypeRef(expr='PySide6.QtWidgets.QStackedLayout.StackingMode | None'), mode=PropMode.CREATE_UPDATE, constructor_name='stackingMode', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
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
            }),
            events=frozendict({
            }),
            mount_points=frozendict({
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
            default_child_mount_point_name='widget',
            default_attach_mount_point_names=('menu_bar', 'widget'),
            child_policy=ChildPolicy.NONE,
        ),
        'QVBoxLayout': UiWidgetSpec(
            kind="QVBoxLayout",
            mounted_type_name="PySide6.QtWidgets.QVBoxLayout",
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
    def CQLayout(
        cls,
        parent: PySide6.QtWidgets.QWidget | None = ...,
        *,
        spacing: int | None = ...,
        contentsMargins: PySide6.QtCore.QMargins | None = ...,
        sizeConstraint: PySide6.QtWidgets.QLayout.SizeConstraint | None = ...,
        horizontalSizeConstraint: PySide6.QtWidgets.QLayout.SizeConstraint | None = ...,
        verticalSizeConstraint: PySide6.QtWidgets.QLayout.SizeConstraint | None = ...,
        objectName: str | MissingType = MISSING,
        alignment: PySide6.QtCore.Qt.AlignmentFlag | MissingType = MISSING,
        contents_margins_left: int | MissingType = MISSING,
        contents_margins_top: int | MissingType = MISSING,
        contents_margins_right: int | MissingType = MISSING,
        contents_margins_bottom: int | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="QLayout",
            parent=parent,
            spacing=spacing,
            contentsMargins=contentsMargins,
            sizeConstraint=sizeConstraint,
            horizontalSizeConstraint=horizontalSizeConstraint,
            verticalSizeConstraint=verticalSizeConstraint,
            objectName=objectName,
            alignment=alignment,
            contents_margins_left=contents_margins_left,
            contents_margins_top=contents_margins_top,
            contents_margins_right=contents_margins_right,
            contents_margins_bottom=contents_margins_bottom,
        )

    @classmethod
    @pyrolyze
    def CQStackedLayout(
        cls,
        parentLayout: PySide6.QtWidgets.QLayout,
        *,
        currentIndex: int | None = ...,
        stackingMode: PySide6.QtWidgets.QStackedLayout.StackingMode | None = ...,
        parent: PySide6.QtWidgets.QWidget,
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
    ) -> None:
        call_native(cls.__element)(
            kind="QStackedLayout",
            parentLayout=parentLayout,
            currentIndex=currentIndex,
            stackingMode=stackingMode,
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
            geometry=geometry,
        )

    @classmethod
    @pyrolyze
    def CQVBoxLayout(
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
            kind="QVBoxLayout",
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
