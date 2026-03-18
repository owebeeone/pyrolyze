from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
from pyrolyze.api import pyrolyse, pyrolyze_slotted

@pyrolyze_slotted
def format_title(name):
    return f'Hello {name}'

def record(value):
    return value

def __pyr_greeting(ctx, __pyr_dirty_state, name):
    with ctx.pass_scope():
        __pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=13)
        __pyr_title_dirty, title = ctx.call_plain(__pyr_slot_1, format_title, name)
        label = title + '!'
        __pyr_label_dirty = __pyr_title_dirty
        __pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=15)
        if __pyr_label_dirty or ctx.visit_slot_and_dirty(__pyr_slot_2):
            ctx.leaf_call(__pyr_slot_2, record, label)

@__pyr_component_ref(__pyr_ComponentMetadata('greeting', __pyr_greeting))
def greeting(name):
    raise __pyr_CallFromNonPyrolyzeContext('greeting')
