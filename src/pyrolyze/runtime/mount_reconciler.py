from __future__ import annotations

from typing import Any, Sequence

from frozendict import frozendict

from pyrolyze.backends.model import MountPointSpec, MountState, TypeRef
from pyrolyze.backends.mounts import (
    ImmutableOrderedMountState,
    MountedRef,
    OrderedMountStateBuilder,
    apply_mount_state,
)

from .trace import TraceChannel, emit_trace, trace_enabled
from .ui_nodes import (
    FROZEN_V1_REGISTRY,
    UiBackendAdapter,
    UiNode,
    UiNodeBinding,
    UiNodeDescriptor,
    UiNodeDescriptorRegistry,
    UiNodeId,
    UiNodeSpec,
    UiOwnerCommitState,
    changed_events,
    changed_props,
    clear_owner_region,
    dispose_subtree,
)


STANDARD_MOUNT_POINT = MountPointSpec(
    name="standard",
    accepted_produced_type=TypeRef("UiNode"),
)


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
    if spec.children:
        children = [
            mount_subtree(
                child_spec,
                backend=backend,
                parent_binding=binding,
                registry=registry,
            )
            for child_spec in spec.children
        ]
        _apply_standard_mount(
            parent_binding=binding,
            previous_nodes=(),
            next_nodes=tuple(children),
            removed_nodes=(),
        )
        node.children = children
    return node


def remount_owner_region(
    owner: UiOwnerCommitState,
    specs: tuple[UiNodeSpec, ...],
    *,
    backend: UiBackendAdapter,
    parent_binding: UiNodeBinding | None,
    registry: UiNodeDescriptorRegistry | None = None,
) -> None:
    next_nodes = [
        mount_subtree(
            spec,
            backend=backend,
            parent_binding=parent_binding,
            registry=registry,
        )
        for spec in specs
    ]
    if parent_binding is not None:
        _apply_standard_mount(
            parent_binding=parent_binding,
            previous_nodes=(),
            next_nodes=tuple(next_nodes),
            removed_nodes=(),
        )
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
    backend_identity = _backend_identity(backend)

    previous_specs = owner.last_specs
    previous_backend_identity = owner.last_backend_identity
    if previous_backend_identity is not None and previous_backend_identity != backend_identity:
        clear_owner_region(owner, parent_binding=parent_binding)
        try:
            remount_owner_region(
                owner,
                next_specs,
                backend=backend,
                parent_binding=parent_binding,
                registry=normalized_registry,
            )
        except Exception:
            clear_owner_region(owner, parent_binding=parent_binding)
            remount_owner_region(
                owner,
                previous_specs,
                backend=backend,
                parent_binding=parent_binding,
                registry=normalized_registry,
            )
            owner.last_backend_identity = backend_identity
            if trace_enabled(TraceChannel.RECONCILE):
                emit_trace(
                    TraceChannel.RECONCILE,
                    "owner_recover",
                    owner_id=owner.owner_id,
                    previous_count=len(previous_specs),
                    next_count=len(next_specs),
                )
            raise
        owner.last_backend_identity = backend_identity
        if trace_enabled(TraceChannel.RECONCILE):
            emit_trace(
                TraceChannel.RECONCILE,
                "owner_backend_swap",
                owner_id=owner.owner_id,
                previous_backend=previous_backend_identity,
                next_backend=backend_identity,
                previous_count=len(previous_specs),
                next_count=len(next_specs),
            )
        return

    previous_by_id = owner.nodes_by_id
    next_nodes: list[UiNode] = []
    seen_ids: set[UiNodeId] = set()
    replaced_node_ids: set[int] = set()
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
        elif _can_reuse_node(
            current,
            spec,
            descriptor=descriptor,
            backend=backend,
            registry=normalized_registry,
        ):
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
            replaced_node_ids.add(id(current))
            replaced_count += 1

        next_nodes.append(node)
        seen_ids.add(spec.node_id)

    to_detach: list[UiNode] = []
    for old in owner.mounted_nodes:
        if old.spec.node_id not in seen_ids or id(old) in replaced_node_ids:
            to_detach.append(old)

    try:
        _apply_standard_mount(
            parent_binding=parent_binding,
            previous_nodes=tuple(owner.mounted_nodes),
            next_nodes=tuple(next_nodes),
            removed_nodes=tuple(to_detach),
        )

        for old in to_detach:
            dispose_subtree(old)

        owner.mounted_nodes = next_nodes
        owner.nodes_by_id = {node.spec.node_id: node for node in next_nodes}
        owner.last_specs = next_specs
        owner.last_backend_identity = backend_identity
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
        owner.last_backend_identity = backend_identity
        if trace_reconcile:
            emit_trace(
                TraceChannel.RECONCILE,
                "owner_recover",
                owner_id=owner.owner_id,
                previous_count=len(previous_specs),
                next_count=len(next_specs),
            )
        raise


def _apply_standard_mount(
    *,
    parent_binding: UiNodeBinding | None,
    previous_nodes: Sequence[UiNode],
    next_nodes: Sequence[UiNode],
    removed_nodes: Sequence[UiNode],
) -> None:
    if parent_binding is None:
        return
    old_state = _standard_mount_state(previous_nodes)
    ordered_state = _build_standard_mount_delta(
        previous_nodes=previous_nodes,
        next_nodes=next_nodes,
        removed_nodes=removed_nodes,
    )
    new_state = MountState(
        mount_point=STANDARD_MOUNT_POINT,
        instance_key=STANDARD_MOUNT_POINT.instance_key({}),
        values=frozendict(),
        objects=ordered_state.objects,
    )
    apply_mount_state(
        parent_binding,
        old_state=old_state,
        new_state=new_state,
        ordered_state=ordered_state,
    )


def _standard_mount_state(nodes: Sequence[UiNode]) -> MountState | None:
    if not nodes:
        return None
    return MountState(
        mount_point=STANDARD_MOUNT_POINT,
        instance_key=STANDARD_MOUNT_POINT.instance_key({}),
        values=frozendict(),
        objects=tuple(_mounted_ref(node) for node in nodes),
    )


def _build_standard_mount_delta(
    *,
    previous_nodes: Sequence[UiNode],
    next_nodes: Sequence[UiNode],
    removed_nodes: Sequence[UiNode],
) -> ImmutableOrderedMountState[UiNode]:
    if previous_nodes:
        builder = OrderedMountStateBuilder.from_state(
            ImmutableOrderedMountState(
                revision=1,
                objects=tuple(_mounted_ref(node) for node in previous_nodes),
            )
        )
    else:
        builder = OrderedMountStateBuilder.empty()

    for node in removed_nodes:
        builder.detach(_mounted_ref(node))

    for index, node in enumerate(next_nodes):
        current = builder.current_objects()
        desired_ref = _mounted_ref(node)
        if index < len(current):
            current_ref = current[index]
            if current_ref.node_id == desired_ref.node_id and current_ref.value is desired_ref.value:
                continue
        builder.place(index, desired_ref)

    return builder.build()


def _mounted_ref(node: UiNode) -> MountedRef[UiNode]:
    return MountedRef(node_id=node.spec.node_id, value=node)


def _backend_identity(backend: UiBackendAdapter) -> tuple[type[Any], str]:
    return (type(backend), str(getattr(backend, "backend_id", type(backend).__name__)))


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
    "STANDARD_MOUNT_POINT",
    "mount_subtree",
    "reconcile_children",
    "reconcile_owner",
    "remount_owner_region",
]
