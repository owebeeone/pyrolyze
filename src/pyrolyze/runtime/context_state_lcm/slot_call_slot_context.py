from __future__ import annotations

from typing import Any, Callable, TypeVar

from .rerunnable_slot_context import RerunnableSlotContextStateMgr


T = TypeVar("T")


class SlotCallSlotContextStateMgr(RerunnableSlotContextStateMgr):
    def evaluate(
        self,
        func: Callable[..., T],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        result_shape: object | None = None,
    ) -> Any:
        owner = self.owner
        resolved_func, resolved_args, resolved_kwargs, site_metadata = owner._resolve_runtime_site_call(
            func,
            args,
            kwargs,
        )
        owner.site_metadata = site_metadata
        if resolved_func is None:
            raise RuntimeError("slot-call resolved to no callable target")
        prepared = owner._prepare_slot_call(resolved_func, resolved_args, resolved_kwargs)
        should_invoke = owner._should_invoke_slot_call(prepared)

        if should_invoke:
            next_result = owner._call_with_optional_runtime_context(prepared)
            commit_result = owner._commit_slot_call_invocation(prepared, next_result)
            owner.binding = commit_result["binding"]
            owner.function_identity = commit_result["function_identity"]
            owner.schema = commit_result["schema"]
            owner.last_args = commit_result["last_args"]
            owner.last_kwargs = commit_result["last_kwargs"]
            result_dirty = commit_result["result_dirty"]
        else:
            result_dirty = False
            binding = owner.binding
            if binding is not None:
                refreshed = owner._refresh_slot_call_binding(binding)
                if refreshed is not None:
                    _, result_dirty = refreshed

        binding = owner.binding
        if binding is None:
            raise RuntimeError("slot-call slot has no binding after evaluation")
        return owner._slot_call_result_cls(
            dirty=owner._project_dirty_state(result_dirty, result_shape),
            value=binding.exposed_value(),
        )

    def queue_slot_call_invalidation(self) -> None:
        self.owner.render_context._queue_invalidation_from(self.owner, include_source=False)

    def mark_slot_call_refresh_only(self) -> None:
        self.queue_slot_call_invalidation()

    def enqueue_slot_call_post_commit(self, callback: Callable[[], None]) -> None:
        self.owner.render_context._enqueue_post_commit(callback)

    def publish_slot_call_mount_advertisement(self, request: Any) -> Any:
        return self.owner.render_context._publish_mount_advertisement(self.owner, request)

    def withdraw_slot_call_mount_advertisement(self) -> None:
        self.owner.render_context._withdraw_mount_advertisement(self.owner.slot_id)

    def _mark_binding_dirty(self) -> None:
        self.queue_slot_call_invalidation()

    def commit_binding(self) -> None:
        binding = self.owner.binding
        if binding is not None:
            binding.commit()
        self.owner._sync_binding_committed_ui()

    def rollback_binding(self) -> None:
        binding = self.owner.binding
        if binding is not None:
            binding.rollback()
        self.owner._sync_binding_committed_ui()

    def deactivate(self) -> None:
        owner = self.owner
        binding = owner.binding
        owner.binding = None
        if binding is not None:
            binding.deactivate()
        owner._committed_ui = ()
        super().deactivate()
