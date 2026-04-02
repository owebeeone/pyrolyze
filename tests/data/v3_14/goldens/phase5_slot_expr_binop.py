from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import LiteralFunctionProvider as __pyr_LiteralFunctionProvider, SlotId as __pyr_SlotId, dm_from_dirty_state as __pyr_dm_from_dirty_state, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry, slot_params as __pyr_slot_params, slot_params_dirt as __pyr_slot_params_dirt
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=22, is_top_level=True)
__pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=22, is_top_level=True)
from pyrolyze.api import pyrolyze, pyrolyze_slotted

@pyrolyze_slotted
def slot_fa(x: int, y: int) -> int:
    return x + y

@pyrolyze_slotted
def slot_fb(x: int, y: int) -> int:
    return x * y

def record(value: int) -> int:
    return value

def __pyr_panel(__pyr_ctx, __pyr_dirty_state, x: int, y: int):
    with __pyr_ctx.pass_scope():
        __pyr_dm = globals()['__pyr_dm_from_dirty_state'](__pyr_dirty_state)
        value = __pyr_ctx.slot_expr(lambda v1, v2: v1.eval() + v2.eval(), lambda v1, v2: v1.dirty() or v2.dirty()).slot_call('v1', __pyr_LiteralFunctionProvider(slot_fa), lambda: __pyr_slot_params(x, y), lambda: __pyr_slot_params_dirt(__pyr_dm.bind.x, __pyr_dm.bind.y), slot_id=__pyr_slot_1).slot_call('v2', __pyr_LiteralFunctionProvider(slot_fb), lambda v1: __pyr_slot_params(1, 2), lambda v1: __pyr_slot_params_dirt(False, False), slot_id=__pyr_slot_2).apply_dirt_sink(__pyr_dm).evaluate('value')
        record(value)

@__pyr_component_ref(__pyr_ComponentMetadata('panel', __pyr_panel))
def panel(x: int, y: int) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('panel')
