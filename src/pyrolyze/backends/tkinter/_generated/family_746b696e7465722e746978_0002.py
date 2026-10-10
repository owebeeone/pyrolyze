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
            "CDirSelectBox": UiInterfaceEntry(public_name="CDirSelectBox", kind="DirSelectBox"),
            "CDirSelectDialog": UiInterfaceEntry(public_name="CDirSelectDialog", kind="DirSelectDialog"),
            "CDirTree": UiInterfaceEntry(public_name="CDirTree", kind="DirTree"),
            "CExFileSelectBox": UiInterfaceEntry(public_name="CExFileSelectBox", kind="ExFileSelectBox"),
        }),
    )

    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({
        'DirSelectBox': UiWidgetSpec(
            kind="DirSelectBox",
            mounted_type_name="tkinter.tix.DirSelectBox",
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
        'DirSelectDialog': UiWidgetSpec(
            kind="DirSelectDialog",
            mounted_type_name="tkinter.tix.DirSelectDialog",
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
        'DirTree': UiWidgetSpec(
            kind="DirTree",
            mounted_type_name="tkinter.tix.DirTree",
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
        'ExFileSelectBox': UiWidgetSpec(
            kind="ExFileSelectBox",
            mounted_type_name="tkinter.tix.ExFileSelectBox",
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
    # NOTE: original signature for DirSelectBox includes omitted variadic arguments
    def CDirSelectBox(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="DirSelectBox",
            master=master,
            cnf=cnf,
            _silent=_silent,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for DirSelectDialog includes omitted variadic arguments
    def CDirSelectDialog(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="DirSelectDialog",
            master=master,
            cnf=cnf,
            _silent=_silent,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for DirTree includes omitted variadic arguments
    def CDirTree(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="DirTree",
            master=master,
            cnf=cnf,
            _silent=_silent,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for ExFileSelectBox includes omitted variadic arguments
    def CExFileSelectBox(
        cls,
        master,
        cnf = {},
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ExFileSelectBox",
            master=master,
            cnf=cnf,
            _silent=_silent,
        )

GENERATION = '8c4455212261e06ca5ca7fbd9961384c9702ac4fe65ccefabb5dd8135d9fb826'
