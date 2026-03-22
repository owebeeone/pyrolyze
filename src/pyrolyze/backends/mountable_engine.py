"""Generic spec-driven engine for generated mountable libraries."""

from __future__ import annotations

from dataclasses import dataclass, field
import importlib
from typing import Any, Callable, Mapping

from pyrolyze.api import MISSING, UIElement
from pyrolyze.backends.model import (
    AccessorKind,
    FillPolicy,
    MethodMode,
    PropMode,
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


class MountableEngine:
    def __init__(
        self,
        mountable_specs: Mapping[str, UiWidgetSpec],
        *,
        read_current_prop_value: Callable[[object, UiWidgetSpec, str], Any] | None = None,
        capture_placement: Callable[[object], object | None] | None = None,
        restore_placement: Callable[[object, object | None], None] | None = None,
        dispose_mountable: Callable[[object], None] | None = None,
    ):
        self._mountable_specs = mountable_specs
        self._mountable_types: dict[str, type[object]] = {}
        self._read_current_prop_value = read_current_prop_value
        self._capture_placement = capture_placement
        self._restore_placement = restore_placement
        self._dispose_mountable = dispose_mountable

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
        node.child_nodes = self._mount_standard_children(
            node.mountable,
            spec,
            element.children,
            parent_slot_id=next_key.slot_id,
        )
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
        child_nodes = self._mount_standard_children(
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
        )

    def _replace_node_mountable(
        self,
        node: MountedMountableNode,
        replacement: MountedMountableNode,
    ) -> None:
        old_mountable = node.mountable
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
            prop = self._prop_for(spec, name)
            if prop.mode is PropMode.READONLY:
                raise ValueError(f"readonly prop {name!r} may not be mounted")
            effective[name] = value
        return effective

    def _create_mountable(self, spec: UiWidgetSpec, effective_props: Mapping[str, Any]) -> object:
        mountable_type = self._mountable_type_for(spec)
        constructor_kwargs: dict[str, Any] = {}
        method_backed_source_props = _method_backed_source_props(spec)
        for name, value in effective_props.items():
            prop = spec.props.get(name)
            if prop is None or prop.constructor_name is None:
                continue
            if name in method_backed_source_props:
                continue
            constructor_kwargs[prop.constructor_name] = value
        mountable = mountable_type(**constructor_kwargs)
        self._apply_mount_props(mountable, spec, effective_props)
        self._apply_mount_methods(mountable, spec, effective_props)
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

    def _mount_standard_children(
        self,
        parent: object,
        spec: UiWidgetSpec,
        children: tuple[UIElement, ...],
        *,
        parent_slot_id: Any | None,
    ) -> list[MountedMountableNode]:
        mount_point = spec.mount_points.get("standard")
        if mount_point is None:
            return []
        child_nodes = [
            self.mount(child, slot_id=_child_slot_id(parent_slot_id, index), call_site_id=child.call_site_id)
            for index, child in enumerate(children)
        ]
        if mount_point.sync_method_name is not None:
            getattr(parent, mount_point.sync_method_name)([child.mountable for child in child_nodes])
        return child_nodes


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


__all__ = ["MountableEngine", "MountedMountableNode", "MountableNodeKey"]
