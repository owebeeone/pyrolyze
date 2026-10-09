"""Keyed item selection borrows the original outer render transaction."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

from ._support import _KeyedLoopIterable, _unwrap
from .completion_render import _CompletionRenderCompletion, _enable_completion_render
from .context_base import ContextBaseStateMgr
from .render_attempt import _LocalRenderScope, _RenderAttempt
from .render_context import RenderContextStateMgr


@dataclass(frozen=True, slots=True)
class _KeyedLoopExecution:
    completion: _KeyedLoopRenderCompletion
    owner: _RenderAttempt

    def require_active(self) -> None:
        self.owner._require_open()
        self.owner._require_identity()
        if self.completion.active is not self.owner or self.completion._completing:
            raise RuntimeError("original keyed-loop render is no longer active")

    @contextmanager
    def scope(self, context: ContextBaseStateMgr) -> Iterator[_LocalRenderScope]:
        self.require_active()
        if self.owner.is_scope_active(context):
            self.completion.reject("recursive keyed-loop iteration is not admitted")
        # No attempt_scope across a suspended yield: the outer owner must still
        # finish, aborting any unexited loop rather than deferring publication.
        with self.owner.scope(
            context,
            manager=context._transaction_manager,
            on_enter=lambda: self.completion._enter_context(context),
            on_exit=context._end_field_only_pass,
            on_abort=context._abort_field_only_pass,
        ) as scope:
            yield scope


@dataclass(eq=False, slots=True)
class _KeyedLoopRenderCompletion(_CompletionRenderCompletion):
    keyed_loop_selection_enabled = True

    def require_slot_type(self, slot_type: type[Any]) -> None:
        from pyrolyze.runtime.context_bare_refactor_lcm import (
            KeyedLoopSlotContext,
            LoopItemSlotContext,
        )

        if slot_type not in (KeyedLoopSlotContext, LoopItemSlotContext):
            super(_KeyedLoopRenderCompletion, self).require_slot_type(slot_type)

    def keyed_loop(
        self,
        context: ContextBaseStateMgr,
        slot_id: Any,
        values: Any,
        key_fn: Callable[[Any], Any],
        parent: Any,
    ) -> _KeyedLoopIterable[Any]:
        from pyrolyze.runtime.context_bare_refactor_lcm import KeyedLoopSlotContext

        self.require_resource_owner()
        assert self.active is not None
        owner = self.active
        with self.attempt_scope():
            raw_values, _ = _unwrap(values)
            normalized = tuple(raw_values)
            owner._require_open()
            owner._require_identity()
            slot = context.ensure_slot(
                slot_id, KeyedLoopSlotContext, parent_facade=parent
            )
            owner._require_identity()
            return _KeyedLoopIterable(
                owner_state_mgr=slot._state_mgr,
                parent_facade=slot,
                values=normalized,
                key_fn=key_fn,
                execution=_KeyedLoopExecution(self, owner),
            )


def _enable_keyed_loop_render(root: RenderContextStateMgr) -> None:
    _enable_completion_render(root)
    root._field_only_completion = _KeyedLoopRenderCompletion(root)
