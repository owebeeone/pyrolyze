from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import LiteralFunctionProvider as __pyr_LiteralFunctionProvider, SlotId as __pyr_SlotId, dm_from_dirty_state as __pyr_dm_from_dirty_state, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry, slot_params as __pyr_slot_params, slot_params_dirt as __pyr_slot_params_dirt
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=17, is_top_level=True)
__pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=17, is_top_level=True)
from pyrolyze.api import pyrolyze as component, pyrolyze_slotted as slotted

@slotted
def upper(label: str) -> str:
    return label.upper()

def record(value: str) -> str:
    return value

def __pyr_panel(__pyr_ctx, __pyr_dirty_state, label: str):
    with __pyr_ctx.pass_scope():
        __pyr_dm = globals()['__pyr_dm_from_dirty_state'](__pyr_dirty_state)
        value = __pyr_ctx.slot_expr(__pyr_slot_1, lambda v1: v1.eval(), lambda v1: v1.dirty()).slot_call('v1', __pyr_LiteralFunctionProvider(upper), lambda: __pyr_slot_params(label), lambda: __pyr_slot_params_dirt(__pyr_dm.bind.label), slot_id=__pyr_slot_2).apply_dirt_sink(__pyr_dm).evaluate('value')
        record(value)

@__pyr_component_ref(__pyr_ComponentMetadata('panel', __pyr_panel))
def panel(label: str) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('panel')
