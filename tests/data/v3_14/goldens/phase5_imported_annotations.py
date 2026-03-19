from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=16, is_top_level=True)
__pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=18, is_top_level=True)
from pyrolyze.api import pyrolyse
from pyrolyze_testsupport.imported_annotations import imported_child, imported_upper
log: list[tuple[object, ...]] = []

def record(value: str) -> None:
    log.append(('record', value))

def __pyr_imported_panel(__pyr_ctx, __pyr_dirty_state, text: str):
    with __pyr_ctx.pass_scope():
        __pyr_value_dirty, value = __pyr_ctx.call_plain(__pyr_slot_1, imported_upper, text)
        record(value)
        if __pyr_value_dirty or __pyr_ctx.visit_slot_and_dirty(__pyr_slot_2):
            __pyr_ctx.component_call(__pyr_slot_2, imported_child, value, dirty_state=__pyr_dirtyof(text=__pyr_value_dirty))

@__pyr_component_ref(__pyr_ComponentMetadata('imported_panel', __pyr_imported_panel))
def imported_panel(text: str) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('imported_panel')
