from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import LiteralFunctionProvider as __pyr_LiteralFunctionProvider, SlotId as __pyr_SlotId, dm_from_dirty_state as __pyr_dm_from_dirty_state, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry, slot_params as __pyr_slot_params, slot_params_dirt as __pyr_slot_params_dirt
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=13, is_top_level=True)
__pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=13, is_top_level=True)
__pyr_slot_3 = __pyr_SlotId(__pyr_module_id, 3, line_no=14, is_top_level=True)
__pyr_slot_4 = __pyr_SlotId(__pyr_module_id, 4, line_no=14, is_top_level=True)
from pyrolyze.api import pyrolyze, pyrolyze_slotted

@pyrolyze_slotted
def use_grip(key: str) -> str:
    return key

def __pyr_panel(__pyr_ctx, __pyr_dirty_state, flag: bool):
    with __pyr_ctx.pass_scope():
        __pyr_dm = globals()['__pyr_dm_from_dirty_state'](__pyr_dirty_state)
        k = __pyr_ctx.slot_expr(__pyr_slot_1, lambda v1: v1.eval(), lambda v1: v1.dirty()).slot_call('v1', __pyr_LiteralFunctionProvider(use_grip), lambda: __pyr_slot_params('A'), lambda: __pyr_slot_params_dirt(False), slot_id=__pyr_slot_2).apply_dirt_sink(__pyr_dm).evaluate('k')
        v = __pyr_ctx.slot_expr(__pyr_slot_3, lambda v2: 10 if flag else v2.eval(), lambda v2: __pyr_dm.bind.flag or (False if flag else v2.dirty())).slot_call('v2', __pyr_LiteralFunctionProvider(use_grip), lambda: __pyr_slot_params(k), lambda: __pyr_slot_params_dirt(__pyr_dm.bind.k), slot_id=__pyr_slot_4).apply_dirt_sink(__pyr_dm).evaluate('v')

@__pyr_component_ref(__pyr_ComponentMetadata('panel', __pyr_panel))
def panel(flag: bool) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('panel')
