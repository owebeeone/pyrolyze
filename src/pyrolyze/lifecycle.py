from __future__ import annotations

"""Declarative current/working lifecycle helpers.

This module builds on :mod:`pyrolyze.freezable` to provide a higher-level,
declarative lifecycle model for stateful runtime objects.

The public surface is intentionally small:

- `@managed_context`
- `managed(...)`
- `managed_binding(...)`
- `LifecycleContext`

`managed(...)` defines ordinary value fields.

`managed_binding(...)` defines lifecycle-managed resource fields. For scalar
annotations this behaves as a single retained binding. For mapping
annotations, reads return a copy-on-write mapping proxy and commit/rollback
diffs drive `accepted()` / `close(was_committed=...)` on the resource values.

`managed(...)` does not attempt to track in-place mutation of nested mutable
values. If a field needs incremental dict-like lifecycle management, model it
as a binding map instead of a plain value field.

The generated current/working state classes are shallow and deliberately
lifecycle-agnostic. Application-specific semantics belong on the decorated
context class via overrides such as `before_commit(...)`.
"""

import sys
import types
from collections.abc import Iterator, Mapping, MutableMapping
from dataclasses import MISSING, dataclass, field
from typing import Any, Callable, Protocol, get_origin, get_type_hints

from .freezable import (
    HintResolutionMode,
    thawable_dataclass,
    thawed_dataclass,
)

_SENTINEL = object()
_MAPPING_ORIGINS = (dict, Mapping, MutableMapping)


class LifecycleBinding(Protocol):
    def accepted(self) -> None: ...

    def close(self, *, was_committed: bool) -> None: ...


@dataclass(slots=True)
class LifecycleTransaction:
    tx_id: int
    dirty_contexts: dict[int, LifecycleContext] = field(default_factory=dict)


class TransactionManager:
    def __init__(self) -> None:
        self._next_tx_id = 1
        self.active_transaction: LifecycleTransaction | None = None

    def begin(self) -> LifecycleTransaction:
        if self.active_transaction is not None:
            raise RuntimeError("nested lifecycle transactions are not supported")
        transaction = LifecycleTransaction(tx_id=self._next_tx_id)
        self._next_tx_id += 1
        self.active_transaction = transaction
        return transaction

    def commit(self) -> int | None:
        transaction = self.active_transaction
        if transaction is None:
            return None
        for context in list(transaction.dirty_contexts.values()):
            context._commit_transaction(transaction.tx_id)
        self.active_transaction = None
        return transaction.tx_id

    def rollback(self) -> int | None:
        transaction = self.active_transaction
        if transaction is None:
            return None
        for context in list(transaction.dirty_contexts.values()):
            context._rollback_transaction(transaction.tx_id)
        self.active_transaction = None
        return transaction.tx_id

    def enlist(self, context: LifecycleContext) -> int:
        transaction = self.active_transaction
        if transaction is None:
            raise RuntimeError("no active lifecycle transaction")
        transaction.dirty_contexts[id(context)] = context
        return transaction.tx_id

    def drop(self, context: LifecycleContext, tx_id: int | None = None) -> None:
        transaction = self.active_transaction
        if transaction is None:
            return
        if tx_id is not None and transaction.tx_id != tx_id:
            return
        transaction.dirty_contexts.pop(id(context), None)


class _ManagedField:
    __slots__ = ("binding", "default", "default_factory", "name", "annotation", "mapping")

    def __init__(
        self,
        *,
        binding: bool,
        default: Any = MISSING,
        default_factory: Callable[[], Any] | object = MISSING,
    ) -> None:
        if default is not MISSING and default_factory is not MISSING:
            raise TypeError("managed fields cannot define both default and default_factory")
        self.binding = binding
        self.default = default
        self.default_factory = default_factory
        self.name: str | None = None
        self.annotation: Any = Any
        self.mapping = False

    def __set_name__(self, owner: type[LifecycleContext], name: str) -> None:
        self.name = name

    def __get__(
        self,
        instance: LifecycleContext | None,
        owner: type[LifecycleContext],
    ) -> Any:
        if instance is None:
            return self
        if self.binding and self.mapping:
            return _BindingMapProxy(instance, self.name_or_error())
        return instance._get_field_value(self.name_or_error())

    def __set__(self, instance: LifecycleContext, value: Any) -> None:
        name = self.name_or_error()
        if self.binding and self.mapping:
            instance._set_binding_map(name, value)
            return
        instance._set_field_value(name, value, binding=self.binding)

    def name_or_error(self) -> str:
        if self.name is None:
            raise RuntimeError("managed field name was not initialized")
        return self.name


def managed(
    *,
    default: Any = MISSING,
    default_factory: Callable[[], Any] | object = MISSING,
) -> Any:
    return _ManagedField(
        binding=False,
        default=default,
        default_factory=default_factory,
    )


def managed_binding(
    *,
    default: Any = MISSING,
    default_factory: Callable[[], Any] | object = MISSING,
) -> Any:
    return _ManagedField(
        binding=True,
        default=default,
        default_factory=default_factory,
    )


class _BindingMapProxy(MutableMapping[Any, Any]):
    __slots__ = ("_owner", "_field_name")

    def __init__(self, owner: LifecycleContext, field_name: str) -> None:
        self._owner = owner
        self._field_name = field_name

    def __getitem__(self, key: Any) -> Any:
        return self._mapping()[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        existing = self._mapping()
        if key in existing and existing[key] is value:
            return
        working = self._owner._ensure_working()
        next_mapping = dict(getattr(working, self._field_name))
        next_mapping[key] = value
        setattr(working, self._field_name, next_mapping)

    def __delitem__(self, key: Any) -> None:
        existing = self._mapping()
        if key not in existing:
            raise KeyError(key)
        working = self._owner._ensure_working()
        next_mapping = dict(getattr(working, self._field_name))
        del next_mapping[key]
        setattr(working, self._field_name, next_mapping)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._mapping())

    def __len__(self) -> int:
        return len(self._mapping())

    def _mapping(self) -> Mapping[Any, Any]:
        return getattr(self._owner.view_state, self._field_name)


class LifecycleContext:
    """Base class for declarative lifecycle-managed contexts.

    Decorated subclasses act as their own lifecycle manager. Property writes
    lazily create a thawed working snapshot. `commit()` freezes the working
    state and accepts newly added bindings; `rollback()` discards the working
    state and closes newly introduced bindings as uncommitted.
    """

    __managed_fields__: dict[str, _ManagedField]
    __state_type__: type[Any]
    __thawed_state_type__: type[Any]

    def __init__(self, **values: Any) -> None:
        state_type = getattr(type(self), "__state_type__", None)
        if state_type is None:
            raise TypeError("LifecycleContext subclasses must be decorated with @managed_context")
        self.transaction_manager = values.pop("transaction_manager", None)
        self._current = state_type(**self._normalize_initial_values(values))
        self._working: Any | None = None
        self._working_tx_id: int | None = None
        self._active = False
        self._closed = False

    def accepted(self) -> None:
        """Allow nested lifecycle contexts to participate as bindings."""

    @property
    def current_state(self) -> Any:
        return self._current

    @property
    def working_state(self) -> Any | None:
        return self._working

    @property
    def view_state(self) -> Any:
        return self._working if self._working is not None else self._current

    @property
    def is_active(self) -> bool:
        return self._active or self._working is not None

    @property
    def is_closed(self) -> bool:
        return self._closed

    def begin(self) -> LifecycleContext:
        self._require_not_closed()
        self._active = True
        return self

    open = begin

    def commit(self) -> Any:
        self._require_not_closed()
        if self._working is None:
            self._active = False
            return self._current

        transaction_manager = self.transaction_manager
        if transaction_manager is not None and self._working_tx_id is not None:
            transaction_manager.drop(self, self._working_tx_id)
        return self._commit_working()

    def rollback(self) -> Any:
        if self._closed:
            return self._current
        transaction_manager = self.transaction_manager
        if transaction_manager is not None and self._working_tx_id is not None:
            transaction_manager.drop(self, self._working_tx_id)
        if self._working is not None:
            self._rollback_new_bindings(self._current, self._working)
            self.after_rollback(self._current)
        self._working = None
        self._working_tx_id = None
        self._active = False
        return self._current

    def close(self, *, was_committed: bool = True) -> None:
        del was_committed
        if self._closed:
            return
        if self._working is not None:
            transaction_manager = self.transaction_manager
            if transaction_manager is not None and self._working_tx_id is not None:
                transaction_manager.drop(self, self._working_tx_id)
            self._rollback_new_bindings(self._current, self._working)
            self._working = None
            self._working_tx_id = None
        self.before_close(self._current)
        self._close_state_bindings(self._current, was_committed=True)
        self._active = False
        self._closed = True
        self.after_close()

    def before_commit(self, current_state: Any, working_state: Any) -> None:
        del current_state, working_state

    def after_commit(self, previous_state: Any, current_state: Any) -> None:
        del previous_state, current_state

    def after_rollback(self, current_state: Any) -> None:
        del current_state

    def before_close(self, current_state: Any) -> None:
        del current_state

    def after_close(self) -> None:
        return None

    def _require_not_closed(self) -> None:
        if self._closed:
            raise RuntimeError(f"{type(self).__name__} is closed")

    def _ensure_working(self) -> Any:
        self._require_not_closed()
        if self._working is None:
            self._working = self._current.to_thawed()
            transaction_manager = self.transaction_manager
            if transaction_manager is not None and transaction_manager.active_transaction is not None:
                self._working_tx_id = transaction_manager.enlist(self)
            self._active = True
        return self._working

    def _commit_working(self) -> Any:
        current = self._current
        working = self._working
        if working is None:
            self._active = False
            return current

        self.before_commit(current, working)
        next_current = working.to_frozen()

        if self._states_equivalent(current, next_current):
            self._working = None
            self._working_tx_id = None
            self._active = False
            return current

        self._accept_commit_bindings(current, next_current)
        self._current = next_current
        self._working = None
        self._working_tx_id = None
        self._active = False
        self.after_commit(current, next_current)
        return next_current

    def _commit_transaction(self, tx_id: int) -> Any:
        if self._working_tx_id != tx_id:
            return self._current
        return self._commit_working()

    def _rollback_transaction(self, tx_id: int) -> Any:
        if self._working_tx_id != tx_id:
            return self._current
        return self.rollback()

    def _get_field_value(self, field_name: str) -> Any:
        return getattr(self.view_state, field_name)

    def _set_field_value(self, field_name: str, value: Any, *, binding: bool) -> None:
        current = getattr(self.view_state, field_name)
        if binding:
            if current is value:
                return
        elif current == value:
            return
        working = self._ensure_working()
        setattr(working, field_name, value)

    def _set_binding_map(self, field_name: str, value: Mapping[Any, Any]) -> None:
        next_mapping = dict(value)
        current = getattr(self.view_state, field_name)
        if _binding_maps_equivalent(current, next_mapping):
            return
        working = self._ensure_working()
        setattr(working, field_name, next_mapping)

    def _normalize_initial_values(self, values: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(values)
        for name, managed_field in type(self).__managed_fields__.items():
            if not (managed_field.binding and managed_field.mapping):
                continue
            if name in normalized:
                normalized[name] = dict(normalized[name])
        return normalized

    def _states_equivalent(self, left: Any, right: Any) -> bool:
        for name, managed_field in type(self).__managed_fields__.items():
            left_value = getattr(left, name)
            right_value = getattr(right, name)
            if managed_field.binding and managed_field.mapping:
                if not _binding_maps_equivalent(left_value, right_value):
                    return False
                continue
            if managed_field.binding:
                if left_value is not right_value:
                    return False
                continue
            if left_value != right_value:
                return False
        return True

    def _accept_commit_bindings(self, previous: Any, current: Any) -> None:
        for name, managed_field in type(self).__managed_fields__.items():
            if not managed_field.binding:
                continue
            previous_value = getattr(previous, name)
            current_value = getattr(current, name)
            if managed_field.mapping:
                self._accept_commit_binding_map(previous_value, current_value)
                continue
            if previous_value is current_value:
                continue
            if current_value is not None:
                _binding_accept(current_value)
            if previous_value is not None:
                _binding_close(previous_value, was_committed=True)

    def _rollback_new_bindings(self, current: Any, working: Any) -> None:
        for name, managed_field in type(self).__managed_fields__.items():
            if not managed_field.binding:
                continue
            current_value = getattr(current, name)
            working_value = getattr(working, name)
            if managed_field.mapping:
                self._rollback_binding_map(current_value, working_value)
                continue
            if current_value is working_value or working_value is None:
                continue
            _binding_close(working_value, was_committed=False)

    def _close_state_bindings(self, state: Any, *, was_committed: bool) -> None:
        for name, managed_field in type(self).__managed_fields__.items():
            if not managed_field.binding:
                continue
            value = getattr(state, name)
            if managed_field.mapping:
                for binding in value.values():
                    if binding is not None:
                        _binding_close(binding, was_committed=was_committed)
                continue
            if value is not None:
                _binding_close(value, was_committed=was_committed)

    def _accept_commit_binding_map(
        self,
        previous: Mapping[Any, Any],
        current: Mapping[Any, Any],
    ) -> None:
        all_keys = set(previous) | set(current)
        for key in all_keys:
            previous_value = previous.get(key, _SENTINEL)
            current_value = current.get(key, _SENTINEL)
            if previous_value is current_value:
                continue
            if current_value is not _SENTINEL and current_value is not None:
                _binding_accept(current_value)
            if previous_value is not _SENTINEL and previous_value is not None:
                _binding_close(previous_value, was_committed=True)

    def _rollback_binding_map(
        self,
        current: Mapping[Any, Any],
        working: Mapping[Any, Any],
    ) -> None:
        all_keys = set(current) | set(working)
        for key in all_keys:
            current_value = current.get(key, _SENTINEL)
            working_value = working.get(key, _SENTINEL)
            if current_value is working_value:
                continue
            if working_value is not _SENTINEL and working_value is not None:
                _binding_close(working_value, was_committed=False)


def managed_context(cls: type[LifecycleContext]) -> type[LifecycleContext]:
    if not issubclass(cls, LifecycleContext):
        raise TypeError("@managed_context requires a LifecycleContext subclass")
    if "__init__" in cls.__dict__:
        raise TypeError("@managed_context classes must not define __init__")

    base_fields: dict[str, _ManagedField] = {}
    direct_managed_bases = [
        base
        for base in cls.__bases__
        if issubclass(base, LifecycleContext) and hasattr(base, "__managed_fields__")
    ]
    for base in direct_managed_bases:
        base_fields.update(base.__managed_fields__)

    annotations = dict(getattr(cls, "__annotations__", {}))
    resolved_hints = _resolve_hints(cls)
    own_fields: dict[str, _ManagedField] = {}
    for name, annotation in annotations.items():
        candidate = cls.__dict__.get(name, _SENTINEL)
        if isinstance(candidate, _ManagedField):
            if name in base_fields:
                raise TypeError(f"managed field {name!r} cannot override a base managed field")
            candidate.annotation = resolved_hints.get(name, annotation)
            candidate.mapping = candidate.binding and _annotation_is_mapping(candidate.annotation)
            own_fields[name] = candidate
            continue
        if name.startswith("_"):
            continue
        raise TypeError(
            f"annotated lifecycle field {name!r} must use managed(...) or managed_binding(...)"
        )

    state_type, thawed_state_type = _build_state_pair(
        owner=cls,
        managed_bases=direct_managed_bases,
        fields=own_fields,
    )

    cls.__managed_fields__ = {**base_fields, **own_fields}
    cls.__state_type__ = state_type
    cls.__thawed_state_type__ = thawed_state_type
    cls.State = state_type
    cls.ThawedState = thawed_state_type
    return cls


def _resolve_hints(cls: type[Any]) -> dict[str, Any]:
    try:
        return get_type_hints(cls, include_extras=True)
    except (AttributeError, NameError, TypeError):
        return dict(getattr(cls, "__annotations__", {}))


def _annotation_is_mapping(annotation: Any) -> bool:
    origin = get_origin(annotation)
    if origin is None:
        return annotation in _MAPPING_ORIGINS
    return origin in _MAPPING_ORIGINS


def _binding_maps_equivalent(left: Mapping[Any, Any], right: Mapping[Any, Any]) -> bool:
    if set(left) != set(right):
        return False
    return all(left[key] is right[key] for key in left)


def _binding_accept(binding: Any) -> None:
    accepted = getattr(binding, "accepted", None)
    if not callable(accepted):
        raise TypeError(f"{type(binding).__name__} does not provide accepted()")
    accepted()


def _binding_close(binding: Any, *, was_committed: bool) -> None:
    close = getattr(binding, "close", None)
    if not callable(close):
        raise TypeError(
            f"{type(binding).__name__} does not provide close(was_committed=...)"
        )
    close(was_committed=was_committed)


def _build_state_pair(
    *,
    owner: type[LifecycleContext],
    managed_bases: list[type[LifecycleContext]],
    fields: dict[str, _ManagedField],
) -> tuple[type[Any], type[Any]]:
    module = sys.modules[owner.__module__]
    state_name = f"_{owner.__name__}State"
    thawed_name = f"_{owner.__name__}ThawedState"
    state_bases = tuple(base.__state_type__ for base in managed_bases)

    state_namespace: dict[str, Any] = {
        "__module__": owner.__module__,
        "__annotations__": {},
    }
    for name, managed_field in fields.items():
        state_namespace["__annotations__"][name] = managed_field.annotation
        if managed_field.default is not MISSING:
            state_namespace[name] = managed_field.default
        elif managed_field.default_factory is not MISSING:
            state_namespace[name] = field(default_factory=managed_field.default_factory)

    raw_state = types.new_class(
        state_name,
        state_bases or (),
        exec_body=lambda ns: ns.update(state_namespace),
    )
    state_type = thawable_dataclass(
        thawed_type=thawed_name,
        freeze_params=False,
        list_params=False,
        hint_resolution=HintResolutionMode.STRICT_MODULE,
    )(raw_state)
    setattr(module, state_name, state_type)

    raw_thawed = types.new_class(
        thawed_name,
        (),
        exec_body=lambda ns: ns.update({"__module__": owner.__module__}),
    )
    thawed_type = thawed_dataclass(
        frozen_type=state_type,
        hint_resolution=HintResolutionMode.STRICT_MODULE,
    )(raw_thawed)
    setattr(module, thawed_name, thawed_type)
    setattr(state_type, "_paired_type", thawed_type)
    return state_type, thawed_type


__all__ = [
    "LifecycleBinding",
    "LifecycleTransaction",
    "LifecycleContext",
    "TransactionManager",
    "managed",
    "managed_binding",
    "managed_context",
]
