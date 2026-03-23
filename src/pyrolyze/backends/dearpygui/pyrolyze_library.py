"""Compiler-facing ``CDpg*`` component stubs for native DearPyGui ``@pyrolyze`` apps.

Mirrors :class:`~pyrolyze.backends.pyside6.generated_library.PySide6UiLibrary` ``CQ*`` /
:class:`~pyrolyze.backends.tkinter.generated_library.TkinterUiLibrary` ``CTtk*``: each
``call_native`` emits a :class:`~pyrolyze.api.UIElement` whose ``kind`` matches
:class:`~pyrolyze.backends.dearpygui.generated_library.DearPyGuiUiLibrary.WIDGET_SPECS``.

Decorator and helper imports use public names (no ``__pyr_*`` aliases) so Python does not
apply class-body name mangling to them.
"""

from __future__ import annotations

from typing import Any, ClassVar

from frozendict import frozendict

from pyrolyze.api import (
    CallFromNonPyrolyzeContext,
    ComponentMetadata,
    UIElement,
    pyrolyze_component_ref,
)
from pyrolyze.backends.model import UiInterface, UiInterfaceEntry


class DearPyGuiPyrolyzeUiLibrary:
    """Small ``CDpg*`` surface for examples; extend as needed."""

    UI_INTERFACE: ClassVar[UiInterface] = UiInterface(
        name="DearPyGuiPyrolyzeUiLibrary",
        owner=None,
        entries=frozendict(
            {
                "CDpgWindow": UiInterfaceEntry(public_name="CDpgWindow", kind="DpgWindow"),
                "CDpgGroup": UiInterfaceEntry(public_name="CDpgGroup", kind="DpgGroup"),
                "CDpgText": UiInterfaceEntry(public_name="CDpgText", kind="DpgText"),
                "CDpgButton": UiInterfaceEntry(public_name="CDpgButton", kind="DpgButton"),
                "CDpgInputText": UiInterfaceEntry(public_name="CDpgInputText", kind="DpgInputText"),
            }
        ),
    )

    @classmethod
    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
        return UIElement(kind=kind, props=dict(kwds))

    def __pyr_DearPyGuiPyrolyzeUiLibrary__CDpgWindow(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        del __pyr_dirty_state
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(
                cls.__element,
                kind="DpgWindow",
                kwds=kwds,
                __pyr_call_site_id=1,
            )

    @classmethod
    @pyrolyze_component_ref(
        ComponentMetadata(
            "DearPyGuiPyrolyzeUiLibrary.CDpgWindow",
            __pyr_DearPyGuiPyrolyzeUiLibrary__CDpgWindow,
            packed_kwargs=True,
            packed_kwarg_param_names=("label", "width", "height", "no_resize"),
        )
    )
    def CDpgWindow(
        cls,
        *,
        label: str | None = None,
        width: int = 0,
        height: int = 0,
        no_resize: bool = False,
    ) -> None:
        raise CallFromNonPyrolyzeContext("DearPyGuiPyrolyzeUiLibrary.CDpgWindow")

    def __pyr_DearPyGuiPyrolyzeUiLibrary__CDpgGroup(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        del __pyr_dirty_state
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(
                cls.__element,
                kind="DpgGroup",
                kwds=kwds,
                __pyr_call_site_id=2,
            )

    @classmethod
    @pyrolyze_component_ref(
        ComponentMetadata(
            "DearPyGuiPyrolyzeUiLibrary.CDpgGroup",
            __pyr_DearPyGuiPyrolyzeUiLibrary__CDpgGroup,
            packed_kwargs=True,
            packed_kwarg_param_names=("horizontal", "label"),
        )
    )
    def CDpgGroup(cls, *, horizontal: bool = False, label: str | None = None) -> None:
        raise CallFromNonPyrolyzeContext("DearPyGuiPyrolyzeUiLibrary.CDpgGroup")

    def __pyr_DearPyGuiPyrolyzeUiLibrary__CDpgText(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        del __pyr_dirty_state
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(
                cls.__element,
                kind="DpgText",
                kwds=kwds,
                __pyr_call_site_id=3,
            )

    @classmethod
    @pyrolyze_component_ref(
        ComponentMetadata(
            "DearPyGuiPyrolyzeUiLibrary.CDpgText",
            __pyr_DearPyGuiPyrolyzeUiLibrary__CDpgText,
            packed_kwargs=True,
            packed_kwarg_param_names=("default_value", "wrap"),
        )
    )
    def CDpgText(cls, *, default_value: str = "", wrap: int = 0) -> None:
        raise CallFromNonPyrolyzeContext("DearPyGuiPyrolyzeUiLibrary.CDpgText")

    def __pyr_DearPyGuiPyrolyzeUiLibrary__CDpgButton(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        del __pyr_dirty_state
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(
                cls.__element,
                kind="DpgButton",
                kwds=kwds,
                __pyr_call_site_id=4,
            )

    @classmethod
    @pyrolyze_component_ref(
        ComponentMetadata(
            "DearPyGuiPyrolyzeUiLibrary.CDpgButton",
            __pyr_DearPyGuiPyrolyzeUiLibrary__CDpgButton,
            packed_kwargs=True,
            packed_kwarg_param_names=("label", "width", "on_press"),
        )
    )
    def CDpgButton(
        cls,
        *,
        label: str | None = None,
        width: int = 0,
        on_press: Any | None = None,
    ) -> None:
        raise CallFromNonPyrolyzeContext("DearPyGuiPyrolyzeUiLibrary.CDpgButton")

    def __pyr_DearPyGuiPyrolyzeUiLibrary__CDpgInputText(cls, __pyr_ctx, __pyr_dirty_state, **kwds):
        del __pyr_dirty_state
        with __pyr_ctx.pass_scope():
            __pyr_ctx.call_native(
                cls.__element,
                kind="DpgInputText",
                kwds=kwds,
                __pyr_call_site_id=5,
            )

    @classmethod
    @pyrolyze_component_ref(
        ComponentMetadata(
            "DearPyGuiPyrolyzeUiLibrary.CDpgInputText",
            __pyr_DearPyGuiPyrolyzeUiLibrary__CDpgInputText,
            packed_kwargs=True,
            packed_kwarg_param_names=("label", "value", "width", "on_change"),
        )
    )
    def CDpgInputText(
        cls,
        *,
        label: str | None = None,
        value: str = "",
        width: int = 0,
        on_change: Any | None = None,
    ) -> None:
        raise CallFromNonPyrolyzeContext("DearPyGuiPyrolyzeUiLibrary.CDpgInputText")


__all__ = ["DearPyGuiPyrolyzeUiLibrary"]
