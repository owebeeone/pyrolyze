from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from pyrolyze.api import MountDirective, UIElement
from pyrolyze.freezable import freezable_dataclass, frozen_dataclass
from pyrolyze.lifecycle import const, local_store, managed, managed_context, transient
from pyrolyze.runtime.app_context import APP_CONTEXT_MISSING
from pyrolyze.runtime.slot_kinds import ContextKind
from pyrolyze.runtime.slot_call_semantics import ExternalStoreRef
from pyrolyze.runtime.slot_expr import SlotExpr
from ._base import StateMgrBase
from ._support import (
    PendingEventHandlerBinding,
    REFRACTOR_CLASSES,
    _AppContextOverrideHandle,
    _CommittedUiEntry,
    _ContainerCallHandle,
    _ContextSlotExprHost,
    _DirectiveCallHandle,
    _KeyedLoopIterable,
    _MountContainerCallHandle,
    _NativeContainerCallHandle,
    _PyrolyzeContainerCallHandle,
    _clean_dirty_state,
    _component_call_key,
    _container_runtime_context_param_name,
    _native_context_param_name,
    _native_emission_slot_identity,
    _resolve_runtime_component_func,
    _resolve_runtime_site_call,
    _unwrap,
    _unwrap_native_value,
)


T = TypeVar("T")

if TYPE_CHECKING:
    from pyrolyze.runtime.app_context import AppContextKey, GenerationTracker
    from pyrolyze.runtime.context_bare_refactor_lcm import ContextBase, RenderContext, SlotContext
    from pyrolyze.runtime.slot_identity import SlotId


UiNode = UIElement | MountDirective
PASS_TX_GROUP = "context_pass"


@dataclass(frozen=True, slots=True)
class UiSnapshotEntry:
    generation_id: int
    element: UiNode


@freezable_dataclass(frozen_type="FrozenContextSubtreeState")
class ContextSubtreeState:
    children: list[tuple["SlotId", "SlotContext"]] = field(default_factory=list)
    own_ui: list[UiNode] = field(default_factory=list)
    own_ui_entries: list[UiSnapshotEntry] = field(default_factory=list)
    ui: list[UiNode] = field(default_factory=list)
    # Integration note:
    # Keep this record as a declarative snapshot container first.
    # The current plan is to move ContextBaseStateMgr toward:
    # - one managed frozen subtree snapshot
    # - transient pass/rollback/staged records
    # - direct lifecycle assignment / snapshot restore
    #
    # That means the speculative member helpers that merely set fields or
    # reconstruct pre-pass state are probably unnecessary. In the lifecycle
    # version, rollback should prefer restoring a prior frozen subtree value
    # rather than rebuilding pieces of state in place.
    #
    # If richer methods survive later, they should represent real subtree
    # invariants, not thin wrappers over simple assignment.
    #
    # Candidate helpers intentionally not added yet:
    # - replace_children(...)
    # - restore_children(...)
    # - apply_own_ui_entries(...)
    # - replace_ui(...)


@frozen_dataclass(mutable_type=ContextSubtreeState)
class FrozenContextSubtreeState:
    pass


@dataclass(slots=True)
class ContextPassControl:
    scope_active: bool = False
    literal_index: int = 0


@dataclass(slots=True)
class ContextRollbackState:
    child_order: tuple["SlotId", ...] = ()
    child_dirty: dict["SlotId", bool] = field(default_factory=dict)
    prior_subtree: FrozenContextSubtreeState | None = None
    prior_committed_native_root: bool | None = None


@dataclass(slots=True)
class ContextStagedState:
    ui: list[UiNode] = field(default_factory=list)
    ui_entries: list[UiSnapshotEntry] = field(default_factory=list)


@dataclass(slots=True)
class ContextLocalCache:
    literal_initialized: list[bool] = field(default_factory=list)


@managed_context
class ContextBaseStateMgr(StateMgrBase):
    # These field declarations are the lifecycle target semantics for the
    # context base state manager.
    #
    # Important:
    # The methods below are still the legacy behavior scaffold and still talk
    # in terms of owner._children / owner._committed_ui / owner._scope_active.
    # We are intentionally not resolving that behavioral mismatch in this step.
    # This change is only to move the state classification into actual
    # lifecycle/freezable declarations so the intended field semantics are
    # visible in the file.
    _generation_tracker_key: AppContextKey[GenerationTracker] = const()
    _render_context: RenderContext = const()
    _subtree: FrozenContextSubtreeState = managed(default=FrozenContextSubtreeState())
    _pass_control: ContextPassControl | None = transient(
        default=None,
        working_default_factory=ContextPassControl,
        tx_group=PASS_TX_GROUP,
    )
    _rollback_state: ContextRollbackState | None = transient(
        default=None,
        working_default_factory=ContextRollbackState,
        tx_group=PASS_TX_GROUP,
    )
    _staged_state: ContextStagedState | None = transient(
        default=None,
        working_default_factory=ContextStagedState,
        tx_group=PASS_TX_GROUP,
    )
    _local_cache: ContextLocalCache = local_store(default_factory=ContextLocalCache)

    def __init__(self, owner: ContextBase) -> None:
        super().__init__(owner)
        self._generation_tracker_key = owner._generation_tracker_key_const
        self._render_context = owner.render_context

    def root_context(self) -> RenderContext:
        return self._render_context

    def get_app_context(self, key: AppContextKey[T]) -> T:
        return self.owner.root_context._scheduler_root._app_context_store.get(key)

    def has_app_context(self, key: AppContextKey[object]) -> bool:
        return self.owner.root_context._scheduler_root._app_context_store.has(key)

    def get_authored_app_context(self, key: AppContextKey[T]) -> T:
        return self.owner._effective_authored_app_context_lookup().get(key)

    def has_authored_app_context(self, key: AppContextKey[object]) -> bool:
        return self.owner._effective_authored_app_context_lookup().has(key)

    def authored_app_context_ref(self, key: AppContextKey[T]) -> ExternalStoreRef[T]:
        lookup = self.owner._effective_authored_app_context_lookup()
        drip = lookup.resolve_drip(key)
        if drip is None or drip.get() is APP_CONTEXT_MISSING:
            raise LookupError(f"no authored app context for key {key.debug_name!r}")

        def subscribe(listener: Callable[[], None]) -> Callable[[], None]:
            initialized = False

            def on_change(_value: object | None) -> None:
                nonlocal initialized
                if not initialized:
                    initialized = True
                    return
                listener()

            return drip.subscribe_priority(on_change)

        def get() -> T:
            current = drip.get()
            if current is APP_CONTEXT_MISSING:
                raise LookupError(f"no authored app context for key {key.debug_name!r}")
            return current

        return ExternalStoreRef(
            identity=drip,
            subscribe=subscribe,
            get=get,
        )

    def current_generation_id(self) -> int:
        tracker = self.get_app_context(self._generation_tracker_key)
        return tracker.current()

    def current_slot_id(self) -> SlotId | None:
        return getattr(self.owner, "slot_id", None)

    def context_kind(self) -> ContextKind:
        return self.owner.get_kind()

    def pass_scope(self) -> Any:
        return self.owner._pass_scope_handle_cls(context=self.owner, activate=not self.owner._scope_active)

    def begin_pass(self) -> None:
        owner = self.owner
        if owner._scope_active:
            raise RuntimeError("scope already active")
        owner._scope_active = True
        owner._literal_index = 0
        owner._pass_child_order = tuple(owner._children.keys())
        owner._pass_child_dirty = {
            slot_id: child.invoke_dirty for slot_id, child in owner._children.items()
        }
        owner._pass_committed_ui = owner._committed_ui
        owner._pass_own_committed_ui = owner._own_committed_ui
        owner._pass_own_committed_ui_entries = owner._own_committed_ui_entries
        if type(owner).__name__ == "ContainerSlotContext":
            owner._pass_committed_native_root = owner.committed_native_root
        owner._staged_ui = []
        owner._staged_ui_entries = []
        for child in owner._children.values():
            child.seen_in_pass = False

    def end_pass(self) -> None:
        owner = self.owner
        if not owner._scope_active:
            raise RuntimeError("scope is not active")
        unseen_slots = [slot_id for slot_id, child in owner._children.items() if not child.seen_in_pass]
        for slot_id in unseen_slots:
            child = owner._children.get(slot_id)
            if child is not None:
                child.deactivate()

        for child in owner._children.values():
            child_type = type(child).__name__
            if child_type in {"SlotCallSlotContext", "SlotExprSlotContext"}:
                child.commit_binding()
            elif child_type == "EventHandlerSlotContext":
                child.commit_handler()
            elif child_type == "ComponentCallSlotContext":
                child.commit_owned_event_handlers()

        owner._own_committed_ui_entries = tuple(owner._staged_ui_entries)
        owner._own_committed_ui = tuple(entry.element for entry in owner._own_committed_ui_entries)
        owner._committed_ui = owner._build_committed_ui()
        if type(owner).__name__ == "ContainerSlotContext":
            owner.committed_native_root = owner.expects_native_root

        for child in owner._children.values():
            child.invoke_dirty = False

        owner._scope_active = False
        owner._pass_child_order = ()
        owner._pass_child_dirty = {}
        owner._pass_committed_ui = ()
        owner._pass_own_committed_ui = ()
        owner._pass_own_committed_ui_entries = ()
        owner._staged_ui = []
        owner._staged_ui_entries = []

    def rollback_pass(self) -> None:
        owner = self.owner
        if not owner._scope_active:
            raise RuntimeError("scope is not active")
        committed_ids = set(owner._pass_child_order)
        for slot_id, child in list(owner._children.items()):
            if slot_id not in committed_ids:
                child.deactivate()
                continue
            child_type = type(child).__name__
            if child_type in {"SlotCallSlotContext", "SlotExprSlotContext"}:
                child.rollback_binding()
            elif child_type == "EventHandlerSlotContext":
                child.rollback_handler()
            elif child_type == "ComponentCallSlotContext":
                child.rollback_owned_event_handlers()
            child.invoke_dirty = owner._pass_child_dirty.get(slot_id, child.invoke_dirty)
            child.seen_in_pass = True

        restored_children: dict[SlotId, SlotContext] = {}
        for slot_id in owner._pass_child_order:
            child = owner._children.get(slot_id)
            if child is not None:
                restored_children[slot_id] = child
        owner._children = restored_children
        owner._committed_ui = owner._pass_committed_ui
        owner._own_committed_ui = owner._pass_own_committed_ui
        owner._own_committed_ui_entries = owner._pass_own_committed_ui_entries
        if type(owner).__name__ == "ContainerSlotContext":
            owner.committed_native_root = owner._pass_committed_native_root

        owner._scope_active = False
        owner._pass_child_order = ()
        owner._pass_child_dirty = {}
        owner._pass_committed_ui = ()
        owner._pass_own_committed_ui = ()
        owner._pass_own_committed_ui_entries = ()
        owner._staged_ui = []
        owner._staged_ui_entries = []

    def lit_dirty(self, value: Any) -> Any:
        _ = value
        owner = self.owner
        if not owner._scope_active:
            raise RuntimeError("scope is not active")
        literal_index = owner._literal_index
        owner._literal_index += 1
        if literal_index == len(owner._literal_initialized):
            owner._literal_initialized.append(True)
            return True
        return False

    def slot_expr(
        self,
        slot_id: Any,
        value_lambda: Callable[..., Any],
        dirty_lambda: Callable[..., Any],
    ) -> Any:
        self.owner._require_active_scope()
        slot_expr_slot_context_cls = REFRACTOR_CLASSES.slot_expr_slot_context_cls
        if slot_expr_slot_context_cls is None:
            raise RuntimeError("slot expr slot context class is not configured")
        expr_slot = self.owner._ensure_slot(slot_id, slot_expr_slot_context_cls)
        return (
            SlotExpr(value_lambda, dirty_lambda)
            .apply_slot_context(self.owner)
            .apply_host_factory(
                lambda call_site_slot_id: _ContextSlotExprHost(
                    expr_slot,
                    expr_slot._resolve_slot_id(call_site_slot_id),
                )
            )
            .apply_call_site_context_manager(expr_slot.call_site_context_manager)
            .apply_runtime_locals_provider(expr_slot.runtime_locals)
            .apply_committed_ui_sync(expr_slot.sync_committed_ui)
            .apply_lifecycle_slot_context(expr_slot)
        )

    def visit_slot_and_dirty(self, slot_id: Any) -> bool:
        self.owner._require_active_scope()
        slot_context_cls = REFRACTOR_CLASSES.slot_context_cls
        if slot_context_cls is None:
            raise RuntimeError("slot context class is not configured")
        slot = self.owner._ensure_slot(slot_id, slot_context_cls)
        return slot.invoke_dirty

    def keyed_loop(
        self,
        slot_id: Any,
        values: list[T],
        *,
        key_fn: Callable[[T], Any],
    ) -> Any:
        self.owner._require_active_scope()
        keyed_loop_slot_context_cls = REFRACTOR_CLASSES.keyed_loop_slot_context_cls
        if keyed_loop_slot_context_cls is None:
            raise RuntimeError("keyed loop slot context class is not configured")
        loop_slot = self.owner._ensure_slot(slot_id, keyed_loop_slot_context_cls)
        raw_values, _ = _unwrap(values)
        return _KeyedLoopIterable(owner=loop_slot, values=tuple(raw_values), key_fn=key_fn)

    def container_call(
        self,
        slot_id: Any,
        container_fn: Callable[..., Any],
        *args: Any,
        dirty_state: Any = None,
        _pyr_param_names: tuple[str, ...] | None = None,
        _pyr_args_dirty: tuple[Any, ...] | None = None,
        _pyr_kwargs_dirty: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        self.owner._require_active_scope()
        container_slot_context_cls = REFRACTOR_CLASSES.container_slot_context_cls
        directive_slot_context_cls = REFRACTOR_CLASSES.directive_slot_context_cls
        if container_slot_context_cls is None or directive_slot_context_cls is None:
            raise RuntimeError("container/directive slot context classes are not configured")
        slot = self.owner._ensure_slot(slot_id, container_slot_context_cls)
        raw_container_fn, raw_args, raw_kwargs, site_metadata = _resolve_runtime_site_call(
            slot,
            container_fn,
            args,
            kwargs,
        )
        slot.site_metadata = site_metadata
        if raw_container_fn is None:
            return None
        mount_context_param = _container_runtime_context_param_name(raw_container_fn)
        if mount_context_param is not None:
            directive_slot = self.owner._ensure_slot(slot_id, directive_slot_context_cls)
            return _MountContainerCallHandle(
                slot=directive_slot,
                container_fn=raw_container_fn,
                args=raw_args,
                kwargs=raw_kwargs,
                context_param=mount_context_param,
            )
        metadata, bound_receiver = _component_call_key(raw_container_fn)
        runtime_func = _resolve_runtime_component_func(getattr(metadata, "_func", None))
        if metadata is not None and runtime_func is not None:
            return _PyrolyzeContainerCallHandle(
                slot=slot,
                runtime_func=runtime_func,
                bound_receiver=bound_receiver,
                args=raw_args,
                kwargs=raw_kwargs,
                dirty_state=dirty_state or _clean_dirty_state(None),
                param_names=tuple(getattr(metadata, "param_names", ())),
                dynamic_param_names=_pyr_param_names,
                dynamic_args_dirty=_pyr_args_dirty,
                dynamic_kwargs_dirty=_pyr_kwargs_dirty,
                packed_kwargs=bool(getattr(metadata, "packed_kwargs", False)),
                packed_kwarg_param_names=tuple(getattr(metadata, "packed_kwarg_param_names", ())),
            )
        native_context_param = _native_context_param_name(raw_container_fn)
        if native_context_param is not None:
            return _NativeContainerCallHandle(
                slot=slot,
                container_fn=raw_container_fn,
                args=raw_args,
                kwargs=raw_kwargs,
                context_param=native_context_param,
            )
        return _ContainerCallHandle(
            slot=slot,
            container_fn=raw_container_fn,
            args=raw_args,
            kwargs=raw_kwargs,
        )

    def open_directive(
        self,
        slot_id: Any,
        directive_fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        self.owner._require_active_scope()
        directive_slot_context_cls = REFRACTOR_CLASSES.directive_slot_context_cls
        if directive_slot_context_cls is None:
            raise RuntimeError("directive slot context class is not configured")
        slot = self.owner._ensure_slot(slot_id, directive_slot_context_cls)
        return _DirectiveCallHandle(slot=slot, directive_fn=directive_fn, args=args, kwargs=kwargs)

    def open_app_context_override(self, slot_id: Any, keys: tuple[Any, ...], *values: Any) -> Any:
        self.owner._require_active_scope()
        app_context_override_slot_context_cls = REFRACTOR_CLASSES.app_context_override_slot_context_cls
        if app_context_override_slot_context_cls is None:
            raise RuntimeError("app-context override slot context class is not configured")
        slot = self.owner._ensure_slot(slot_id, app_context_override_slot_context_cls)
        return _AppContextOverrideHandle(slot=slot, keys=keys, values=values)

    def component_call(
        self,
        slot_id: Any,
        component: Callable[..., Any],
        *args: Any,
        dirty_state: Any = None,
        _pyr_param_names: tuple[str, ...] | None = None,
        _pyr_args_dirty: tuple[Any, ...] | None = None,
        _pyr_kwargs_dirty: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        self.owner._require_active_scope()
        component_call_slot_context_cls = REFRACTOR_CLASSES.component_call_slot_context_cls
        if component_call_slot_context_cls is None:
            raise RuntimeError("component call slot context class is not configured")
        slot = self.owner._ensure_slot(slot_id, component_call_slot_context_cls)
        raw_component, raw_args, raw_kwargs, site_metadata = _resolve_runtime_site_call(
            slot,
            component,
            args,
            kwargs,
        )
        slot.site_metadata = site_metadata
        if raw_component is None:
            return None
        unwrapped_component, _ = _unwrap(raw_component)
        metadata, _ = _component_call_key(unwrapped_component)
        runtime_func = _resolve_runtime_component_func(getattr(metadata, "_func", None))
        if metadata is None or runtime_func is None:
            raise TypeError("component_call expects a ComponentRef with _pyrolyze_meta._func")
        slot.invoke(
            raw_component,
            raw_args,
            raw_kwargs,
            dirty_state=dirty_state,
            _pyr_param_names=_pyr_param_names,
            _pyr_args_dirty=_pyr_args_dirty,
            _pyr_kwargs_dirty=_pyr_kwargs_dirty,
        )
        return None

    def event_handler(self, slot_id: Any, *, dirty: bool, callback: Callable[..., Any]) -> Any:
        self.owner._require_active_scope()
        event_handler_slot_context_cls = REFRACTOR_CLASSES.event_handler_slot_context_cls
        if event_handler_slot_context_cls is None:
            raise RuntimeError("event handler slot context class is not configured")
        slot = self.owner._ensure_slot(slot_id, event_handler_slot_context_cls)
        return slot.stage_callback(callback=callback, dirty=dirty)

    def event_handler_binding(self, slot_id: Any, *, dirty: bool, callback: Callable[..., Any]) -> Any:
        self.owner._require_active_scope()
        return PendingEventHandlerBinding(
            slot_id=self.owner._resolve_slot_id(slot_id),
            dirty=dirty,
            callback=callback,
        )

    def call_native(self, factory: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        self.owner._require_active_scope()
        raw_args = tuple(_unwrap_native_value(arg) for arg in args)
        raw_kwargs = {key: _unwrap_native_value(value) for key, value in kwargs.items()}
        call_site_id = raw_kwargs.pop("__pyr_call_site_id", None)
        result = factory(*raw_args, **raw_kwargs)
        if result is None:
            return None
        if isinstance(result, UIElement):
            source_slot_id = _native_emission_slot_identity(self.owner)
            normalized_call_site_id = result.call_site_id if call_site_id is None else call_site_id
            normalized_slot_id = result.slot_id if result.slot_id is not None else source_slot_id
            if result.call_site_id != normalized_call_site_id or result.slot_id != normalized_slot_id:
                result = UIElement(
                    kind=result.kind,
                    props=result.props,
                    children=result.children,
                    call_site_id=normalized_call_site_id,
                    slot_id=normalized_slot_id,
                )
            self.owner._staged_ui.append(result)
            self.owner._staged_ui_entries.append(
                _CommittedUiEntry(
                    generation_id=self.current_generation_id(),
                    element=result,
                )
            )
            return None
        if os.environ.get("PYROLYZE_ENV") == "prod":
            return None
        raise TypeError("call_native factory must return UIElement or None")
