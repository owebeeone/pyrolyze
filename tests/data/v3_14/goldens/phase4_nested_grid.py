from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=21)
__pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=22)
__pyr_slot_3 = __pyr_SlotId(__pyr_module_id, 3, line_no=23)
__pyr_slot_4 = __pyr_SlotId(__pyr_module_id, 4, line_no=24)
from pyrolyze.api import UIElement, call_native, keyed, pyrolyse
log: list[tuple[object, ...]] = []

def __pyr_row(__pyr_ctx, __pyr_dirty_state, title: str):
    with __pyr_ctx.pass_scope():
        log.append(('row', title))
        __pyr_ctx.call_native(UIElement, kind='row', props={'title': title})

@__pyr_component_ref(__pyr_ComponentMetadata('row', __pyr_row))
def row(title: str) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('row')

def button(label: str, *, value: int) -> None:
    log.append(('button', label, value))

def __pyr_grid_panel(__pyr_ctx, __pyr_dirty_state, labels: list[str], values: list[int]):
    with __pyr_ctx.pass_scope():
        if __pyr_dirty_state.labels or __pyr_dirty_state.values or __pyr_ctx.visit_slot_and_dirty(__pyr_slot_1):
            for __pyr_ctx_slot_1_k in __pyr_ctx.keyed_loop(__pyr_slot_1, labels, key_fn=lambda x: x):
                with __pyr_ctx_slot_1_k.pass_scope():
                    __pyr_label_dirty, label = __pyr_ctx_slot_1_k.current_value()
                    if not (__pyr_dirty_state.labels or (__pyr_label_dirty or __pyr_dirty_state.values) or __pyr_ctx_slot_1_k.visit_self_and_dirty()):
                        continue
                    if __pyr_label_dirty or (__pyr_dirty_state.values or __pyr_label_dirty) or __pyr_ctx_slot_1_k.visit_slot_and_dirty(__pyr_slot_2):
                        with __pyr_ctx_slot_1_k.container_call(__pyr_slot_2, row, label, dirty_state=__pyr_dirtyof(title=__pyr_label_dirty)) as __pyr_ctx_slot_2:
                            if __pyr_dirty_state.values or __pyr_label_dirty or __pyr_ctx_slot_2.visit_slot_and_dirty(__pyr_slot_3):
                                for __pyr_ctx_slot_3_k in __pyr_ctx_slot_2.keyed_loop(__pyr_slot_3, values, key_fn=lambda x: x):
                                    with __pyr_ctx_slot_3_k.pass_scope():
                                        __pyr_value_dirty, value = __pyr_ctx_slot_3_k.current_value()
                                        if not (__pyr_dirty_state.values or (__pyr_value_dirty or __pyr_label_dirty) or __pyr_ctx_slot_3_k.visit_self_and_dirty()):
                                            continue
                                        if (__pyr_label_dirty or __pyr_value_dirty) or (__pyr_value_dirty or __pyr_label_dirty) or __pyr_ctx_slot_3_k.visit_slot_and_dirty(__pyr_slot_4):
                                            with __pyr_ctx_slot_3_k.container_call(__pyr_slot_4, row, f'{label}:{value}', dirty_state=__pyr_dirtyof(title=__pyr_label_dirty or __pyr_value_dirty)) as __pyr_ctx_slot_4:
                                                button(f'{label}:{value}', value=value)

@__pyr_component_ref(__pyr_ComponentMetadata('grid_panel', __pyr_grid_panel))
def grid_panel(labels: list[str], values: list[int]) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('grid_panel')
