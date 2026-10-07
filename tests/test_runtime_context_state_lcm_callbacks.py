from __future__ import annotations

from typing import Any

import pytest

from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.callback_render import _enable_callback_render
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted


def _root() -> Any:
    root = runtime.RenderContext()
    _enable_callback_render(root._state_mgr)
    return root


def _slot() -> Any:
    return runtime.SlotId(runtime.ModuleId("tests.callback_faults"), 1)


@pytest.mark.parametrize(
    "slot_type",
    (
        runtime.SlotExprSlotContext,
        runtime.SlotCallSlotContext,
        runtime.AppContextOverrideSlotContext,
    ),
)
def test_callback_gate_still_rejects_other_resource_construction(
    slot_type: type[Any],
) -> None:
    root = _root()
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            with pytest.raises(RuntimeError, match="not admitted"):
                slot_type(root, root, _slot())
    assert root._slots_by_id == {}


def test_callback_write_rejects_replacement_token_before_mutation() -> None:
    root = _root()
    first = lambda: None
    with root.pass_scope():
        root.event_handler(_slot(), callback=first, dirty=False)
    state = root._slots_by_id[_slot()]._state_mgr
    manager = state._transaction_manager
    replacement: Any = None
    with pytest.raises(RuntimeError, match="missing or replaced"):
        with root.pass_scope():
            manager.rollback(PASS_TX_KEY)
            replacement = manager.begin(PASS_TX_KEY)
            state.stage_callback(callback=lambda: None, dirty=True)
    assert state.current._callback is first
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    manager.rollback(PASS_TX_KEY)


def test_retirement_preparation_error_discards_and_allows_clean_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _root()
    calls: list[str] = []
    callback = lambda: calls.append("accepted")
    with root.pass_scope():
        dispatch = root.event_handler(_slot(), callback=callback, dirty=False)
    state = root._slots_by_id[_slot()]._state_mgr
    error = ValueError("retirement staging failed")

    def fail(self: Any) -> None:
        raise error

    with monkeypatch.context() as patch:
        patch.setattr(type(state), "_stage_retirement", fail)
        with pytest.raises(ValueError) as caught:
            with root.pass_scope():
                pass
    assert caught.value is error
    assert root.debug_is_active(_slot())
    dispatch()
    assert calls == ["accepted"]
    assert root._state_mgr._field_only_completion.last.reuse_ready
    with root.pass_scope():
        assert root.event_handler(_slot(), callback=callback, dirty=False) is dispatch


def test_retirement_staging_reentry_cannot_publish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _root()
    callback = lambda: None
    with root.pass_scope():
        root.event_handler(_slot(), callback=callback, dirty=False)
    state = root._slots_by_id[_slot()]._state_mgr

    def reenter(self: Any) -> None:
        with root.pass_scope():
            pytest.fail("retirement staging must fence reentry")

    with monkeypatch.context() as patch:
        patch.setattr(type(state), "_stage_retirement", reenter)
        with pytest.raises(RuntimeError, match="completion is in progress"):
            with root.pass_scope():
                pass
    assert state.current._callback is callback
    assert root.debug_is_active(_slot())
