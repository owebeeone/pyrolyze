from __future__ import annotations

from typing import Any, Callable

from pyrolyze.runtime.trace import TraceChannel, emit_trace, trace_enabled

from .context_base import ContextBaseStateMgr


class RenderContextStateMgr(ContextBaseStateMgr):
    def mount(self, callback: Callable[[], None]) -> None:
        self.owner._mounted_callback = callback
        self._run_boundary()

    def _run_boundary(self) -> None:
        callback = self.owner._mounted_callback
        if callback is None:
            raise RuntimeError("render context is not mounted")
        scheduler_root = self.owner._scheduler_root
        scheduler = self.owner._scheduler
        is_outermost_boundary = not scheduler.active
        tracker = scheduler_root._app_context_store.get(self._generation_tracker_key)
        if is_outermost_boundary:
            tracker.begin()
        scheduler.enter_active(self.owner)
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
            scheduler.exit_active(self.owner)
            if trace_enabled(TraceChannel.BOUNDARY):
                emit_trace(
                    TraceChannel.BOUNDARY,
                    "end",
                    boundary=self._debug_boundary_id(),
                )

    def pass_scope(self) -> Any:
        return super().pass_scope()

    def set_flush_poster(self, post: Callable[[Callable[[], None]], None]) -> None:
        self.owner._scheduler_root._flush_poster = post

    def run_pending_invalidations(self) -> None:
        scheduler_root = self.owner._scheduler_root
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
        self.owner._post_commit_callbacks.clear()

    def debug_children_of(self, slot_id: Any = None) -> tuple[Any, ...]:
        if slot_id is None:
            owner = self.owner
        else:
            slot = self.owner._slots_by_id.get(slot_id)
            if slot is None or not hasattr(slot, "_children"):
                return ()
            owner = slot
        return tuple(owner._children.keys())

    def debug_is_active(self, slot_id: Any) -> bool:
        return slot_id in self.owner._slots_by_id

    def debug_pending_boundaries(self) -> tuple[Any, ...]:
        scheduler_root = self.owner._scheduler_root
        return tuple(boundary._debug_boundary_id() for boundary in scheduler_root._scheduler.queue)

    def debug_mount_advertisements(self) -> tuple[Any, ...]:
        return tuple(self.owner._mount_advertisements_by_slot.values())

    def debug_ui(self, slot_id: Any = None) -> tuple[Any, ...]:
        if slot_id is None:
            owner = self.owner
        else:
            slot = self.owner._slots_by_id.get(slot_id)
            if slot is None or not hasattr(slot, "_committed_ui"):
                return ()
            owner = slot
        return owner._committed_ui

    def committed_ui(self) -> tuple[Any, ...]:
        return self.owner._committed_ui

    def refresh_committed_ui_from_children(self) -> None:
        self.owner._committed_ui = self.owner._build_committed_ui()
        owner_slot = self.owner._owner_slot
        if owner_slot is None:
            return
        owner_slot._committed_ui = self.owner._committed_ui
        owner_slot.parent._refresh_committed_ui_from_children()

    def walk_context_graph(self, listener: object) -> None:
        from pyrolyze.visitor import walk_context_graph

        walk_context_graph(self.owner, listener)

    def close_app_contexts(self) -> None:
        self.owner._scheduler_root._app_context_store.close_all()

    def _debug_boundary_id(self) -> Any:
        owner_slot = self.owner._owner_slot
        if owner_slot is None:
            return None
        return owner_slot.slot_id

    def _is_ancestor_boundary_of(self, other: Any) -> bool:
        current = other
        while current is not None:
            if current is self.owner:
                return True
            owner_slot = getattr(current, "_owner_slot", None)
            current = owner_slot.render_context if owner_slot is not None else None
        return False

    def _remove_from_scheduler(self) -> None:
        self.owner._scheduler.remove(self.owner)

    def _flush_post_commit(self) -> None:
        callbacks = self.owner._post_commit_callbacks
        self.owner._post_commit_callbacks = []
        for callback in callbacks:
            callback()

    def _post_flush_if_needed(self, *, was_pending: bool) -> None:
        scheduler_root = self.owner._scheduler_root
        if scheduler_root._flush_poster is None:
            return
        if was_pending or not scheduler_root._scheduler.has_pending_work():
            return
        if scheduler_root._flush_posted or scheduler_root._flush_running:
            return
        scheduler_root._flush_posted = True
        scheduler_root._flush_poster(scheduler_root.run_pending_invalidations)

    def _rebuild_mount_advertisement_surface(self) -> None:
        from pyrolyze.runtime.context_bare_refactor import SlotCallSlotContext, SlotExprSlotContext
        from pyrolyze.runtime.slot_call_semantics import PyrolyzeMountAdvertisementBinding

        next_entries: dict[Any, Any] = {}
        for slot_id, slot in self.owner._slots_by_id.items():
            if isinstance(slot, SlotCallSlotContext):
                binding = slot.binding
                if not isinstance(binding, PyrolyzeMountAdvertisementBinding):
                    continue
                advertisement = binding.retained_advertisement()
                if advertisement is None:
                    continue
                next_entries[slot_id] = advertisement
                continue
            if isinstance(slot, SlotExprSlotContext):
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
        self.owner._mount_advertisements_by_slot = next_entries

    def _validate_mount_advertisement_surface(
        self,
        advertisements_by_slot: dict[Any, Any],
        *,
        surface_owner_id: Any,
    ) -> None:
        from pyrolyze.runtime.context_bare_refactor import DuplicateMountAdvertisementError

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
