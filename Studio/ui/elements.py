#@pyrolyze
from __future__ import annotations

from typing import Callable

from pyrolyze.api import UIElement, call_native, pyrolyse


@pyrolyse
def section(title: str, *, accent: str = "blue", visible: bool = True) -> None:
    call_native(UIElement)(
        kind="section",
        props={
            "title": title,
            "accent": accent,
            "visible": bool(visible),
        },
    )


@pyrolyse
def row(row_id: str, *, headline: str, visible: bool = True) -> None:
    call_native(UIElement)(
        kind="row",
        props={
            "row_id": row_id,
            "headline": headline,
            "visible": bool(visible),
        },
    )


@pyrolyse
def badge(text: str, *, tone: str = "info", visible: bool = True) -> None:
    call_native(UIElement)(
        kind="badge",
        props={
            "text": text,
            "tone": tone,
            "visible": bool(visible),
        },
    )


@pyrolyse
def button(
    label: str,
    *,
    on_press: Callable[[], None],
    enabled: bool = True,
    tone: str = "default",
    visible: bool = True,
) -> None:
    call_native(UIElement)(
        kind="button",
        props={
            "label": label,
            "enabled": bool(enabled),
            "tone": tone,
            "visible": bool(visible),
            "on_press": on_press,
        },
    )


@pyrolyse
def text_field(
    field_id: str,
    label: str,
    value: str,
    *,
    on_change: Callable[[str], None],
    enabled: bool = True,
    placeholder: str | None = None,
    visible: bool = True,
) -> None:
    call_native(UIElement)(
        kind="text_field",
        props={
            "field_id": field_id,
            "label": label,
            "value": value,
            "enabled": bool(enabled),
            "placeholder": placeholder,
            "visible": bool(visible),
            "on_change": on_change,
        },
    )


@pyrolyse
def toggle(
    field_id: str,
    label: str,
    checked: bool,
    *,
    on_toggle: Callable[[bool], None],
    enabled: bool = True,
    visible: bool = True,
) -> None:
    call_native(UIElement)(
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


@pyrolyse
def select_field(
    field_id: str,
    label: str,
    value: str,
    *,
    options: tuple[str, ...],
    on_change: Callable[[str], None],
    enabled: bool = True,
    visible: bool = True,
) -> None:
    call_native(UIElement)(
        kind="select_field",
        props={
            "field_id": field_id,
            "label": label,
            "value": value,
            "options": options,
            "enabled": bool(enabled),
            "visible": bool(visible),
            "on_change": on_change,
        },
    )
