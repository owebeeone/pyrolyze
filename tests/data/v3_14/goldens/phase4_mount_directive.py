from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import LiteralFunctionProvider as __pyr_LiteralFunctionProvider, SlotId as __pyr_SlotId, dm_from_dirty_state as __pyr_dm_from_dirty_state, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry, slot_params as __pyr_slot_params, slot_params_dirt as __pyr_slot_params_dirt
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=15, is_top_level=True)
__pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=16, is_top_level=True)
__pyr_slot_3 = __pyr_SlotId(__pyr_module_id, 3, line_no=18, is_top_level=True)
__pyr_slot_4 = __pyr_SlotId(__pyr_module_id, 4, line_no=19, is_top_level=True)
from pyrolyze.api import MountSelector, UIElement, call_native, default, mount, pyrolyze
menu: MountSelector = MountSelector.named('menu')
corner: MountSelector = MountSelector.named('corner_widget')

def __pyr_badge(__pyr_ctx, __pyr_dirty_state, text: str):
    with __pyr_ctx.pass_scope():
        __pyr_dm = globals()['__pyr_dm_from_dirty_state'](__pyr_dirty_state)
        __pyr_ctx.call_native(UIElement, kind='badge', props={'text': text}, __pyr_call_site_id=1)

@__pyr_component_ref(__pyr_ComponentMetadata('badge', __pyr_badge))
def badge(text: str) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('badge')

def __pyr_panel(__pyr_ctx, __pyr_dirty_state, show_inner: bool):
    with __pyr_ctx.pass_scope():
        __pyr_dm = globals()['__pyr_dm_from_dirty_state'](__pyr_dirty_state)
        if __pyr_dm.bind.show_inner or __pyr_ctx.visit_slot_and_dirty(__pyr_slot_1):
            with __pyr_ctx.container_call(__pyr_slot_1, mount, menu, default, dirty_state=__pyr_dirtyof()) as __pyr_ctx_slot_1:
                if __pyr_ctx_slot_1.visit_slot_and_dirty(__pyr_slot_2):
                    __pyr_ctx_slot_1.component_call(__pyr_slot_2, badge, 'File', dirty_state=__pyr_dirtyof(text=False))
                if show_inner:
                    if __pyr_ctx_slot_1.visit_slot_and_dirty(__pyr_slot_3):
                        with __pyr_ctx_slot_1.container_call(__pyr_slot_3, mount, corner(corner='top_left'), dirty_state=__pyr_dirtyof()) as __pyr_ctx_slot_3:
                            if __pyr_ctx_slot_3.visit_slot_and_dirty(__pyr_slot_4):
                                __pyr_ctx_slot_3.component_call(__pyr_slot_4, badge, 'Edit', dirty_state=__pyr_dirtyof(text=False))

@__pyr_component_ref(__pyr_ComponentMetadata('panel', __pyr_panel))
def panel(show_inner: bool) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('panel')
