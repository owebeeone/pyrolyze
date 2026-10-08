from __future__ import annotations

from typing import Any

import pytest

from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.field_only_render import (
    _enable_field_only_render,
)
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted


def _root_and_leaf() -> tuple[Any, Any]:
    root = runtime.RenderContext()
    _enable_field_only_render(root._state_mgr)
    slot_id = runtime.SlotId(runtime.ModuleId("tests.invocation_faults"), 1)
    with root.pass_scope():
        leaf = root._ensure_slot(slot_id, runtime.LeafSlotContext)
        leaf.invoke(lambda value: value, (1,), {})
    return root, leaf


def _invoke(leaf: Any, native: bool, kwargs: dict[str, Any]) -> None:
    if native:
        leaf.invoke_native(
            lambda context, value: None, (2,), kwargs, context_param="context"
        )
    else:
        leaf.invoke(lambda value: None, (2,), kwargs)


@pytest.mark.parametrize("native", (False, True))
def test_legacy_keyword_failure_preserves_sequential_attempt_tracking(
    native: bool,
) -> None:
    root = runtime.RenderContext()
    slot_id = runtime.SlotId(runtime.ModuleId("tests.legacy_invocation_faults"), 1)
    with root.pass_scope():
        leaf = root._ensure_slot(slot_id, runtime.LeafSlotContext)
        leaf.invoke(lambda value, **kwargs: None, (1,), {"flag": True})
    error = ValueError("legacy keyword normalization failed")

    class FailingKeywords(dict[str, Any]):
        def items(self) -> Any:
            raise error

    with pytest.raises(ValueError) as caught:
        _invoke(leaf, native, FailingKeywords())
    assert caught.value is error
    assert leaf.last_args == (2,)
    assert leaf.last_kwargs == (("flag", True),)


@pytest.mark.parametrize("native", (False, True))
def test_keyword_preparation_failure_poisoned_even_if_parent_catches(
    native: bool,
) -> None:
    root, leaf = _root_and_leaf()
    error = ValueError("keyword normalization failed")

    class FailingKeywords(dict[str, Any]):
        def items(self) -> Any:
            raise error

    with pytest.raises(RenderAttemptAborted) as caught:
        with root.pass_scope():
            root._ensure_slot(leaf.slot_id, runtime.LeafSlotContext)
            with pytest.raises(ValueError) as inner:
                _invoke(leaf, native, FailingKeywords())
            assert inner.value is error
    assert caught.value.__cause__ is error
    assert leaf.last_args == (1,)
    assert root._state_mgr._field_only_completion.last.reuse_ready


@pytest.mark.parametrize("native", (False, True))
def test_keyword_preparation_cannot_stage_into_replacement_token(native: bool) -> None:
    root, leaf = _root_and_leaf()
    manager = root._state_mgr._transaction_manager
    replacement: Any = None

    class ReplacingKeywords(dict[str, Any]):
        def items(self) -> Any:
            nonlocal replacement
            manager.rollback(PASS_TX_KEY)
            replacement = manager.begin(PASS_TX_KEY)
            return super().items()

    with pytest.raises(RuntimeError, match="missing or replaced"):
        with root.pass_scope():
            root._ensure_slot(leaf.slot_id, runtime.LeafSlotContext)
            _invoke(leaf, native, ReplacingKeywords())
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    assert leaf._state_mgr._last_args == (1,)
    assert leaf.last_args == (1,)
    assert root._state_mgr._field_only_completion.last.published is None
    assert not root._state_mgr._field_only_completion.last.reuse_ready
    manager.rollback(PASS_TX_KEY)
