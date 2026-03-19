from __future__ import annotations

from pyrolyze.api import (
    CallFromNonPyrolyzeContext,
    ComponentMetadata,
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
