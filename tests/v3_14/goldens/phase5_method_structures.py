from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=26)
__pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=27)
__pyr_slot_3 = __pyr_SlotId(__pyr_module_id, 3, line_no=33)
__pyr_slot_4 = __pyr_SlotId(__pyr_module_id, 4, line_no=34)
__pyr_slot_5 = __pyr_SlotId(__pyr_module_id, 5, line_no=40)
__pyr_slot_6 = __pyr_SlotId(__pyr_module_id, 6, line_no=41)
from pyrolyze.api import UIElement, call_native, keyed, pyrolyse
log: list[tuple[object, ...]] = []

def __pyr_group(__pyr_ctx, __pyr_dirty_state, name: str):
    with __pyr_ctx.pass_scope():
        log.append(('group', name))
        __pyr_ctx.call_native(UIElement, kind='group', props={'name': name})

@__pyr_component_ref(__pyr_ComponentMetadata('group', __pyr_group))
def group(name: str) -> None:
    raise __pyr_CallFromNonPyrolyzeContext('group')

def text(value: str) -> None:
    log.append(('text', value))

def label(value: str) -> None:
    log.append(('label', value))

class Panels:

    def __pyr_Panels__instance(self, __pyr_ctx, __pyr_dirty_state, prefix: str, items: list[str]):
        with __pyr_ctx.pass_scope():
            if (__pyr_dirty_state.items or __pyr_dirty_state.prefix) or __pyr_ctx.visit_slot_and_dirty(globals()['__pyr_slot_1']):
                with __pyr_ctx.container_call(globals()['__pyr_slot_1'], group, 'instance', dirty_state=globals()['__pyr_dirtyof'](name=False)) as __pyr_ctx_slot_1:
                    if __pyr_dirty_state.items or __pyr_dirty_state.prefix or __pyr_ctx_slot_1.visit_slot_and_dirty(globals()['__pyr_slot_2']):
                        for __pyr_ctx_slot_2_k in __pyr_ctx_slot_1.keyed_loop(globals()['__pyr_slot_2'], items, key_fn=lambda x: x):
                            with __pyr_ctx_slot_2_k.pass_scope():
                                __pyr_item_dirty, item = __pyr_ctx_slot_2_k.current_value()
                                if not (__pyr_dirty_state.items or (__pyr_dirty_state.prefix or __pyr_item_dirty) or __pyr_ctx_slot_2_k.visit_self_and_dirty()):
                                    continue
                                text(prefix + item)

    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('Panels.instance', __pyr_Panels__instance))
    def instance(self, prefix: str, items: list[str]) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('Panels.instance')

    def __pyr_Panels__build(cls, __pyr_ctx, __pyr_dirty_state, prefix: str, items: list[str]):
        with __pyr_ctx.pass_scope():
            if (__pyr_dirty_state.items or __pyr_dirty_state.prefix) or __pyr_ctx.visit_slot_and_dirty(globals()['__pyr_slot_3']):
                with __pyr_ctx.container_call(globals()['__pyr_slot_3'], group, 'class', dirty_state=globals()['__pyr_dirtyof'](name=False)) as __pyr_ctx_slot_3:
                    if __pyr_dirty_state.items or __pyr_dirty_state.prefix or __pyr_ctx_slot_3.visit_slot_and_dirty(globals()['__pyr_slot_4']):
                        for __pyr_ctx_slot_4_k in __pyr_ctx_slot_3.keyed_loop(globals()['__pyr_slot_4'], items, key_fn=lambda x: x):
                            with __pyr_ctx_slot_4_k.pass_scope():
                                __pyr_item_dirty, item = __pyr_ctx_slot_4_k.current_value()
                                if not (__pyr_dirty_state.items or (__pyr_dirty_state.prefix or __pyr_item_dirty) or __pyr_ctx_slot_4_k.visit_self_and_dirty()):
                                    continue
                                label(prefix + item)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('Panels.build', __pyr_Panels__build))
    def build(cls, prefix: str, items: list[str]) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('Panels.build')

    def __pyr_Panels__static(__pyr_ctx, __pyr_dirty_state, prefix: str, items: list[str]):
        with __pyr_ctx.pass_scope():
            if (__pyr_dirty_state.items or __pyr_dirty_state.prefix) or __pyr_ctx.visit_slot_and_dirty(globals()['__pyr_slot_5']):
                with __pyr_ctx.container_call(globals()['__pyr_slot_5'], group, 'static', dirty_state=globals()['__pyr_dirtyof'](name=False)) as __pyr_ctx_slot_5:
                    if __pyr_dirty_state.items or __pyr_dirty_state.prefix or __pyr_ctx_slot_5.visit_slot_and_dirty(globals()['__pyr_slot_6']):
                        for __pyr_ctx_slot_6_k in __pyr_ctx_slot_5.keyed_loop(globals()['__pyr_slot_6'], items, key_fn=lambda x: x):
                            with __pyr_ctx_slot_6_k.pass_scope():
                                __pyr_item_dirty, item = __pyr_ctx_slot_6_k.current_value()
                                if not (__pyr_dirty_state.items or (__pyr_dirty_state.prefix or __pyr_item_dirty) or __pyr_ctx_slot_6_k.visit_self_and_dirty()):
                                    continue
                                text(prefix + item)

    @staticmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('Panels.static', __pyr_Panels__static))
    def static(prefix: str, items: list[str]) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('Panels.static')
