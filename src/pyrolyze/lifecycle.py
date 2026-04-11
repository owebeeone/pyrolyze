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

Only the restarted Phase 1.1/1.10 surface is implemented here:

- ``lifecycle_field``
- ``const``
- ``static``
- ``managed``
- ``binding``
- ``owned``
- ``transient``
- ``local_store``
- ``derived``
- ``commit_order_key``
- ``commit_validator``
- ``on_before_commit``
- ``on_after_commit``
- ``on_after_rollback``
- ``managed_context``
- ``LifecycleContext``
- ``TransactionManager``
"""

import copy
import functools
from abc import ABC, abstractmethod
from collections.abc import Mapping
from collections.abc import Callable
from collections.abc import Hashable
from dataclasses import MISSING, dataclass, field
import inspect
import types
import typing
from typing import Any

from pyrolyze.type_annotations import is_annotation_narrower_or_equal

_SENTINEL = object()
DEFAULT_TRANSACTION: Hashable = "default_transaction"


class LifecycleValidatorReturnedFalse(RuntimeError):
    """Raised when a context's ``validate_commit`` hook returns False (not an exception)."""

    def __init__(self, context: "LifecycleContext") -> None:
        self.context = context
        super().__init__(
            f"validate_commit returned False for {type(context).__qualname__!r}",
        )


@dataclass(slots=True)
class Record:
    values: dict[str, Any] = field(default_factory=dict)
    field_state: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class _LifecycleTxState:
    working_record: Record | None = None
    working_tx_id: int | None = None


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
    tx_group: Hashable = DEFAULT_TRANSACTION
    dirty_contexts: dict[int, LifecycleContext] = field(default_factory=dict)
    validator_contexts: dict[int, LifecycleContext] = field(default_factory=dict)
    _scope_commit: Callable[[], Any] | None = field(default=None, init=False, repr=False, compare=False)
    _scope_rollback: Callable[[], Any] | None = field(default=None, init=False, repr=False, compare=False)

    def commit_order(self) -> tuple[LifecycleContext, ...]:
        contexts = list(self.dirty_contexts.values())
        contexts.sort(key=lambda context: context.commit_order_key_for(self.tx_group), reverse=True)
        return tuple(contexts)

    def rollback_dirty(self) -> None:
        for ctx in list(self.dirty_contexts.values()):
            ctx._rollback_transaction(self.tx_id, self.tx_group)

    def validate_commit(self) -> None:
        failures: list[BaseException] = []
        for context in self.validator_contexts.values():
            try:
                ok = context.validate_commit_for(self.tx_group)
            except BaseException as exc:
                failures.append(exc)
                continue
            if not ok:
                failures.append(LifecycleValidatorReturnedFalse(context))
        if failures:
            raise ExceptionGroup("lifecycle commit validation failed", failures)

    def apply_commits(self) -> None:
        for context in self.commit_order():
            context._commit_transaction(self.tx_id, self.tx_group)

    def bind_scope(
        self,
        *,
        commit: Callable[[], Any],
        rollback: Callable[[], Any],
    ) -> "LifecycleTransaction":
        self._scope_commit = commit
        self._scope_rollback = rollback
        return self

    def __enter__(self) -> "LifecycleTransaction":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> bool:
        del exc, tb
        if self._scope_commit is None or self._scope_rollback is None:
            raise RuntimeError("lifecycle transaction scope is not bound")
        if exc_type is None:
            self._scope_commit()
        else:
            self._scope_rollback()
        return False


@dataclass(slots=True)
class GroupTransactionManager:
    tx_group: Hashable = DEFAULT_TRANSACTION
    _next_tx_id: int = field(default=1, init=False, repr=False)
    active_transaction: LifecycleTransaction | None = field(default=None, init=False, repr=False)
    begin_count: int = field(default=0, init=False, repr=False)

    def active_transaction_for(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> LifecycleTransaction | None:
        if tx_group != self.tx_group:
            raise RuntimeError(f"unknown lifecycle transaction group {tx_group!r}")
        return self.active_transaction

    def begin(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> LifecycleTransaction:
        if tx_group != self.tx_group:
            raise RuntimeError(f"unknown lifecycle transaction group {tx_group!r}")
        if self.begin_count == 0:
            if self.active_transaction is not None:
                raise RuntimeError("lifecycle transaction manager state is corrupted")
            self.active_transaction = LifecycleTransaction(tx_id=self._next_tx_id, tx_group=self.tx_group)
            self._next_tx_id += 1
        self.begin_count += 1
        transaction = self.active_transaction
        assert transaction is not None
        return transaction.bind_scope(
            commit=lambda: self.commit(self.tx_group),
            rollback=lambda: self.rollback(self.tx_group),
        )

    def validate(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> None:
        if tx_group != self.tx_group:
            raise RuntimeError(f"unknown lifecycle transaction group {tx_group!r}")
        if self.begin_count <= 0:
            raise RuntimeError("no active lifecycle transaction")
        transaction = self.active_transaction
        if transaction is None:
            raise RuntimeError("lifecycle transaction manager state is corrupted")
        transaction.validate_commit()

    def commit_only(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> int | None:
        if tx_group != self.tx_group:
            raise RuntimeError(f"unknown lifecycle transaction group {tx_group!r}")
        if self.begin_count <= 0:
            raise RuntimeError("no active lifecycle transaction")
        if self.begin_count > 1:
            self.begin_count -= 1
            return None
        transaction = self.active_transaction
        if transaction is None:
            raise RuntimeError("lifecycle transaction manager state is corrupted")
        tx_id = transaction.tx_id
        try:
            transaction.apply_commits()
        finally:
            self.active_transaction = None
            self.begin_count = 0
        return tx_id

    def commit(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> int | None:
        if tx_group != self.tx_group:
            raise RuntimeError(f"unknown lifecycle transaction group {tx_group!r}")
        if self.begin_count <= 0:
            raise RuntimeError("no active lifecycle transaction")
        if self.begin_count > 1:
            self.begin_count -= 1
            return None
        try:
            self.validate(tx_group)
        except BaseExceptionGroup as exc_group:
            self.rollback(tx_group)
            raise exc_group
        return self.commit_only(tx_group)

    def rollback(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> int | None:
        if tx_group != self.tx_group:
            raise RuntimeError(f"unknown lifecycle transaction group {tx_group!r}")
        if self.begin_count <= 0 or self.active_transaction is None:
            raise RuntimeError("no active lifecycle transaction")
        transaction = self.active_transaction
        transaction.rollback_dirty()
        tx_id = transaction.tx_id
        self.active_transaction = None
        self.begin_count = 0
        return tx_id

    def enlist(self, context: LifecycleContext, tx_group: Hashable = DEFAULT_TRANSACTION) -> int:
        if tx_group != self.tx_group:
            raise RuntimeError(f"unknown lifecycle transaction group {tx_group!r}")
        transaction = self.active_transaction
        if transaction is None:
            raise RuntimeError("no active lifecycle transaction")
        transaction.dirty_contexts[id(context)] = context
        if context.requires_validation_for(tx_group):
            transaction.validator_contexts[id(context)] = context
        return transaction.tx_id

    def drop(
        self,
        context: LifecycleContext,
        tx_id: int | None = None,
        tx_group: Hashable = DEFAULT_TRANSACTION,
    ) -> None:
        if tx_group != self.tx_group:
            raise RuntimeError(f"unknown lifecycle transaction group {tx_group!r}")
        transaction = self.active_transaction
        if transaction is None:
            return
        if tx_id is not None and transaction.tx_id != tx_id:
            return
        cid = id(context)
        transaction.dirty_contexts.pop(cid, None)
        transaction.validator_contexts.pop(cid, None)


class _MultiGroupTransactionScope:
    __slots__ = ("_manager", "_groups")

    def __init__(self, manager: "TransactionManager", groups: tuple[Hashable, ...]) -> None:
        self._manager = manager
        self._groups = groups

    def __enter__(self) -> "_MultiGroupTransactionScope":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> bool:
        del exc, tb
        if exc_type is None:
            self._manager.commit(*reversed(self._groups))
        else:
            self._manager.rollback(*reversed(self._groups))
        return False


class TransactionManager:
    __slots__ = ("_tx_groups", "_tx_group_set", "_group_managers")

    def __init__(self, *, tx_groups: typing.Iterable[Hashable] = ()) -> None:
        normalized_groups: list[Hashable] = []
        seen = {DEFAULT_TRANSACTION}
        for group in tx_groups:
            if group in seen:
                continue
            seen.add(group)
            normalized_groups.append(group)
        self._tx_groups = tuple(normalized_groups)
        self._tx_group_set = frozenset((DEFAULT_TRANSACTION, *self._tx_groups))
        self._group_managers: dict[Hashable, GroupTransactionManager] = {}

    @property
    def tx_groups(self) -> tuple[Hashable, ...]:
        return self._tx_groups

    @property
    def active_transaction(self) -> LifecycleTransaction | None:
        return self._get_group_manager(DEFAULT_TRANSACTION).active_transaction

    @active_transaction.setter
    def active_transaction(self, value: LifecycleTransaction | None) -> None:
        self._get_group_manager(DEFAULT_TRANSACTION).active_transaction = value

    @property
    def begin_count(self) -> int:
        return self._get_group_manager(DEFAULT_TRANSACTION).begin_count

    def active_transaction_for(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> LifecycleTransaction | None:
        return self._get_group_manager(tx_group).active_transaction

    def _normalize_groups(self, groups: tuple[Hashable, ...]) -> tuple[Hashable, ...]:
        if not groups:
            return (DEFAULT_TRANSACTION, *self._tx_groups)
        normalized: list[Hashable] = []
        seen: set[Hashable] = set()
        for group in groups:
            self._require_known_group(group)
            if group in seen:
                continue
            seen.add(group)
            normalized.append(group)
        return tuple(normalized)

    def _require_known_group(self, group: Hashable) -> None:
        if group not in self._tx_group_set:
            raise RuntimeError(f"unknown lifecycle transaction group {group!r}")

    def _get_group_manager(self, group: Hashable) -> GroupTransactionManager:
        self._require_known_group(group)
        manager = self._group_managers.get(group)
        if manager is None:
            manager = GroupTransactionManager(tx_group=group)
            self._group_managers[group] = manager
        return manager

    def begin(self, *groups: Hashable) -> LifecycleTransaction | _MultiGroupTransactionScope:
        normalized_groups = self._normalize_groups(groups)
        if len(normalized_groups) == 1:
            return self._get_group_manager(normalized_groups[0]).begin(normalized_groups[0])
        for group in normalized_groups:
                self._get_group_manager(group).begin(group)
        return _MultiGroupTransactionScope(self, normalized_groups)

    def validate(self, *groups: Hashable) -> None:
        normalized_groups = self._normalize_groups(groups)
        failures: list[BaseException] = []
        for group in normalized_groups:
            try:
                self._get_group_manager(group).validate(group)
            except BaseException as exc:
                failures.append(exc)
        if not failures:
            return
        if len(failures) == 1:
            raise failures[0]
        raise ExceptionGroup("lifecycle transaction group validation failed", failures)

    def commit_only(self, *groups: Hashable) -> int | tuple[int | None, ...] | None:
        normalized_groups = self._normalize_groups(groups)
        if len(normalized_groups) == 1:
            return self._get_group_manager(normalized_groups[0]).commit_only(normalized_groups[0])
        failures: list[BaseException] = []
        results: list[int | None] = []
        for group in normalized_groups:
            try:
                results.append(self._get_group_manager(group).commit_only(group))
            except BaseException as exc:
                failures.append(exc)
        if failures:
            if len(failures) == 1:
                raise failures[0]
            raise ExceptionGroup("lifecycle transaction group commit_only failed", failures)
        return tuple(results)

    def commit(self, *groups: Hashable) -> int | tuple[int | None, ...] | None:
        normalized_groups = self._normalize_groups(groups)
        if len(normalized_groups) == 1:
            return self._get_group_manager(normalized_groups[0]).commit(normalized_groups[0])
        failures: list[BaseException] = []
        results: list[int | None] = []
        for group in normalized_groups:
            try:
                results.append(self._get_group_manager(group).commit(group))
            except BaseException as exc:
                failures.append(exc)
        if failures:
            if len(failures) == 1:
                raise failures[0]
            raise ExceptionGroup("lifecycle transaction group commit failed", failures)
        return tuple(results)

    def rollback(self, *groups: Hashable) -> int | tuple[int | None, ...] | None:
        normalized_groups = self._normalize_groups(groups)
        if len(normalized_groups) == 1:
            return self._get_group_manager(normalized_groups[0]).rollback(normalized_groups[0])
        failures: list[BaseException] = []
        results: list[int | None] = []
        for group in normalized_groups:
            try:
                results.append(self._get_group_manager(group).rollback(group))
            except BaseException as exc:
                failures.append(exc)
        if failures:
            if len(failures) == 1:
                raise failures[0]
            raise ExceptionGroup("lifecycle transaction group rollback failed", failures)
        return tuple(results)

    def enlist(self, context: LifecycleContext, tx_group: Hashable = DEFAULT_TRANSACTION) -> int:
        return self._get_group_manager(tx_group).enlist(context, tx_group)

    def drop(
        self,
        context: LifecycleContext,
        tx_id: int | None = None,
        tx_group: Hashable = DEFAULT_TRANSACTION,
    ) -> None:
        self._get_group_manager(tx_group).drop(context, tx_id, tx_group)


@dataclass(eq=False, slots=True)
class BindingBase(ABC):
    _ref_count: int = field(default=1, init=False, repr=False)
    _accepted: bool = field(default=False, init=False, repr=False)
    _closed: bool = field(default=False, init=False, repr=False)

    @property
    def ref_count(self) -> int:
        return self._ref_count

    @property
    def is_accepted(self) -> bool:
        return self._accepted

    @property
    def is_closed(self) -> bool:
        return self._closed

    def inc_ref(self) -> None:
        if self._closed or self._ref_count <= 0:
            raise RuntimeError("cannot retain a closed binding")
        self._ref_count += 1

    def accepted(self) -> None:
        if self._closed:
            raise RuntimeError("cannot accept a closed binding")
        self._accepted = True

    def dec_ref(self) -> None:
        if self._ref_count <= 0:
            raise AssertionError("dec_ref called without a matching inc_ref")
        self._ref_count -= 1
        if self._ref_count == 0:
            if self._closed:
                raise AssertionError("binding closed more than once")
            self._closed = True
            self._close()

    @abstractmethod
    def _close(self) -> None: ...


FieldStateFactory = Callable[[], Any]
StateCopyHelper = Callable[[Any], Any]
FieldGetter = Callable[["LifecycleContextState", str], Any]
FieldSetter = Callable[["LifecycleContextState", str, Any], None]
FieldHook = Callable[["LifecycleContextState", str], None]
FactoryRunner = Callable[["LifecycleContextState"], Any]
InjectedRunner = Callable[["LifecycleContextState", dict[str, Any]], Any]

_SUPPORTED_FACTORY_PARAMS = frozenset({"self", "current", "working"})
_BEFORE_COMMIT_PARAMS = frozenset({"self", "current", "working", "tx_group"})
_AFTER_COMMIT_PARAMS = frozenset({"self", "previous", "current", "tx_group"})
_AFTER_ROLLBACK_PARAMS = frozenset({"self", "current", "tx_group"})


@dataclass(slots=True)
class HookRunnerTables:
    before_commit: dict[Hashable, list[InjectedRunner]] = field(default_factory=dict)
    after_commit: dict[Hashable, list[InjectedRunner]] = field(default_factory=dict)
    after_rollback: dict[Hashable, list[InjectedRunner]] = field(default_factory=dict)


@dataclass(slots=True)
class SpecialFieldTables:
    commit_order_key_by_group: dict[Hashable, str] = field(default_factory=dict)
    commit_validator_by_group: dict[Hashable, str] = field(default_factory=dict)


@dataclass(slots=True)
class _FieldTables:
    get_default: dict[str, FieldGetter] = field(default_factory=dict)
    get_current: dict[str, FieldGetter] = field(default_factory=dict)
    get_working: dict[str, FieldGetter] = field(default_factory=dict)
    set_default: dict[str, FieldSetter] = field(default_factory=dict)
    set_working: dict[str, FieldSetter] = field(default_factory=dict)
    commit_field: dict[str, FieldHook] = field(default_factory=dict)
    rollback_field: dict[str, FieldHook] = field(default_factory=dict)
    close_field: dict[str, FieldHook] = field(default_factory=dict)
    state_factory: dict[str, FieldStateFactory | None] = field(default_factory=dict)
    state_copy: dict[str, StateCopyHelper | None] = field(default_factory=dict)
    field_tx_index: dict[str, int] = field(default_factory=dict)
    default_factory_runner: dict[str, FactoryRunner] = field(default_factory=dict)
    working_default_factory_runner: dict[str, FactoryRunner] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ExposedParam:
    """Appears in the generated helper's keyword-only signature."""
    annotation_src: str
    default_src: str
    doc: str = ""
    allowed_values: frozenset | None = None


@dataclass(frozen=True, slots=True)
class FixedParam:
    """Passed to lifecycle_field with a fixed value; not in the signature."""
    value_src: str


class _ScrubType:
    __slots__ = ()
    def __repr__(self) -> str:
        return 'SCRUB_PARAM'


SCRUB_PARAM = _ScrubType()

_ParamEntry = ExposedParam | FixedParam | _ScrubType


class HelperParams:
    """Chained builder for ``helper_params`` declarations on ``LCKind``."""

    __slots__ = ('_params',)

    def __init__(self) -> None:
        self._params: dict[str, _ParamEntry] = {}

    def param(self, name: str, doc: str = "") -> "HelperParams":
        preset = _PARAM_PRESETS[name]
        self._params[name] = ExposedParam(
            preset.annotation_src, preset.default_src, doc, preset.allowed_values,
        )
        return self

    def fixed(self, name: str, value_src: str) -> "HelperParams":
        self._params[name] = FixedParam(value_src)
        return self

    def scrub(self, name: str) -> "HelperParams":
        self._params[name] = SCRUB_PARAM
        return self


def _param(name: str, doc: str = "") -> HelperParams:
    return HelperParams().param(name, doc)


def _fixed(name: str, value_src: str) -> HelperParams:
    return HelperParams().fixed(name, value_src)


def _scrub(name: str) -> HelperParams:
    return HelperParams().scrub(name)


_PARAM_PRESETS: dict[str, ExposedParam] = {
    "compare":                 ExposedParam("str",                        '"value"',            allowed_values=frozenset({"value", "identity"})),
    "tx_group":                ExposedParam("Hashable",                   "DEFAULT_TRANSACTION"),
    "default":                 ExposedParam("Any",                        "MISSING"),
    "default_factory":         ExposedParam("Callable[[], Any] | object", "MISSING"),
    "working_default_factory": ExposedParam("Callable[[], Any] | object", "MISSING"),
    "initial_working":         ExposedParam("Any",                        "MISSING"),
    "freeze":                  ExposedParam("Callable[[Any], Any] | None", "None"),
    "thaw":                    ExposedParam("Callable[[Any], Any] | None", "None"),
    "state_factory":           ExposedParam("Callable[[], Any] | None",   "None"),
    "state_copy":              ExposedParam("StateCopyHelper | None",     "None"),
}


_LIFECYCLE_FIELD_NEUTRALS: dict[str, Any] = {
    "compare":                 "value",
    "tx_group":                DEFAULT_TRANSACTION,
    "default":                 MISSING,
    "default_factory":         MISSING,
    "working_default_factory": MISSING,
    "initial_working":         MISSING,
    "freeze":                  None,
    "thaw":                    None,
    "state_factory":           None,
    "state_copy":              None,
}


def _resolve_helper_params(cls: type) -> dict[str, ExposedParam | FixedParam]:
    merged: dict[str, ExposedParam | FixedParam] = {}
    for base in reversed(cls.__mro__):
        hp = base.__dict__.get('helper_params')
        if hp is None:
            continue
        for name, entry in hp._params.items():
            if isinstance(entry, _ScrubType):
                merged.pop(name, None)
            else:
                merged[name] = entry
    return merged


_TERMINAL_KINDS: list[type] = []


class LCKind:
    name: str = "<unset>"
    _resolved_params: dict[str, ExposedParam | FixedParam]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._resolved_params = _resolve_helper_params(cls)

    @classmethod
    def validate_spec(cls, spec: FieldSpec) -> None:
        return None

    @classmethod
    def validate_field_spec(cls, spec: FieldSpec) -> None:
        resolved = cls._resolved_params
        for kwarg, neutral in _LIFECYCLE_FIELD_NEUTRALS.items():
            actual = getattr(spec, kwarg)
            param = resolved.get(kwarg)
            if param is None:
                if actual is not neutral and actual != neutral:
                    raise TypeError(
                        f"{cls.name!r} fields cannot define {kwarg}"
                    )
            elif isinstance(param, ExposedParam) and param.allowed_values is not None:
                if actual not in param.allowed_values:
                    raise TypeError(
                        f"{cls.name!r} fields require {kwarg} in "
                        f"{param.allowed_values}"
                    )
        cls.validate_spec(spec)

    @classmethod
    def validate_override(cls, base: FieldSpec, derived: FieldSpec) -> None:
        if derived.kind is not cls:
            raise TypeError(f"incompatible lifecycle field override for {base.name!r}")
        if base.compare != derived.compare:
            raise TypeError(f"incompatible lifecycle field override for {base.name!r}")
        if base.tx_group != derived.tx_group:
            raise TypeError(f"incompatible lifecycle field override for {base.name!r}")
        if base.initial_working != derived.initial_working and derived.initial_working is not MISSING:
            raise TypeError(f"incompatible lifecycle field override for {base.name!r}")
        if base.freeze != derived.freeze and derived.freeze is not None:
            raise TypeError(f"incompatible lifecycle field override for {base.name!r}")
        if base.thaw != derived.thaw and derived.thaw is not None:
            raise TypeError(f"incompatible lifecycle field override for {base.name!r}")
        if base.state_factory != derived.state_factory and derived.state_factory is not None:
            raise TypeError(f"incompatible lifecycle field override for {base.name!r}")
        if base.state_copy != derived.state_copy and derived.state_copy is not None:
            raise TypeError(f"incompatible lifecycle field override for {base.name!r}")

    @classmethod
    def default_value(cls, spec: FieldSpec) -> Any:
        if spec.default is not MISSING:
            return spec.default
        if spec.default_factory is not MISSING:
            return spec.default_factory()
        raise TypeError(f"missing required lifecycle field {spec.name!r}")

    @classmethod
    def initialize_constructor_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
        values: dict[str, Any],
    ) -> None:
        if name in values:
            state.current_record.values[name] = values.pop(name)

    @classmethod
    def default_store_contains(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> bool:
        return name in state.current_record.values

    @classmethod
    def get_default_store_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> Any:
        return state.current_record.values[name]

    @classmethod
    def set_default_store_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
        value: Any,
    ) -> Any:
        state.current_record.values[name] = value
        return value

    @classmethod
    def reset_default_store(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> None:
        state.current_record.values.pop(name, None)

    @classmethod
    def register_hook_runner(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        hook_tables: HookRunnerTables,
    ) -> None:
        return None

    @classmethod
    def register_special_field(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        special_tables: SpecialFieldTables,
    ) -> None:
        return None

    @classmethod
    def build_default_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        raise NotImplementedError

    @classmethod
    def build_current_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        raise NotImplementedError

    @classmethod
    def build_working_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        raise NotImplementedError

    @classmethod
    def build_default_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        raise NotImplementedError

    @classmethod
    def build_working_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        raise NotImplementedError

    @classmethod
    def build_commit_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        raise NotImplementedError

    @classmethod
    def build_rollback_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        raise NotImplementedError

    @classmethod
    def build_close_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        raise NotImplementedError

    @classmethod
    def build_state_factory(cls, spec: FieldSpec) -> FieldStateFactory | None:
        raise NotImplementedError

    @classmethod
    def build_state_copy(cls, spec: FieldSpec) -> StateCopyHelper | None:
        raise NotImplementedError

    @classmethod
    def install_field_tables(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        tx_index: int,
        tables: _FieldTables,
    ) -> None:
        tables.get_default[name] = cls.build_default_getter(tx_index=tx_index, spec=spec)
        tables.get_current[name] = cls.build_current_getter(tx_index=tx_index, spec=spec)
        tables.get_working[name] = cls.build_working_getter(tx_index=tx_index, spec=spec)
        tables.set_default[name] = cls.build_default_setter(tx_index=tx_index, spec=spec)
        tables.set_working[name] = cls.build_working_setter(tx_index=tx_index, spec=spec)
        tables.commit_field[name] = cls.build_commit_hook(tx_index=tx_index, spec=spec)
        tables.rollback_field[name] = cls.build_rollback_hook(tx_index=tx_index, spec=spec)
        tables.close_field[name] = cls.build_close_hook(tx_index=tx_index, spec=spec)
        tables.state_factory[name] = cls.build_state_factory(spec)
        tables.state_copy[name] = cls.build_state_copy(spec)


LCKind._resolved_params = {}


class NoStateHelpersOperationalKind(LCKind):
    @classmethod
    def build_state_factory(cls, spec: FieldSpec) -> FieldStateFactory | None:
        return None

    @classmethod
    def build_state_copy(cls, spec: FieldSpec) -> StateCopyHelper | None:
        return None


class NoLifecycleHooksOperationalKind(NoStateHelpersOperationalKind):
    @classmethod
    def build_commit_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _close_noop

    @classmethod
    def build_rollback_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _close_noop

    @classmethod
    def build_close_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _close_noop


class SameGetterEverywhereOperationalKind(LCKind):
    @classmethod
    def build_shared_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        raise NotImplementedError

    @classmethod
    def build_default_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return cls.build_shared_getter(tx_index=tx_index, spec=spec)

    @classmethod
    def build_current_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return cls.build_shared_getter(tx_index=tx_index, spec=spec)

    @classmethod
    def build_working_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return cls.build_shared_getter(tx_index=tx_index, spec=spec)


class SameSetterEverywhereOperationalKind(LCKind):
    @classmethod
    def build_shared_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        raise NotImplementedError

    @classmethod
    def build_default_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return cls.build_shared_setter(tx_index=tx_index, spec=spec)

    @classmethod
    def build_working_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return cls.build_shared_setter(tx_index=tx_index, spec=spec)


class OverlayOperationalKind(LCKind):
    @classmethod
    def build_default_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        if spec.thaw is not None:
            return _build_managed_thawed_getter(tx_index)
        if spec.initial_working is not MISSING:
            return _build_managed_initial_working_getter(tx_index)
        return _build_default_overlay_getter(tx_index)

    @classmethod
    def build_current_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_current_field

    @classmethod
    def build_working_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        if spec.thaw is not None:
            return _build_managed_thawed_getter(tx_index)
        if spec.initial_working is not MISSING:
            return _build_managed_initial_working_getter(tx_index)
        return _build_working_overlay_getter(tx_index)

    @classmethod
    def build_default_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        if spec.compare == "identity":
            return _build_default_identity_setter(tx_index)
        return _build_default_value_setter(tx_index)

    @classmethod
    def build_working_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        if spec.compare == "identity":
            return _build_working_identity_setter(tx_index)
        return _build_working_value_setter(tx_index)

    @classmethod
    def build_commit_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _build_overlay_commit_hook(tx_index)

    @classmethod
    def build_rollback_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _rollback_overlay_field

    @classmethod
    def build_close_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _close_noop

    @classmethod
    def build_state_factory(cls, spec: FieldSpec) -> FieldStateFactory | None:
        return spec.state_factory

    @classmethod
    def build_state_copy(cls, spec: FieldSpec) -> StateCopyHelper | None:
        return spec.state_copy


class ImmutableOperationalKind(
    SameGetterEverywhereOperationalKind,
    SameSetterEverywhereOperationalKind,
    NoLifecycleHooksOperationalKind,
):
    pass


class ConstOperationalKind(ImmutableOperationalKind):
    @classmethod
    def build_shared_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_current_field

    @classmethod
    def build_shared_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return _set_const_field


class StaticOperationalKind(ImmutableOperationalKind):
    @classmethod
    def build_shared_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_static_field

    @classmethod
    def build_shared_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return _set_static_field


class StoredDeclarationOperationalKind(ConstOperationalKind):
    pass


class RetainedResourceOperationalKind(NoStateHelpersOperationalKind):
    @classmethod
    def _is_mapping_field(cls, spec: FieldSpec) -> bool:
        return typing.get_origin(spec.annotation) in {dict, typing.Dict}

    @classmethod
    def build_default_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _build_default_overlay_getter(tx_index)

    @classmethod
    def build_current_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_current_field

    @classmethod
    def build_working_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _build_working_overlay_getter(tx_index)

    @classmethod
    def build_default_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        if cls._is_mapping_field(spec):
            return _build_default_binding_map_setter(tx_index)
        return _build_default_binding_setter(tx_index)

    @classmethod
    def build_working_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        if cls._is_mapping_field(spec):
            return _build_working_binding_map_setter(tx_index)
        return _build_working_binding_setter(tx_index)

    @classmethod
    def build_commit_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        if cls._is_mapping_field(spec):
            return _build_binding_map_commit_hook(tx_index)
        return _build_binding_commit_hook(tx_index)

    @classmethod
    def build_rollback_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        if cls._is_mapping_field(spec):
            return _build_binding_map_rollback_hook(tx_index)
        return _build_binding_rollback_hook(tx_index)

    @classmethod
    def build_close_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        if cls._is_mapping_field(spec):
            return _close_binding_map_field
        return _close_binding_field


class TransientOperationalKind(NoLifecycleHooksOperationalKind):
    @classmethod
    def build_default_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        if spec.working_default_factory is not MISSING:
            return _build_transient_working_default_getter(tx_index)
        return _build_default_overlay_getter(tx_index)

    @classmethod
    def build_current_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_current_field

    @classmethod
    def build_working_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        if spec.working_default_factory is not MISSING:
            return _build_transient_working_default_getter(tx_index)
        return _build_working_overlay_getter(tx_index)

    @classmethod
    def build_default_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return _build_default_value_setter(tx_index)

    @classmethod
    def build_working_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return _build_working_value_setter(tx_index)


class LocalStoreOperationalKind(
    SameGetterEverywhereOperationalKind,
    SameSetterEverywhereOperationalKind,
    NoStateHelpersOperationalKind,
):
    @classmethod
    def build_shared_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_local_store_field

    @classmethod
    def build_shared_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return _set_local_store_field

    @classmethod
    def build_commit_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _close_noop

    @classmethod
    def build_rollback_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _close_noop

    @classmethod
    def build_close_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _close_local_store_field


class DerivedOperationalKind(
    SameGetterEverywhereOperationalKind,
    SameSetterEverywhereOperationalKind,
    NoStateHelpersOperationalKind,
):
    @classmethod
    def build_shared_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_derived_field

    @classmethod
    def build_shared_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return _set_derived_field

    @classmethod
    def build_commit_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _reset_derived_field

    @classmethod
    def build_rollback_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _reset_derived_field

    @classmethod
    def build_close_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _reset_derived_field


class HookOperationalKind(
    SameGetterEverywhereOperationalKind,
    SameSetterEverywhereOperationalKind,
    NoLifecycleHooksOperationalKind,
):
    @classmethod
    def build_shared_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_hook_declaration_field

    @classmethod
    def build_shared_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return _set_hook_declaration_field


class CurrentRecordStorageKind(LCKind):
    pass


class LocalStoreStorageKind(LCKind):
    @classmethod
    def initialize_constructor_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
        values: dict[str, Any],
    ) -> None:
        if name in values:
            state.local_store_values[name] = values.pop(name)

    @classmethod
    def default_store_contains(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> bool:
        return name in state.local_store_values

    @classmethod
    def get_default_store_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> Any:
        return state.local_store_values[name]

    @classmethod
    def set_default_store_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
        value: Any,
    ) -> Any:
        state.local_store_values[name] = value
        return value

    @classmethod
    def reset_default_store(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> None:
        state.local_store_values.pop(name, None)


class DerivedStoreStorageKind(LCKind):
    @classmethod
    def initialize_constructor_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
        values: dict[str, Any],
    ) -> None:
        if name in values:
            state.derived_values[name] = values.pop(name)

    @classmethod
    def default_store_contains(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> bool:
        return name in state.derived_values

    @classmethod
    def get_default_store_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> Any:
        return state.derived_values[name]

    @classmethod
    def set_default_store_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
        value: Any,
    ) -> Any:
        state.derived_values[name] = value
        return value

    @classmethod
    def reset_default_store(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> None:
        state.derived_values.pop(name, None)


class DeclarationStorageKind(LCKind):
    @classmethod
    def initialize_constructor_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
        values: dict[str, Any],
    ) -> None:
        del state
        values.pop(name, None)


class StoredKind(CurrentRecordStorageKind, LCKind):
    @classmethod
    def validate_spec(cls, spec: FieldSpec) -> None:
        return None


class NonStoredHookKind(DeclarationStorageKind, LCKind):
    @classmethod
    def validate_spec(cls, spec: FieldSpec) -> None:
        if spec.default is MISSING:
            raise TypeError(f"{cls.name!r} fields require default=callable")


class DefaultStoredKind(StoredKind, OverlayOperationalKind):
    helper_params = (
        _param("compare").param("tx_group")
        .param("default").param("default_factory")
        .param("initial_working")
        .param("freeze").param("thaw")
        .param("state_factory").param("state_copy")
    )


class SimpleStoredKind(StoredKind, OverlayOperationalKind):
    helper_params = (
        _param("compare").param("tx_group")
        .param("default").param("default_factory")
    )


class HookKind(NonStoredHookKind, HookOperationalKind):
    helper_params = (
        _fixed("compare", '"identity"')
        .param("tx_group").param("default")
    )

    @classmethod
    def register_hook_runner(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        hook_tables: HookRunnerTables,
    ) -> None:
        raise NotImplementedError


class ImmutableConfigKind(StoredKind):
    helper_params = (
        _fixed("compare", '"value"')
        .param("default").param("default_factory")
    )


class StoredNeverKind(ConstOperationalKind):
    pass


class StoredOnceKind(StaticOperationalKind):
    pass


class ResourceKind(RetainedResourceOperationalKind, SimpleStoredKind):
    pass


class StoredMetadataKind(StoredKind, StoredDeclarationOperationalKind):
    helper_params = (
        _param("compare").param("tx_group").param("default")
    )


class HookDeclarationKind(HookKind):
    pass


class LocalLikeKind(StoredKind):
    helper_params = (
        _fixed("compare", '"value"')
        .param("default").param("default_factory")
    )


class TxScopedScratchKind(TransientOperationalKind, LocalLikeKind):
    helper_params = (
        _param("working_default_factory").param("tx_group")
    )


class NonTransactionalHelperKind(LocalLikeKind):
    pass


class NonTransactionalLocalKind(
    LocalStoreOperationalKind,
    LocalStoreStorageKind,
    NonTransactionalHelperKind,
):
    pass


class DerivedHelperKind(
    DerivedOperationalKind,
    DerivedStoreStorageKind,
    NonTransactionalHelperKind,
):
    pass


_DEFINED_KIND_NAMES: set[str] = set()


def define_kind(cls: type[LCKind]) -> type[LCKind]:
    """Decorator for terminal LCKind classes.

    Validates the declaration and registers the kind for helper generation.
    Actual helper functions are installed by ``_generate_kind_helpers()``
    after ``lifecycle_field`` is defined.
    """
    name = cls.name
    if name == "<unset>":
        raise TypeError(f"{cls.__name__} must set name")
    if name in _DEFINED_KIND_NAMES:
        raise TypeError(f"duplicate kind name {name!r}")
    if not hasattr(cls, 'helper_doc'):
        raise TypeError(f"{cls.__name__} must set helper_doc")
    _DEFINED_KIND_NAMES.add(name)
    _TERMINAL_KINDS.append(cls)
    return cls


def _generate_kind_helpers() -> None:
    """Generate and install all helper functions for registered terminal kinds.

    Must be called after ``lifecycle_field`` is defined.
    """
    import sys
    module = sys.modules[__name__]
    all_list: list[str] = getattr(module, '__all__', [])

    exec_globals: dict[str, Any] = {
        'lifecycle_field': lifecycle_field,
        'MISSING': MISSING,
        'DEFAULT_TRANSACTION': DEFAULT_TRANSACTION,
    }

    for kind_cls in _TERMINAL_KINDS:
        resolved = kind_cls._resolved_params
        name = kind_cls.name
        lc_name = f"LC_{name.upper()}"

        exposed: list[tuple[str, ExposedParam]] = []
        fixed: list[tuple[str, FixedParam]] = []
        for pname, entry in resolved.items():
            if isinstance(entry, ExposedParam):
                exposed.append((pname, entry))
            elif isinstance(entry, FixedParam):
                fixed.append((pname, entry))

        local_ns: dict[str, Any] = {
            '_kind_cls': kind_cls,
            'lifecycle_field': lifecycle_field,
        }

        sig_parts: list[str] = []
        call_parts: list[str] = [f"kind=_kind_cls"]
        annotation_stmts: list[str] = []

        for pname, param in exposed:
            dflt_key = f'_dflt_{pname}'
            local_ns[dflt_key] = eval(param.default_src, exec_globals)  # noqa: S307
            sig_parts.append(f"{pname}={dflt_key}")
            call_parts.append(f"{pname}={pname}")

        for pname, param in fixed:
            fval_key = f'_fval_{pname}'
            local_ns[fval_key] = eval(param.value_src, exec_globals)  # noqa: S307
            call_parts.append(f"{pname}={fval_key}")

        sig_str = ", ".join(sig_parts)
        call_str = ", ".join(call_parts)

        src = (
            f"def {name}(*, {sig_str}) -> Any:\n"
            f"    return lifecycle_field({call_str})\n"
        )

        fn_ns: dict[str, Any] = {'Any': Any, **local_ns}
        exec(src, fn_ns)  # noqa: S102
        fn = fn_ns[name]
        fn.__module__ = __name__
        fn.__qualname__ = name
        fn.__doc__ = getattr(kind_cls, 'helper_doc', None)

        ann: dict[str, Any] = {}
        for pname, param in exposed:
            try:
                ann[pname] = eval(param.annotation_src, exec_globals)  # noqa: S307
            except Exception:
                ann[pname] = param.annotation_src
        ann['return'] = Any
        fn.__annotations__ = ann

        setattr(module, name, fn)
        setattr(module, lc_name, kind_cls)

        if name not in all_list:
            all_list.append(name)
        if lc_name not in all_list:
            all_list.append(lc_name)

        kind_cls._generated_helper = fn


@define_kind
class ManagedKind(DefaultStoredKind):
    name = "managed"
    helper_doc = "Managed transactional field with overlay, commit, and rollback."


@define_kind
class ConstKind(StoredNeverKind, ImmutableConfigKind):
    name = "const"
    helper_doc = "Immutable per-instance configuration, set at construction."


@define_kind
class StaticKind(StoredOnceKind, ImmutableConfigKind):
    name = "static"
    helper_doc = "Class-level shared value, written at most once."

    @classmethod
    def default_value(cls, spec: FieldSpec) -> Any:
        if spec.default is MISSING and spec.default_factory is MISSING:
            return _SENTINEL
        return super().default_value(spec)


@define_kind
class BindingKind(ResourceKind):
    name = "binding"
    helper_doc = "Identity-compared retained resource binding."
    helper_params = _fixed("compare", '"identity"')


@define_kind
class OwnedKind(ResourceKind):
    name = "owned"
    helper_doc = "Identity-compared owned child resource."
    helper_params = _fixed("compare", '"identity"')


@define_kind
class TransientKind(TxScopedScratchKind):
    name = "transient"
    helper_doc = "Transaction-scoped scratch that exists only while a group is open."


@define_kind
class LocalStoreKind(NonTransactionalLocalKind):
    name = "local_store"
    helper_doc = "Non-transactional local storage, cleared on close."


@define_kind
class DerivedKind(DerivedHelperKind):
    name = "derived"
    helper_doc = "Cached derived value, reset on commit/rollback/close."


@define_kind
class CommitOrderKeyKind(StoredMetadataKind):
    name = "commit_order_key"
    helper_doc = "Sortable key controlling commit ordering within a group."
    helper_params = _fixed("compare", '"value"').param("default_factory")

    @classmethod
    def default_value(cls, spec: FieldSpec) -> Any:
        if spec.default is not MISSING:
            return spec.default
        if spec.default_factory is not MISSING:
            return spec.default_factory()
        return ()

    @classmethod
    def register_special_field(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        special_tables: SpecialFieldTables,
    ) -> None:
        if spec.tx_group in special_tables.commit_order_key_by_group:
            raise TypeError(
                f"at most one commit_order_key field is allowed for group {spec.tx_group!r}"
            )
        special_tables.commit_order_key_by_group[spec.tx_group] = name


@define_kind
class CommitValidatorKind(StoredMetadataKind):
    name = "commit_validator"
    helper_doc = "Callable that validates state before commit is finalized."
    helper_params = _fixed("compare", '"identity"')

    @classmethod
    def default_value(cls, spec: FieldSpec) -> Any:
        if spec.default is not MISSING:
            return spec.default
        return None

    @classmethod
    def register_special_field(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        special_tables: SpecialFieldTables,
    ) -> None:
        if spec.tx_group in special_tables.commit_validator_by_group:
            raise TypeError(
                f"at most one commit_validator field is allowed for group {spec.tx_group!r}"
            )
        special_tables.commit_validator_by_group[spec.tx_group] = name


@define_kind
class OnBeforeCommitKind(HookDeclarationKind):
    name = "on_before_commit"
    helper_doc = "Hook invoked before a transaction group commits."

    @classmethod
    def register_hook_runner(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        hook_tables: HookRunnerTables,
    ) -> None:
        hook = typing.cast(Callable[..., Any], spec.default)
        if not callable(hook):
            raise TypeError(f"{spec.kind.name} field {name!r} requires a callable default")
        hook_tables.before_commit.setdefault(spec.tx_group, []).append(
            _compile_hook_runner(
                field_name=name,
                hook_name="on_before_commit",
                hook=hook,
                allowed_params=_BEFORE_COMMIT_PARAMS,
            )
        )


@define_kind
class OnAfterCommitKind(HookDeclarationKind):
    name = "on_after_commit"
    helper_doc = "Hook invoked after a transaction group commits."

    @classmethod
    def register_hook_runner(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        hook_tables: HookRunnerTables,
    ) -> None:
        hook = typing.cast(Callable[..., Any], spec.default)
        if not callable(hook):
            raise TypeError(f"{spec.kind.name} field {name!r} requires a callable default")
        hook_tables.after_commit.setdefault(spec.tx_group, []).append(
            _compile_hook_runner(
                field_name=name,
                hook_name="on_after_commit",
                hook=hook,
                allowed_params=_AFTER_COMMIT_PARAMS,
            )
        )


@define_kind
class OnAfterRollbackKind(HookDeclarationKind):
    name = "on_after_rollback"
    helper_doc = "Hook invoked after a transaction group rolls back."

    @classmethod
    def register_hook_runner(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        hook_tables: HookRunnerTables,
    ) -> None:
        hook = typing.cast(Callable[..., Any], spec.default)
        if not callable(hook):
            raise TypeError(f"{spec.kind.name} field {name!r} requires a callable default")
        hook_tables.after_rollback.setdefault(spec.tx_group, []).append(
            _compile_hook_runner(
                field_name=name,
                hook_name="on_after_rollback",
                hook=hook,
                allowed_params=_AFTER_ROLLBACK_PARAMS,
            )
        )


def _compile_injected_runner(
    *,
    field_name: str,
    hook_name: str,
    function: Callable[..., Any],
    allowed_params: frozenset[str],
) -> InjectedRunner:
    if inspect.isbuiltin(function) or inspect.isclass(function):
        return lambda state, injected, function=function: function()
    try:
        signature = inspect.signature(function)
    except (TypeError, ValueError):
        return lambda state, injected, function=function: function()
    parameter_names: tuple[str, ...] = ()
    if signature.parameters:
        names: list[str] = []
        for parameter in signature.parameters.values():
            if parameter.kind not in {
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            }:
                raise TypeError(
                    f"{hook_name} for field {field_name!r} must use named parameters only",
                )
            if parameter.name not in allowed_params:
                allowed = ", ".join(sorted(allowed_params))
                raise TypeError(
                    f"{hook_name} for field {field_name!r} uses unsupported parameter "
                    f"{parameter.name!r}; allowed: {allowed}",
                )
            names.append(parameter.name)
        parameter_names = tuple(names)
    if not parameter_names:
        return lambda state, injected, function=function: function()

    def run(
        state: LifecycleContextState,
        injected: dict[str, Any],
        function: Callable[..., Any] = function,
    ) -> Any:
        kwargs: dict[str, Any] = {}
        for name in parameter_names:
            if name == "self":
                kwargs[name] = state.owner
            elif name == "current":
                kwargs[name] = injected.get("current", state.current_view)
            elif name == "working":
                kwargs[name] = injected.get("working", state.working_view)
            elif name == "previous":
                kwargs[name] = injected["previous"]
            elif name == "tx_group":
                kwargs[name] = injected["tx_group"]
            else:
                raise AssertionError(f"unexpected compiled lifecycle parameter {name!r}")
        return function(**kwargs)

    return run


def _compile_factory_runner(
    *,
    field_name: str,
    hook_name: str,
    factory: Callable[..., Any],
) -> FactoryRunner:
    injected_runner = _compile_injected_runner(
        field_name=field_name,
        hook_name=hook_name,
        function=factory,
        allowed_params=_SUPPORTED_FACTORY_PARAMS,
    )
    return lambda state, injected_runner=injected_runner: injected_runner(state, {})


def _compile_hook_runner(
    *,
    field_name: str,
    hook_name: str,
    hook: Callable[..., Any],
    allowed_params: frozenset[str],
) -> InjectedRunner:
    return _compile_injected_runner(
        field_name=field_name,
        hook_name=hook_name,
        function=hook,
        allowed_params=allowed_params,
    )


@dataclass(slots=True)
class FieldSpec:
    name: str
    kind: type[LCKind]
    annotation: Any
    compare: str
    default: Any = MISSING
    default_factory: Callable[[], Any] | object = MISSING
    working_default_factory: Callable[[], Any] | object = MISSING
    initial_working: Any = MISSING
    tx_group: Hashable = DEFAULT_TRANSACTION
    freeze: Callable[[Any], Any] | None = None
    thaw: Callable[[Any], Any] | None = None
    state_factory: FieldStateFactory | None = None
    state_copy: StateCopyHelper | None = None


class LifecycleField:
    __slots__ = (
        "compare",
        "default",
        "default_factory",
        "freeze",
        "initial_working",
        "kind",
        "name",
        "state_copy",
        "state_factory",
        "thaw",
        "tx_group",
        "working_default_factory",
    )

    def __init__(
        self,
        *,
        kind: type[LCKind] = ManagedKind,
        compare: str = "value",
        tx_group: Hashable = DEFAULT_TRANSACTION,
        default: Any = MISSING,
        default_factory: Callable[[], Any] | object = MISSING,
        working_default_factory: Callable[[], Any] | object = MISSING,
        initial_working: Any = MISSING,
        freeze: Callable[[Any], Any] | None = None,
        thaw: Callable[[Any], Any] | None = None,
        state_factory: Callable[[], Any] | None = None,
        state_copy: StateCopyHelper | None = None,
    ) -> None:
        if not isinstance(kind, type) or not issubclass(kind, LCKind):
            raise TypeError(f"unsupported lifecycle field kind {kind!r}")
        if default is not MISSING and default_factory is not MISSING:
            raise TypeError("lifecycle fields cannot define both default and default_factory")
        self.compare = compare
        self.default = default
        self.default_factory = default_factory
        self.working_default_factory = working_default_factory
        self.initial_working = initial_working
        self.freeze = freeze
        self.kind = kind
        self.state_factory = state_factory
        self.state_copy = state_copy
        self.thaw = thaw
        self.tx_group = tx_group
        self.name: str | None = None
        temp_spec = FieldSpec(
            name="<unbound>",
            kind=kind,
            annotation=Any,
            compare=compare,
            tx_group=tx_group,
            default=default,
            default_factory=default_factory,
            working_default_factory=working_default_factory,
            initial_working=initial_working,
            freeze=freeze,
            thaw=thaw,
            state_factory=state_factory,
            state_copy=state_copy,
        )
        kind.validate_field_spec(temp_spec)

    def __set_name__(self, owner: type[LifecycleContext], name: str) -> None:
        self.name = name

    def __get__(self, instance: LifecycleContext | None, owner: type[LifecycleContext]) -> Any:
        if instance is None:
            return self
        return instance.__get_field__(self.name_or_error())

    def __set__(self, instance: LifecycleContext, value: Any) -> None:
        instance.__set_field__(self.name_or_error(), value)

    def build_spec(self, annotation: Any) -> FieldSpec:
        spec = FieldSpec(
            name=self.name_or_error(),
            kind=self.kind,
            annotation=annotation,
            compare=self.compare,
            tx_group=self.tx_group,
            default=self.default,
            default_factory=self.default_factory,
            working_default_factory=self.working_default_factory,
            initial_working=self.initial_working,
            freeze=self.freeze,
            thaw=self.thaw,
            state_factory=self.state_factory,
            state_copy=self.state_copy,
        )
        spec.kind.validate_field_spec(spec)
        return spec

    def name_or_error(self) -> str:
        if self.name is None:
            raise RuntimeError("lifecycle field name was not initialized")
        return self.name


def lifecycle_field(
    *,
    kind: type[LCKind] = ManagedKind,
    compare: str = "value",
    tx_group: Hashable = DEFAULT_TRANSACTION,
    default: Any = MISSING,
    default_factory: Callable[[], Any] | object = MISSING,
    working_default_factory: Callable[[], Any] | object = MISSING,
    initial_working: Any = MISSING,
    freeze: Callable[[Any], Any] | None = None,
    thaw: Callable[[Any], Any] | None = None,
    state_factory: Callable[[], Any] | None = None,
    state_copy: StateCopyHelper | None = None,
) -> Any:
    return LifecycleField(
        kind=kind,
        compare=compare,
        tx_group=tx_group,
        default=default,
        default_factory=default_factory,
        working_default_factory=working_default_factory,
        initial_working=initial_working,
        freeze=freeze,
        state_factory=state_factory,
        state_copy=state_copy,
        thaw=thaw,
    )


_generate_kind_helpers()


def _get_hook_declaration_field(state: LifecycleContextState, name: str) -> Any:
    del state
    raise AttributeError(f"hook field {name!r} is a declaration and is not readable")


def _set_hook_declaration_field(state: LifecycleContextState, name: str, value: Any) -> None:
    del state, value
    raise AttributeError(f"hook field {name!r} is a declaration and is not writable")


def _get_default_overlay_field_for_index(
    state: LifecycleContextState,
    name: str,
    tx_index: int,
) -> Any:
    working = state.working_record_for_index(tx_index)
    if working is not None and name in working.values:
        return working.values[name]
    return state.resolve_default_field(name)


@functools.cache
def _build_default_overlay_getter(tx_index: int) -> FieldGetter:
    return lambda state, name, tx_index=tx_index: _get_default_overlay_field_for_index(state, name, tx_index)


def _get_current_field(state: LifecycleContextState, name: str) -> Any:
    return state.resolve_default_field(name)


def _get_working_overlay_field_for_index(
    state: LifecycleContextState,
    name: str,
    tx_index: int,
) -> Any:
    working = state.working_record_for_index(tx_index)
    if working is not None and name in working.values:
        return working.values[name]
    return state.resolve_default_field(name)


@functools.cache
def _build_working_overlay_getter(tx_index: int) -> FieldGetter:
    return lambda state, name, tx_index=tx_index: _get_working_overlay_field_for_index(state, name, tx_index)


def _get_managed_initial_working_field_for_index(
    state: LifecycleContextState,
    name: str,
    tx_index: int,
) -> Any:
    working = state.working_record_for_index(tx_index)
    if working is not None and name in working.values:
        return working.values[name]
    tx_group = type(state).__class_tx_groups__[tx_index]
    transaction = (
        state.transaction_manager.active_transaction_for(tx_group)
        if state.transaction_manager is not None
        else None
    )
    spec = type(state).__field_specs__[name]
    if transaction is not None and not state.ever_committed and spec.initial_working is not MISSING:
        return spec.initial_working
    return state.resolve_default_field(name)


@functools.cache
def _build_managed_initial_working_getter(tx_index: int) -> FieldGetter:
    return lambda state, name, tx_index=tx_index: _get_managed_initial_working_field_for_index(
        state, name, tx_index
    )


def _get_managed_thawed_field_for_index(
    state: LifecycleContextState,
    name: str,
    tx_index: int,
) -> Any:
    working = state.working_record_for_index(tx_index)
    if working is not None and name in working.values:
        return working.values[name]
    tx_group = type(state).__class_tx_groups__[tx_index]
    transaction = (
        state.transaction_manager.active_transaction_for(tx_group)
        if state.transaction_manager is not None
        else None
    )
    spec = type(state).__field_specs__[name]
    if transaction is None or spec.thaw is None:
        return state.resolve_default_field(name)
    working = state.ensure_working_record_for_index(tx_index)
    if name not in working.values:
        working.values[name] = spec.thaw(state.resolve_default_field(name))
    return working.values[name]


@functools.cache
def _build_managed_thawed_getter(tx_index: int) -> FieldGetter:
    return lambda state, name, tx_index=tx_index: _get_managed_thawed_field_for_index(state, name, tx_index)


def _get_transient_working_default_field_for_index(
    state: LifecycleContextState,
    name: str,
    tx_index: int,
) -> Any:
    working = state.working_record_for_index(tx_index)
    if working is not None and name in working.values:
        return working.values[name]
    tx_group = type(state).__class_tx_groups__[tx_index]
    transaction = (
        state.transaction_manager.active_transaction_for(tx_group)
        if state.transaction_manager is not None
        else None
    )
    if transaction is not None and name in type(state).__class_ftable_working_default_factory_runner__:
        return state.resolve_working_default_field_for_index(name, tx_index)
    return state.resolve_default_field(name)


@functools.cache
def _build_transient_working_default_getter(tx_index: int) -> FieldGetter:
    return lambda state, name, tx_index=tx_index: _get_transient_working_default_field_for_index(
        state, name, tx_index
    )


def _get_static_field(state: LifecycleContextState, name: str) -> Any:
    value = state.resolve_default_field(name)
    if value is _SENTINEL:
        raise AttributeError(f"static field {name!r} is not initialized")
    return value


def _get_local_store_field(state: LifecycleContextState, name: str) -> Any:
    return state.resolve_default_field(name)


def _get_derived_field(state: LifecycleContextState, name: str) -> Any:
    return state.resolve_default_field(name)


def _is_binding_map_value(value: Any) -> bool:
    return isinstance(value, Mapping)


def _normalize_binding_map_value(name: str, value: Any) -> dict[Any, BindingBase]:
    if not isinstance(value, Mapping):
        raise TypeError(f"binding field {name!r} expects a mapping value")
    normalized = dict(value)
    for binding_value in normalized.values():
        if not isinstance(binding_value, BindingBase):
            raise TypeError(f"binding field {name!r} expects BindingBase values")
    return normalized


def _binding_occurrences(bindings: Mapping[Any, BindingBase]) -> dict[int, tuple[BindingBase, int]]:
    counts: dict[int, tuple[BindingBase, int]] = {}
    for binding_value in bindings.values():
        binding_id = id(binding_value)
        if binding_id in counts:
            existing, count = counts[binding_id]
            counts[binding_id] = (existing, count + 1)
        else:
            counts[binding_id] = (binding_value, 1)
    return counts


def _same_binding_map(left: Mapping[Any, BindingBase], right: Mapping[Any, BindingBase]) -> bool:
    if left.keys() != right.keys():
        return False
    return all(left[key] is right[key] for key in left)


def _release_binding_map(bindings: Mapping[Any, BindingBase]) -> None:
    for binding_value, count in _binding_occurrences(bindings).values():
        for _ in range(count):
            binding_value.dec_ref()


def _accept_binding_map(bindings: Mapping[Any, BindingBase]) -> None:
    for binding_value, _ in _binding_occurrences(bindings).values():
        binding_value.accepted()


def _set_const_field(state: LifecycleContextState, name: str, value: Any) -> None:
    del state, value
    raise AttributeError(f"const field {name!r} is read-only")


def _set_static_field(state: LifecycleContextState, name: str, value: Any) -> None:
    current = state.current_record.values[name]
    if current is _SENTINEL:
        state.current_record.values[name] = value
        return
    raise AttributeError(f"static field {name!r} is already initialized")


def _set_local_store_field(state: LifecycleContextState, name: str, value: Any) -> None:
    state.local_store_values[name] = value


def _set_derived_field(state: LifecycleContextState, name: str, value: Any) -> None:
    state.derived_values[name] = value


def _set_default_value_field_for_index(
    state: LifecycleContextState,
    name: str,
    value: Any,
    tx_index: int,
) -> None:
    state.require_active_transaction_for_index(tx_index)
    if type(state).__class_ftable_get_default__[name](state, name) == value:
        return
    state.ensure_working_record_for_index(tx_index).values[name] = value


@functools.cache
def _build_default_value_setter(tx_index: int) -> FieldSetter:
    return lambda state, name, value, tx_index=tx_index: _set_default_value_field_for_index(
        state, name, value, tx_index
    )


def _set_default_identity_field_for_index(
    state: LifecycleContextState,
    name: str,
    value: Any,
    tx_index: int,
) -> None:
    state.require_active_transaction_for_index(tx_index)
    if type(state).__class_ftable_get_default__[name](state, name) is value:
        return
    state.ensure_working_record_for_index(tx_index).values[name] = value


@functools.cache
def _build_default_identity_setter(tx_index: int) -> FieldSetter:
    return lambda state, name, value, tx_index=tx_index: _set_default_identity_field_for_index(
        state, name, value, tx_index
    )


def _set_working_value_field_for_index(
    state: LifecycleContextState,
    name: str,
    value: Any,
    tx_index: int,
) -> None:
    state.require_active_transaction_for_index(tx_index)
    if type(state).__class_ftable_get_working__[name](state, name) == value:
        return
    working = state.ensure_working_record_for_index(tx_index)
    working.values[name] = value


@functools.cache
def _build_working_value_setter(tx_index: int) -> FieldSetter:
    return lambda state, name, value, tx_index=tx_index: _set_working_value_field_for_index(
        state, name, value, tx_index
    )


def _set_working_identity_field_for_index(
    state: LifecycleContextState,
    name: str,
    value: Any,
    tx_index: int,
) -> None:
    state.require_active_transaction_for_index(tx_index)
    if type(state).__class_ftable_get_working__[name](state, name) is value:
        return
    working = state.ensure_working_record_for_index(tx_index)
    working.values[name] = value


@functools.cache
def _build_working_identity_setter(tx_index: int) -> FieldSetter:
    return lambda state, name, value, tx_index=tx_index: _set_working_identity_field_for_index(
        state, name, value, tx_index
    )


def _set_default_binding_field_for_index(
    state: LifecycleContextState,
    name: str,
    value: Any,
    tx_index: int,
) -> None:
    state.require_active_transaction_for_index(tx_index)
    current = type(state).__class_ftable_get_default__[name](state, name)
    if current is value:
        return
    state.ensure_working_record_for_index(tx_index).values[name] = value


@functools.cache
def _build_default_binding_setter(tx_index: int) -> FieldSetter:
    return lambda state, name, value, tx_index=tx_index: _set_default_binding_field_for_index(
        state, name, value, tx_index
    )


def _set_working_binding_field_for_index(
    state: LifecycleContextState,
    name: str,
    value: Any,
    tx_index: int,
) -> None:
    state.require_active_transaction_for_index(tx_index)
    current = type(state).__class_ftable_get_working__[name](state, name)
    if current is value:
        return
    working = state.ensure_working_record_for_index(tx_index)
    working.values[name] = value


@functools.cache
def _build_working_binding_setter(tx_index: int) -> FieldSetter:
    return lambda state, name, value, tx_index=tx_index: _set_working_binding_field_for_index(
        state, name, value, tx_index
    )


def _set_default_binding_map_field_for_index(
    state: LifecycleContextState,
    name: str,
    value: Any,
    tx_index: int,
) -> None:
    state.require_active_transaction_for_index(tx_index)
    new_map = _normalize_binding_map_value(name, value)
    working = state.ensure_working_record_for_index(tx_index)
    current_map = state.current_record.values[name]
    old_working_map = working.values.get(name)
    visible_map = old_working_map if old_working_map is not None else current_map
    if _same_binding_map(visible_map, new_map):
        return

    current_counts = _binding_occurrences(current_map)
    previous_counts = _binding_occurrences(old_working_map or {})
    new_counts = _binding_occurrences(new_map)

    for binding_id, (binding_value, new_count) in new_counts.items():
        previous_count = previous_counts.get(binding_id, (binding_value, 0))[1]
        additional = new_count - previous_count
        if additional <= 0:
            continue
        current_count = current_counts.get(binding_id, (binding_value, 0))[1]
        for _ in range(min(additional, current_count)):
            binding_value.inc_ref()

    for binding_id, (binding_value, previous_count) in previous_counts.items():
        next_count = new_counts.get(binding_id, (binding_value, 0))[1]
        removed = previous_count - next_count
        for _ in range(max(0, removed)):
            binding_value.dec_ref()

    working.values[name] = new_map


@functools.cache
def _build_default_binding_map_setter(tx_index: int) -> FieldSetter:
    return lambda state, name, value, tx_index=tx_index: _set_default_binding_map_field_for_index(
        state, name, value, tx_index
    )


def _set_working_binding_map_field_for_index(
    state: LifecycleContextState,
    name: str,
    value: Any,
    tx_index: int,
) -> None:
    _set_default_binding_map_field_for_index(state, name, value, tx_index)


@functools.cache
def _build_working_binding_map_setter(tx_index: int) -> FieldSetter:
    return lambda state, name, value, tx_index=tx_index: _set_working_binding_map_field_for_index(
        state, name, value, tx_index
    )


def _commit_overlay_field_for_index(state: LifecycleContextState, name: str, tx_index: int) -> None:
    working = state.working_record_for_index(tx_index)
    if working is None:
        return
    if name in working.values:
        spec = type(state).__field_specs__[name]
        next_value = working.values[name]
        if spec.freeze is not None:
            next_value = spec.freeze(next_value)
        state.current_record.values[name] = next_value
    if name in working.field_state:
        state.current_record.field_state[name] = working.field_state[name]


@functools.cache
def _build_overlay_commit_hook(tx_index: int) -> FieldHook:
    return lambda state, name, tx_index=tx_index: _commit_overlay_field_for_index(state, name, tx_index)


def _commit_binding_field_for_index(state: LifecycleContextState, name: str, tx_index: int) -> None:
    working = state.working_record_for_index(tx_index)
    if working is None or name not in working.values:
        return
    current = state.current_record.values[name]
    next_value = working.values[name]
    if next_value is not None and next_value is not current:
        next_value.accepted()
    if current is not None and current is not next_value:
        state.defer_commit_cleanup(current.dec_ref)
    state.current_record.values[name] = next_value


@functools.cache
def _build_binding_commit_hook(tx_index: int) -> FieldHook:
    return lambda state, name, tx_index=tx_index: _commit_binding_field_for_index(state, name, tx_index)


def _rollback_binding_field_for_index(state: LifecycleContextState, name: str, tx_index: int) -> None:
    working = state.working_record_for_index(tx_index)
    if working is None or name not in working.values:
        return
    staged = working.values[name]
    current = state.current_record.values[name]
    if staged is not None and staged is not current:
        staged.dec_ref()


def _close_binding_field(state: LifecycleContextState, name: str) -> None:
    current = state.current_record.values[name]
    if current is not None:
        current.dec_ref()


@functools.cache
def _build_binding_rollback_hook(tx_index: int) -> FieldHook:
    return lambda state, name, tx_index=tx_index: _rollback_binding_field_for_index(state, name, tx_index)


def _commit_binding_map_field_for_index(state: LifecycleContextState, name: str, tx_index: int) -> None:
    working = state.working_record_for_index(tx_index)
    if working is None or name not in working.values:
        return
    current_map = state.current_record.values[name]
    next_map = working.values[name]
    _accept_binding_map(next_map)
    state.defer_commit_cleanup(lambda current_map=current_map: _release_binding_map(current_map))
    state.current_record.values[name] = next_map


@functools.cache
def _build_binding_map_commit_hook(tx_index: int) -> FieldHook:
    return lambda state, name, tx_index=tx_index: _commit_binding_map_field_for_index(state, name, tx_index)


def _rollback_binding_map_field_for_index(state: LifecycleContextState, name: str, tx_index: int) -> None:
    working = state.working_record_for_index(tx_index)
    if working is None or name not in working.values:
        return
    _release_binding_map(working.values[name])


@functools.cache
def _build_binding_map_rollback_hook(tx_index: int) -> FieldHook:
    return lambda state, name, tx_index=tx_index: _rollback_binding_map_field_for_index(state, name, tx_index)


def _close_binding_map_field(state: LifecycleContextState, name: str) -> None:
    _release_binding_map(state.current_record.values[name])


def _rollback_overlay_field(state: LifecycleContextState, name: str) -> None:
    del state, name


def _close_noop(state: LifecycleContextState, name: str) -> None:
    del state, name


def _close_local_store_field(state: LifecycleContextState, name: str) -> None:
    state.reset_to_default(name)


def _reset_derived_field(state: LifecycleContextState, name: str) -> None:
    state.reset_to_default(name)


class LifecycleContextState:
    __field_specs__: dict[str, FieldSpec] = {}
    __field_names__: tuple[str, ...] = ()
    __class_tx_groups__: tuple[Hashable, ...] = (DEFAULT_TRANSACTION,)
    __class_tx_group_to_index__: dict[Hashable, int] = {DEFAULT_TRANSACTION: 0}
    __class_commit_order_key_by_group__: dict[Hashable, str] = {}
    __class_commit_validator_by_group__: dict[Hashable, str] = {}
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
    __class_ftable_tx_index__: dict[str, int] = {}
    __class_ftable_default_factory_runner__: dict[str, FactoryRunner] = {}
    __class_ftable_working_default_factory_runner__: dict[str, FactoryRunner] = {}
    __class_ftable_before_commit_runners__: dict[Hashable, tuple[InjectedRunner, ...]] = {}
    __class_ftable_after_commit_runners__: dict[Hashable, tuple[InjectedRunner, ...]] = {}
    __class_ftable_after_rollback_runners__: dict[Hashable, tuple[InjectedRunner, ...]] = {}

    __slots__ = (
        "owner",
        "transaction_manager",
        "current_record",
        "_tx_state_by_index",
        "ever_committed",
        "local_store_values",
        "derived_values",
        "unmanaged_store",
        "closed",
        "current_view",
        "working_view",
        "_resolving_factories",
        "_deferred_commit_cleanup",
    )

    def __init__(
        self,
        owner: LifecycleContext,
        *,
        transaction_manager: TransactionManager | None,
        values: dict[str, Any],
    ) -> None:
        self.owner = owner
        object.__setattr__(owner, "_state", self)
        self.transaction_manager = transaction_manager
        self.current_record = Record()
        self._tx_state_by_index = [_LifecycleTxState() for _ in type(self).__class_tx_groups__]
        self.ever_committed = False
        self.local_store_values: dict[str, Any] = {}
        self.derived_values: dict[str, Any] = {}
        self.unmanaged_store: dict[str, Any] = {}
        self.closed = False
        self.current_view = type(owner).__current_view_cls__(_state=self, _owner=owner)
        self.working_view = type(owner).__working_view_cls__(_state=self, _owner=owner)
        self._resolving_factories: list[tuple[str, str]] = []
        self._deferred_commit_cleanup: list[Callable[[], None]] | None = None

        for name, spec in type(self).__field_specs__.items():
            spec.kind.initialize_constructor_value(state=self, name=name, values=values)

        if values:
            unexpected = ", ".join(sorted(values))
            raise TypeError(f"unexpected lifecycle constructor fields: {unexpected}")

        for name, spec in type(self).__field_specs__.items():
            if issubclass(spec.kind, NonStoredHookKind):
                continue
            self.resolve_default_field(name)

    def get_field(self, name: str) -> Any:
        return type(self).__class_ftable_get_default__[name](self, name)

    def set_field(self, name: str, value: Any) -> None:
        type(self).__class_ftable_set_default__[name](self, name, value)

    def get_current_field(self, name: str) -> Any:
        return type(self).__class_ftable_get_current__[name](self, name)

    def get_working_field(self, name: str) -> Any:
        return type(self).__class_ftable_get_working__[name](self, name)

    def set_working_field(self, name: str, value: Any) -> None:
        type(self).__class_ftable_set_working__[name](self, name, value)

    @property
    def working_record(self) -> Record | None:
        return self._tx_state_by_index[0].working_record

    @working_record.setter
    def working_record(self, value: Record | None) -> None:
        self._tx_state_by_index[0].working_record = value

    @property
    def working_tx_id(self) -> int | None:
        return self._tx_state_by_index[0].working_tx_id

    @working_tx_id.setter
    def working_tx_id(self, value: int | None) -> None:
        self._tx_state_by_index[0].working_tx_id = value

    def tx_state_for_index(self, tx_index: int) -> _LifecycleTxState:
        return self._tx_state_by_index[tx_index]

    def working_record_for_index(self, tx_index: int) -> Record | None:
        return self._tx_state_by_index[tx_index].working_record

    def working_tx_id_for_index(self, tx_index: int) -> int | None:
        return self._tx_state_by_index[tx_index].working_tx_id

    def tx_index_for_group(self, tx_group: Hashable) -> int:
        try:
            return type(self).__class_tx_group_to_index__[tx_group]
        except KeyError as exc:
            raise RuntimeError(f"unknown lifecycle transaction group {tx_group!r}") from exc

    def tx_index_for_field(self, name: str) -> int:
        return type(self).__class_ftable_tx_index__[name]

    def get_field_state(self, name: str) -> Any:
        tx_index = self.tx_index_for_field(name)
        working = self.working_record_for_index(tx_index)
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
        tx_index = self.tx_index_for_field(name)
        state_factory = type(self).__class_ftable_state_factory__[name]
        if state_factory is None:
            raise RuntimeError(f"field {name!r} does not define runtime state")
        working = self.ensure_working_record_for_index(tx_index)
        if name not in working.field_state:
            current_state = self.get_current_field_state(name)
            state_copy = type(self).__class_ftable_state_copy__[name] or copy.copy
            working.field_state[name] = state_copy(current_state)
        return working.field_state[name]

    def ensure_working_record_for_index(self, tx_index: int) -> Record:
        tx_state = self.tx_state_for_index(tx_index)
        working = tx_state.working_record
        if working is not None:
            self.require_active_transaction_for_index(tx_index)
            return working

        self.require_active_transaction_for_index(tx_index)

        working = Record()
        tx_state.working_record = working
        tx_group = type(self).__class_tx_groups__[tx_index]
        tx_state.working_tx_id = self.transaction_manager.enlist(self.owner, tx_group)
        return working

    def ensure_working_record(self) -> Record:
        return self.ensure_working_record_for_index(0)

    def require_active_transaction_for_index(self, tx_index: int) -> None:
        tx_group = type(self).__class_tx_groups__[tx_index]
        transaction = (
            self.transaction_manager.active_transaction_for(tx_group)
            if self.transaction_manager is not None
            else None
        )
        tx_state = self.tx_state_for_index(tx_index)
        if transaction is None:
            if tx_state.working_record is not None:
                raise RuntimeError("stale lifecycle working record without an active transaction")
            raise RuntimeError("writes require an active lifecycle transaction")
        if tx_state.working_record is not None and tx_state.working_tx_id != transaction.tx_id:
            raise RuntimeError("working record belongs to a different lifecycle transaction")

    def require_active_transaction(self) -> None:
        self.require_active_transaction_for_index(0)

    def snapshot_current(self) -> _RecordSnapshot:
        return _RecordSnapshot(self.current_record.values)

    def _default_store_contains(self, name: str) -> bool:
        return type(self).__field_specs__[name].kind.default_store_contains(state=self, name=name)

    def _get_default_store_value(self, name: str) -> Any:
        return type(self).__field_specs__[name].kind.get_default_store_value(state=self, name=name)

    def _set_default_store_value(self, name: str, value: Any) -> Any:
        return type(self).__field_specs__[name].kind.set_default_store_value(
            state=self,
            name=name,
            value=value,
        )

    def _run_factory_runner(self, kind: str, name: str, runner: FactoryRunner) -> Any:
        key = (kind, name)
        if key in self._resolving_factories:
            cycle = " -> ".join(
                f"{step_kind}:{step_name}" for step_kind, step_name in (*self._resolving_factories, key)
            )
            raise RuntimeError(f"lifecycle factory cycle detected: {cycle}")
        self._resolving_factories.append(key)
        try:
            return runner(self)
        finally:
            popped = self._resolving_factories.pop()
            assert popped == key

    def resolve_default_field(self, name: str) -> Any:
        if self._default_store_contains(name):
            return self._get_default_store_value(name)
        runner = type(self).__class_ftable_default_factory_runner__.get(name)
        if runner is not None:
            value = self._run_factory_runner("default_factory", name, runner)
        else:
            spec = type(self).__field_specs__[name]
            value = spec.kind.default_value(spec)
        return self._set_default_store_value(name, value)

    def resolve_working_default_field(self, name: str) -> Any:
        return self.resolve_working_default_field_for_index(name, 0)

    def resolve_working_default_field_for_index(self, name: str, tx_index: int) -> Any:
        self.require_active_transaction_for_index(tx_index)
        working = self.ensure_working_record_for_index(tx_index)
        if name in working.values:
            return working.values[name]
        runner = type(self).__class_ftable_working_default_factory_runner__.get(name)
        if runner is None:
            return self.resolve_default_field(name)
        value = self._run_factory_runner("working_default_factory", name, runner)
        working.values[name] = value
        return value

    def commit_order_key_for(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> tuple[Any, ...]:
        field_name = type(self).__class_commit_order_key_by_group__.get(tx_group)
        if field_name is None:
            return ()
        return self.current_record.values[field_name]

    def commit_validator_for(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> Any:
        field_name = type(self).__class_commit_validator_by_group__.get(tx_group)
        if field_name is None:
            return None
        return self.current_record.values[field_name]

    def defer_commit_cleanup(self, callback: Callable[[], None]) -> None:
        if self._deferred_commit_cleanup is None:
            callback()
            return
        self._deferred_commit_cleanup.append(callback)

    def _run_before_commit_hooks(
        self,
        tx_group: Hashable,
        *,
        current: _ManagedContextBase,
        working: _ManagedContextBase,
    ) -> None:
        self.owner.before_commit(current, working)
        injected = {
            "current": current,
            "working": working,
            "tx_group": tx_group,
        }
        for runner in type(self).__class_ftable_before_commit_runners__.get(tx_group, ()):
            runner(self, injected)

    def _run_after_commit_hooks(
        self,
        tx_group: Hashable,
        *,
        previous: _RecordSnapshot,
        current: _ManagedContextBase,
    ) -> None:
        self.owner.after_commit(previous, self.snapshot_current())
        injected = {
            "previous": previous,
            "current": current,
            "tx_group": tx_group,
        }
        for runner in type(self).__class_ftable_after_commit_runners__.get(tx_group, ()):
            runner(self, injected)

    def _run_after_rollback_hooks(
        self,
        tx_group: Hashable,
        *,
        current: _ManagedContextBase,
    ) -> None:
        self.owner.after_rollback(self.snapshot_current())
        injected = {
            "current": current,
            "tx_group": tx_group,
        }
        for runner in type(self).__class_ftable_after_rollback_runners__.get(tx_group, ()):
            runner(self, injected)

    def reset_to_default(self, name: str) -> Any:
        type(self).__field_specs__[name].kind.reset_default_store(state=self, name=name)
        return self.resolve_default_field(name)

    def commit(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> _ManagedContextBase:
        tx_index = self.tx_index_for_group(tx_group)
        tx_state = self.tx_state_for_index(tx_index)
        if tx_state.working_record is None:
            return self.owner.current

        if self.transaction_manager is not None and tx_state.working_tx_id is not None:
            self.transaction_manager.drop(self.owner, tx_state.working_tx_id, tx_group)

        previous = self.snapshot_current()
        committed = False
        self._deferred_commit_cleanup = []
        try:
            self._run_before_commit_hooks(
                tx_group,
                current=self.current_view,
                working=self.working_view,
            )
            for name in type(self).__field_names__:
                if self.tx_index_for_field(name) != tx_index:
                    continue
                type(self).__class_ftable_commit_field__[name](self, name)
            tx_state.working_record = None
            tx_state.working_tx_id = None
            self.ever_committed = True
            committed = True
            current = self.owner.current
            try:
                self._run_after_commit_hooks(tx_group, previous=previous, current=current)
            finally:
                for callback in self._deferred_commit_cleanup:
                    callback()
        except BaseException:
            if not committed and tx_state.working_record is not None:
                for name in type(self).__field_names__:
                    if self.tx_index_for_field(name) != tx_index:
                        continue
                    type(self).__class_ftable_rollback_field__[name](self, name)
                tx_state.working_record = None
                tx_state.working_tx_id = None
            raise
        finally:
            self._deferred_commit_cleanup = None
        return self.owner.current

    def rollback(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> _ManagedContextBase:
        tx_index = self.tx_index_for_group(tx_group)
        tx_state = self.tx_state_for_index(tx_index)
        if tx_state.working_record is None:
            return self.owner.current

        if self.transaction_manager is not None and tx_state.working_tx_id is not None:
            self.transaction_manager.drop(self.owner, tx_state.working_tx_id, tx_group)

        for name in type(self).__field_names__:
            if self.tx_index_for_field(name) != tx_index:
                continue
            type(self).__class_ftable_rollback_field__[name](self, name)
        tx_state.working_record = None
        tx_state.working_tx_id = None
        self._run_after_rollback_hooks(tx_group, current=self.owner.current)
        return self.owner.current

    def commit_transaction(
        self,
        tx_id: int,
        tx_group: Hashable = DEFAULT_TRANSACTION,
    ) -> _ManagedContextBase:
        tx_index = self.tx_index_for_group(tx_group)
        if self.working_tx_id_for_index(tx_index) != tx_id:
            return self.owner.current
        return self.commit(tx_group)

    def rollback_transaction(
        self,
        tx_id: int,
        tx_group: Hashable = DEFAULT_TRANSACTION,
    ) -> _ManagedContextBase:
        tx_index = self.tx_index_for_group(tx_group)
        if self.working_tx_id_for_index(tx_index) != tx_id:
            return self.owner.current
        return self.rollback(tx_group)

    def close(self, *, was_committed: bool = True) -> None:
        del was_committed
        if self.closed:
            return
        for tx_group, tx_index in type(self).__class_tx_group_to_index__.items():
            if self.working_record_for_index(tx_index) is not None:
                self.rollback(tx_group)
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
        if name in type(self).__state_cls__.__field_specs__:
            return self.__get_field__(name)
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
    
    def commit_order_key(self) -> tuple[Any, ...]:
        """Return the sort key used for manager commit ordering (higher sorts first).

        Declare the value with the ``commit_order_key`` field helper using another
        attribute name so this method is not shadowed.
        """
        return self._state.commit_order_key_for()

    def commit_order_key_for(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> tuple[Any, ...]:
        return self._state.commit_order_key_for(tx_group)
    
    def requires_validation(self) -> bool:
        """Return True if the context requires validation before commit, False otherwise."""
        return self._state.commit_validator_for() is not None

    def requires_validation_for(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> bool:
        return self._state.commit_validator_for(tx_group) is not None

    def validate_commit(self) -> bool:
        """Return True if the context is valid and can be committed, False otherwise."""
        validator = self._state.commit_validator_for()
        if validator is not None:
            return validator(self)
        return True

    def validate_commit_for(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> bool:
        validator = self._state.commit_validator_for(tx_group)
        if validator is not None:
            return validator(self)
        return True

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

    def commit(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> _ManagedContextBase:
        return self._state.commit(tx_group)

    def rollback(self, tx_group: Hashable = DEFAULT_TRANSACTION) -> _ManagedContextBase:
        return self._state.rollback(tx_group)

    def _commit_transaction(
        self,
        tx_id: int,
        tx_group: Hashable = DEFAULT_TRANSACTION,
    ) -> _ManagedContextBase:
        return self._state.commit_transaction(tx_id, tx_group)

    def _rollback_transaction(
        self,
        tx_id: int,
        tx_group: Hashable = DEFAULT_TRANSACTION,
    ) -> _ManagedContextBase:
        return self._state.rollback_transaction(tx_id, tx_group)


LifecycleContext = _ManagedContextBase


def _build_hook_runner_tables(
    specs: dict[str, FieldSpec],
) -> dict[str, dict[Hashable, tuple[InjectedRunner, ...]]]:
    hook_tables = HookRunnerTables()
    for name, spec in specs.items():
        spec.kind.register_hook_runner(name=name, spec=spec, hook_tables=hook_tables)

    return {
        "__class_ftable_before_commit_runners__": {
            tx_group: tuple(runners) for tx_group, runners in hook_tables.before_commit.items()
        },
        "__class_ftable_after_commit_runners__": {
            tx_group: tuple(runners) for tx_group, runners in hook_tables.after_commit.items()
        },
        "__class_ftable_after_rollback_runners__": {
            tx_group: tuple(runners) for tx_group, runners in hook_tables.after_rollback.items()
        },
    }


def _build_class_tables(
    specs: dict[str, FieldSpec],
    *,
    tx_group_to_index: dict[Hashable, int],
) -> dict[str, dict[str, Callable[..., Any]]]:
    tables = _FieldTables()
    for name, spec in specs.items():
        tx_index = tx_group_to_index[spec.tx_group]
        tables.field_tx_index[name] = tx_index
        if spec.default_factory is not MISSING:
            tables.default_factory_runner[name] = _compile_factory_runner(
                field_name=name,
                hook_name="default_factory",
                factory=typing.cast(Callable[..., Any], spec.default_factory),
            )
        if spec.working_default_factory is not MISSING:
            tables.working_default_factory_runner[name] = _compile_factory_runner(
                field_name=name,
                hook_name="working_default_factory",
                factory=typing.cast(Callable[..., Any], spec.working_default_factory),
            )
        spec.kind.install_field_tables(name=name, spec=spec, tx_index=tx_index, tables=tables)

    return {
        "__class_ftable_get_default__": tables.get_default,
        "__class_ftable_get_current__": tables.get_current,
        "__class_ftable_get_working__": tables.get_working,
        "__class_ftable_set_default__": tables.set_default,
        "__class_ftable_set_working__": tables.set_working,
        "__class_ftable_commit_field__": tables.commit_field,
        "__class_ftable_rollback_field__": tables.rollback_field,
        "__class_ftable_close_field__": tables.close_field,
        "__class_ftable_state_factory__": tables.state_factory,
        "__class_ftable_state_copy__": tables.state_copy,
        "__class_ftable_tx_index__": tables.field_tx_index,
        "__class_ftable_default_factory_runner__": tables.default_factory_runner,
        "__class_ftable_working_default_factory_runner__": tables.working_default_factory_runner,
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
    base.kind.validate_override(base, derived)
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
    working_default_factory = (
        derived.working_default_factory
        if derived.working_default_factory is not MISSING
        else base.working_default_factory
    )
    state_factory = derived.state_factory if derived.state_factory is not None else base.state_factory
    state_copy = derived.state_copy if derived.state_copy is not None else base.state_copy
    initial_working = (
        derived.initial_working if derived.initial_working is not MISSING else base.initial_working
    )
    freeze = derived.freeze if derived.freeze is not None else base.freeze
    thaw = derived.thaw if derived.thaw is not None else base.thaw

    merged = FieldSpec(
        name=base.name,
        kind=base.kind,
        annotation=derived.annotation,
        compare=base.compare,
        tx_group=base.tx_group,
        default=default,
        default_factory=default_factory,
        working_default_factory=working_default_factory,
        initial_working=initial_working,
        freeze=freeze,
        thaw=thaw,
        state_factory=state_factory,
        state_copy=state_copy,
    )
    merged.kind.validate_field_spec(merged)
    return merged


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

    tx_groups: list[Hashable] = [DEFAULT_TRANSACTION]
    for spec in merged_specs.values():
        if spec.tx_group not in tx_groups:
            tx_groups.append(spec.tx_group)
    tx_group_to_index = {tx_group: index for index, tx_group in enumerate(tx_groups)}

    special_tables = SpecialFieldTables()
    for name, spec in merged_specs.items():
        spec.kind.register_special_field(name=name, spec=spec, special_tables=special_tables)

    state_name = f"{wrapped.__name__}_State"
    state_namespace = {
        "__module__": wrapped.__module__,
        "__field_specs__": merged_specs,
        "__class_tx_groups__": tuple(tx_groups),
        "__class_tx_group_to_index__": tx_group_to_index,
        "__class_commit_order_key_by_group__": special_tables.commit_order_key_by_group,
        "__class_commit_validator_by_group__": special_tables.commit_validator_by_group,
    }
    state_cls = type(state_name, (base_state_cls,), state_namespace)
    state_cls.__field_names__ = tuple(state_cls.__field_specs__)
    for table_name, table in _build_class_tables(
        state_cls.__field_specs__,
        tx_group_to_index=state_cls.__class_tx_group_to_index__,
    ).items():
        setattr(state_cls, table_name, table)
    for table_name, table in _build_hook_runner_tables(state_cls.__field_specs__).items():
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
    "BindingBase",
    "DEFAULT_TRANSACTION",
    "GroupTransactionManager",
    "LCKind",
    "LifecycleContext",
    "LifecycleTransaction",
    "LifecycleValidatorReturnedFalse",
    "Record",
    "TransactionManager",
    "lifecycle_field",
    "managed_context",
]
