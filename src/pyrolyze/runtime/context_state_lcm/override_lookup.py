"""Lexical candidate reads with stable, publication-only Drip notifications."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import weakref

from pyrolyze.runtime.app_context import (
    APP_CONTEXT_MISSING,
    AppContextKey,
    AppContextLookup,
)
from pyrolyze.runtime.drip import Drip


@dataclass(frozen=True, slots=True)
class _OverrideSelection:
    keys: tuple[AppContextKey[Any], ...] = ()
    values: tuple[Any, ...] = ()


class _OverrideDrip(Drip[object]):
    def __init__(self, state: Any, key: AppContextKey[Any]) -> None:
        super().__init__(initial=APP_CONTEXT_MISSING, elide_policy="equality")
        self._state_ref = weakref.ref(state)
        self._key = key
        self._notifying = False

    def get(self) -> Any:
        state = self._state_ref()
        if not self._notifying and state is not None and state.is_scope_active():
            try:
                return state._managed_lookup.get(self._key)
            except LookupError:
                return APP_CONTEXT_MISSING
        return super().get()

    def next(self, value: object | None) -> None:
        # Parent-stream events can arrive during a render. Their observers must
        # read that accepted event, not the render's lexical candidate value.
        notifying, self._notifying = self._notifying, True
        try:
            super().next(value)
        finally:
            self._notifying = notifying


@dataclass(frozen=True, slots=True)
class _OverrideLookup(AppContextLookup):
    state_ref: weakref.ReferenceType[Any]

    def get(self, key: AppContextKey[Any]) -> Any:
        state = self.state_ref()
        if state is None:
            raise LookupError(f"no authored app context for key {key.debug_name!r}")
        selection = (
            state._override if state.is_scope_active() else state.current._override
        )
        if key in selection.keys:
            value = selection.values[selection.keys.index(key)]
            if value is not None:
                return value
        return state._parent_state_mgr.effective_authored_app_context_lookup().get(key)

    def has(self, key: AppContextKey[Any]) -> bool:
        try:
            self.get(key)
        except LookupError:
            return False
        return True

    def resolve_drip(self, key: AppContextKey[Any]) -> Drip[object] | None:
        state = self.state_ref()
        if state is None:
            return None
        selection = (
            state._override if state.is_scope_active() else state.current._override
        )
        if key in selection.keys:
            return state._committed_key_states[key].drip
        return state._parent_state_mgr.effective_authored_app_context_lookup().resolve_drip(
            key
        )


def _override_lookup(self: Any) -> _OverrideLookup:
    return _OverrideLookup(weakref.ref(self))


def _structure_error(owner: Any) -> type[Exception]:
    return type(owner)._structure_error_cls
