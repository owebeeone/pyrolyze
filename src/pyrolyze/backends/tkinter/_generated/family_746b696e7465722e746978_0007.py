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
            "CScrolledListBox": UiInterfaceEntry(public_name="CScrolledListBox", kind="ScrolledListBox"),
            "CScrolledTList": UiInterfaceEntry(public_name="CScrolledTList", kind="ScrolledTList"),
            "CScrolledWindow": UiInterfaceEntry(public_name="CScrolledWindow", kind="ScrolledWindow"),
            "CSelect": UiInterfaceEntry(public_name="CSelect", kind="Select"),
        }),
    )

    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({
        'ScrolledListBox': UiWidgetSpec(
            kind="ScrolledListBox",
            mounted_type_name="tkinter.tix.ScrolledListBox",
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
        'ScrolledTList': UiWidgetSpec(
            kind="ScrolledTList",
            mounted_type_name="tkinter.tix.ScrolledTList",
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
        'ScrolledWindow': UiWidgetSpec(
            kind="ScrolledWindow",
            mounted_type_name="tkinter.tix.ScrolledWindow",
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
        'Select': UiWidgetSpec(
            kind="Select",
            mounted_type_name="tkinter.tix.Select",
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
    # NOTE: original signature for ScrolledListBox includes omitted variadic arguments
    def CScrolledListBox(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ScrolledListBox",
            master=master,
            cnf=cnf,
            _silent=_silent,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for ScrolledTList includes omitted variadic arguments
    def CScrolledTList(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ScrolledTList",
            master=master,
            cnf=cnf,
            _silent=_silent,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for ScrolledWindow includes omitted variadic arguments
    def CScrolledWindow(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ScrolledWindow",
            master=master,
            cnf=cnf,
            _silent=_silent,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for Select includes omitted variadic arguments
    def CSelect(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="Select",
            master=master,
            cnf=cnf,
            _silent=_silent,
        )

GENERATION = '8c4455212261e06ca5ca7fbd9961384c9702ac4fe65ccefabb5dd8135d9fb826'
