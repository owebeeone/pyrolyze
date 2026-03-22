from pyrolyze.api import CallFromNonPyrolyzeContext as __pyr_CallFromNonPyrolyzeContext, ComponentMetadata as __pyr_ComponentMetadata, pyrolyze_component_ref as __pyr_component_ref
from pyrolyze.runtime import SlotId as __pyr_SlotId, dirtyof as __pyr_dirtyof, module_registry as __pyr_module_registry
__pyr_module_id = __pyr_module_registry.module_id(__name__)
from typing import Any
from pyrolyze.api import UIElement, call_native, pyrolyze, ui_interface

@ui_interface
class PySide6UiLibrary:

    @classmethod
    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
        return UIElement(kind=kind, props=dict(kwds))

    def __pyr_PySide6UiLibrary__CQPushButton(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='QPushButton', kwds=kwds, __pyr_call_site_id=1)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('PySide6UiLibrary.CQPushButton', __pyr_PySide6UiLibrary__CQPushButton, packed_kwargs=True, packed_kwarg_param_names=('text', 'flat', 'enabled')))
    def CQPushButton(cls, text: str, *, flat: bool | None=None, enabled: bool | None=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('PySide6UiLibrary.CQPushButton')

    def __pyr_PySide6UiLibrary__CQLabel(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(cls.__element, kind='QLabel', kwds=kwds, __pyr_call_site_id=2)

    @classmethod
    @globals()['__pyr_component_ref'](globals()['__pyr_ComponentMetadata']('PySide6UiLibrary.CQLabel', __pyr_PySide6UiLibrary__CQLabel, packed_kwargs=True, packed_kwarg_param_names=('text', 'wordWrap', 'openExternalLinks')))
    def CQLabel(cls, text: str, *, wordWrap: bool | None=None, openExternalLinks: bool | None=None) -> None:
        raise globals()['__pyr_CallFromNonPyrolyzeContext']('PySide6UiLibrary.CQLabel')
