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
            "CScrolledtextScrolledText": UiInterfaceEntry(public_name="CScrolledtextScrolledText", kind="scrolledtext_ScrolledText"),
        }),
    )

    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({
        'scrolledtext_ScrolledText': UiWidgetSpec(
            kind="scrolledtext_ScrolledText",
            mounted_type_name="tkinter.scrolledtext.ScrolledText",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "autoseparators": UiPropSpec(name="autoseparators", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "background": UiPropSpec(name="background", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "bd": UiPropSpec(name="bd", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "bg": UiPropSpec(name="bg", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "blockcursor": UiPropSpec(name="blockcursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "borderwidth": UiPropSpec(name="borderwidth", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "endline": UiPropSpec(name="endline", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "exportselection": UiPropSpec(name="exportselection", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "fg": UiPropSpec(name="fg", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "font": UiPropSpec(name="font", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "foreground": UiPropSpec(name="foreground", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "height": UiPropSpec(name="height", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "highlightbackground": UiPropSpec(name="highlightbackground", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "highlightcolor": UiPropSpec(name="highlightcolor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "highlightthickness": UiPropSpec(name="highlightthickness", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "inactiveselectbackground": UiPropSpec(name="inactiveselectbackground", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "insertbackground": UiPropSpec(name="insertbackground", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "insertborderwidth": UiPropSpec(name="insertborderwidth", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "insertofftime": UiPropSpec(name="insertofftime", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "insertontime": UiPropSpec(name="insertontime", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "insertunfocussed": UiPropSpec(name="insertunfocussed", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "insertwidth": UiPropSpec(name="insertwidth", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "maxundo": UiPropSpec(name="maxundo", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "padx": UiPropSpec(name="padx", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "pady": UiPropSpec(name="pady", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "relief": UiPropSpec(name="relief", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "selectbackground": UiPropSpec(name="selectbackground", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "selectborderwidth": UiPropSpec(name="selectborderwidth", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "selectforeground": UiPropSpec(name="selectforeground", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "setgrid": UiPropSpec(name="setgrid", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "spacing1": UiPropSpec(name="spacing1", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "spacing2": UiPropSpec(name="spacing2", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "spacing3": UiPropSpec(name="spacing3", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "startline": UiPropSpec(name="startline", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "state": UiPropSpec(name="state", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "tabs": UiPropSpec(name="tabs", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "tabstyle": UiPropSpec(name="tabstyle", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "undo": UiPropSpec(name="undo", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "width": UiPropSpec(name="width", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "wrap": UiPropSpec(name="wrap", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "xscrollcommand": UiPropSpec(name="xscrollcommand", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "yscrollcommand": UiPropSpec(name="yscrollcommand", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
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
    # NOTE: original signature for ScrolledText includes omitted variadic arguments
    def CScrolledtextScrolledText(
        cls,
        master = None,
        *,
        autoseparators: Any | MissingType = MISSING,
        background: Any | MissingType = MISSING,
        bd: Any | MissingType = MISSING,
        bg: Any | MissingType = MISSING,
        blockcursor: Any | MissingType = MISSING,
        borderwidth: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        endline: Any | MissingType = MISSING,
        exportselection: Any | MissingType = MISSING,
        fg: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        highlightbackground: Any | MissingType = MISSING,
        highlightcolor: Any | MissingType = MISSING,
        highlightthickness: Any | MissingType = MISSING,
        inactiveselectbackground: Any | MissingType = MISSING,
        insertbackground: Any | MissingType = MISSING,
        insertborderwidth: Any | MissingType = MISSING,
        insertofftime: Any | MissingType = MISSING,
        insertontime: Any | MissingType = MISSING,
        insertunfocussed: Any | MissingType = MISSING,
        insertwidth: Any | MissingType = MISSING,
        maxundo: Any | MissingType = MISSING,
        padx: Any | MissingType = MISSING,
        pady: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        selectbackground: Any | MissingType = MISSING,
        selectborderwidth: Any | MissingType = MISSING,
        selectforeground: Any | MissingType = MISSING,
        setgrid: Any | MissingType = MISSING,
        spacing1: Any | MissingType = MISSING,
        spacing2: Any | MissingType = MISSING,
        spacing3: Any | MissingType = MISSING,
        startline: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        tabs: Any | MissingType = MISSING,
        tabstyle: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        undo: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        wrap: Any | MissingType = MISSING,
        xscrollcommand: Any | MissingType = MISSING,
        yscrollcommand: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="scrolledtext_ScrolledText",
            master=master,
            autoseparators=autoseparators,
            background=background,
            bd=bd,
            bg=bg,
            blockcursor=blockcursor,
            borderwidth=borderwidth,
            cursor=cursor,
            endline=endline,
            exportselection=exportselection,
            fg=fg,
            font=font,
            foreground=foreground,
            height=height,
            highlightbackground=highlightbackground,
            highlightcolor=highlightcolor,
            highlightthickness=highlightthickness,
            inactiveselectbackground=inactiveselectbackground,
            insertbackground=insertbackground,
            insertborderwidth=insertborderwidth,
            insertofftime=insertofftime,
            insertontime=insertontime,
            insertunfocussed=insertunfocussed,
            insertwidth=insertwidth,
            maxundo=maxundo,
            padx=padx,
            pady=pady,
            relief=relief,
            selectbackground=selectbackground,
            selectborderwidth=selectborderwidth,
            selectforeground=selectforeground,
            setgrid=setgrid,
            spacing1=spacing1,
            spacing2=spacing2,
            spacing3=spacing3,
            startline=startline,
            state=state,
            tabs=tabs,
            tabstyle=tabstyle,
            takefocus=takefocus,
            undo=undo,
            width=width,
            wrap=wrap,
            xscrollcommand=xscrollcommand,
            yscrollcommand=yscrollcommand,
        )

GENERATION = '8c4455212261e06ca5ca7fbd9961384c9702ac4fe65ccefabb5dd8135d9fb826'
