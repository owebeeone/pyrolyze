"""Runtime types and compatibility checks for the generic testing backend."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from frozendict import frozendict

from .model import PyroArgs, PyroMountBucket, PyroMountEntry, PyroNode
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

    @property
    def generation(self) -> int:
        return self._pyro_generation

    def to_pyro_node(self) -> PyroNode:
        mounts: dict[object, tuple[PyroMountBucket, ...]] = {}
        for mount_name, bucket_map in self._pyro_mounts.items():
            if not bucket_map:
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
            )
            mounts[mount_name] = buckets
        return PyroNode(
            node_type=type(self).__node_spec__.name,
            generation=self._pyro_generation,
            kwargs=frozendict(self._pyro_constructor_kwargs),
            mounts=frozendict(mounts),
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
        bucket_map[bucket_key] = _LiveMountBucket(
            key=bucket_key,
            values=PyroArgs(),
            objects=resolved_children,
        )
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
        existing.objects = updated
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
        self._update_generation()


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
                namespace[f"insert_{mount.name}"] = _make_insert_method(mount.name)
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


def _make_insert_method(mount_name: str) -> Any:
    def insert(self: GeneratedPyroMountable, index: int, child: GeneratedPyroMountable) -> None:
        self._ordered_insert(mount_name, index, child)

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
