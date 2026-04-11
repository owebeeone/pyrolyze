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
    def __init__(self, owner: object, **kwargs: object) -> None:
        super().__init__(owner, **kwargs)
        self._structure_error_cls = type(owner)._structure_error_cls
        self._declared_keys: tuple[Any, ...] = ()
        self._committed_values: tuple[Any, ...] = ()
        self._committed_key_states: dict[Any, _CommittedAppContextOverrideKeyState] = {}
        self._committed_lookup: AppContextLookup = EMPTY_APP_CONTEXT_LOOKUP
        self._pass_committed_values: tuple[Any, ...] = ()
        self._pass_committed_lookup: AppContextLookup = EMPTY_APP_CONTEXT_LOOKUP
        self._pending_values: tuple[Any, ...] = ()
        self._pending_lookup: AppContextLookup = EMPTY_APP_CONTEXT_LOOKUP
        self._pending_initialized = False

    def stage_override(self, keys: tuple[Any, ...], values: tuple[Any, ...]) -> None:
        self._validate_override(keys, values)
        if self._declared_keys and self._declared_keys != keys:
            raise self._structure_error_cls(
                "app_context_override fixed keys cannot change at one slot"
            )
        if not self._declared_keys:
            self._declared_keys = keys
        self._apply_pending_values(values)
        self._pending_values = values
        self._pending_lookup = OverlayAppContextLookup(
            parent=self._parent_state_mgr.effective_authored_app_context_lookup(),
            drips={key: self._committed_key_states[key].drip for key in keys},
        )
        self._pending_initialized = True

    def effective_authored_app_context_lookup(self) -> AppContextLookup:
        if self._scope_active and self._pending_initialized:
            return self._pending_lookup
        if self._declared_keys:
            return self._committed_lookup
        return self._parent_state_mgr.effective_authored_app_context_lookup()

    def begin_scope_pass(self) -> None:
        self._pass_committed_values = self._committed_values
        self._pass_committed_lookup = self._committed_lookup
        super().begin_pass()

    def commit_scope_pass(self) -> None:
        if not self._pending_initialized:
            raise RuntimeError("app_context_override slot was not staged")
        self._committed_values = self._pending_values
        self._committed_lookup = OverlayAppContextLookup(
            parent=self._parent_state_mgr.effective_authored_app_context_lookup(),
            drips={key: self._committed_key_states[key].drip for key in self._declared_keys},
        )
        super().end_pass()
        self._pending_values = ()
        self._pending_lookup = EMPTY_APP_CONTEXT_LOOKUP
        self._pending_initialized = False
        self._pass_committed_values = ()
        self._pass_committed_lookup = EMPTY_APP_CONTEXT_LOOKUP

    def rollback_scope_pass(self) -> None:
        super().rollback_pass()
        self._committed_values = self._pass_committed_values
        self._committed_lookup = self._pass_committed_lookup
        if self._declared_keys and len(self._pass_committed_values) == len(self._declared_keys):
            self._apply_values(self._pass_committed_values)
        elif not self._pass_committed_values:
            for state in self._committed_key_states.values():
                state.deactivate()
        self._pending_values = ()
        self._pending_lookup = EMPTY_APP_CONTEXT_LOOKUP
        self._pending_initialized = False
        self._pass_committed_values = ()
        self._pass_committed_lookup = EMPTY_APP_CONTEXT_LOOKUP

    def deactivate(self) -> None:
        for state in self._committed_key_states.values():
            state.deactivate()
        self._committed_key_states = {}
        self._pending_values = ()
        self._pending_lookup = EMPTY_APP_CONTEXT_LOOKUP
        self._pending_initialized = False
        super().deactivate()

    def _apply_pending_values(self, values: tuple[Any, ...]) -> None:
        self._apply_values(values)

    def _apply_values(self, values: tuple[Any, ...]) -> None:
        parent_lookup = self._parent_state_mgr.effective_authored_app_context_lookup()
        for key, value in zip(self._declared_keys, values, strict=True):
            state = self._committed_key_states.get(key)
            if state is None:
                state = _CommittedAppContextOverrideKeyState(key=key)
                self._committed_key_states[key] = state
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
            raise self._structure_error_cls("app_context_override requires at least one key")
        if len(keys) != len(values):
            raise self._structure_error_cls(
                "app_context_override key/value arity must match"
            )
        seen: set[AppContextKey[Any]] = set()
        for key in keys:
            if not isinstance(key, AppContextKey):
                raise self._structure_error_cls(
                    "app_context_override keys must be AppContextKey instances"
                )
            if key in seen:
                raise self._structure_error_cls(
                    f"app_context_override duplicate key {key.debug_name!r}"
                )
            seen.add(key)
