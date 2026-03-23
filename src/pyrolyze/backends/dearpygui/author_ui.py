"""Author-facing :class:`~pyrolyze.api.UIElement` emitters for DearPyGui (``DearPyGuiUiLibrary.C``).

Mirrors the role of generated ``CQ*`` helpers for PySide6: call ``C.Window(...)`` instead of
hand-assembling ``UIElement(kind=\"DpgWindow\", ...)``. Only common widgets are covered; extend
this module as examples need more kinds.

For :class:`DearPyGuiUiLibrary` tables, child kinds ``DpgTableColumn`` / ``DpgTableRow`` are routed
to the correct mount points; DearPyGui still expects a sensible creation order. Use
:meth:`DearPyGuiC.TableOrdered` when you want a **typed workflow** that only allows ``.rows(...)``
after ``.columns(...)`` so column nodes always precede row nodes in the emitted ``children`` tuple.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pyrolyze.api import UIElement


@dataclass(slots=True)
class DearPyGuiTableColumnPhase:
    """First step of :meth:`DearPyGuiC.TableOrdered`; there is no ``rows`` method here."""

    _slot_id: str | None = None
    _props: dict[str, Any] = field(default_factory=dict)

    def columns(self, *cols: UIElement) -> DearPyGuiTableRowPhase:
        return DearPyGuiTableRowPhase(_slot_id=self._slot_id, _props=self._props, _columns=cols)


@dataclass(slots=True)
class DearPyGuiTableRowPhase:
    """Second step: call ``rows`` to finish the table (columns are fixed for this instance)."""

    _slot_id: str | None = None
    _props: dict[str, Any] = field(default_factory=dict)
    _columns: tuple[UIElement, ...] = ()

    def rows(self, *rows: UIElement) -> UIElement:
        return UIElement(
            kind="DpgTable",
            props=dict(self._props),
            children=self._columns + rows,
            slot_id=self._slot_id,
        )


class DearPyGuiC:
    """Static emitters; exposed as ``DearPyGuiUiLibrary.C`` after this module is imported."""

    @staticmethod
    def Window(
        *,
        slot_id: str | None = None,
        children: tuple[UIElement, ...] = (),
        label: str | None = None,
        width: int = 0,
        height: int = 0,
        **props: Any,
    ) -> UIElement:
        p = dict(props)
        if label is not None:
            p["label"] = label
        if width:
            p["width"] = width
        if height:
            p["height"] = height
        return UIElement(kind="DpgWindow", props=p, children=children, slot_id=slot_id)

    @staticmethod
    def MenuBar(
        *,
        slot_id: str | None = None,
        children: tuple[UIElement, ...] = (),
        **props: Any,
    ) -> UIElement:
        return UIElement(kind="DpgMenuBar", props=dict(props), children=children, slot_id=slot_id)

    @staticmethod
    def Menu(
        *,
        slot_id: str | None = None,
        children: tuple[UIElement, ...] = (),
        label: str | None = None,
        **props: Any,
    ) -> UIElement:
        p = dict(props)
        if label is not None:
            p["label"] = label
        return UIElement(kind="DpgMenu", props=p, children=children, slot_id=slot_id)

    @staticmethod
    def MenuItem(
        *,
        slot_id: str | None = None,
        children: tuple[UIElement, ...] = (),
        label: str | None = None,
        callback: Any | None = None,
        **props: Any,
    ) -> UIElement:
        p = dict(props)
        if label is not None:
            p["label"] = label
        if callback is not None:
            p["callback"] = callback
        return UIElement(kind="DpgMenuItem", props=p, children=children, slot_id=slot_id)

    @staticmethod
    def Group(
        *,
        slot_id: str | None = None,
        children: tuple[UIElement, ...] = (),
        horizontal: bool = False,
        **props: Any,
    ) -> UIElement:
        p = dict(props)
        if horizontal:
            p["horizontal"] = True
        return UIElement(kind="DpgGroup", props=p, children=children, slot_id=slot_id)

    @staticmethod
    def Text(
        *,
        slot_id: str | None = None,
        children: tuple[UIElement, ...] = (),
        default_value: str = "",
        wrap: int = 0,
        **props: Any,
    ) -> UIElement:
        p = dict(props)
        if default_value != "":
            p["default_value"] = default_value
        if wrap:
            p["wrap"] = wrap
        return UIElement(kind="DpgText", props=p, children=children, slot_id=slot_id)

    @staticmethod
    def InputText(
        *,
        slot_id: str | None = None,
        children: tuple[UIElement, ...] = (),
        label: str | None = None,
        value: str = "",
        on_change: Any | None = None,
        **props: Any,
    ) -> UIElement:
        p = dict(props)
        if label is not None:
            p["label"] = label
        if value != "":
            p["value"] = value
        if on_change is not None:
            p["on_change"] = on_change
        return UIElement(kind="DpgInputText", props=p, children=children, slot_id=slot_id)

    @staticmethod
    def Checkbox(
        *,
        slot_id: str | None = None,
        children: tuple[UIElement, ...] = (),
        label: str | None = None,
        value: bool = False,
        on_change: Any | None = None,
        **props: Any,
    ) -> UIElement:
        p = dict(props)
        if label is not None:
            p["label"] = label
        p["value"] = value
        if on_change is not None:
            p["on_change"] = on_change
        return UIElement(kind="DpgCheckbox", props=p, children=children, slot_id=slot_id)

    @staticmethod
    def Button(
        *,
        slot_id: str | None = None,
        children: tuple[UIElement, ...] = (),
        label: str | None = None,
        on_press: Any | None = None,
        on_drag: Any | None = None,
        on_drop: Any | None = None,
        **props: Any,
    ) -> UIElement:
        p = dict(props)
        if label is not None:
            p["label"] = label
        if on_press is not None:
            p["on_press"] = on_press
        if on_drag is not None:
            p["on_drag"] = on_drag
        if on_drop is not None:
            p["on_drop"] = on_drop
        return UIElement(kind="DpgButton", props=p, children=children, slot_id=slot_id)

    @staticmethod
    def TableOrdered(
        *,
        slot_id: str | None = None,
        **props: Any,
    ) -> DearPyGuiTableColumnPhase:
        """Build a ``DpgTable`` in two steps: ``.columns(...).rows(...)`` (columns always first)."""

        return DearPyGuiTableColumnPhase(_slot_id=slot_id, _props=dict(props))

    @staticmethod
    def Table(
        *,
        slot_id: str | None = None,
        children: tuple[UIElement, ...] = (),
        **props: Any,
    ) -> UIElement:
        return UIElement(kind="DpgTable", props=dict(props), children=children, slot_id=slot_id)

    @staticmethod
    def TableColumn(
        *,
        slot_id: str | None = None,
        children: tuple[UIElement, ...] = (),
        **props: Any,
    ) -> UIElement:
        return UIElement(kind="DpgTableColumn", props=dict(props), children=children, slot_id=slot_id)

    @staticmethod
    def TableRow(
        *,
        slot_id: str | None = None,
        children: tuple[UIElement, ...] = (),
        **props: Any,
    ) -> UIElement:
        return UIElement(kind="DpgTableRow", props=dict(props), children=children, slot_id=slot_id)


def _attach_c_namespace() -> None:
    from pyrolyze.backends.dearpygui.generated_library import DearPyGuiUiLibrary

    DearPyGuiUiLibrary.C = DearPyGuiC  # type: ignore[attr-defined]


_attach_c_namespace()

__all__ = [
    "DearPyGuiC",
    "DearPyGuiTableColumnPhase",
    "DearPyGuiTableRowPhase",
    "_attach_c_namespace",
]
