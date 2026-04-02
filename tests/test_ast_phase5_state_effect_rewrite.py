from __future__ import annotations

import pytest

from pyrolyze.compiler import emit_transformed_source, load_transformed_namespace
from pyrolyze.compiler.diagnostics import PyRolyzeCompileError
from pyrolyze.runtime import RenderContext, dirtyof


def test_phase5_lowers_imported_use_state_by_runtime_context_signature() -> None:
    source = """
from pyrolyze.api import pyrolyze, pyrolyze_slotted, use_state

log = []
setters = []

@pyrolyze_slotted
def record(value):
    log.append(("record", value))

@pyrolyze
def panel():
    count, set_count = use_state(0)
    setters[:] = [set_count]
    record(count)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase5.imported_use_state",
        filename="/virtual/example/phase5/imported_use_state.py",
    )

    assert "__pyr_SlotId(__pyr_module_id, 1, line_no=13, is_top_level=True)" in transformed
    assert "__pyr_ctx.slot_expr(" in transformed
    assert ".slot_call(" in transformed
    assert ".evaluate('count', 'set_count')" in transformed or '.evaluate("count", "set_count")' in transformed
    assert "use_state" in transformed
    assert "__pyr_LiteralFunctionProvider(record)" in transformed
    assert ".evaluate()" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase5.imported_use_state",
        filename="/virtual/example/phase5/imported_use_state.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof())
    panel._pyrolyze_meta._func(ctx, dirtyof())
    setter = namespace["setters"][0]
    setter(7)
    panel._pyrolyze_meta._func(ctx, dirtyof())
    panel._pyrolyze_meta._func(ctx, dirtyof())

    assert namespace["log"] == [
        ("record", 0),
        ("record", 7),
    ]


def test_phase5_lowers_aliased_use_state_by_runtime_context_signature() -> None:
    source = """
from pyrolyze.api import pyrolyze, pyrolyze_slotted, use_state as my_us_state

log = []
setters = []

@pyrolyze_slotted
def record(value):
    log.append(("record", value))

@pyrolyze
def panel():
    count, set_count = my_us_state(0)
    setters[:] = [set_count]
    record(count)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase5.aliased_use_state",
        filename="/virtual/example/phase5/aliased_use_state.py",
    )

    assert "my_us_state" in transformed
    assert "__pyr_ctx.slot_expr(" in transformed
    assert ".slot_call(" in transformed
    assert ".evaluate('count', 'set_count')" in transformed or '.evaluate("count", "set_count")' in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase5.aliased_use_state",
        filename="/virtual/example/phase5/aliased_use_state.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof())
    panel._pyrolyze_meta._func(ctx, dirtyof())
    setter = namespace["setters"][0]
    setter(9)
    panel._pyrolyze_meta._func(ctx, dirtyof())
    panel._pyrolyze_meta._func(ctx, dirtyof())

    assert namespace["log"] == [
        ("record", 0),
        ("record", 9),
    ]


def test_phase5_lowers_custom_named_state_helper_with_three_value_destructure() -> None:
    source = """
from typing import Any, Callable, cast

from pyrolyze.api import pyrolyze, pyrolyze_slotted, use_state
from pyrolyze.runtime import PlainCallRuntimeContext

log = []
setters = []

@pyrolyze_slotted
def record(left: int, right: int):
    log.append((left, right))

@pyrolyze_slotted
def my_us_state(
    left_initial: int,
    right_initial: int,
    *,
    __pyrolyze_ctx: PlainCallRuntimeContext = cast(Any, None),
) -> tuple[int, int, Callable[[int, int], None]]:
    pair, set_pair = use_state(
        (left_initial, right_initial),
        __pyrolyze_ctx=__pyrolyze_ctx,
    )
    left, right = pair

    def set_both(next_left: int, next_right: int) -> None:
        set_pair((next_left, next_right))

    return left, right, set_both

@pyrolyze
def panel():
    left, right, set_both = my_us_state(1, 2)
    setters[:] = [set_both]
    record(left, right)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase5.custom_named_use_state",
        filename="/virtual/example/phase5/custom_named_use_state.py",
    )

    assert "my_us_state" in transformed
    assert "__pyr_ctx.slot_expr(" in transformed
    assert ".slot_call(" in transformed
    assert (
        ".evaluate('left', 'right', 'set_both')" in transformed
        or '.evaluate("left", "right", "set_both")' in transformed
    )

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase5.custom_named_use_state",
        filename="/virtual/example/phase5/custom_named_use_state.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof())
    panel._pyrolyze_meta._func(ctx, dirtyof())
    setter = namespace["setters"][0]
    setter(7, 8)
    panel._pyrolyze_meta._func(ctx, dirtyof())
    panel._pyrolyze_meta._func(ctx, dirtyof())

    assert namespace["log"] == [
        (1, 2),
        (7, 8),
    ]


def test_phase5_lowers_imported_use_grip_by_return_contract() -> None:
    source = """
from pyrolyze.api import pyrolyze, use_grip
from pyrolyze.runtime import ExternalStoreRef

log = []

def subscribe(listener):
    return lambda: None

def get_value():
    log.append(("get",))
    return "warm"

STORE = ExternalStoreRef(identity="weather", subscribe=subscribe, get=get_value)

def record(value):
    log.append(("record", value))

@pyrolyze
def panel():
    value = use_grip(STORE)
    record(value)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase5.imported_use_grip",
        filename="/virtual/example/phase5/imported_use_grip.py",
    )

    assert "__pyr_ctx.slot_expr(" in transformed
    assert ".slot_call(" in transformed
    assert ".evaluate('value')" in transformed or '.evaluate("value")' in transformed
    assert "use_grip" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase5.imported_use_grip",
        filename="/virtual/example/phase5/imported_use_grip.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof())
    panel._pyrolyze_meta._func(ctx, dirtyof())

    assert namespace["log"] == [
        ("get",),
        ("record", "warm"),
        ("record", "warm"),
    ]


def test_phase5_lowers_imported_use_effect_statement_call() -> None:
    source = """
from pyrolyze.api import pyrolyze, use_effect

log = []

@pyrolyze
def panel(label):
    def effect():
        log.append(("setup", label))
        return None

    use_effect(effect, deps=[label])
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase5.imported_use_effect",
        filename="/virtual/example/phase5/imported_use_effect.py",
    )

    assert "__pyr_ctx.slot_expr(" in transformed
    assert ".slot_call(" in transformed
    assert ".evaluate()" in transformed
    assert "use_effect" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase5.imported_use_effect",
        filename="/virtual/example/phase5/imported_use_effect.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(label=True), "alpha")
    panel._pyrolyze_meta._func(ctx, dirtyof(label=False), "alpha")
    panel._pyrolyze_meta._func(ctx, dirtyof(label=True), "beta")

    assert namespace["log"] == [
        ("setup", "alpha"),
        ("setup", "beta"),
    ]


def test_phase5_hoists_use_grip_inside_or_expression() -> None:
    source = """
from pyrolyze.api import pyrolyze, use_grip
from pyrolyze.runtime import ExternalStoreRef

log = []

def subscribe(listener):
    return lambda: None

def get_value():
    log.append(("get",))
    return ""

STORE = ExternalStoreRef(identity="weather", subscribe=subscribe, get=get_value)

def record(value):
    log.append(("record", value))

@pyrolyze
def panel():
    value = use_grip(STORE) or "clock"
    record(value)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase5.use_grip_or_expression",
        filename="/virtual/example/phase5/use_grip_or_expression.py",
    )

    assert "__pyr_ctx.slot_expr(" in transformed
    assert ".slot_call(" in transformed
    assert ".evaluate('value')" in transformed or '.evaluate("value")' in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase5.use_grip_or_expression",
        filename="/virtual/example/phase5/use_grip_or_expression.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof())
    assert namespace["log"] == [
        ("get",),
        ("record", "clock"),
    ]


def test_phase5_hoists_use_grip_inside_int_coercion_expression() -> None:
    source = """
from pyrolyze.api import pyrolyze, use_grip
from pyrolyze.runtime import ExternalStoreRef

log = []

def subscribe(listener):
    return lambda: None

def get_value():
    log.append(("get",))
    return None

STORE = ExternalStoreRef(identity="count", subscribe=subscribe, get=get_value)

def record(value):
    log.append(("record", value))

@pyrolyze
def panel():
    count = int(use_grip(STORE) or 0)
    record(count)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase5.use_grip_int_expression",
        filename="/virtual/example/phase5/use_grip_int_expression.py",
    )

    assert "__pyr_ctx.slot_expr(" in transformed
    assert ".slot_call(" in transformed
    assert ".evaluate('count')" in transformed or '.evaluate("count")' in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase5.use_grip_int_expression",
        filename="/virtual/example/phase5/use_grip_int_expression.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof())
    assert namespace["log"] == [
        ("get",),
        ("record", 0),
    ]


def test_phase5_lowers_multiple_slot_calls_inside_binop_expression() -> None:
    source = """
from pyrolyze.api import pyrolyze, pyrolyze_slotted

log = []

@pyrolyze_slotted
def slot_fa(x, y):
    log.append(("a", x, y))
    return x + y

@pyrolyze_slotted
def slot_fb(x, y):
    log.append(("b", x, y))
    return x * y

def record(value):
    log.append(("record", value))

@pyrolyze
def panel(x, y):
    value = slot_fa(x, y) + slot_fb(1, 2)
    record(value)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase5.slot_expr_binop",
        filename="/virtual/example/phase5/slot_expr_binop.py",
    )

    assert "__pyr_ctx.slot_expr(" in transformed
    assert transformed.count(".slot_call(") >= 2

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase5.slot_expr_binop",
        filename="/virtual/example/phase5/slot_expr_binop.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(x=True, y=True), 3, 4)

    assert namespace["log"] == [
        ("a", 3, 4),
        ("b", 1, 2),
        ("record", 9),
    ]


def test_phase5_lowers_nested_slot_call_arguments() -> None:
    source = """
from pyrolyze.api import pyrolyze, pyrolyze_slotted

log = []

@pyrolyze_slotted
def slot_f2(x, y):
    log.append(("f2", x, y))
    return x + y

@pyrolyze_slotted
def slot_f1(value):
    log.append(("f1", value))
    return value, value * 2

@pyrolyze
def panel(a):
    v1, v2 = slot_f1(slot_f2(1, a))
    log.append(("pair", v1, v2))
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase5.slot_expr_nested_args",
        filename="/virtual/example/phase5/slot_expr_nested_args.py",
    )

    assert "__pyr_ctx.slot_expr(" in transformed
    assert transformed.count(".slot_call(") >= 2

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase5.slot_expr_nested_args",
        filename="/virtual/example/phase5/slot_expr_nested_args.py",
    )
    panel = namespace["panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(a=True), 5)

    assert namespace["log"] == [
        ("f2", 1, 5),
        ("f1", 6),
        ("pair", 6, 12),
    ]


def test_phase5_rejects_walrus_inside_slot_bearing_expression() -> None:
    source = """
from pyrolyze.api import pyrolyze, use_grip
from pyrolyze.runtime import ExternalStoreRef

def subscribe(listener):
    return lambda: None

def get_value():
    return "warm"

STORE = ExternalStoreRef(identity="weather", subscribe=subscribe, get=get_value)

@pyrolyze
def panel():
    value = (current := use_grip(STORE)) or "clock"
"""

    with pytest.raises(
        PyRolyzeCompileError,
        match="slot-bearing expressions do not support walrus operators or comprehensions in Phase C",
    ):
        emit_transformed_source(
            source,
            module_name="example.phase5.slot_expr_walrus_rejected",
            filename="/virtual/example/phase5/slot_expr_walrus_rejected.py",
        )
