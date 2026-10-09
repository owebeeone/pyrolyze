from __future__ import annotations

from typing import Any

import pytest

from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.pass_state_render import (
    _enable_pass_state_render,
)
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY


def _root() -> Any:
    root = runtime.RenderContext()
    _enable_pass_state_render(root._state_mgr)
    return root


def _visit(root: Any) -> Any:
    return root._ensure_slot(
        runtime.SlotId(runtime.ModuleId("pass-state-faults"), 1),
        runtime.SlotCallSlotContext,
    )


def test_notification_after_visit_is_not_acknowledged_by_local_success() -> None:
    root = _root()
    with root.pass_scope():
        slot = _visit(root)
        slot.evaluate(lambda: 1, (), {})
    with root._state_mgr._field_only_completion.attempt_scope():
        with root.pass_scope():
            slot = _visit(root)
            root._state_mgr.queue_invalidation_from(slot)
        assert slot.invoke_dirty


def test_failed_pass_retains_notification_without_dirty_snapshot() -> None:
    root = _root()
    source = lambda: 1
    with root.pass_scope():
        slot = _visit(root)
        slot.evaluate(source, (), {})
    with pytest.raises(ValueError, match="discard"):
        with root.pass_scope():
            slot = _visit(root)
            assert root._state_mgr._pass_child_dirty == {}
            root._state_mgr.queue_invalidation_from(slot)
            raise ValueError("discard")
    assert slot.invoke_dirty


def test_replaced_token_cannot_acknowledge_new_transaction() -> None:
    root = _root()
    with root.pass_scope():
        slot = _visit(root)
        slot.evaluate(lambda: 1, (), {})
    completion = root._state_mgr._field_only_completion
    manager = root._state_mgr._transaction_manager
    with pytest.raises(RuntimeError):
        with completion.attempt_scope():
            slot._state_mgr._invoke_dirty = True
            manager.rollback(PASS_TX_KEY)
            newer = manager.begin(PASS_TX_KEY)
            slot._state_mgr._invoke_dirty = False
    assert manager.active_transaction_for(PASS_TX_KEY) is newer
    assert slot.invoke_dirty
    manager.rollback(PASS_TX_KEY)
