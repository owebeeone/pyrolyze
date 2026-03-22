from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=17, is_top_level=True)
from pyrolyze.api import pyrolyze as component, pyrolyze_slotted as slotted

@slotted
def upper(label: str) -> str:
    return label.upper()

def record(value: str) -> str:
    return value

def __pyr_panel(__pyr_ctx, __pyr_dirty_state, label: str):
    with __pyr_ctx.pass_scope():
        __pyr_value_dirty, value = __pyr_ctx.call_plain(__pyr_slot_1, upper, label)
        record(value)

@__pyr_component_ref(__pyr_ComponentMetadata('panel', __pyr_panel))
def panel(label: str) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('panel')
