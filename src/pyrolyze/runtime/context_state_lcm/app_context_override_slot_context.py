from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from pyrolyze.runtime.app_context import (
    APP_CONTEXT_MISSING,
    EMPTY_APP_CONTEXT_LOOKUP,
    AppContextKey,
    AppContextLookup,
    OverlayAppContextLookup,
)
from pyrolyze.runtime.drip import Drip

from .rerunnable_slot_context import RerunnableSlotContextStateMgr


def _empty_authored_app_context_lookup() -> AppContextLookup:
    return EMPTY_APP_CONTEXT_LOOKUP


def _authored_app_context_drip() -> Drip[object]:
    return Drip(initial=APP_CONTEXT_MISSING, elide_policy="equality")


@dataclass(slots=True)
class _ParentAuthoredAppContextLookup(AppContextLookup):
    parent_context: Any

    def get(self, key: AppContextKey[Any]) -> Any:
        return self.parent_context._effective_authored_app_context_lookup().get(key)

    def has(self, key: AppContextKey[Any]) -> bool:
        return self.parent_context._effective_authored_app_context_lookup().has(key)

    def resolve_drip(self, key: AppContextKey[Any]) -> Drip[object] | None:
        return self.parent_context._effective_authored_app_context_lookup().resolve_drip(key)


@dataclass(slots=True)
class _CommittedAppContextOverrideKeyState:
    key: AppContextKey[Any]
    drip: Drip[object] = field(default_factory=_authored_app_context_drip)
    parent_drip: Drip[object] | None = None
    unsubscribe_parent: Callable[[], None] | None = None

    def sync_value(self, value: Any) -> None:
        self._clear_parent_link()
        self.drip.next(value)

    def sync_parent(self, parent_drip: Drip[object] | None) -> None:
        if parent_drip is None:
            self._clear_parent_link()
            self.drip.next(APP_CONTEXT_MISSING)
            return
        if self.parent_drip is parent_drip and self.unsubscribe_parent is not None:
            self.drip.next(parent_drip.get())
            return

        self._clear_parent_link()
        self.parent_drip = parent_drip
        self.drip.next(parent_drip.get())

        def on_parent_change(next_value: object | None) -> None:
            self.drip.next(APP_CONTEXT_MISSING if next_value is None else next_value)

        self.unsubscribe_parent = parent_drip.subscribe_priority(on_parent_change)

    def deactivate(self) -> None:
        self._clear_parent_link()

    def _clear_parent_link(self) -> None:
        unsubscribe = self.unsubscribe_parent
        self.unsubscribe_parent = None
        self.parent_drip = None
        if unsubscribe is not None:
            unsubscribe()


class AppContextOverrideSlotContextStateMgr(RerunnableSlotContextStateMgr):
    def stage_override(self, keys: tuple[Any, ...], values: tuple[Any, ...]) -> None:
        owner = self.owner
        self._validate_override(keys, values)
        if owner.declared_keys and owner.declared_keys != keys:
            raise owner._structure_error_cls(
                "app_context_override fixed keys cannot change at one slot"
            )
        if not owner.declared_keys:
            owner.declared_keys = keys
        self._apply_pending_values(values)
        owner._pending_values = values
        owner._pending_lookup = OverlayAppContextLookup(
            parent=_ParentAuthoredAppContextLookup(owner.parent),
            drips={key: owner._committed_key_states[key].drip for key in keys},
        )
        owner._pending_initialized = True

    def effective_authored_app_context_lookup(self) -> AppContextLookup:
        owner = self.owner
        if owner._scope_active and owner._pending_initialized:
            return owner._pending_lookup
        if owner.declared_keys:
            return owner._committed_lookup
        return owner.parent._effective_authored_app_context_lookup()

    def begin_scope_pass(self) -> None:
        owner = self.owner
        owner._pass_committed_values = owner.committed_values
        owner._pass_committed_lookup = owner._committed_lookup
        super().begin_pass()

    def commit_scope_pass(self) -> None:
        owner = self.owner
        if not owner._pending_initialized:
            raise RuntimeError("app_context_override slot was not staged")
        owner.committed_values = owner._pending_values
        owner._committed_lookup = OverlayAppContextLookup(
            parent=_ParentAuthoredAppContextLookup(owner.parent),
            drips={key: owner._committed_key_states[key].drip for key in owner.declared_keys},
        )
        super().end_pass()
        owner._pending_values = ()
        owner._pending_lookup = EMPTY_APP_CONTEXT_LOOKUP
        owner._pending_initialized = False
        owner._pass_committed_values = ()
        owner._pass_committed_lookup = EMPTY_APP_CONTEXT_LOOKUP

    def rollback_scope_pass(self) -> None:
        owner = self.owner
        super().rollback_pass()
        owner.committed_values = owner._pass_committed_values
        owner._committed_lookup = owner._pass_committed_lookup
        if owner.declared_keys and len(owner._pass_committed_values) == len(owner.declared_keys):
            self._apply_values(owner._pass_committed_values)
        elif not owner._pass_committed_values:
            for state in owner._committed_key_states.values():
                state.deactivate()
        owner._pending_values = ()
        owner._pending_lookup = EMPTY_APP_CONTEXT_LOOKUP
        owner._pending_initialized = False
        owner._pass_committed_values = ()
        owner._pass_committed_lookup = EMPTY_APP_CONTEXT_LOOKUP

    def deactivate(self) -> None:
        owner = self.owner
        for state in owner._committed_key_states.values():
            state.deactivate()
        owner._committed_key_states = {}
        owner._pending_values = ()
        owner._pending_lookup = EMPTY_APP_CONTEXT_LOOKUP
        owner._pending_initialized = False
        super().deactivate()

    def __post_init__(self) -> None:
        super().__post_init__()
        owner = self.owner
        owner.declared_keys = ()
        owner.committed_values = ()
        owner._committed_key_states = {}
        owner._committed_lookup = EMPTY_APP_CONTEXT_LOOKUP
        owner._pass_committed_values = ()
        owner._pass_committed_lookup = EMPTY_APP_CONTEXT_LOOKUP
        owner._pending_values = ()
        owner._pending_lookup = EMPTY_APP_CONTEXT_LOOKUP
        owner._pending_initialized = False

    def _apply_pending_values(self, values: tuple[Any, ...]) -> None:
        self._apply_values(values)

    def _apply_values(self, values: tuple[Any, ...]) -> None:
        owner = self.owner
        parent_lookup = owner.parent._effective_authored_app_context_lookup()
        for key, value in zip(owner.declared_keys, values, strict=True):
            state = owner._committed_key_states.get(key)
            if state is None:
                state = _CommittedAppContextOverrideKeyState(key=key)
                owner._committed_key_states[key] = state
            if value is None:
                state.sync_parent(parent_lookup.resolve_drip(key))
            else:
                state.sync_value(value)

    def _validate_override(
        self,
        keys: tuple[AppContextKey[Any], ...],
        values: tuple[Any, ...],
    ) -> None:
        if not keys:
            raise self.owner._structure_error_cls("app_context_override requires at least one key")
        if len(keys) != len(values):
            raise self.owner._structure_error_cls(
                "app_context_override key/value arity must match"
            )
        seen: set[AppContextKey[Any]] = set()
        for key in keys:
            if not isinstance(key, AppContextKey):
                raise self.owner._structure_error_cls(
                    "app_context_override keys must be AppContextKey instances"
                )
            if key in seen:
                raise self.owner._structure_error_cls(
                    f"app_context_override duplicate key {key.debug_name!r}"
                )
            seen.add(key)
