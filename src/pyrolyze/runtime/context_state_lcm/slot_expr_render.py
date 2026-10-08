"""Private plain-expression selection under the outer render decision.

The borrowed collection manager stages only; it never completes the shared
transaction. Legacy expression resource handlers remain excluded. Collection
release below retires explicit ownership, not generated field publication.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

from pyrolyze.runtime.call_site_context import (
    CallSiteContextManager,
    CallSitePassContext,
)
from pyrolyze.runtime.call_site_ownership import _CallSiteCollection
from pyrolyze.runtime.slot_call_semantics import (
    SlotCallBinding,
    SlotCallBindingHost,
    SlotValueHandler,
    select_slot_call_handler,
)
from .callback_render import _graph_states
from .context_base import PASS_TX_KEY
from .lifecycle_adapter import managed_context, owned, transient
from .mount_render import _MountRenderCompletion, _enable_mount_render
from .render_attempt import _RenderAttempt, _raise_with_cleanup
from .render_context import RenderContextStateMgr
from .slot_expr_slot_context import SlotExprSlotContextStateMgr


@managed_context
class RenderCallSitePassContext(CallSitePassContext):
    contexts: _CallSiteCollection = owned(
        default_factory=_CallSiteCollection,
        compare="identity",
        tx_key=PASS_TX_KEY,
    )
    visited: frozenset[Any] = transient(default_factory=frozenset, tx_key=PASS_TX_KEY)


def _enable_slot_expr_render(root: RenderContextStateMgr) -> None:
    _enable_mount_render(root)
    root._field_only_completion = _SlotExprRenderCompletion(root)


@dataclass(eq=False, slots=True)
class _ExpressionExecution:
    completion: _SlotExprRenderCompletion
    state: SlotExprSlotContextStateMgr
    owner: _RenderAttempt

    def require_active(self) -> None:
        self.owner._require_open()
        self.owner._require_identity()
        if self.completion.active is not self.owner or self.completion._completing:
            raise RuntimeError("original expression render is no longer active")

    @contextmanager
    def scope(self, manager: CallSiteContextManager) -> Iterator[None]:
        self.require_active()
        with self.completion.pass_scope(self.state):
            if manager is not self.state._call_site_context_manager:
                self.completion.reject("shared expression uses a different collection")
            identity = id(self.state)
            if identity in self.completion._evaluating_states:
                self.completion.reject(
                    "recursive expression evaluation is not admitted"
                )
            self.completion._evaluating_states.add(identity)
            try:
                yield
            finally:
                self.completion._evaluating_states.discard(identity)
                self.completion.remember_collections(self.state)

    def bind_result(
        self, host: SlotCallBindingHost, result: Any, previous: SlotCallBinding | None
    ) -> SlotCallBinding:
        self.require_active()
        handler = select_slot_call_handler(result)
        self.require_active()
        if type(handler) is not SlotValueHandler:
            self.completion.reject("resource expression results are not admitted")
        binding = self.completion.bind_slot_call_result(handler, host, result, previous)
        self.require_active()
        return binding

    def finish_evaluation(self) -> None:
        self.require_active()
        self.state._call_site_context_manager._prepare_pass()
        self.require_active()


@dataclass(eq=False, slots=True)
class _SlotExprRenderCompletion(_MountRenderCompletion):
    _expression_states: dict[int, SlotExprSlotContextStateMgr] = field(
        default_factory=dict, init=False
    )
    _expression_collections: dict[int, _CallSiteCollection] = field(
        default_factory=dict, init=False
    )
    _evaluating_states: set[int] = field(default_factory=set, init=False)

    def require_slot_type(self, slot_type: type[Any]) -> None:
        from pyrolyze.runtime.context_bare_refactor_lcm import SlotExprSlotContext

        if slot_type is not SlotExprSlotContext:
            super(_SlotExprRenderCompletion, self).require_slot_type(slot_type)

    def expression_execution(
        self, state: SlotExprSlotContextStateMgr
    ) -> _ExpressionExecution:
        self.require_resource_owner()
        manager = state._call_site_context_manager
        if manager._owns_transaction:
            if manager.iter_current() or manager._active_transaction is not None:
                self.reject("cannot adopt an existing independent expression pass")
            context = RenderCallSitePassContext(
                transaction_manager=state._transaction_manager
            )
            manager = CallSiteContextManager._for_render_pass(
                context, state._transaction_manager, PASS_TX_KEY
            )
            state._call_site_context_manager = manager
        self._expression_states[id(state)] = state
        self.remember_collections(state)
        assert self.active is not None
        return _ExpressionExecution(self, state, self.active)

    def remember_collections(self, state: SlotExprSlotContextStateMgr) -> None:
        context = state._call_site_context_manager._pass_context
        for collection in (context.current.contexts, context.contexts):
            self._expression_collections[id(collection)] = collection

    def _complete(self, propagating: BaseException | None) -> None:
        assert self.active is not None
        owner = self.active
        failure: BaseException | None = None
        self._completing = True
        try:
            known = {
                id(state): state
                for state in _graph_states(self.root, current=True)
                if isinstance(state, SlotExprSlotContextStateMgr)
            }
            known.update(self._expression_states)
            self._expression_states = known
            if owner.first_failure is None and not owner._scopes:
                owner._require_identity()
                candidates = {
                    id(state) for state in _graph_states(self.root, current=False)
                }
                for identity, state in known.items():
                    self.remember_collections(state)
                    if identity not in candidates:
                        state._call_site_context_manager._replace_collection({})
                        owner._require_identity()
                        self.remember_collections(state)
        except BaseException as error:
            owner.fail(error)
            failure = error
            if propagating is None:
                propagating = error
        try:
            super(_SlotExprRenderCompletion, self)._complete(propagating)
        except BaseException as error:
            failure = error
        errors: list[BaseException] = []
        self._completing = True
        try:
            if owner.published is not None:
                retained = {
                    id(state._call_site_context_manager._pass_context.current.contexts)
                    for state in self._expression_states.values()
                }
                for identity, collection in self._expression_collections.items():
                    if identity not in retained:
                        try:
                            collection.release()
                        except BaseException as error:
                            errors.append(error)
                            self._cleanup_failure = error
                self._expression_collections.clear()
                self._expression_states.clear()
            # Unknown publication preserves ownership evidence for quarantine.
        finally:
            self._completing = False
        primary = failure if failure is not None else propagating
        if errors:
            if primary is not None:
                _raise_with_cleanup(primary, errors)
            if len(errors) == 1:
                raise errors[0]
            raise BaseExceptionGroup("expression retirement failed", errors)
        if failure is not None:
            raise failure
