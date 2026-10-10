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
            "CTreeview": UiInterfaceEntry(public_name="CTreeview", kind="Treeview"),
            "CTtkButton": UiInterfaceEntry(public_name="CTtkButton", kind="ttk_Button"),
            "CTtkCheckbutton": UiInterfaceEntry(public_name="CTtkCheckbutton", kind="ttk_Checkbutton"),
            "CTtkEntry": UiInterfaceEntry(public_name="CTtkEntry", kind="ttk_Entry"),
        }),
    )

    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({
        'Treeview': UiWidgetSpec(
            kind="Treeview",
            mounted_type_name="tkinter.ttk.Treeview",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "columns": UiPropSpec(name="columns", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "displaycolumns": UiPropSpec(name="displaycolumns", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "height": UiPropSpec(name="height", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "padding": UiPropSpec(name="padding", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "selectmode": UiPropSpec(name="selectmode", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "selecttype": UiPropSpec(name="selecttype", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "show": UiPropSpec(name="show", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "striped": UiPropSpec(name="striped", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "titlecolumns": UiPropSpec(name="titlecolumns", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "titleitems": UiPropSpec(name="titleitems", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "xscrollcommand": UiPropSpec(name="xscrollcommand", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "yscrollcommand": UiPropSpec(name="yscrollcommand", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
            }),
            methods=frozendict({
                "set": UiMethodSpec(
                    name="set",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="item", annotation=None, default_repr=None),
                        UiParamSpec(name="column", annotation=None, default_repr='None'),
                        UiParamSpec(name="value", annotation=None, default_repr='None'),
                    ),
                    source_props=("item", "column", "value"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=False,
                ),
                "set_children": UiMethodSpec(
                    name="set_children",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="item", annotation=None, default_repr=None),
                    ),
                    source_props=("_children",),
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
        'ttk_Button': UiWidgetSpec(
            kind="ttk_Button",
            mounted_type_name="tkinter.ttk.Button",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "compound": UiPropSpec(name="compound", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "default": UiPropSpec(name="default", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "image": UiPropSpec(name="image", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "justify": UiPropSpec(name="justify", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "padding": UiPropSpec(name="padding", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "state": UiPropSpec(name="state", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "text": UiPropSpec(name="text", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "textvariable": UiPropSpec(name="textvariable", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "underline": UiPropSpec(name="underline", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "width": UiPropSpec(name="width", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
            }),
            methods=frozendict({
            }),
            events=frozendict({
                "on_command": UiEventSpec(
                    name="on_command",
                    signal_name="command",
                    payload_policy=EventPayloadPolicy.NONE,
                ),
            }),
            mount_points=frozendict({
            }),
            default_child_mount_point_name=None,
            default_attach_mount_point_names=(),
            child_policy=ChildPolicy.NONE,
        ),
        'ttk_Checkbutton': UiWidgetSpec(
            kind="ttk_Checkbutton",
            mounted_type_name="tkinter.ttk.Checkbutton",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "command": UiPropSpec(name="command", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "compound": UiPropSpec(name="compound", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "image": UiPropSpec(name="image", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "justify": UiPropSpec(name="justify", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "offvalue": UiPropSpec(name="offvalue", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "onvalue": UiPropSpec(name="onvalue", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "padding": UiPropSpec(name="padding", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "state": UiPropSpec(name="state", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "text": UiPropSpec(name="text", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "textvariable": UiPropSpec(name="textvariable", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "underline": UiPropSpec(name="underline", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "variable": UiPropSpec(name="variable", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "width": UiPropSpec(name="width", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
            }),
            methods=frozendict({
            }),
            events=frozendict({
            }),
            mount_points=frozendict({
            }),
            default_child_mount_point_name=None,
            default_attach_mount_point_names=(),
            child_policy=ChildPolicy.NONE,
        ),
        'ttk_Entry': UiWidgetSpec(
            kind="ttk_Entry",
            mounted_type_name="tkinter.ttk.Entry",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "widget": UiParamSpec(name="widget", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "background": UiPropSpec(name="background", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "exportselection": UiPropSpec(name="exportselection", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "font": UiPropSpec(name="font", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "foreground": UiPropSpec(name="foreground", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "invalidcommand": UiPropSpec(name="invalidcommand", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "justify": UiPropSpec(name="justify", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "placeholder": UiPropSpec(name="placeholder", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "placeholderforeground": UiPropSpec(name="placeholderforeground", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "show": UiPropSpec(name="show", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "state": UiPropSpec(name="state", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "textvariable": UiPropSpec(name="textvariable", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "validate": UiPropSpec(name="validate", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "validatecommand": UiPropSpec(name="validatecommand", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "width": UiPropSpec(name="width", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "xscrollcommand": UiPropSpec(name="xscrollcommand", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
            }),
            methods=frozendict({
            }),
            events=frozendict({
                "on_key_release": UiEventSpec(
                    name="on_key_release",
                    signal_name="bind:<KeyRelease>",
                    payload_policy=EventPayloadPolicy.FIRST_ARG,
                ),
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
    # NOTE: original signature for Treeview includes omitted variadic arguments
    def CTreeview(
        cls,
        master = None,
        *,
        columns: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        displaycolumns: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        selectmode: Any | MissingType = MISSING,
        selecttype: Any | MissingType = MISSING,
        show: Any | MissingType = MISSING,
        striped: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        titlecolumns: Any | MissingType = MISSING,
        titleitems: Any | MissingType = MISSING,
        xscrollcommand: Any | MissingType = MISSING,
        yscrollcommand: Any | MissingType = MISSING,
        item: Any | MissingType = MISSING,
        column: Any | MissingType = MISSING,
        value: Any | MissingType = MISSING,
        _children: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="Treeview",
            master=master,
            columns=columns,
            cursor=cursor,
            displaycolumns=displaycolumns,
            height=height,
            padding=padding,
            selectmode=selectmode,
            selecttype=selecttype,
            show=show,
            striped=striped,
            style=style,
            takefocus=takefocus,
            titlecolumns=titlecolumns,
            titleitems=titleitems,
            xscrollcommand=xscrollcommand,
            yscrollcommand=yscrollcommand,
            item=item,
            column=column,
            value=value,
            _children=_children,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for Button includes omitted variadic arguments
    def CTtkButton(
        cls,
        *,
        compound: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        default: Any | MissingType = MISSING,
        image: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        on_command: PyrolyzeHandler[[], None] | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ttk_Button",
            compound=compound,
            cursor=cursor,
            default=default,
            image=image,
            justify=justify,
            padding=padding,
            state=state,
            style=style,
            takefocus=takefocus,
            text=text,
            textvariable=textvariable,
            underline=underline,
            width=width,
            on_command=on_command,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for Checkbutton includes omitted variadic arguments
    def CTtkCheckbutton(
        cls,
        master = None,
        *,
        command: Any | MissingType = MISSING,
        compound: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        image: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        offvalue: Any | MissingType = MISSING,
        onvalue: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        variable: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ttk_Checkbutton",
            master=master,
            command=command,
            compound=compound,
            cursor=cursor,
            image=image,
            justify=justify,
            offvalue=offvalue,
            onvalue=onvalue,
            padding=padding,
            state=state,
            style=style,
            takefocus=takefocus,
            text=text,
            textvariable=textvariable,
            underline=underline,
            variable=variable,
            width=width,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for Entry includes omitted variadic arguments
    def CTtkEntry(
        cls,
        *,
        background: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        exportselection: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        invalidcommand: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        placeholder: Any | MissingType = MISSING,
        placeholderforeground: Any | MissingType = MISSING,
        show: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        validate: Any | MissingType = MISSING,
        validatecommand: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        xscrollcommand: Any | MissingType = MISSING,
        on_key_release: PyrolyzeHandler[[Any], None] | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ttk_Entry",
            background=background,
            cursor=cursor,
            exportselection=exportselection,
            font=font,
            foreground=foreground,
            invalidcommand=invalidcommand,
            justify=justify,
            placeholder=placeholder,
            placeholderforeground=placeholderforeground,
            show=show,
            state=state,
            style=style,
            takefocus=takefocus,
            textvariable=textvariable,
            validate=validate,
            validatecommand=validatecommand,
            width=width,
            xscrollcommand=xscrollcommand,
            on_key_release=on_key_release,
        )

GENERATION = '8c4455212261e06ca5ca7fbd9961384c9702ac4fe65ccefabb5dd8135d9fb826'
