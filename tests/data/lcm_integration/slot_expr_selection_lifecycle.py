"""Render-owned expression collections follow one outer completion decision."""

from __future__ import annotations

import json
from typing import Any

from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted
from pyrolyze.runtime.context_state_lcm.slot_expr_render import _enable_slot_expr_render
from pyrolyze.runtime.dirt import DM
from pyrolyze.runtime.slot_expr import (
    LiteralFunctionProvider,
    slot_params,
    slot_params_dirt,
)


def characterize() -> dict[str, Any]:
    root = runtime.RenderContext()
    _enable_slot_expr_render(root._state_mgr)
    module = runtime.ModuleId("tests.expression_selection")
    expr_id = runtime.SlotId(module, 1)
    call_id = runtime.SlotId(module, 2)
    calls: list[int] = []
    manager: Any = None

    def source(value: int) -> int:
        calls.append(value)
        return value + 1

    def evaluate(value: int) -> int:
        nonlocal manager
        expr = root.slot_expr(expr_id, lambda v: v.eval(), lambda v: v.dirty())
        expr.slot_call(
            "v",
            LiteralFunctionProvider(source),
            lambda: slot_params(value),
            lambda: slot_params_dirt(False),
            slot_id=call_id,
        ).apply_dirt_sink(DM())
        manager = expr.call_site_context_manager
        return expr.evaluate("result")

    def current() -> int | None:
        context = manager.get_current(call_id)
        return None if context is None else context.binding.exposed_value()

    result: dict[str, Any] = {}
    with root.pass_scope():
        result["first"] = evaluate(1)
        result["initial_provisional"] = current()
        result["same_manager"] = (
            manager._transaction_manager is root._state_mgr._transaction_manager
        )
    result["initial"] = current()
    with root.pass_scope():
        result["unchanged"] = evaluate(1)
        result["pending"] = evaluate(2)
        result["accepted_during_pass"] = current()
        result["candidate"] = manager.get_visible(call_id).binding.exposed_value()
        result["candidate_elision"] = evaluate(2)
    result["published"] = current()
    try:
        with root.pass_scope():
            evaluate(3)
            raise ValueError("parent failed")
    except ValueError:
        pass
    result["discarded"] = current()
    try:
        with root.pass_scope():
            try:
                expr = root.slot_expr(
                    expr_id,
                    lambda: (_ for _ in ()).throw(ValueError("expression failed")),
                    lambda: False,
                )
                expr.apply_dirt_sink(DM()).evaluate()
            except ValueError:
                pass
    except RenderAttemptAborted as error:
        result["caught_failure"] = str(error.__cause__)
    result["after_caught_failure"] = current()
    with root.pass_scope():
        result["retry"] = evaluate(3)
    result["after_retry"] = current()
    with root.pass_scope():
        pass
    result["removed"] = current()
    result["calls"] = calls
    result["ready"] = root._state_mgr._field_only_completion.last.reuse_ready
    branch_root = runtime.RenderContext()
    _enable_slot_expr_render(branch_root._state_mgr)
    branch_manager: Any = None

    def branch_source(value: int) -> int:
        return value

    def evaluate_branch(both: bool) -> Any:
        nonlocal branch_manager
        expr = branch_root.slot_expr(
            expr_id,
            lambda a, b: (a.eval(), b.eval()) if both else a.eval(),
            lambda a, b: (a.dirty(), b.dirty()) if both else a.dirty(),
        )
        expr.slot_call(
            "a",
            LiteralFunctionProvider(branch_source),
            lambda: slot_params(2),
            lambda: slot_params_dirt(False),
            slot_id=runtime.SlotId(module, 2),
        ).slot_call(
            "b",
            LiteralFunctionProvider(branch_source),
            lambda: slot_params(3),
            lambda: slot_params_dirt(False),
            slot_id=runtime.SlotId(module, 3),
        )
        branch_manager = expr.call_site_context_manager
        return expr.apply_dirt_sink(DM()).evaluate("result")

    with branch_root.pass_scope():
        result["branches_initial"] = evaluate_branch(True)
    retained_branch = branch_manager.get_current(runtime.SlotId(module, 3))
    try:
        with branch_root.pass_scope():
            evaluate_branch(False)
            result["pruning_provisional"] = len(branch_manager.iter_current())
            raise ValueError("branch render failed")
    except ValueError:
        pass
    result["pruning_discarded"] = [
        len(branch_manager.iter_current()),
        retained_branch.is_closed,
    ]
    with branch_root.pass_scope():
        evaluate_branch(False)
    result["pruning_published"] = [
        len(branch_manager.iter_current()),
        retained_branch.is_closed,
    ]
    return result


if __name__ == "__main__":
    print(json.dumps(characterize(), sort_keys=True, indent=2))
