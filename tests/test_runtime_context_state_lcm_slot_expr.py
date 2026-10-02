from __future__ import annotations

from pyrolyze.runtime.context_state_lcm.slot_expr_slot_context import SlotExprSlotContextStateMgr
from pyrolyze.runtime.slot_call_semantics import PyrolyzeMountAdvertisementBinding
from pyrolyze.runtime.slot_kinds import ContextKind
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.lifecycle_adapter import TransactionManager


class _DummyPassScope:
    def __init__(self, *, context: object, activate: bool) -> None:
        self.context = context
        self.activate = activate


class _DummyOwner:
    _generation_tracker_key_const = object()
    _pass_scope_handle_cls = _DummyPassScope
    _context_kind = ContextKind.SLOT


class _RenderContextStateMgrStub:
    def __init__(self) -> None:
        self._transaction_manager = TransactionManager(tx_keys={PASS_TX_KEY})
        self.slots: dict[object, object] = {}

    def register_slot_state_mgr(self, slot_state_mgr: object) -> None:
        self.slots[getattr(slot_state_mgr, "_slot_id")] = slot_state_mgr


class _ParentStateMgrStub:
    def __init__(self) -> None:
        self.children: dict[object, object] = {}

    def register_child_state_mgr(self, slot_id: object, child_state_mgr: object) -> None:
        self.children[slot_id] = child_state_mgr


def _mgr() -> SlotExprSlotContextStateMgr:
    return SlotExprSlotContextStateMgr.create(
        owner=_DummyOwner(),
        render_context_state_mgr=_RenderContextStateMgrStub(),
        parent_state_mgr=_ParentStateMgrStub(),
        slot_id="slot-1",
        invoke_dirty=False,
        seen_in_pass=False,
    )


def test_slot_expr_runtime_locals_reuse_per_slot() -> None:
    mgr = _mgr()

    first = mgr.runtime_locals("slot-a")
    second = mgr.runtime_locals("slot-a")

    assert first is second
    assert mgr._runtime_locals_by_slot_id["slot-a"] is first


def test_slot_expr_stage_slot_expr_pass_merges_ids_and_callbacks() -> None:
    mgr = _mgr()

    def callback() -> None:
        return None

    mgr._transaction_manager.begin(PASS_TX_KEY)

    mgr.stage_slot_expr_pass(
        visited_call_site_ids=("one", "two"),
        post_commit_callbacks=(callback,),
    )
    mgr.stage_slot_expr_pass(
        visited_call_site_ids=("two", "three"),
        post_commit_callbacks=(),
    )

    assert mgr._staged_call_site_ids == ("one", "two", "three")
    assert mgr._staged_post_commit_callbacks == (callback,)
    mgr._transaction_manager.rollback(PASS_TX_KEY)


def test_slot_expr_commit_and_rollback_binding_clear_staged_state() -> None:
    mgr = _mgr()

    def callback() -> None:
        return None

    mgr._transaction_manager.begin(PASS_TX_KEY)
    mgr._staged_call_site_ids = ("one",)
    mgr._staged_post_commit_callbacks = (callback,)

    mgr.commit_binding()
    assert mgr._staged_call_site_ids == ()
    assert mgr._staged_post_commit_callbacks == ()

    mgr._transaction_manager.rollback(PASS_TX_KEY)
    mgr._transaction_manager.begin(PASS_TX_KEY)
    mgr._staged_call_site_ids = ("one",)
    mgr._staged_post_commit_callbacks = (callback,)
    mgr.rollback_binding()
    assert mgr._staged_call_site_ids == ()
    assert mgr._staged_post_commit_callbacks == ()
    mgr._transaction_manager.rollback(PASS_TX_KEY)


def test_slot_expr_mount_binding_type_remains_pyrolyze_advert_binding() -> None:
    mgr = _mgr()

    assert mgr._mount_advertisement_binding_type is PyrolyzeMountAdvertisementBinding
