from __future__ import annotations

import pytest

from pyrolyze.runtime.context_state_lcm.lifecycle_adapter import TransactionManager
from pyrolyze.runtime.context_state_lcm.context_base import ContextBaseStateMgr
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.rerunnable_slot_context import RerunnableSlotContextStateMgr


class _DummyPassScope:
    def __init__(self, *, context: object, activate: bool) -> None:
        self.context = context
        self.activate = activate


class _DummyOwner:
    _generation_tracker_key_const = object()
    _pass_scope_handle_cls = _DummyPassScope


class _RenderContextWithStateMgr:
    def __init__(self, state_mgr: object) -> None:
        self._state_mgr = state_mgr


class _RenderContextStateMgrStub:
    def __init__(self, transaction_manager: TransactionManager | None) -> None:
        self._transaction_manager = transaction_manager
        self.slots: dict[object, object] = {}

    def register_slot_state_mgr(self, slot_state_mgr: object) -> None:
        self.slots[getattr(slot_state_mgr, "_slot_id")] = slot_state_mgr


class _ParentStateMgrStub:
    def __init__(self) -> None:
        self.children: dict[object, object] = {}

    def register_child_state_mgr(self, slot_id: object, child_state_mgr: object) -> None:
        self.children[slot_id] = child_state_mgr


class _DerivedContextBaseStateMgr(ContextBaseStateMgr):
    def __init__(self, owner: object, **kwargs: object) -> None:
        super().__init__(owner=owner, **kwargs)


def test_context_base_resolves_render_context_state_mgr_from_explicit_initvar() -> None:
    explicit_state_mgr = object()
    from_render_context = object()

    mgr = ContextBaseStateMgr(
        owner=_DummyOwner(),
        render_context_state_mgr=explicit_state_mgr,
        render_context=_RenderContextWithStateMgr(from_render_context),
    )

    assert mgr._render_context_state_mgr is explicit_state_mgr
    lifecycle_field_names = mgr.__yidl_lifecycle_definition__["class"]["lifecycle_field_names"]
    assert "render_context_state_mgr" not in lifecycle_field_names
    assert "render_context" not in lifecycle_field_names
    assert "_resolved_render_context_state_mgr" not in lifecycle_field_names


def test_context_base_resolves_render_context_state_mgr_from_render_context_initvar() -> None:
    from_render_context = object()

    mgr = ContextBaseStateMgr(
        owner=_DummyOwner(),
        render_context=_RenderContextWithStateMgr(from_render_context),
    )

    assert mgr._render_context_state_mgr is from_render_context


def test_context_base_subclass_can_forward_owner_keyword_to_managed_constructor() -> None:
    explicit_state_mgr = object()

    mgr = _DerivedContextBaseStateMgr(
        owner=_DummyOwner(),
        render_context_state_mgr=explicit_state_mgr,
    )

    assert mgr._render_context_state_mgr is explicit_state_mgr


def test_context_base_reads_transaction_manager_from_render_context_state_mgr() -> None:
    txm = TransactionManager(tx_keys={PASS_TX_KEY})
    render_context_state_mgr = _RenderContextStateMgrStub(transaction_manager=txm)

    mgr = ContextBaseStateMgr(
        owner=_DummyOwner(),
        render_context_state_mgr=render_context_state_mgr,
    )

    assert mgr._transaction_manager is txm


def test_rerunnable_slot_context_inherits_transaction_manager_from_render_context_state_mgr() -> None:
    txm = TransactionManager(tx_keys={PASS_TX_KEY})
    render_context_state_mgr = _RenderContextStateMgrStub(transaction_manager=txm)
    parent_state_mgr = _ParentStateMgrStub()

    mgr = RerunnableSlotContextStateMgr(
        owner=_DummyOwner(),
        parent_state_mgr=parent_state_mgr,
        slot_id="slot-1",
        invoke_dirty=False,
        seen_in_pass=False,
        render_context_state_mgr=render_context_state_mgr,
    )

    assert mgr._transaction_manager is txm


def test_scope_activity_tracks_transaction_state() -> None:
    txm = TransactionManager(tx_keys={PASS_TX_KEY})
    render_context_state_mgr = _RenderContextStateMgrStub(transaction_manager=txm)
    mgr = ContextBaseStateMgr(
        owner=_DummyOwner(),
        render_context_state_mgr=render_context_state_mgr,
    )

    assert mgr.is_scope_active() is False
    with pytest.raises(RuntimeError, match="scope is not active"):
        mgr.require_active_scope()

    txm.begin(PASS_TX_KEY)

    assert mgr.is_scope_active() is True
    mgr.require_active_scope()

    txm.rollback(PASS_TX_KEY)
    assert mgr.is_scope_active() is False


def test_begin_end_and_rollback_pass_manage_pass_transaction() -> None:
    txm = TransactionManager(tx_keys={PASS_TX_KEY})
    render_context_state_mgr = _RenderContextStateMgrStub(transaction_manager=txm)
    mgr = ContextBaseStateMgr(
        owner=_DummyOwner(),
        render_context_state_mgr=render_context_state_mgr,
    )

    mgr.begin_pass()
    assert txm.active_transaction_for(PASS_TX_KEY) is not None
    assert mgr.is_scope_active() is True

    mgr.end_pass()
    assert txm.active_transaction_for(PASS_TX_KEY) is None
    assert mgr.is_scope_active() is False

    mgr.begin_pass()
    assert mgr.is_scope_active() is True
    mgr.rollback_pass()
    assert txm.active_transaction_for(PASS_TX_KEY) is None
    assert mgr.is_scope_active() is False
