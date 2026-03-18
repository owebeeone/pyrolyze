from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
from contextlib import contextmanager
from pyrolyze.api import pyrolyse
log = []

@contextmanager
def section(title, *, accent):
    log.append(('section.enter', title, accent))
    try:
        yield
    finally:
        log.append(('section.exit', title, accent))

def badge(text, *, tone):
    log.append(('badge', text, tone))

def __pyr_stats_panel(ctx, __pyr_dirty_state, show_extra, count):
    with ctx.pass_scope():
        __pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=21)
        if (__pyr_dirty_state.count or __pyr_dirty_state.show_extra) or ctx.visit_slot_and_dirty(__pyr_slot_1):
            with ctx.container_call(__pyr_slot_1, section, 'Stats', accent='green') as __pyr_section_ctx:
                __pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=22)
                if __pyr_dirty_state.count or __pyr_section_ctx.visit_slot_and_dirty(__pyr_slot_2):
                    __pyr_section_ctx.leaf_call(__pyr_slot_2, badge, f'Count: {count}', tone='info')
                if show_extra:
                    __pyr_slot_3 = __pyr_SlotId(__pyr_module_id, 3, line_no=24)
                    if __pyr_section_ctx.visit_slot_and_dirty(__pyr_slot_3):
                        __pyr_section_ctx.leaf_call(__pyr_slot_3, badge, 'Visible', tone='success')
                else:
                    __pyr_slot_4 = __pyr_SlotId(__pyr_module_id, 4, line_no=26)
                    if __pyr_section_ctx.visit_slot_and_dirty(__pyr_slot_4):
                        __pyr_section_ctx.leaf_call(__pyr_slot_4, badge, 'Hidden', tone='muted')

@__pyr_component_ref(__pyr_ComponentMetadata('stats_panel', __pyr_stats_panel))
def stats_panel(show_extra, count):
    raise __pyr_CallFromNonPyrolyzeContext('stats_panel')
