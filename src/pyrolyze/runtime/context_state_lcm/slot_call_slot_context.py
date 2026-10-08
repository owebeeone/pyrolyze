from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from pyrolyze.runtime.slot_call_semantics import (
    PyrolyzeMountAdvertisementBinding,
    SlotCallBinding,
    SlotValueBinding,
)
from ._base import USE_FACTORY, USE_OWNER
from ._support import _project_dirty_state, _resolve_runtime_site_call, _unwrap
from .rerunnable_slot_context import RerunnableSlotContextStateMgr
from .context_base import PASS_TX_KEY
from .field_only_render import _field_only_completion
from .lifecycle_adapter import const, local_store, managed, managed_context
from pyrolyze.runtime.slot_call_core import (
    SlotCallStateSnapshot,
    call_with_optional_runtime_context,
    commit_slot_call_invocation,
    prepare_slot_call,
    refresh_slot_call_binding,
    should_invoke_slot_call,
)

if TYPE_CHECKING:
    from .render_attempt import _RenderAttempt

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class _SlotCallInvocation:
    function_identity: Any = None
    schema: tuple[int, tuple[str, ...]] = (0, ())
    args: tuple[Any, ...] = ()
    kwargs: tuple[tuple[str, Any], ...] = ()
    binding: SlotCallBinding | None = None


@managed_context
class SlotCallSlotContextStateMgr(RerunnableSlotContextStateMgr):
    _slot_call_result_cls: type[Any] = const(
        init=False, default_factory=lambda owner: type(owner)._slot_call_result_cls
    )
    _slot_runtime_context_cls: type[Any] = const(
        init=False, default_factory=lambda owner: type(owner)._slot_runtime_context_cls
    )
    _invocation: _SlotCallInvocation = managed(
        init=False,
        default_factory=_SlotCallInvocation,
        compare="identity",
        tx_key=PASS_TX_KEY,
    )
    # Unactivated binding handlers still own their existing immediate selection.
    _legacy_invocation: _SlotCallInvocation = local_store(
        default_factory=_SlotCallInvocation
    )
    _runtime_locals: dict[str, Any] = local_store(default_factory=dict)

    def _invocation_record(self) -> _SlotCallInvocation:
        if _field_only_completion(self) is None:
            return self._legacy_invocation
        return self._invocation

    def accepted_invocation(self) -> _SlotCallInvocation:
        if _field_only_completion(self) is None:
            return self._legacy_invocation
        return self.current._invocation

    @property
    def _function_identity(self) -> Any:
        return self._invocation_record().function_identity

    @property
    def _schema(self) -> tuple[int, tuple[str, ...]]:
        return self._invocation_record().schema

    @property
    def _last_args(self) -> tuple[Any, ...]:
        return self._invocation_record().args

    @property
    def _last_kwargs(self) -> tuple[tuple[str, Any], ...]:
        return self._invocation_record().kwargs

    @property
    def _binding(self) -> SlotCallBinding | None:
        return self._invocation_record().binding

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
        completion = _field_only_completion(self)
        execution = nullcontext() if completion is None else completion.attempt_scope()
        with execution:
            owner = None if completion is None else completion.active
            if owner is not None:
                completion.require_slot_type(type(self.owner))
                owner._require_open()
                owner._require_identity()
            return self._evaluate(
                func,
                args,
                kwargs,
                result_shape=result_shape,
                host=host,
                runtime_context_factory=runtime_context_factory,
                owner=owner,
            )

    def _evaluate(
        self,
        func: Callable[..., T],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        result_shape: object | None,
        host: Any,
        runtime_context_factory: Callable[[], Any] | object,
        owner: _RenderAttempt | None,
    ) -> Any:
        host = self._resolve_owner_arg(host)
        if runtime_context_factory is USE_FACTORY:
            runtime_context_factory = lambda: self._slot_runtime_context_cls(host)
        resolved_func, resolved_args, resolved_kwargs, site_metadata = (
            self.resolve_runtime_site_call(
                func,
                args,
                kwargs,
                host=host,
            )
        )
        self._site_metadata = site_metadata
        if resolved_func is None:
            raise RuntimeError("slot-call resolved to no callable target")
        prepared = self.prepare_slot_call(resolved_func, resolved_args, resolved_kwargs)
        should_invoke = self.should_invoke_slot_call(prepared)
        if owner is not None:
            owner._require_open()
            owner._require_identity()

        invocation = self._invocation_record()
        if should_invoke:
            next_result = self.call_with_optional_runtime_context(
                prepared, runtime_context_factory
            )
            if owner is not None:
                owner._require_open()
                owner._require_identity()
            commit_result = self.commit_slot_call_invocation(
                prepared, next_result, host=host
            )
            invocation = _SlotCallInvocation(
                commit_result["function_identity"],
                commit_result["schema"],
                commit_result["last_args"],
                commit_result["last_kwargs"],
                commit_result["binding"],
            )
            if owner is None:
                self._legacy_invocation = invocation
            result_dirty = commit_result["result_dirty"]
        else:
            result_dirty = False
            binding = self._binding
            if binding is not None:
                refreshed = self.refresh_slot_call_binding(binding)
                if refreshed is not None:
                    _, result_dirty = refreshed

        binding = invocation.binding
        if binding is None:
            raise RuntimeError("slot-call slot has no binding after evaluation")
        result = self._slot_call_result_cls(
            dirty=self.project_dirty_state(result_dirty, result_shape),
            value=binding.exposed_value(),
        )
        if owner is not None:
            owner._require_open()
            owner._require_identity()
            if should_invoke:
                self._invocation = invocation
        return result

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
        invocation = self._invocation_record()
        return should_invoke_slot_call(
            SlotCallStateSnapshot(
                invoke_dirty=self._invoke_dirty,
                function_identity=invocation.function_identity,
                schema=invocation.schema,
                last_args=invocation.args,
                last_kwargs=invocation.kwargs,
                has_binding=invocation.binding is not None,
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
        previous_binding = self._binding
        completion = _field_only_completion(self)
        if completion is not None:
            completion.require_slot_call_result(result)
            # The shared handler may rebind its input. Give it a detached value
            # binding, never the selected current or candidate referent.
            if previous_binding is not None:
                if type(previous_binding) is not SlotValueBinding:
                    completion.reject("external resource binding is not admitted")
                previous_binding = SlotValueBinding(previous_binding.exposed_value())
        commit_result = commit_slot_call_invocation(
            host=host,
            prepared=prepared,
            previous_binding=previous_binding,
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
        self.ui_state = self.build_committed_ui()

    def queue_slot_call_invalidation(self, host: Any = USE_OWNER) -> None:
        host = self._resolve_owner_arg(host)
        self._render_context_state_mgr.queue_invalidation_from(
            host, include_source=False
        )

    def mark_slot_call_refresh_only(self) -> None:
        raise RuntimeError(
            "mark_slot_call_refresh_only() requires explicit facade host"
        )

    def enqueue_slot_call_post_commit(self, callback: Callable[[], None]) -> None:
        self._render_context_state_mgr.enqueue_post_commit(callback)

    def publish_slot_call_mount_advertisement(
        self, request: Any, host: Any = USE_OWNER
    ) -> Any:
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
        completion = _field_only_completion(self)
        if completion is None:
            self._legacy_invocation = replace(self._legacy_invocation, binding=None)
        else:
            completion.require_retirement_allowed(self)
            if completion.active is None:
                completion.reject("slot-call retirement requires an active render")
            completion.active._require_open()
            completion.active._require_identity()
            self._invocation = replace(self._invocation, binding=None)
        if binding is not None:
            binding.deactivate()
        self.ui_state = ()
        super().deactivate()
