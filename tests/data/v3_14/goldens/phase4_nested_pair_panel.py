from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=21, is_top_level=True)
__pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=23, is_top_level=True)
from pyrolyze.api import UIElement, call_native, pyrolyze
log: list[tuple[object, ...]] = []

def __pyr_row(__pyr_ctx, __pyr_dirty_state, name: str):
    with __pyr_ctx.pass_scope():
        log.append(('row', name))
        __pyr_ctx.call_native(UIElement, kind='row', props={'name': name}, __pyr_call_site_id=1)

@__pyr_component_ref(__pyr_ComponentMetadata('row', __pyr_row))
def row(name: str) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('row')

def label(text: str) -> None:
    log.append(('label', text))

def __pyr_pair_panel(__pyr_ctx, __pyr_dirty_state, v1: str, v2: str):
    with __pyr_ctx.pass_scope():
        if (__pyr_dirty_state.v1 or __pyr_dirty_state.v2) or __pyr_ctx.visit_slot_and_dirty(__pyr_slot_1):
            with __pyr_ctx.container_call(__pyr_slot_1, row, 'outer', dirty_state=__pyr_dirtyof(name=False)) as __pyr_ctx_slot_1:
                label('row-start')
                if (__pyr_dirty_state.v1 or __pyr_dirty_state.v2) or __pyr_ctx_slot_1.visit_slot_and_dirty(__pyr_slot_2):
                    with __pyr_ctx_slot_1.container_call(__pyr_slot_2, row, 'inner', dirty_state=__pyr_dirtyof(name=False)) as __pyr_ctx_slot_2:
                        label(v1)
                        label(v2)

@__pyr_component_ref(__pyr_ComponentMetadata('pair_panel', __pyr_pair_panel))
def pair_panel(v1: str, v2: str) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('pair_panel')
