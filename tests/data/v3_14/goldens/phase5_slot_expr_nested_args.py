from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import LiteralFunctionProvider as __pyr_LiteralFunctionProvider, SlotId as __pyr_SlotId, dm_from_dirty_state as __pyr_dm_from_dirty_state, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry, slot_params as __pyr_slot_params, slot_params_dirt as __pyr_slot_params_dirt
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=18, is_top_level=True)
__pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=18, is_top_level=True)
__pyr_slot_3 = __pyr_SlotId(__pyr_module_id, 3, line_no=18, is_top_level=True)
from pyrolyze.api import pyrolyze, pyrolyze_slotted

@pyrolyze_slotted
def slot_f2(x: int, y: int) -> int:
    return x + y

@pyrolyze_slotted
def slot_f1(value: int) -> tuple[int, int]:
    return (value, value * 2)

def __pyr_panel(__pyr_ctx, __pyr_dirty_state, a: int):
    with __pyr_ctx.pass_scope():
        __pyr_dm = globals()['__pyr_dm_from_dirty_state'](__pyr_dirty_state)
        v1, v2 = __pyr_ctx.slot_expr(__pyr_slot_1, lambda v1, v2: v2.eval(), lambda v1, v2: v2.dirty()).slot_call('v1', __pyr_LiteralFunctionProvider(slot_f2), lambda: __pyr_slot_params(1, a), lambda: __pyr_slot_params_dirt(False, __pyr_dm.bind.a), slot_id=__pyr_slot_2).slot_call('v2', __pyr_LiteralFunctionProvider(slot_f1), lambda v1: __pyr_slot_params(v1.eval()), lambda v1: __pyr_slot_params_dirt(v1.dirty()), slot_id=__pyr_slot_3).apply_dirt_sink(__pyr_dm).evaluate('v1', 'v2')
        pair = (v1, v2)
        __pyr_dm.bind.pair = (__pyr_dm.bind.v1, __pyr_dm.bind.v2)

@__pyr_component_ref(__pyr_ComponentMetadata('panel', __pyr_panel))
def panel(a: int) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('panel')
