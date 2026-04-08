from __future__ import annotations

from abc import ABC
from dataclasses import InitVar, dataclass, field, replace
from enum import IntEnum
from typing import Any, Generic, Hashable, Iterable, Mapping, Self, TypeVar

from pyrolyze.lifecycle import BindingBase, TransactionManager, managed_context, owned, transient

from .pyro_call import RuntimeSiteMetadata


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
class _CallSitePassContext:
    contexts: dict[Hashable, CallSiteContext] = owned(default_factory=dict)
    visited: set[Hashable] = transient(default_factory=set)


class CallSiteContextManager:
    __slots__ = ("_transaction_manager", "_pass_context")

    def __init__(self) -> None:
        self._transaction_manager = TransactionManager()
        self._pass_context = _CallSitePassContext(transaction_manager=self._transaction_manager)

    def get_current(self, slot_id: Hashable) -> CallSiteContext | None:
        return self._pass_context.current.contexts.get(slot_id)

    def stage(self, slot_id: Hashable, context: CallSiteContext) -> None:
        next_contexts = dict(self._pass_context.contexts)
        next_contexts[slot_id] = context
        self._pass_context.contexts = next_contexts

    def replace_current(self, slot_id: Hashable, context: CallSiteContext) -> None:
        current_contexts = self._pass_context.state.current_record.values["contexts"]
        previous_current = current_contexts.get(slot_id)
        if previous_current is context:
            return
        next_contexts = dict(current_contexts)
        next_contexts[slot_id] = context
        context.accepted()
        self._pass_context.state.current_record.values["contexts"] = next_contexts
        if previous_current is not None:
            previous_current.close()

    def mark_visited(self, slot_id: Hashable) -> None:
        next_visited = set(self._pass_context.visited)
        next_visited.add(slot_id)
        self._pass_context.visited = next_visited

    def begin_pass(self) -> None:
        if self._transaction_manager.active_transaction is not None:
            self.rollback_pass()
        self._transaction_manager.begin()

    def commit_pass(self) -> None:
        if self._transaction_manager.active_transaction is None:
            return
        next_contexts = {
            slot_id: context
            for slot_id, context in self._pass_context.contexts.items()
            if slot_id in self._pass_context.visited
        }
        self._pass_context.contexts = next_contexts
        self._transaction_manager.commit()

    def rollback_pass(self) -> None:
        if self._transaction_manager.active_transaction is None:
            return
        self._transaction_manager.rollback()

    def close_all(self) -> None:
        if self._transaction_manager.active_transaction is not None:
            self._transaction_manager.rollback()
        self._pass_context.close()
        self._pass_context = _CallSitePassContext(transaction_manager=self._transaction_manager)
