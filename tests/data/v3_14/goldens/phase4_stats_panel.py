from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=21, is_top_level=True)
from pyrolyze.api import UIElement, call_native, pyrolyse
log: list[tuple[object, ...]] = []

def __pyr_section(__pyr_ctx, __pyr_dirty_state, title: str, *, accent: str):
    with __pyr_ctx.pass_scope():
        log.append(('section', title, accent))
        __pyr_ctx.call_native(UIElement, kind='section', props={'title': title, 'accent': accent}, __pyr_call_site_id=1)

@__pyr_component_ref(__pyr_ComponentMetadata('section', __pyr_section))
def section(title: str, *, accent: str) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('section')

def badge(text: str, *, tone: str) -> None:
    log.append(('badge', text, tone))

def __pyr_stats_panel(__pyr_ctx, __pyr_dirty_state, show_extra: bool, count: int):
    with __pyr_ctx.pass_scope():
        if (__pyr_dirty_state.count or __pyr_dirty_state.show_extra) or __pyr_ctx.visit_slot_and_dirty(__pyr_slot_1):
            with __pyr_ctx.container_call(__pyr_slot_1, section, 'Stats', accent='green', dirty_state=__pyr_dirtyof(title=False, accent=False)) as __pyr_ctx_slot_1:
                badge(f'Count: {count}', tone='info')
                if show_extra:
                    badge('Visible', tone='success')
                else:
                    badge('Hidden', tone='muted')

@__pyr_component_ref(__pyr_ComponentMetadata('stats_panel', __pyr_stats_panel))
def stats_panel(show_extra: bool, count: int) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('stats_panel')
