from __future__ import annotations

import pytest

from pyrolyze.api import MountSelector, PyrolyzeMountAdvertisement, UIElement, advertise_mount
from pyrolyze.runtime import (
    ContextBase,
    DuplicateMountAdvertisementError,
    MountAdvertisementContextError,
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
_CONTAINER_SLOT = SlotId(_MODULE_ID, 4, line_no=13)
_PLAIN_CONTAINER_SLOT = SlotId(_MODULE_ID, 5, line_no=14)
_LOOP_SLOT = SlotId(_MODULE_ID, 6, line_no=15)
_LOOP_ADVERT_SLOT = SlotId(_MODULE_ID, 7, line_no=16)

def _pyr_section(ctx: ContextBase, title: str) -> None:
    ctx.call_native(
        UIElement,
        kind="section",
        props={"title": title},
    )


def test_mount_advert_binding_commits_and_deactivates_publication() -> None:
    ctx = RenderContext()
    menu = MountSelector.named("menu")

    with ctx.pass_scope():
        with ctx.container_call(_CONTAINER_SLOT, _pyr_section, "Wrapper") as section_ctx:
            _ = section_ctx.call_plain(
                _ADVERT_SLOT,
                advertise_mount,
                "body",
                target=menu,
                default=True,
            )

    advertisements = ctx.debug_mount_advertisements()
    assert len(advertisements) == 1
    assert advertisements[0].key == "body"
    assert advertisements[0].selectors == (menu,)
    assert advertisements[0].default is True
    assert advertisements[0].source_slot_id == _ADVERT_SLOT
    assert advertisements[0].surface_owner_id == _CONTAINER_SLOT
    assert advertisements[0].mount_owner_id == _CONTAINER_SLOT
    assert ctx.debug_ui() == (
        UIElement(
            kind="section",
            props={"title": "Wrapper"},
            children=(
                PyrolyzeMountAdvertisement(
                    key="body",
                    selectors=(menu,),
                    default=True,
                ),
            ),
        ),
    )

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
        with ctx.container_call(_CONTAINER_SLOT, _pyr_section, "Wrapper") as section_ctx:
            _ = section_ctx.call_plain(
                _ADVERT_SLOT,
                advertise_mount,
                "body",
                target=menu,
            )

    with pytest.raises(RuntimeError, match="boom"):
        with ctx.pass_scope():
            with ctx.container_call(_CONTAINER_SLOT, _pyr_section, "Wrapper") as section_ctx:
                _ = section_ctx.call_plain(
                    _ADVERT_SLOT,
                    advertise_mount,
                    "next",
                    target=menu,
                    default=True,
                )
                raise RuntimeError("boom")

    advertisements = ctx.debug_mount_advertisements()
    assert len(advertisements) == 1
    assert advertisements[0].key == "body"
    assert advertisements[0].default is False


def test_duplicate_mount_advertisement_keys_raise_without_committing_partial_state() -> None:
    ctx = RenderContext()

    with pytest.raises(DuplicateMountAdvertisementError, match="duplicate mount advertisement key"):
        with ctx.pass_scope():
            with ctx.container_call(_CONTAINER_SLOT, _pyr_section, "Wrapper") as section_ctx:
                _ = section_ctx.call_plain(_FIRST_DUPLICATE_SLOT, advertise_mount, "body")
                _ = section_ctx.call_plain(_SECOND_DUPLICATE_SLOT, advertise_mount, "body")

    assert ctx.debug_mount_advertisements() == ()


def test_duplicate_mount_advertisement_defaults_raise_without_committing_partial_state() -> None:
    ctx = RenderContext()

    with pytest.raises(DuplicateMountAdvertisementError, match="duplicate default mount advertisement"):
        with ctx.pass_scope():
            with ctx.container_call(_CONTAINER_SLOT, _pyr_section, "Wrapper") as section_ctx:
                _ = section_ctx.call_plain(
                    _FIRST_DUPLICATE_SLOT,
                    advertise_mount,
                    "left",
                    default=True,
                )
                _ = section_ctx.call_plain(
                    _SECOND_DUPLICATE_SLOT,
                    advertise_mount,
                    "right",
                    default=True,
                )

    assert ctx.debug_mount_advertisements() == ()


def test_advertise_mount_rejects_root_render_context_owner() -> None:
    ctx = RenderContext()

    with pytest.raises(MountAdvertisementContextError, match="native container owner"):
        with ctx.pass_scope():
            _ = ctx.call_plain(_ADVERT_SLOT, advertise_mount, "body")


def test_advertise_mount_rejects_non_native_container_owner() -> None:
    ctx = RenderContext()

    with pytest.raises(MountAdvertisementContextError, match="native container node owner"):
        with ctx.pass_scope():
            with ctx.container_call(_PLAIN_CONTAINER_SLOT, len, [1, 2, 3]) as plain_ctx:
                _ = plain_ctx.call_plain(_ADVERT_SLOT, advertise_mount, "body")


def test_advertise_mount_resolves_enclosing_native_container_through_loop_scopes() -> None:
    ctx = RenderContext()
    menu = MountSelector.named("menu")

    with ctx.pass_scope():
        with ctx.container_call(_CONTAINER_SLOT, _pyr_section, "Wrapper") as section_ctx:
            for item_ctx in section_ctx.keyed_loop(_LOOP_SLOT, ["a"], key_fn=lambda value: value):
                with item_ctx.pass_scope():
                    _ = item_ctx.call_plain(
                        _LOOP_ADVERT_SLOT,
                        advertise_mount,
                        "body",
                        target=menu,
                        default=True,
                    )

    advertisements = ctx.debug_mount_advertisements()
    assert len(advertisements) == 1
    assert advertisements[0].key == "body"
    assert advertisements[0].selectors == (menu,)
    assert advertisements[0].surface_owner_id == _CONTAINER_SLOT
    assert advertisements[0].mount_owner_id == _CONTAINER_SLOT
