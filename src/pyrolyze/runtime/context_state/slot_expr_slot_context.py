from __future__ import annotations

from typing import Any, Callable

from pyrolyze.runtime.call_site_context import CallSiteContextManager
from pyrolyze.runtime.slot_call_semantics import PyrolyzeMountAdvertisementBinding
from .rerunnable_slot_context import RerunnableSlotContextStateMgr


class SlotExprSlotContextStateMgr(RerunnableSlotContextStateMgr):
    def __init__(self, owner: object, **kwargs: object) -> None:
        super().__init__(owner, **kwargs)
        self._call_site_context_manager = CallSiteContextManager()
        self._runtime_locals_by_slot_id: dict[Any, dict[str, Any]] = {}
        self._staged_call_site_ids: tuple[Any, ...] = ()
        self._staged_post_commit_callbacks: tuple[Callable[[], None], ...] = ()
        self._mount_advertisement_binding_type = PyrolyzeMountAdvertisementBinding

    def runtime_locals(self, slot_id: Any) -> dict[str, Any]:
        return self._runtime_locals_by_slot_id.setdefault(slot_id, {})

    def stage_slot_expr_pass(
        self,
        *,
        visited_call_site_ids: tuple[Any, ...],
        post_commit_callbacks: tuple[Callable[[], None], ...],
    ) -> None:
        merged_ids = list(self._staged_call_site_ids)
        for slot_id in visited_call_site_ids:
            if slot_id not in merged_ids:
                merged_ids.append(slot_id)
        self._staged_call_site_ids = tuple(merged_ids)
        if post_commit_callbacks:
            self._staged_post_commit_callbacks += post_commit_callbacks

    def append_slot_expr_post_commit_callback(self, callback: Callable[[], None]) -> None:
        self._staged_post_commit_callbacks += (callback,)

    def commit_binding(self) -> None:
        for call_site_id in self._staged_call_site_ids:
            call_site_context = (
                self._call_site_context_manager._staged.get(call_site_id)
                or self._call_site_context_manager._current.get(call_site_id)
            )
            binding = call_site_context.binding if call_site_context is not None else None
            commit = getattr(binding, "commit", None)
            if callable(commit):
                commit()
        self._call_site_context_manager.commit_pass()
        self.sync_committed_ui()
        callbacks = self._staged_post_commit_callbacks
        self._staged_call_site_ids = ()
        self._staged_post_commit_callbacks = ()
        for callback in callbacks:
            callback()

    def rollback_binding(self) -> None:
        for call_site_id in self._staged_call_site_ids:
            call_site_context = (
                self._call_site_context_manager._staged.get(call_site_id)
                or self._call_site_context_manager._current.get(call_site_id)
            )
            binding = call_site_context.binding if call_site_context is not None else None
            rollback = getattr(binding, "rollback", None)
            if callable(rollback):
                rollback()
        self._call_site_context_manager.rollback_pass()
        self.sync_committed_ui()
        self._staged_call_site_ids = ()
        self._staged_post_commit_callbacks = ()

    def sync_committed_ui(self) -> None:
        advertisements: list[Any] = []
        for call_site_context in self._call_site_context_manager._current.values():
            binding = call_site_context.binding
            wrapped_binding = getattr(binding, "binding", None) if binding is not None else None
            if not isinstance(wrapped_binding, self._mount_advertisement_binding_type):
                continue
            advertisement = wrapped_binding.retained_advertisement()
            if advertisement is not None:
                advertisements.append(advertisement)
        self._committed_ui = tuple(advertisements)

    def deactivate(self) -> None:
        self._staged_call_site_ids = ()
        self._staged_post_commit_callbacks = ()
        self._call_site_context_manager.close_all()
        self._runtime_locals_by_slot_id.clear()
        self._committed_ui = ()
        super().deactivate()
