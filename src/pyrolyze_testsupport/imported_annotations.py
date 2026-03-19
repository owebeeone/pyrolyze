from __future__ import annotations

from pyrolyze.api import (
    CallFromNonPyrolyzeContext,
    ComponentMetadata,
    PyrolyzeHandler,
    UIElement,
    pyrolyze_component_ref,
    pyrolyze_slotted,
)


LOG: list[tuple[object, ...]] = []


def reset_logs() -> None:
    LOG.clear()


@pyrolyze_slotted
def imported_upper(label: str) -> str:
    LOG.append(("upper", label))
    return label.upper()


def imported_badge(text: str, *, tone: str) -> None:
    LOG.append(("badge", text, tone))


def __pyr_imported_child(__pyr_ctx, __pyr_dirty_state, text: str) -> None:
    with __pyr_ctx.pass_scope():
        imported_badge(text, tone="info")


@pyrolyze_component_ref(ComponentMetadata("imported_child", __pyr_imported_child))
def imported_child(text: str) -> None:
    raise CallFromNonPyrolyzeContext("imported_child")


def __pyr_imported_button(
    __pyr_ctx,
    __pyr_dirty_state,
    label: str,
    *,
    on_press: PyrolyzeHandler[[], None] | None = None,
) -> None:
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="button",
            props={"label": label, "on_press": on_press},
        )


@pyrolyze_component_ref(ComponentMetadata("imported_button", __pyr_imported_button))
def imported_button(
    label: str,
    *,
    on_press: PyrolyzeHandler[[], None] | None = None,
) -> None:
    raise CallFromNonPyrolyzeContext("imported_button")
