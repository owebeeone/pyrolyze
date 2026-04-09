from __future__ import annotations

from typing import Any, Callable

from .rerunnable_slot_context import RerunnableSlotContextStateMgr
from ._base import unavailable


class LeafSlotContextStateMgr(RerunnableSlotContextStateMgr):
    def invoke(self, leaf_fn: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
        owner = self.owner
        owner.last_args = args
        owner.last_kwargs = tuple(sorted(kwargs.items()))
        return leaf_fn(*args, **kwargs)

    def invoke_native(
        self,
        leaf_fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        context_param: str,
    ) -> Any:
        owner = self.owner
        owner.last_args = args
        owner.last_kwargs = tuple(sorted(kwargs.items()))
        owner._begin_scope_pass()
        try:
            _ = context_param
            result = leaf_fn(owner, *args, **kwargs)
            if result is not None:
                raise TypeError("@pyrolyze functions must return None")
        except BaseException:
            owner._rollback_scope_pass()
            raise
        owner._commit_scope_pass()
        return None
