from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
from pyrolyze.api import Label, call_native, pyrolyze

def __pyr_label_panel(__pyr_ctx, __pyr_dirty_state, text: str):
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(Label, text=text, __pyr_call_site_id=1)

@__pyr_component_ref(__pyr_ComponentMetadata('label_panel', __pyr_label_panel))
def label_panel(text: str) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('label_panel')
