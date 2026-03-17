from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Mapping, Sequence

from pyrolyze.api import UIElement
from pyrolyze.runtime.context import SlotId


NodeRole = Literal["leaf", "container", "input", "root"]
ChildPolicy = Literal["none", "ordered", "single"]
BackendId = Literal["pyside6", "tkinter"]


_MISSING = object()


@dataclass(frozen=True, slots=True)
class UiNodeId:
    owner_slot_id: SlotId
    region_index: int
    key_path: tuple[Any, ...] = ()


@dataclass(frozen=True, slots=True)
class UiPropSpec:
    name: str
    required: bool = False
    dynamic: bool = True
    affects_identity: bool = False
    default: object = _MISSING


@dataclass(frozen=True, slots=True)
class UiEventSpec:
    name: str
    payload_shape: Literal["none", "text", "bool", "value"] = "none"


@dataclass(frozen=True, slots=True)
class UiNodeDescriptor:
    kind: str
    role: NodeRole
    child_policy: ChildPolicy
    props: Mapping[str, UiPropSpec]
    events: Mapping[str, UiEventSpec]


@dataclass(frozen=True, slots=True)
class UiNodeSpec:
    node_id: UiNodeId
    kind: str
    props: Mapping[str, Any]
    event_props: Mapping[str, Callable[..., None] | None] = field(default_factory=dict)
    children: tuple["UiNodeSpec", ...] = ()


@dataclass(slots=True)
class UiNode:
    spec: UiNodeSpec
    binding: Any
    children: list["UiNode"] = field(default_factory=list)


@dataclass(slots=True)
class UiNodeDescriptorRegistry:
    descriptors: dict[str, UiNodeDescriptor] = field(default_factory=dict)

    def descriptor_for(self, kind: str) -> UiNodeDescriptor:
        descriptor = self.descriptors.get(kind)
        if descriptor is None:
            raise ValueError(f"unsupported UIElement kind {kind!r}")
        return descriptor


def _descriptor(
    *,
    kind: str,
    role: NodeRole,
    child_policy: ChildPolicy,
    props: Sequence[UiPropSpec],
    events: Sequence[UiEventSpec] = (),
) -> UiNodeDescriptor:
    return UiNodeDescriptor(
        kind=kind,
        role=role,
        child_policy=child_policy,
        props={prop.name: prop for prop in props},
        events={event.name: event for event in events},
    )


FROZEN_V1_REGISTRY = UiNodeDescriptorRegistry(
    descriptors={
        "section": _descriptor(
            kind="section",
            role="container",
            child_policy="ordered",
            props=(
                UiPropSpec("title", required=True),
                UiPropSpec("accent", default=None),
                UiPropSpec("visible", default=True),
            ),
        ),
        "row": _descriptor(
            kind="row",
            role="container",
            child_policy="ordered",
            props=(
                UiPropSpec("row_id", required=True),
                UiPropSpec("headline", required=True),
                UiPropSpec("visible", default=True),
            ),
        ),
        "badge": _descriptor(
            kind="badge",
            role="leaf",
            child_policy="none",
            props=(
                UiPropSpec("text", required=True),
                UiPropSpec("tone", default=None),
                UiPropSpec("visible", default=True),
            ),
        ),
        "button": _descriptor(
            kind="button",
            role="input",
            child_policy="none",
            props=(
                UiPropSpec("label", required=True),
                UiPropSpec("enabled", default=True),
                UiPropSpec("visible", default=True),
            ),
            events=(UiEventSpec("on_press"),),
        ),
        "text_field": _descriptor(
            kind="text_field",
            role="input",
            child_policy="none",
            props=(
                UiPropSpec("field_id", required=True, affects_identity=True),
                UiPropSpec("label", required=True),
                UiPropSpec("value", required=True),
                UiPropSpec("enabled", default=True),
                UiPropSpec("placeholder", default=None),
                UiPropSpec("visible", default=True),
            ),
            events=(
                UiEventSpec("on_change", payload_shape="text"),
                UiEventSpec("on_submit"),
            ),
        ),
        "toggle": _descriptor(
            kind="toggle",
            role="input",
            child_policy="none",
            props=(
                UiPropSpec("field_id", required=True, affects_identity=True),
                UiPropSpec("label", required=True),
                UiPropSpec("checked", required=True),
                UiPropSpec("enabled", default=True),
                UiPropSpec("visible", default=True),
            ),
            events=(UiEventSpec("on_toggle", payload_shape="bool"),),
        ),
    }
)


def normalize_ui_elements(
    owner_slot_id: SlotId,
    elements: Sequence[UIElement],
    *,
    registry: UiNodeDescriptorRegistry | None = None,
) -> tuple[UiNodeSpec, ...]:
    normalized_registry = registry or FROZEN_V1_REGISTRY
    next_region_index = 0

    def normalize_element(element: UIElement) -> UiNodeSpec:
        nonlocal next_region_index

        descriptor = normalized_registry.descriptor_for(element.kind)
        raw_props = dict(element.props)
        value_props: dict[str, Any] = {}
        event_props: dict[str, Callable[..., None] | None] = {}

        for key, value in raw_props.items():
            if key in descriptor.events:
                if value is not None and not callable(value):
                    raise ValueError(
                        f"event prop {key!r} for kind {element.kind!r} must be callable or None"
                    )
                if value is not None:
                    event_props[key] = value
                continue

            prop_spec = descriptor.props.get(key)
            if prop_spec is None:
                raise ValueError(f"unsupported prop {key!r} for kind {element.kind!r}")
            value_props[key] = value

        for name, prop_spec in descriptor.props.items():
            if name in value_props:
                continue
            if prop_spec.default is not _MISSING:
                value_props[name] = prop_spec.default
                continue
            if prop_spec.required:
                raise ValueError(f"missing required prop {name!r} for kind {element.kind!r}")

        region_index = next_region_index
        next_region_index += 1
        children = tuple(normalize_element(child) for child in element.children)
        return UiNodeSpec(
            node_id=UiNodeId(owner_slot_id=owner_slot_id, region_index=region_index),
            kind=descriptor.kind,
            props=value_props,
            event_props=event_props,
            children=children,
        )

    return tuple(normalize_element(element) for element in elements)


__all__ = [
    "BackendId",
    "ChildPolicy",
    "FROZEN_V1_REGISTRY",
    "NodeRole",
    "UiEventSpec",
    "UiNode",
    "UiNodeDescriptor",
    "UiNodeDescriptorRegistry",
    "UiNodeId",
    "UiNodeSpec",
    "UiPropSpec",
    "normalize_ui_elements",
]
