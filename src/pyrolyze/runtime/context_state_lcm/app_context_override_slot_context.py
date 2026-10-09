from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable
import weakref

from pyrolyze.runtime.app_context import (
    APP_CONTEXT_MISSING,
    EMPTY_APP_CONTEXT_LOOKUP,
    AppContextKey,
    AppContextLookup,
    OverlayAppContextLookup,
)
from pyrolyze.runtime.drip import Drip

from .rerunnable_slot_context import RerunnableSlotContextStateMgr
from .context_base import PASS_TX_KEY
from .field_only_render import _field_only_completion
from .lifecycle_adapter import const, local_store, managed, managed_context
from .override_lookup import (
    _OverrideSelection,
    _OverrideDrip,
    _override_lookup,
    _structure_error,
)


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
        return (
            self.parent_context._effective_authored_app_context_lookup().resolve_drip(
                key
            )
        )


@dataclass(slots=True, weakref_slot=True)
class _CommittedAppContextOverrideKeyState:
    key: AppContextKey[Any]
    drip: Drip[object] = field(default_factory=_authored_app_context_drip)
    parent_drip: Drip[object] | None = None
    unsubscribe_parent: Callable[[], None] | None = None
    _parent_finalizer: weakref.finalize | None = field(default=None, init=False)
    _provenance: tuple[object, ...] | None = field(default=None, init=False)

    def sync_value(
        self, value: Any, provenance: tuple[object, ...] | None = None
    ) -> None:
        self._clear_parent_link()
        self._deliver(value, provenance)

    def _deliver(self, value: Any, provenance: tuple[object, ...] | None) -> None:
        if isinstance(self.drip, _OverrideDrip):
            self.drip.publish(value, provenance)
        else:
            self.drip.next(value)

    def sync_parent(
        self,
        parent_drip: Drip[object] | None,
        provenance: tuple[object, ...] | None = None,
    ) -> None:
        self._provenance = provenance
        parent_provenance = (
            parent_drip._published_provenance
            if isinstance(parent_drip, _OverrideDrip)
            else None
        )
        effective_provenance = (
            provenance + parent_provenance
            if provenance is not None and parent_provenance is not None
            else None
        )
        if parent_drip is None:
            self._clear_parent_link()
            self.drip.next(APP_CONTEXT_MISSING)
            return
        if self.parent_drip is parent_drip and self.unsubscribe_parent is not None:
            self._deliver(parent_drip.get(), effective_provenance)
            return

        self._clear_parent_link()
        self.parent_drip = parent_drip
        self._deliver(parent_drip.get(), effective_provenance)

        if isinstance(self.drip, _OverrideDrip):
            target = weakref.ref(self)
            initialized = False

            def on_parent_change(next_value: object | None) -> None:
                nonlocal initialized
                # sync_parent delivered this initial snapshot with provenance.
                # Replaying the subscribe-time emission would erase it.
                if not initialized:
                    initialized = True
                    return
                state = target()
                if state is not None:
                    source = state.parent_drip
                    parent_publication = (
                        source._publication
                        if isinstance(source, _OverrideDrip)
                        else None
                    )
                    state._deliver(
                        APP_CONTEXT_MISSING if next_value is None else next_value,
                        state._provenance + parent_publication
                        if state._provenance is not None and parent_publication is not None
                        else None,
                    )

        else:

            def on_parent_change(next_value: object | None) -> None:
                self.drip.next(
                    APP_CONTEXT_MISSING if next_value is None else next_value
                )

        self.unsubscribe_parent = parent_drip.subscribe_priority(on_parent_change)
        if isinstance(self.drip, _OverrideDrip):
            # The parent callback is weak: stream lifetime must not own the
            # render graph or leave a link behind when that graph is collected.
            self._parent_finalizer = weakref.finalize(self, self.unsubscribe_parent)

    def deactivate(self) -> None:
        self._clear_parent_link()

    def _clear_parent_link(self) -> None:
        finalizer, self._parent_finalizer = self._parent_finalizer, None
        if finalizer is not None:
            finalizer.detach()
        unsubscribe = self.unsubscribe_parent
        self.unsubscribe_parent = None
        self.parent_drip = None
        if unsubscribe is not None:
            unsubscribe()


@managed_context
class AppContextOverrideSlotContextStateMgr(RerunnableSlotContextStateMgr):
    _structure_error_cls: Any = const(init=False, default_factory=_structure_error)
    _declared_keys: tuple[Any, ...] = local_store(default=())
    _legacy_committed_values: tuple[Any, ...] = local_store(default=())
    _committed_key_states: dict[Any, _CommittedAppContextOverrideKeyState] = (
        local_store(default_factory=dict)
    )
    _committed_lookup: AppContextLookup = local_store(
        default_factory=_empty_authored_app_context_lookup
    )
    _pass_committed_values: tuple[Any, ...] = local_store(default=())
    _pass_committed_lookup: AppContextLookup = local_store(
        default_factory=_empty_authored_app_context_lookup
    )
    _pending_values: tuple[Any, ...] = local_store(default=())
    _pending_lookup: AppContextLookup = local_store(
        default_factory=_empty_authored_app_context_lookup
    )
    _pending_initialized: bool = local_store(default=False)
    _override: _OverrideSelection = managed(
        default_factory=_OverrideSelection,
        init=False,
        compare="identity",
        tx_key=PASS_TX_KEY,
    )
    _managed_lookup: AppContextLookup = const(
        init=False, default_factory=_override_lookup, allow_self_factory=True
    )

    def _override_completion(self) -> Any:
        completion = _field_only_completion(self)
        return (
            completion
            if getattr(completion, "override_selection_enabled", False)
            else None
        )

    @property
    def _committed_values(self) -> tuple[Any, ...]:
        if self._override_completion() is not None:
            return self.current._override.values
        return self._legacy_committed_values

    @_committed_values.setter
    def _committed_values(self, values: tuple[Any, ...]) -> None:
        self._legacy_committed_values = values

    def stage_override(self, keys: tuple[Any, ...], values: tuple[Any, ...]) -> None:
        completion = self._override_completion()
        if completion is not None:
            owner = completion.active
            try:
                completion.require_resource_owner()
                self._validate_override(keys, values)
                selection = self._override
                if selection.keys and selection.keys != keys:
                    completion.reject(
                        "app_context_override fixed keys cannot change at one slot"
                    )
                for key in keys:
                    if key not in self._committed_key_states:
                        self._committed_key_states[key] = (
                            _CommittedAppContextOverrideKeyState(
                                key, _OverrideDrip(self, key)
                            )
                        )
                completion.require_resource_owner()
                assert owner is not None
                self._override = _OverrideSelection(keys, values, owner.read_token)
            except BaseException as error:
                if owner is not None:
                    owner.fail(error)
                raise
            return
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
        if self._override_completion() is not None:
            return self._managed_lookup
        if self.is_scope_active() and self._pending_initialized:
            return self._pending_lookup
        if self._declared_keys:
            return self._committed_lookup
        return self._parent_state_mgr.effective_authored_app_context_lookup()

    def begin_scope_pass(self) -> None:
        if self._override_completion() is not None:
            super().begin_pass()
            return
        self._pass_committed_values = self._committed_values
        self._pass_committed_lookup = self._committed_lookup
        super().begin_pass()

    def commit_scope_pass(self) -> None:
        if self._override_completion() is not None:
            super().end_pass()
            return
        if not self._pending_initialized:
            raise RuntimeError("app_context_override slot was not staged")
        self._committed_values = self._pending_values
        self._committed_lookup = OverlayAppContextLookup(
            parent=self._parent_state_mgr.effective_authored_app_context_lookup(),
            drips={
                key: self._committed_key_states[key].drip for key in self._declared_keys
            },
        )
        super().end_pass()
        self._pending_values = ()
        self._pending_lookup = EMPTY_APP_CONTEXT_LOOKUP
        self._pending_initialized = False
        self._pass_committed_values = ()
        self._pass_committed_lookup = EMPTY_APP_CONTEXT_LOOKUP

    def rollback_scope_pass(self) -> None:
        if self._override_completion() is not None:
            super().rollback_pass()
            return
        super().rollback_pass()
        self._committed_values = self._pass_committed_values
        self._committed_lookup = self._pass_committed_lookup
        if self._declared_keys and len(self._pass_committed_values) == len(
            self._declared_keys
        ):
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
        completion = self._override_completion()
        if completion is not None:
            completion.require_resource_owner()
            self._override = _OverrideSelection()
            self.children_state = {}
            children = dict(self._parent_state_mgr.children_state)
            if children.get(self._slot_id) is self:
                children.pop(self._slot_id)
                self._parent_state_mgr.children_state = children
            return
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
            raise self._structure_error_cls(
                "app_context_override requires at least one key"
            )
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
