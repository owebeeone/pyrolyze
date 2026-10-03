from __future__ import annotations

from typing import Any

import pytest

from pyrolyze.api import UIElement
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.field_only_render import (
    _enable_field_only_render,
)
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted


def _root() -> Any:
    root = runtime.RenderContext()
    _enable_field_only_render(root._state_mgr)
    return root


@pytest.mark.parametrize(
    "slot_type",
    (
        runtime.SlotExprSlotContext,
        runtime.SlotCallSlotContext,
        runtime.EventHandlerSlotContext,
        runtime.DirectiveSlotContext,
        runtime.AppContextOverrideSlotContext,
        runtime.ContainerSlotContext,
        runtime.KeyedLoopSlotContext,
    ),
)
def test_gate_rejects_resource_slots_before_construction(slot_type: type[Any]) -> None:
    root = _root()
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            with pytest.raises(RuntimeError, match="not admitted"):
                slot_type(root, root, runtime.SlotId(runtime.ModuleId("gate"), 1))
    assert root._slots_by_id == {}
    assert root._state_mgr.current.children_state == {}


def test_late_activation_rejected_even_after_empty_legacy_pass() -> None:
    root = runtime.RenderContext()
    with root.pass_scope():
        pass
    with pytest.raises(RuntimeError, match="fresh graph"):
        _enable_field_only_render(root._state_mgr)


def test_entry_reset_error_preserves_error_and_allows_clean_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _root()
    state = root._state_mgr
    error = ValueError("reset failed")

    def fail_reset(self: Any) -> None:
        raise error

    with monkeypatch.context() as patch:
        patch.setattr(type(state), "_begin_field_only_pass", fail_reset)
        with pytest.raises(ValueError) as caught:
            with root.pass_scope():
                pytest.fail("entry should not reach the body")
    assert caught.value is error
    assert not state.is_scope_active()
    assert state._transaction_manager.active_transaction_for(PASS_TX_KEY) is None
    with root.pass_scope():
        pass


def test_adapter_cleanup_failure_quarantines_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _root()
    state = root._state_mgr
    error = ValueError("adapter cleanup failed")

    def fail_cleanup(self: Any, *, published: bool) -> None:
        raise error

    with monkeypatch.context() as patch:
        patch.setattr(type(state), "_clear_field_only_pass", fail_cleanup)
        with pytest.raises(ExceptionGroup) as caught:
            with root.pass_scope():
                raise RuntimeError("body failed")
    assert caught.value.exceptions[0].args == ("body failed",)
    assert caught.value.exceptions[1] is error
    assert not state.is_scope_active()
    with pytest.raises(RuntimeError, match="not ready for reuse"):
        with root.pass_scope():
            pass


def test_lost_transaction_blocks_retry_and_does_not_clear_replacement() -> None:
    root = _root()
    manager = root._state_mgr._transaction_manager
    with pytest.raises(RuntimeError, match="missing or replaced"):
        with root.pass_scope():
            manager.rollback(PASS_TX_KEY)
            replacement = manager.begin(PASS_TX_KEY)
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    assert not root._state_mgr.is_scope_active()
    with pytest.raises(RuntimeError, match="not ready for reuse"):
        with root.pass_scope():
            pass
    manager.rollback(PASS_TX_KEY)


def test_direct_local_success_cannot_publish_before_lexical_scope_exit() -> None:
    root = _root()
    with pytest.raises(ValueError, match="later body failed"):
        with root.pass_scope():
            root._state_mgr.own_ui_state = (
                UIElement(kind="candidate", props={}, children=()),
            )
            root.end_pass()
            assert root._state_mgr.current.ui_state == ()
            raise ValueError("later body failed")
    assert root._state_mgr.current.ui_state == ()


def test_explicit_local_rollback_poison_survives_normal_scope_exit() -> None:
    root = _root()
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            root.rollback_pass()
    assert root._state_mgr.current.ui_state == ()


def test_nested_root_cannot_attach_without_an_owned_component() -> None:
    root = _root()
    with pytest.raises(RuntimeError, match="owned component"):
        runtime.RenderContext(scheduler_root=root)


def test_component_retirement_remains_gated() -> None:
    root = _root()
    slot_id = runtime.SlotId(runtime.ModuleId("retirement"), 1)
    with root.pass_scope():
        component = root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
        component.invoke(lambda context: None, (), {})
    with pytest.raises(RuntimeError, match="retirement is not admitted"):
        with root.pass_scope():
            pass
    assert root._slots_by_id[slot_id] is component
