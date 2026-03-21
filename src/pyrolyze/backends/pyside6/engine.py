"""Basic create/update/remount engine for generated PySide6 widget specs."""

from __future__ import annotations

from dataclasses import dataclass, field
import importlib
from typing import Any, Mapping

from PySide6.QtWidgets import QApplication, QLayout, QWidget

from pyrolyze.api import MISSING, UIElement
from pyrolyze.backends.model import AccessorKind, PropMode, UiPropSpec, UiWidgetSpec


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


@dataclass(frozen=True, slots=True)
class _WidgetPlacement:
    parent_widget: QWidget | None
    layout: QLayout | None
    index: int | None


class PySide6WidgetEngine:
    def __init__(self, widget_specs: Mapping[str, UiWidgetSpec]):
        self._widget_specs = widget_specs
        self._widget_types: dict[str, type[QWidget]] = {}

    def mount(
        self,
        element: UIElement,
        *,
        slot_id: Any | None = None,
        call_site_id: int | str | None = None,
    ) -> MountedWidgetNode:
        self._ensure_app()
        spec = self._spec_for(element.kind)
        if element.children:
            raise NotImplementedError("PySide6WidgetEngine child mounting is not implemented yet")
        effective_props = self._initial_effective_props(spec, element)
        widget = self._create_widget(spec, effective_props)
        return MountedWidgetNode(
            key=WidgetNodeKey(
                slot_id=slot_id if slot_id is not None else element.slot_id,
                call_site_id=call_site_id if call_site_id is not None else element.call_site_id,
                kind=element.kind,
            ),
            element=element,
            spec=spec,
            widget=widget,
            effective_props=effective_props,
        )

    def update(
        self,
        node: MountedWidgetNode,
        element: UIElement,
        *,
        slot_id: Any | None = None,
        call_site_id: int | str | None = None,
    ) -> MountedWidgetNode:
        self._ensure_app()
        spec = self._spec_for(element.kind)
        next_key = WidgetNodeKey(
            slot_id=slot_id if slot_id is not None else node.key.slot_id,
            call_site_id=call_site_id if call_site_id is not None else node.key.call_site_id,
            kind=element.kind,
        )
        next_effective = dict(node.effective_props)
        changed_props: dict[str, Any] = {}
        remount_required = spec.kind != node.spec.kind

        for name, value in element.props.items():
            if value is MISSING:
                continue
            prop = self._prop_for(spec, name)
            if prop.mode is PropMode.READONLY:
                raise ValueError(f"readonly prop {name!r} may not be updated")
            if prop.mode is PropMode.CREATE_ONLY:
                continue
            previous = next_effective.get(name, MISSING)
            if previous == value:
                continue
            next_effective[name] = value
            changed_props[name] = value
            if prop.mode is PropMode.CREATE_ONLY_REMOUNT:
                remount_required = True

        if remount_required:
            placement = _capture_widget_placement(node.widget)
            old_widget = node.widget
            node.spec = spec
            node.key = next_key
            node.element = element
            node.effective_props = next_effective
            node.widget = self._create_widget(spec, next_effective)
            _restore_widget_placement(node.widget, placement)
            _dispose_widget(old_widget)
            return node

        self._apply_changed_props(node.widget, spec, changed_props)
        node.spec = spec
        node.key = next_key
        node.element = element
        node.effective_props = next_effective
        return node

    def _ensure_app(self) -> QApplication:
        return QApplication.instance() or QApplication([])

    def _spec_for(self, kind: str) -> UiWidgetSpec:
        spec = self._widget_specs.get(kind)
        if spec is None:
            raise ValueError(f"unsupported widget kind {kind!r}")
        return spec

    def _prop_for(self, spec: UiWidgetSpec, name: str) -> UiPropSpec:
        prop = spec.props.get(name)
        if prop is None:
            raise ValueError(f"unsupported prop {name!r} for widget kind {spec.kind!r}")
        return prop

    def _initial_effective_props(self, spec: UiWidgetSpec, element: UIElement) -> dict[str, Any]:
        effective: dict[str, Any] = {}
        for name, value in element.props.items():
            if value is MISSING:
                continue
            prop = self._prop_for(spec, name)
            if prop.mode is PropMode.READONLY:
                raise ValueError(f"readonly prop {name!r} may not be mounted")
            effective[name] = value
        return effective

    def _create_widget(self, spec: UiWidgetSpec, effective_props: Mapping[str, Any]) -> QWidget:
        widget_type = self._widget_type_for(spec)
        constructor_kwargs: dict[str, Any] = {}
        for name, value in effective_props.items():
            prop = spec.props.get(name)
            if prop is None or prop.constructor_name is None:
                continue
            if prop.mode in {PropMode.CREATE_ONLY, PropMode.CREATE_ONLY_REMOUNT} or prop.setter_kind is None:
                constructor_kwargs[prop.constructor_name] = value
        widget = widget_type(**constructor_kwargs)
        self._apply_mount_props(widget, spec, effective_props)
        return widget

    def _widget_type_for(self, spec: UiWidgetSpec) -> type[QWidget]:
        widget_type = self._widget_types.get(spec.mounted_type_name)
        if widget_type is not None:
            return widget_type
        module_name, _, attr_name = spec.mounted_type_name.rpartition(".")
        module = importlib.import_module(module_name)
        resolved = getattr(module, attr_name)
        if not isinstance(resolved, type) or not issubclass(resolved, QWidget):
            raise TypeError(f"{spec.mounted_type_name!r} is not a QWidget type")
        self._widget_types[spec.mounted_type_name] = resolved
        return resolved

    def _apply_mount_props(
        self,
        widget: QWidget,
        spec: UiWidgetSpec,
        effective_props: Mapping[str, Any],
    ) -> None:
        for name, value in effective_props.items():
            prop = spec.props.get(name)
            if prop is None or prop.setter_kind is None:
                continue
            if prop.mode in {PropMode.CREATE_UPDATE, PropMode.UPDATE_ONLY}:
                self._apply_prop(widget, prop, value)
            elif prop.mode in {PropMode.CREATE_ONLY, PropMode.CREATE_ONLY_REMOUNT} and prop.constructor_name is None:
                self._apply_prop(widget, prop, value)

    def _apply_changed_props(
        self,
        widget: QWidget,
        spec: UiWidgetSpec,
        changed_props: Mapping[str, Any],
    ) -> None:
        for name, value in changed_props.items():
            prop = spec.props.get(name)
            if prop is None or prop.setter_kind is None:
                continue
            if prop.mode not in {PropMode.CREATE_UPDATE, PropMode.UPDATE_ONLY}:
                continue
            self._apply_prop(widget, prop, value)

    def _apply_prop(self, widget: QWidget, prop: UiPropSpec, value: Any) -> None:
        if prop.setter_kind is AccessorKind.QT_PROPERTY:
            widget.setProperty(prop.name, value)
            return
        if prop.setter_kind is AccessorKind.METHOD:
            if prop.setter_name is None:
                raise ValueError(f"missing setter_name for method prop {prop.name!r}")
            getattr(widget, prop.setter_name)(value)
            return
        if prop.setter_kind is AccessorKind.PYTHON_PROPERTY:
            setattr(widget, prop.setter_name or prop.name, value)
            return
        raise NotImplementedError(f"unsupported setter kind {prop.setter_kind!r} for PySide6 backend")


def _capture_widget_placement(widget: QWidget) -> _WidgetPlacement:
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


def _restore_widget_placement(widget: QWidget, placement: _WidgetPlacement) -> None:
    if widget.parentWidget() is not None:
        return
    if placement.layout is not None and placement.index is not None:
        placement.layout.insertWidget(placement.index, widget)
        return
    if placement.parent_widget is not None:
        widget.setParent(placement.parent_widget)


def _dispose_widget(widget: QWidget) -> None:
    widget.hide()
    widget.setParent(None)
    widget.deleteLater()


__all__ = ["MountedWidgetNode", "PySide6WidgetEngine", "WidgetNodeKey"]
