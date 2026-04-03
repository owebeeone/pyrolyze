from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import LiteralFunctionProvider as __pyr_LiteralFunctionProvider, SlotId as __pyr_SlotId, dm_from_dirty_state as __pyr_dm_from_dirty_state, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry, slot_params as __pyr_slot_params, slot_params_dirt as __pyr_slot_params_dirt
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=17, is_top_level=True)
__pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=17, is_top_level=True)
from pyrolyze.api import pyrolyze, pyrolyze_slotted

@pyrolyze_slotted
def format_title(name: str) -> str:
    return f'Hello {name}'

def record(value: str) -> str:
    return value

def __pyr_greeting(__pyr_ctx, __pyr_dirty_state, name: str):
    with __pyr_ctx.pass_scope():
        __pyr_dm = globals()['__pyr_dm_from_dirty_state'](__pyr_dirty_state)
        title = __pyr_ctx.slot_expr(__pyr_slot_1, lambda v1: v1.eval(), lambda v1: v1.dirty()).slot_call('v1', __pyr_LiteralFunctionProvider(format_title), lambda: __pyr_slot_params(name), lambda: __pyr_slot_params_dirt(__pyr_dm.bind.name), slot_id=__pyr_slot_2).apply_dirt_sink(__pyr_dm).evaluate('title')
        label = title + '!'
        __pyr_dm.bind.label = __pyr_dm.bind.title
        record(label)

@__pyr_component_ref(__pyr_ComponentMetadata('greeting', __pyr_greeting))
def greeting(name: str) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('greeting')
