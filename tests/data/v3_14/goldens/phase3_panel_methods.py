from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=20, is_top_level=True)
__pyr_slot_2 = __pyr_SlotId(__pyr_module_id, 2, line_no=26, is_top_level=True)
__pyr_slot_3 = __pyr_SlotId(__pyr_module_id, 3, line_no=32, is_top_level=True)
from pyrolyze.api import pyrolyse, pyrolyze_slotted

@pyrolyze_slotted
def upper(label: str) -> str:
    return label.upper()

def record(value: str) -> str:
    return value

class Panel:
    prefix: str

    def __pyr_Panel__show(self, __pyr_ctx, __pyr_dirty_state, label: str):
        with __pyr_ctx.pass_scope():
            __pyr_value_dirty, value = __pyr_ctx.call_plain(globals()['__pyr_slot_1'], upper, label)
            record(self.prefix + ':' + value)

    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('Panel.show', __pyr_Panel__show))
    def show(self, label: str) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('Panel.show')

    def __pyr_Panel__build(cls, __pyr_ctx, __pyr_dirty_state, label: str):
        with __pyr_ctx.pass_scope():
            __pyr_value_dirty, value = __pyr_ctx.call_plain(globals()['__pyr_slot_2'], upper, label)
            record(cls.__name__ + ':' + value)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('Panel.build', __pyr_Panel__build))
    def build(cls, label: str) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('Panel.build')

    def __pyr_Panel__static(__pyr_ctx, __pyr_dirty_state, label: str):
        with __pyr_ctx.pass_scope():
            __pyr_value_dirty, value = __pyr_ctx.call_plain(globals()['__pyr_slot_3'], upper, label)
            record('static:' + value)

    @staticmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('Panel.static', __pyr_Panel__static))
    def static(label: str) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('Panel.static')
