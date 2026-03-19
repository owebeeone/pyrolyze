from __future__ import annotations

from pyrolyze.compiler import emit_transformed_source, load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof


def test_phase5_lowers_imported_use_state_by_runtime_context_signature() -> None:
    source = """
from pyrolyze.api import pyrolyse, pyrolyze_slotted, use_state

log = []
setters = []

@pyrolyze_slotted
def record(value):
    log.append(("record", value))

@pyrolyse
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
    assert "(__pyr_count_dirty, __pyr_set_count_dirty), (count, set_count) = __pyr_ctx.call_plain(" in transformed
    assert "use_state" in transformed
    assert "result_shape=('tuple', 2)" in transformed
    assert "record, count" in transformed

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


def test_phase5_lowers_imported_use_grip_by_return_contract() -> None:
    source = """
from pyrolyze.api import pyrolyse, use_grip
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

@pyrolyse
def panel():
    value = use_grip(STORE)
    record(value)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase5.imported_use_grip",
        filename="/virtual/example/phase5/imported_use_grip.py",
    )

    assert "__pyr_value_dirty, value = __pyr_ctx.call_plain(" in transformed
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
from pyrolyze.api import pyrolyse, use_effect

log = []

@pyrolyse
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

    assert "__pyr_ctx.call_plain(" in transformed
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
