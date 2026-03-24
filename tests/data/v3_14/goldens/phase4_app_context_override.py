from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=16, is_top_level=True)
from pyrolyze.api import app_context_override, pyrolyze
THEME_KEY: object = object()
LOCALE_KEY: object = object()

def badge(text: str) -> None:
    print(text)

def __pyr_panel(__pyr_ctx, __pyr_dirty_state, theme: str, locale: str, show: bool):
    with __pyr_ctx.pass_scope():
        if (__pyr_dirty_state.theme or __pyr_dirty_state.locale) or __pyr_dirty_state.show or __pyr_ctx.visit_slot_and_dirty(__pyr_slot_1):
            with __pyr_ctx.open_app_context_override(__pyr_slot_1, (THEME_KEY, LOCALE_KEY), theme, locale) as __pyr_ctx_slot_1:
                badge('body')
                if show:
                    badge('extra')

@__pyr_component_ref(__pyr_ComponentMetadata('panel', __pyr_panel))
def panel(theme: str, locale: str, show: bool) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('panel')
