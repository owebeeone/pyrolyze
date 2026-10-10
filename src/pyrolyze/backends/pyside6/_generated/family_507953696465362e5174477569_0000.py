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
            "CQAction": UiInterfaceEntry(public_name="CQAction", kind="QAction"),
        }),
    )

    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({
        'QAction': UiWidgetSpec(
            kind="QAction",
            mounted_type_name="PySide6.QtGui.QAction",
            constructor_params=frozendict({
                "text": UiParamSpec(name="text", annotation=TypeRef(expr='str'), default_repr=None),
                "parent": UiParamSpec(name="parent", annotation=TypeRef(expr='PySide6.QtCore.QObject | None'), default_repr='...'),
                "checkable": UiParamSpec(name="checkable", annotation=TypeRef(expr='bool | None'), default_repr='...'),
                "checked": UiParamSpec(name="checked", annotation=TypeRef(expr='bool | None'), default_repr='...'),
                "enabled": UiParamSpec(name="enabled", annotation=TypeRef(expr='bool | None'), default_repr='...'),
                "icon": UiParamSpec(name="icon", annotation=TypeRef(expr='PySide6.QtGui.QIcon | None'), default_repr='...'),
                "iconText": UiParamSpec(name="iconText", annotation=TypeRef(expr='str | None'), default_repr='...'),
                "toolTip": UiParamSpec(name="toolTip", annotation=TypeRef(expr='str | None'), default_repr='...'),
                "statusTip": UiParamSpec(name="statusTip", annotation=TypeRef(expr='str | None'), default_repr='...'),
                "whatsThis": UiParamSpec(name="whatsThis", annotation=TypeRef(expr='str | None'), default_repr='...'),
                "font": UiParamSpec(name="font", annotation=TypeRef(expr='PySide6.QtGui.QFont | None'), default_repr='...'),
                "shortcut": UiParamSpec(name="shortcut", annotation=TypeRef(expr='PySide6.QtGui.QKeySequence | None'), default_repr='...'),
                "shortcutContext": UiParamSpec(name="shortcutContext", annotation=TypeRef(expr='PySide6.QtCore.Qt.ShortcutContext | None'), default_repr='...'),
                "autoRepeat": UiParamSpec(name="autoRepeat", annotation=TypeRef(expr='bool | None'), default_repr='...'),
                "visible": UiParamSpec(name="visible", annotation=TypeRef(expr='bool | None'), default_repr='...'),
                "menuRole": UiParamSpec(name="menuRole", annotation=TypeRef(expr='PySide6.QtGui.QAction.MenuRole | None'), default_repr='...'),
                "iconVisibleInMenu": UiParamSpec(name="iconVisibleInMenu", annotation=TypeRef(expr='bool | None'), default_repr='...'),
                "shortcutVisibleInContextMenu": UiParamSpec(name="shortcutVisibleInContextMenu", annotation=TypeRef(expr='bool | None'), default_repr='...'),
                "priority": UiParamSpec(name="priority", annotation=TypeRef(expr='PySide6.QtGui.QAction.Priority | None'), default_repr='...'),
            }),
            props=frozendict({
                "text": UiPropSpec(name="text", annotation=TypeRef(expr='str'), mode=PropMode.CREATE_UPDATE, constructor_name='text', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "parent": UiPropSpec(name="parent", annotation=TypeRef(expr='PySide6.QtCore.QObject | None'), mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='parent', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "checkable": UiPropSpec(name="checkable", annotation=TypeRef(expr='bool | None'), mode=PropMode.CREATE_UPDATE, constructor_name='checkable', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "checked": UiPropSpec(name="checked", annotation=TypeRef(expr='bool | None'), mode=PropMode.CREATE_UPDATE, constructor_name='checked', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "enabled": UiPropSpec(name="enabled", annotation=TypeRef(expr='bool | None'), mode=PropMode.CREATE_UPDATE, constructor_name='enabled', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "icon": UiPropSpec(name="icon", annotation=TypeRef(expr='PySide6.QtGui.QIcon | None'), mode=PropMode.CREATE_UPDATE, constructor_name='icon', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "iconText": UiPropSpec(name="iconText", annotation=TypeRef(expr='str | None'), mode=PropMode.CREATE_UPDATE, constructor_name='iconText', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "toolTip": UiPropSpec(name="toolTip", annotation=TypeRef(expr='str | None'), mode=PropMode.CREATE_UPDATE, constructor_name='toolTip', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "statusTip": UiPropSpec(name="statusTip", annotation=TypeRef(expr='str | None'), mode=PropMode.CREATE_UPDATE, constructor_name='statusTip', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "whatsThis": UiPropSpec(name="whatsThis", annotation=TypeRef(expr='str | None'), mode=PropMode.CREATE_UPDATE, constructor_name='whatsThis', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "font": UiPropSpec(name="font", annotation=TypeRef(expr='PySide6.QtGui.QFont | None'), mode=PropMode.CREATE_UPDATE, constructor_name='font', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "shortcut": UiPropSpec(name="shortcut", annotation=TypeRef(expr='PySide6.QtGui.QKeySequence | None'), mode=PropMode.CREATE_UPDATE, constructor_name='shortcut', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "shortcutContext": UiPropSpec(name="shortcutContext", annotation=TypeRef(expr='PySide6.QtCore.Qt.ShortcutContext | None'), mode=PropMode.CREATE_UPDATE, constructor_name='shortcutContext', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "autoRepeat": UiPropSpec(name="autoRepeat", annotation=TypeRef(expr='bool | None'), mode=PropMode.CREATE_UPDATE, constructor_name='autoRepeat', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "visible": UiPropSpec(name="visible", annotation=TypeRef(expr='bool | None'), mode=PropMode.CREATE_UPDATE, constructor_name='visible', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "menuRole": UiPropSpec(name="menuRole", annotation=TypeRef(expr='PySide6.QtGui.QAction.MenuRole | None'), mode=PropMode.CREATE_UPDATE, constructor_name='menuRole', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "iconVisibleInMenu": UiPropSpec(name="iconVisibleInMenu", annotation=TypeRef(expr='bool | None'), mode=PropMode.CREATE_UPDATE, constructor_name='iconVisibleInMenu', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "shortcutVisibleInContextMenu": UiPropSpec(name="shortcutVisibleInContextMenu", annotation=TypeRef(expr='bool | None'), mode=PropMode.CREATE_UPDATE, constructor_name='shortcutVisibleInContextMenu', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "priority": UiPropSpec(name="priority", annotation=TypeRef(expr='PySide6.QtGui.QAction.Priority | None'), mode=PropMode.CREATE_UPDATE, constructor_name='priority', setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
                "objectName": UiPropSpec(name="objectName", annotation=TypeRef(expr='QString'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.QT_PROPERTY, setter_name="setProperty", getter_kind=AccessorKind.QT_PROPERTY, getter_name="property", affects_identity=False),
            }),
            methods=frozendict({
                "setData": UiMethodSpec(
                    name="setData",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="var", annotation=TypeRef(expr='typing.Any'), default_repr=None),
                    ),
                    source_props=("data",),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setSeparator": UiMethodSpec(
                    name="setSeparator",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="b", annotation=TypeRef(expr='bool'), default_repr=None),
                    ),
                    source_props=("separator",),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "setShortcuts": UiMethodSpec(
                    name="setShortcuts",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="shortcuts", annotation=TypeRef(expr='collections.abc.Sequence[PySide6.QtGui.QKeySequence]'), default_repr=None),
                    ),
                    source_props=("shortcuts",),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            events=frozendict({
                "on_triggered": UiEventSpec(
                    name="on_triggered",
                    signal_name="triggered",
                    payload_policy=EventPayloadPolicy.NONE,
                ),
            }),
            mount_points=frozendict({
                "menu": MountPointSpec(
                    name="menu",
                    accepted_produced_type=TypeRef(expr='PySide6.QtWidgets.QMenu'),
                    params=(
                    ),
                    min_children=0,
                    max_children=1,
                    apply_method_name='setMenu',
                    sync_method_name=None,
                    place_method_name=None,
                    append_method_name=None,
                    detach_method_name=None,
                    replay_kind=MountReplayKind.NONE,
                    prefer_sync=False,
                ),
            }),
            default_child_mount_point_name='menu',
            default_attach_mount_point_names=('menu',),
            child_policy=ChildPolicy.NONE,
        ),
    })

    class mounts:
        menu = MountSelector.named("menu")

    QT_PROPERTY_GETTER: ClassVar[str] = "property"
    QT_PROPERTY_SETTER: ClassVar[str] = "setProperty"

    @classmethod
    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
        return UIElement(kind=kind, props=dict(kwds))

    @classmethod
    @pyrolyze
    def CQAction(
        cls,
        text: str,
        parent: PySide6.QtCore.QObject | None = ...,
        *,
        checkable: bool | None = ...,
        checked: bool | None = ...,
        enabled: bool | None = ...,
        icon: PySide6.QtGui.QIcon | None = ...,
        iconText: str | None = ...,
        toolTip: str | None = ...,
        statusTip: str | None = ...,
        whatsThis: str | None = ...,
        font: PySide6.QtGui.QFont | None = ...,
        shortcut: PySide6.QtGui.QKeySequence | None = ...,
        shortcutContext: PySide6.QtCore.Qt.ShortcutContext | None = ...,
        autoRepeat: bool | None = ...,
        visible: bool | None = ...,
        menuRole: PySide6.QtGui.QAction.MenuRole | None = ...,
        iconVisibleInMenu: bool | None = ...,
        shortcutVisibleInContextMenu: bool | None = ...,
        priority: PySide6.QtGui.QAction.Priority | None = ...,
        objectName: str | MissingType = MISSING,
        data: typing.Any | MissingType = MISSING,
        separator: bool | MissingType = MISSING,
        shortcuts: collections.abc.Sequence[PySide6.QtGui.QKeySequence] | MissingType = MISSING,
        on_triggered: PyrolyzeHandler[[], None] | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="QAction",
            text=text,
            parent=parent,
            checkable=checkable,
            checked=checked,
            enabled=enabled,
            icon=icon,
            iconText=iconText,
            toolTip=toolTip,
            statusTip=statusTip,
            whatsThis=whatsThis,
            font=font,
            shortcut=shortcut,
            shortcutContext=shortcutContext,
            autoRepeat=autoRepeat,
            visible=visible,
            menuRole=menuRole,
            iconVisibleInMenu=iconVisibleInMenu,
            shortcutVisibleInContextMenu=shortcutVisibleInContextMenu,
            priority=priority,
            objectName=objectName,
            data=data,
            separator=separator,
            shortcuts=shortcuts,
            on_triggered=on_triggered,
        )

GENERATION = '838d675e072d719e784fa29c8a8c31fa1ca08824f0fa486530ca58fbefcf477d'
