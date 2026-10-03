"""Private SC2 activation; resource-bearing graphs remain on the legacy route."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .render_attempt import _LocalRenderScope, _RenderAttempt, _raise_with_cleanup

if TYPE_CHECKING:
    from .context_base import ContextBaseStateMgr
    from .render_context import RenderContextStateMgr


def _nearest_render_state(context: Any) -> Any:
    resolve = getattr(context, "root_context_state_mgr", None)
    if resolve is not None:
        return resolve()
    return getattr(context, "_render_context_state_mgr", None) or context


def _field_only_completion(context: Any) -> _FieldOnlyRenderCompletion | None:
    root = _nearest_render_state(context)
    scheduler_root = getattr(root, "_scheduler_root_state_mgr", root)
    return getattr(scheduler_root, "_field_only_completion", None)


def _enable_field_only_render(root: RenderContextStateMgr) -> None:
    from pyrolyze.runtime.context_bare_refactor_lcm import RenderContext
    from .context_base import PASS_TX_KEY
    from .render_context import RenderContextStateMgr

    if (
        type(root) is not RenderContextStateMgr
        or type(root.owner) is not RenderContext
        or root._scheduler_root_state_mgr is not root
        or root._owner_slot_state_mgr is not None
    ):
        raise RuntimeError("field-only activation requires an exact scheduler root")
    if (
        root._slots_by_id
        or root.children_state
        or root._mounted_callback is not None
        or root._transaction_manager.active_transaction_for(PASS_TX_KEY) is not None
        or _field_only_completion(root) is not None
        or getattr(root, "_has_entered_pass", False)
    ):
        raise RuntimeError("field-only activation requires a fresh graph")
    root._field_only_completion = _FieldOnlyRenderCompletion(root)


@dataclass(eq=False, slots=True)
class _FieldOnlyRenderCompletion:
    root: RenderContextStateMgr
    active: _RenderAttempt | None = field(default=None, init=False)
    last: _RenderAttempt | None = field(default=None, init=False)
    contexts: list[ContextBaseStateMgr] = field(default_factory=list, init=False)
    render_roots: list[RenderContextStateMgr] = field(default_factory=list, init=False)
    _completing: bool = field(default=False, init=False)
    _cleanup_failure: BaseException | None = field(default=None, init=False)
    _execution_depth: int = field(default=0, init=False)
    _completion_requested: bool = field(default=False, init=False)

    def require_slot_type(self, slot_type: type[Any]) -> None:
        from pyrolyze.runtime.context_bare_refactor_lcm import (
            ComponentCallSlotContext,
            LeafSlotContext,
            SlotContext,
        )

        if slot_type not in (
            SlotContext,
            LeafSlotContext,
            ComponentCallSlotContext,
        ):
            self.reject("resource-bearing slot is not admitted by SC2")

    def reject(self, message: str) -> None:
        error = RuntimeError(message)
        if self.active is not None:
            self.active.fail(error)
        raise error

    def require_retirement_allowed(self, context: Any) -> None:
        from .component_call_slot_context import ComponentCallSlotContextStateMgr
        from .context_base import ContextBaseStateMgr

        visited: set[int] = set()

        def check(state: Any) -> None:
            if id(state) in visited:
                return
            visited.add(id(state))
            if isinstance(state, ComponentCallSlotContextStateMgr):
                self.reject("component retirement is not admitted by SC2")
            if isinstance(state, ContextBaseStateMgr):
                for children in (state.current.children_state, state.children_state):
                    for child in children.values():
                        check(child)

        check(context)

    def require_attachment(
        self, parent: ContextBaseStateMgr, render: RenderContextStateMgr, slot_id: Any
    ) -> None:
        if self.active is None:
            self.reject("slot construction requires an active render execution")
        self.active._require_open()
        self.active._require_identity()
        if (
            slot_id in parent.children_state
            or slot_id in parent.current.children_state
            or slot_id in render._slots_by_id
        ):
            self.reject("slot replacement is not admitted by SC2")

    def note_render_root(self, render: RenderContextStateMgr) -> None:
        if self.active is not None and render not in self.render_roots:
            self.render_roots.append(render)

    def _start(self) -> None:
        from .context_base import PASS_TX_KEY

        if self._completing:
            self.reject("field-only render completion is in progress")
        if self._cleanup_failure is not None or (
            self.last is not None and not self.last.reuse_ready
        ):
            self.reject("render completion is not ready for reuse")
        tracker = self.root.get_app_context(self.root._generation_tracker_key)
        if tracker.active_generation_id is not None:
            self.reject("render generation is already active")
        owner = _RenderAttempt.start(self.root._transaction_manager, PASS_TX_KEY)
        self.active = owner
        self.contexts = []
        self.render_roots = [self.root]
        self._execution_depth = 0
        self._completion_requested = False
        try:
            tracker.begin()
        except BaseException as error:
            owner.fail(error)
            self._complete(error)
            raise

    @contextmanager
    def attempt_scope(self) -> Iterator[None]:
        outer = self.active is None
        if outer:
            self._start()
        elif self._completing:
            self.reject("field-only render completion is in progress")
        assert self.active is not None
        owner = self.active
        error: BaseException | None = None
        self._execution_depth += 1
        try:
            owner._require_open()
            owner._require_identity()
            yield
        except BaseException as caught:
            error = caught
            owner.fail(caught)
            raise
        finally:
            if outer:
                self._completion_requested = True
            self._execution_depth -= 1
            if self._execution_depth == 0 and self._completion_requested:
                self._complete(error)

    @contextmanager
    def pass_scope(self, context: ContextBaseStateMgr) -> Iterator[None]:
        with self.attempt_scope():
            if context.is_scope_active():
                scope = getattr(context, "_field_only_local_scope", None)
                if scope is not None:
                    scope._require_active()
                yield
                return
            assert self.active is not None
            scope = self.active.scope(
                context,
                manager=context._transaction_manager,
                on_enter=lambda: self._enter_context(context),
                on_exit=context._end_field_only_pass,
                on_abort=context._abort_field_only_pass,
            )
            try:
                with scope:
                    context._field_only_local_scope = scope
                    context._field_only_outer_pass = False
                    yield
            finally:
                context._field_only_local_scope = None
                context._field_only_outer_pass = False

    def _enter_context(self, context: ContextBaseStateMgr) -> None:
        if context not in self.contexts:
            self.contexts.append(context)
        context._begin_field_only_pass()

    def begin_pass(self, context: ContextBaseStateMgr) -> None:
        outer = self.active is None
        if outer:
            self._start()
        elif self._completing:
            self.reject("field-only render completion is in progress")
        assert self.active is not None
        owner = self.active
        try:
            scope = owner.begin_scope(
                context,
                manager=context._transaction_manager,
                on_enter=lambda: self._enter_context(context),
                on_exit=context._end_field_only_pass,
                on_abort=context._abort_field_only_pass,
            )
        except BaseException as error:
            if outer:
                self._complete(error)
            raise
        context._field_only_local_scope = scope
        context._field_only_outer_pass = outer

    def finish_pass(
        self, context: ContextBaseStateMgr, error: BaseException | None = None
    ) -> None:
        scope: _LocalRenderScope | None = getattr(
            context, "_field_only_local_scope", None
        )
        if scope is None:
            self.reject("local render scope is not active")
        scope._require_active()
        outer = context._field_only_outer_pass
        caught: BaseException | None = error
        try:
            if error is None:
                scope.finish()
            else:
                scope.abort(error)
        except BaseException as failure:
            caught = failure
            raise
        finally:
            context._field_only_local_scope = None
            context._field_only_outer_pass = False
            if outer:
                self._completion_requested = True
                if self._execution_depth == 0:
                    self._complete(caught)

    def _complete(self, propagating: BaseException | None) -> None:
        assert self.active is not None
        owner = self.active
        self._completing = True
        failure: BaseException | None = None
        try:
            owner.finish(propagating)
        except BaseException as error:
            failure = error
        finally:
            self.last = owner
            try:
                if owner.reuse_ready:
                    published = owner.first_failure is None
                    for context in self.contexts:
                        context._clear_field_only_pass(published=published)
                    self._reconcile_registry()
                    tracker = self.root.get_app_context(
                        self.root._generation_tracker_key
                    )
                    if published:
                        tracker.commit()
                    else:
                        tracker.rollback()
            except BaseException as error:
                self._cleanup_failure = error
                primary = failure or propagating
                if primary is not None:
                    _raise_with_cleanup(primary, [error])
                raise
            finally:
                for context in self.contexts:
                    context._field_only_local_scope = None
                    context._field_only_outer_pass = False
                self.active = None
                self.contexts = []
                self.render_roots = []
                self._completing = False
                self._completion_requested = False
        if failure is not None:
            raise failure

    def _reconcile_registry(self) -> None:
        # Registrations are a cache of current membership, not resource lifetime.
        from .component_call_slot_context import ComponentCallSlotContextStateMgr
        from .context_base import ContextBaseStateMgr

        visited: set[int] = set()

        def rebuild(render: RenderContextStateMgr) -> None:
            if id(render) in visited:
                return
            visited.add(id(render))
            render._slots_by_id.clear()
            visit(render, render)

        def visit(render: RenderContextStateMgr, parent: ContextBaseStateMgr) -> None:
            if not isinstance(parent, ContextBaseStateMgr):
                return
            for slot_id, child in parent.current.children_state.items():
                render._slots_by_id[slot_id] = child
                if isinstance(child, ComponentCallSlotContextStateMgr):
                    nested = child._child_context_state_mgr
                    if nested is not None:
                        rebuild(nested)
                visit(render, child)

        rebuild(self.root)
        reachable = set(visited)
        affected = self.render_roots + [
            _nearest_render_state(context) for context in self.contexts
        ]
        for render in affected:
            if id(render) not in reachable and render._owner_slot_state_mgr is not None:
                # Cancel only orphan scheduler bookkeeping, not resource lifetime.
                render._remove_from_scheduler()
            rebuild(render)
