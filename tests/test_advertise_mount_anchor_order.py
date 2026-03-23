from __future__ import annotations

from pyrolyze.api import MountSelector, PyrolyzeMountAdvertisement, UIElement, advertise_mount
from pyrolyze.runtime import ContextBase, ModuleRegistry, RenderContext, SlotId


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.advertise_mount_anchor_order")

_CONTAINER_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_FIRST_TEXT_SLOT = SlotId(_MODULE_ID, 2, line_no=11)
_FIRST_ADVERT_SLOT = SlotId(_MODULE_ID, 3, line_no=12)
_SECOND_TEXT_SLOT = SlotId(_MODULE_ID, 4, line_no=13)
_SECOND_ADVERT_SLOT = SlotId(_MODULE_ID, 5, line_no=14)


def _pyr_section(ctx: ContextBase, title: str) -> None:
    ctx.call_native(
        UIElement,
        kind="section",
        props={"title": title},
    )

def _pyr_text(ctx: ContextBase, value: str) -> None:
    ctx.call_native(
        UIElement,
        kind="text",
        props={"value": value},
    )


def test_advertise_mount_is_retained_at_exact_anchor_sites_in_container_order() -> None:
    ctx = RenderContext()
    first = MountSelector.named("first")
    second = MountSelector.named("second")

    with ctx.pass_scope():
        with ctx.container_call(_CONTAINER_SLOT, _pyr_section, "Greeting") as section_ctx:
            section_ctx.leaf_call(_FIRST_TEXT_SLOT, _pyr_text, "hello")
            _ = section_ctx.call_plain(
                _FIRST_ADVERT_SLOT,
                advertise_mount,
                name="first_name",
                target=first,
                default=True,
            )
            section_ctx.leaf_call(_SECOND_TEXT_SLOT, _pyr_text, "hope you have a")
            _ = section_ctx.call_plain(
                _SECOND_ADVERT_SLOT,
                advertise_mount,
                name="type_of_day",
                target=second,
            )

    advertisements = ctx.debug_mount_advertisements()
    assert [advertisement.key for advertisement in advertisements] == [
        "first_name",
        "type_of_day",
    ]
    assert ctx.debug_ui() == (
        UIElement(
            kind="section",
            props={"title": "Greeting"},
            children=(
                UIElement(kind="text", props={"value": "hello"}),
                PyrolyzeMountAdvertisement(
                    key="first_name",
                    selectors=(first,),
                    default=True,
                ),
                UIElement(kind="text", props={"value": "hope you have a"}),
                PyrolyzeMountAdvertisement(
                    key="type_of_day",
                    selectors=(second,),
                    default=False,
                ),
            ),
        ),
    )


def test_advertise_mount_key_mapping_updates_legal_public_shape_on_rerender() -> None:
    ctx = RenderContext()
    target = MountSelector.named("widget")

    with ctx.pass_scope():
        with ctx.container_call(_CONTAINER_SLOT, _pyr_section, "Wrapper") as section_ctx:
            _ = section_ctx.call_plain(
                _FIRST_ADVERT_SLOT,
                advertise_mount,
                name="first_name",
                target=target,
            )

    first_pass = ctx.debug_mount_advertisements()
    assert [advertisement.key for advertisement in first_pass] == ["first_name"]

    with ctx.pass_scope():
        with ctx.container_call(_CONTAINER_SLOT, _pyr_section, "Wrapper") as section_ctx:
            _ = section_ctx.call_plain(
                _FIRST_ADVERT_SLOT,
                advertise_mount,
                name="display_name",
                target=target,
            )

    second_pass = ctx.debug_mount_advertisements()
    assert [advertisement.key for advertisement in second_pass] == ["display_name"]
    assert second_pass[0].selectors == (target,)
    assert second_pass[0].source_slot_id == _FIRST_ADVERT_SLOT
