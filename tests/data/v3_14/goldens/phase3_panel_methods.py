from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import LiteralFunctionProvider as __pyr_LiteralFunctionProvider, SlotId as __pyr_SlotId, dm_from_dirty_state as __pyr_dm_from_dirty_state, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry, slot_params as __pyr_slot_params, slot_params_dirt as __pyr_slot_params_dirt
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=20, is_top_level=True)
__pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=26, is_top_level=True)
__pyr_slot_3 = __pyr_SlotId(__pyr_module_id, 3, line_no=32, is_top_level=True)
from pyrolyze.api import pyrolyze, pyrolyze_slotted

@pyrolyze_slotted
def upper(label: str) -> str:
    return label.upper()

def record(value: str) -> str:
    return value

class Panel:
    prefix: str

    def __pyr_Panel__show(self, __pyr_ctx, __pyr_dirty_state, label: str):
        with __pyr_ctx.pass_scope():
            __pyr_dm = globals()['__pyr_dm_from_dirty_state'](__pyr_dirty_state)
            value = __pyr_ctx.slot_expr(lambda v1: v1.eval(), lambda v1: v1.dirty()).slot_call('v1', globals()['__pyr_LiteralFunctionProvider'](upper), lambda: globals()['__pyr_slot_params'](label), lambda: globals()['__pyr_slot_params_dirt'](__pyr_dm.bind.label), slot_id=globals()['__pyr_slot_1']).apply_dirt_sink(__pyr_dm).evaluate('value')
            record(self.prefix + ':' + value)

    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('Panel.show', __pyr_Panel__show))
    def show(self, label: str) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('Panel.show')

    def __pyr_Panel__build(cls, __pyr_ctx, __pyr_dirty_state, label: str):
        with __pyr_ctx.pass_scope():
            __pyr_dm = globals()['__pyr_dm_from_dirty_state'](__pyr_dirty_state)
            value = __pyr_ctx.slot_expr(lambda v2: v2.eval(), lambda v2: v2.dirty()).slot_call('v2', globals()['__pyr_LiteralFunctionProvider'](upper), lambda: globals()['__pyr_slot_params'](label), lambda: globals()['__pyr_slot_params_dirt'](__pyr_dm.bind.label), slot_id=globals()['__pyr_slot_2']).apply_dirt_sink(__pyr_dm).evaluate('value')
            record(cls.__name__ + ':' + value)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('Panel.build', __pyr_Panel__build))
    def build(cls, label: str) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('Panel.build')

    def __pyr_Panel__static(__pyr_ctx, __pyr_dirty_state, label: str):
        with __pyr_ctx.pass_scope():
            __pyr_dm = globals()['__pyr_dm_from_dirty_state'](__pyr_dirty_state)
            value = __pyr_ctx.slot_expr(lambda v3: v3.eval(), lambda v3: v3.dirty()).slot_call('v3', globals()['__pyr_LiteralFunctionProvider'](upper), lambda: globals()['__pyr_slot_params'](label), lambda: globals()['__pyr_slot_params_dirt'](__pyr_dm.bind.label), slot_id=globals()['__pyr_slot_3']).apply_dirt_sink(__pyr_dm).evaluate('value')
            record('static:' + value)

    @staticmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('Panel.static', __pyr_Panel__static))
    def static(label: str) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('Panel.static')
