"""Runtime types and compatibility checks for the generic testing backend."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from frozendict import frozendict

from pyrolyze.backends.model import MountReplayKind

from .model import (
    PyroArgs,
    PyroHostSurface,
    PyroHostSurfaceEntry,
    PyroHostSurfaceOperation,
    PyroMountBucket,
    PyroMountEntry,
    PyroMountOperation,
    PyroNode,
)
from .specs import MountInterfaceKind, MountSpec, NodeGenSpec, validate_node_specs

_CURRENT_GENERATION: ContextVar[int] = ContextVar("pyrolyze_generic_backend_generation", default=0)
_STRICT_COMPATIBILITY: ContextVar[bool] = ContextVar("pyrolyze_generic_backend_strict", default=True)


class PyrolyzeMountCompatibilityError(TypeError):
    """Raised when a generated mount receives an incompatible child type."""


@contextmanager
def generic_backend_runtime_context(*, generation: int, strict_compatibility: bool) -> Iterable[None]:
    generation_token = _CURRENT_GENERATION.set(generation)
    strict_token = _STRICT_COMPATIBILITY.set(strict_compatibility)
    try:
        yield
    finally:
        _STRICT_COMPATIBILITY.reset(strict_token)
        _CURRENT_GENERATION.reset(generation_token)


def current_generation() -> int:
    return _CURRENT_GENERATION.get()


def strict_compatibility_enabled() -> bool:
    return _STRICT_COMPATIBILITY.get()


@dataclass(slots=True)
class _LiveMountBucket:
    key: PyroArgs
    values: PyroArgs
    objects: list[GeneratedPyroMountable]


@dataclass(slots=True)
class _LiveHostSurfaceEntry:
    placement_handle: object
    child: GeneratedPyroMountable


@dataclass(slots=True)
class _LiveHostSurface:
    surface_name: str
    entries: list[_LiveHostSurfaceEntry]
    next_handle: int = 0


class GeneratedPyroMountable:
    __node_spec__: NodeGenSpec
    __runtime_types__: Mapping[str, type[GeneratedPyroMountable]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        constructor_names = tuple(param.name for param in type(self).__node_spec__.constructor)
        resolved_kwargs = dict(kwargs)
        for index, value in enumerate(args):
            if index >= len(constructor_names):
                raise TypeError(f"too many positional args for {type(self).__name__}")
            resolved_kwargs.setdefault(constructor_names[index], value)
        self._pyro_constructor_kwargs = {
            name: resolved_kwargs[name]
            for name in constructor_names
            if name in resolved_kwargs
        }
        self._pyro_generation = current_generation()
        self._pyro_mounts: dict[str, dict[PyroArgs, _LiveMountBucket]] = {
            mount.name: {} for mount in type(self).__node_spec__.mounts
        }
        self._pyro_mount_operations: list[PyroMountOperation] = []
        self._pyro_host_surfaces: dict[str, _LiveHostSurface] = {}
        self._pyro_host_surface_operations: list[PyroHostSurfaceOperation] = []

    @property
    def generation(self) -> int:
        return self._pyro_generation

    def to_pyro_node(self) -> PyroNode:
        mounts: dict[object, tuple[PyroMountBucket, ...]] = {}
        mount_metadata: dict[object, frozendict[str, Any]] = {}
        host_surfaces: dict[object, PyroHostSurface] = {}
        host_surface_metadata: dict[object, frozendict[str, Any]] = {}
        for mount_name, bucket_map in self._pyro_mounts.items():
            mount_spec = self._mount_spec(mount_name)
            host_surface = self._pyro_host_surfaces.get(mount_name)
            if not bucket_map and host_surface is None:
                continue
            buckets = tuple(
                PyroMountBucket(
                    key=bucket.key,
                    values=bucket.values,
                    entries=tuple(
                        PyroMountEntry(placement_id=index, node=child.to_pyro_node())
                        for index, child in enumerate(bucket.objects)
                    ),
                )
                for bucket in _sorted_live_buckets(bucket_map.values())
                if bucket.objects
            )
            if buckets:
                mounts[mount_name] = buckets
                mount_metadata[mount_name] = _mount_metadata(mount_spec)
            if host_surface is not None and host_surface.entries:
                host_surfaces[mount_name] = PyroHostSurface(
                    surface_name=host_surface.surface_name,
                    entries=tuple(
                        PyroHostSurfaceEntry(
                            placement_handle=entry.placement_handle,
                            node=entry.child.to_pyro_node(),
                        )
                        for entry in host_surface.entries
                    ),
                )
                host_surface_metadata[mount_name] = _host_surface_metadata(mount_spec)
        return PyroNode(
            node_type=type(self).__node_spec__.name,
            generation=self._pyro_generation,
            kwargs=frozendict(self._pyro_constructor_kwargs),
            mounts=frozendict(mounts),
            mount_metadata=frozendict(mount_metadata),
            mount_operations=tuple(self._pyro_mount_operations),
            host_surfaces=frozendict(host_surfaces),
            host_surface_metadata=frozendict(host_surface_metadata),
            host_surface_operations=tuple(self._pyro_host_surface_operations),
        )

    def _update_generation(self) -> None:
        self._pyro_generation = current_generation()

    def _mount_spec(self, mount_name: str) -> MountSpec:
        for mount in type(self).__node_spec__.mounts:
            if mount.name == mount_name:
                return mount
        raise ValueError(f"unknown mount {mount_name!r} on {type(self).__node_spec__.name!r}")

    def _validate_child(self, mount_spec: MountSpec, child: GeneratedPyroMountable) -> None:
        if not strict_compatibility_enabled():
            return
        accepted_kind = mount_spec.accepted_kind
        if accepted_kind is not None:
            if type(child).__node_spec__.name != accepted_kind:
                raise PyrolyzeMountCompatibilityError(
                    f"{type(self).__node_spec__.name!r} mount {mount_spec.name!r} accepts exact kind "
                    f"{accepted_kind!r}, got {type(child).__node_spec__.name!r}"
                )
            return
        accepted_base = mount_spec.accepted_base
        if accepted_base is None:
            return
        accepted_type = type(self).__runtime_types__[accepted_base]
        if not isinstance(child, accepted_type):
            raise PyrolyzeMountCompatibilityError(
                f"{type(self).__node_spec__.name!r} mount {mount_spec.name!r} accepts base "
                f"{accepted_base!r}, got {type(child).__node_spec__.name!r}"
            )

    def _ordered_add(self, mount_name: str, child: GeneratedPyroMountable) -> None:
        mount_spec = self._mount_spec(mount_name)
        self._validate_child(mount_spec, child)
        bucket_map = self._pyro_mounts[mount_name]
        bucket_key = PyroArgs()
        bucket = bucket_map.setdefault(bucket_key, _LiveMountBucket(key=bucket_key, values=PyroArgs(), objects=[]))
        bucket.objects.append(child)
        self._record_mount_operation(mount_name, "append", child=child)
        self._host_surface_append(mount_spec, child)
        self._update_generation()

    def _ordered_insert(self, mount_name: str, index: int, child: GeneratedPyroMountable) -> None:
        mount_spec = self._mount_spec(mount_name)
        self._validate_child(mount_spec, child)
        bucket_map = self._pyro_mounts[mount_name]
        bucket_key = PyroArgs()
        bucket = bucket_map.setdefault(bucket_key, _LiveMountBucket(key=bucket_key, values=PyroArgs(), objects=[]))
        bucket.objects = [existing for existing in bucket.objects if existing is not child]
        if index < 0:
            index = 0
        if index > len(bucket.objects):
            index = len(bucket.objects)
        bucket.objects.insert(index, child)
        self._record_mount_operation(mount_name, "place_by_index", index=index, child=child)
        self._host_surface_place_by_index(mount_spec, index, child)
        self._update_generation()

    def _ordered_insert_before(
        self,
        mount_name: str,
        before: GeneratedPyroMountable | None,
        child: GeneratedPyroMountable,
    ) -> None:
        mount_spec = self._mount_spec(mount_name)
        self._validate_child(mount_spec, child)
        bucket_map = self._pyro_mounts[mount_name]
        bucket_key = PyroArgs()
        bucket = bucket_map.setdefault(bucket_key, _LiveMountBucket(key=bucket_key, values=PyroArgs(), objects=[]))
        bucket.objects = [existing for existing in bucket.objects if existing is not child]
        index = len(bucket.objects)
        if before is not None and before in bucket.objects:
            index = bucket.objects.index(before)
        bucket.objects.insert(index, child)
        self._record_mount_operation(mount_name, "place_before_anchor", before=before, child=child)
        self._host_surface_place_before(mount_spec, before, child)
        self._update_generation()

    def _ordered_sync(self, mount_name: str, children: Iterable[GeneratedPyroMountable]) -> None:
        mount_spec = self._mount_spec(mount_name)
        resolved_children = list(children)
        for child in resolved_children:
            self._validate_child(mount_spec, child)
        bucket_key = PyroArgs()
        bucket_map = self._pyro_mounts[mount_name]
        existing = bucket_map.get(bucket_key)
        if existing is not None and existing.objects == resolved_children:
            return
        if not resolved_children:
            bucket_map.pop(bucket_key, None)
            self._record_mount_operation(mount_name, "sync", count=0)
            self._host_surface_sync(mount_spec, ())
            self._update_generation()
            return
        bucket_map[bucket_key] = _LiveMountBucket(
            key=bucket_key,
            values=PyroArgs(),
            objects=resolved_children,
        )
        self._record_mount_operation(mount_name, "sync", count=len(resolved_children))
        self._host_surface_sync(mount_spec, resolved_children)
        self._update_generation()

    def _ordered_detach(self, mount_name: str, child: GeneratedPyroMountable) -> None:
        bucket_key = PyroArgs()
        bucket_map = self._pyro_mounts[mount_name]
        existing = bucket_map.get(bucket_key)
        if existing is None:
            return
        updated = [entry for entry in existing.objects if entry is not child]
        if updated == existing.objects:
            return
        if not updated:
            bucket_map.pop(bucket_key, None)
        else:
            existing.objects = updated
        self._record_mount_operation(mount_name, "detach", child=child)
        self._host_surface_detach(self._mount_spec(mount_name), child)
        self._update_generation()

    def _set_single_or_keyed(
        self,
        mount_name: str,
        *call_args: Any,
        **call_kwargs: Any,
    ) -> None:
        mount_spec = self._mount_spec(mount_name)
        child, resolved_values = _resolve_mount_call(mount_spec, call_args, call_kwargs)
        bucket_key = _bucket_key(mount_spec, resolved_values)
        bucket_map = self._pyro_mounts[mount_name]
        if child is None:
            if bucket_key not in bucket_map:
                return
            bucket_map.pop(bucket_key, None)
            self._record_mount_operation(mount_name, "keyed_remove", key=bucket_key)
            self._host_surface_remove(self._mount_spec(mount_name), child=None)
            self._update_generation()
            return
        self._validate_child(mount_spec, child)
        bucket_values = _bucket_values(mount_spec, resolved_values)
        existing = bucket_map.get(bucket_key)
        if (
            existing is not None
            and existing.values == bucket_values
            and len(existing.objects) == 1
            and existing.objects[0] is child
        ):
            return
        bucket_map[bucket_key] = _LiveMountBucket(
            key=bucket_key,
            values=bucket_values,
            objects=[child],
        )
        self._record_mount_operation(mount_name, "keyed_set", key=bucket_key, child=child)
        self._host_surface_keyed_set(mount_spec, child)
        self._update_generation()

    def _record_mount_operation(
        self,
        mount_name: str,
        kind: str,
        **details: Any,
    ) -> None:
        normalized: dict[str, Any] = {}
        for key, value in details.items():
            if isinstance(value, GeneratedPyroMountable):
                normalized[f"{key}_type"] = type(value).__node_spec__.name
                child_name = value._pyro_constructor_kwargs.get("name")
                if child_name is not None:
                    normalized[f"{key}_name"] = child_name
                continue
            if isinstance(value, PyroArgs):
                normalized[key] = {
                    "args": value.args,
                    "kwargs": dict(value.kwargs),
                }
                continue
            normalized[key] = value
        self._pyro_mount_operations.append(
            PyroMountOperation(
                mount_name=mount_name,
                kind=kind,
                details=frozendict(normalized),
            )
        )

    def _host_surface(self, mount_spec: MountSpec) -> _LiveHostSurface | None:
        if mount_spec.host_surface_label is None:
            return None
        return self._pyro_host_surfaces.setdefault(
            mount_spec.name,
            _LiveHostSurface(surface_name=mount_spec.host_surface_label, entries=[]),
        )

    def _host_surface_append(self, mount_spec: MountSpec, child: GeneratedPyroMountable) -> None:
        surface = self._host_surface(mount_spec)
        if surface is None:
            return
        self._remove_host_child(surface, child)
        surface.entries.append(
            _LiveHostSurfaceEntry(
                placement_handle=self._next_host_handle(surface),
                child=child,
            )
        )
        self._record_host_surface_operation(mount_spec.name, "surface_attach", child=child)

    def _host_surface_place_by_index(
        self,
        mount_spec: MountSpec,
        index: int,
        child: GeneratedPyroMountable,
    ) -> None:
        surface = self._host_surface(mount_spec)
        if surface is None:
            return
        handle = self._remove_host_child(surface, child)
        if handle is None:
            handle = self._next_host_handle(surface)
            self._record_host_surface_operation(mount_spec.name, "surface_attach", child=child)
        bounded_index = max(0, min(index, len(surface.entries)))
        surface.entries.insert(
            bounded_index,
            _LiveHostSurfaceEntry(placement_handle=handle, child=child),
        )
        self._record_host_surface_operation(
            mount_spec.name,
            "surface_place_index",
            child=child,
            index=bounded_index,
        )

    def _host_surface_place_before(
        self,
        mount_spec: MountSpec,
        before: GeneratedPyroMountable | None,
        child: GeneratedPyroMountable,
    ) -> None:
        surface = self._host_surface(mount_spec)
        if surface is None:
            return
        handle = self._remove_host_child(surface, child)
        if handle is None:
            handle = self._next_host_handle(surface)
            self._record_host_surface_operation(mount_spec.name, "surface_attach", child=child)
        index = len(surface.entries)
        if before is not None:
            for current_index, entry in enumerate(surface.entries):
                if entry.child is before:
                    index = current_index
                    break
        surface.entries.insert(index, _LiveHostSurfaceEntry(placement_handle=handle, child=child))
        self._record_host_surface_operation(
            mount_spec.name,
            "surface_place_before",
            child=child,
            before=before,
        )

    def _host_surface_sync(
        self,
        mount_spec: MountSpec,
        children: Iterable[GeneratedPyroMountable],
    ) -> None:
        surface = self._host_surface(mount_spec)
        if surface is None:
            return
        resolved_children = list(children)
        if not resolved_children:
            self._pyro_host_surfaces.pop(mount_spec.name, None)
            self._record_host_surface_operation(mount_spec.name, "surface_sync", count=0)
            return
        existing_handles = {id(entry.child): entry.placement_handle for entry in surface.entries}
        surface.entries = [
            _LiveHostSurfaceEntry(
                placement_handle=existing_handles.get(id(child), self._next_host_handle(surface)),
                child=child,
            )
            for child in resolved_children
        ]
        self._record_host_surface_operation(
            mount_spec.name,
            "surface_sync",
            count=len(resolved_children),
        )

    def _host_surface_detach(self, mount_spec: MountSpec, child: GeneratedPyroMountable) -> None:
        surface = self._host_surface(mount_spec)
        if surface is None:
            return
        handle = self._remove_host_child(surface, child)
        if handle is None:
            return
        if not surface.entries:
            self._pyro_host_surfaces.pop(mount_spec.name, None)
        self._record_host_surface_operation(mount_spec.name, "surface_detach", child=child)

    def _host_surface_keyed_set(self, mount_spec: MountSpec, child: GeneratedPyroMountable) -> None:
        surface = self._host_surface(mount_spec)
        if surface is None:
            return
        handle = self._remove_host_child(surface, child)
        if handle is None:
            handle = self._next_host_handle(surface)
            self._record_host_surface_operation(mount_spec.name, "surface_attach", child=child)
        surface.entries.append(_LiveHostSurfaceEntry(placement_handle=handle, child=child))

    def _host_surface_remove(
        self,
        mount_spec: MountSpec,
        *,
        child: GeneratedPyroMountable | None,
    ) -> None:
        surface = self._host_surface(mount_spec)
        if surface is None:
            return
        if child is None:
            self._pyro_host_surfaces.pop(mount_spec.name, None)
            self._record_host_surface_operation(mount_spec.name, "surface_detach")
            return
        self._host_surface_detach(mount_spec, child)

    def _remove_host_child(
        self,
        surface: _LiveHostSurface,
        child: GeneratedPyroMountable,
    ) -> object | None:
        for index, entry in enumerate(surface.entries):
            if entry.child is child:
                surface.entries.pop(index)
                return entry.placement_handle
        return None

    def _next_host_handle(self, surface: _LiveHostSurface) -> int:
        handle = surface.next_handle
        surface.next_handle += 1
        return handle

    def _record_host_surface_operation(
        self,
        surface_name: str,
        kind: str,
        **details: Any,
    ) -> None:
        normalized: dict[str, Any] = {}
        for key, value in details.items():
            if isinstance(value, GeneratedPyroMountable):
                normalized[f"{key}_type"] = type(value).__node_spec__.name
                child_name = value._pyro_constructor_kwargs.get("name")
                if child_name is not None:
                    normalized[f"{key}_name"] = child_name
                continue
            normalized[key] = value
        self._pyro_host_surface_operations.append(
            PyroHostSurfaceOperation(
                surface_name=surface_name,
                kind=kind,
                details=frozendict(normalized),
            )
        )


def build_runtime_types(
    node_specs: tuple[NodeGenSpec, ...] | list[NodeGenSpec],
) -> dict[str, type[GeneratedPyroMountable]]:
    validated = validate_node_specs(node_specs)
    runtime_types: dict[str, type[GeneratedPyroMountable]] = {}
    for spec in validated:
        base_type = GeneratedPyroMountable if spec.base_name is None else runtime_types[spec.base_name]
        namespace: dict[str, Any] = {"__node_spec__": spec}
        for mount in spec.mounts:
            if mount.interface is MountInterfaceKind.ORDERED:
                namespace[f"add_{mount.name}"] = _make_add_method(mount.name)
                namespace[f"insert_{mount.name}"] = _make_insert_method(mount)
                namespace[f"sync_{_pluralize(mount.name)}"] = _make_sync_method(mount.name)
                namespace[f"detach_{mount.name}"] = _make_detach_method(mount.name)
            else:
                namespace[f"set_{mount.name}"] = _make_set_method(mount.name)
        runtime_types[spec.name] = type(spec.name, (base_type,), namespace)
    for runtime_type in runtime_types.values():
        runtime_type.__runtime_types__ = runtime_types
    return runtime_types


def _make_add_method(mount_name: str) -> Any:
    def add(self: GeneratedPyroMountable, child: GeneratedPyroMountable) -> None:
        self._ordered_add(mount_name, child)

    return add


def _make_insert_method(mount_spec: MountSpec) -> Any:
    if mount_spec.replay_kind is MountReplayKind.ANCHOR_BEFORE:
        def insert(
            self: GeneratedPyroMountable,
            before: GeneratedPyroMountable | None,
            child: GeneratedPyroMountable,
        ) -> None:
            self._ordered_insert_before(mount_spec.name, before, child)

        return insert

    def insert(self: GeneratedPyroMountable, index: int, child: GeneratedPyroMountable) -> None:
        self._ordered_insert(mount_spec.name, index, child)

    return insert


def _make_sync_method(mount_name: str) -> Any:
    def sync(self: GeneratedPyroMountable, children: Iterable[GeneratedPyroMountable]) -> None:
        self._ordered_sync(mount_name, children)

    return sync


def _make_detach_method(mount_name: str) -> Any:
    def detach(self: GeneratedPyroMountable, child: GeneratedPyroMountable) -> None:
        self._ordered_detach(mount_name, child)

    return detach


def _make_set_method(mount_name: str) -> Any:
    def set_mount(self: GeneratedPyroMountable, *call_args: Any, **call_kwargs: Any) -> None:
        self._set_single_or_keyed(mount_name, *call_args, **call_kwargs)

    return set_mount


def _resolve_mount_call(
    mount_spec: MountSpec,
    call_args: tuple[Any, ...],
    call_kwargs: Mapping[str, Any],
) -> tuple[GeneratedPyroMountable | None, dict[str, Any]]:
    if not call_args:
        raise TypeError(f"mount {mount_spec.name!r} requires a child value")
    if isinstance(call_args[0], GeneratedPyroMountable):
        child = call_args[0]
        param_args = call_args[1:]
    elif call_args[0] is None:
        child = None
        param_args = call_args[1:]
    else:
        last = call_args[-1]
        if last is None:
            child = None
            param_args = call_args[:-1]
        else:
            if not isinstance(last, GeneratedPyroMountable):
                raise TypeError(f"mount {mount_spec.name!r} requires a child value")
            child = last
            param_args = call_args[:-1]
    resolved_values = {
        param.name: value for param, value in zip(mount_spec.params, param_args)
    }
    resolved_values.update(call_kwargs)
    return child, resolved_values


def _bucket_key(mount_spec: MountSpec, resolved_values: Mapping[str, Any]) -> PyroArgs:
    keyed_values = tuple(
        resolved_values[param.name]
        for param in mount_spec.params
        if param.keyed and param.name in resolved_values
    )
    return PyroArgs(args=keyed_values)


def _bucket_values(mount_spec: MountSpec, resolved_values: Mapping[str, Any]) -> PyroArgs:
    return PyroArgs(
        kwargs=frozendict(
            {
                param.name: resolved_values[param.name]
                for param in mount_spec.params
                if not param.keyed and param.name in resolved_values
            }
        )
    )


def _mount_metadata(mount_spec: MountSpec) -> frozendict[str, Any]:
    metadata: dict[str, Any] = {
        "interface": mount_spec.interface.value,
        "replay_kind": mount_spec.replay_kind.value,
        "prefer_sync": mount_spec.prefer_sync,
    }
    if mount_spec.style_label is not None:
        metadata["style_label"] = mount_spec.style_label
    if mount_spec.profile_label is not None:
        metadata["profile_label"] = mount_spec.profile_label
    if mount_spec.mutation_policy is not None:
        metadata["mutation_policy"] = mount_spec.mutation_policy.value
    if mount_spec.small_delta_threshold is not None:
        metadata["small_delta_threshold"] = mount_spec.small_delta_threshold
    if mount_spec.host_surface_label is not None:
        metadata["host_surface_label"] = mount_spec.host_surface_label
        metadata["host_surface_ordered"] = mount_spec.host_surface_ordered
        metadata["host_surface_supports_anchor_before"] = mount_spec.host_surface_supports_anchor_before
        metadata["host_surface_keyed"] = mount_spec.host_surface_keyed
    if mount_spec.host_placement_profile_label is not None:
        metadata["host_placement_profile_label"] = mount_spec.host_placement_profile_label
    if mount_spec.host_child_kind is not None:
        metadata["host_child_kind"] = mount_spec.host_child_kind.value
        metadata["host_stable_slot_identity"] = mount_spec.host_stable_slot_identity
        metadata["host_separates_structure_from_placement"] = (
            mount_spec.host_separates_structure_from_placement
        )
    return frozendict(metadata)


def _host_surface_metadata(mount_spec: MountSpec) -> frozendict[str, Any]:
    metadata: dict[str, Any] = {}
    if mount_spec.host_surface_label is not None:
        metadata["host_surface_label"] = mount_spec.host_surface_label
        metadata["host_surface_ordered"] = mount_spec.host_surface_ordered
        metadata["host_surface_supports_anchor_before"] = mount_spec.host_surface_supports_anchor_before
        metadata["host_surface_keyed"] = mount_spec.host_surface_keyed
    if mount_spec.host_placement_profile_label is not None:
        metadata["host_placement_profile_label"] = mount_spec.host_placement_profile_label
    if mount_spec.host_child_kind is not None:
        metadata["host_child_kind"] = mount_spec.host_child_kind.value
        metadata["host_stable_slot_identity"] = mount_spec.host_stable_slot_identity
        metadata["host_separates_structure_from_placement"] = (
            mount_spec.host_separates_structure_from_placement
        )
    return frozendict(metadata)


def _sorted_live_buckets(
    buckets: Iterable[_LiveMountBucket],
) -> tuple[_LiveMountBucket, ...]:
    return tuple(
        sorted(
            buckets,
            key=lambda bucket: (repr(bucket.key.args), repr(tuple(sorted(bucket.key.kwargs.items())))),
        )
    )


def _pluralize(name: str) -> str:
    if name.endswith("s"):
        return name
    return f"{name}s"


__all__ = [
    "GeneratedPyroMountable",
    "PyrolyzeMountCompatibilityError",
    "build_runtime_types",
    "current_generation",
    "generic_backend_runtime_context",
    "strict_compatibility_enabled",
]
