"""Override admission; domain notifications follow accepted graph publication."""

from dataclasses import dataclass, field
from typing import Any

from .component_render import _ComponentRenderCompletion
from .callback_render import _graph_states, _graph_states_many
from .app_context_override_slot_context import (
    AppContextOverrideSlotContextStateMgr,
    _CommittedAppContextOverrideKeyState,
)
from pyrolyze.runtime.drip import Drip
from .override_lookup import _OverrideSelection


@dataclass(eq=False, slots=True)
class _OverrideRenderCompletion(_ComponentRenderCompletion):
    override_selection_enabled = True
    _overrides: dict[int, AppContextOverrideSlotContextStateMgr] = field(
        default_factory=dict, init=False
    )

    def require_slot_type(self, slot_type: type[Any]) -> None:
        from pyrolyze.runtime.context_lifecycle import (
            AppContextOverrideSlotContext,
        )

        if slot_type is not AppContextOverrideSlotContext:
            super(_OverrideRenderCompletion, self).require_slot_type(slot_type)

    def _complete(self, propagating: BaseException | None) -> None:
        assert self.active is not None
        owner = self.active
        for current in (True, False):
            for state in _graph_states_many((self.root, *self.render_roots), current=current):
                if isinstance(state, AppContextOverrideSlotContextStateMgr):
                    self._overrides[id(state)] = state
        if owner.first_failure is None and not owner._scopes:
            try:
                owner._require_identity()
                candidates = {
                    id(state) for state in _graph_states(self.root, current=False)
                }
                for identity, state in self._overrides.items():
                    if identity not in candidates:
                        state._override = _OverrideSelection()
                owner._require_identity()
            except BaseException as error:
                owner.fail(error)
                if propagating is None:
                    propagating = error
        super(_OverrideRenderCompletion, self)._complete(propagating)

    def _after_field_publication(self, published: bool) -> None:
        super(_OverrideRenderCompletion, self)._after_field_publication(published)
        retained = {id(state) for state in _graph_states(self.root, current=True)}
        errors: list[BaseException] = []
        deliveries: list[
            tuple[
                _CommittedAppContextOverrideKeyState, Any,
                Drip[object] | None, tuple[object, ...] | None,
            ]
        ] = []
        pending, self._overrides = self._overrides, {}
        for identity, state in pending.items():
            selection = state.current._override
            for key, key_state in tuple(state._committed_key_states.items()):
                try:
                    if identity not in retained or key not in selection.keys:
                        key_state.deactivate()
                        state._committed_key_states.pop(key, None)
                    elif published:
                        # Existing parent callbacks must use this accepted
                        # selection before any stream in the batch delivers.
                        key_state._provenance = selection.provenance()
                        value = selection.values[selection.keys.index(key)]
                        parent_drip = (
                            state._parent_state_mgr.effective_authored_app_context_lookup().resolve_drip(
                                key
                            )
                            if value is None
                            else None
                        )
                        # Detach stale/removed links across the entire batch
                        # before a parent update can reach a now-concrete child.
                        if (
                            value is not None
                            or key_state.parent_drip is not parent_drip
                        ):
                            key_state.deactivate()
                        deliveries.append(
                            (key_state, value, parent_drip, key_state._provenance)
                        )
                except BaseException as error:
                    errors.append(error)
                    self._cleanup_failure = error
        for key_state, value, parent_drip, provenance in deliveries:
            try:
                if value is None:
                    key_state.sync_parent(parent_drip, provenance)
                else:
                    key_state.sync_value(value, provenance)
            except BaseException as error:
                errors.append(error)
                self._cleanup_failure = error
        if errors:
            if len(errors) == 1:
                raise errors[0]
            raise BaseExceptionGroup("override publication failed", errors)
