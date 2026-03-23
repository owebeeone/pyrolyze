"""Generic spec-driven engine for generated mountable libraries."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
import importlib
from typing import Any, Callable, Mapping

from frozendict import frozendict

from pyrolyze.api import MISSING, EmittedNode, MountDirective, MountSelector, SlotSelector, UIElement
from pyrolyze.backends.mounts import MountedRef, apply_mount_state
from pyrolyze.backends.model import (
    AccessorKind,
    FillPolicy,
    MethodMode,
    MountPointSpec,
    MountState,
    PropMode,
    TypeRef,
    UiEventSpec,
    UiMethodSpec,
    UiPropSpec,
    UiWidgetSpec,
)


@dataclass(frozen=True, slots=True)
class MountableNodeKey:
    slot_id: Any | None
    call_site_id: int | str | None
    kind: str


@dataclass(slots=True)
class MountedMountableNode:
    key: MountableNodeKey
    element: UIElement
    spec: UiWidgetSpec
    mountable: object
    effective_props: dict[str, Any] = field(default_factory=dict)
    child_nodes: list["MountedMountableNode"] = field(default_factory=list)
    mount_states: dict[tuple[object, ...], MountState] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class _FlattenedMountAttachment:
    element: UIElement
    mount_point: MountPointSpec
    values: frozendict[str, Any]


class MountableEngine:
    def __init__(
        self,
        mountable_specs: Mapping[str, UiWidgetSpec],
        *,
        read_current_prop_value: Callable[[object, UiWidgetSpec, str], Any] | None = None,
        connect_event_signal: Callable[[object, UiEventSpec, Callable[..., None]], None] | None = None,
        capture_placement: Callable[[object], object | None] | None = None,
        restore_placement: Callable[[object, object | None], None] | None = None,
        dispose_mountable: Callable[[object], None] | None = None,
    ):
        self._mountable_specs = mountable_specs
        self._mountable_types: dict[str, type[object]] = {}
        self._read_current_prop_value = read_current_prop_value
        self._connect_event_signal = connect_event_signal
        self._capture_placement = capture_placement
        self._restore_placement = restore_placement
        self._dispose_mountable = dispose_mountable
        self._event_callbacks: dict[int, dict[str, Callable[..., None] | None]] = {}
        self._connected_events: set[tuple[int, str]] = set()

    def mount(
        self,
        element: UIElement,
        *,
        slot_id: Any | None = None,
        call_site_id: int | str | None = None,
    ) -> MountedMountableNode:
        spec = self._spec_for(element.kind)
        effective_props = self._initial_effective_props(spec, element)
        return self._mount_node(
            element=element,
            spec=spec,
            effective_props=effective_props,
            key=MountableNodeKey(
                slot_id=slot_id if slot_id is not None else element.slot_id,
                call_site_id=call_site_id if call_site_id is not None else element.call_site_id,
                kind=element.kind,
            ),
        )

    def update(
        self,
        node: MountedMountableNode,
        element: UIElement,
        *,
        slot_id: Any | None = None,
        call_site_id: int | str | None = None,
    ) -> MountedMountableNode:
        spec = self._spec_for(element.kind)
        next_key = MountableNodeKey(
            slot_id=slot_id if slot_id is not None else node.key.slot_id,
            call_site_id=call_site_id if call_site_id is not None else node.key.call_site_id,
            kind=element.kind,
        )

        if spec.kind != node.spec.kind:
            replacement = self.mount(element, slot_id=next_key.slot_id, call_site_id=next_key.call_site_id)
            self._replace_node_mountable(node, replacement)
            return node

        next_effective = dict(node.effective_props)
        changed_props: dict[str, Any] = {}
        remount_required = False
        for name, value in element.props.items():
            if value is MISSING:
                continue
            if name in spec.events:
                next_effective[name] = value
                changed_props[name] = value
                continue
            prop = self._prop_for(spec, name)
            if prop.mode is PropMode.READONLY:
                raise ValueError(f"readonly prop {name!r} may not be updated")
            if prop.mode is PropMode.CREATE_ONLY:
                continue
            if next_effective.get(name, MISSING) == value:
                continue
            next_effective[name] = value
            changed_props[name] = value
            if prop.mode is PropMode.CREATE_ONLY_REMOUNT:
                remount_required = True

        if remount_required:
            replacement = self._mount_node(
                element=element,
                spec=spec,
                effective_props=next_effective,
                key=next_key,
            )
            self._replace_node_mountable(node, replacement)
            return node

        self._apply_changed_props(node.mountable, spec, changed_props)
        self._apply_changed_methods(node.mountable, spec, next_effective, changed_props)
        self._apply_mount_events(node.mountable, spec, next_effective)
        child_nodes, mount_states = self._mount_children(
            node.mountable,
            spec,
            element.children,
            parent_slot_id=next_key.slot_id,
            old_child_nodes=node.child_nodes,
            old_mount_states=node.mount_states,
        )
        node.child_nodes = child_nodes
        node.mount_states = mount_states
        node.key = next_key
        node.element = element
        node.spec = spec
        node.effective_props = next_effective
        return node

    def _mount_node(
        self,
        *,
        element: UIElement,
        spec: UiWidgetSpec,
        effective_props: Mapping[str, Any],
        key: MountableNodeKey,
    ) -> MountedMountableNode:
        mountable = self._create_mountable(spec, effective_props)
        child_nodes, mount_states = self._mount_children(
            mountable,
            spec,
            element.children,
            parent_slot_id=key.slot_id,
        )
        return MountedMountableNode(
            key=key,
            element=element,
            spec=spec,
            mountable=mountable,
            effective_props=dict(effective_props),
            child_nodes=child_nodes,
            mount_states=mount_states,
        )

    def _replace_node_mountable(
        self,
        node: MountedMountableNode,
        replacement: MountedMountableNode,
    ) -> None:
        old_mountable = node.mountable
        old_event_names = tuple(node.spec.events)
        placement = (
            None if self._capture_placement is None else self._capture_placement(old_mountable)
        )
        node.key = replacement.key
        node.element = replacement.element
        node.spec = replacement.spec
        node.mountable = replacement.mountable
        node.effective_props = replacement.effective_props
        node.child_nodes = replacement.child_nodes
        if self._restore_placement is not None:
            self._restore_placement(node.mountable, placement)
        if self._dispose_mountable is not None:
            self._dispose_mountable(old_mountable)
        self._event_callbacks.pop(id(old_mountable), None)
        for event_name in old_event_names:
            self._connected_events.discard((id(old_mountable), event_name))

    def _spec_for(self, kind: str) -> UiWidgetSpec:
        spec = self._mountable_specs.get(kind)
        if spec is None:
            raise ValueError(f"unsupported mountable kind {kind!r}")
        return spec

    def _prop_for(self, spec: UiWidgetSpec, name: str) -> UiPropSpec:
        prop = spec.props.get(name)
        if prop is None:
            raise ValueError(f"unsupported prop {name!r} for mountable kind {spec.kind!r}")
        return prop

    def _initial_effective_props(self, spec: UiWidgetSpec, element: UIElement) -> dict[str, Any]:
        effective: dict[str, Any] = {}
        for name, value in element.props.items():
            if value is MISSING:
                continue
            if name in spec.events:
                effective[name] = value
                continue
            prop = self._prop_for(spec, name)
            if prop.mode is PropMode.READONLY:
                raise ValueError(f"readonly prop {name!r} may not be mounted")
            effective[name] = value
        return effective

    def _create_mountable(self, spec: UiWidgetSpec, effective_props: Mapping[str, Any]) -> object:
        mountable_type = self._mountable_type_for(spec)
        constructor_args: list[Any] = []
        constructor_kwargs: dict[str, Any] = {}
        method_backed_source_props = _method_backed_source_props(spec)
        for name in spec.constructor_params:
            if name not in effective_props:
                continue
            value = effective_props[name]
            prop = spec.props.get(name)
            if prop is None or prop.constructor_name is None:
                continue
            if name in method_backed_source_props:
                continue
            if _is_positional_constructor_name(prop.constructor_name):
                position = _constructor_position(prop.constructor_name)
                while len(constructor_args) <= position:
                    constructor_args.append(MISSING)
                constructor_args[position] = value
                continue
            constructor_kwargs[prop.constructor_name] = value
        mountable = mountable_type(
            *[value for value in constructor_args if value is not MISSING],
            **constructor_kwargs,
        )
        self._apply_mount_props(mountable, spec, effective_props)
        self._apply_mount_methods(mountable, spec, effective_props)
        self._apply_mount_events(mountable, spec, effective_props)
        return mountable

    def _mountable_type_for(self, spec: UiWidgetSpec) -> type[object]:
        resolved = self._mountable_types.get(spec.mounted_type_name)
        if resolved is not None:
            return resolved
        module_name, _, attr_name = spec.mounted_type_name.rpartition(".")
        module = importlib.import_module(module_name)
        resolved = getattr(module, attr_name)
        if not isinstance(resolved, type):
            raise TypeError(f"{spec.mounted_type_name!r} is not a type")
        self._mountable_types[spec.mounted_type_name] = resolved
        return resolved

    def _apply_mount_props(
        self,
        mountable: object,
        spec: UiWidgetSpec,
        effective_props: Mapping[str, Any],
    ) -> None:
        method_backed_source_props = _method_backed_source_props(spec)
        for name, value in effective_props.items():
            if name in method_backed_source_props:
                continue
            prop = spec.props.get(name)
            if prop is None or prop.setter_kind is None:
                continue
            if prop.mode in {PropMode.CREATE_UPDATE, PropMode.UPDATE_ONLY}:
                self._apply_prop(mountable, prop, value)
            elif prop.mode in {PropMode.CREATE_ONLY, PropMode.CREATE_ONLY_REMOUNT} and prop.constructor_name is None:
                self._apply_prop(mountable, prop, value)

    def _apply_mount_methods(
        self,
        mountable: object,
        spec: UiWidgetSpec,
        effective_props: Mapping[str, Any],
    ) -> None:
        for method in spec.methods.values():
            if method.mode not in {
                MethodMode.CREATE_ONLY,
                MethodMode.CREATE_ONLY_REMOUNT,
                MethodMode.CREATE_UPDATE,
            }:
                continue
            resolved = self._resolve_method_args(mountable, spec, effective_props, method)
            if resolved is None:
                continue
            args, _ = resolved
            self._apply_method(mountable, method, args)

    def _apply_changed_props(
        self,
        mountable: object,
        spec: UiWidgetSpec,
        changed_props: Mapping[str, Any],
    ) -> None:
        method_backed_source_props = _method_backed_source_props(spec)
        for name, value in changed_props.items():
            if name in method_backed_source_props:
                continue
            prop = spec.props.get(name)
            if prop is None or prop.setter_kind is None:
                continue
            if prop.mode not in {PropMode.CREATE_UPDATE, PropMode.UPDATE_ONLY}:
                continue
            self._apply_prop(mountable, prop, value)

    def _apply_changed_methods(
        self,
        mountable: object,
        spec: UiWidgetSpec,
        effective_props: dict[str, Any],
        changed_props: Mapping[str, Any],
    ) -> None:
        if not changed_props:
            return
        changed_names = set(changed_props)
        for method in spec.methods.values():
            if method.mode not in {MethodMode.CREATE_UPDATE, MethodMode.UPDATE_ONLY}:
                continue
            if not changed_names.intersection(method.source_props):
                continue
            resolved = self._resolve_method_args(mountable, spec, effective_props, method)
            if resolved is None:
                continue
            args, backfilled = resolved
            if backfilled:
                effective_props.update(backfilled)
            self._apply_method(mountable, method, args)

    def _apply_mount_events(
        self,
        mountable: object,
        spec: UiWidgetSpec,
        effective_props: Mapping[str, Any],
    ) -> None:
        if not spec.events:
            return
        callbacks = self._event_callbacks.setdefault(id(mountable), {})
        for event_name, event_spec in spec.events.items():
            callback = effective_props.get(event_name)
            callbacks[event_name] = callback if callable(callback) else None
            self._ensure_event_connected(mountable, event_spec)

    def _ensure_event_connected(
        self,
        mountable: object,
        event_spec: UiEventSpec,
    ) -> None:
        if self._connect_event_signal is None:
            return
        event_key = (id(mountable), event_spec.name)
        if event_key in self._connected_events:
            return
        self._connect_event_signal(
            mountable,
            event_spec,
            self._event_dispatcher(mountable, event_spec),
        )
        self._connected_events.add(event_key)

    def _event_dispatcher(
        self,
        mountable: object,
        event_spec: UiEventSpec,
    ) -> Callable[..., None]:
        def dispatch(*args: Any) -> None:
            callback = self._event_callbacks.get(id(mountable), {}).get(event_spec.name)
            if callback is None:
                return
            if event_spec.payload_policy.value == "none":
                callback()
                return
            if event_spec.payload_policy.value == "first_arg":
                callback(args[0] if args else None)
                return
            callback(*args)

        return dispatch

    def _resolve_method_args(
        self,
        mountable: object,
        spec: UiWidgetSpec,
        effective_props: Mapping[str, Any],
        method: UiMethodSpec,
    ) -> tuple[tuple[Any, ...], dict[str, Any]] | None:
        args: list[Any] = []
        backfilled: dict[str, Any] = {}
        for source_prop in method.source_props:
            if source_prop not in effective_props:
                if method.fill_policy is FillPolicy.RETAIN_EFFECTIVE:
                    if self._read_current_prop_value is None:
                        return None
                    value = self._read_current_prop_value(mountable, spec, source_prop)
                    if value is MISSING:
                        return None
                    backfilled[source_prop] = value
                    args.append(value)
                    continue
                return None
            args.append(effective_props[source_prop])
        return (tuple(args), backfilled)

    def _apply_prop(self, mountable: object, prop: UiPropSpec, value: Any) -> None:
        if prop.setter_kind is AccessorKind.PYTHON_PROPERTY:
            setattr(mountable, prop.setter_name or prop.name, value)
            return
        if prop.setter_kind is AccessorKind.METHOD:
            if prop.setter_name is None:
                raise ValueError(f"missing setter_name for method prop {prop.name!r}")
            getattr(mountable, prop.setter_name)(value)
            return
        if prop.setter_kind is AccessorKind.QT_PROPERTY:
            setter = getattr(mountable, "setProperty", None)
            if not callable(setter):
                raise NotImplementedError(
                    f"{type(mountable).__name__} does not support qt_property updates"
                )
            setter(prop.name, value)
            return
        if prop.setter_kind is AccessorKind.TK_CONFIG:
            if prop.setter_name is None:
                raise ValueError(f"missing setter_name for tk_config prop {prop.name!r}")
            getattr(mountable, prop.setter_name)(**{prop.name: value})
            return
        raise NotImplementedError(f"unsupported setter kind {prop.setter_kind!r}")

    def _apply_method(self, mountable: object, method: UiMethodSpec, args: tuple[Any, ...]) -> None:
        for method_name in (method.name, _camel_to_snake(method.name)):
            if hasattr(mountable, method_name):
                getattr(mountable, method_name)(*args)
                return
        raise AttributeError(f"{type(mountable).__name__} has no method for spec {method.name!r}")

    def _mount_children(
        self,
        parent: object,
        spec: UiWidgetSpec,
        children: tuple[EmittedNode, ...],
        *,
        parent_slot_id: Any | None,
        old_child_nodes: list[MountedMountableNode] | None = None,
        old_mount_states: Mapping[tuple[object, ...], MountState] | None = None,
    ) -> tuple[list[MountedMountableNode], dict[tuple[object, ...], MountState]]:
        if not children and not old_mount_states and not old_child_nodes:
            return [], {}
        flattened_children = self._flatten_child_attachments(spec, children)
        reusable_children = _child_node_pool(old_child_nodes or [])
        child_nodes: list[MountedMountableNode] = []
        for index, attachment in enumerate(flattened_children):
            child = attachment.element
            child_slot_id = _resolved_child_slot_id(child, parent_slot_id, index)
            child_call_site_id = child.call_site_id
            current = _take_reusable_child(
                reusable_children,
                child,
                slot_id=child_slot_id,
                call_site_id=child_call_site_id,
            )
            if current is None:
                child_nodes.append(
                    self.mount(
                        child,
                        slot_id=child_slot_id,
                        call_site_id=child_call_site_id,
                    )
                )
                continue
            child_nodes.append(
                self.update(
                    current,
                    child,
                    slot_id=child_slot_id,
                    call_site_id=child_call_site_id,
                )
            )
        mount_states = self._build_mount_states(child_nodes, flattened_children)

        if old_mount_states is not None:
            for instance_key, old_state in old_mount_states.items():
                if instance_key in mount_states:
                    continue
                apply_mount_state(
                    parent,
                    old_state=old_state,
                    new_state=MountState(
                        mount_point=old_state.mount_point,
                        instance_key=old_state.instance_key,
                        values=old_state.values,
                        objects=(),
                    ),
                )
        for instance_key, state in mount_states.items():
            apply_mount_state(
                parent,
                old_state=None if old_mount_states is None else old_mount_states.get(instance_key),
                new_state=state,
            )
        for removed_child in _remaining_reusable_children(reusable_children):
            self._dispose_node_subtree(removed_child)
        return child_nodes, mount_states

    def _flatten_child_attachments(
        self,
        parent_spec: UiWidgetSpec,
        children: tuple[EmittedNode, ...],
        *,
        selectors: tuple[SlotSelector, ...] | None = None,
    ) -> list[_FlattenedMountAttachment]:
        attachments: list[_FlattenedMountAttachment] = []
        for child in children:
            if isinstance(child, MountDirective):
                directive_selectors = child.selectors
                if any(
                    isinstance(selector, MountSelector) and selector.kind == "no_emit"
                    for selector in directive_selectors
                ):
                    if child.children:
                        raise RuntimeError("mount(no_emit) does not allow emitted children")
                    continue
                attachments.extend(
                    self._flatten_child_attachments(
                        parent_spec,
                        child.children,
                        selectors=directive_selectors,
                    )
                )
                continue
            mount_point, values = self._resolve_child_mount(parent_spec, child, selectors)
            attachments.append(
                _FlattenedMountAttachment(
                    element=child,
                    mount_point=mount_point,
                    values=frozendict(values),
                )
            )
        return attachments

    def _resolve_child_mount(
        self,
        parent_spec: UiWidgetSpec,
        child: UIElement,
        selectors: tuple[SlotSelector, ...] | None,
    ) -> tuple[MountPointSpec, dict[str, Any]]:
        child_spec = self._spec_for(child.kind)
        if selectors is None:
            mount_point = self._default_mount_point_for_child(parent_spec, child_spec)
            return mount_point, {}
        child_type = self._mountable_type_for(child_spec)
        for selector in selectors:
            resolved = self._resolve_selector_mount_point(
                parent_spec,
                child_type,
                selector,
            )
            if resolved is not None:
                return resolved
        raise ValueError(
            self._format_selector_attach_error(
                parent_spec,
                child_spec,
                selectors,
            )
        )

    def _resolve_selector_mount_point(
        self,
        parent_spec: UiWidgetSpec,
        child_type: type[object],
        selector: SlotSelector,
    ) -> tuple[MountPointSpec, dict[str, Any]] | None:
        if not isinstance(selector, MountSelector):
            raise TypeError("mount selectors must currently be MountSelector values")
        if selector.kind == "no_emit":
            raise RuntimeError("mount(no_emit) does not allow emitted children")
        if selector.kind == "default":
            mount_point = self._try_default_mount_point_for_child(parent_spec, child_type)
            if mount_point is None:
                return None
            return mount_point, {}
        if selector.kind != "named" or selector.name is None:
            return None
        mount_point = parent_spec.mount_points.get(selector.name)
        if mount_point is None:
            return None
        if not self._mount_point_accepts_child(mount_point, child_type):
            return None
        values = dict(selector.values)
        if not self._selector_values_satisfy_mount_point(mount_point, values):
            return None
        return mount_point, values

    def _selector_values_satisfy_mount_point(
        self,
        mount_point: MountPointSpec,
        values: Mapping[str, Any],
    ) -> bool:
        param_names = {param.name for param in mount_point.params}
        if any(name not in param_names for name in values):
            return False
        for param in mount_point.params:
            if param.name in values:
                continue
            if param.default_repr is None:
                return False
        return True

    def _dispose_node_subtree(self, node: MountedMountableNode) -> None:
        for child in node.child_nodes:
            self._dispose_node_subtree(child)
        mountable = node.mountable
        self._event_callbacks.pop(id(mountable), None)
        for event_name in node.spec.events:
            self._connected_events.discard((id(mountable), event_name))
        if self._dispose_mountable is not None:
            self._dispose_mountable(mountable)

    def _build_mount_states(
        self,
        child_nodes: list[MountedMountableNode],
        attachments: list[_FlattenedMountAttachment],
    ) -> dict[tuple[object, ...], MountState]:
        grouped: dict[tuple[object, ...], dict[str, Any]] = {}
        for index, (child, attachment) in enumerate(zip(child_nodes, attachments, strict=True)):
            mount_point = attachment.mount_point
            values = dict(attachment.values)
            instance_key = self._mount_instance_key(mount_point, values)
            bucket = grouped.setdefault(
                instance_key,
                {
                    "mount_point": mount_point,
                    "values": values,
                    "objects": [],
                },
            )
            bucket["objects"].append(
                MountedRef(
                    node_id=child.key.slot_id if child.key.slot_id is not None else index,
                    value=child.mountable,
                )
            )

        return {
            instance_key: MountState(
                mount_point=bucket["mount_point"],
                instance_key=instance_key,
                values=frozendict(bucket["values"]),
                objects=tuple(bucket["objects"]),
            )
            for instance_key, bucket in grouped.items()
        }

    def _default_mount_point_for_child(
        self,
        parent_spec: UiWidgetSpec,
        child_spec: UiWidgetSpec,
    ) -> MountPointSpec:
        child_type = self._mountable_type_for(child_spec)
        mount_point = self._try_default_mount_point_for_child(parent_spec, child_type)
        if mount_point is not None:
            return mount_point
        default_mount_points = [
            mount_point
            for mount_name in parent_spec.default_attach_mount_point_names
            if (mount_point := parent_spec.mount_points.get(mount_name)) is not None
        ]
        compatible_explicit_mount_points = [
            mount_point
            for mount_point in parent_spec.mount_points.values()
            if mount_point.name not in parent_spec.default_attach_mount_point_names
            and self._mount_point_accepts_child(mount_point, child_type)
        ]
        raise ValueError(
            self._format_unspecified_attach_error(
                parent_spec,
                child_spec,
                default_mount_points=default_mount_points,
                compatible_explicit_mount_points=compatible_explicit_mount_points,
            )
        )

    def _try_default_mount_point_for_child(
        self,
        parent_spec: UiWidgetSpec,
        child_type: type[object],
    ) -> MountPointSpec | None:
        for mount_name in parent_spec.default_attach_mount_point_names:
            mount_point = parent_spec.mount_points.get(mount_name)
            if mount_point is None:
                continue
            if not self._mount_point_accepts_child(mount_point, child_type):
                continue
            return mount_point
        return None

    def _mount_instance_key(
        self,
        mount_point: MountPointSpec,
        values: dict[str, Any],
    ) -> tuple[object, ...]:
        resolved_values = dict(values)
        for param in mount_point.params:
            if not param.keyed or param.name in resolved_values:
                continue
            if param.default_repr is None:
                raise ValueError(
                    f"mount point {mount_point.name!r} requires keyed parameter {param.name!r}"
                )
            resolved_values[param.name] = self._mount_param_default_value(param.default_repr)
        return mount_point.instance_key(resolved_values)

    def _mount_param_default_value(self, default_repr: str) -> Any:
        try:
            return ast.literal_eval(default_repr)
        except Exception:
            return default_repr

    def _mount_point_accepts_child(
        self,
        mount_point: MountPointSpec,
        child_type: type[object],
    ) -> bool:
        accepted_type = self._resolve_type_ref(mount_point.accepted_produced_type)
        return accepted_type is not None and issubclass(child_type, accepted_type)

    def _format_unspecified_attach_error(
        self,
        parent_spec: UiWidgetSpec,
        child_spec: UiWidgetSpec,
        *,
        default_mount_points: list[MountPointSpec],
        compatible_explicit_mount_points: list[MountPointSpec],
    ) -> str:
        prefix = (
            f"Cannot attach child kind {child_spec.kind!r} to parent {parent_spec.kind!r} "
            "without an explicit mount."
        )
        if default_mount_points:
            default_summary = ", ".join(
                self._format_mount_point_summary(mount_point) for mount_point in default_mount_points
            )
            if compatible_explicit_mount_points:
                explicit_summary = ", ".join(
                    self._format_mount_point_summary(mount_point)
                    for mount_point in compatible_explicit_mount_points
                )
                return (
                    f"{prefix} Default attach mount points are: {default_summary}. "
                    f"This child is supported, but explicit mount is required. "
                    f"Compatible explicit mount points: {explicit_summary}."
                )
            return (
                f"{prefix} Default attach mount points are: {default_summary}. "
                "No compatible explicit mount points were found."
            )
        if compatible_explicit_mount_points:
            explicit_summary = ", ".join(
                self._format_mount_point_summary(mount_point)
                for mount_point in compatible_explicit_mount_points
            )
            return (
                f"{prefix} {parent_spec.kind!r} has no default attach mount point. "
                f"This child is supported, but explicit mount is required. "
                f"Compatible explicit mount points: {explicit_summary}."
            )
        available_mount_points = ", ".join(
            self._format_mount_point_summary(mount_point)
            for mount_point in parent_spec.mount_points.values()
        ) or "none"
        return (
            f"{prefix} {parent_spec.kind!r} has no compatible default attach mount point, "
            f"and no explicit mount point accepts {child_spec.kind!r}. "
            f"Available mount points: {available_mount_points}."
        )

    def _format_selector_attach_error(
        self,
        parent_spec: UiWidgetSpec,
        child_spec: UiWidgetSpec,
        selectors: tuple[SlotSelector, ...],
    ) -> str:
        selector_summary = ", ".join(self._format_selector(selector) for selector in selectors)
        compatible_mount_points = [
            mount_point
            for mount_point in parent_spec.mount_points.values()
            if self._mount_point_accepts_child(
                mount_point,
                self._mountable_type_for(child_spec),
            )
        ]
        if compatible_mount_points:
            available = ", ".join(
                self._format_mount_point_summary(mount_point)
                for mount_point in compatible_mount_points
            )
            return (
                f"Cannot attach child kind {child_spec.kind!r} to parent {parent_spec.kind!r} "
                f"using selectors [{selector_summary}]. Compatible mount points are: {available}."
            )
        return (
            f"Cannot attach child kind {child_spec.kind!r} to parent {parent_spec.kind!r} "
            f"using selectors [{selector_summary}]; no compatible mount points were found."
        )

    def _format_selector(self, selector: SlotSelector) -> str:
        if not isinstance(selector, MountSelector):
            return type(selector).__name__
        if selector.kind == "named":
            if selector.values:
                args = ", ".join(f"{name}={value!r}" for name, value in selector.values.items())
                return f"{selector.name}({args})"
            return selector.name or "named"
        return selector.kind

    def _format_mount_point_summary(self, mount_point: MountPointSpec) -> str:
        details = [f"accepts {mount_point.accepted_produced_type.expr}"]
        keyed_params = [param.name for param in mount_point.params if param.keyed]
        required_params = [
            param.name for param in mount_point.params if not param.keyed and param.default_repr is None
        ]
        if keyed_params:
            details.append(f"keyed params: {', '.join(keyed_params)}")
        if required_params:
            details.append(f"required params: {', '.join(required_params)}")
        return f"{mount_point.name} ({'; '.join(details)})"

    def _format_standard_mount_error(
        self,
        parent_spec: UiWidgetSpec,
        child_spec: UiWidgetSpec,
        mount_point: MountPointSpec,
    ) -> str:
        return (
            f"Cannot attach child kind {child_spec.kind!r} to parent {parent_spec.kind!r} "
            f"through default mount point {mount_point.name!r}; it accepts "
            f"{mount_point.accepted_produced_type.expr}."
        )

    def _resolve_type_ref(self, type_ref: TypeRef) -> type[object] | None:
        expr = type_ref.expr.strip()
        if not expr or "|" in expr:
            return None
        spec = self._mountable_specs.get(expr)
        if spec is not None:
            return self._mountable_type_for(spec)
        resolved = self._mountable_types.get(expr)
        if resolved is not None:
            return resolved
        module_name, _, attr_name = expr.rpartition(".")
        if not module_name or not attr_name:
            return None
        module = importlib.import_module(module_name)
        resolved = getattr(module, attr_name)
        if not isinstance(resolved, type):
            return None
        self._mountable_types[expr] = resolved
        return resolved


def _method_backed_source_props(spec: UiWidgetSpec) -> set[str]:
    names: set[str] = set()
    for method in spec.methods.values():
        if not method.constructor_equivalent:
            continue
        names.update(method.source_props)
    return names


def _camel_to_snake(name: str) -> str:
    chars: list[str] = []
    for index, char in enumerate(name):
        if char.isupper() and index > 0:
            chars.append("_")
        chars.append(char.lower())
    return "".join(chars)


def _child_slot_id(parent_slot_id: Any | None, index: int) -> Any:
    if parent_slot_id is None:
        return (index,)
    if isinstance(parent_slot_id, tuple):
        return (*parent_slot_id, index)
    return (parent_slot_id, index)


def _resolved_child_slot_id(child: UIElement, parent_slot_id: Any | None, index: int) -> Any:
    if child.slot_id is not None:
        return child.slot_id
    return _child_slot_id(parent_slot_id, index)


@dataclass(slots=True)
class _ReusableChildPool:
    explicit: dict[tuple[Any | None, int | str | None], list[MountedMountableNode]]
    implicit: list[MountedMountableNode]


def _child_node_pool(child_nodes: list[MountedMountableNode]) -> _ReusableChildPool:
    explicit: dict[tuple[Any | None, int | str | None], list[MountedMountableNode]] = {}
    implicit: list[MountedMountableNode] = []
    for child_node in child_nodes:
        element_slot_id = child_node.element.slot_id
        element_call_site_id = child_node.element.call_site_id
        if element_slot_id is None and element_call_site_id is None:
            implicit.append(child_node)
            continue
        key = (element_slot_id, element_call_site_id)
        explicit.setdefault(key, []).append(child_node)
    return _ReusableChildPool(explicit=explicit, implicit=implicit)


def _take_reusable_child(
    pool: _ReusableChildPool,
    child: UIElement,
    *,
    slot_id: Any | None,
    call_site_id: int | str | None,
) -> MountedMountableNode | None:
    if child.slot_id is not None or call_site_id is not None:
        bucket = pool.explicit.get((child.slot_id, call_site_id))
        if bucket:
            return bucket.pop(0)
        bucket = pool.explicit.get((child.slot_id, None))
        if bucket:
            return bucket.pop(0)
    for index, existing in enumerate(pool.implicit):
        if existing.element == child:
            return pool.implicit.pop(index)
    if pool.implicit:
        return pool.implicit.pop(0)
    return None


def _remaining_reusable_children(
    pool: _ReusableChildPool,
) -> list[MountedMountableNode]:
    remaining = list(pool.implicit)
    for bucket in pool.explicit.values():
        remaining.extend(bucket)
    return remaining


def _is_positional_constructor_name(name: str) -> bool:
    return name.startswith("arg__")


def _constructor_position(name: str) -> int:
    return int(name.removeprefix("arg__")) - 1


__all__ = ["MountableEngine", "MountedMountableNode", "MountableNodeKey"]
