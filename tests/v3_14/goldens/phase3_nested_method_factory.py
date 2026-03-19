from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
__pyr_slot_1 = __pyr_SlotId(__pyr_module_id, 1, line_no=21)
from pyrolyze.api import ComponentRef, pyrolyse, pyrolyze_slotted

@pyrolyze_slotted
def upper(label: str) -> str:
    return label.upper()

def record(value: str) -> str:
    return value

class PanelFactory:
    prefix: str

    def make(self) -> ComponentRef[[str]]:

        def __pyr_PanelFactory__make___locals___panel(__pyr_ctx, __pyr_dirty_state, label: str):
            with __pyr_ctx.pass_scope():
                __pyr_value_dirty, value = __pyr_ctx.call_plain(globals()['__pyr_slot_1'], upper, label)
                record(self.prefix + ':' + value)

        @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('PanelFactory.make.<locals>.panel', __pyr_PanelFactory__make___locals___panel))
        def panel(label: str) -> None:
            raise globals()['__pyr_CallFromNonPyrolyzeContext']('PanelFactory.make.<locals>.panel')
        return panel
