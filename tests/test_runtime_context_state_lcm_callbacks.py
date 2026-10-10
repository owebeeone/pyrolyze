from __future__ import annotations

from typing import Any

import pytest

from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted


def _root() -> Any:
    root = runtime.RenderContext()
    return root


def _slot() -> Any:
    return runtime.SlotId(runtime.ModuleId("tests.callback_faults"), 1)




def test_callback_write_rejects_replacement_token_before_mutation() -> None:
    root = _root()
    first = lambda: None
    with root.pass_scope():
        root.event_handler(_slot(), callback=first, dirty=False)
    state = root._slots_by_id[_slot()]
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


@pytest.mark.parametrize("attack", ("equality", "property"))
def test_callback_user_code_cannot_write_into_replacement_token(attack: str) -> None:
    root = _root()
    manager = root._transaction_manager
    replacement: Any = None
    armed = False

    def replace_token() -> None:
        nonlocal replacement
        manager.rollback(PASS_TX_KEY)
        replacement = manager.begin(PASS_TX_KEY)

    class Callback:
        def __eq__(self, other: object) -> bool:
            if armed and attack == "equality":
                replace_token()
            return False

        @property
        def __self__(self) -> None:
            if armed and attack == "property":
                replace_token()
            return None

        def __call__(self) -> None:
            pass

    first = Callback()
    with root.pass_scope():
        root.event_handler(_slot(), callback=first, dirty=False)
    state = root._slots_by_id[_slot()]
    armed = True
    with pytest.raises(RuntimeError, match="missing or replaced"):
        with root.pass_scope():
            selected = Callback() if attack == "property" else lambda: None
            state.stage_callback(callback=selected, dirty=attack == "property")
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    assert state._callback is first
    assert state._callback_key is first
    completion = root._field_only_completion
    assert completion.last.published is None
    assert not completion.last.reuse_ready
    manager.rollback(PASS_TX_KEY)


def test_retirement_preparation_error_discards_and_allows_clean_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _root()
    calls: list[str] = []
    callback = lambda: calls.append("accepted")
    with root.pass_scope():
        dispatch = root.event_handler(_slot(), callback=callback, dirty=False)
    state = root._slots_by_id[_slot()]
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
    assert root._field_only_completion.last.reuse_ready
    with root.pass_scope():
        assert root.event_handler(_slot(), callback=callback, dirty=False) is dispatch


def test_retirement_staging_reentry_cannot_publish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _root()
    callback = lambda: None
    with root.pass_scope():
        root.event_handler(_slot(), callback=callback, dirty=False)
    state = root._slots_by_id[_slot()]

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
