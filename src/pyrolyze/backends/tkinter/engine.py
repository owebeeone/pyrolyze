"""tkinter adapter over the generic spec-driven mountable engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

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
    widget: Any
    effective_props: dict[str, Any] = field(default_factory=dict)
    _mountable_node: MountedMountableNode | None = field(default=None, repr=False)


class TkinterWidgetEngine:
    def __init__(self, widget_specs: Mapping[str, UiWidgetSpec]):
        self._engine = MountableEngine(
            widget_specs,
            read_current_prop_value=self._read_current_prop_value,
            connect_event_signal=self._connect_event_signal,
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

    def _to_widget_node(self, mounted: MountedMountableNode) -> MountedWidgetNode:
        return MountedWidgetNode(
            key=WidgetNodeKey(
                slot_id=mounted.key.slot_id,
                call_site_id=mounted.key.call_site_id,
                kind=mounted.key.kind,
            ),
            element=mounted.element,
            spec=mounted.spec,
            widget=mounted.mountable,
            effective_props=dict(mounted.effective_props),
            _mountable_node=mounted,
        )

    def _sync_widget_node(
        self,
        node: MountedWidgetNode,
        mounted: MountedMountableNode,
    ) -> None:
        node.key = WidgetNodeKey(
            slot_id=mounted.key.slot_id,
            call_site_id=mounted.key.call_site_id,
            kind=mounted.key.kind,
        )
        node.element = mounted.element
        node.spec = mounted.spec
        node.widget = mounted.mountable
        node.effective_props = dict(mounted.effective_props)
        node._mountable_node = mounted

    def _read_current_prop_value(
        self,
        mountable: object,
        spec: UiWidgetSpec,
        prop_name: str,
    ) -> Any:
        prop = spec.props.get(prop_name)
        if prop is None or prop.getter_kind is None:
            return MISSING
        if prop.getter_kind is AccessorKind.TK_CONFIG:
            getter_name = prop.getter_name or "cget"
            return getattr(mountable, getter_name)(prop.name)
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
        signal_name = event_spec.signal_name
        if signal_name == "command":
            configure = getattr(mountable, "configure", None)
            if not callable(configure):
                raise AttributeError(
                    f"{type(mountable).__name__} has no configure(...) for command event hookup"
                )
            configure(command=callback)
            return
        if signal_name.startswith("bind:"):
            bind = getattr(mountable, "bind", None)
            if not callable(bind):
                raise AttributeError(
                    f"{type(mountable).__name__} has no bind(...) for event hookup"
                )
            bind(signal_name.partition(":")[2], callback)
            return
        raise AttributeError(
            f"{type(mountable).__name__} has no supported tkinter event hookup for {signal_name!r}"
        )


def _dispose_widget(widget: object) -> None:
    destroy = getattr(widget, "destroy", None)
    if callable(destroy):
        destroy()


__all__ = ["MountedWidgetNode", "TkinterWidgetEngine", "WidgetNodeKey"]
