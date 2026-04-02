from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import LiteralFunctionProvider as __pyr_LiteralFunctionProvider, SlotId as __pyr_SlotId, dm_from_dirty_state as __pyr_dm_from_dirty_state, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry, slot_params as __pyr_slot_params, slot_params_dirt as __pyr_slot_params_dirt
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=16, is_top_level=True)
__pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=18, is_top_level=True)
from pyrolyze.api import pyrolyze
from pyrolyze_testsupport.imported_annotations import imported_child, imported_upper
log: list[tuple[object, ...]] = []

def record(value: str) -> None:
    log.append(('record', value))

def __pyr_imported_panel(__pyr_ctx, __pyr_dirty_state, text: str):
    with __pyr_ctx.pass_scope():
        __pyr_dm = globals()['__pyr_dm_from_dirty_state'](__pyr_dirty_state)
        value = __pyr_ctx.slot_expr(lambda v1: v1.eval(), lambda v1: v1.dirty()).slot_call('v1', __pyr_LiteralFunctionProvider(imported_upper), lambda: __pyr_slot_params(text), lambda: __pyr_slot_params_dirt(__pyr_dm.bind.text), slot_id=__pyr_slot_1).apply_dirt_sink(__pyr_dm).evaluate('value')
        record(value)
        if __pyr_dm.bind.value or __pyr_ctx.visit_slot_and_dirty(__pyr_slot_2):
            __pyr_ctx.component_call(__pyr_slot_2, imported_child, value, dirty_state=__pyr_dirtyof(text=__pyr_dm.bind.value))

@__pyr_component_ref(__pyr_ComponentMetadata('imported_panel', __pyr_imported_panel))
def imported_panel(text: str) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('imported_panel')
