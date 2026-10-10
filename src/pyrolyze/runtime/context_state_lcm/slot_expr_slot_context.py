from __future__ import annotations

from typing import Any, Callable, Hashable

from .lifecycle_adapter import const, local_store, managed_context, transient
from pyrolyze.runtime.call_site_context import CallSiteContextManager
from pyrolyze.runtime.slot_call_semantics import PyrolyzeMountAdvertisementBinding
from .context_base import PASS_TX_KEY
from .field_only_render import _field_only_completion
from ._base import _copy_parent_state_mgr, _copy_slot_id
from .rerunnable_slot_context import RerunnableSlotContextStateMgr


@managed_context
class SlotExprSlotContextStateMgr(RerunnableSlotContextStateMgr):
    _parent_state_mgr: Any = const(init=False, default_factory=_copy_parent_state_mgr)
    _slot_id: Any = const(init=False, default_factory=_copy_slot_id)
    _call_site_context_manager: CallSiteContextManager = local_store(
        default_factory=CallSiteContextManager,
    )
    _runtime_locals_by_slot_id: dict[Hashable, dict[str, Any]] = local_store(default_factory=dict)
    _staged_call_site_ids: tuple[Hashable, ...] = transient(default_factory=tuple, tx_key=PASS_TX_KEY)
    _staged_post_commit_callbacks: tuple[Callable[[], None], ...] = transient(
        default_factory=tuple,
        tx_key=PASS_TX_KEY,
    )
    _mount_advertisement_binding_type = PyrolyzeMountAdvertisementBinding

    def runtime_locals(self, slot_id: Any) -> dict[str, Any]:
        return self._runtime_locals_by_slot_id.setdefault(slot_id, {})

    def stage_slot_expr_pass(
        self,
        *,
        visited_call_site_ids: tuple[Any, ...],
        post_commit_callbacks: tuple[Callable[[], None], ...],
    ) -> None:
        self.require_active_scope()
        merged_ids = list(self._staged_call_site_ids)
        for slot_id in visited_call_site_ids:
            if slot_id not in merged_ids:
                merged_ids.append(slot_id)
        self._staged_call_site_ids = tuple(merged_ids)
        if post_commit_callbacks:
            for callback in post_commit_callbacks:
                self.append_slot_expr_post_commit_callback(callback)

    def append_slot_expr_post_commit_callback(self, callback: Callable[[], None]) -> None:
        self.require_active_scope()
        completion = _field_only_completion(self)
        if completion is not None and getattr(
            completion, "directive_selection_enabled", False
        ):
            completion.enqueue_post_commit(self, callback)
            return
        self._staged_post_commit_callbacks += (callback,)

    def commit_binding(self) -> None:
        self.require_active_scope()
        for call_site_id in self._staged_call_site_ids:
            call_site_context = self._call_site_context_manager.get_visible(call_site_id)
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
        self.require_active_scope()
        for call_site_id in self._staged_call_site_ids:
            call_site_context = self._call_site_context_manager.get_visible(call_site_id)
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
        for call_site_context in self._call_site_context_manager.iter_current():
            binding = call_site_context.binding
            wrapped_binding = getattr(binding, "binding", None) if binding is not None else None
            if not isinstance(wrapped_binding, self._mount_advertisement_binding_type):
                continue
            advertisement = wrapped_binding.retained_advertisement()
            if advertisement is not None:
                advertisements.append(advertisement)
        self.ui_state = tuple(advertisements)

    def deactivate(self) -> None:
        with self.publish_write_scope():
            self._staged_call_site_ids = ()
            self._staged_post_commit_callbacks = ()
            self._call_site_context_manager.close_all()
            self._runtime_locals_by_slot_id.clear()
            self.ui_state = ()
            super().deactivate()
