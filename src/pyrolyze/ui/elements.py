from __future__ import annotations

from pyrolyze.api import (
    CallFromNonPyrolyzeContext,
    ComponentMetadata,
    PyrolyzeHandler,
    UIElement,
    pyrolyze_component_ref,
)


def __pyr_section(
    __pyr_ctx: object,
    __pyr_dirty_state: object,
    title: str,
    *,
    accent: str = "blue",
    visible: bool = True,
) -> None:
    del __pyr_dirty_state
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="section",
            props={
                "title": title,
                "accent": accent,
                "visible": bool(visible),
            },
        )


@pyrolyze_component_ref(ComponentMetadata("section", __pyr_section))
def section(
    title: str,
    *,
    accent: str = "blue",
    visible: bool = True,
) -> None:
    raise CallFromNonPyrolyzeContext("section")


def __pyr_row(
    __pyr_ctx: object,
    __pyr_dirty_state: object,
    row_id: str,
    *,
    headline: str,
    visible: bool = True,
) -> None:
    del __pyr_dirty_state
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="row",
            props={
                "row_id": row_id,
                "headline": headline,
                "visible": bool(visible),
            },
        )


@pyrolyze_component_ref(ComponentMetadata("row", __pyr_row))
def row(
    row_id: str,
    *,
    headline: str,
    visible: bool = True,
) -> None:
    raise CallFromNonPyrolyzeContext("row")


def __pyr_badge(
    __pyr_ctx: object,
    __pyr_dirty_state: object,
    text: str,
    *,
    tone: str = "info",
    visible: bool = True,
) -> None:
    del __pyr_dirty_state
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="badge",
            props={
                "text": text,
                "tone": tone,
                "visible": bool(visible),
            },
        )


@pyrolyze_component_ref(ComponentMetadata("badge", __pyr_badge))
def badge(
    text: str,
    *,
    tone: str = "info",
    visible: bool = True,
) -> None:
    raise CallFromNonPyrolyzeContext("badge")


def __pyr_button(
    __pyr_ctx: object,
    __pyr_dirty_state: object,
    label: str,
    *,
    on_press: PyrolyzeHandler[[], None],
    enabled: bool = True,
    tone: str = "default",
    visible: bool = True,
) -> None:
    del __pyr_dirty_state
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="button",
            props={
                "label": label,
                "enabled": bool(enabled),
                "tone": tone,
                "visible": bool(visible),
                "on_press": on_press,
            },
        )


@pyrolyze_component_ref(ComponentMetadata("button", __pyr_button))
def button(
    label: str,
    *,
    on_press: PyrolyzeHandler[[], None],
    enabled: bool = True,
    tone: str = "default",
    visible: bool = True,
) -> None:
    raise CallFromNonPyrolyzeContext("button")


def __pyr_text_field(
    __pyr_ctx: object,
    __pyr_dirty_state: object,
    field_id: str,
    label: str,
    value: str,
    *,
    on_change: PyrolyzeHandler[[str], None],
    on_submit: PyrolyzeHandler[[], None] | None = None,
    enabled: bool = True,
    placeholder: str | None = None,
    visible: bool = True,
) -> None:
    del __pyr_dirty_state
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="text_field",
            props={
                "field_id": field_id,
                "label": label,
                "value": value,
                "enabled": bool(enabled),
                "placeholder": placeholder,
                "visible": bool(visible),
                "on_change": on_change,
                "on_submit": on_submit,
            },
        )


@pyrolyze_component_ref(ComponentMetadata("text_field", __pyr_text_field))
def text_field(
    field_id: str,
    label: str,
    value: str,
    *,
    on_change: PyrolyzeHandler[[str], None],
    on_submit: PyrolyzeHandler[[], None] | None = None,
    enabled: bool = True,
    placeholder: str | None = None,
    visible: bool = True,
) -> None:
    raise CallFromNonPyrolyzeContext("text_field")


def __pyr_toggle(
    __pyr_ctx: object,
    __pyr_dirty_state: object,
    field_id: str,
    label: str,
    checked: bool,
    *,
    on_toggle: PyrolyzeHandler[[bool], None],
    enabled: bool = True,
    visible: bool = True,
) -> None:
    del __pyr_dirty_state
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="toggle",
            props={
                "field_id": field_id,
                "label": label,
                "checked": bool(checked),
                "enabled": bool(enabled),
                "visible": bool(visible),
                "on_toggle": on_toggle,
            },
        )


@pyrolyze_component_ref(ComponentMetadata("toggle", __pyr_toggle))
def toggle(
    field_id: str,
    label: str,
    checked: bool,
    *,
    on_toggle: PyrolyzeHandler[[bool], None],
    enabled: bool = True,
    visible: bool = True,
) -> None:
    raise CallFromNonPyrolyzeContext("toggle")


def __pyr_select_field(
    __pyr_ctx: object,
    __pyr_dirty_state: object,
    field_id: str,
    label: str,
    value: str,
    *,
    options: tuple[str, ...],
    on_change: PyrolyzeHandler[[str], None],
    enabled: bool = True,
    visible: bool = True,
) -> None:
    del __pyr_dirty_state
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="select_field",
            props={
                "field_id": field_id,
                "label": label,
                "value": value,
                "options": tuple(options),
                "enabled": bool(enabled),
                "visible": bool(visible),
                "on_change": on_change,
            },
        )


@pyrolyze_component_ref(ComponentMetadata("select_field", __pyr_select_field))
def select_field(
    field_id: str,
    label: str,
    value: str,
    *,
    options: tuple[str, ...],
    on_change: PyrolyzeHandler[[str], None],
    enabled: bool = True,
    visible: bool = True,
) -> None:
    raise CallFromNonPyrolyzeContext("select_field")


__all__ = [
    "badge",
    "button",
    "row",
    "section",
    "select_field",
    "text_field",
    "toggle",
]
