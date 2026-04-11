from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import Any, Callable, TYPE_CHECKING, TypeVar

from pyrolyze.api import MountDirective, UIElement
from pyrolyze.freezable import freezable_dataclass, frozen_dataclass
from pyrolyze.lifecycle import const, managed, managed_context, transient
from pyrolyze.runtime.app_context import APP_CONTEXT_MISSING, EMPTY_APP_CONTEXT_LOOKUP
from pyrolyze.runtime.slot_kinds import ContextKind
from pyrolyze.runtime.slot_call_semantics import ExternalStoreRef
from pyrolyze.runtime.slot_expr import SlotExpr
from ._base import StateMgrBase, USE_OWNER
from ._support import (
    PendingEventHandlerBinding,
    REFRACTOR_CLASSES,
    SlotOwnershipError,
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
    from pyrolyze.runtime.context_bare_refactor_lcm import RenderContext, SlotContext
    from pyrolyze.runtime.slot_identity import SlotId


PASS_TX_GROUP = "context_pass"
UiNode = UIElement | MountDirective


def _default_generation_tracker_key(self: ContextBaseStateMgr) -> Any:
    return type(self.owner)._generation_tracker_key_const


def _default_context_kind(self: ContextBaseStateMgr) -> ContextKind:
    return getattr(type(self.owner), "_context_kind", ContextKind.SLOT)


def _default_pass_scope_handle_cls(self: ContextBaseStateMgr) -> Any:
    return type(self.owner)._pass_scope_handle_cls


def _default_owner_type_name(self: ContextBaseStateMgr) -> str:
    return type(self.owner).__name__


def _default_render_context_state_mgr(self: ContextBaseStateMgr) -> Any | None:
    if self._render_context_state_mgr_seed is not None:
        return self._render_context_state_mgr_seed
    render_context = self._render_context_seed
    if render_context is not None and hasattr(render_context, "_state_mgr"):
        return render_context._state_mgr
    return None


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
    # Field-semantics target only.
    # Keep this as the published subtree state unit while the methods below are
    # still in legacy imperative form. The later rewrite should move commit and
    # rollback to snapshot replacement rather than field-by-field mutation.


@frozen_dataclass(mutable_type=ContextSubtreeState)
class FrozenContextSubtreeState:
    pass


@dataclass(slots=True)
class ContextStagedState:
    ui: list[UiNode] = field(default_factory=list)
    ui_entries: list[UiSnapshotEntry] = field(default_factory=list)


@managed_context
class ContextBaseStateMgr(StateMgrBase):
    # Constructor-only seeds for values that cannot yet be derived from owner at
    # initialization time. The semantic fields below should depend on these, not
    # on constructor plumbing.
    _render_context_state_mgr_seed: Any | None = const(default=None)
    _render_context_seed: Any | None = const(default=None)

    _generation_tracker_key: AppContextKey[GenerationTracker] = const(
        default_factory=_default_generation_tracker_key
    )
    _context_kind: ContextKind = const(default_factory=_default_context_kind)
    _pass_scope_handle_cls: Any = const(default_factory=_default_pass_scope_handle_cls)
    _owner_type_name: str = const(default_factory=_default_owner_type_name)
    _render_context_state_mgr: Any | None = const(default_factory=_default_render_context_state_mgr)

    _subtree: FrozenContextSubtreeState = managed(default=FrozenContextSubtreeState())
    _scope_active: bool = transient(default=False, tx_group=PASS_TX_GROUP)
    _pass_child_order: tuple[Any, ...] = transient(default=(), tx_group=PASS_TX_GROUP)
    _pass_child_dirty: dict[Any, bool] = transient(default_factory=dict, tx_group=PASS_TX_GROUP)
    _pass_committed_ui: tuple[Any, ...] = transient(default=(), tx_group=PASS_TX_GROUP)
    _pass_own_committed_ui: tuple[Any, ...] = transient(default=(), tx_group=PASS_TX_GROUP)
    _pass_own_committed_ui_entries: tuple[Any, ...] = transient(default=(), tx_group=PASS_TX_GROUP)
    _staged_state: ContextStagedState | None = transient(
        default=None,
        working_default_factory=ContextStagedState,
        tx_group=PASS_TX_GROUP,
    )
    _pass_committed_native_root: bool = transient(default=False, tx_group=PASS_TX_GROUP)

    # Integration note:
    # The field declarations above are the lifecycle target semantics.
    # The methods below are still the legacy imperative implementation and do
    # not yet respect these state units. That mismatch is intentional in this
    # step: lock the field model first, then rewrite the methods against it.

    def root_context_state_mgr(self) -> Any:
        if self._render_context_state_mgr is None:
            return self
        return self._render_context_state_mgr

    def children_by_slot_id(self) -> dict[Any, Any]:
        return self._children

    def iter_children(self) -> tuple[Any, ...]:
        return tuple(child_state_mgr.owner for child_state_mgr in self._children.values())

    def committed_ui(self) -> tuple[Any, ...]:
        return self._committed_ui

    def own_committed_ui(self) -> tuple[Any, ...]:
        return self._own_committed_ui

    def own_committed_ui_entries(self) -> tuple[Any, ...]:
        return self._own_committed_ui_entries

    def parent_context(self) -> Any | None:
        parent_state_mgr = getattr(self, "_parent_state_mgr", None)
        return None if parent_state_mgr is None else parent_state_mgr.owner

    def get_app_context(self, key: Any) -> Any:
        root_context_state_mgr = self.root_context_state_mgr()._scheduler_root_state_mgr
        return root_context_state_mgr._app_context_store.get(key)

    def has_app_context(self, key: Any) -> bool:
        root_context_state_mgr = self.root_context_state_mgr()._scheduler_root_state_mgr
        return root_context_state_mgr._app_context_store.has(key)

    def get_authored_app_context(self, key: Any) -> Any:
        return self.effective_authored_app_context_lookup().get(key)

    def has_authored_app_context(self, key: Any) -> bool:
        return self.effective_authored_app_context_lookup().has(key)

    def authored_app_context_ref(self, key: Any) -> Any:
        lookup = self.effective_authored_app_context_lookup()
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

        def get() -> Any:
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

    def current_slot_id(self) -> Any:
        if self.context_kind() in {ContextKind.RENDER_ROOT, ContextKind.COMPONENT_RENDER}:
            return None
        return self._slot_id

    def context_kind(self) -> ContextKind:
        return self._context_kind

    def pass_scope(self) -> Any:
        return self._pass_scope_handle_cls(context=self, activate=not self._scope_active)

    def require_active_scope(self) -> None:
        if not self._scope_active:
            raise RuntimeError("scope is not active")

    def is_scope_active(self) -> bool:
        return self._scope_active

    def register_child(self, slot_id: Any, child: Any) -> None:
        self._children[slot_id] = child._state_mgr

    def register_child_state_mgr(self, slot_id: Any, child_state_mgr: Any) -> None:
        self._children[slot_id] = child_state_mgr

    def staged_ui_len(self) -> int:
        staged_ui = self._staged_ui
        return 0 if staged_ui is None else len(staged_ui)

    def begin_pass(self) -> None:
        if self._scope_active:
            raise RuntimeError("scope already active")
        self._transaction_manager.begin(PASS_TX_GROUP)
        self._scope_active = True
        self._pass_child_order = tuple(self._children.keys())
        self._pass_child_dirty = {
            slot_id: child_state_mgr._invoke_dirty for slot_id, child_state_mgr in self._children.items()
        }
        self._pass_committed_ui = self._committed_ui
        self._pass_own_committed_ui = self._own_committed_ui
        self._pass_own_committed_ui_entries = self._own_committed_ui_entries
        if hasattr(self, "_committed_native_root"):
            self._pass_committed_native_root = self._committed_native_root
        self._staged_ui = []
        self._staged_ui_entries = []
        for child_state_mgr in self._children.values():
            child_state_mgr._seen_in_pass = False

    def end_pass(self) -> None:
        if not self._scope_active:
            raise RuntimeError("scope is not active")
        try:
            unseen_slots = [
                slot_id
                for slot_id, child_state_mgr in self._children.items()
                if not child_state_mgr._seen_in_pass
            ]
            for slot_id in unseen_slots:
                child_state_mgr = self._children.get(slot_id)
                if child_state_mgr is not None:
                    child_state_mgr.deactivate()

            for child_state_mgr in self._children.values():
                child_type = type(child_state_mgr.owner).__name__
                if child_type in {"SlotCallSlotContext", "SlotExprSlotContext"}:
                    child_state_mgr.commit_binding()
                elif child_type == "EventHandlerSlotContext":
                    child_state_mgr.commit_handler()
                elif child_type == "ComponentCallSlotContext":
                    child_state_mgr.commit_owned_event_handlers()

            staged_ui_entries = self._staged_ui_entries
            if staged_ui_entries is None:
                staged_ui_entries = []
            self._own_committed_ui_entries = tuple(staged_ui_entries)
            self._own_committed_ui = tuple(entry.element for entry in self._own_committed_ui_entries)
            self._committed_ui = self.build_committed_ui()
            if hasattr(self, "_committed_native_root") and hasattr(self, "_expects_native_root"):
                self._committed_native_root = self._expects_native_root

            for child_state_mgr in self._children.values():
                child_state_mgr._invoke_dirty = False

            self._scope_active = False
            self._pass_child_order = ()
            self._pass_child_dirty = {}
            self._pass_committed_ui = ()
            self._pass_own_committed_ui = ()
            self._pass_own_committed_ui_entries = ()
            self._staged_ui = []
            self._staged_ui_entries = []
            self._transaction_manager.commit(PASS_TX_GROUP)
        except BaseException:
            self._transaction_manager.rollback(PASS_TX_GROUP)
            raise

    def rollback_pass(self) -> None:
        if not self._scope_active:
            raise RuntimeError("scope is not active")
        try:
            committed_ids = set(self._pass_child_order)
            for slot_id, child_state_mgr in list(self._children.items()):
                if slot_id not in committed_ids:
                    child_state_mgr.deactivate()
                    continue
                child_type = type(child_state_mgr.owner).__name__
                if child_type in {"SlotCallSlotContext", "SlotExprSlotContext"}:
                    child_state_mgr.rollback_binding()
                elif child_type == "EventHandlerSlotContext":
                    child_state_mgr.rollback_handler()
                elif child_type == "ComponentCallSlotContext":
                    child_state_mgr.rollback_owned_event_handlers()
                child_state_mgr._invoke_dirty = self._pass_child_dirty.get(
                    slot_id,
                    child_state_mgr._invoke_dirty,
                )
                child_state_mgr._seen_in_pass = True

            restored_children: dict[Any, Any] = {}
            for slot_id in self._pass_child_order:
                child_state_mgr = self._children.get(slot_id)
                if child_state_mgr is not None:
                    restored_children[slot_id] = child_state_mgr
            self._children = restored_children
            self._committed_ui = self._pass_committed_ui
            self._own_committed_ui = self._pass_own_committed_ui
            self._own_committed_ui_entries = self._pass_own_committed_ui_entries
            if hasattr(self, "_committed_native_root"):
                self._committed_native_root = self._pass_committed_native_root

            self._scope_active = False
            self._pass_child_order = ()
            self._pass_child_dirty = {}
            self._pass_committed_ui = ()
            self._pass_own_committed_ui = ()
            self._pass_own_committed_ui_entries = ()
            self._staged_ui = []
            self._staged_ui_entries = []
        finally:
            self._transaction_manager.rollback(PASS_TX_GROUP)

    def runtime_key_path(self) -> tuple[Any, ...]:
        owner_kind = self.context_kind()
        if owner_kind is ContextKind.RENDER_ROOT:
            return ()
        if owner_kind is ContextKind.COMPONENT_RENDER:
            return self._owner_slot_state_mgr.current_slot_id().key_path
        return self.current_slot_id().key_path

    def resolve_slot_id(self, slot_id: Any) -> Any:
        runtime_key_path = self.runtime_key_path()
        return type(slot_id)(
            module_id=slot_id.module_id,
            slot_index=slot_id.slot_index,
            key_path=runtime_key_path + slot_id.key_path,
            line_no=slot_id.line_no,
            is_top_level=slot_id.is_top_level,
        )

    def ensure_slot(
        self,
        slot_id: Any,
        slot_type: type[T],
        *,
        parent_facade: Any = USE_OWNER,
    ) -> T:
        return self.ensure_resolved_slot(self.resolve_slot_id(slot_id), slot_type, parent_facade=parent_facade)

    def ensure_resolved_slot(
        self,
        slot_id: Any,
        slot_type: type[T],
        *,
        parent_facade: Any = USE_OWNER,
    ) -> T:
        parent_facade = self._resolve_owner_arg(parent_facade)
        resolved_slot_id = slot_id
        root_context_state_mgr = self.root_context_state_mgr()
        root_context = root_context_state_mgr.owner
        existing = root_context_state_mgr.get_registered_slot(resolved_slot_id)
        if existing is not None and existing._state_mgr._parent_state_mgr is not self:
            raise SlotOwnershipError(
                f"slot {resolved_slot_id!r} is owned by {type(existing._state_mgr._parent_state_mgr.owner).__name__}, "
                f"not {self._owner_type_name}"
            )
        if existing is not None and not isinstance(existing, slot_type):
            existing.deactivate()
            existing = None
        if existing is None:
            slot = slot_type(render_context=root_context, parent=parent_facade, slot_id=resolved_slot_id)
            existing = slot
        self._children.pop(resolved_slot_id, None)
        self._children[resolved_slot_id] = existing._state_mgr
        existing._state_mgr._seen_in_pass = True
        return existing

    def materialize_pending_event_handler(
        self,
        binding: PendingEventHandlerBinding,
        *,
        parent_facade: Any = USE_OWNER,
    ) -> Callable[..., None]:
        event_handler_slot_context_cls = REFRACTOR_CLASSES.event_handler_slot_context_cls
        if event_handler_slot_context_cls is None:
            raise RuntimeError("event handler slot context class is not configured")
        slot = self.ensure_resolved_slot(
            binding.slot_id,
            event_handler_slot_context_cls,
            parent_facade=parent_facade,
        )
        return slot.stage_callback(callback=binding.callback, dirty=binding.dirty)

    def build_committed_ui(self) -> tuple[Any, ...]:
        own_elements = self._own_committed_ui
        child_elements = tuple(
            element
            for child_state_mgr in self._children.values()
            for element in child_state_mgr.committed_ui()
        )
        if hasattr(self, "_expects_native_root") and (
            self._expects_native_root or self._committed_native_root
        ):
            if len(own_elements) != 1:
                raise RuntimeError("native container helpers must emit exactly one root UIElement")
            root = own_elements[0]
            if child_elements:
                root = UIElement(
                    kind=root.kind,
                    props=root.props,
                    children=child_elements,
                    call_site_id=root.call_site_id,
                    slot_id=root.slot_id,
                )
            return (root,)
        if own_elements:
            return own_elements + child_elements
        return child_elements

    def refresh_committed_ui_from_children(self) -> None:
        self._committed_ui = self.build_committed_ui()
        parent_state_mgr = getattr(self, "_parent_state_mgr", None)
        if parent_state_mgr is not None:
            parent_state_mgr.refresh_committed_ui_from_children()

    def effective_authored_app_context_lookup(self) -> Any:
        if self.context_kind() in {
            ContextKind.RENDER_ROOT,
            ContextKind.COMPONENT_RENDER,
        }:
            return self._authored_app_context_lookup
        parent_state_mgr = getattr(self, "_parent_state_mgr", None)
        if parent_state_mgr is not None:
            return parent_state_mgr.effective_authored_app_context_lookup()
        return EMPTY_APP_CONTEXT_LOOKUP

    def slot_expr(
        self,
        slot_id: Any,
        value_lambda: Callable[..., Any],
        dirty_lambda: Callable[..., Any],
        *,
        slot_context_facade: Any = USE_OWNER,
    ) -> Any:
        slot_context_facade = self._resolve_owner_arg(slot_context_facade)
        self.require_active_scope()
        slot_expr_slot_context_cls = REFRACTOR_CLASSES.slot_expr_slot_context_cls
        if slot_expr_slot_context_cls is None:
            raise RuntimeError("slot expr slot context class is not configured")
        expr_slot = self.ensure_slot(slot_id, slot_expr_slot_context_cls, parent_facade=slot_context_facade)
        return (
            SlotExpr(value_lambda, dirty_lambda)
            .apply_slot_context(slot_context_facade)
            .apply_host_factory(
                lambda call_site_slot_id: _ContextSlotExprHost(
                    expr_slot._state_mgr,
                    expr_slot._resolve_slot_id(call_site_slot_id),
                )
            )
            .apply_call_site_context_manager(expr_slot.call_site_context_manager)
            .apply_runtime_locals_provider(expr_slot.runtime_locals)
            .apply_committed_ui_sync(expr_slot.sync_committed_ui)
            .apply_lifecycle_slot_context(expr_slot)
        )

    def visit_slot_and_dirty(self, slot_id: Any, *, parent_facade: Any = USE_OWNER) -> bool:
        self.require_active_scope()
        slot_context_cls = REFRACTOR_CLASSES.slot_context_cls
        if slot_context_cls is None:
            raise RuntimeError("slot context class is not configured")
        slot = self.ensure_slot(slot_id, slot_context_cls, parent_facade=parent_facade)
        return slot.invoke_dirty

    def keyed_loop(
        self,
        slot_id: Any,
        values: list[T],
        *,
        key_fn: Callable[[T], Any],
        parent_facade: Any = USE_OWNER,
    ) -> Any:
        self.require_active_scope()
        keyed_loop_slot_context_cls = REFRACTOR_CLASSES.keyed_loop_slot_context_cls
        if keyed_loop_slot_context_cls is None:
            raise RuntimeError("keyed loop slot context class is not configured")
        loop_slot = self.ensure_slot(slot_id, keyed_loop_slot_context_cls, parent_facade=parent_facade)
        raw_values, _ = _unwrap(values)
        return _KeyedLoopIterable(
            owner_state_mgr=loop_slot._state_mgr,
            parent_facade=loop_slot,
            values=tuple(raw_values),
            key_fn=key_fn,
        )

    def container_call(
        self,
        slot_id: Any,
        container_fn: Callable[..., Any],
        *args: Any,
        parent_facade: Any = USE_OWNER,
        dirty_state: Any = None,
        _pyr_param_names: tuple[str, ...] | None = None,
        _pyr_args_dirty: tuple[Any, ...] | None = None,
        _pyr_kwargs_dirty: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        self.require_active_scope()
        container_slot_context_cls = REFRACTOR_CLASSES.container_slot_context_cls
        directive_slot_context_cls = REFRACTOR_CLASSES.directive_slot_context_cls
        if container_slot_context_cls is None or directive_slot_context_cls is None:
            raise RuntimeError("container/directive slot context classes are not configured")
        slot = self.ensure_slot(slot_id, container_slot_context_cls, parent_facade=parent_facade)
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
            directive_slot = self.ensure_slot(slot_id, directive_slot_context_cls, parent_facade=parent_facade)
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
        parent_facade: Any = USE_OWNER,
        **kwargs: Any,
    ) -> Any:
        self.require_active_scope()
        directive_slot_context_cls = REFRACTOR_CLASSES.directive_slot_context_cls
        if directive_slot_context_cls is None:
            raise RuntimeError("directive slot context class is not configured")
        slot = self.ensure_slot(slot_id, directive_slot_context_cls, parent_facade=parent_facade)
        return _DirectiveCallHandle(slot=slot, directive_fn=directive_fn, args=args, kwargs=kwargs)

    def open_app_context_override(
        self,
        slot_id: Any,
        keys: tuple[Any, ...],
        *values: Any,
        parent_facade: Any = USE_OWNER,
    ) -> Any:
        self.require_active_scope()
        app_context_override_slot_context_cls = REFRACTOR_CLASSES.app_context_override_slot_context_cls
        if app_context_override_slot_context_cls is None:
            raise RuntimeError("app-context override slot context class is not configured")
        slot = self.ensure_slot(slot_id, app_context_override_slot_context_cls, parent_facade=parent_facade)
        return _AppContextOverrideHandle(slot=slot, keys=keys, values=values)

    def component_call(
        self,
        slot_id: Any,
        component: Callable[..., Any],
        *args: Any,
        parent_facade: Any = USE_OWNER,
        dirty_state: Any = None,
        _pyr_param_names: tuple[str, ...] | None = None,
        _pyr_args_dirty: tuple[Any, ...] | None = None,
        _pyr_kwargs_dirty: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        self.require_active_scope()
        component_call_slot_context_cls = REFRACTOR_CLASSES.component_call_slot_context_cls
        if component_call_slot_context_cls is None:
            raise RuntimeError("component call slot context class is not configured")
        slot = self.ensure_slot(slot_id, component_call_slot_context_cls, parent_facade=parent_facade)
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

    def event_handler(
        self,
        slot_id: Any,
        *,
        dirty: bool,
        callback: Callable[..., Any],
        parent_facade: Any = USE_OWNER,
    ) -> Any:
        self.require_active_scope()
        event_handler_slot_context_cls = REFRACTOR_CLASSES.event_handler_slot_context_cls
        if event_handler_slot_context_cls is None:
            raise RuntimeError("event handler slot context class is not configured")
        slot = self.ensure_slot(slot_id, event_handler_slot_context_cls, parent_facade=parent_facade)
        return slot.stage_callback(callback=callback, dirty=dirty)

    def event_handler_binding(self, slot_id: Any, *, dirty: bool, callback: Callable[..., Any]) -> Any:
        self.require_active_scope()
        return PendingEventHandlerBinding(
            slot_id=self.resolve_slot_id(slot_id),
            dirty=dirty,
            callback=callback,
        )

    def call_native(self, factory: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        self.require_active_scope()
        raw_args = tuple(_unwrap_native_value(arg) for arg in args)
        raw_kwargs = {key: _unwrap_native_value(value) for key, value in kwargs.items()}
        call_site_id = raw_kwargs.pop("__pyr_call_site_id", None)
        context_facade = raw_kwargs.pop("__pyr_context_facade")
        result = factory(*raw_args, **raw_kwargs)
        if result is None:
            return None
        if isinstance(result, UIElement):
            source_slot_id = _native_emission_slot_identity(context_facade)
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
            self._staged_ui.append(result)
            self._staged_ui_entries.append(
                _CommittedUiEntry(
                    generation_id=self.current_generation_id(),
                    element=result,
                )
            )
            return None
        if os.environ.get("PYROLYZE_ENV") == "prod":
            return None
        raise TypeError("call_native factory must return UIElement or None")
