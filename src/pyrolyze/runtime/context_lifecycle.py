"""Public lifecycle contexts; each object owns its managed state directly."""

from __future__ import annotations

__PYROLYZE_CONTEXT_IMPLEMENTATION__ = "lcm"

from typing import Any, Callable, TypeVar

from pyrolyze.api import (
    MountDirective,
    PyrolyzeMountAdvertisement,
    PyrolyzeMountAdvertisementRequest,
    SlotSelector,
    UIElement,
)

from .app_context import (
    EMPTY_APP_CONTEXT_LOOKUP,
    GENERATION_TRACKER_KEY,
    AppContextKey,
    AppContextLookup,
    AppContextStore,
)
from .call_site_context import CallSiteContextManager
from .context_state_lcm import _support
from .context_state_lcm import (
    AppContextOverrideSlotContextStateMgr,
    ComponentCallSlotContextStateMgr,
    ContainerSlotContextStateMgr,
    ContextBaseStateMgr,
    DirectiveSlotContextStateMgr,
    EventHandlerSlotContextStateMgr,
    KeyedLoopSlotContextStateMgr,
    LeafSlotContextStateMgr,
    LoopItemSlotContextStateMgr,
    RenderContextStateMgr,
    RerunnableSlotContextStateMgr,
    SlotCallSlotContextStateMgr,
    SlotContextStateMgr,
    SlotExprSlotContextStateMgr,
)
from .context_state_lcm.field_only_render import _require_fresh_render_root
from .context_state_lcm.pass_state_render import _PassStateRenderCompletion
from .pyro_call import RuntimeSiteMetadata
from .slot_expr import SlotExprLiteralContext
from .slot_call_semantics import (
    ExternalStoreBinding,
    ExternalStoreRef,
    PyrolyzeMountAdvertisementBinding,
    SlotCallBinding,
    SlotValueBinding,
    UseEffectAsyncBinding,
    UseEffectAsyncRequest,
    UseEffectBinding,
    UseEffectRequest,
)
from .slot_kinds import ContextKind
from .slot_identity import ModuleId, ModuleRegistry, SlotId, SlotIdPath, module_registry


class _AdoptionRenderCompletion(_PassStateRenderCompletion):
    __slots__ = ()
    opaque_containers_enabled = True


T = TypeVar("T")
TESTING_ONLY = property


class _ContextConstruction:
    _managed_context_cls = ContextBaseStateMgr
    _runtime_context_kind = ContextKind.SLOT

    def _initialize_context(self, **kwargs: Any) -> None:
        kwargs = self._managed_context_cls.construction_kwargs(self, **kwargs)
        self._managed_context_cls.__init__(self, owner=self, **kwargs)
        if isinstance(self, SlotContextStateMgr):
            self.attach_to_graph()


    def get_kind(self) -> ContextKind:
        return ContextBaseStateMgr.context_kind(self)


DirtyStateContext = _support.DirtyStateContext
dirtyof = _support.dirtyof
dirtyof_values = _support.dirtyof_values
SlotOwnershipError = _support.SlotOwnershipError
DuplicateKeyError = _support.DuplicateKeyError
DuplicateMountAdvertisementError = _support.DuplicateMountAdvertisementError
MountAdvertisementContextError = _support.MountAdvertisementContextError
AppContextOverrideStructureError = _support.AppContextOverrideStructureError
_SlotCallResult = _support._SlotCallResult
PendingEventHandlerBinding = _support.PendingEventHandlerBinding
_CommittedUiEntry = _support._CommittedUiEntry
SlotRuntimeContext = _support.SlotRuntimeContext
ContainerCallRuntimeContext = _support.ContainerCallRuntimeContext
_PassScopeHandle = _support._PassScopeHandle
_InvalidationScheduler = _support._InvalidationScheduler


class ContextBase(_ContextConstruction, SlotExprLiteralContext, ContextBaseStateMgr):
    _managed_context_cls = ContextBaseStateMgr
    _pass_scope_handle_cls = _PassScopeHandle
    _generation_tracker_key_const = GENERATION_TRACKER_KEY
    _runtime_context_kind = ContextKind.SLOT
    render_context: RenderContext

    def __init__(self, render_context: RenderContext) -> None:
        self._initialize_context(render_context_state_mgr=render_context)

    @property
    def render_context(self) -> RenderContext:
        render_context_state_mgr = self._render_context_state_mgr
        return self if render_context_state_mgr is None else render_context_state_mgr.owner

    def _require_active_scope(self) -> None:
        ContextBaseStateMgr.require_active_scope(self)

    def _begin_scope_pass(self) -> None:
        ContextBaseStateMgr.begin_pass(self)

    def _commit_scope_pass(self) -> None:
        ContextBaseStateMgr.end_pass(self)

    def _rollback_scope_pass(self) -> None:
        ContextBaseStateMgr.rollback_pass(self)


    def _resolve_slot_id(self, slot_id: SlotId) -> SlotId:
        return ContextBaseStateMgr.resolve_slot_id(self, slot_id)

    def _ensure_slot(self, slot_id: SlotId, slot_type: type[T]) -> T:
        return ContextBaseStateMgr.ensure_slot(self, slot_id, slot_type, parent_facade=self)


    def _materialize_pending_event_handler(
        self,
        binding: PendingEventHandlerBinding,
    ) -> Callable[..., None]:
        return ContextBaseStateMgr.materialize_pending_event_handler(self, binding, parent_facade=self)


    def _refresh_committed_ui_from_children(self) -> None:
        ContextBaseStateMgr.refresh_committed_ui_from_children(self)

    @property
    def root_context(self) -> RenderContext:
        render_context_state_mgr = self._render_context_state_mgr
        return self if render_context_state_mgr is None else render_context_state_mgr.owner


    def _effective_authored_app_context_lookup(self) -> AppContextLookup:
        return ContextBaseStateMgr.effective_authored_app_context_lookup(self)


class SlotContext(_ContextConstruction, SlotContextStateMgr):
    _managed_context_cls = SlotContextStateMgr
    _runtime_context_kind = ContextKind.SLOT
    render_context: RenderContext
    parent: ContextBase
    slot_id: SlotId
    invoke_dirty: bool
    seen_in_pass: bool

    def __init__(
        self,
        render_context: RenderContext,
        parent: ContextBase,
        slot_id: SlotId,
        invoke_dirty: bool = True,
        seen_in_pass: bool = False,
    ) -> None:
        self._initialize_context(
            render_context_state_mgr=render_context,
            parent_state_mgr=parent,
            slot_id=slot_id,
            invoke_dirty=invoke_dirty,
            seen_in_pass=seen_in_pass,
        )

    @property
    def render_context(self) -> RenderContext:
        return self._render_context_state_mgr.owner

    @render_context.setter
    def render_context(self, value: RenderContext) -> None:
        self._render_context_state_mgr = value

    @property
    def parent(self) -> ContextBase:
        return self._parent_state_mgr.owner

    @parent.setter
    def parent(self, value: ContextBase) -> None:
        self._parent_state_mgr = value

    @property
    def slot_id(self) -> SlotId:
        return self._slot_id

    @slot_id.setter
    def slot_id(self, value: SlotId) -> None:
        self._slot_id = value

    @property
    def invoke_dirty(self) -> bool:
        return self._invoke_dirty

    @invoke_dirty.setter
    def invoke_dirty(self, value: bool) -> None:
        self._invoke_dirty = value

    @property
    def seen_in_pass(self) -> bool:
        return self._seen_in_pass

    @seen_in_pass.setter
    def seen_in_pass(self, value: bool) -> None:
        self._seen_in_pass = value

    @property
    def site_metadata(self) -> tuple[RuntimeSiteMetadata[Any], ...]:
        return self._site_metadata

    @site_metadata.setter
    def site_metadata(self, value: tuple[RuntimeSiteMetadata[Any], ...]) -> None:
        self._site_metadata = value


class EventHandlerSlotContext(SlotContext, EventHandlerSlotContextStateMgr):
    _managed_context_cls = EventHandlerSlotContextStateMgr
    _runtime_context_kind = ContextKind.EVENT_HANDLER


    @property
    def committed_callback(self) -> Callable[..., Any] | None:
        return self.current._callback

    @property
    def committed_key(self) -> object | None:
        return self.current._callback_key

    @property
    def dispatch(self) -> Callable[..., None] | None:
        return self._dispatch


class RerunnableSlotContext(SlotContext, ContextBase, RerunnableSlotContextStateMgr):
    _managed_context_cls = RerunnableSlotContextStateMgr


class SlotExprSlotContext(RerunnableSlotContext, SlotExprSlotContextStateMgr):
    _managed_context_cls = SlotExprSlotContextStateMgr


    @property
    def call_site_context_manager(self) -> CallSiteContextManager:
        return self._call_site_context_manager


class SlotCallSlotContext(RerunnableSlotContext, SlotCallSlotContextStateMgr):
    _managed_context_cls = SlotCallSlotContextStateMgr
    _runtime_context_kind = ContextKind.SLOT_CALL
    _slot_call_result_cls = _SlotCallResult
    _slot_runtime_context_cls = SlotRuntimeContext


    @property
    def function_identity(self) -> Any:
        return SlotCallSlotContextStateMgr.accepted_invocation(self).function_identity

    @property
    def schema(self) -> tuple[int, tuple[str, ...]]:
        return SlotCallSlotContextStateMgr.accepted_invocation(self).schema

    @property
    def last_args(self) -> tuple[Any, ...]:
        return SlotCallSlotContextStateMgr.accepted_invocation(self).args

    @property
    def last_kwargs(self) -> tuple[tuple[str, Any], ...]:
        return SlotCallSlotContextStateMgr.accepted_invocation(self).kwargs

    @property
    def binding(self) -> SlotCallBinding | None:
        return SlotCallSlotContextStateMgr.accepted_invocation(self).binding

    def _published_slot_call_binding(self) -> SlotCallBinding | None:
        return self.current._invocation.binding

    @property
    def site_metadata(self) -> tuple[RuntimeSiteMetadata[Any], ...]:
        return self._site_metadata


    def mark_slot_call_refresh_only(self) -> None:
        SlotCallSlotContextStateMgr.queue_slot_call_invalidation(self, self)


    def publish_slot_call_mount_advertisement(
        self,
        request: PyrolyzeMountAdvertisementRequest,
    ) -> PyrolyzeMountAdvertisement:
        return SlotCallSlotContextStateMgr.publish_slot_call_mount_advertisement(self, request, host=self)


    def _mark_binding_dirty(self) -> None:
        SlotCallSlotContextStateMgr.queue_slot_call_invalidation(self, self)


class DirectiveSlotContext(SlotCallSlotContext, DirectiveSlotContextStateMgr):
    _managed_context_cls = DirectiveSlotContextStateMgr


    @property
    def committed_selectors(self) -> tuple[SlotSelector, ...]:
        return self._committed_selectors


    def _begin_scope_pass(self) -> None:
        DirectiveSlotContextStateMgr.begin_scope_pass(self)

    def _commit_scope_pass(self) -> None:
        DirectiveSlotContextStateMgr.commit_scope_pass(self)

    def _rollback_scope_pass(self) -> None:
        DirectiveSlotContextStateMgr.rollback_scope_pass(self)


class AppContextOverrideSlotContext(RerunnableSlotContext, AppContextOverrideSlotContextStateMgr):
    _managed_context_cls = AppContextOverrideSlotContextStateMgr
    _runtime_context_kind = ContextKind.APP_CONTEXT_OVERRIDE
    _structure_error_cls = AppContextOverrideStructureError


    @TESTING_ONLY
    def committed_values(self) -> tuple[Any, ...]:
        return self._committed_values


    def _effective_authored_app_context_lookup(self) -> AppContextLookup:
        return AppContextOverrideSlotContextStateMgr.effective_authored_app_context_lookup(self)

    def _begin_scope_pass(self) -> None:
        AppContextOverrideSlotContextStateMgr.begin_scope_pass(self)

    def _commit_scope_pass(self) -> None:
        AppContextOverrideSlotContextStateMgr.commit_scope_pass(self)

    def _rollback_scope_pass(self) -> None:
        AppContextOverrideSlotContextStateMgr.rollback_scope_pass(self)


class ContainerSlotContext(RerunnableSlotContext, ContainerSlotContextStateMgr):
    _managed_context_cls = ContainerSlotContextStateMgr
    _runtime_context_kind = ContextKind.CONTAINER


    @property
    def expects_native_root(self) -> bool:
        return self._expects_native_root

    @expects_native_root.setter
    def expects_native_root(self, value: bool) -> None:
        self._expects_native_root = value

    @property
    def committed_native_root(self) -> bool:
        return self._committed_native_root

    @committed_native_root.setter
    def committed_native_root(self, value: bool) -> None:
        self._committed_native_root = value


class ComponentCallSlotContext(RerunnableSlotContext, ComponentCallSlotContextStateMgr):
    _managed_context_cls = ComponentCallSlotContextStateMgr
    _runtime_context_kind = ContextKind.COMPONENT_CALL


    @property
    def child_context(self) -> RenderContext | None:
        child_state_mgr = self._child_context_state_mgr
        return None if child_state_mgr is None else child_state_mgr.owner


class KeyedLoopSlotContext(RerunnableSlotContext, KeyedLoopSlotContextStateMgr):
    _managed_context_cls = KeyedLoopSlotContextStateMgr
    _runtime_context_kind = ContextKind.KEYED_LOOP


class LoopItemSlotContext(RerunnableSlotContext, LoopItemSlotContextStateMgr):
    _managed_context_cls = LoopItemSlotContextStateMgr
    _runtime_context_kind = ContextKind.LOOP_ITEM


class LeafSlotContext(RerunnableSlotContext, LeafSlotContextStateMgr):
    _managed_context_cls = LeafSlotContextStateMgr
    _runtime_context_kind = ContextKind.LEAF


    @property
    def last_args(self) -> tuple[Any, ...]:
        return LeafSlotContextStateMgr.accepted_invocation(self).args

    @property
    def last_kwargs(self) -> tuple[tuple[str, Any], ...]:
        return LeafSlotContextStateMgr.accepted_invocation(self).kwargs


class RenderContext(ContextBase, RenderContextStateMgr):
    _managed_context_cls = RenderContextStateMgr
    _context_kind_cls = ContextKind
    _mount_advertisement_cls = PyrolyzeMountAdvertisement

    def mount(self, callback: Callable[[], None]) -> None:
        RenderContextStateMgr.mount(self, self, callback)

    def walk_context_graph(self, listener: object) -> None:
        RenderContextStateMgr.walk_context_graph(self, self, listener)

    @staticmethod
    def _scheduler_factory() -> _InvalidationScheduler:
        return _InvalidationScheduler()

    def __init__(
        self,
        *,
        owner_slot: ComponentCallSlotContext | None = None,
        scheduler_root: RenderContext | None = None,
        app_context_store: AppContextStore | None = None,
        authored_app_context_lookup: AppContextLookup | None = None,
    ) -> None:
        self._runtime_context_kind = (
            ContextKind.RENDER_ROOT if owner_slot is None else ContextKind.COMPONENT_RENDER
        )
        self._initialize_context(
            owner_slot_state_mgr=owner_slot,
            scheduler_root_state_mgr=scheduler_root,
            app_context_store=(app_context_store or AppContextStore()) if scheduler_root is None else None,
            authored_app_context_lookup=(
                (authored_app_context_lookup or EMPTY_APP_CONTEXT_LOOKUP)
                if scheduler_root is None
                else authored_app_context_lookup
            ),
        )
        if owner_slot is None and scheduler_root is None:
            _require_fresh_render_root(self)
            self._field_only_completion = _AdoptionRenderCompletion(self)


    @TESTING_ONLY
    def _scheduler_root(self) -> RenderContext:
        return self._scheduler_root_state_mgr.owner


    @TESTING_ONLY
    def _owner_slot(self) -> ComponentCallSlotContext | None:
        owner_slot_state_mgr = self._owner_slot_state_mgr
        return None if owner_slot_state_mgr is None else owner_slot_state_mgr.owner


    def _refresh_committed_ui_from_children(self) -> None:
        RenderContextStateMgr.refresh_committed_ui_from_children(self)


    def _queue_invalidation_from(self, slot: object, *, include_source: bool = True) -> None:
        RenderContextStateMgr.queue_invalidation_from(self, slot, include_source=include_source)

    def _enqueue_post_commit(self, callback: Callable[[], None]) -> None:
        RenderContextStateMgr.enqueue_post_commit(self, callback)

    def _publish_mount_advertisement(
        self,
        slot: SlotCallSlotContext,
        request: PyrolyzeMountAdvertisementRequest,
    ) -> PyrolyzeMountAdvertisement:
        return RenderContextStateMgr.publish_mount_advertisement(self, slot, request)

    def _withdraw_mount_advertisement(self, slot_id: SlotId) -> None:
        RenderContextStateMgr.withdraw_mount_advertisement(self, slot_id)

_support.REFRACTOR_CLASSES.context_base_cls = ContextBase
_support.REFRACTOR_CLASSES.render_context_cls = RenderContext
_support.REFRACTOR_CLASSES.slot_context_cls = SlotContext
_support.REFRACTOR_CLASSES.event_handler_slot_context_cls = EventHandlerSlotContext
_support.REFRACTOR_CLASSES.slot_expr_slot_context_cls = SlotExprSlotContext
_support.REFRACTOR_CLASSES.slot_call_slot_context_cls = SlotCallSlotContext
_support.REFRACTOR_CLASSES.directive_slot_context_cls = DirectiveSlotContext
_support.REFRACTOR_CLASSES.app_context_override_slot_context_cls = AppContextOverrideSlotContext
_support.REFRACTOR_CLASSES.container_slot_context_cls = ContainerSlotContext
_support.REFRACTOR_CLASSES.component_call_slot_context_cls = ComponentCallSlotContext
_support.REFRACTOR_CLASSES.keyed_loop_slot_context_cls = KeyedLoopSlotContext
_support.REFRACTOR_CLASSES.loop_item_slot_context_cls = LoopItemSlotContext


__all__ = [
    "AppContextKey",
    "AppContextLookup",
    "AppContextOverrideSlotContext",
    "AppContextOverrideStructureError",
    "AppContextStore",
    "ComponentCallSlotContext",
    "ContainerCallRuntimeContext",
    "ContainerSlotContext",
    "ContextBase",
    "DirtyStateContext",
    "DirectiveSlotContext",
    "DuplicateKeyError",
    "DuplicateMountAdvertisementError",
    "EventHandlerSlotContext",
    "ExternalStoreBinding",
    "ExternalStoreRef",
    "KeyedLoopSlotContext",
    "LeafSlotContext",
    "LoopItemSlotContext",
    "ModuleId",
    "ModuleRegistry",
    "MountAdvertisementContextError",
    "PyrolyzeMountAdvertisementBinding",
    "RenderContext",
    "RerunnableSlotContext",
    "SlotCallSlotContext",
    "SlotContext",
    "SlotExprSlotContext",
    "SlotId",
    "SlotIdPath",
    "SlotOwnershipError",
    "SlotRuntimeContext",
    "SlotValueBinding",
    "UseEffectAsyncBinding",
    "UseEffectAsyncRequest",
    "UseEffectBinding",
    "UseEffectRequest",
    "dirtyof",
    "dirtyof_values",
    "module_registry",
]
