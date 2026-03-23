from __future__ import annotations

import pytest

from pyrolyze.api import MountSelector, PyrolyzeMountAdvertisementRequest
from pyrolyze.runtime import (
    DuplicateMountAdvertisementError,
    ModuleRegistry,
    PlainCallSlotContext,
    PyrolyzeMountAdvertisementBinding,
    RenderContext,
    SlotId,
)


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.mount_advert_binding")

_ADVERT_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_FIRST_DUPLICATE_SLOT = SlotId(_MODULE_ID, 2, line_no=11)
_SECOND_DUPLICATE_SLOT = SlotId(_MODULE_ID, 3, line_no=12)


def _advert_request(
    key: object,
    *selectors: MountSelector,
    default: bool = False,
) -> PyrolyzeMountAdvertisementRequest:
    return PyrolyzeMountAdvertisementRequest(
        key=key,
        selectors=tuple(selectors),
        default=default,
    )


def test_mount_advert_binding_commits_and_deactivates_publication() -> None:
    ctx = RenderContext()
    menu = MountSelector.named("menu")

    with ctx.pass_scope():
        _ = ctx.call_plain(_ADVERT_SLOT, _advert_request, "body", menu, default=True)

    advertisements = ctx.debug_mount_advertisements()
    assert len(advertisements) == 1
    assert advertisements[0].key == "body"
    assert advertisements[0].selectors == (menu,)
    assert advertisements[0].default is True
    assert advertisements[0].source_slot_id == _ADVERT_SLOT
    assert advertisements[0].surface_owner_id is None

    slot = ctx._slots_by_id[_ADVERT_SLOT]
    assert isinstance(slot, PlainCallSlotContext)
    assert isinstance(slot.binding, PyrolyzeMountAdvertisementBinding)

    with ctx.pass_scope():
        pass

    assert ctx.debug_mount_advertisements() == ()


def test_mount_advert_binding_rollback_discards_staged_publication() -> None:
    ctx = RenderContext()
    menu = MountSelector.named("menu")

    with ctx.pass_scope():
        _ = ctx.call_plain(_ADVERT_SLOT, _advert_request, "body", menu)

    with pytest.raises(RuntimeError, match="boom"):
        with ctx.pass_scope():
            _ = ctx.call_plain(_ADVERT_SLOT, _advert_request, "next", menu, default=True)
            raise RuntimeError("boom")

    advertisements = ctx.debug_mount_advertisements()
    assert len(advertisements) == 1
    assert advertisements[0].key == "body"
    assert advertisements[0].default is False


def test_duplicate_mount_advertisement_keys_raise_without_committing_partial_state() -> None:
    ctx = RenderContext()

    with pytest.raises(DuplicateMountAdvertisementError, match="duplicate mount advertisement key"):
        with ctx.pass_scope():
            _ = ctx.call_plain(_FIRST_DUPLICATE_SLOT, _advert_request, "body")
            _ = ctx.call_plain(_SECOND_DUPLICATE_SLOT, _advert_request, "body")

    assert ctx.debug_mount_advertisements() == ()


def test_duplicate_mount_advertisement_defaults_raise_without_committing_partial_state() -> None:
    ctx = RenderContext()

    with pytest.raises(DuplicateMountAdvertisementError, match="duplicate default mount advertisement"):
        with ctx.pass_scope():
            _ = ctx.call_plain(_FIRST_DUPLICATE_SLOT, _advert_request, "left", default=True)
            _ = ctx.call_plain(_SECOND_DUPLICATE_SLOT, _advert_request, "right", default=True)

    assert ctx.debug_mount_advertisements() == ()
