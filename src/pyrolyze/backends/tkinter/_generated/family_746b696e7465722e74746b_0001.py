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
            "CPanedwindow": UiInterfaceEntry(public_name="CPanedwindow", kind="Panedwindow"),
            "CProgressbar": UiInterfaceEntry(public_name="CProgressbar", kind="Progressbar"),
            "CSeparator": UiInterfaceEntry(public_name="CSeparator", kind="Separator"),
            "CSizegrip": UiInterfaceEntry(public_name="CSizegrip", kind="Sizegrip"),
        }),
    )

    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({
        'Panedwindow': UiWidgetSpec(
            kind="Panedwindow",
            mounted_type_name="tkinter.ttk.Panedwindow",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "height": UiPropSpec(name="height", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "orient": UiPropSpec(name="orient", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "width": UiPropSpec(name="width", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
            }),
            methods=frozendict({
            }),
            events=frozendict({
            }),
            mount_points=frozendict({
                "pane": MountPointSpec(
                    name="pane",
                    accepted_produced_type=TypeRef(expr='tkinter.Widget'),
                    params=(
                    ),
                    min_children=0,
                    max_children=None,
                    apply_method_name=None,
                    sync_method_name=None,
                    place_method_name='insert',
                    append_method_name='add',
                    detach_method_name='forget',
                    replay_kind=MountReplayKind.INDEX,
                    prefer_sync=False,
                ),
            }),
            default_child_mount_point_name='pane',
            default_attach_mount_point_names=('pane',),
            child_policy=ChildPolicy.NONE,
        ),
        'Progressbar': UiWidgetSpec(
            kind="Progressbar",
            mounted_type_name="tkinter.ttk.Progressbar",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "anchor": UiPropSpec(name="anchor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "font": UiPropSpec(name="font", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "foreground": UiPropSpec(name="foreground", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "justify": UiPropSpec(name="justify", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "length": UiPropSpec(name="length", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "maximum": UiPropSpec(name="maximum", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "mode": UiPropSpec(name="mode", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "orient": UiPropSpec(name="orient", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "phase": UiPropSpec(name="phase", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "text": UiPropSpec(name="text", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "value": UiPropSpec(name="value", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "variable": UiPropSpec(name="variable", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
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
        'Separator': UiWidgetSpec(
            kind="Separator",
            mounted_type_name="tkinter.ttk.Separator",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "orient": UiPropSpec(name="orient", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
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
        'Sizegrip': UiWidgetSpec(
            kind="Sizegrip",
            mounted_type_name="tkinter.ttk.Sizegrip",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
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
    })

    class mounts:
        pane = MountSelector.named("pane")

    @classmethod
    # NOTE: a trailing `kwds` parameter enables PyRolyze's tail kwds optimization.
    # The compiler lowers matching wrappers so only actually passed arguments
    # are forwarded into `UIElement.props`. See
    # docs/design/Packed_Kwds_UI_Interface_Optimization.md.
    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
        return UIElement(kind=kind, props=dict(kwds))

    @classmethod
    @pyrolyze
    # NOTE: original signature for Panedwindow includes omitted variadic arguments
    def CPanedwindow(
        cls,
        *,
        cursor: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        orient: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="Panedwindow",
            cursor=cursor,
            height=height,
            orient=orient,
            style=style,
            takefocus=takefocus,
            width=width,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for Progressbar includes omitted variadic arguments
    def CProgressbar(
        cls,
        master = None,
        *,
        anchor: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        length: Any | MissingType = MISSING,
        maximum: Any | MissingType = MISSING,
        mode: Any | MissingType = MISSING,
        orient: Any | MissingType = MISSING,
        phase: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        value: Any | MissingType = MISSING,
        variable: Any | MissingType = MISSING,
        wraplength: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="Progressbar",
            master=master,
            anchor=anchor,
            cursor=cursor,
            font=font,
            foreground=foreground,
            justify=justify,
            length=length,
            maximum=maximum,
            mode=mode,
            orient=orient,
            phase=phase,
            style=style,
            takefocus=takefocus,
            text=text,
            value=value,
            variable=variable,
            wraplength=wraplength,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for Separator includes omitted variadic arguments
    def CSeparator(
        cls,
        master = None,
        *,
        cursor: Any | MissingType = MISSING,
        orient: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="Separator",
            master=master,
            cursor=cursor,
            orient=orient,
            style=style,
            takefocus=takefocus,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for Sizegrip includes omitted variadic arguments
    def CSizegrip(
        cls,
        master = None,
        *,
        cursor: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="Sizegrip",
            master=master,
            cursor=cursor,
            style=style,
            takefocus=takefocus,
        )

GENERATION = '8c4455212261e06ca5ca7fbd9961384c9702ac4fe65ccefabb5dd8135d9fb826'
