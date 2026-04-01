from __future__ import annotations

from dataclasses import dataclass

from pyrolyze.runtime.context import CompValue, ExternalStoreRef, UseEffectRequest
from pyrolyze.runtime.dirt import DM
from pyrolyze.runtime.slot_expr import Args, SlotExpr, slot_params, slot_params_dirt


@dataclass
class FakeSlotContext:
    initial_render: bool = True

    def literal(self, value):
        return CompValue(value=value, dirty=self.initial_render)


def test_args_capture_and_call() -> None:
    args = Args.capture(1, 2, x=3)

    assert args.args == (1, 2)
    assert args.kwds == {"x": 3}
    assert args.call(lambda a, b, *, x: a + b + x) == 6


def test_slot_expr_single_call_binds_scalar_result_and_dirt() -> None:
    dm = DM()
    slot_ctx = FakeSlotContext(initial_render=True)
    expr = SlotExpr.single_call(
        lambda value: value,
        lambda: slot_params("clock"),
        lambda: slot_params_dirt(slot_ctx.literal("clock").dirty),
    ).apply_slot_context(slot_ctx).apply_dirt_sink(dm)

    value = expr.evaluate("value")

    assert value == "clock"
    assert dm.bind.value is True


def test_slot_expr_single_call_fast_path_matches_general_path() -> None:
    dm_fast = DM()
    slot_ctx_fast = FakeSlotContext(initial_render=True)
    fast = SlotExpr.single_call(
        lambda value: value,
        lambda: slot_params("clock"),
        lambda: slot_params_dirt(slot_ctx_fast.literal("clock").dirty),
    ).apply_slot_context(slot_ctx_fast).apply_dirt_sink(dm_fast)

    dm_general = DM()
    slot_ctx_general = FakeSlotContext(initial_render=True)
    general = (
        SlotExpr(
            value_lambda=lambda v1: v1.eval(),
            dirty_lambda=lambda v1: v1.dirty(),
        )
        .slot_call(
            "v1",
            lambda value: value,
            lambda: slot_params("clock"),
            lambda: slot_params_dirt(slot_ctx_general.literal("clock").dirty),
        )
        .apply_slot_context(slot_ctx_general)
        .apply_dirt_sink(dm_general)
    )

    assert fast.evaluate("value") == general.evaluate("value")
    assert dm_fast.bind.value == dm_general.bind.value


def test_slot_expr_or_short_circuits_right_eval_and_right_dirt_is_clean() -> None:
    dm = DM()
    slot_ctx = FakeSlotContext(initial_render=False)
    touched = {"right": 0}

    def left() -> str:
        return "clock"

    def right() -> str:
        touched["right"] += 1
        return "fallback"

    expr = (
        SlotExpr(
            value_lambda=lambda a, b: a.eval() or b.eval(),
            dirty_lambda=lambda a, b: a.dirty() or b.dirty(),
        )
        .slot_call("a", left, lambda: slot_params(), lambda: slot_params_dirt(False))
        .slot_call("b", right, lambda: slot_params(), lambda: slot_params_dirt(True))
        .apply_slot_context(slot_ctx)
        .apply_dirt_sink(dm)
    )

    first_value = expr.evaluate("value")

    assert first_value == "clock"
    assert touched["right"] == 0

    value = expr.evaluate("value")

    assert value == "clock"
    assert touched["right"] == 0
    assert dm.bind.value is False


def test_slot_expr_and_short_circuits_right_eval_and_right_dirt_is_clean() -> None:
    dm = DM()
    slot_ctx = FakeSlotContext(initial_render=False)
    touched = {"right": 0}

    def left() -> str:
        return ""

    def right() -> str:
        touched["right"] += 1
        return "fallback"

    expr = (
        SlotExpr(
            value_lambda=lambda a, b: a.eval() and b.eval(),
            dirty_lambda=lambda a, b: a.dirty() or b.dirty(),
        )
        .slot_call("a", left, lambda: slot_params(), lambda: slot_params_dirt(False))
        .slot_call("b", right, lambda: slot_params(), lambda: slot_params_dirt(True))
        .apply_slot_context(slot_ctx)
        .apply_dirt_sink(dm)
    )

    first_value = expr.evaluate("value")

    assert first_value == ""
    assert touched["right"] == 0

    value = expr.evaluate("value")

    assert value == ""
    assert touched["right"] == 0
    assert dm.bind.value is False


def test_slot_expr_multiple_calls_combines_dirt() -> None:
    dm = DM()
    slot_ctx = FakeSlotContext(initial_render=False)
    expr = (
        SlotExpr(
            value_lambda=lambda a, b: a.eval() + b.eval(),
            dirty_lambda=lambda a, b: a.dirty() or b.dirty(),
        )
        .slot_call("a", lambda value: value, lambda: slot_params(2), lambda: slot_params_dirt(False))
        .slot_call("b", lambda value: value, lambda: slot_params(3), lambda: slot_params_dirt(True))
        .apply_slot_context(slot_ctx)
        .apply_dirt_sink(dm)
    )

    value = expr.evaluate("total")

    assert value == 5
    assert dm.bind.total is True


def test_slot_expr_multi_result_unpacks_value_and_dirt() -> None:
    dm = DM()
    slot_ctx = FakeSlotContext(initial_render=True)
    expr = SlotExpr.single_call(
        lambda initial: (initial, lambda next_value: next_value),
        lambda: slot_params(3),
        lambda: slot_params_dirt(slot_ctx.literal(3).dirty),
    ).apply_slot_context(slot_ctx).apply_dirt_sink(dm)

    val, func = expr.evaluate("val", "func")

    assert val == 3
    assert callable(func)
    assert dm.bind.val is True
    assert dm.bind.func is True


def test_slot_expr_multi_result_keeps_tuple_dirty_under_one_name() -> None:
    dm = DM()
    slot_ctx = FakeSlotContext(initial_render=True)
    expr = SlotExpr.single_call(
        lambda initial: (initial, lambda next_value: next_value),
        lambda: slot_params(3),
        lambda: slot_params_dirt(slot_ctx.literal(3).dirty),
    ).apply_slot_context(slot_ctx).apply_dirt_sink(dm)

    result = expr.evaluate("result")

    assert result[0] == 3
    assert callable(result[1])
    assert dm.bind.result == (True, True)


def test_slot_expr_evaluate_raises_on_value_shape_mismatch() -> None:
    dm = DM()
    slot_ctx = FakeSlotContext(initial_render=True)
    expr = SlotExpr.single_call(
        lambda value: value,
        lambda: slot_params(3),
        lambda: slot_params_dirt(slot_ctx.literal(3).dirty),
    ).apply_slot_context(slot_ctx).apply_dirt_sink(dm)

    try:
        expr.evaluate("a", "b")
    except ValueError as exc:
        assert "value shape" in str(exc)
    else:
        raise AssertionError("expected shape mismatch")


def test_slot_expr_nested_args_can_depend_on_prior_evaluator() -> None:
    dm = DM()
    slot_ctx = FakeSlotContext(initial_render=True)
    expr = (
        SlotExpr(
            value_lambda=lambda v1, v2: v2.eval(),
            dirty_lambda=lambda v1, v2: v1.dirty() or v2.dirty(),
        )
        .slot_call(
            "v1",
            lambda value: value,
            lambda: slot_params("clock"),
            lambda: slot_params_dirt(slot_ctx.literal("clock").dirty),
        )
        .slot_call(
            "v2",
            lambda value: f"{value}-suffix",
            lambda v1: slot_params(v1.eval()),
            lambda v1: slot_params_dirt(v1.dirty()),
        )
        .apply_slot_context(slot_ctx)
        .apply_dirt_sink(dm)
    )

    value = expr.evaluate("value")

    assert value == "clock-suffix"
    assert dm.bind.value is True


def test_slot_expr_rerender_clean_shape_for_tuple_result() -> None:
    dm = DM()
    initial_slot_ctx = FakeSlotContext(initial_render=True)
    setter = lambda next_value: next_value
    expr = SlotExpr.single_call(
        lambda initial: (initial, setter),
        lambda: slot_params(3),
        lambda: slot_params_dirt(initial_slot_ctx.literal(3).dirty),
    ).apply_slot_context(initial_slot_ctx).apply_dirt_sink(dm)

    _ = expr.evaluate("result")
    expr.apply_slot_context(FakeSlotContext(initial_render=False))
    result = expr.evaluate("result")

    assert result[0] == 3
    assert dm.bind.result == (False, False)


def test_slot_expr_external_store_ref_refreshes_without_reinvoking_call() -> None:
    store = {"value": 1}
    call_count = {"count": 0}

    def source() -> ExternalStoreRef[int]:
        call_count["count"] += 1
        return ExternalStoreRef(
            identity="store",
            subscribe=lambda listener: (lambda: None),
            get=lambda: store["value"],
        )

    dm = DM()
    slot_ctx = FakeSlotContext(initial_render=True)
    expr = SlotExpr.single_call(
        source,
        lambda: slot_params(),
        lambda: slot_params_dirt(False),
    ).apply_slot_context(slot_ctx).apply_dirt_sink(dm)

    assert expr.evaluate("value") == 1
    assert call_count["count"] == 1

    expr.apply_slot_context(FakeSlotContext(initial_render=False))
    store["value"] = 2
    assert expr.evaluate("value") == 2
    assert call_count["count"] == 1
    assert dm.bind.value is True


def test_slot_expr_effect_like_results_expose_none_and_track_dirty() -> None:
    dm = DM()
    slot_ctx = FakeSlotContext(initial_render=True)
    expr = SlotExpr.single_call(
        lambda: UseEffectRequest(effect_fn=lambda: None, deps=("a",)),
        lambda: slot_params(),
        lambda: slot_params_dirt(slot_ctx.literal(None).dirty),
    ).apply_slot_context(slot_ctx).apply_dirt_sink(dm)

    assert expr.evaluate("effect_result") is None
    assert dm.bind.effect_result is True


@dataclass
class Box:
    value: int = 0


def test_phase_a_attribute_and_subscript_behaviors_can_be_tracked_in_parallel() -> None:
    dm = DM()
    box = Box()
    items = {"value": 0}

    box.value = 3
    setattr(dm.bind, "box.value", True)
    items["value"] = 4
    setattr(dm.bind, "items['value']", False)

    assert dm.is_dirty(dm.lookup("box.value")) is True
    assert dm.is_dirty(dm.lookup("items['value']")) is False
