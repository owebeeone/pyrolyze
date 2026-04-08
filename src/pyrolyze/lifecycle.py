from __future__ import annotations

"""Record-based declarative lifecycle primitives.

This module is the restarted lifecycle core. It does not depend on
``pyrolyze.freezable`` and it does not use whole-object frozen/thawed state
clones as its primary representation.

The core ideas are:

- field specs are compiled at class-decoration time
- field access goes through minimal descriptors
- contexts hold a committed ``current`` record plus a sparse ``working`` record
- ordinary reads see ``current`` until a working overlay exists, then see the
  overlay
- transaction managers enlist only contexts that actually promote to working

Only the restarted Phase 1.1/1.2 surface is implemented here:

- ``lifecycle_field``
- ``managed_context``
- ``LifecycleContext``
- ``TransactionManager``

Later phases should layer ``const()``, ``static()``, ``managed()``,
``binding()``, and the other higher-level field kinds on top of this engine.
"""

import copy
from collections.abc import Callable
from dataclasses import MISSING, dataclass, field
import inspect
import types
import typing
from typing import Any

from pyrolyze.type_annotations import is_annotation_narrower_or_equal

_SENTINEL = object()


@dataclass(slots=True)
class Record:
    values: dict[str, Any] = field(default_factory=dict)
    field_state: dict[str, Any] = field(default_factory=dict)


class _RecordSnapshot:
    __slots__ = ("_values",)

    def __init__(self, values: dict[str, Any]) -> None:
        self._values = dict(values)

    def __getattr__(self, name: str) -> Any:
        try:
            return self._values[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


def _view_init(self, *, _state: LifecycleContextState, _owner: _ManagedContextBase) -> None:
    object.__setattr__(self, "_state", _state)
    object.__setattr__(self, "_owner", _owner)


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


FieldStateFactory = Callable[[], Any]
StateCopyHelper = Callable[[Any], Any]
FieldGetter = Callable[["LifecycleContextState", str], Any]
FieldSetter = Callable[["LifecycleContextState", str, Any], None]
FieldHook = Callable[["LifecycleContextState", str], None]


@dataclass(slots=True)
class FieldSpec:
    name: str
    annotation: Any
    compare: str
    default: Any = MISSING
    default_factory: Callable[[], Any] | object = MISSING
    state_factory: FieldStateFactory | None = None
    state_copy: StateCopyHelper | None = None

    def default_value(self) -> Any:
        if self.default is not MISSING:
            return self.default
        if self.default_factory is not MISSING:
            return self.default_factory()
        raise TypeError(f"missing required lifecycle field {self.name!r}")


class LifecycleField:
    __slots__ = ("compare", "default", "default_factory", "name", "state_copy", "state_factory")

    def __init__(
        self,
        *,
        compare: str = "value",
        default: Any = MISSING,
        default_factory: Callable[[], Any] | object = MISSING,
        state_factory: Callable[[], Any] | None = None,
        state_copy: StateCopyHelper | None = None,
    ) -> None:
        if compare not in {"value", "identity"}:
            raise TypeError(f"unsupported compare mode {compare!r}")
        if default is not MISSING and default_factory is not MISSING:
            raise TypeError("lifecycle fields cannot define both default and default_factory")
        self.compare = compare
        self.default = default
        self.default_factory = default_factory
        self.state_factory = state_factory
        self.state_copy = state_copy or copy.copy
        self.name: str | None = None

    def __set_name__(self, owner: type[LifecycleContext], name: str) -> None:
        self.name = name

    def __get__(self, instance: LifecycleContext | None, owner: type[LifecycleContext]) -> Any:
        if instance is None:
            return self
        return instance.__get_field__(self.name_or_error())

    def __set__(self, instance: LifecycleContext, value: Any) -> None:
        instance.__set_field__(self.name_or_error(), value)

    def build_spec(self, annotation: Any) -> FieldSpec:
        return FieldSpec(
            name=self.name_or_error(),
            annotation=annotation,
            compare=self.compare,
            default=self.default,
            default_factory=self.default_factory,
            state_factory=self.state_factory,
            state_copy=self.state_copy,
        )

    def name_or_error(self) -> str:
        if self.name is None:
            raise RuntimeError("lifecycle field name was not initialized")
        return self.name


def lifecycle_field(
    *,
    compare: str = "value",
    default: Any = MISSING,
    default_factory: Callable[[], Any] | object = MISSING,
    state_factory: Callable[[], Any] | None = None,
    state_copy: StateCopyHelper | None = None,
) -> Any:
    return LifecycleField(
        compare=compare,
        default=default,
        default_factory=default_factory,
        state_factory=state_factory,
        state_copy=state_copy,
    )


def _get_default_overlay_field(state: LifecycleContextState, name: str) -> Any:
    working = state.working_record
    if working is not None and name in working.values:
        return working.values[name]
    return state.current_record.values[name]


def _get_current_field(state: LifecycleContextState, name: str) -> Any:
    return state.current_record.values[name]


def _get_working_overlay_field(state: LifecycleContextState, name: str) -> Any:
    working = state.working_record
    if working is not None and name in working.values:
        return working.values[name]
    return state.current_record.values[name]


def _set_default_value_field(state: LifecycleContextState, name: str, value: Any) -> None:
    if type(state).__class_ftable_get_default__[name](state, name) == value:
        return
    state.ensure_working_record().values[name] = value


def _set_default_identity_field(state: LifecycleContextState, name: str, value: Any) -> None:
    if type(state).__class_ftable_get_default__[name](state, name) is value:
        return
    state.ensure_working_record().values[name] = value


def _set_working_value_field(state: LifecycleContextState, name: str, value: Any) -> None:
    if type(state).__class_ftable_get_working__[name](state, name) == value:
        return
    working = state.ensure_working_record()
    working.values[name] = value


def _set_working_identity_field(state: LifecycleContextState, name: str, value: Any) -> None:
    if type(state).__class_ftable_get_working__[name](state, name) is value:
        return
    working = state.ensure_working_record()
    working.values[name] = value


def _commit_overlay_field(state: LifecycleContextState, name: str) -> None:
    working = state.working_record
    if working is None:
        return
    if name in working.values:
        state.current_record.values[name] = working.values[name]
    if name in working.field_state:
        state.current_record.field_state[name] = working.field_state[name]


def _rollback_overlay_field(state: LifecycleContextState, name: str) -> None:
    del state, name


def _close_noop(state: LifecycleContextState, name: str) -> None:
    del state, name


class LifecycleContextState:
    __field_specs__: dict[str, FieldSpec] = {}
    __field_names__: tuple[str, ...] = ()
    __class_ftable_get_default__: dict[str, FieldGetter] = {}
    __class_ftable_get_current__: dict[str, FieldGetter] = {}
    __class_ftable_get_working__: dict[str, FieldGetter] = {}
    __class_ftable_set_default__: dict[str, FieldSetter] = {}
    __class_ftable_set_working__: dict[str, FieldSetter] = {}
    __class_ftable_commit_field__: dict[str, FieldHook] = {}
    __class_ftable_rollback_field__: dict[str, FieldHook] = {}
    __class_ftable_close_field__: dict[str, FieldHook] = {}
    __class_ftable_state_factory__: dict[str, FieldStateFactory | None] = {}
    __class_ftable_state_copy__: dict[str, StateCopyHelper | None] = {}

    __slots__ = (
        "owner",
        "transaction_manager",
        "current_record",
        "working_record",
        "working_tx_id",
        "unmanaged_store",
        "closed",
        "current_view",
        "working_view",
    )

    def __init__(
        self,
        owner: LifecycleContext,
        *,
        transaction_manager: TransactionManager | None,
        values: dict[str, Any],
    ) -> None:
        self.owner = owner
        self.transaction_manager = transaction_manager
        self.current_record = Record()
        self.working_record: Record | None = None
        self.working_tx_id: int | None = None
        self.unmanaged_store: dict[str, Any] = {}
        self.closed = False
        self.current_view = type(owner).__current_view_cls__(_state=self, _owner=owner)
        self.working_view = type(owner).__working_view_cls__(_state=self, _owner=owner)

        for name, spec in type(self).__field_specs__.items():
            if name in values:
                self.current_record.values[name] = values.pop(name)
            else:
                self.current_record.values[name] = spec.default_value()

        if values:
            unexpected = ", ".join(sorted(values))
            raise TypeError(f"unexpected lifecycle constructor fields: {unexpected}")

    def get_field(self, name: str) -> Any:
        return type(self).__class_ftable_get_default__[name](self, name)

    def set_field(self, name: str, value: Any) -> None:
        self.require_active_transaction()
        type(self).__class_ftable_set_default__[name](self, name, value)

    def get_current_field(self, name: str) -> Any:
        return type(self).__class_ftable_get_current__[name](self, name)

    def get_working_field(self, name: str) -> Any:
        return type(self).__class_ftable_get_working__[name](self, name)

    def set_working_field(self, name: str, value: Any) -> None:
        self.require_active_transaction()
        type(self).__class_ftable_set_working__[name](self, name, value)

    def get_field_state(self, name: str) -> Any:
        working = self.working_record
        if working is not None and name in working.field_state:
            return working.field_state[name]
        return self.get_current_field_state(name)

    def get_current_field_state(self, name: str) -> Any:
        state_factory = type(self).__class_ftable_state_factory__[name]
        if state_factory is None:
            raise RuntimeError(f"field {name!r} does not define runtime state")
        if name not in self.current_record.field_state:
            self.current_record.field_state[name] = state_factory()
        return self.current_record.field_state[name]

    def ensure_working_field_state(self, name: str) -> Any:
        state_factory = type(self).__class_ftable_state_factory__[name]
        if state_factory is None:
            raise RuntimeError(f"field {name!r} does not define runtime state")
        working = self.ensure_working_record()
        if name not in working.field_state:
            current_state = self.get_current_field_state(name)
            state_copy = type(self).__class_ftable_state_copy__[name] or copy.copy
            working.field_state[name] = state_copy(current_state)
        return working.field_state[name]

    def ensure_working_record(self) -> Record:
        working = self.working_record
        if working is not None:
            return working

        self.require_active_transaction()

        working = Record()
        self.working_record = working
        self.working_tx_id = self.transaction_manager.enlist(self.owner)
        return working

    def require_active_transaction(self) -> None:
        transaction = self.transaction_manager.active_transaction if self.transaction_manager is not None else None
        if transaction is None:
            raise RuntimeError("writes require an active lifecycle transaction")

    def snapshot_current(self) -> _RecordSnapshot:
        return _RecordSnapshot(self.current_record.values)

    def commit(self) -> _ManagedContextBase:
        if self.working_record is None:
            return self.owner.current

        if self.transaction_manager is not None and self.working_tx_id is not None:
            self.transaction_manager.drop(self.owner, self.working_tx_id)

        previous = self.snapshot_current()
        self.owner.before_commit(self.current_view, self.working_view)
        for name in type(self).__field_names__:
            type(self).__class_ftable_commit_field__[name](self, name)
        self.working_record = None
        self.working_tx_id = None
        self.owner.after_commit(previous, self.snapshot_current())
        return self.owner.current

    def rollback(self) -> _ManagedContextBase:
        if self.working_record is None:
            return self.owner.current

        if self.transaction_manager is not None and self.working_tx_id is not None:
            self.transaction_manager.drop(self.owner, self.working_tx_id)

        for name in type(self).__field_names__:
            type(self).__class_ftable_rollback_field__[name](self, name)
        self.working_record = None
        self.working_tx_id = None
        self.owner.after_rollback(self.snapshot_current())
        return self.owner.current

    def commit_transaction(self, tx_id: int) -> _ManagedContextBase:
        if self.working_tx_id != tx_id:
            return self.owner.current
        return self.commit()

    def rollback_transaction(self, tx_id: int) -> _ManagedContextBase:
        if self.working_tx_id != tx_id:
            return self.owner.current
        return self.rollback()

    def close(self, *, was_committed: bool = True) -> None:
        del was_committed
        if self.closed:
            return
        if self.working_record is not None:
            self.rollback()
        for name in type(self).__field_names__:
            type(self).__class_ftable_close_field__[name](self, name)
        self.closed = True


class _ManagedContextBase:
    __state_cls__: type[LifecycleContextState] = LifecycleContextState
    __current_view_cls__: type[_ManagedContextBase]
    __working_view_cls__: type[_ManagedContextBase]
    __view_mode__ = "default"

    def __init__(self, **values: Any) -> None:
        transaction_manager = values.pop("transaction_manager", None)
        object.__setattr__(
            self,
            "_state",
            type(self).__state_cls__(self, transaction_manager=transaction_manager, values=values),
        )

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        store = self._state.unmanaged_store
        try:
            return store[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        if name in type(self).__state_cls__.__field_specs__:
            self.__set_field__(name, value)
            return
        descriptor = inspect.getattr_static(type(self), name, _SENTINEL)
        if descriptor is not _SENTINEL and hasattr(descriptor, "__set__"):
            object.__setattr__(self, name, value)
            return
        self._state.unmanaged_store[name] = value

    @property
    def state(self) -> LifecycleContextState:
        return self._state

    @property
    def _transaction_manager(self) -> TransactionManager | None:
        return self._state.transaction_manager

    @property
    def _current_record(self) -> Record:
        return self._state.current_record

    @property
    def _working_record(self) -> Record | None:
        return self._state.working_record

    @property
    def _working_tx_id(self) -> int | None:
        return self._state.working_tx_id

    @property
    def _closed(self) -> bool:
        return self._state.closed

    @property
    def current(self) -> _ManagedContextBase:
        return self._state.current_view

    @property
    def working(self) -> _ManagedContextBase:
        return self._state.working_view

    @property
    def _default_record(self) -> _ManagedContextBase:
        return self

    def accepted(self) -> None:
        return None

    def close(self, *, was_committed: bool = True) -> None:
        self._state.close(was_committed=was_committed)

    def before_commit(self, current: object, working: object) -> None:
        del current, working

    def after_commit(self, previous: object, current: object) -> None:
        del previous, current

    def after_rollback(self, current: object) -> None:
        del current

    def __get_field__(self, name: str) -> Any:
        mode = type(self).__view_mode__
        if mode == "current":
            return self._state.get_current_field(name)
        if mode == "working":
            return self._state.get_working_field(name)
        return self._state.get_field(name)

    def __set_field__(self, name: str, value: Any) -> None:
        mode = type(self).__view_mode__
        if mode == "current":
            raise AttributeError("current record is read-only")
        if mode == "working":
            self._state.set_working_field(name, value)
            return
        self._state.set_field(name, value)

    def __get_current_field__(self, name: str) -> Any:
        return self._state.get_current_field(name)

    def __get_working_field__(self, name: str) -> Any:
        return self._state.get_working_field(name)

    def __set_working_field__(self, name: str, value: Any) -> None:
        self._state.set_working_field(name, value)

    def __get_field_state__(self, name: str) -> Any:
        return self._state.get_field_state(name)

    def __get_current_field_state__(self, name: str) -> Any:
        return self._state.get_current_field_state(name)

    def __ensure_working_field_state__(self, name: str) -> Any:
        return self._state.ensure_working_field_state(name)

    def __ensure_working_record__(self) -> Record:
        return self._state.ensure_working_record()

    def _snapshot_current(self) -> _RecordSnapshot:
        return self._state.snapshot_current()

    def commit(self) -> _ManagedContextBase:
        return self._state.commit()

    def rollback(self) -> _ManagedContextBase:
        return self._state.rollback()

    def _commit_transaction(self, tx_id: int) -> _ManagedContextBase:
        return self._state.commit_transaction(tx_id)

    def _rollback_transaction(self, tx_id: int) -> _ManagedContextBase:
        return self._state.rollback_transaction(tx_id)


LifecycleContext = _ManagedContextBase


def _build_class_tables(
    specs: dict[str, FieldSpec],
) -> dict[str, dict[str, Callable[..., Any]]]:
    get_default: dict[str, FieldGetter] = {}
    get_current: dict[str, FieldGetter] = {}
    get_working: dict[str, FieldGetter] = {}
    set_default: dict[str, FieldSetter] = {}
    set_working: dict[str, FieldSetter] = {}
    commit_field: dict[str, FieldHook] = {}
    rollback_field: dict[str, FieldHook] = {}
    close_field: dict[str, FieldHook] = {}
    state_factory: dict[str, FieldStateFactory | None] = {}
    state_copy: dict[str, StateCopyHelper | None] = {}

    for name, spec in specs.items():
        get_default[name] = _get_default_overlay_field
        get_current[name] = _get_current_field
        get_working[name] = _get_working_overlay_field
        if spec.compare == "identity":
            set_default[name] = _set_default_identity_field
            set_working[name] = _set_working_identity_field
        else:
            set_default[name] = _set_default_value_field
            set_working[name] = _set_working_value_field
        commit_field[name] = _commit_overlay_field
        rollback_field[name] = _rollback_overlay_field
        close_field[name] = _close_noop
        state_factory[name] = spec.state_factory
        state_copy[name] = spec.state_copy

    return {
        "__class_ftable_get_default__": get_default,
        "__class_ftable_get_current__": get_current,
        "__class_ftable_get_working__": get_working,
        "__class_ftable_set_default__": set_default,
        "__class_ftable_set_working__": set_working,
        "__class_ftable_commit_field__": commit_field,
        "__class_ftable_rollback_field__": rollback_field,
        "__class_ftable_close_field__": close_field,
        "__class_ftable_state_factory__": state_factory,
        "__class_ftable_state_copy__": state_copy,
    }


def _collect_own_field_specs(cls: type[Any]) -> dict[str, FieldSpec]:
    own_annotation_names = dict(getattr(cls, "__annotations__", {}))
    try:
        resolved_annotations = typing.get_type_hints(cls, include_extras=True)
    except (AttributeError, NameError, TypeError):
        resolved_annotations = own_annotation_names
    annotations = {
        name: resolved_annotations.get(name, annotation)
        for name, annotation in own_annotation_names.items()
    }
    own_specs: dict[str, FieldSpec] = {}
    for name, annotation in annotations.items():
        candidate = cls.__dict__.get(name, _SENTINEL)
        if isinstance(candidate, LifecycleField):
            own_specs[name] = candidate.build_spec(annotation)
            continue
        if name.startswith("_"):
            continue
        raise TypeError(
            f"annotated lifecycle field {name!r} must use lifecycle_field(...)"
        )
    return own_specs


def _merge_field_specs(base: FieldSpec, derived: FieldSpec) -> FieldSpec:
    if base.compare != derived.compare:
        raise TypeError(f"incompatible lifecycle field override for {base.name!r}")
    if base.state_factory != derived.state_factory and derived.state_factory is not None:
        raise TypeError(f"incompatible lifecycle field override for {base.name!r}")
    if base.state_copy != derived.state_copy and derived.state_copy != copy.copy:
        raise TypeError(f"incompatible lifecycle field override for {base.name!r}")
    if not is_annotation_narrower_or_equal(derived.annotation, base.annotation):
        raise TypeError(f"incompatible lifecycle field override for {base.name!r}")

    if derived.default is not MISSING:
        default = derived.default
        default_factory = MISSING
    elif derived.default_factory is not MISSING:
        default = MISSING
        default_factory = derived.default_factory
    else:
        default = base.default
        default_factory = base.default_factory
    state_factory = derived.state_factory if derived.state_factory is not None else base.state_factory
    state_copy = derived.state_copy if derived.state_copy != copy.copy else base.state_copy

    return FieldSpec(
        name=base.name,
        annotation=derived.annotation,
        compare=base.compare,
        default=default,
        default_factory=default_factory,
        state_factory=state_factory,
        state_copy=state_copy,
    )


def _merge_field_specs_from_mro(
    cls: type[Any],
    *,
    attr_name: str,
    own_items: dict[str, FieldSpec],
) -> dict[str, FieldSpec]:
    merged: dict[str, FieldSpec] = {}
    for mro_cls in reversed(cls.__mro__):
        if mro_cls in {object, _ManagedContextBase}:
            continue
        source = own_items if mro_cls is cls else getattr(mro_cls, attr_name, None)
        if not source:
            continue
        for name, value in source.items():
            if name in merged:
                merged[name] = _merge_field_specs(merged[name], value)
            else:
                merged[name] = value
    return merged


def _build_view_class(
    name: str,
    base_cls: type[_ManagedContextBase],
    *,
    mode: str,
) -> type[_ManagedContextBase]:
    def exec_body(namespace: dict[str, Any]) -> None:
        namespace["__module__"] = base_cls.__module__
        namespace["__view_mode__"] = mode
        namespace["__init__"] = _view_init

    view_cls = types.new_class(name, (base_cls,), exec_body=exec_body)
    view_cls.__qualname__ = f"{base_cls.__qualname__}.{name}"
    return view_cls


def managed_context(cls: type[LifecycleContext]) -> type[LifecycleContext]:
    wrapped: type[LifecycleContext]
    if issubclass(cls, _ManagedContextBase):
        wrapped = cls
    else:
        def exec_body(namespace: dict[str, Any]) -> None:
            namespace["__module__"] = cls.__module__
            namespace["__doc__"] = cls.__doc__

        wrapped = types.new_class(
            cls.__name__,
            (cls, _ManagedContextBase),
            exec_body=exec_body,
        )
        wrapped.__qualname__ = cls.__qualname__

    own_specs = _collect_own_field_specs(cls)
    wrapped.__managed_own_field_specs__ = own_specs

    base_state_cls = LifecycleContextState
    for base in wrapped.__mro__[1:]:
        if hasattr(base, "__state_cls__"):
            base_state_cls = base.__state_cls__
            break

    merged_specs = _merge_field_specs_from_mro(
        wrapped,
        attr_name="__managed_own_field_specs__",
        own_items=own_specs,
    )

    state_name = f"{wrapped.__name__}_State"
    state_namespace = {
        "__module__": wrapped.__module__,
        "__field_specs__": merged_specs,
    }
    state_cls = type(state_name, (base_state_cls,), state_namespace)
    state_cls.__field_names__ = tuple(state_cls.__field_specs__)
    for table_name, table in _build_class_tables(state_cls.__field_specs__).items():
        setattr(state_cls, table_name, table)
    wrapped.__state_cls__ = state_cls
    wrapped.__current_view_cls__ = _build_view_class(
        f"{wrapped.__name__}_CurrentView",
        wrapped,
        mode="current",
    )
    wrapped.__working_view_cls__ = _build_view_class(
        f"{wrapped.__name__}_WorkingView",
        wrapped,
        mode="working",
    )
    return wrapped


__all__ = [
    "FieldSpec",
    "LifecycleContext",
    "LifecycleTransaction",
    "Record",
    "TransactionManager",
    "lifecycle_field",
    "managed_context",
]
