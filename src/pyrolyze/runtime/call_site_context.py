from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import InitVar, dataclass, field, replace
from enum import IntEnum
from typing import Any, Generic, Hashable, Iterable, Mapping, Self, TypeVar


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
class CallSiteBindingBase(ABC):
    _call_site_ref_count: int = field(default=1, init=False, repr=False, compare=False)

    @property
    def ref_count(self) -> int:
        return self._call_site_ref_count

    def inc_ref(self) -> None:
        if self._call_site_ref_count <= 0:
            raise RuntimeError("cannot retain a dead call-site binding")
        self._call_site_ref_count += 1

    def dec_ref(self) -> None:
        if self._call_site_ref_count <= 0:
            raise AssertionError("dec_ref called without a matching inc_ref")
        self._call_site_ref_count -= 1
        if self._call_site_ref_count == 0:
            self.close()

    @abstractmethod
    def close(self) -> None: ...


@dataclass(slots=True)
class _MutableState(Generic[T]):
    value: T


@dataclass(frozen=True, slots=True)
class CallSiteContext(ABC):
    binding: CallSiteBindingBase | None
    function_identity: Any
    last_args: CallSiteArgs
    invoke_state_value: InitVar[CallSiteInvokeState] = CallSiteInvokeState.NOT_SET
    invoke_state: _MutableState[CallSiteInvokeState] = field(
        default_factory=lambda: _MutableState(CallSiteInvokeState.NOT_SET),
        init=False,
        compare=False,
        hash=False,
        repr=False,
    )
    _close_state: _MutableState[bool] = field(
        default_factory=lambda: _MutableState(False),
        init=False,
        compare=False,
        hash=False,
        repr=False,
    )

    def __post_init__(self, invoke_state_value: CallSiteInvokeState) -> None:
        self.invoke_state.value = CallSiteInvokeState(invoke_state_value)

    def close(self) -> None:
        if self._close_state.value:
            return
        self._close_state.value = True
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


@dataclass(slots=True)
class CallSiteContextManager:
    _current: dict[Hashable, CallSiteContext] = field(default_factory=dict)
    _staged: dict[Hashable, CallSiteContext] = field(default_factory=dict)
    _visited: set[Hashable] = field(default_factory=set)

    def get_current(self, slot_id: Hashable) -> CallSiteContext | None:
        return self._current.get(slot_id)

    def stage(self, slot_id: Hashable, context: CallSiteContext) -> None:
        previous_staged = self._staged.get(slot_id)
        if previous_staged is not None and previous_staged is not context:
            previous_staged.close()
        self._staged[slot_id] = context

    def replace_current(self, slot_id: Hashable, context: CallSiteContext) -> None:
        previous_current = self._current.get(slot_id)
        if previous_current is context:
            return
        self._current[slot_id] = context
        if previous_current is not None:
            previous_current.close()

    def mark_visited(self, slot_id: Hashable) -> None:
        self._visited.add(slot_id)

    def begin_pass(self) -> None:
        if self._staged:
            self.rollback_pass()
        self._visited.clear()

    def commit_pass(self) -> None:
        for slot_id, staged in list(self._staged.items()):
            current = self._current.get(slot_id)
            if current is not None and current is not staged:
                current.close()
            self._current[slot_id] = staged

        unseen_slot_ids = [slot_id for slot_id in self._current if slot_id not in self._visited and slot_id not in self._staged]
        for slot_id in unseen_slot_ids:
            current = self._current.pop(slot_id, None)
            if current is not None:
                current.close()

        self._staged.clear()
        self._visited.clear()

    def rollback_pass(self) -> None:
        for slot_id, staged in list(self._staged.items()):
            current = self._current.get(slot_id)
            if current is not staged:
                staged.close()
        self._staged.clear()
        self._visited.clear()

    def close_all(self) -> None:
        for context in list(self._staged.values()):
            context.close()
        for context in list(self._current.values()):
            context.close()
        self._staged.clear()
        self._current.clear()
        self._visited.clear()
