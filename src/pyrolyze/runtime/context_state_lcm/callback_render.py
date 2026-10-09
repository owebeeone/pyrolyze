"""Private callback selection admission; other resource routes remain gated."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .field_only_render import _FieldOnlyRenderCompletion, _enable_field_only_render

if TYPE_CHECKING:
    from ._base import StateMgrBase
    from .component_call_slot_context import ComponentCallSlotContextStateMgr
    from .render_context import RenderContextStateMgr


def _enable_callback_render(root: RenderContextStateMgr) -> None:
    _enable_field_only_render(root)
    root._field_only_completion = _CallbackRenderCompletion(root)


def _graph_states(
    root: RenderContextStateMgr, *, current: bool, render_local: bool = False
) -> tuple[StateMgrBase, ...]:
    return _graph_states_many((root,), current=current, render_local=render_local)


def _graph_states_many(
    roots: Iterable[RenderContextStateMgr], *, current: bool, render_local: bool = False
) -> tuple[StateMgrBase, ...]:
    from .component_call_slot_context import ComponentCallSlotContextStateMgr
    from .context_base import ContextBaseStateMgr
    from .render_context import RenderContextStateMgr

    states: list[StateMgrBase] = []
    visited: set[int] = set()

    def visit(state: Any) -> None:
        if (
            render_local
            and isinstance(state, RenderContextStateMgr)
            and state is not root
        ):
            return
        if id(state) in visited:
            return
        visited.add(id(state))
        states.append(state)
        if isinstance(state, ContextBaseStateMgr):
            facade = state.current if current else state
            for child in facade.children_state.values():
                visit(child)
        if isinstance(state, ComponentCallSlotContextStateMgr):
            facade = state.current if current else state
            nested = facade._child_context_state_mgr
            if nested is not None:
                visit(nested)

    # Nested roots overlap. Share visitation only within this traversal/view;
    # later staging and publication can change which descendants are reachable.
    for root in roots:
        visit(root)
    return tuple(states)


@dataclass(eq=False, slots=True)
class _CallbackRenderCompletion(_FieldOnlyRenderCompletion):
    owned_handler_passes: list[ComponentCallSlotContextStateMgr] = field(
        default_factory=list, init=False
    )

    def note_owned_event_handler_pass(
        self, context: ComponentCallSlotContextStateMgr
    ) -> None:
        if self.active is None or self._completing:
            self.reject("owned-handler selection requires an active render execution")
        self.active._require_open()
        self.active._require_identity()
        if context not in self.owned_handler_passes:
            self.owned_handler_passes.append(context)

    def require_event_handler_binding(self) -> None:
        return None

    def require_slot_type(self, slot_type: type[Any]) -> None:
        from pyrolyze.runtime.context_bare_refactor_lcm import EventHandlerSlotContext

        if slot_type is not EventHandlerSlotContext:
            super(_CallbackRenderCompletion, self).require_slot_type(slot_type)

    def _complete(self, propagating: BaseException | None) -> None:
        from .event_handler_slot_context import EventHandlerSlotContextStateMgr

        assert self.active is not None
        owner = self.active
        self._completing = True
        preparation_error: BaseException | None = None
        try:
            if owner.first_failure is None and not owner._scopes:
                owner._require_identity()
                for state in self.owned_handler_passes:
                    children = state.children_state
                    retained = {
                        slot_id: child
                        for slot_id, child in children.items()
                        if not isinstance(child, EventHandlerSlotContextStateMgr)
                        or child._seen_in_pass
                    }
                    if len(retained) != len(children):
                        state.children_state = retained
                candidates = {
                    id(state) for state in _graph_states(self.root, current=False)
                }
                known = {
                    id(state): state
                    for state in _graph_states(self.root, current=True)
                    if isinstance(state, EventHandlerSlotContextStateMgr)
                }
                for render in self.render_roots:
                    for state in render._slots_by_id.values():
                        if isinstance(state, EventHandlerSlotContextStateMgr):
                            known[id(state)] = state
                # Removal is staged before participant capture, never applied by
                # this adapter. Include new handlers omitted before acceptance.
                for identity, handler in known.items():
                    if identity not in candidates:
                        handler._stage_retirement()
        except BaseException as error:
            owner.fail(error)
            preparation_error = error
            if propagating is None:
                propagating = error
        try:
            super(_CallbackRenderCompletion, self)._complete(propagating)
        finally:
            self.owned_handler_passes.clear()
        if preparation_error is not None:
            raise preparation_error

    def _reconcile_registry(self) -> None:
        from .event_handler_slot_context import EventHandlerSlotContextStateMgr

        super(_CallbackRenderCompletion, self)._reconcile_registry()
        for state in self.owned_handler_passes:
            state._pass_owned_event_handler_order = ()
            for child in state.current.children_state.values():
                if isinstance(child, EventHandlerSlotContextStateMgr) and not getattr(
                    self, "pass_state_selection_enabled", False
                ):
                    child._seen_in_pass = True
