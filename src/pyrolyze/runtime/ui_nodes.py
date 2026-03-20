from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Mapping, Protocol, Sequence

from pyrolyze.api import UIElement
from pyrolyze.runtime.context import SlotId
from pyrolyze.runtime.trace import TraceChannel, emit_trace, trace_enabled


NodeRole = Literal["leaf", "container", "input", "root"]
ChildPolicy = Literal["none", "ordered", "single"]
BackendId = Literal["pyside6", "tkinter"]
UiPropDiffMode = Literal["equality", "identity", "always_dirty"]


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
    diff_mode: UiPropDiffMode = "equality"


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


class UiNodeBinding(Protocol):
    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None: ...

    def place_child(self, child: "UiNode", index: int) -> None: ...
    def detach_child(self, child: "UiNode") -> None: ...
    def dispose(self) -> None: ...


class UiBackendAdapter(Protocol):
    backend_id: str

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding: ...
    def can_reuse(self, current: "UiNode", next_spec: UiNodeSpec) -> bool: ...
    def assert_ui_thread(self) -> None: ...
    def post_to_ui(self, callback: Callable[[], None]) -> None: ...


@dataclass(eq=False, slots=True)
class UiNode:
    spec: UiNodeSpec
    binding: UiNodeBinding
    children: list["UiNode"] = field(default_factory=list)


@dataclass(slots=True)
class UiOwnerCommitState:
    owner_id: Any
    mounted_nodes: list[UiNode] = field(default_factory=list)
    nodes_by_id: dict[UiNodeId, UiNode] = field(default_factory=dict)
    last_specs: tuple[UiNodeSpec, ...] = ()


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
                UiPropSpec("tone", default="default"),
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
        "select_field": _descriptor(
            kind="select_field",
            role="input",
            child_policy="none",
            props=(
                UiPropSpec("field_id", required=True, affects_identity=True),
                UiPropSpec("label", required=True),
                UiPropSpec("value", required=True),
                UiPropSpec("options", required=True),
                UiPropSpec("enabled", default=True),
                UiPropSpec("visible", default=True),
            ),
            events=(UiEventSpec("on_change", payload_shape="value"),),
        ),
    }
)


def normalize_ui_elements(
    owner_slot_id: SlotId,
    elements: Sequence[UIElement],
    *,
    registry: UiNodeDescriptorRegistry | None = None,
) -> tuple[UiNodeSpec, ...]:
    return normalize_ui_inputs(owner_slot_id, elements, registry=registry)


def normalize_ui_inputs(
    owner_slot_id: SlotId,
    elements: Sequence[UIElement | Mapping[str, Any]],
    *,
    registry: UiNodeDescriptorRegistry | None = None,
) -> tuple[UiNodeSpec, ...]:
    normalized_registry = registry or FROZEN_V1_REGISTRY
    next_region_index = 0

    def normalize_element(element: UIElement | Mapping[str, Any]) -> UiNodeSpec:
        nonlocal next_region_index

        if isinstance(element, UIElement):
            kind = element.kind
            raw_props = dict(element.props)
            raw_children: Sequence[UIElement | Mapping[str, Any]] = element.children
            node_id = _ui_element_node_id(
                owner_slot_id=owner_slot_id,
                element=element,
                fallback_region_index=next_region_index,
            )
            next_region_index += 1
        elif isinstance(element, Mapping):
            kind = str(element.get("kind", ""))
            raw_props = dict(element.get("props", {}) or element.get("values", {}) or {})
            raw_children = tuple(element.get("children", ()))
            if kind == "row" and "row_id" in element and "row_id" not in raw_props:
                raw_props["row_id"] = element["row_id"]
            if kind in {"text_field", "toggle", "select_field"}:
                if "field_id" in element and "field_id" not in raw_props:
                    raw_props["field_id"] = element["field_id"]
            node_id = _mapping_node_id(
                owner_slot_id=owner_slot_id,
                mapping=element,
                fallback_region_index=next_region_index,
            )
            if "slot_id" not in element:
                next_region_index += 1
        else:
            raise TypeError(f"expected UIElement or mapping, got {type(element).__name__}")

        descriptor = normalized_registry.descriptor_for(kind)
        value_props: dict[str, Any] = {}
        event_props: dict[str, Callable[..., None] | None] = {}

        for key, value in raw_props.items():
            if key in descriptor.events:
                if value is not None and not callable(value):
                    raise ValueError(
                        f"event prop {key!r} for kind {kind!r} must be callable or None"
                    )
                event_props[key] = value
                continue

            prop_spec = descriptor.props.get(key)
            if prop_spec is None:
                raise ValueError(f"unsupported prop {key!r} for kind {kind!r}")
            value_props[key] = value

        for name, prop_spec in descriptor.props.items():
            if name in value_props:
                continue
            if prop_spec.default is not _MISSING:
                value_props[name] = prop_spec.default
                continue
            if prop_spec.required:
                raise ValueError(f"missing required prop {name!r} for kind {kind!r}")

        for name in descriptor.events:
            event_props.setdefault(name, None)

        children = tuple(normalize_element(child) for child in raw_children)
        return UiNodeSpec(
            node_id=node_id,
            kind=descriptor.kind,
            props=value_props,
            event_props=event_props,
            children=children,
        )

    return tuple(normalize_element(element) for element in elements)


def _mapping_node_id(
    *,
    owner_slot_id: SlotId,
    mapping: Mapping[str, Any],
    fallback_region_index: int,
) -> UiNodeId:
    raw_slot_id = mapping.get("slot_id")
    if raw_slot_id is None:
        return UiNodeId(owner_slot_id=owner_slot_id, region_index=fallback_region_index)

    raw_index = getattr(raw_slot_id, "index", fallback_region_index)
    try:
        region_index = int(raw_index)
    except (TypeError, ValueError):
        region_index = fallback_region_index

    key_parts: list[Any] = [
        "slot",
        getattr(raw_slot_id, "owner", ""),
        getattr(raw_slot_id, "slot_kind", ""),
        raw_index,
    ]
    call_site_id = mapping.get("call_site_id")
    if call_site_id is not None:
        key_parts.extend(("call_site", str(call_site_id)))
    field_id = mapping.get("field_id")
    if field_id is not None:
        key_parts.extend(("field_id", str(field_id)))

    return UiNodeId(
        owner_slot_id=owner_slot_id,
        region_index=region_index,
        key_path=tuple(key_parts),
    )


def _ui_element_node_id(
    *,
    owner_slot_id: SlotId,
    element: UIElement,
    fallback_region_index: int,
) -> UiNodeId:
    region_index = fallback_region_index
    key_parts: list[Any] = []

    call_site_id = element.call_site_id
    if call_site_id is not None:
        region_index = _coerce_call_site_region_index(call_site_id, fallback=fallback_region_index)
        key_parts.extend(("call_site", str(call_site_id)))

    raw_slot_id = element.slot_id
    if raw_slot_id is not None:
        key_parts.extend(_slot_identity_key_parts(raw_slot_id))

    return UiNodeId(
        owner_slot_id=owner_slot_id,
        region_index=region_index,
        key_path=tuple(key_parts),
    )


def _slot_identity_key_parts(slot_identity: object) -> tuple[Any, ...]:
    if isinstance(slot_identity, SlotId):
        return (
            "slot",
            slot_identity.module_id.canonical_name,
            slot_identity.slot_index,
            slot_identity.key_path,
        )
    if isinstance(slot_identity, tuple):
        normalized_path: list[Any] = []
        for item in slot_identity:
            if isinstance(item, SlotId):
                normalized_path.append(
                    (
                        item.module_id.canonical_name,
                        item.slot_index,
                        item.key_path,
                    )
                )
            else:
                normalized_path.append(str(item))
        return ("slot_path", tuple(normalized_path))
    return ("slot", str(slot_identity))


def _coerce_call_site_region_index(value: int | str, *, fallback: int) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return fallback
    return fallback


def prop_values_equal(spec: UiPropSpec, previous: Any, current: Any) -> bool:
    if spec.diff_mode == "always_dirty":
        return False
    if spec.diff_mode == "identity":
        return previous is current
    if previous is current:
        return True
    return previous == current


def event_values_equal(
    previous: Callable[..., None] | None,
    current: Callable[..., None] | None,
) -> bool:
    return previous is current


def changed_props(
    previous: UiNodeSpec,
    current: UiNodeSpec,
    *,
    descriptor: UiNodeDescriptor,
) -> dict[str, Any]:
    changed: dict[str, Any] = {}
    for name, spec in descriptor.props.items():
        previous_value = previous.props[name]
        current_value = current.props[name]
        if not prop_values_equal(spec, previous_value, current_value):
            changed[name] = current_value
    return changed


def changed_events(
    previous: UiNodeSpec,
    current: UiNodeSpec,
    *,
    descriptor: UiNodeDescriptor,
) -> dict[str, Callable[..., None] | None]:
    changed: dict[str, Callable[..., None] | None] = {}
    for name in descriptor.events:
        previous_value = previous.event_props[name]
        current_value = current.event_props[name]
        if not event_values_equal(previous_value, current_value):
            changed[name] = current_value
    return changed


def mount_subtree(
    spec: UiNodeSpec,
    *,
    backend: UiBackendAdapter,
    parent_binding: UiNodeBinding | None = None,
    registry: UiNodeDescriptorRegistry | None = None,
) -> UiNode:
    _ = (registry or FROZEN_V1_REGISTRY).descriptor_for(spec.kind)
    binding = backend.create_binding(spec, parent_binding=parent_binding)
    node = UiNode(spec=spec, binding=binding)
    for index, child_spec in enumerate(spec.children):
        child = mount_subtree(
            child_spec,
            backend=backend,
            parent_binding=binding,
            registry=registry,
        )
        binding.place_child(child, index)
        node.children.append(child)
    return node


def dispose_subtree(node: UiNode) -> None:
    for child in reversed(tuple(node.children)):
        dispose_subtree(child)
    node.children.clear()
    node.binding.dispose()


def clear_owner_region(
    owner: UiOwnerCommitState,
    *,
    parent_binding: UiNodeBinding | None,
) -> None:
    for node in reversed(tuple(owner.mounted_nodes)):
        if parent_binding is not None:
            parent_binding.detach_child(node)
        dispose_subtree(node)
    owner.mounted_nodes.clear()
    owner.nodes_by_id.clear()


def remount_owner_region(
    owner: UiOwnerCommitState,
    specs: tuple[UiNodeSpec, ...],
    *,
    backend: UiBackendAdapter,
    parent_binding: UiNodeBinding | None,
    registry: UiNodeDescriptorRegistry | None = None,
) -> None:
    next_nodes: list[UiNode] = []
    for index, spec in enumerate(specs):
        node = mount_subtree(
            spec,
            backend=backend,
            parent_binding=parent_binding,
            registry=registry,
        )
        if parent_binding is not None:
            parent_binding.place_child(node, index)
        next_nodes.append(node)
    owner.mounted_nodes = next_nodes
    owner.nodes_by_id = {node.spec.node_id: node for node in next_nodes}
    owner.last_specs = specs


def reconcile_children(
    node: UiNode,
    next_children: tuple[UiNodeSpec, ...],
    *,
    backend: UiBackendAdapter,
    registry: UiNodeDescriptorRegistry | None = None,
) -> None:
    child_owner = UiOwnerCommitState(
        owner_id=node.spec.node_id,
        mounted_nodes=list(node.children),
        nodes_by_id={child.spec.node_id: child for child in node.children},
        last_specs=tuple(child.spec for child in node.children),
    )
    reconcile_owner(
        child_owner,
        next_children,
        backend=backend,
        parent_binding=node.binding,
        registry=registry,
    )
    node.children = child_owner.mounted_nodes


def reconcile_owner(
    owner: UiOwnerCommitState,
    next_specs: tuple[UiNodeSpec, ...],
    *,
    backend: UiBackendAdapter,
    parent_binding: UiNodeBinding | None,
    registry: UiNodeDescriptorRegistry | None = None,
) -> None:
    normalized_registry = registry or FROZEN_V1_REGISTRY
    backend.assert_ui_thread()

    previous_specs = owner.last_specs
    previous_by_id = owner.nodes_by_id
    next_nodes: list[UiNode] = []
    seen_ids: set[UiNodeId] = set()
    replaced_nodes: list[UiNode] = []
    trace_reconcile = trace_enabled(TraceChannel.RECONCILE)
    created_count = 0
    reused_count = 0
    updated_count = 0
    replaced_count = 0

    for spec in next_specs:
        if spec.node_id in seen_ids:
            raise ValueError(f"duplicate UiNodeId encountered during reconciliation: {spec.node_id!r}")
        descriptor = normalized_registry.descriptor_for(spec.kind)
        current = previous_by_id.get(spec.node_id)

        if current is None:
            node = mount_subtree(
                spec,
                backend=backend,
                parent_binding=parent_binding,
                registry=normalized_registry,
            )
            created_count += 1
        elif _can_reuse_node(current, spec, descriptor=descriptor, backend=backend, registry=normalized_registry):
            prop_delta = changed_props(current.spec, spec, descriptor=descriptor)
            event_delta = changed_events(current.spec, spec, descriptor=descriptor)
            if prop_delta or event_delta:
                current.binding.update_props(
                    spec,
                    changed_props=prop_delta,
                    changed_events=event_delta,
                )
                updated_count += 1
            reconcile_children(
                current,
                spec.children,
                backend=backend,
                registry=normalized_registry,
            )
            current.spec = spec
            node = current
            reused_count += 1
        else:
            node = mount_subtree(
                spec,
                backend=backend,
                parent_binding=parent_binding,
                registry=normalized_registry,
            )
            replaced_nodes.append(current)
            replaced_count += 1

        next_nodes.append(node)
        seen_ids.add(spec.node_id)

    to_detach: list[UiNode] = []
    for old in owner.mounted_nodes:
        if old.spec.node_id not in seen_ids or any(old is replaced for replaced in replaced_nodes):
            to_detach.append(old)

    try:
        for old in reversed(to_detach):
            if parent_binding is not None:
                parent_binding.detach_child(old)

        for index, node in enumerate(next_nodes):
            if parent_binding is not None:
                parent_binding.place_child(node, index)

        for old in to_detach:
            dispose_subtree(old)

        owner.mounted_nodes = next_nodes
        owner.nodes_by_id = {node.spec.node_id: node for node in next_nodes}
        owner.last_specs = next_specs
        if trace_reconcile:
            emit_trace(
                TraceChannel.RECONCILE,
                "owner_commit",
                owner_id=owner.owner_id,
                previous_count=len(previous_specs),
                next_count=len(next_specs),
                created=created_count,
                reused=reused_count,
                updated=updated_count,
                replaced=replaced_count,
                removed=len(to_detach),
            )
    except Exception:
        recovery_nodes = _unique_nodes((*next_nodes, *to_detach))
        owner.mounted_nodes = list(recovery_nodes)
        owner.nodes_by_id.clear()
        clear_owner_region(owner, parent_binding=parent_binding)
        remount_owner_region(
            owner,
            previous_specs,
            backend=backend,
            parent_binding=parent_binding,
            registry=normalized_registry,
        )
        if trace_reconcile:
            emit_trace(
                TraceChannel.RECONCILE,
                "owner_recover",
                owner_id=owner.owner_id,
                previous_count=len(previous_specs),
                next_count=len(next_specs),
            )
        raise


def _can_reuse_node(
    current: UiNode,
    next_spec: UiNodeSpec,
    *,
    descriptor: UiNodeDescriptor,
    backend: UiBackendAdapter,
    registry: UiNodeDescriptorRegistry,
) -> bool:
    if current.spec.node_id != next_spec.node_id:
        return False
    if current.spec.kind != next_spec.kind:
        return False

    current_descriptor = registry.descriptor_for(current.spec.kind)
    if current_descriptor.child_policy != descriptor.child_policy:
        return False

    for name, prop_spec in descriptor.props.items():
        if not prop_spec.affects_identity:
            continue
        if current.spec.props[name] != next_spec.props[name]:
            return False

    return backend.can_reuse(current, next_spec)


def _unique_nodes(nodes: Sequence[UiNode]) -> tuple[UiNode, ...]:
    seen: set[int] = set()
    unique: list[UiNode] = []
    for node in nodes:
        marker = id(node)
        if marker in seen:
            continue
        seen.add(marker)
        unique.append(node)
    return tuple(unique)


__all__ = [
    "BackendId",
    "ChildPolicy",
    "FROZEN_V1_REGISTRY",
    "NodeRole",
    "UiBackendAdapter",
    "UiEventSpec",
    "UiNode",
    "UiNodeBinding",
    "UiNodeDescriptor",
    "UiNodeDescriptorRegistry",
    "UiNodeId",
    "UiOwnerCommitState",
    "UiPropDiffMode",
    "UiNodeSpec",
    "UiPropSpec",
    "changed_events",
    "changed_props",
    "clear_owner_region",
    "dispose_subtree",
    "event_values_equal",
    "mount_subtree",
    "normalize_ui_elements",
    "normalize_ui_inputs",
    "prop_values_equal",
    "reconcile_children",
    "reconcile_owner",
    "remount_owner_region",
]
