"""DearPyGui-backed mountable engine (host context, events, tag-stable creation).

Use :class:`~pyrolyze.backends.dearpygui.host.RecordingDpgHost` for unit tests and
:class:`~pyrolyze.backends.dearpygui.live_host.LiveDpgHost` for a real viewport.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

from pyrolyze.api import MISSING, UIElement
from pyrolyze.backends.dearpygui.host import (
    DpgRuntimeHost,
    dpg_host_reset,
    dpg_host_token,
    dpg_slot_reset,
    dpg_slot_token,
)
from pyrolyze.backends.model import AccessorKind, UiEventSpec, UiWidgetSpec
from pyrolyze.backends.mountable_engine import (
    MountableEngine,
    MountedMountableNode,
    MountableNodeKey,
)


def connect_dpg_event_signal(
    mountable: object,
    event_spec: UiEventSpec,
    dispatcher: Callable[..., None],
) -> None:
    """Install a stable dispatcher via ``configure_item(..., <signal>=dispatcher)``."""

    host = getattr(mountable, "host", None)
    tag = getattr(mountable, "tag", None)
    if host is None or tag is None:
        msg = "DearPyGui mountable must expose host and tag for event wiring"
        raise TypeError(msg)
    host.configure_item(tag, **{event_spec.signal_name: dispatcher})


class DpgMountableEngine(MountableEngine):
    """`MountableEngine` with an active `DpgRuntimeHost` and per-node slot id for tag stability."""

    def __init__(
        self,
        mountable_specs: Mapping[str, UiWidgetSpec],
        host: DpgRuntimeHost,
    ) -> None:
        self._dpg_host = host
        super().__init__(
            mountable_specs,
            read_current_prop_value=self._read_dpg_prop,
            connect_event_signal=connect_dpg_event_signal,
            dispose_mountable=_dispose_dpg_item,
        )

    def mount(
        self,
        element: UIElement,
        *,
        slot_id: Any | None = None,
        call_site_id: int | str | None = None,
    ) -> MountedMountableNode:
        tok = dpg_host_token(self._dpg_host)
        try:
            return super().mount(element, slot_id=slot_id, call_site_id=call_site_id)
        finally:
            dpg_host_reset(tok)

    def update(
        self,
        node: MountedMountableNode,
        element: UIElement,
        *,
        slot_id: Any | None = None,
        call_site_id: int | str | None = None,
    ) -> MountedMountableNode:
        tok = dpg_host_token(self._dpg_host)
        try:
            return super().update(node, element, slot_id=slot_id, call_site_id=call_site_id)
        finally:
            dpg_host_reset(tok)

    def _mount_node(
        self,
        *,
        element: UIElement,
        spec: UiWidgetSpec,
        effective_props: Mapping[str, Any],
        key: MountableNodeKey,
    ) -> MountedMountableNode:
        tok = dpg_slot_token(key.slot_id)
        try:
            return super()._mount_node(
                element=element,
                spec=spec,
                effective_props=effective_props,
                key=key,
            )
        finally:
            dpg_slot_reset(tok)

    def _read_dpg_prop(
        self,
        mountable: object,
        spec: UiWidgetSpec,
        prop_name: str,
    ) -> Any:
        prop = spec.props.get(prop_name)
        if prop is None or prop.getter_kind is None:
            return MISSING
        host = getattr(mountable, "host", None)
        tag = getattr(mountable, "tag", None)
        if host is None or tag is None:
            return MISSING
        if prop.getter_kind is AccessorKind.DPG_CONFIG:
            return host.get_config_value(tag, prop.getter_name or prop.name)
        if prop.getter_kind is AccessorKind.DPG_VALUE:
            return host.get_item_value(tag)
        return MISSING


def _dispose_dpg_item(mountable: object) -> None:
    dispose = getattr(mountable, "dispose", None)
    if callable(dispose):
        dispose()


__all__ = ["DpgMountableEngine", "connect_dpg_event_signal"]
