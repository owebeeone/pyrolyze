from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=23, is_top_level=True)
__pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=23, is_top_level=True)
from pyrolyze.api import PyrolyzeHandler, UIElement, call_native, pyrolyse
log: list[str] = []

def __pyr_button(__pyr_ctx, __pyr_dirty_state, label: str, *, on_press: PyrolyzeHandler[[], None] | None=None):
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(UIElement, kind='button', props={'label': label, 'on_press': on_press}, __pyr_call_site_id=1)

@__pyr_component_ref(__pyr_ComponentMetadata('button', __pyr_button))
def button(label: str, *, on_press: PyrolyzeHandler[[], None] | None=None) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('button')

def __pyr_panel(__pyr_ctx, __pyr_dirty_state, name: str):
    with __pyr_ctx.pass_scope():
        if __pyr_dirty_state.name or __pyr_ctx.visit_slot_and_dirty(__pyr_slot_1):
            __pyr_ctx.component_call(__pyr_slot_1, button, 'Save', on_press=__pyr_ctx.event_handler(__pyr_slot_2, dirty=__pyr_dirty_state.name, callback=lambda: log.append(name)), dirty_state=__pyr_dirtyof(label=False, on_press=__pyr_dirty_state.name))

@__pyr_component_ref(__pyr_ComponentMetadata('panel', __pyr_panel))
def panel(name: str) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('panel')
