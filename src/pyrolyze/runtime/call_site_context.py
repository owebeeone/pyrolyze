from __future__ import annotations

from abc import ABC
from dataclasses import InitVar, dataclass, field, replace
from enum import IntEnum
from typing import Any, Generic, Hashable, Iterable, Mapping, Self, TypeVar

from pyrolyze.lifecycle import BindingBase
from yidl_lifecycle.lifecycle import lifecycle as managed_context
from yidl_lifecycle.lifecycle import owned, transient
from yidl_lifecycle.transaction_yidl import DEFAULT_TRANSACTION, LifecycleTransaction, TransactionManager

from .pyro_call import RuntimeSiteMetadata
from .call_site_ownership import _CallSiteCollection, _raise_cleanup_errors


class _UNSET_TYPE:
    pass


_UNSET = _UNSET_TYPE()

T = TypeVar("T")


class CallSiteInvokeState(IntEnum):
    NOT_SET = 0
    GET_SET = 1
    DIRTY_SET = 2


@dataclass(frozen=True, slots=True)
class CallSiteArgs:
    args: tuple[Any, ...] = ()
    kwargs: tuple[tuple[str, Any], ...] = ()

    @classmethod
    def capture(cls, *args: Any, **kwargs: Any) -> CallSiteArgs:
        return cls(
            args=tuple(args),
            kwargs=tuple(sorted(kwargs.items())),
        )

    @classmethod
    def from_parts(
        cls,
        args: Iterable[Any] = (),
        kwargs: Mapping[str, Any] | Iterable[tuple[str, Any]] = (),
    ) -> CallSiteArgs:
        kwargs_items: Iterable[tuple[str, Any]]
        if isinstance(kwargs, Mapping):
            kwargs_items = kwargs.items()
        else:
            kwargs_items = kwargs
        return cls(
            args=tuple(args),
            kwargs=tuple(sorted(kwargs_items)),
        )

    def call(self, func: Any) -> Any:
        return func(*self.args, **dict(self.kwargs))


@dataclass(slots=True, eq=False)
class CallSiteBindingBase(BindingBase):
    pass


@dataclass(slots=True)
class _MutableState(Generic[T]):
    value: T


@dataclass(slots=True, eq=False)
class CallSiteContext(BindingBase, ABC):
    binding: CallSiteBindingBase | None
    function_identity: Any
    last_args: CallSiteArgs
    site_metadata: tuple[RuntimeSiteMetadata[Any], ...] = ()
    invoke_state_value: InitVar[CallSiteInvokeState] = CallSiteInvokeState.NOT_SET
    invoke_state: _MutableState[CallSiteInvokeState] = field(
        default_factory=lambda: _MutableState(CallSiteInvokeState.NOT_SET),
        init=False,
        compare=False,
        hash=False,
        repr=False,
    )
    def __post_init__(self, invoke_state_value: CallSiteInvokeState) -> None:
        self.invoke_state.value = CallSiteInvokeState(invoke_state_value)

    def close(self) -> None:
        if self.is_closed:
            return
        self.dec_ref()

    def _close(self) -> None:
        if self.binding is not None:
            self.binding.dec_ref()

    def mark_invoke_get(self) -> None:
        if self.invoke_state.value is CallSiteInvokeState.NOT_SET:
            self.invoke_state.value = CallSiteInvokeState.GET_SET

    def mark_invoke_dirty(self) -> None:
        self.invoke_state.value = CallSiteInvokeState.DIRTY_SET

    def clear_invoke_dirty(self) -> None:
        if self.invoke_state.value is CallSiteInvokeState.DIRTY_SET:
            self.invoke_state.value = CallSiteInvokeState.NOT_SET

    def clear_invoke_state(self) -> None:
        self.invoke_state.value = CallSiteInvokeState.NOT_SET

    def replace(
        self,
        *,
        binding: CallSiteBindingBase | None | _UNSET_TYPE = _UNSET,
        **kwds,
    ) -> Self:
        """
        Create a new immutable context with replaced fields.

        binding ownership semantics:

        - If ``binding`` is provided explicitly, it is treated as already owned
          by the caller for the new context instance, so no automatic
          ``inc_ref()`` is performed.

        - If ``binding`` is not provided explicitly, the new context instance
          takes ownership of the existing binding and calls ``inc_ref()``.

        """

        retained_binding: CallSiteBindingBase | None = None
        if binding is _UNSET:
            retained_binding = self.binding
            if retained_binding is not None:
                retained_binding.inc_ref()
        else:
            kwds["binding"] = binding
        kwds["invoke_state_value"] = kwds.pop("invoke_state_value", self.invoke_state.value)
        try:
            return replace(self, **kwds)
        except BaseException:
            if retained_binding is not None:
                retained_binding.dec_ref()
            raise


@managed_context
class CallSitePassContext:
    contexts: _CallSiteCollection = owned(
        default_factory=_CallSiteCollection, compare="identity",
    )
    visited: frozenset[Hashable] = transient(default_factory=frozenset)


class CallSiteContextManager:
    __slots__ = ("_transaction_manager", "_pass_context", "_completing", "_tx_key", "_owns_transaction")

    def __init__(self) -> None:
        self._transaction_manager = TransactionManager()
        self._pass_context = CallSitePassContext(transaction_manager=self._transaction_manager)
        self._completing = False
        self._tx_key = DEFAULT_TRANSACTION
        self._owns_transaction = True

    @classmethod
    def _for_render_pass(
        cls, pass_context: CallSitePassContext, manager: TransactionManager, tx_key: Hashable,
    ) -> CallSiteContextManager:
        instance = cls.__new__(cls)
        instance._pass_context = pass_context
        instance._transaction_manager = manager
        instance._tx_key = tx_key
        instance._owns_transaction = False
        instance._completing = False
        return instance

    @property
    def _active_transaction(self) -> LifecycleTransaction | None:
        return self._transaction_manager.active_transaction_for(self._tx_key)

    def get_current(self, slot_id: Hashable) -> CallSiteContext | None:
        return self._current.get(slot_id)

    def get_visible(self, slot_id: Hashable) -> CallSiteContext | None:
        return self._staged.get(slot_id) or self._current.get(slot_id)

    def iter_current(self) -> tuple[CallSiteContext, ...]:
        return tuple(self._current.values())

    @property
    def _current(self) -> dict[Hashable, CallSiteContext]:
        return self._pass_context.current.contexts.contexts

    @property
    def _staged(self) -> dict[Hashable, CallSiteContext]:
        if self._active_transaction is None:
            return {}
        current = self._pass_context.current.contexts
        visible = self._pass_context.contexts
        return {} if visible is current else visible.contexts

    def _require_not_completing(self) -> None:
        if self._completing:
            raise RuntimeError("call-site completion is in progress")

    def _replace_collection(self, contexts: Mapping[Hashable, CallSiteContext]) -> None:
        previous = self._pass_context.contexts
        replacement = _CallSiteCollection.replacing(
            contexts,
            previous,
            self._pass_context.current.contexts,
        )
        try:
            self._pass_context.contexts = replacement
        except BaseException as error:
            errors = [error]
            try:
                replacement.release()
            except BaseException as cleanup:
                errors.append(cleanup)
            _raise_cleanup_errors(errors)
        if previous is not self._pass_context.current.contexts:
            completing = self._completing
            self._completing = True
            try:
                previous.release()
            finally:
                self._completing = completing

    def _require_original_transaction(self, transaction: LifecycleTransaction) -> None:
        if self._active_transaction is not transaction:
            raise RuntimeError("original call-site transaction is no longer active")

    def stage(self, slot_id: Hashable, context: CallSiteContext) -> None:
        self._require_not_completing()
        transaction = self._active_transaction
        if transaction is None:
            raise RuntimeError("call-site selection requires an active pass")
        next_contexts = dict(self._pass_context.contexts.contexts)
        next_contexts[slot_id] = context
        self._require_original_transaction(transaction)
        self._replace_collection(next_contexts)

    def mark_visited(self, slot_id: Hashable) -> None:
        self._require_not_completing()
        transaction = self._active_transaction
        if transaction is None:
            raise RuntimeError("call-site visitation requires an active pass")
        visited = self._pass_context.visited | {slot_id}
        self._require_original_transaction(transaction)
        self._pass_context.visited = visited

    def begin_pass(self) -> None:
        self._require_not_completing()
        if not self._owns_transaction:
            if self._active_transaction is None:
                raise RuntimeError("expression selection requires the outer render transaction")
            self._pass_context.visited = frozenset()
            return
        if self._active_transaction is not None:
            self.rollback_pass()
        self._transaction_manager.begin(self._tx_key)

    def commit_pass(self) -> None:
        self._require_not_completing()
        if not self._owns_transaction:
            raise RuntimeError("the outer render owns expression completion")
        if self._active_transaction is None:
            return
        self._prepare_pass()
        self._finish_pass(commit=True)

    def _prepare_pass(self) -> None:
        self._require_not_completing()
        transaction = self._active_transaction
        if transaction is None:
            raise RuntimeError("call-site selection requires an active pass")
        self._completing = True
        try:
            next_contexts = {
                slot_id: context
                for slot_id, context in self._pass_context.contexts.contexts.items()
                if slot_id in self._pass_context.visited
            }
            self._require_original_transaction(transaction)
            self._replace_collection(next_contexts)
        finally:
            self._completing = False

    def rollback_pass(self) -> None:
        self._require_not_completing()
        if not self._owns_transaction:
            raise RuntimeError("the outer render owns expression completion")
        if self._active_transaction is None:
            return
        self._finish_pass(commit=False)

    def _finish_pass(self, *, commit: bool) -> None:
        current = self._pass_context.current.contexts
        pending = self._pass_context.contexts
        errors: list[BaseException] = []
        self._completing = True
        try:
            try:
                if commit:
                    self._transaction_manager.commit(self._tx_key)
                else:
                    self._transaction_manager.rollback(self._tx_key)
            except BaseException as error:
                errors.append(error)
            retained = {
                id(self._pass_context.current.contexts),
                id(self._pass_context.contexts),
            }
            for collection in {id(current): current, id(pending): pending}.values():
                if id(collection) in retained:
                    continue
                try:
                    collection.release()
                except BaseException as error:
                    errors.append(error)
        finally:
            self._completing = False
        _raise_cleanup_errors(errors)

    def close_all(self) -> None:
        self._require_not_completing()
        errors: list[BaseException] = []
        if not self._owns_transaction and self._active_transaction is not None:
            raise RuntimeError("cannot close expression collections during an outer render")
        if self._active_transaction is not None:
            try:
                self.rollback_pass()
            except BaseException as error:
                errors.append(error)
        self._completing = True
        try:
            self._pass_context.current.contexts.release()
        except BaseException as error:
            errors.append(error)
        finally:
            self._completing = False
        self._pass_context = type(self._pass_context)(transaction_manager=self._transaction_manager)
        _raise_cleanup_errors(errors)
