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
            "CTtkFrame": UiInterfaceEntry(public_name="CTtkFrame", kind="ttk_Frame"),
            "CTtkLabel": UiInterfaceEntry(public_name="CTtkLabel", kind="ttk_Label"),
            "CTtkMenubutton": UiInterfaceEntry(public_name="CTtkMenubutton", kind="ttk_Menubutton"),
            "CTtkOptionMenu": UiInterfaceEntry(public_name="CTtkOptionMenu", kind="ttk_OptionMenu"),
        }),
    )

    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({
        'ttk_Frame': UiWidgetSpec(
            kind="ttk_Frame",
            mounted_type_name="tkinter.ttk.Frame",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "borderwidth": UiPropSpec(name="borderwidth", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "height": UiPropSpec(name="height", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "padding": UiPropSpec(name="padding", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "relief": UiPropSpec(name="relief", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "width": UiPropSpec(name="width", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
            }),
            methods=frozendict({
            }),
            events=frozendict({
            }),
            mount_points=frozendict({
                "pack": MountPointSpec(
                    name="pack",
                    accepted_produced_type=TypeRef(expr='tkinter.Widget'),
                    params=(
                        MountParamSpec(name="side", annotation=TypeRef(expr='Any'), keyed=False, default_repr='None'),
                        MountParamSpec(name="fill", annotation=TypeRef(expr='Any'), keyed=False, default_repr='None'),
                        MountParamSpec(name="expand", annotation=TypeRef(expr='Any'), keyed=False, default_repr='None'),
                        MountParamSpec(name="padx", annotation=TypeRef(expr='Any'), keyed=False, default_repr='None'),
                        MountParamSpec(name="pady", annotation=TypeRef(expr='Any'), keyed=False, default_repr='None'),
                    ),
                    min_children=0,
                    max_children=None,
                    apply_method_name=None,
                    sync_method_name='pack',
                    place_method_name=None,
                    append_method_name='pack',
                    detach_method_name='pack_forget',
                    replay_kind=MountReplayKind.NONE,
                    prefer_sync=True,
                ),
                "grid": MountPointSpec(
                    name="grid",
                    accepted_produced_type=TypeRef(expr='tkinter.Widget'),
                    params=(
                        MountParamSpec(name="row", annotation=TypeRef(expr='int'), keyed=True, default_repr=None),
                        MountParamSpec(name="column", annotation=TypeRef(expr='int'), keyed=True, default_repr=None),
                        MountParamSpec(name="rowspan", annotation=TypeRef(expr='int'), keyed=False, default_repr='1'),
                        MountParamSpec(name="columnspan", annotation=TypeRef(expr='int'), keyed=False, default_repr='1'),
                        MountParamSpec(name="sticky", annotation=TypeRef(expr='Any'), keyed=False, default_repr='None'),
                        MountParamSpec(name="padx", annotation=TypeRef(expr='Any'), keyed=False, default_repr='None'),
                        MountParamSpec(name="pady", annotation=TypeRef(expr='Any'), keyed=False, default_repr='None'),
                    ),
                    min_children=0,
                    max_children=1,
                    apply_method_name='grid',
                    sync_method_name=None,
                    place_method_name=None,
                    append_method_name=None,
                    detach_method_name='grid_forget',
                    replay_kind=MountReplayKind.NONE,
                    prefer_sync=False,
                ),
            }),
            default_child_mount_point_name='pack',
            default_attach_mount_point_names=('pack',),
            child_policy=ChildPolicy.NONE,
        ),
        'ttk_Label': UiWidgetSpec(
            kind="ttk_Label",
            mounted_type_name="tkinter.ttk.Label",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "anchor": UiPropSpec(name="anchor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "background": UiPropSpec(name="background", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "borderwidth": UiPropSpec(name="borderwidth", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "compound": UiPropSpec(name="compound", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "font": UiPropSpec(name="font", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "foreground": UiPropSpec(name="foreground", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "image": UiPropSpec(name="image", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "justify": UiPropSpec(name="justify", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "padding": UiPropSpec(name="padding", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "relief": UiPropSpec(name="relief", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "state": UiPropSpec(name="state", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "text": UiPropSpec(name="text", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "textvariable": UiPropSpec(name="textvariable", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "underline": UiPropSpec(name="underline", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "width": UiPropSpec(name="width", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "wraplength": UiPropSpec(name="wraplength", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
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
        'ttk_Menubutton': UiWidgetSpec(
            kind="ttk_Menubutton",
            mounted_type_name="tkinter.ttk.Menubutton",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "compound": UiPropSpec(name="compound", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "direction": UiPropSpec(name="direction", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "image": UiPropSpec(name="image", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "justify": UiPropSpec(name="justify", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "menu": UiPropSpec(name="menu", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
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
            }),
            mount_points=frozendict({
            }),
            default_child_mount_point_name=None,
            default_attach_mount_point_names=(),
            child_policy=ChildPolicy.NONE,
        ),
        'ttk_OptionMenu': UiWidgetSpec(
            kind="ttk_OptionMenu",
            mounted_type_name="tkinter.ttk.OptionMenu",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr=None),
                "variable": UiParamSpec(name="variable", annotation=None, default_repr=None),
                "default": UiParamSpec(name="default", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "variable": UiPropSpec(name="variable", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='variable', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "default": UiPropSpec(name="default", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='default', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
            }),
            methods=frozendict({
                "set_menu": UiMethodSpec(
                    name="set_menu",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="default", annotation=None, default_repr='None'),
                    ),
                    source_props=("_menu",),
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
        grid = MountSelector.named("grid")
        pack = MountSelector.named("pack")

    @classmethod
    # NOTE: a trailing `kwds` parameter enables PyRolyze's tail kwds optimization.
    # The compiler lowers matching wrappers so only actually passed arguments
    # are forwarded into `UIElement.props`. See
    # docs/design/Packed_Kwds_UI_Interface_Optimization.md.
    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
        return UIElement(kind=kind, props=dict(kwds))

    @classmethod
    @pyrolyze
    # NOTE: original signature for Frame includes omitted variadic arguments
    def CTtkFrame(
        cls,
        *,
        borderwidth: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ttk_Frame",
            borderwidth=borderwidth,
            cursor=cursor,
            height=height,
            padding=padding,
            relief=relief,
            style=style,
            takefocus=takefocus,
            width=width,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for Label includes omitted variadic arguments
    def CTtkLabel(
        cls,
        master = None,
        *,
        anchor: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        compound: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        image: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        wraplength: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ttk_Label",
            master=master,
            anchor=anchor,
            background=background,
            borderwidth=borderwidth,
            compound=compound,
            cursor=cursor,
            font=font,
            foreground=foreground,
            image=image,
            justify=justify,
            padding=padding,
            relief=relief,
            state=state,
            style=style,
            takefocus=takefocus,
            text=text,
            textvariable=textvariable,
            underline=underline,
            width=width,
            wraplength=wraplength,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for Menubutton includes omitted variadic arguments
    def CTtkMenubutton(
        cls,
        master = None,
        *,
        compound: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        direction: Any | MissingType = MISSING,
        image: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        menu: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ttk_Menubutton",
            master=master,
            compound=compound,
            cursor=cursor,
            direction=direction,
            image=image,
            justify=justify,
            menu=menu,
            padding=padding,
            state=state,
            style=style,
            takefocus=takefocus,
            text=text,
            textvariable=textvariable,
            underline=underline,
            width=width,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for OptionMenu includes omitted variadic arguments
    def CTtkOptionMenu(
        cls,
        master,
        variable,
        default = None,
        *,
        _menu: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="ttk_OptionMenu",
            master=master,
            variable=variable,
            default=default,
            _menu=_menu,
        )

GENERATION = '8c4455212261e06ca5ca7fbd9961384c9702ac4fe65ccefabb5dd8135d9fb826'
