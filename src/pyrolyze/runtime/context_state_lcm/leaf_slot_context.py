from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ._base import USE_OWNER
from .context_base import PASS_TX_KEY
from .rerunnable_slot_context import RerunnableSlotContextStateMgr
from .field_only_render import _field_only_completion
from .lifecycle_adapter import managed, managed_context


@dataclass(frozen=True, slots=True)
class _LeafInvocation:
    args: tuple[Any, ...] = ()
    kwargs: tuple[tuple[str, Any], ...] = ()


@managed_context
class LeafSlotContextStateMgr(RerunnableSlotContextStateMgr):
    _invocation: _LeafInvocation = managed(
        default_factory=_LeafInvocation,
        init=False,
        compare="identity",
        tx_key=PASS_TX_KEY,
    )
    def _argument_record(self) -> _LeafInvocation:
        return self._invocation

    @property
    def _last_args(self) -> tuple[Any, ...]:
        return self._argument_record().args

    @property
    def _last_kwargs(self) -> tuple[tuple[str, Any], ...]:
        return self._argument_record().kwargs

    def accepted_invocation(self) -> _LeafInvocation:
        return self.current._invocation

    def invoke(
        self, leaf_fn: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> Any:
        completion = _field_only_completion(self)
        if completion is None:
            raise RuntimeError("render completion is not configured")
        with completion.attempt_scope():
            owner = completion.active
            assert owner is not None
            invocation = _LeafInvocation(args, tuple(sorted(kwargs.items())))
            owner._require_open()
            owner._require_identity()
            self._invocation = invocation
            return leaf_fn(*args, **kwargs)

    def invoke_native(
        self,
        leaf_fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        context_param: str,
        context_facade: Any = USE_OWNER,
    ) -> Any:
        context_facade = self._resolve_owner_arg(context_facade)
        completion = _field_only_completion(self)
        if completion is None:
            raise RuntimeError("render completion is not configured")
        execution = completion.attempt_scope()
        with execution:
            self.begin_pass()
            try:
                if completion is not None:
                    owner = completion.active
                    assert owner is not None
                    invocation = _LeafInvocation(args, tuple(sorted(kwargs.items())))
                    owner._require_open()
                    owner._require_identity()
                    self._invocation = invocation
                _ = context_param
                result = leaf_fn(context_facade, *args, **kwargs)
                if result is not None:
                    raise TypeError("@pyrolyze functions must return None")
            except BaseException as error:
                if completion is None or self.is_scope_active():
                    self.rollback_pass(error)
                raise
            if completion is None or self.is_scope_active():
                self.end_pass()
        return None
