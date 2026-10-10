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
            "CTtkRadiobutton": UiInterfaceEntry(public_name="CTtkRadiobutton", kind="ttk_Radiobutton"),
            "CTtkScale": UiInterfaceEntry(public_name="CTtkScale", kind="ttk_Scale"),
            "CTtkScrollbar": UiInterfaceEntry(public_name="CTtkScrollbar", kind="ttk_Scrollbar"),
            "CTtkSpinbox": UiInterfaceEntry(public_name="CTtkSpinbox", kind="ttk_Spinbox"),
        }),
    )

    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({
        'ttk_Radiobutton': UiWidgetSpec(
            kind="ttk_Radiobutton",
            mounted_type_name="tkinter.ttk.Radiobutton",
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
                "padding": UiPropSpec(name="padding", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "state": UiPropSpec(name="state", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "text": UiPropSpec(name="text", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "textvariable": UiPropSpec(name="textvariable", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "underline": UiPropSpec(name="underline", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "value": UiPropSpec(name="value", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
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
        'ttk_Scale': UiWidgetSpec(
            kind="ttk_Scale",
            mounted_type_name="tkinter.ttk.Scale",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "command": UiPropSpec(name="command", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "length": UiPropSpec(name="length", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "orient": UiPropSpec(name="orient", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "state": UiPropSpec(name="state", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "to": UiPropSpec(name="to", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "value": UiPropSpec(name="value", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "variable": UiPropSpec(name="variable", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
            }),
            methods=frozendict({
                "set": UiMethodSpec(
                    name="set",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="value", annotation=None, default_repr=None),
                    ),
                    source_props=("value",),
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
        'ttk_Scrollbar': UiWidgetSpec(
            kind="ttk_Scrollbar",
            mounted_type_name="tkinter.ttk.Scrollbar",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "command": UiPropSpec(name="command", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "orient": UiPropSpec(name="orient", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
            }),
            methods=frozendict({
                "set": UiMethodSpec(
                    name="set",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="first", annotation=None, default_repr=None),
                        UiParamSpec(name="last", annotation=None, default_repr=None),
                    ),
                    source_props=("first", "last"),
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
        'ttk_Spinbox': UiWidgetSpec(
            kind="ttk_Spinbox",
            mounted_type_name="tkinter.ttk.Spinbox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "background": UiPropSpec(name="background", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "command": UiPropSpec(name="command", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "exportselection": UiPropSpec(name="exportselection", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "font": UiPropSpec(name="font", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "foreground": UiPropSpec(name="foreground", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "format": UiPropSpec(name="format", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "increment": UiPropSpec(name="increment", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "invalidcommand": UiPropSpec(name="invalidcommand", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "justify": UiPropSpec(name="justify", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "placeholder": UiPropSpec(name="placeholder", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "placeholderforeground": UiPropSpec(name="placeholderforeground", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "show": UiPropSpec(name="show", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "state": UiPropSpec(name="state", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "textvariable": UiPropSpec(name="textvariable", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "to": UiPropSpec(name="to", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "validate": UiPropSpec(name="validate", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "validatecommand": UiPropSpec(name="validatecommand", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "values": UiPropSpec(name="values", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "width": UiPropSpec(name="width", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "wrap": UiPropSpec(name="wrap", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "xscrollcommand": UiPropSpec(name="xscrollcommand", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
            }),
            methods=frozendict({
                "set": UiMethodSpec(
                    name="set",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="value", annotation=None, default_repr=None),
                    ),
                    source_props=("value",),
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
    # NOTE: original signature for Radiobutton includes omitted variadic arguments
    def CTtkRadiobutton(
        cls,
        master = None,
        *,
        command: Any | MissingType = MISSING,
        compound: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        image: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        value: Any | MissingType = MISSING,
        variable: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ttk_Radiobutton",
            master=master,
            command=command,
            compound=compound,
            cursor=cursor,
            image=image,
            justify=justify,
            padding=padding,
            state=state,
            style=style,
            takefocus=takefocus,
            text=text,
            textvariable=textvariable,
            underline=underline,
            value=value,
            variable=variable,
            width=width,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for Scale includes omitted variadic arguments
    def CTtkScale(
        cls,
        master = None,
        *,
        command: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        length: Any | MissingType = MISSING,
        orient: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        to: Any | MissingType = MISSING,
        value: Any | MissingType = MISSING,
        variable: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ttk_Scale",
            master=master,
            command=command,
            cursor=cursor,
            length=length,
            orient=orient,
            state=state,
            style=style,
            takefocus=takefocus,
            to=to,
            value=value,
            variable=variable,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for Scrollbar includes omitted variadic arguments
    def CTtkScrollbar(
        cls,
        master = None,
        *,
        command: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        orient: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        first: Any | MissingType = MISSING,
        last: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ttk_Scrollbar",
            master=master,
            command=command,
            cursor=cursor,
            orient=orient,
            style=style,
            takefocus=takefocus,
            first=first,
            last=last,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for Spinbox includes omitted variadic arguments
    def CTtkSpinbox(
        cls,
        master = None,
        *,
        background: Any | MissingType = MISSING,
        command: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        exportselection: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        format: Any | MissingType = MISSING,
        increment: Any | MissingType = MISSING,
        invalidcommand: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        placeholder: Any | MissingType = MISSING,
        placeholderforeground: Any | MissingType = MISSING,
        show: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        to: Any | MissingType = MISSING,
        validate: Any | MissingType = MISSING,
        validatecommand: Any | MissingType = MISSING,
        values: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        wrap: Any | MissingType = MISSING,
        xscrollcommand: Any | MissingType = MISSING,
        value: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ttk_Spinbox",
            master=master,
            background=background,
            command=command,
            cursor=cursor,
            exportselection=exportselection,
            font=font,
            foreground=foreground,
            format=format,
            increment=increment,
            invalidcommand=invalidcommand,
            justify=justify,
            placeholder=placeholder,
            placeholderforeground=placeholderforeground,
            show=show,
            state=state,
            style=style,
            takefocus=takefocus,
            textvariable=textvariable,
            to=to,
            validate=validate,
            validatecommand=validatecommand,
            values=values,
            width=width,
            wrap=wrap,
            xscrollcommand=xscrollcommand,
            value=value,
        )

GENERATION = '8c4455212261e06ca5ca7fbd9961384c9702ac4fe65ccefabb5dd8135d9fb826'
