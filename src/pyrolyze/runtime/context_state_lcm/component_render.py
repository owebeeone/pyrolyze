"""Stage component retirement before publication, detach only known orphans."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .callback_render import _graph_states, _graph_states_many
from .component_call_slot_context import (
    ComponentCallSlotContextStateMgr,
    _ComponentSelection,
)
from .context_base import ContextBaseStateMgr
from .field_only_render import _field_only_completion
from .mount_expr_render import _MountExprRenderCompletion, _enable_mount_expr_render
from .render_attempt import _raise_with_cleanup
from .render_context import RenderContextStateMgr


@dataclass(eq=False, slots=True)
class _ComponentRenderCompletion(_MountExprRenderCompletion):
    component_selection_enabled = True
    _child_roots: dict[int, RenderContextStateMgr] = field(
        default_factory=dict, init=False
    )

    def require_retirement_allowed(self, context: Any) -> None:
        self.require_resource_owner()
        if _field_only_completion(context) is not self:
            self.reject("component retirement belongs to a different render")

    def _complete(self, propagating: BaseException | None) -> None:
        assert self.active is not None
        owner = self.active
        roots = (self.root, *self.render_roots)
        known = {id(state): state for state in _graph_states_many(roots, current=True)}
        for render in self.render_roots:
            if render is not self.root:
                self._child_roots[id(render)] = render
        known.update(
            {
                id(state): state
                for state in _graph_states_many(self.render_roots, current=False)
            }
        )
        for state in known.values():
            if isinstance(state, RenderContextStateMgr) and state is not self.root:
                self._child_roots[id(state)] = state
        failure: BaseException | None = None
        self._completing = True
        try:
            if owner.first_failure is None and not owner._scopes:
                owner._require_identity()
                candidates = {
                    id(state) for state in _graph_states(self.root, current=False)
                }
                # Removal is data staging, not recursive deactivate(): existing
                # resource adapters see the old/current graph and drain owners.
                for identity, state in known.items():
                    if identity in candidates:
                        continue
                    if isinstance(state, ComponentCallSlotContextStateMgr):
                        state._selection = _ComponentSelection()
                        state._call_pending_dirty_state = None
                    if isinstance(state, ContextBaseStateMgr):
                        state.children_state = {}
                        state.own_ui_state = ()
                        state.own_ui_entries_state = ()
                        state.ui_state = ()
                owner._require_identity()
        except BaseException as error:
            owner.fail(error)
            failure = error
            if propagating is None:
                propagating = error
        try:
            super(_ComponentRenderCompletion, self)._complete(propagating)
        except BaseException as error:
            failure = error
        errors: list[BaseException] = []
        self._completing = True
        try:
            if owner.published is not None:
                retained = {
                    id(state) for state in _graph_states(self.root, current=True)
                }
                roots, self._child_roots = self._child_roots, {}
                for identity, render in roots.items():
                    if identity in retained:
                        continue
                    # Also detach failed/superseded candidates retained by a
                    # traceback. Never infer retirement from Python lifetime.
                    render._mounted_callback = None
                    render._slots_by_id.clear()
                    try:
                        render._remove_from_scheduler()
                    except BaseException as error:
                        errors.append(error)
                        self._cleanup_failure = error
            # Unknown publication retains roots as quarantined evidence.
        finally:
            self._completing = False
        if errors:
            primary = failure if failure is not None else propagating
            if primary is not None:
                _raise_with_cleanup(primary, errors)
            if len(errors) == 1:
                raise errors[0]
            raise BaseExceptionGroup("component retirement failed", errors)
        if failure is not None:
            raise failure


def _enable_component_render(root: RenderContextStateMgr) -> None:
    _enable_mount_expr_render(root)
    root._field_only_completion = _ComponentRenderCompletion(root)
