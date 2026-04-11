from __future__ import annotations

from typing import Any, Callable

from ._base import USE_OWNER
from .rerunnable_slot_context import RerunnableSlotContextStateMgr
from ._base import unavailable


class LeafSlotContextStateMgr(RerunnableSlotContextStateMgr):
    def __init__(self, owner: object, **kwargs: object) -> None:
        super().__init__(owner, **kwargs)
        self._last_args: tuple[Any, ...] = ()
        self._last_kwargs: tuple[tuple[str, Any], ...] = ()

    def invoke(self, leaf_fn: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
        self._last_args = args
        self._last_kwargs = tuple(sorted(kwargs.items()))
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
        self._last_args = args
        self._last_kwargs = tuple(sorted(kwargs.items()))
        self.begin_pass()
        try:
            _ = context_param
            result = leaf_fn(context_facade, *args, **kwargs)
            if result is not None:
                raise TypeError("@pyrolyze functions must return None")
        except BaseException:
            self.rollback_pass()
            raise
        self.end_pass()
        return None
