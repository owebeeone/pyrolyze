#@pyrolyze

"""Generated UI interface stubs for discovered widgets."""

from __future__ import annotations

import tkinter

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
class TkinterUiLibrary:
    ROOT_MODULE: ClassVar[str] = "tkinter"

    UI_INTERFACE: ClassVar[UiInterface] = UiInterface(
        name="TkinterUiLibrary",
        owner=None,
        entries=frozendict({
            "CPopupMenu": UiInterfaceEntry(public_name="CPopupMenu", kind="PopupMenu"),
            "CResizeHandle": UiInterfaceEntry(public_name="CResizeHandle", kind="ResizeHandle"),
            "CScrolledGrid": UiInterfaceEntry(public_name="CScrolledGrid", kind="ScrolledGrid"),
            "CScrolledHList": UiInterfaceEntry(public_name="CScrolledHList", kind="ScrolledHList"),
        }),
    )

    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({
        'PopupMenu': UiWidgetSpec(
            kind="PopupMenu",
            mounted_type_name="tkinter.tix.PopupMenu",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
                "set_silent": UiMethodSpec(
                    name="set_silent",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="value", annotation=None, default_repr=None),
                    ),
                    source_props=("_silent",),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            events=frozendict({
            }),
            mount_points=frozendict({
            }),
            default_child_mount_point_name=None,
            default_attach_mount_point_names=(),
            child_policy=ChildPolicy.NONE,
        ),
        'ResizeHandle': UiWidgetSpec(
            kind="ResizeHandle",
            mounted_type_name="tkinter.tix.ResizeHandle",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
                "set_silent": UiMethodSpec(
                    name="set_silent",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="value", annotation=None, default_repr=None),
                    ),
                    source_props=("_silent",),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            events=frozendict({
            }),
            mount_points=frozendict({
            }),
            default_child_mount_point_name=None,
            default_attach_mount_point_names=(),
            child_policy=ChildPolicy.NONE,
        ),
        'ScrolledGrid': UiWidgetSpec(
            kind="ScrolledGrid",
            mounted_type_name="tkinter.tix.ScrolledGrid",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
                "set": UiMethodSpec(
                    name="set",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="x", annotation=None, default_repr=None),
                        UiParamSpec(name="y", annotation=None, default_repr=None),
                        UiParamSpec(name="itemtype", annotation=None, default_repr='None'),
                    ),
                    source_props=("x", "y", "itemtype"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "set_silent": UiMethodSpec(
                    name="set_silent",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="value", annotation=None, default_repr=None),
                    ),
                    source_props=("_silent",),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            events=frozendict({
            }),
            mount_points=frozendict({
            }),
            default_child_mount_point_name=None,
            default_attach_mount_point_names=(),
            child_policy=ChildPolicy.NONE,
        ),
        'ScrolledHList': UiWidgetSpec(
            kind="ScrolledHList",
            mounted_type_name="tkinter.tix.ScrolledHList",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "cnf": UiParamSpec(name="cnf", annotation=None, default_repr='{}'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cnf": UiPropSpec(name="cnf", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='cnf', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
                "set_silent": UiMethodSpec(
                    name="set_silent",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="value", annotation=None, default_repr=None),
                    ),
                    source_props=("_silent",),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
            }),
            events=frozendict({
            }),
            mount_points=frozendict({
            }),
            default_child_mount_point_name=None,
            default_attach_mount_point_names=(),
            child_policy=ChildPolicy.NONE,
        ),
    })

    class mounts:
        pass

    @classmethod
    # NOTE: a trailing `kwds` parameter enables PyRolyze's tail kwds optimization.
    # The compiler lowers matching wrappers so only actually passed arguments
    # are forwarded into `UIElement.props`. See
    # docs/design/Packed_Kwds_UI_Interface_Optimization.md.
    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
        return UIElement(kind=kind, props=dict(kwds))

    @classmethod
    @pyrolyze
    # NOTE: original signature for PopupMenu includes omitted variadic arguments
    def CPopupMenu(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="PopupMenu",
            master=master,
            cnf=cnf,
            _silent=_silent,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for ResizeHandle includes omitted variadic arguments
    def CResizeHandle(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ResizeHandle",
            master=master,
            cnf=cnf,
            _silent=_silent,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for ScrolledGrid includes omitted variadic arguments
    def CScrolledGrid(
        cls,
        master = None,
        cnf = {},
        *,
        x: Any | MissingType = MISSING,
        y: Any | MissingType = MISSING,
        itemtype: Any | MissingType = MISSING,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ScrolledGrid",
            master=master,
            cnf=cnf,
            x=x,
            y=y,
            itemtype=itemtype,
            _silent=_silent,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for ScrolledHList includes omitted variadic arguments
    def CScrolledHList(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ScrolledHList",
            master=master,
            cnf=cnf,
            _silent=_silent,
        )

GENERATION = '8c4455212261e06ca5ca7fbd9961384c9702ac4fe65ccefabb5dd8135d9fb826'
