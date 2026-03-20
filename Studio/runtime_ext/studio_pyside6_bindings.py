from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from pyrolyze.runtime.ui_nodes import UiNode, UiNodeBinding, UiNodeSpec

from Studio.runtime_ext.studio_descriptors import STUDIO_CUSTOM_KINDS


@dataclass(eq=False, slots=True, kw_only=True)
class StudioBindingPlaceholder(UiNodeBinding):
    kind: str
    spec: UiNodeSpec

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Any],
    ) -> None:
        del changed_props, changed_events
        self.spec = next_spec

    def place_child(self, child: UiNode, index: int) -> None:
        del child, index
        raise NotImplementedError(f"Studio custom binding {self.kind!r} is not wired yet")

    def detach_child(self, child: UiNode) -> None:
        del child
        return None

    def dispose(self) -> None:
        return None


def is_studio_custom_kind(kind: str) -> bool:
    return kind in STUDIO_CUSTOM_KINDS


def create_studio_binding_placeholder(spec: UiNodeSpec) -> StudioBindingPlaceholder:
    if not is_studio_custom_kind(spec.kind):
        raise ValueError(f"unsupported Studio custom kind: {spec.kind!r}")
    return StudioBindingPlaceholder(kind=spec.kind, spec=spec)


__all__ = [
    "StudioBindingPlaceholder",
    "create_studio_binding_placeholder",
    "is_studio_custom_kind",
]
