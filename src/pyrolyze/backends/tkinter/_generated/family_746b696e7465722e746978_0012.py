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
            "C_dummyHList": UiInterfaceEntry(public_name="C_dummyHList", kind="_dummyHList"),
            "C_dummyLabel": UiInterfaceEntry(public_name="C_dummyLabel", kind="_dummyLabel"),
            "C_dummyListbox": UiInterfaceEntry(public_name="C_dummyListbox", kind="_dummyListbox"),
            "C_dummyMenu": UiInterfaceEntry(public_name="C_dummyMenu", kind="_dummyMenu"),
        }),
    )

    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({
        '_dummyHList': UiWidgetSpec(
            kind="_dummyHList",
            mounted_type_name="tkinter.tix._dummyHList",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
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
        '_dummyLabel': UiWidgetSpec(
            kind="_dummyLabel",
            mounted_type_name="tkinter.tix._dummyLabel",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
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
        '_dummyListbox': UiWidgetSpec(
            kind="_dummyListbox",
            mounted_type_name="tkinter.tix._dummyListbox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
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
        '_dummyMenu': UiWidgetSpec(
            kind="_dummyMenu",
            mounted_type_name="tkinter.tix._dummyMenu",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "name": UiParamSpec(name="name", annotation=None, default_repr=None),
                "destroy_physically": UiParamSpec(name="destroy_physically", annotation=None, default_repr='1'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "name": UiPropSpec(name="name", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='name', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "destroy_physically": UiPropSpec(name="destroy_physically", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='destroy_physically', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
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
    def C_dummyHList(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyHList",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
            _silent=_silent,
        )

    @classmethod
    @pyrolyze
    def C_dummyLabel(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyLabel",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
            _silent=_silent,
        )

    @classmethod
    @pyrolyze
    def C_dummyListbox(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyListbox",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
            _silent=_silent,
        )

    @classmethod
    @pyrolyze
    def C_dummyMenu(
        cls,
        master,
        name,
        destroy_physically = 1,
        *,
        _silent: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="_dummyMenu",
            master=master,
            name=name,
            destroy_physically=destroy_physically,
            _silent=_silent,
        )

GENERATION = '8c4455212261e06ca5ca7fbd9961384c9702ac4fe65ccefabb5dd8135d9fb826'
