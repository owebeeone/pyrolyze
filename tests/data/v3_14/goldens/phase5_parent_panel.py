from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=20, is_top_level=True)
from pyrolyze.api import pyrolyze
log: list[tuple[object, ...]] = []

def badge(text: str, *, tone: str) -> None:
    log.append(('badge', text, tone))

def __pyr_child_badge(__pyr_ctx, __pyr_dirty_state, text: str):
    with __pyr_ctx.pass_scope():
        badge(text, tone='info')

@__pyr_component_ref(__pyr_ComponentMetadata('child_badge', __pyr_child_badge))
def child_badge(text: str) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('child_badge')

def __pyr_parent_panel(__pyr_ctx, __pyr_dirty_state, text: str):
    with __pyr_ctx.pass_scope():
        if __pyr_dirty_state.text or __pyr_ctx.visit_slot_and_dirty(__pyr_slot_1):
            __pyr_ctx.component_call(__pyr_slot_1, child_badge, text, dirty_state=__pyr_dirtyof(text=__pyr_dirty_state.text))

@__pyr_component_ref(__pyr_ComponentMetadata('parent_panel', __pyr_parent_panel))
def parent_panel(text: str) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('parent_panel')
