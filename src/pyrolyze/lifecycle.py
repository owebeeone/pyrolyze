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
- ``managed_context``
- ``LifecycleContext``
- ``TransactionManager``
"""

import copy
from abc import ABC, abstractmethod
from collections.abc import Mapping
from collections.abc import Callable
from dataclasses import MISSING, dataclass, field
import inspect
import types
import typing
from typing import Any

from pyrolyze.type_annotations import is_annotation_narrower_or_equal

_SENTINEL = object()


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
    validator_contexts: dict[int, LifecycleContext] = field(default_factory=dict)

    def commit_order(self) -> tuple[LifecycleContext, ...]:
        contexts = list(self.dirty_contexts.values())
        contexts.sort(key=lambda context: context.commit_order_key(), reverse=True)
        return tuple(contexts)

    def rollback_dirty(self) -> None:
        for ctx in list(self.dirty_contexts.values()):
            ctx._rollback_transaction(self.tx_id)

    def validate_commit(self) -> None:
        failures: list[BaseException] = []
        for context in self.validator_contexts.values():
            try:
                ok = context.validate_commit()
            except BaseException as exc:
                failures.append(exc)
                continue
            if not ok:
                failures.append(LifecycleValidatorReturnedFalse(context))
        if failures:
            raise ExceptionGroup("lifecycle commit validation failed", failures)

    def apply_commits(self) -> None:
        for context in self.commit_order():
            context._commit_transaction(self.tx_id)


@dataclass(slots=True)
class TransactionManager:
    _next_tx_id: int = field(default=1, init=False, repr=False)
    active_transaction: LifecycleTransaction | None = field(default=None, init=False, repr=False)
    begin_count: int = field(default=0, init=False, repr=False)

    def begin(self) -> LifecycleTransaction:
        if self.begin_count == 0:
            if self.active_transaction is not None:
                raise RuntimeError("lifecycle transaction manager state is corrupted")
            self.active_transaction = LifecycleTransaction(tx_id=self._next_tx_id)
            self._next_tx_id += 1
        self.begin_count += 1
        transaction = self.active_transaction
        assert transaction is not None
        return transaction

    def commit(self) -> int | None:
        if self.begin_count <= 0:
            raise RuntimeError("no active lifecycle transaction")
        if self.begin_count > 1:
            self.begin_count -= 1
            return None
        transaction = self.active_transaction
        if transaction is None:
            raise RuntimeError("lifecycle transaction manager state is corrupted")
        try:
            transaction.validate_commit()
        except BaseExceptionGroup as exc_group:
            self.rollback()
            raise exc_group
        tx_id = transaction.tx_id
        transaction.apply_commits()
        self.active_transaction = None
        self.begin_count = 0
        return tx_id

    def rollback(self) -> int | None:
        if self.begin_count <= 0 or self.active_transaction is None:
            raise RuntimeError("no active lifecycle transaction")
        transaction = self.active_transaction
        transaction.rollback_dirty()
        tx_id = transaction.tx_id
        self.active_transaction = None
        self.begin_count = 0
        return tx_id

    def enlist(self, context: LifecycleContext) -> int:
        transaction = self.active_transaction
        if transaction is None:
            raise RuntimeError("no active lifecycle transaction")
        transaction.dirty_contexts[id(context)] = context
        if context.requires_validation():
            transaction.validator_contexts[id(context)] = context
        return transaction.tx_id

    def drop(self, context: LifecycleContext, tx_id: int | None = None) -> None:
        transaction = self.active_transaction
        if transaction is None:
            return
        if tx_id is not None and transaction.tx_id != tx_id:
            return
        cid = id(context)
        transaction.dirty_contexts.pop(cid, None)
        transaction.validator_contexts.pop(cid, None)


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

_SUPPORTED_FACTORY_PARAMS = frozenset({"self", "current", "working"})


def _compile_factory_runner(
    *,
    field_name: str,
    hook_name: str,
    factory: Callable[..., Any],
) -> FactoryRunner:
    if inspect.isbuiltin(factory) or inspect.isclass(factory):
        return lambda state, factory=factory: factory()
    try:
        signature = inspect.signature(factory)
    except (TypeError, ValueError):
        return lambda state, factory=factory: factory()
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
            if parameter.name not in _SUPPORTED_FACTORY_PARAMS:
                allowed = ", ".join(sorted(_SUPPORTED_FACTORY_PARAMS))
                raise TypeError(
                    f"{hook_name} for field {field_name!r} uses unsupported parameter "
                    f"{parameter.name!r}; allowed: {allowed}",
                )
            names.append(parameter.name)
        parameter_names = tuple(names)
    if not parameter_names:
        return lambda state, factory=factory: factory()

    def run(state: LifecycleContextState, factory: Callable[..., Any] = factory) -> Any:
        kwargs: dict[str, Any] = {}
        for name in parameter_names:
            if name == "self":
                kwargs[name] = state.owner
            elif name == "current":
                kwargs[name] = state.current_view
            elif name == "working":
                kwargs[name] = state.working_view
            else:
                raise AssertionError(f"unexpected compiled lifecycle factory parameter {name!r}")
        return factory(**kwargs)

    return run


@dataclass(slots=True)
class FieldSpec:
    name: str
    kind: str
    annotation: Any
    compare: str
    default: Any = MISSING
    default_factory: Callable[[], Any] | object = MISSING
    working_default_factory: Callable[[], Any] | object = MISSING
    initial_working: Any = MISSING
    freeze: Callable[[Any], Any] | None = None
    thaw: Callable[[Any], Any] | None = None
    state_factory: FieldStateFactory | None = None
    state_copy: StateCopyHelper | None = None

    def default_value(self) -> Any:
        if self.kind == "static":
            if self.default is MISSING and self.default_factory is MISSING:
                return _SENTINEL
        if self.kind == "commit_order_key":
            if self.default is not MISSING:
                return self.default
            if self.default_factory is not MISSING:
                return self.default_factory()
            return ()
        if self.kind == "commit_validator":
            if self.default is not MISSING:
                return self.default
            return None
        if self.default is not MISSING:
            return self.default
        if self.default_factory is not MISSING:
            return self.default_factory()
        raise TypeError(f"missing required lifecycle field {self.name!r}")


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
        "working_default_factory",
    )

    def __init__(
        self,
        *,
        kind: str = "managed",
        compare: str = "value",
        default: Any = MISSING,
        default_factory: Callable[[], Any] | object = MISSING,
        working_default_factory: Callable[[], Any] | object = MISSING,
        initial_working: Any = MISSING,
        freeze: Callable[[Any], Any] | None = None,
        thaw: Callable[[Any], Any] | None = None,
        state_factory: Callable[[], Any] | None = None,
        state_copy: StateCopyHelper | None = None,
    ) -> None:
        if kind not in {
            "managed",
            "const",
            "static",
            "binding",
            "owned",
            "transient",
            "local_store",
            "derived",
            "commit_order_key",
            "commit_validator",
        }:
            raise TypeError(f"unsupported lifecycle field kind {kind!r}")
        if compare not in {"value", "identity"}:
            raise TypeError(f"unsupported compare mode {compare!r}")
        if default is not MISSING and default_factory is not MISSING:
            raise TypeError("lifecycle fields cannot define both default and default_factory")
        if working_default_factory is not MISSING and kind != "transient":
            raise TypeError("only transient fields can define working_default_factory")
        if kind == "commit_validator":
            if default_factory is not MISSING:
                raise TypeError("commit_validator fields cannot define default_factory")
            if initial_working is not MISSING:
                raise TypeError("commit_validator fields cannot define initial_working")
        if (
            kind
            in {
                "const",
                "static",
                "binding",
                "owned",
                "transient",
                "local_store",
                "derived",
                "commit_order_key",
                "commit_validator",
            }
            and state_factory is not None
        ):
            raise TypeError(f"{kind} fields cannot define state_factory")
        self.compare = compare
        self.default = default
        self.default_factory = default_factory
        self.working_default_factory = working_default_factory
        self.initial_working = initial_working
        self.freeze = freeze
        self.kind = kind
        self.state_factory = state_factory
        self.state_copy = state_copy or copy.copy
        self.thaw = thaw
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
            kind=self.kind,
            annotation=annotation,
            compare=self.compare,
            default=self.default,
            default_factory=self.default_factory,
            working_default_factory=self.working_default_factory,
            initial_working=self.initial_working,
            freeze=self.freeze,
            thaw=self.thaw,
            state_factory=self.state_factory,
            state_copy=self.state_copy,
        )

    def name_or_error(self) -> str:
        if self.name is None:
            raise RuntimeError("lifecycle field name was not initialized")
        return self.name


def lifecycle_field(
    *,
    kind: str = "managed",
    compare: str = "value",
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
        default=default,
        default_factory=default_factory,
        working_default_factory=working_default_factory,
        initial_working=initial_working,
        freeze=freeze,
        state_factory=state_factory,
        state_copy=state_copy,
        thaw=thaw,
    )


def const(
    *,
    default: Any = MISSING,
    default_factory: Callable[[], Any] | object = MISSING,
) -> Any:
    return lifecycle_field(
        kind="const",
        default=default,
        default_factory=default_factory,
    )


def managed(
    *,
    compare: str = "value",
    default: Any = MISSING,
    default_factory: Callable[[], Any] | object = MISSING,
    initial_working: Any = MISSING,
    freeze: Callable[[Any], Any] | None = None,
    thaw: Callable[[Any], Any] | None = None,
    state_factory: Callable[[], Any] | None = None,
    state_copy: StateCopyHelper | None = None,
) -> Any:
    return lifecycle_field(
        kind="managed",
        compare=compare,
        default=default,
        default_factory=default_factory,
        initial_working=initial_working,
        freeze=freeze,
        state_factory=state_factory,
        state_copy=state_copy,
        thaw=thaw,
    )


def static(
    *,
    default: Any = MISSING,
    default_factory: Callable[[], Any] | object = MISSING,
) -> Any:
    return lifecycle_field(
        kind="static",
        default=default,
        default_factory=default_factory,
    )


def binding(
    *,
    default: Any = MISSING,
    default_factory: Callable[[], Any] | object = MISSING,
) -> Any:
    return lifecycle_field(
        kind="binding",
        compare="identity",
        default=default,
        default_factory=default_factory,
    )


def owned(
    *,
    default: Any = MISSING,
    default_factory: Callable[[], Any] | object = MISSING,
) -> Any:
    return lifecycle_field(
        kind="owned",
        compare="identity",
        default=default,
        default_factory=default_factory,
    )


def transient(
    *,
    default: Any = MISSING,
    default_factory: Callable[[], Any] | object = MISSING,
    working_default_factory: Callable[[], Any] | object = MISSING,
) -> Any:
    return lifecycle_field(
        kind="transient",
        compare="value",
        default=default,
        default_factory=default_factory,
        working_default_factory=working_default_factory,
    )


def local_store(
    *,
    default: Any = MISSING,
    default_factory: Callable[[], Any] | object = MISSING,
) -> Any:
    return lifecycle_field(
        kind="local_store",
        compare="value",
        default=default,
        default_factory=default_factory,
    )


def derived(
    *,
    default: Any = MISSING,
    default_factory: Callable[[], Any] | object = MISSING,
) -> Any:
    return lifecycle_field(
        kind="derived",
        compare="value",
        default=default,
        default_factory=default_factory,
    )


def commit_order_key(
    *,
    default: Any = MISSING,
    default_factory: Callable[[], Any] | object = MISSING,
) -> Any:
    return lifecycle_field(
        kind="commit_order_key",
        compare="value",
        default=default,
        default_factory=default_factory,
    )


def commit_validator(*, default: Any = MISSING) -> Any:
    return lifecycle_field(
        kind="commit_validator",
        compare="identity",
        default=default,
    )


def _get_default_overlay_field(state: LifecycleContextState, name: str) -> Any:
    working = state.working_record
    if working is not None and name in working.values:
        return working.values[name]
    return state.resolve_default_field(name)


def _get_current_field(state: LifecycleContextState, name: str) -> Any:
    return state.resolve_default_field(name)


def _get_working_overlay_field(state: LifecycleContextState, name: str) -> Any:
    working = state.working_record
    if working is not None and name in working.values:
        return working.values[name]
    return state.resolve_default_field(name)


def _get_managed_initial_working_field(state: LifecycleContextState, name: str) -> Any:
    working = state.working_record
    if working is not None and name in working.values:
        return working.values[name]
    transaction = state.transaction_manager.active_transaction if state.transaction_manager is not None else None
    spec = type(state).__field_specs__[name]
    if transaction is not None and not state.ever_committed and spec.initial_working is not MISSING:
        return spec.initial_working
    return state.resolve_default_field(name)


def _get_managed_thawed_field(state: LifecycleContextState, name: str) -> Any:
    working = state.working_record
    if working is not None and name in working.values:
        return working.values[name]
    transaction = state.transaction_manager.active_transaction if state.transaction_manager is not None else None
    spec = type(state).__field_specs__[name]
    if transaction is None or spec.thaw is None:
        return state.resolve_default_field(name)
    working = state.ensure_working_record()
    if name not in working.values:
        working.values[name] = spec.thaw(state.resolve_default_field(name))
    return working.values[name]


def _get_transient_working_default_field(state: LifecycleContextState, name: str) -> Any:
    working = state.working_record
    if working is not None and name in working.values:
        return working.values[name]
    transaction = state.transaction_manager.active_transaction if state.transaction_manager is not None else None
    if transaction is not None and name in type(state).__class_ftable_working_default_factory_runner__:
        return state.resolve_working_default_field(name)
    return state.resolve_default_field(name)


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


def _set_default_value_field(state: LifecycleContextState, name: str, value: Any) -> None:
    state.require_active_transaction()
    if type(state).__class_ftable_get_default__[name](state, name) == value:
        return
    state.ensure_working_record().values[name] = value


def _set_default_identity_field(state: LifecycleContextState, name: str, value: Any) -> None:
    state.require_active_transaction()
    if type(state).__class_ftable_get_default__[name](state, name) is value:
        return
    state.ensure_working_record().values[name] = value


def _set_working_value_field(state: LifecycleContextState, name: str, value: Any) -> None:
    state.require_active_transaction()
    if type(state).__class_ftable_get_working__[name](state, name) == value:
        return
    working = state.ensure_working_record()
    working.values[name] = value


def _set_working_identity_field(state: LifecycleContextState, name: str, value: Any) -> None:
    state.require_active_transaction()
    if type(state).__class_ftable_get_working__[name](state, name) is value:
        return
    working = state.ensure_working_record()
    working.values[name] = value


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


def _set_default_binding_field(state: LifecycleContextState, name: str, value: Any) -> None:
    state.require_active_transaction()
    current = type(state).__class_ftable_get_default__[name](state, name)
    if current is value:
        return
    state.ensure_working_record().values[name] = value


def _set_working_binding_field(state: LifecycleContextState, name: str, value: Any) -> None:
    state.require_active_transaction()
    current = type(state).__class_ftable_get_working__[name](state, name)
    if current is value:
        return
    working = state.ensure_working_record()
    working.values[name] = value


def _set_default_binding_map_field(state: LifecycleContextState, name: str, value: Any) -> None:
    state.require_active_transaction()
    new_map = _normalize_binding_map_value(name, value)
    working = state.ensure_working_record()
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


def _set_working_binding_map_field(state: LifecycleContextState, name: str, value: Any) -> None:
    _set_default_binding_map_field(state, name, value)


def _commit_overlay_field(state: LifecycleContextState, name: str) -> None:
    working = state.working_record
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


def _commit_binding_field(state: LifecycleContextState, name: str) -> None:
    working = state.working_record
    if working is None or name not in working.values:
        return
    current = state.current_record.values[name]
    next_value = working.values[name]
    if next_value is not None and next_value is not current:
        next_value.accepted()
    if current is not None and current is not next_value:
        current.dec_ref()
    state.current_record.values[name] = next_value


def _rollback_binding_field(state: LifecycleContextState, name: str) -> None:
    working = state.working_record
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


def _commit_binding_map_field(state: LifecycleContextState, name: str) -> None:
    working = state.working_record
    if working is None or name not in working.values:
        return
    current_map = state.current_record.values[name]
    next_map = working.values[name]
    _accept_binding_map(next_map)
    _release_binding_map(current_map)
    state.current_record.values[name] = next_map


def _rollback_binding_map_field(state: LifecycleContextState, name: str) -> None:
    working = state.working_record
    if working is None or name not in working.values:
        return
    _release_binding_map(working.values[name])


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
    __class_ftable_default_factory_runner__: dict[str, FactoryRunner] = {}
    __class_ftable_working_default_factory_runner__: dict[str, FactoryRunner] = {}

    __slots__ = (
        "owner",
        "transaction_manager",
        "current_record",
        "working_record",
        "working_tx_id",
        "ever_committed",
        "local_store_values",
        "derived_values",
        "unmanaged_store",
        "closed",
        "current_view",
        "working_view",
        "_commit_order_key",
        "commit_validator",
        "_resolving_factories",
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
        self.working_record: Record | None = None
        self.working_tx_id: int | None = None
        self.ever_committed = False
        self.local_store_values: dict[str, Any] = {}
        self.derived_values: dict[str, Any] = {}
        self.unmanaged_store: dict[str, Any] = {}
        self.closed = False
        self.current_view = type(owner).__current_view_cls__(_state=self, _owner=owner)
        self.working_view = type(owner).__working_view_cls__(_state=self, _owner=owner)
        self._resolving_factories: list[tuple[str, str]] = []

        for name, spec in type(self).__field_specs__.items():
            if spec.kind == "local_store":
                if name in values:
                    self.local_store_values[name] = values.pop(name)
                continue
            if spec.kind == "derived":
                if name in values:
                    self.derived_values[name] = values.pop(name)
                continue
            if name in values:
                self.current_record.values[name] = values.pop(name)

        if values:
            unexpected = ", ".join(sorted(values))
            raise TypeError(f"unexpected lifecycle constructor fields: {unexpected}")

        for name in type(self).__field_specs__:
            self.resolve_default_field(name)

        commit_key_names = [n for n, s in type(self).__field_specs__.items() if s.kind == "commit_order_key"]
        if len(commit_key_names) > 1:
            raise TypeError("at most one commit_order_key field is allowed")
        if commit_key_names:
            self._commit_order_key = self.current_record.values[commit_key_names[0]]
        else:
            self._commit_order_key = ()

        validator_names = [n for n, s in type(self).__field_specs__.items() if s.kind == "commit_validator"]
        if len(validator_names) > 1:
            raise TypeError("at most one commit_validator field is allowed")
        if validator_names:
            self.commit_validator = self.current_record.values[validator_names[0]]
        else:
            self.commit_validator = None

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
            self.require_active_transaction()
            return working

        self.require_active_transaction()

        working = Record()
        self.working_record = working
        self.working_tx_id = self.transaction_manager.enlist(self.owner)
        return working

    def require_active_transaction(self) -> None:
        transaction = self.transaction_manager.active_transaction if self.transaction_manager is not None else None
        if transaction is None:
            if self.working_record is not None:
                raise RuntimeError("stale lifecycle working record without an active transaction")
            raise RuntimeError("writes require an active lifecycle transaction")
        if self.working_record is not None and self.working_tx_id != transaction.tx_id:
            raise RuntimeError("working record belongs to a different lifecycle transaction")

    def snapshot_current(self) -> _RecordSnapshot:
        return _RecordSnapshot(self.current_record.values)

    def _default_store_contains(self, name: str) -> bool:
        spec = type(self).__field_specs__[name]
        if spec.kind == "local_store":
            return name in self.local_store_values
        if spec.kind == "derived":
            return name in self.derived_values
        return name in self.current_record.values

    def _get_default_store_value(self, name: str) -> Any:
        spec = type(self).__field_specs__[name]
        if spec.kind == "local_store":
            return self.local_store_values[name]
        if spec.kind == "derived":
            return self.derived_values[name]
        return self.current_record.values[name]

    def _set_default_store_value(self, name: str, value: Any) -> Any:
        spec = type(self).__field_specs__[name]
        if spec.kind == "local_store":
            self.local_store_values[name] = value
        elif spec.kind == "derived":
            self.derived_values[name] = value
        else:
            self.current_record.values[name] = value
        return value

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
            value = type(self).__field_specs__[name].default_value()
        return self._set_default_store_value(name, value)

    def resolve_working_default_field(self, name: str) -> Any:
        self.require_active_transaction()
        working = self.ensure_working_record()
        if name in working.values:
            return working.values[name]
        runner = type(self).__class_ftable_working_default_factory_runner__.get(name)
        if runner is None:
            return self.resolve_default_field(name)
        value = self._run_factory_runner("working_default_factory", name, runner)
        working.values[name] = value
        return value

    def reset_to_default(self, name: str) -> Any:
        spec = type(self).__field_specs__[name]
        if spec.kind == "local_store":
            self.local_store_values.pop(name, None)
        elif spec.kind == "derived":
            self.derived_values.pop(name, None)
        else:
            self.current_record.values.pop(name, None)
        return self.resolve_default_field(name)

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
        self.ever_committed = True
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
        return self._state._commit_order_key
    
    def requires_validation(self) -> bool:
        """Return True if the context requires validation before commit, False otherwise."""
        return self._state.commit_validator is not None

    def validate_commit(self) -> bool:
        """Return True if the context is valid and can be committed, False otherwise."""
        validator = self._state.commit_validator
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
    default_factory_runner: dict[str, FactoryRunner] = {}
    working_default_factory_runner: dict[str, FactoryRunner] = {}

    for name, spec in specs.items():
        if spec.default_factory is not MISSING:
            default_factory_runner[name] = _compile_factory_runner(
                field_name=name,
                hook_name="default_factory",
                factory=typing.cast(Callable[..., Any], spec.default_factory),
            )
        if spec.working_default_factory is not MISSING:
            working_default_factory_runner[name] = _compile_factory_runner(
                field_name=name,
                hook_name="working_default_factory",
                factory=typing.cast(Callable[..., Any], spec.working_default_factory),
            )
        if spec.kind == "managed":
            if spec.thaw is not None:
                get_default[name] = _get_managed_thawed_field
                get_current[name] = _get_current_field
                get_working[name] = _get_managed_thawed_field
            elif spec.initial_working is not MISSING:
                get_default[name] = _get_managed_initial_working_field
                get_current[name] = _get_current_field
                get_working[name] = _get_managed_initial_working_field
            else:
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
            state_factory[name] = spec.state_factory
            state_copy[name] = spec.state_copy
        elif spec.kind == "const":
            get_default[name] = _get_current_field
            get_current[name] = _get_current_field
            get_working[name] = _get_current_field
            set_default[name] = _set_const_field
            set_working[name] = _set_const_field
            commit_field[name] = _close_noop
            rollback_field[name] = _close_noop
            state_factory[name] = None
            state_copy[name] = None
        elif spec.kind == "static":
            get_default[name] = _get_static_field
            get_current[name] = _get_static_field
            get_working[name] = _get_static_field
            set_default[name] = _set_static_field
            set_working[name] = _set_static_field
            commit_field[name] = _close_noop
            rollback_field[name] = _close_noop
            state_factory[name] = None
            state_copy[name] = None
        elif spec.kind in {"binding", "owned"}:
            get_default[name] = _get_default_overlay_field
            get_current[name] = _get_current_field
            get_working[name] = _get_working_overlay_field
            if typing.get_origin(spec.annotation) in {dict, typing.Dict}:
                set_default[name] = _set_default_binding_map_field
                set_working[name] = _set_working_binding_map_field
                commit_field[name] = _commit_binding_map_field
                rollback_field[name] = _rollback_binding_map_field
                close_field[name] = _close_binding_map_field
            else:
                set_default[name] = _set_default_binding_field
                set_working[name] = _set_working_binding_field
                commit_field[name] = _commit_binding_field
                rollback_field[name] = _rollback_binding_field
                close_field[name] = _close_binding_field
            state_factory[name] = None
            state_copy[name] = None
        elif spec.kind == "transient":
            if name in working_default_factory_runner:
                get_default[name] = _get_transient_working_default_field
                get_working[name] = _get_transient_working_default_field
            else:
                get_default[name] = _get_default_overlay_field
                get_working[name] = _get_working_overlay_field
            get_current[name] = _get_current_field
            set_default[name] = _set_default_value_field
            set_working[name] = _set_working_value_field
            commit_field[name] = _close_noop
            rollback_field[name] = _close_noop
            state_factory[name] = None
            state_copy[name] = None
        elif spec.kind == "local_store":
            get_default[name] = _get_local_store_field
            get_current[name] = _get_local_store_field
            get_working[name] = _get_local_store_field
            set_default[name] = _set_local_store_field
            set_working[name] = _set_local_store_field
            commit_field[name] = _close_noop
            rollback_field[name] = _close_noop
            close_field[name] = _close_local_store_field
            state_factory[name] = None
            state_copy[name] = None
        elif spec.kind == "derived":
            get_default[name] = _get_derived_field
            get_current[name] = _get_derived_field
            get_working[name] = _get_derived_field
            set_default[name] = _set_derived_field
            set_working[name] = _set_derived_field
            commit_field[name] = _reset_derived_field
            rollback_field[name] = _reset_derived_field
            close_field[name] = _reset_derived_field
            state_factory[name] = None
            state_copy[name] = None
        elif spec.kind in {"commit_order_key", "commit_validator"}:
            get_default[name] = _get_current_field
            get_current[name] = _get_current_field
            get_working[name] = _get_current_field
            set_default[name] = _set_const_field
            set_working[name] = _set_const_field
            commit_field[name] = _close_noop
            rollback_field[name] = _close_noop
            state_factory[name] = None
            state_copy[name] = None
        else:
            raise TypeError(f"unsupported lifecycle field kind {spec.kind!r}")
            close_field[name] = _close_noop
        if name not in close_field:
            close_field[name] = _close_noop

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
        "__class_ftable_default_factory_runner__": default_factory_runner,
        "__class_ftable_working_default_factory_runner__": working_default_factory_runner,
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
    if base.kind != derived.kind:
        raise TypeError(f"incompatible lifecycle field override for {base.name!r}")
    if base.compare != derived.compare:
        raise TypeError(f"incompatible lifecycle field override for {base.name!r}")
    if base.initial_working != derived.initial_working and derived.initial_working is not MISSING:
        raise TypeError(f"incompatible lifecycle field override for {base.name!r}")
    if base.freeze != derived.freeze and derived.freeze is not None:
        raise TypeError(f"incompatible lifecycle field override for {base.name!r}")
    if base.thaw != derived.thaw and derived.thaw is not None:
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
    working_default_factory = (
        derived.working_default_factory
        if derived.working_default_factory is not MISSING
        else base.working_default_factory
    )
    state_factory = derived.state_factory if derived.state_factory is not None else base.state_factory
    state_copy = derived.state_copy if derived.state_copy != copy.copy else base.state_copy
    initial_working = (
        derived.initial_working if derived.initial_working is not MISSING else base.initial_working
    )
    freeze = derived.freeze if derived.freeze is not None else base.freeze
    thaw = derived.thaw if derived.thaw is not None else base.thaw

    return FieldSpec(
        name=base.name,
        kind=base.kind,
        annotation=derived.annotation,
        compare=base.compare,
        default=default,
        default_factory=default_factory,
        working_default_factory=working_default_factory,
        initial_working=initial_working,
        freeze=freeze,
        thaw=thaw,
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
    "BindingBase",
    "LifecycleContext",
    "LifecycleTransaction",
    "LifecycleValidatorReturnedFalse",
    "Record",
    "TransactionManager",
    "binding",
    "commit_order_key",
    "commit_validator",
    "const",
    "derived",
    "lifecycle_field",
    "local_store",
    "managed",
    "managed_context",
    "owned",
    "static",
    "transient",
]
