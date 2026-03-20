#@pyrolyze
from __future__ import annotations

#
# NOTE:
# This module is the regular author-style PyRolyze source-form mirror of the
# standard helper surface.
#
# The runtime/canonical implementation currently lives in `elements_pyr.py`
# because that file provides pre-lowered component refs that are import-safe
# even when the import hook is disabled.
#
# Use `from pyrolyze.ui import ...` in application code.
#

from pyrolyze.api import PyrolyzeHandler, UIElement, call_native, pyrolyse


@pyrolyse
def section(
    title: str,
    *,
    accent: str = "blue",
    visible: bool = True,
) -> None:
    call_native(UIElement)(
        kind="section",
        props={
            "title": title,
            "accent": accent,
            "visible": bool(visible),
        },
    )


@pyrolyse
def row(
    row_id: str,
    *,
    headline: str,
    visible: bool = True,
) -> None:
    call_native(UIElement)(
        kind="row",
        props={
            "row_id": row_id,
            "headline": headline,
            "visible": bool(visible),
        },
    )


@pyrolyse
def badge(
    text: str,
    *,
    tone: str = "info",
    visible: bool = True,
) -> None:
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
    on_press: PyrolyzeHandler[[], None],
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
    on_change: PyrolyzeHandler[[str], None],
    on_submit: PyrolyzeHandler[[], None] | None = None,
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
            "on_submit": on_submit,
        },
    )


@pyrolyse
def toggle(
    field_id: str,
    label: str,
    checked: bool,
    *,
    on_toggle: PyrolyzeHandler[[bool], None],
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
    on_change: PyrolyzeHandler[[str], None],
    enabled: bool = True,
    visible: bool = True,
) -> None:
    call_native(UIElement)(
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


__all__ = [
    "badge",
    "button",
    "row",
    "section",
    "select_field",
    "text_field",
    "toggle",
]
