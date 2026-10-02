from __future__ import annotations

from typing import Any, Callable, Hashable

from .lifecycle_adapter import const, field as lifecycle_field, initvar, local_store, managed_context, transient
from pyrolyze.runtime.call_site_context import CallSiteContextManager
from pyrolyze.runtime.slot_call_semantics import PyrolyzeMountAdvertisementBinding
from .context_base import PASS_TX_KEY
from .rerunnable_slot_context import RerunnableSlotContextStateMgr


def _copy_parent_state_mgr(cls: type[object], parent_state_mgr: Any) -> Any:
    del cls
    return parent_state_mgr


def _copy_slot_id(cls: type[object], slot_id: Any) -> Any:
    del cls
    return slot_id


def _copy_invoke_dirty(cls: type[object], invoke_dirty: bool) -> bool:
    del cls
    return invoke_dirty


def _copy_seen_in_pass(cls: type[object], seen_in_pass: bool) -> bool:
    del cls
    return seen_in_pass


def _attach_slot_expr_to_graph(self: object) -> None:
    self.attach_to_graph()
    return None


@managed_context
class SlotExprSlotContextStateMgr(RerunnableSlotContextStateMgr):
    parent_state_mgr: Any = initvar(default=None)
    slot_id: Any = initvar(default=None)
    invoke_dirty: bool = initvar(default=True)
    seen_in_pass: bool = initvar(default=False)
    _parent_state_mgr: Any = const(
        init=False,
        default_factory=_copy_parent_state_mgr,
    )
    _slot_id: Any = const(
        init=False,
        default_factory=_copy_slot_id,
    )
    _invoke_dirty: bool = lifecycle_field(
        init=False,
        default_factory=_copy_invoke_dirty,
    )
    _seen_in_pass: bool = lifecycle_field(
        init=False,
        default_factory=_copy_seen_in_pass,
    )
    _site_metadata: tuple[Any, ...] = local_store(default_factory=tuple)
    _call_site_context_manager: CallSiteContextManager = local_store(
        default_factory=CallSiteContextManager,
    )
    _runtime_locals_by_slot_id: dict[Hashable, dict[str, Any]] = local_store(default_factory=dict)
    _staged_call_site_ids: tuple[Hashable, ...] = transient(default_factory=tuple, tx_key=PASS_TX_KEY)
    _staged_post_commit_callbacks: tuple[Callable[[], None], ...] = transient(
        default_factory=tuple,
        tx_key=PASS_TX_KEY,
    )
    _attach_to_graph_bad_program: None = const(
        init=False,
        default_factory=_attach_slot_expr_to_graph,
        allow_self_factory=True,
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
            self._staged_post_commit_callbacks += post_commit_callbacks

    def append_slot_expr_post_commit_callback(self, callback: Callable[[], None]) -> None:
        self.require_active_scope()
        self._staged_post_commit_callbacks += (callback,)

    def commit_binding(self) -> None:
        self.require_active_scope()
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
        self.require_active_scope()
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
        self.ui_state = tuple(advertisements)

    def deactivate(self) -> None:
        with self.publish_write_scope():
            self._staged_call_site_ids = ()
            self._staged_post_commit_callbacks = ()
            self._call_site_context_manager.close_all()
            self._runtime_locals_by_slot_id.clear()
            self.ui_state = ()
            super().deactivate()
