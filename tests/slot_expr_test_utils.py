from __future__ import annotations

from typing import Any

from pyrolyze.runtime import LiteralFunctionProvider, dm_from_dirty_state, slot_params, slot_params_dirt
from pyrolyze.runtime.context import ContextBase, DirtyStateContext, SlotExprSlotContext, SlotId


def eval_single_slot_expr(
    ctx: ContextBase,
    dirty_state: DirtyStateContext,
    expr_slot: SlotId,
    func: Any,
    *args: Any,
    args_dirty: tuple[Any, ...] = (),
    kwargs_dirty: dict[str, Any] | None = None,
    result_name: str = "value",
    call_id: str = "v1",
    call_slot: SlotId | None = None,
    **kwargs: Any,
) -> tuple[Any, Any]:
    dm = dm_from_dirty_state(dirty_state)
    value = (
        ctx.slot_expr(
            expr_slot,
            lambda v1: v1.eval(),
            lambda v1: v1.dirty(),
        )
        .slot_call(
            call_id,
            LiteralFunctionProvider(func),
            lambda: slot_params(*args, **kwargs),
            lambda: slot_params_dirt(*args_dirty, **(kwargs_dirty or {})),
            slot_id=call_slot or expr_slot,
        )
        .apply_dirt_sink(dm)
        .evaluate(result_name)
    )
    return getattr(dm.bind, result_name), value


def slot_expr_binding_for(
    ctx: ContextBase,
    expr_slot: SlotId,
    *,
    call_slot: SlotId | None = None,
) -> Any:
    slot = ctx._slots_by_id[expr_slot]
    assert isinstance(slot, SlotExprSlotContext)
    call_site_context = (
        slot.call_site_context_manager.get_current(call_slot or expr_slot)
        or slot.call_site_context_manager._staged.get(call_slot or expr_slot)
    )
    assert call_site_context is not None
    binding = call_site_context.binding
    assert binding is not None
    return getattr(binding, "binding", binding)
