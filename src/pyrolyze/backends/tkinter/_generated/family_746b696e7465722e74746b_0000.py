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
            "CCombobox": UiInterfaceEntry(public_name="CCombobox", kind="Combobox"),
            "CLabeledScale": UiInterfaceEntry(public_name="CLabeledScale", kind="LabeledScale"),
            "CLabelframe": UiInterfaceEntry(public_name="CLabelframe", kind="Labelframe"),
            "CNotebook": UiInterfaceEntry(public_name="CNotebook", kind="Notebook"),
        }),
    )

    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({
        'Combobox': UiWidgetSpec(
            kind="Combobox",
            mounted_type_name="tkinter.ttk.Combobox",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "background": UiPropSpec(name="background", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "exportselection": UiPropSpec(name="exportselection", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "font": UiPropSpec(name="font", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "foreground": UiPropSpec(name="foreground", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "height": UiPropSpec(name="height", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "invalidcommand": UiPropSpec(name="invalidcommand", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "justify": UiPropSpec(name="justify", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "placeholder": UiPropSpec(name="placeholder", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "placeholderforeground": UiPropSpec(name="placeholderforeground", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "postcommand": UiPropSpec(name="postcommand", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "show": UiPropSpec(name="show", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "state": UiPropSpec(name="state", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "textvariable": UiPropSpec(name="textvariable", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "validate": UiPropSpec(name="validate", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "validatecommand": UiPropSpec(name="validatecommand", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "values": UiPropSpec(name="values", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "width": UiPropSpec(name="width", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
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
        'LabeledScale': UiWidgetSpec(
            kind="LabeledScale",
            mounted_type_name="tkinter.ttk.LabeledScale",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
                "variable": UiParamSpec(name="variable", annotation=None, default_repr='None'),
                "from_": UiParamSpec(name="from_", annotation=None, default_repr='0'),
                "to": UiParamSpec(name="to", annotation=None, default_repr='10'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "variable": UiPropSpec(name="variable", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='variable', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "from_": UiPropSpec(name="from_", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='from_', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "to": UiPropSpec(name="to", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='to', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
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
            }),
            default_child_mount_point_name=None,
            default_attach_mount_point_names=(),
            child_policy=ChildPolicy.NONE,
        ),
        'Labelframe': UiWidgetSpec(
            kind="Labelframe",
            mounted_type_name="tkinter.ttk.Labelframe",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "master": UiPropSpec(name="master", annotation=None, mode=PropMode.CREATE_ONLY_REMOUNT, constructor_name='master', setter_kind=None, setter_name=None, getter_kind=None, getter_name=None, affects_identity=True),
                "borderwidth": UiPropSpec(name="borderwidth", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "height": UiPropSpec(name="height", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "labelanchor": UiPropSpec(name="labelanchor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "labelwidget": UiPropSpec(name="labelwidget", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "padding": UiPropSpec(name="padding", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "relief": UiPropSpec(name="relief", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "text": UiPropSpec(name="text", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "underline": UiPropSpec(name="underline", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
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
        'Notebook': UiWidgetSpec(
            kind="Notebook",
            mounted_type_name="tkinter.ttk.Notebook",
            constructor_params=frozendict({
                "master": UiParamSpec(name="master", annotation=None, default_repr='None'),
            }),
            props=frozendict({
                "cursor": UiPropSpec(name="cursor", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "height": UiPropSpec(name="height", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "padding": UiPropSpec(name="padding", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "style": UiPropSpec(name="style", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "takefocus": UiPropSpec(name="takefocus", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
                "width": UiPropSpec(name="width", annotation=TypeRef(expr='Any'), mode=PropMode.CREATE_UPDATE, constructor_name=None, setter_kind=AccessorKind.TK_CONFIG, setter_name="configure", getter_kind=AccessorKind.TK_CONFIG, getter_name="cget", affects_identity=False),
            }),
            methods=frozendict({
            }),
            events=frozendict({
            }),
            mount_points=frozendict({
                "tab": MountPointSpec(
                    name="tab",
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
            default_child_mount_point_name='tab',
            default_attach_mount_point_names=('tab',),
            child_policy=ChildPolicy.NONE,
        ),
    })

    class mounts:
        grid = MountSelector.named("grid")
        pack = MountSelector.named("pack")
        tab = MountSelector.named("tab")

    @classmethod
    # NOTE: a trailing `kwds` parameter enables PyRolyze's tail kwds optimization.
    # The compiler lowers matching wrappers so only actually passed arguments
    # are forwarded into `UIElement.props`. See
    # docs/design/Packed_Kwds_UI_Interface_Optimization.md.
    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
        return UIElement(kind=kind, props=dict(kwds))

    @classmethod
    @pyrolyze
    # NOTE: original signature for Combobox includes omitted variadic arguments
    def CCombobox(
        cls,
        master = None,
        *,
        background: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        exportselection: Any | MissingType = MISSING,
        font: Any | MissingType = MISSING,
        foreground: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        invalidcommand: Any | MissingType = MISSING,
        justify: Any | MissingType = MISSING,
        placeholder: Any | MissingType = MISSING,
        placeholderforeground: Any | MissingType = MISSING,
        postcommand: Any | MissingType = MISSING,
        show: Any | MissingType = MISSING,
        state: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        textvariable: Any | MissingType = MISSING,
        validate: Any | MissingType = MISSING,
        validatecommand: Any | MissingType = MISSING,
        values: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
        xscrollcommand: Any | MissingType = MISSING,
        value: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="Combobox",
            master=master,
            background=background,
            cursor=cursor,
            exportselection=exportselection,
            font=font,
            foreground=foreground,
            height=height,
            invalidcommand=invalidcommand,
            justify=justify,
            placeholder=placeholder,
            placeholderforeground=placeholderforeground,
            postcommand=postcommand,
            show=show,
            state=state,
            style=style,
            takefocus=takefocus,
            textvariable=textvariable,
            validate=validate,
            validatecommand=validatecommand,
            values=values,
            width=width,
            xscrollcommand=xscrollcommand,
            value=value,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for LabeledScale includes omitted variadic arguments
    def CLabeledScale(
        cls,
        master = None,
        variable = None,
        from_ = 0,
        to = 10,
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
            kind="LabeledScale",
            master=master,
            variable=variable,
            from_=from_,
            to=to,
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
    # NOTE: original signature for Labelframe includes omitted variadic arguments
    def CLabelframe(
        cls,
        master = None,
        *,
        borderwidth: Any | MissingType = MISSING,
        cursor: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        labelanchor: Any | MissingType = MISSING,
        labelwidget: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        relief: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        text: Any | MissingType = MISSING,
        underline: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="Labelframe",
            master=master,
            borderwidth=borderwidth,
            cursor=cursor,
            height=height,
            labelanchor=labelanchor,
            labelwidget=labelwidget,
            padding=padding,
            relief=relief,
            style=style,
            takefocus=takefocus,
            text=text,
            underline=underline,
            width=width,
        )

    @classmethod
    @pyrolyze
    # NOTE: original signature for Notebook includes omitted variadic arguments
    def CNotebook(
        cls,
        *,
        cursor: Any | MissingType = MISSING,
        height: Any | MissingType = MISSING,
        padding: Any | MissingType = MISSING,
        style: Any | MissingType = MISSING,
        takefocus: Any | MissingType = MISSING,
        width: Any | MissingType = MISSING,
    ) -> None:
        call_native(cls.__element)(
            kind="Notebook",
            cursor=cursor,
            height=height,
            padding=padding,
            style=style,
            takefocus=takefocus,
            width=width,
        )

GENERATION = '8c4455212261e06ca5ca7fbd9961384c9702ac4fe65ccefabb5dd8135d9fb826'
