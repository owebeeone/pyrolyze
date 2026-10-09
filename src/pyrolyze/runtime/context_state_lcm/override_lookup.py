"""Lexical candidate reads with stable, publication-only Drip notifications."""

from __future__ import annotations

from dataclasses import dataclass, field
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
    attempt_token: object | None = None
    publication_token: object = field(default_factory=object, repr=False, compare=False)

    def provenance(self) -> tuple[object, ...] | None:
        if self.attempt_token is None:
            return None
        return (self.publication_token, self.attempt_token)


@dataclass(frozen=True, slots=True)
class _OverrideReadReceipt:
    source_ref: weakref.ReferenceType[_OverrideDrip]
    provenance: tuple[object, ...]

    def acknowledges(self, source: _OverrideDrip) -> bool:
        publication = source._publication
        return (
            self.source_ref() is source
            and publication is not None
            and len(self.provenance) == len(publication)
            and all(
                read is delivered
                for read, delivered in zip(self.provenance, publication)
            )
        )


@dataclass(frozen=True, slots=True)
class _OverrideRead:
    """Private getter adapter; generic external stores retain their usual protocol."""

    source: _OverrideDrip

    def __call__(self) -> Any:
        return self.read()[0]

    def read(self) -> tuple[Any, _OverrideReadReceipt | None]:
        value, provenance = self.source.read()
        if value is APP_CONTEXT_MISSING:
            raise LookupError(
                f"no authored app context for key {self.source._key.debug_name!r}"
            )
        receipt = (
            None
            if provenance is None
            else _OverrideReadReceipt(weakref.ref(self.source), provenance)
        )
        return value, receipt


class _OverrideDrip(Drip[object]):
    def __init__(self, state: Any, key: AppContextKey[Any]) -> None:
        super().__init__(initial=APP_CONTEXT_MISSING, elide_policy="equality")
        self._state_ref = weakref.ref(state)
        self._key = key
        self._notifying = False
        self._publication: tuple[object, ...] | None = None
        self._published_provenance: tuple[object, ...] | None = None

    def get(self) -> Any:
        return self.read()[0]

    def read(self) -> tuple[Any, tuple[object, ...] | None]:
        state = self._state_ref()
        if not self._notifying and state is not None and state.is_scope_active():
            try:
                return state._managed_lookup.read(self._key)
            except LookupError:
                return APP_CONTEXT_MISSING, None
        return super().get(), None

    def next(self, value: object | None) -> None:
        self._deliver(value, None)

    def publish(
        self, value: object | None, provenance: tuple[object, ...] | None
    ) -> None:
        self._deliver(value, provenance)

    def _deliver(
        self, value: object | None, provenance: tuple[object, ...] | None
    ) -> None:
        # Parent-stream events can arrive during a render. Their observers must
        # read that accepted event, not the render's lexical candidate value.
        notifying, self._notifying = self._notifying, True
        publication, self._publication = self._publication, provenance
        # Ordinary reentrant events must not inherit an enclosing publication.
        self._published_provenance = provenance
        try:
            super().next(value)
        except BaseException:
            # Equality or an observer may fail before delivery is certified.
            self._published_provenance = None
            raise
        finally:
            self._publication = publication
            self._notifying = notifying


@dataclass(frozen=True, slots=True)
class _OverrideLookup(AppContextLookup):
    state_ref: weakref.ReferenceType[Any]

    def get(self, key: AppContextKey[Any]) -> Any:
        return self.read(key)[0]

    def read(self, key: AppContextKey[Any]) -> tuple[Any, tuple[object, ...] | None]:
        state = self.state_ref()
        if state is None:
            raise LookupError(f"no authored app context for key {key.debug_name!r}")
        active = state.is_scope_active()
        selection = state._override if active else state.current._override
        provenance = selection.provenance() if active else None
        if key in selection.keys:
            value = selection.values[selection.keys.index(key)]
            if value is not None:
                return value, provenance
        parent = state._parent_state_mgr.effective_authored_app_context_lookup()
        if isinstance(parent, _OverrideLookup):
            value, parent_provenance = parent.read(key)
            return value, (
                provenance + parent_provenance
                if provenance is not None and parent_provenance is not None
                else None
            )
        # A plain parent stream has no exact publication identity to acknowledge.
        return parent.get(key), None

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
