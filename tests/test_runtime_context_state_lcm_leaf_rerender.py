from __future__ import annotations

from pyrolyze.api import UIElement
from pyrolyze.runtime.context_bare_refactor_lcm import LeafSlotContext, ModuleId, RenderContext, SlotId
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_GROUP


def _slot(index: int) -> SlotId:
    return SlotId(ModuleId("tests.context_state_lcm_leaf_rerender"), index)


def _emit_text(ctx: LeafSlotContext, value: str) -> None:
    ctx.call_native(
        UIElement,
        kind="text",
        props={"value": value},
        children=(),
    )


def _run_leaf_pass(root: RenderContext, slot_order: tuple[int, ...]) -> None:
    txm = root._state_mgr._transaction_manager
    with txm.begin(PASS_TX_GROUP):
        root._state_mgr.children_state = {}
        root._state_mgr.ui_state = ()
        for slot_index in slot_order:
            slot = root._ensure_slot(_slot(slot_index), LeafSlotContext)
            slot._state_mgr.own_ui_entries_state = ()
            slot._state_mgr.own_ui_state = ()
            slot._state_mgr.ui_state = ()
            slot.invoke_native(
                lambda ctx, value: _emit_text(ctx, value),
                (f"slot-{slot_index}",),
                {},
                context_param="ctx",
            )
        root._refresh_committed_ui_from_children()


def test_leaf_slot_rerender_sequence_updates_child_and_ui_order() -> None:
    root = RenderContext()

    _run_leaf_pass(root, (1,))
    assert root.debug_children_of() == (_slot(1),)
    assert tuple(item.props["value"] for item in root.debug_ui()) == ("slot-1",)

    _run_leaf_pass(root, (1, 2))
    assert root.debug_children_of() == (_slot(1), _slot(2))
    assert tuple(item.props["value"] for item in root.debug_ui()) == ("slot-1", "slot-2")

    _run_leaf_pass(root, (2, 1))
    assert root.debug_children_of() == (_slot(2), _slot(1))
    assert tuple(item.props["value"] for item in root.debug_ui()) == ("slot-2", "slot-1")

    _run_leaf_pass(root, (3,))
    assert root.debug_children_of() == (_slot(3),)
    assert tuple(item.props["value"] for item in root.debug_ui()) == ("slot-3",)

    _run_leaf_pass(root, (1, 2, 3))
    assert root.debug_children_of() == (_slot(1), _slot(2), _slot(3))
    assert tuple(item.props["value"] for item in root.debug_ui()) == ("slot-1", "slot-2", "slot-3")

    _run_leaf_pass(root, (3, 2, 1))
    assert root.debug_children_of() == (_slot(3), _slot(2), _slot(1))
    assert tuple(item.props["value"] for item in root.debug_ui()) == ("slot-3", "slot-2", "slot-1")

    _run_leaf_pass(root, (3, 2, 1))
    assert root.debug_children_of() == (_slot(3), _slot(2), _slot(1))
    assert tuple(item.props["value"] for item in root.debug_ui()) == ("slot-3", "slot-2", "slot-1")
