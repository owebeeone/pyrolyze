from __future__ import annotations

from typing import Any

import pytest

from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.call_site_context import CallSiteContextManager
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted
from pyrolyze.runtime.dirt import DM
from pyrolyze.runtime.slot_call_semantics import UseEffectRequest
from pyrolyze.runtime.slot_expr import (
    LiteralFunctionProvider,
    SlotExpr,
    slot_params,
    slot_params_dirt,
)


def _root() -> Any:
    root = runtime.RenderContext()
    return root


def _expr(root: Any, source: Any, *, args: Any = lambda: slot_params()) -> SlotExpr:
    module = runtime.ModuleId("tests.expression_render_faults")
    expression = root.slot_expr(
        runtime.SlotId(module, 1), lambda v: v.eval(), lambda v: v.dirty()
    )
    return expression.slot_call(
        "v",
        LiteralFunctionProvider(source),
        args,
        lambda: slot_params_dirt(),
        slot_id=runtime.SlotId(module, 2),
    ).apply_dirt_sink(DM())




def test_caught_argument_preparation_failure_poison_outer_without_early_publication() -> (
    None
):
    root = _root()
    with root.pass_scope():
        expression = _expr(root, lambda value: value, args=lambda: slot_params(1))
        expression.evaluate()
    manager = expression.call_site_context_manager
    accepted = manager.iter_current()
    error = ValueError("argument preparation")

    def fail_args() -> Any:
        raise error

    with pytest.raises(RenderAttemptAborted) as caught:
        with root.pass_scope():
            _expr(root, lambda value: value, args=lambda: slot_params(2)).evaluate()
            try:
                _expr(root, lambda value: value, args=fail_args).evaluate()
            except ValueError:
                pass
    assert caught.value.__cause__ is error
    assert manager.iter_current() == accepted
    assert accepted[0].binding.exposed_value() == 1


def test_source_replacing_token_cannot_write_candidates_to_replacement() -> None:
    root = _root()
    manager = root._transaction_manager
    replacement: Any = None

    def replace_token() -> int:
        nonlocal replacement
        manager.rollback(PASS_TX_KEY)
        replacement = manager.begin(PASS_TX_KEY)
        return 99

    with pytest.raises((RuntimeError, BaseExceptionGroup)):
        with root.pass_scope():
            expression = _expr(root, replace_token)
            expression.evaluate()
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    assert expression.call_site_context_manager.iter_current() == ()
    assert expression.call_site_context_manager._staged == {}
    assert not root._field_only_completion.last.reuse_ready
    manager.rollback(PASS_TX_KEY)


def test_borrowed_collection_manager_cannot_complete_the_render() -> None:
    root = _root()
    with root.pass_scope():
        expression = _expr(root, lambda: 1)
        manager = expression.call_site_context_manager
        token = root._transaction_manager.active_transaction_for(PASS_TX_KEY)
        with pytest.raises(RuntimeError, match="outer render owns"):
            manager.commit_pass()
        with pytest.raises(RuntimeError, match="outer render owns"):
            manager.rollback_pass()
        assert (
            root._transaction_manager.active_transaction_for(PASS_TX_KEY)
            is token
        )
        expression.evaluate()


def test_independent_collection_cannot_be_substituted_into_shared_expression() -> None:
    root = _root()
    foreign = CallSiteContextManager()
    with pytest.raises(RuntimeError, match="different collection"):
        with root.pass_scope():
            expression = _expr(root, lambda: 1)
            expression.apply_call_site_context_manager(foreign).evaluate()
    assert foreign._active_transaction is None
    assert foreign.iter_current() == ()


def test_recursive_evaluation_of_the_same_expression_collection_is_rejected() -> None:
    root = _root()

    def recurse() -> int:
        return _expr(root, lambda: 2).evaluate()

    with pytest.raises(RuntimeError, match="recursive expression evaluation"):
        with root.pass_scope():
            _expr(root, recurse).evaluate()
    assert root.current.children_state == {}
    with root.pass_scope():
        assert _expr(root, lambda: 3).evaluate() == 3
