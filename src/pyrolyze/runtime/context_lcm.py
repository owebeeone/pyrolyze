"""Lifecycle-backed context runtime overrides."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from pyrolyze.lifecycle import TransactionManager, local_store, managed, managed_context, transient

from . import context_original as _base

for _name, _value in vars(_base).items():
    if _name.startswith("_") and _name != "__all__":
        continue
    globals()[_name] = _value


@managed_context
class _EventHandlerSlotState:
    committed_callback: Callable[..., Any] | None = managed(default=None, compare="identity")
    committed_key: object | None = managed(default=None, compare="identity")
    staged_callback: Callable[..., Any] | None = transient(default=None)
    staged_key: object | None = transient(default=None)
    dispatch: Callable[..., None] | None = local_store(default=None)


@managed_context
class _LeafSlotState:
    last_args: tuple[Any, ...] = local_store(default_factory=tuple)
    last_kwargs: tuple[tuple[str, Any], ...] = local_store(default_factory=tuple)


@managed_context
class _ContainerSlotState:
    expects_native_root: bool = local_store(default=False)
    committed_native_root: bool = managed(default=False)
    site_metadata: tuple[_base.RuntimeSiteMetadata[Any], ...] = local_store(default_factory=tuple)


class _LifecycleSlotMixin:
    _lcm_fields: tuple[str, ...] = ()

    def _lcm_sync(self) -> None:
        state = object.__getattribute__(self, "_lcm_state")
        for name in self._lcm_fields:
            object.__setattr__(self, name, getattr(state, name))

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        fields = type(self)._lcm_fields
        state = getattr(self, "_lcm_state", None)
        if state is not None and name in fields:
            setattr(state, name, value)
            object.__setattr__(self, name, getattr(state, name))
            return
        object.__setattr__(self, name, value)


@dataclass(slots=True)
class EventHandlerSlotContext(_LifecycleSlotMixin, _base.EventHandlerSlotContext):
    _lcm_txm: TransactionManager = field(init=False, repr=False)
    _lcm_state: _EventHandlerSlotState = field(init=False, repr=False)

    _lcm_fields = (
        "committed_callback",
        "committed_key",
        "staged_callback",
        "staged_key",
        "dispatch",
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "_lcm_txm", TransactionManager())
        object.__setattr__(
            self,
            "_lcm_state",
            _EventHandlerSlotState(
                transaction_manager=self._lcm_txm,
                committed_callback=self.committed_callback,
                committed_key=self.committed_key,
                dispatch=self.dispatch,
            ),
        )
        self._lcm_sync()

    def stage_callback(
        self,
        *,
        callback: Callable[..., Any],
        dirty: bool,
    ) -> Callable[..., None]:
        callback_key = _base._callback_key(callback)
        if dirty or self.committed_callback is None or self.committed_key != callback_key:
            if self._lcm_txm.active_transaction is None:
                self._lcm_txm.begin()
            self.staged_callback = callback
            self.staged_key = callback_key
        return self._dispatch_callable()

    def commit_handler(self) -> None:
        if self.staged_callback is None:
            return
        if self._lcm_txm.active_transaction is None:
            self._lcm_txm.begin()
        self.committed_callback = self.staged_callback
        self.committed_key = self.staged_key
        self._lcm_txm.commit()
        self._lcm_sync()

    def rollback_handler(self) -> None:
        if self._lcm_txm.active_transaction is not None:
            self._lcm_txm.rollback()
        self._lcm_sync()

    def deactivate(self) -> None:
        dispatch = self.dispatch
        if self._lcm_txm.active_transaction is not None:
            self._lcm_txm.rollback()
        object.__setattr__(self, "_lcm_txm", TransactionManager())
        object.__setattr__(
            self,
            "_lcm_state",
            _EventHandlerSlotState(
                transaction_manager=self._lcm_txm,
                dispatch=dispatch,
            ),
        )
        self._lcm_sync()
        _base.SlotContext.deactivate(self)

    def _dispatch_callable(self) -> Callable[..., None]:
        if self.dispatch is None:

            def dispatch(*args: Any, **kwargs: Any) -> None:
                callback = self.committed_callback
                if callback is None:
                    if _base.os.environ.get("PYROLYZE_ENV") == "prod":
                        return
                    raise RuntimeError("event handler is inactive")
                callback(*args, **kwargs)

            self.dispatch = dispatch
        return self.dispatch


@dataclass(slots=True)
class LeafSlotContext(_LifecycleSlotMixin, _base.LeafSlotContext):
    _lcm_state: _LeafSlotState = field(init=False, repr=False)

    _lcm_fields = (
        "last_args",
        "last_kwargs",
    )

    def __post_init__(self) -> None:
        _base.RerunnableSlotContext.__post_init__(self)
        object.__setattr__(
            self,
            "_lcm_state",
            _LeafSlotState(
                last_args=self.last_args,
                last_kwargs=self.last_kwargs,
            ),
        )
        self._lcm_sync()

    def invoke(self, leaf_fn: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
        self.last_args = args
        self.last_kwargs = tuple(sorted(kwargs.items()))
        return leaf_fn(*args, **kwargs)

    def invoke_native(
        self,
        leaf_fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        context_param: str,
    ) -> Any:
        self.last_args = args
        self.last_kwargs = tuple(sorted(kwargs.items()))
        self._begin_scope_pass()
        try:
            _ = context_param
            result = leaf_fn(self, *args, **kwargs)
            if result is not None:
                raise TypeError("@pyrolyze functions must return None")
        except BaseException:
            self._rollback_scope_pass()
            raise
        self._commit_scope_pass()
        return None


@dataclass(slots=True)
class ContainerSlotContext(_LifecycleSlotMixin, _base.ContainerSlotContext):
    _lcm_txm: TransactionManager = field(init=False, repr=False)
    _lcm_state: _ContainerSlotState = field(init=False, repr=False)

    _lcm_fields = (
        "expects_native_root",
        "committed_native_root",
        "site_metadata",
    )

    def __post_init__(self) -> None:
        _base.RerunnableSlotContext.__post_init__(self)
        object.__setattr__(self, "_lcm_txm", TransactionManager())
        object.__setattr__(
            self,
            "_lcm_state",
            _ContainerSlotState(
                transaction_manager=self._lcm_txm,
                expects_native_root=self.expects_native_root,
                committed_native_root=self.committed_native_root,
                site_metadata=self.site_metadata,
            ),
        )
        self._lcm_sync()

    def _begin_scope_pass(self) -> None:
        self._lcm_txm.begin()
        _base.ContextBase._begin_scope_pass(self)

    def _commit_scope_pass(self) -> None:
        try:
            _base.ContextBase._commit_scope_pass(self)
            self._lcm_txm.commit()
        finally:
            self._lcm_sync()

    def _rollback_scope_pass(self) -> None:
        try:
            _base.ContextBase._rollback_scope_pass(self)
        finally:
            self._lcm_txm.rollback()
            self._lcm_sync()


_base.EventHandlerSlotContext = EventHandlerSlotContext
_base.ContainerSlotContext = ContainerSlotContext
_base.LeafSlotContext = LeafSlotContext

globals()["EventHandlerSlotContext"] = EventHandlerSlotContext
globals()["ContainerSlotContext"] = ContainerSlotContext
globals()["LeafSlotContext"] = LeafSlotContext

__PYROLYZE_CONTEXT_IMPLEMENTATION__ = "lcm"
