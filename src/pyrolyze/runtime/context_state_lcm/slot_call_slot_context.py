from __future__ import annotations

from typing import Any, Callable, TypeVar

from pyrolyze.runtime.slot_call_semantics import PyrolyzeMountAdvertisementBinding
from ._base import USE_FACTORY, USE_OWNER
from ._support import _project_dirty_state, _resolve_runtime_site_call, _unwrap
from .rerunnable_slot_context import RerunnableSlotContextStateMgr
from pyrolyze.runtime.slot_call_core import (
    SlotCallStateSnapshot,
    call_with_optional_runtime_context,
    commit_slot_call_invocation,
    prepare_slot_call,
    refresh_slot_call_binding,
    should_invoke_slot_call,
)


T = TypeVar("T")


class SlotCallSlotContextStateMgr(RerunnableSlotContextStateMgr):
    def __init__(self, owner: object, **kwargs: object) -> None:
        super().__init__(owner, **kwargs)
        self._slot_call_result_cls = type(owner)._slot_call_result_cls
        self._slot_runtime_context_cls = type(owner)._slot_runtime_context_cls
        self._function_identity: Any = None
        self._schema: tuple[int, tuple[str, ...]] = (0, ())
        self._last_args: tuple[Any, ...] = ()
        self._last_kwargs: tuple[tuple[str, Any], ...] = ()
        self._binding: Any = None
        self._site_metadata: tuple[Any, ...] = ()
        self._runtime_locals: dict[str, Any] = {}

    def evaluate(
        self,
        func: Callable[..., T],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        result_shape: object | None = None,
        host: Any = USE_OWNER,
        runtime_context_factory: Callable[[], Any] | object = USE_FACTORY,
    ) -> Any:
        host = self._resolve_owner_arg(host)
        if runtime_context_factory is USE_FACTORY:
            runtime_context_factory = lambda: self._slot_runtime_context_cls(host)
        resolved_func, resolved_args, resolved_kwargs, site_metadata = self.resolve_runtime_site_call(
            func,
            args,
            kwargs,
            host=host,
        )
        self._site_metadata = site_metadata
        if resolved_func is None:
            raise RuntimeError("slot-call resolved to no callable target")
        prepared = self.prepare_slot_call(resolved_func, resolved_args, resolved_kwargs)
        should_invoke = self.should_invoke_slot_call(prepared)

        if should_invoke:
            next_result = self.call_with_optional_runtime_context(prepared, runtime_context_factory)
            commit_result = self.commit_slot_call_invocation(prepared, next_result, host=host)
            self._binding = commit_result["binding"]
            self._function_identity = commit_result["function_identity"]
            self._schema = commit_result["schema"]
            self._last_args = commit_result["last_args"]
            self._last_kwargs = commit_result["last_kwargs"]
            result_dirty = commit_result["result_dirty"]
        else:
            result_dirty = False
            binding = self._binding
            if binding is not None:
                refreshed = self.refresh_slot_call_binding(binding)
                if refreshed is not None:
                    _, result_dirty = refreshed

        binding = self._binding
        if binding is None:
            raise RuntimeError("slot-call slot has no binding after evaluation")
        return self._slot_call_result_cls(
            dirty=self.project_dirty_state(result_dirty, result_shape),
            value=binding.exposed_value(),
        )

    def resolve_runtime_site_call(
        self,
        func: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        host: Any = USE_OWNER,
    ) -> tuple[Any | None, tuple[Any, ...], dict[str, Any], tuple[Any, ...]]:
        host = self._resolve_owner_arg(host)
        return _resolve_runtime_site_call(host, func, args, kwargs)

    def prepare_slot_call(
        self,
        func: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        return prepare_slot_call(func, args, kwargs, unwrap=_unwrap)

    def should_invoke_slot_call(self, prepared: Any) -> bool:
        return should_invoke_slot_call(
            SlotCallStateSnapshot(
                invoke_dirty=self._invoke_dirty,
                function_identity=self._function_identity,
                schema=self._schema,
                last_args=self._last_args,
                last_kwargs=self._last_kwargs,
                has_binding=self._binding is not None,
            ),
            prepared,
        )

    def call_with_optional_runtime_context(
        self,
        prepared: Any,
        runtime_context_factory: Callable[[], Any] | object = USE_FACTORY,
    ) -> Any:
        if runtime_context_factory is USE_FACTORY:
            host = self._owner_facade()
            runtime_context_factory = lambda: self._slot_runtime_context_cls(host)
        return call_with_optional_runtime_context(
            prepared,
            cache_attr_name="_pyrolyze_slot_runtime_ctx_param",
            runtime_context_annotation=self._slot_runtime_context_cls,
            runtime_context_factory=runtime_context_factory,
        )

    def commit_slot_call_invocation(
        self,
        prepared: Any,
        result: Any,
        host: Any = USE_OWNER,
    ) -> dict[str, Any]:
        host = self._resolve_owner_arg(host)
        commit_result = commit_slot_call_invocation(
            host=host,
            prepared=prepared,
            previous_binding=self._binding,
            result=result,
        )
        return {
            "binding": commit_result.binding,
            "function_identity": commit_result.function_identity,
            "schema": commit_result.schema,
            "last_args": commit_result.last_args,
            "last_kwargs": commit_result.last_kwargs,
            "result_dirty": commit_result.result_dirty,
        }

    def refresh_slot_call_binding(self, binding: Any) -> tuple[Any, bool] | None:
        return refresh_slot_call_binding(binding)

    def project_dirty_state(self, dirty: bool, result_shape: object | None) -> Any:
        return _project_dirty_state(dirty, result_shape)

    def build_committed_ui(self) -> tuple[Any, ...]:
        binding = self._binding
        if isinstance(binding, PyrolyzeMountAdvertisementBinding):
            advertisement = binding.retained_advertisement()
            if advertisement is None:
                return ()
            return (advertisement,)
        return ()

    def sync_binding_committed_ui(self) -> None:
        self._committed_ui = self.build_committed_ui()

    def queue_slot_call_invalidation(self, host: Any = USE_OWNER) -> None:
        host = self._resolve_owner_arg(host)
        self._render_context_state_mgr.queue_invalidation_from(host, include_source=False)

    def mark_slot_call_refresh_only(self) -> None:
        raise RuntimeError("mark_slot_call_refresh_only() requires explicit facade host")

    def enqueue_slot_call_post_commit(self, callback: Callable[[], None]) -> None:
        self._render_context_state_mgr.enqueue_post_commit(callback)

    def publish_slot_call_mount_advertisement(self, request: Any, host: Any = USE_OWNER) -> Any:
        host = self._resolve_owner_arg(host)
        return self._render_context_state_mgr.publish_mount_advertisement(host, request)

    def withdraw_slot_call_mount_advertisement(self) -> None:
        self._render_context_state_mgr.withdraw_mount_advertisement(self._slot_id)

    def _mark_binding_dirty(self) -> None:
        raise RuntimeError("_mark_binding_dirty() requires explicit facade host")

    def commit_binding(self) -> None:
        binding = self._binding
        if binding is not None:
            binding.commit()
        self.sync_binding_committed_ui()

    def rollback_binding(self) -> None:
        binding = self._binding
        if binding is not None:
            binding.rollback()
        self.sync_binding_committed_ui()

    def deactivate(self) -> None:
        binding = self._binding
        self._binding = None
        if binding is not None:
            binding.deactivate()
        self._committed_ui = ()
        super().deactivate()
