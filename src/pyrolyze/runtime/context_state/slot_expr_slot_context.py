from __future__ import annotations

from typing import Any, Callable

from .rerunnable_slot_context import RerunnableSlotContextStateMgr


class SlotExprSlotContextStateMgr(RerunnableSlotContextStateMgr):
    def runtime_locals(self, slot_id: Any) -> dict[str, Any]:
        return self.owner._runtime_locals_by_slot_id.setdefault(slot_id, {})

    def stage_slot_expr_pass(
        self,
        *,
        visited_call_site_ids: tuple[Any, ...],
        post_commit_callbacks: tuple[Callable[[], None], ...],
    ) -> None:
        owner = self.owner
        merged_ids = list(owner._staged_call_site_ids)
        for slot_id in visited_call_site_ids:
            if slot_id not in merged_ids:
                merged_ids.append(slot_id)
        owner._staged_call_site_ids = tuple(merged_ids)
        if post_commit_callbacks:
            owner._staged_post_commit_callbacks += post_commit_callbacks

    def append_slot_expr_post_commit_callback(self, callback: Callable[[], None]) -> None:
        self.owner._staged_post_commit_callbacks += (callback,)

    def commit_binding(self) -> None:
        owner = self.owner
        for call_site_id in owner._staged_call_site_ids:
            call_site_context = (
                owner.call_site_context_manager._staged.get(call_site_id)
                or owner.call_site_context_manager._current.get(call_site_id)
            )
            binding = call_site_context.binding if call_site_context is not None else None
            commit = getattr(binding, "commit", None)
            if callable(commit):
                commit()
        owner.call_site_context_manager.commit_pass()
        self.sync_committed_ui()
        callbacks = owner._staged_post_commit_callbacks
        owner._staged_call_site_ids = ()
        owner._staged_post_commit_callbacks = ()
        for callback in callbacks:
            callback()

    def rollback_binding(self) -> None:
        owner = self.owner
        for call_site_id in owner._staged_call_site_ids:
            call_site_context = (
                owner.call_site_context_manager._staged.get(call_site_id)
                or owner.call_site_context_manager._current.get(call_site_id)
            )
            binding = call_site_context.binding if call_site_context is not None else None
            rollback = getattr(binding, "rollback", None)
            if callable(rollback):
                rollback()
        owner.call_site_context_manager.rollback_pass()
        self.sync_committed_ui()
        owner._staged_call_site_ids = ()
        owner._staged_post_commit_callbacks = ()

    def sync_committed_ui(self) -> None:
        owner = self.owner
        advertisements: list[Any] = []
        for call_site_context in owner.call_site_context_manager._current.values():
            binding = call_site_context.binding
            wrapped_binding = getattr(binding, "binding", None) if binding is not None else None
            if not isinstance(wrapped_binding, owner._mount_advertisement_binding_type):
                continue
            advertisement = wrapped_binding.retained_advertisement()
            if advertisement is not None:
                advertisements.append(advertisement)
        owner._committed_ui = tuple(advertisements)

    def deactivate(self) -> None:
        owner = self.owner
        owner._staged_call_site_ids = ()
        owner._staged_post_commit_callbacks = ()
        owner.call_site_context_manager.close_all()
        owner._runtime_locals_by_slot_id.clear()
        owner._committed_ui = ()
        super().deactivate()
