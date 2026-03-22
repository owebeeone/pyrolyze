"""PySide6 adapter over the generic spec-driven mountable engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from PySide6.QtWidgets import QApplication, QLayout, QWidget

from pyrolyze.api import MISSING, UIElement
from pyrolyze.backends.model import AccessorKind, UiEventSpec, UiWidgetSpec
from pyrolyze.backends.mountable_engine import MountableEngine, MountedMountableNode, MountableNodeKey


@dataclass(frozen=True, slots=True)
class WidgetNodeKey:
    slot_id: Any | None
    call_site_id: int | str | None
    kind: str


@dataclass(slots=True)
class MountedWidgetNode:
    key: WidgetNodeKey
    element: UIElement
    spec: UiWidgetSpec
    widget: QWidget
    effective_props: dict[str, Any] = field(default_factory=dict)
    _mountable_node: MountedMountableNode | None = field(default=None, repr=False)


@dataclass(frozen=True, slots=True)
class _WidgetPlacement:
    parent_widget: QWidget | None
    layout: QLayout | None
    index: int | None


class PySide6WidgetEngine:
    def __init__(self, widget_specs: Mapping[str, UiWidgetSpec]):
        self._engine = MountableEngine(
            widget_specs,
            read_current_prop_value=self._read_current_prop_value,
            connect_event_signal=self._connect_event_signal,
            capture_placement=_capture_widget_placement,
            restore_placement=_restore_widget_placement,
            dispose_mountable=_dispose_widget,
        )
        self._widget_types = self._engine._mountable_types

    def mount(
        self,
        element: UIElement,
        *,
        slot_id: Any | None = None,
        call_site_id: int | str | None = None,
    ) -> MountedWidgetNode:
        self._ensure_app()
        mounted = self._engine.mount(element, slot_id=slot_id, call_site_id=call_site_id)
        return self._to_widget_node(mounted)

    def update(
        self,
        node: MountedWidgetNode,
        element: UIElement,
        *,
        slot_id: Any | None = None,
        call_site_id: int | str | None = None,
    ) -> MountedWidgetNode:
        self._ensure_app()
        if node._mountable_node is None:
            raise ValueError("MountedWidgetNode is missing its underlying mountable node")
        mounted = self._engine.update(
            node._mountable_node,
            element,
            slot_id=slot_id,
            call_site_id=call_site_id,
        )
        self._sync_widget_node(node, mounted)
        return node

    def _ensure_app(self) -> QApplication:
        return QApplication.instance() or QApplication([])

    def _to_widget_node(self, mounted: MountedMountableNode) -> MountedWidgetNode:
        widget = mounted.mountable
        if not isinstance(widget, QWidget):
            raise TypeError(f"{type(widget).__name__} is not a QWidget")
        return MountedWidgetNode(
            key=WidgetNodeKey(
                slot_id=mounted.key.slot_id,
                call_site_id=mounted.key.call_site_id,
                kind=mounted.key.kind,
            ),
            element=mounted.element,
            spec=mounted.spec,
            widget=widget,
            effective_props=dict(mounted.effective_props),
            _mountable_node=mounted,
        )

    def _sync_widget_node(
        self,
        node: MountedWidgetNode,
        mounted: MountedMountableNode,
    ) -> None:
        widget = mounted.mountable
        if not isinstance(widget, QWidget):
            raise TypeError(f"{type(widget).__name__} is not a QWidget")
        node.key = WidgetNodeKey(
            slot_id=mounted.key.slot_id,
            call_site_id=mounted.key.call_site_id,
            kind=mounted.key.kind,
        )
        node.element = mounted.element
        node.spec = mounted.spec
        node.widget = widget
        node.effective_props = dict(mounted.effective_props)
        node._mountable_node = mounted

    def _read_current_prop_value(
        self,
        mountable: object,
        spec: UiWidgetSpec,
        prop_name: str,
    ) -> Any:
        if not isinstance(mountable, QWidget):
            return MISSING
        prop = spec.props.get(prop_name)
        if prop is None or prop.getter_kind is None:
            return MISSING
        if prop.getter_kind is AccessorKind.QT_PROPERTY:
            return mountable.property(prop.name)
        if prop.getter_kind is AccessorKind.PYTHON_PROPERTY:
            return getattr(mountable, prop.getter_name or prop.name, MISSING)
        if prop.getter_kind is AccessorKind.METHOD:
            if prop.getter_name is None:
                return MISSING
            return getattr(mountable, prop.getter_name)()
        return MISSING

    def _connect_event_signal(
        self,
        mountable: object,
        event_spec: UiEventSpec,
        callback: Callable[..., None],
    ) -> None:
        signal = getattr(mountable, event_spec.signal_name, None)
        if signal is None or not hasattr(signal, "connect"):
            raise AttributeError(
                f"{type(mountable).__name__} has no connectable signal {event_spec.signal_name!r}"
            )
        signal.connect(callback)


def _capture_widget_placement(widget: object) -> _WidgetPlacement:
    if not isinstance(widget, QWidget):
        return _WidgetPlacement(parent_widget=None, layout=None, index=None)
    parent_widget = widget.parentWidget()
    if parent_widget is None:
        return _WidgetPlacement(parent_widget=None, layout=None, index=None)
    layout = parent_widget.layout()
    if layout is None:
        return _WidgetPlacement(parent_widget=parent_widget, layout=None, index=None)
    for index in range(layout.count()):
        item = layout.itemAt(index)
        if item is not None and item.widget() is widget:
            return _WidgetPlacement(parent_widget=parent_widget, layout=layout, index=index)
    return _WidgetPlacement(parent_widget=parent_widget, layout=None, index=None)


def _restore_widget_placement(widget: object, placement: object | None) -> None:
    if not isinstance(widget, QWidget):
        return
    if not isinstance(placement, _WidgetPlacement):
        return
    if widget.parentWidget() is not None:
        return
    if placement.layout is not None and placement.index is not None:
        placement.layout.insertWidget(placement.index, widget)
        return
    if placement.parent_widget is not None:
        widget.setParent(placement.parent_widget)


def _dispose_widget(widget: object) -> None:
    if not isinstance(widget, QWidget):
        return
    widget.hide()
    widget.setParent(None)
    widget.deleteLater()


__all__ = ["MountedWidgetNode", "PySide6WidgetEngine", "WidgetNodeKey"]
