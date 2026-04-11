from __future__ import annotations

from typing import Any, Callable

from pyrolyze.runtime.slot_kinds import ContextKind
from pyrolyze.runtime.slot_call_semantics import PyrolyzeMountAdvertisementBinding
from pyrolyze.runtime.trace import TraceChannel, emit_trace, trace_enabled

from ._base import USE_OWNER
from .context_base import ContextBaseStateMgr
from ._support import (
    DuplicateMountAdvertisementError,
    MountAdvertisementContextError,
    REFRACTOR_CLASSES,
    REFRACTOR_RUNTIME,
    _InvalidationScheduler,
    _resolve_mount_advertisement_owner,
)


class RenderContextStateMgr(ContextBaseStateMgr):
    def __init__(
        self,
        owner: Any,
        *,
        owner_slot_state_mgr: Any | None = None,
        scheduler_root_state_mgr: Any | None = None,
        app_context_store: Any | None = None,
        authored_app_context_lookup: Any | None = None,
        scheduler: Any | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            owner,
            render_context_state_mgr=None,
            context_kind=(
                ContextKind.RENDER_ROOT
                if owner_slot_state_mgr is None
                else ContextKind.COMPONENT_RENDER
            ),
            **kwargs,
        )
        self._slots_by_id: dict[Any, Any] = {}
        self._mount_advertisements_by_slot: dict[Any, Any] = {}
        self._owner_slot_state_mgr = owner_slot_state_mgr
        self._mounted_callback: Callable[[], None] | None = None
        self._post_commit_callbacks: list[Callable[[], None]] = []
        self._queued_invalidations: list[Any] = []
        self._flush_poster: Callable[[Callable[[], None]], None] | None = None
        self._flush_posted = False
        self._flush_running = False
        if scheduler_root_state_mgr is None:
            self._scheduler_root_state_mgr = self
            self._scheduler = scheduler if scheduler is not None else _InvalidationScheduler()
            self._app_context_store = app_context_store
            self._authored_app_context_lookup = authored_app_context_lookup
        else:
            self._scheduler_root_state_mgr = scheduler_root_state_mgr
            self._scheduler = scheduler_root_state_mgr._scheduler
            self._app_context_store = scheduler_root_state_mgr._app_context_store
            self._authored_app_context_lookup = (
                scheduler_root_state_mgr._authored_app_context_lookup
                if authored_app_context_lookup is None
                else authored_app_context_lookup
            )

    def context_kind(self) -> Any:
        return self._context_kind

    def register_slot(self, slot: Any) -> None:
        self._slots_by_id[slot.slot_id] = slot._state_mgr

    def register_slot_state_mgr(self, slot_state_mgr: Any) -> None:
        self._slots_by_id[slot_state_mgr.current_slot_id()] = slot_state_mgr

    def unregister_slot(self, slot_id: Any) -> None:
        self._slots_by_id.pop(slot_id, None)

    def get_registered_slot(self, slot_id: Any) -> Any | None:
        slot_state_mgr = self._slots_by_id.get(slot_id)
        if slot_state_mgr is None:
            return None
        return slot_state_mgr.owner

    def clear_registered_slots(self) -> None:
        self._slots_by_id.clear()

    def mount(self, boundary_facade: Any = USE_OWNER, callback: Callable[[], None] | None = None) -> None:
        boundary_facade = self._resolve_owner_arg(boundary_facade)
        if callback is None:
            raise RuntimeError("mount callback is required")
        self._mounted_callback = callback
        self._run_boundary(boundary_facade)

    def _run_boundary(self, boundary_facade: Any = USE_OWNER) -> None:
        boundary_facade = self._resolve_owner_arg(boundary_facade)
        callback = self._mounted_callback
        if callback is None:
            raise RuntimeError("render context is not mounted")
        scheduler_root = self._scheduler_root_state_mgr
        scheduler = self._scheduler
        is_outermost_boundary = not scheduler.active
        tracker = scheduler_root._app_context_store.get(self._generation_tracker_key)
        if is_outermost_boundary:
            tracker.begin()
        scheduler.enter_active(boundary_facade)
        if trace_enabled(TraceChannel.BOUNDARY):
            emit_trace(
                TraceChannel.BOUNDARY,
                "start",
                boundary=self._debug_boundary_id(),
                queued=tuple(boundary._debug_boundary_id() for boundary in scheduler.queue),
            )
        try:
            callback()
            if is_outermost_boundary:
                tracker.commit()
        except BaseException:
            if trace_enabled(TraceChannel.BOUNDARY):
                emit_trace(
                    TraceChannel.BOUNDARY,
                    "error",
                    boundary=self._debug_boundary_id(),
                )
            if is_outermost_boundary:
                tracker.rollback()
            raise
        finally:
            scheduler.exit_active(boundary_facade)
            if trace_enabled(TraceChannel.BOUNDARY):
                emit_trace(
                    TraceChannel.BOUNDARY,
                    "end",
                    boundary=self._debug_boundary_id(),
                )

    def pass_scope(self) -> Any:
        return super().pass_scope()

    def set_flush_poster(self, post: Callable[[Callable[[], None]], None]) -> None:
        self._scheduler_root_state_mgr._flush_poster = post

    def run_pending_invalidations(self) -> None:
        scheduler_root = self._scheduler_root_state_mgr
        scheduler = scheduler_root._scheduler
        if scheduler_root._flush_running:
            return None
        if trace_enabled(TraceChannel.FLUSH):
            emit_trace(
                TraceChannel.FLUSH,
                "start",
                queued=tuple(boundary._debug_boundary_id() for boundary in scheduler.queue),
            )
        scheduler_root._flush_posted = False
        scheduler_root._flush_running = True
        try:
            while True:
                boundary = scheduler.pop_next()
                if boundary is None:
                    break
                boundary._run_boundary()
        finally:
            scheduler_root._flush_running = False
        if scheduler_root._scheduler.has_pending_work():
            scheduler_root._post_flush_if_needed(was_pending=False)
        if trace_enabled(TraceChannel.FLUSH):
            emit_trace(
                TraceChannel.FLUSH,
                "end",
                queued=tuple(boundary._debug_boundary_id() for boundary in scheduler_root._scheduler.queue),
            )
        return None

    def begin_pass(self) -> None:
        super().begin_pass()

    def end_pass(self) -> None:
        super().end_pass()
        self._rebuild_mount_advertisement_surface()
        self._flush_post_commit()

    def rollback_pass(self) -> None:
        super().rollback_pass()
        self._rebuild_mount_advertisement_surface()
        self._post_commit_callbacks.clear()

    def debug_children_of(self, slot_id: Any = None) -> tuple[Any, ...]:
        if slot_id is None:
            children = self._children
        else:
            slot = self.get_registered_slot(slot_id)
            if slot is None:
                return ()
            children = slot._state_mgr.children_by_slot_id()
        return tuple(children.keys())

    def debug_is_active(self, slot_id: Any) -> bool:
        return slot_id in self._slots_by_id

    def debug_pending_boundaries(self) -> tuple[Any, ...]:
        scheduler_root = self._scheduler_root_state_mgr
        return tuple(boundary._debug_boundary_id() for boundary in scheduler_root._scheduler.queue)

    def debug_mount_advertisements(self) -> tuple[Any, ...]:
        return tuple(self._mount_advertisements_by_slot.values())

    def debug_ui(self, slot_id: Any = None) -> tuple[Any, ...]:
        if slot_id is None:
            return self._committed_ui
        else:
            slot = self.get_registered_slot(slot_id)
            if slot is None:
                return ()
            return slot._state_mgr.committed_ui()

    def committed_ui(self) -> tuple[Any, ...]:
        return self._committed_ui

    def refresh_committed_ui_from_children(self) -> None:
        self._committed_ui = self.build_committed_ui()
        owner_slot_state_mgr = self._owner_slot_state_mgr
        if owner_slot_state_mgr is None:
            return
        owner_slot_state_mgr._committed_ui = self._committed_ui
        owner_slot_state_mgr._parent_state_mgr.refresh_committed_ui_from_children()

    def walk_context_graph(self, boundary_facade: Any = USE_OWNER, listener: object | None = None) -> None:
        boundary_facade = self._resolve_owner_arg(boundary_facade)
        if listener is None:
            raise RuntimeError("listener is required")
        if REFRACTOR_RUNTIME.walk_context_graph is None:
            raise RuntimeError("context graph walker is not configured")
        REFRACTOR_RUNTIME.walk_context_graph(boundary_facade, listener)

    def close_app_contexts(self) -> None:
        self._scheduler_root_state_mgr._app_context_store.close_all()

    def _debug_boundary_id(self) -> Any:
        if self._owner_slot_state_mgr is None:
            return None
        return self._owner_slot_state_mgr.current_slot_id()

    def _is_ancestor_boundary_of(self, other: Any) -> bool:
        current_state_mgr = other._state_mgr
        while current_state_mgr is not None:
            if current_state_mgr is self:
                return True
            owner_slot_state_mgr = getattr(current_state_mgr, "_owner_slot_state_mgr", None)
            current_state_mgr = (
                owner_slot_state_mgr._render_context_state_mgr
                if owner_slot_state_mgr is not None
                else None
            )
        return False

    def _remove_from_scheduler(self, boundary_facade: Any = USE_OWNER) -> None:
        boundary_facade = self._resolve_owner_arg(boundary_facade)
        self._scheduler.remove(boundary_facade)

    def _flush_post_commit(self) -> None:
        callbacks = self._post_commit_callbacks
        self._post_commit_callbacks = []
        for callback in callbacks:
            callback()

    def _post_flush_if_needed(self, *, was_pending: bool) -> None:
        scheduler_root = self._scheduler_root_state_mgr
        if scheduler_root._flush_poster is None:
            return
        if was_pending or not scheduler_root._scheduler.has_pending_work():
            return
        if scheduler_root._flush_posted or scheduler_root._flush_running:
            return
        scheduler_root._flush_posted = True
        scheduler_root._flush_poster(lambda: scheduler_root.run_pending_invalidations())

    def _rebuild_mount_advertisement_surface(self) -> None:
        slot_call_slot_context_cls = REFRACTOR_CLASSES.slot_call_slot_context_cls
        slot_expr_slot_context_cls = REFRACTOR_CLASSES.slot_expr_slot_context_cls
        next_entries: dict[Any, Any] = {}
        for slot_id, slot_state_mgr in self._slots_by_id.items():
            slot = slot_state_mgr.owner
            if slot_call_slot_context_cls is not None and isinstance(slot, slot_call_slot_context_cls):
                binding = slot.binding
                if not isinstance(binding, PyrolyzeMountAdvertisementBinding):
                    continue
                advertisement = binding.retained_advertisement()
                if advertisement is None:
                    continue
                next_entries[slot_id] = advertisement
                continue
            if slot_expr_slot_context_cls is not None and isinstance(slot, slot_expr_slot_context_cls):
                for call_site_context in slot.call_site_context_manager._current.values():
                    binding = call_site_context.binding
                    wrapped_binding = getattr(binding, "binding", None) if binding is not None else None
                    if not isinstance(wrapped_binding, PyrolyzeMountAdvertisementBinding):
                        continue
                    advertisement = wrapped_binding.retained_advertisement()
                    if advertisement is None or advertisement.source_slot_id is None:
                        continue
                    next_entries[advertisement.source_slot_id] = advertisement
        for surface_owner_id in {
            advertisement.surface_owner_id for advertisement in next_entries.values()
        }:
            self._validate_mount_advertisement_surface(
                next_entries,
                surface_owner_id=surface_owner_id,
            )
        self._mount_advertisements_by_slot = next_entries

    def queue_invalidation_from(self, slot: object, *, include_source: bool = True) -> None:
        slot_state_mgr = slot._state_mgr if hasattr(slot, "_state_mgr") else slot
        boundary_state_mgr = slot_state_mgr._render_context_state_mgr
        scheduler_root = boundary_state_mgr._scheduler_root_state_mgr
        was_pending = scheduler_root._scheduler.has_pending_work()
        if include_source:
            slot_state_mgr._invoke_dirty = True

        current = slot_state_mgr._parent_state_mgr
        dirty_contexts = 0
        while current is not None:
            dirty_contexts += 1
            current._invoke_dirty = True
            current_state_mgr = current
            if current_state_mgr.context_kind() in {
                ContextKind.RENDER_ROOT,
                ContextKind.COMPONENT_RENDER,
            }:
                boundary_state_mgr = current_state_mgr
                break
            current = current._parent_state_mgr

        owner_slot_state_mgr = boundary_state_mgr._owner_slot_state_mgr
        if owner_slot_state_mgr is not None:
            owner_slot_state_mgr._invoke_dirty = True

        boundary_state_mgr._scheduler.request(boundary_state_mgr.owner)
        if not any(queued is slot_state_mgr for queued in self._queued_invalidations):
            self._queued_invalidations.append(slot_state_mgr)
        scheduler_root._post_flush_if_needed(was_pending=was_pending)
        if trace_enabled(TraceChannel.INVALIDATION):
            emit_trace(
                TraceChannel.INVALIDATION,
                "queued",
                source_slot=slot_state_mgr.current_slot_id(),
                boundary=boundary_state_mgr._debug_boundary_id(),
                owner_slot=owner_slot_state_mgr.current_slot_id() if owner_slot_state_mgr is not None else None,
                include_source=include_source,
                dirty_contexts=dirty_contexts,
                queued=tuple(item._debug_boundary_id() for item in boundary_state_mgr._scheduler.queue),
            )

    def enqueue_post_commit(self, callback: Callable[[], None]) -> None:
        self._post_commit_callbacks.append(callback)

    def publish_mount_advertisement(self, slot: Any, request: Any) -> Any:
        slot_state_mgr = slot._state_mgr if hasattr(slot, "_state_mgr") else slot
        parent = _resolve_mount_advertisement_owner(slot_state_mgr._parent_state_mgr)
        if parent is None:
            raise MountAdvertisementContextError("advertise_mount() requires a native container owner")
        if not (parent._expects_native_root or parent._committed_native_root):
            raise MountAdvertisementContextError(
                "advertise_mount() requires a native container node owner"
            )
        mount_owner_id = parent.current_slot_id()
        if mount_owner_id is None:
            raise MountAdvertisementContextError(
                "advertise_mount() could not resolve a container slot owner"
            )
        from pyrolyze.api import PyrolyzeMountAdvertisement

        return PyrolyzeMountAdvertisement(
            key=request.key,
            selectors=request.selectors,
            default=request.default,
            source_slot_id=slot_state_mgr.current_slot_id(),
            surface_owner_id=mount_owner_id,
            mount_owner_id=mount_owner_id,
        )

    def withdraw_mount_advertisement(self, slot_id: Any) -> None:
        if slot_id not in self._mount_advertisements_by_slot:
            return
        next_entries = dict(self._mount_advertisements_by_slot)
        next_entries.pop(slot_id, None)
        self._mount_advertisements_by_slot = next_entries

    def _validate_mount_advertisement_surface(
        self,
        advertisements_by_slot: dict[Any, Any],
        *,
        surface_owner_id: Any,
    ) -> None:
        surface_entries = [
            advertisement
            for advertisement in advertisements_by_slot.values()
            if advertisement.surface_owner_id == surface_owner_id
        ]
        seen_keys: list[object] = []
        seen_default = False
        for advertisement in surface_entries:
            if any(advertisement.key == existing_key for existing_key in seen_keys):
                raise DuplicateMountAdvertisementError(
                    f"duplicate mount advertisement key {advertisement.key!r}"
                )
            seen_keys.append(advertisement.key)
            if advertisement.default:
                if seen_default:
                    raise DuplicateMountAdvertisementError(
                        "duplicate default mount advertisement"
                    )
                seen_default = True
