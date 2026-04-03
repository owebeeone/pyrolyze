from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar, cast

from pyrolyze.api import PyrolyzeMountAdvertisement, PyrolyzeMountAdvertisementRequest


T = TypeVar("T")


class SlotCallBindingHost(ABC):
    @abstractmethod
    def queue_slot_call_invalidation(self) -> None: ...

    @abstractmethod
    def mark_slot_call_refresh_only(self) -> None: ...

    @abstractmethod
    def enqueue_slot_call_post_commit(self, callback: Callable[[], None]) -> None: ...

    @abstractmethod
    def publish_slot_call_mount_advertisement(
        self,
        request: PyrolyzeMountAdvertisementRequest,
    ) -> PyrolyzeMountAdvertisement: ...

    @abstractmethod
    def withdraw_slot_call_mount_advertisement(self) -> None: ...


class AsyncEffectHandle(ABC):
    @abstractmethod
    def cancel(self) -> None: ...


@dataclass(frozen=True, slots=True)
class ExternalStoreRef(Generic[T]):
    identity: object
    subscribe: Callable[[Callable[[], None]], Callable[[], None]]
    get: Callable[[], T]


@dataclass(frozen=True, slots=True)
class UseEffectRequest:
    effect_fn: Callable[[], Callable[[], None] | None]
    deps: tuple[Any, ...] | None = None
    phase: str = "passive"


@dataclass(frozen=True, slots=True)
class UseEffectAsyncRequest:
    start: Callable[[Callable[[], None]], AsyncEffectHandle | None]
    deps: tuple[Any, ...] | None = None
    cleanup: Callable[[], None] | None = None


class SlotCallBinding:
    def exposed_value(self) -> Any:
        raise NotImplementedError

    def refresh(self) -> tuple[Any, bool] | None:
        return None

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None

    def deactivate(self) -> None:
        return None


@dataclass(slots=True)
class SlotValueBinding(SlotCallBinding):
    value: Any

    def exposed_value(self) -> Any:
        return self.value

    def rebind(self, value: Any) -> None:
        self.value = value


@dataclass(slots=True)
class ExternalStoreBinding(SlotCallBinding):
    host: SlotCallBindingHost
    ref: ExternalStoreRef[Any]
    value: Any = None
    initialized: bool = False
    dirty: bool = False
    unsubscribe: Callable[[], None] | None = None

    @classmethod
    def bind(
        cls,
        host: SlotCallBindingHost,
        ref: ExternalStoreRef[Any],
    ) -> ExternalStoreBinding:
        binding = cls(host=host, ref=ref)
        binding._subscribe(ref)
        binding._update_from_get()
        return binding

    def exposed_value(self) -> Any:
        return self.value

    def refresh(self) -> tuple[Any, bool] | None:
        if not self.dirty:
            return None
        dirty = self._update_from_get()
        self.dirty = False
        return self.value, dirty

    def rebind(self, ref: ExternalStoreRef[Any]) -> None:
        if self.ref.identity == ref.identity:
            self.ref = ref
        else:
            next_unsubscribe = ref.subscribe(self._mark_dirty)
            previous_unsubscribe = self.unsubscribe
            self.ref = ref
            self.unsubscribe = next_unsubscribe
            if previous_unsubscribe is not None:
                previous_unsubscribe()
        self._update_from_get()

    def deactivate(self) -> None:
        previous_unsubscribe = self.unsubscribe
        self.unsubscribe = None
        self.dirty = False
        if previous_unsubscribe is not None:
            previous_unsubscribe()

    def _subscribe(self, ref: ExternalStoreRef[Any]) -> None:
        self.unsubscribe = ref.subscribe(self._mark_dirty)

    def _mark_dirty(self) -> None:
        self.dirty = True
        self.host.mark_slot_call_refresh_only()

    def _update_from_get(self) -> bool:
        next_value = self.ref.get()
        dirty = (not self.initialized) or (next_value != self.value)
        self.value = next_value
        self.initialized = True
        return dirty


_EFFECT_DEPS_UNSET = object()


@dataclass(slots=True)
class UseEffectBinding(SlotCallBinding):
    host: SlotCallBindingHost
    request: UseEffectRequest | None = None
    cleanup: Callable[[], None] | None = None
    deps: object = _EFFECT_DEPS_UNSET
    staged_request: UseEffectRequest | None = None

    @classmethod
    def bind(
        cls,
        host: SlotCallBindingHost,
        request: UseEffectRequest,
    ) -> UseEffectBinding:
        binding = cls(host=host)
        binding.stage(request)
        return binding

    def exposed_value(self) -> None:
        return None

    def stage(self, request: UseEffectRequest) -> None:
        self.staged_request = request

    def commit(self) -> None:
        request = self.staged_request
        if request is None:
            return

        self.staged_request = None
        should_run = self._should_run(request)
        self.request = request
        self.deps = request.deps
        if should_run:
            self.host.enqueue_slot_call_post_commit(self._make_post_commit_callback(request))

    def rollback(self) -> None:
        self.staged_request = None

    def deactivate(self) -> None:
        self.staged_request = None
        cleanup = self.cleanup
        self.cleanup = None
        self.request = None
        self.deps = _EFFECT_DEPS_UNSET
        if cleanup is not None:
            cleanup()

    def _should_run(self, request: UseEffectRequest) -> bool:
        if self.request is None:
            return True
        if request.deps is None:
            return True
        return self.deps is _EFFECT_DEPS_UNSET or request.deps != self.deps

    def _make_post_commit_callback(self, request: UseEffectRequest) -> Callable[[], None]:
        def run_effect() -> None:
            cleanup = self.cleanup
            if cleanup is not None:
                self.cleanup = None
                cleanup()

            next_cleanup = request.effect_fn()
            if next_cleanup is not None and not callable(next_cleanup):
                raise TypeError("effect must return a cleanup callable or None")
            self.cleanup = cast("Callable[[], None] | None", next_cleanup)

        return run_effect


@dataclass(slots=True)
class UseEffectAsyncBinding(SlotCallBinding):
    host: SlotCallBindingHost
    request: UseEffectAsyncRequest | None = None
    deps: object = _EFFECT_DEPS_UNSET
    staged_request: UseEffectAsyncRequest | None = None
    handle: AsyncEffectHandle | None = None
    active_token: object | None = None
    cleanup: Callable[[], None] | None = None

    @classmethod
    def bind(
        cls,
        host: SlotCallBindingHost,
        request: UseEffectAsyncRequest,
    ) -> UseEffectAsyncBinding:
        binding = cls(host=host)
        binding.stage(request)
        return binding

    def exposed_value(self) -> None:
        return None

    def stage(self, request: UseEffectAsyncRequest) -> None:
        self.staged_request = request

    def commit(self) -> None:
        request = self.staged_request
        if request is None:
            return

        self.staged_request = None
        should_run = self._should_run(request)
        self.request = request
        self.deps = request.deps
        if should_run:
            self.host.enqueue_slot_call_post_commit(self._make_post_commit_callback(request))

    def rollback(self) -> None:
        self.staged_request = None

    def deactivate(self) -> None:
        self.staged_request = None
        self.request = None
        self.deps = _EFFECT_DEPS_UNSET
        self._teardown_active()

    def _should_run(self, request: UseEffectAsyncRequest) -> bool:
        if self.request is None:
            return True
        if request.deps is None:
            return True
        return self.deps is _EFFECT_DEPS_UNSET or request.deps != self.deps

    def _make_post_commit_callback(self, request: UseEffectAsyncRequest) -> Callable[[], None]:
        def start_effect() -> None:
            self._teardown_active()
            self.cleanup = request.cleanup
            token = object()
            self.active_token = token

            def on_complete() -> None:
                if self.active_token is not token:
                    return
                self.handle = None
                self.host.queue_slot_call_invalidation()

            self.handle = request.start(on_complete)

        return start_effect

    def _teardown_active(self) -> None:
        handle = self.handle
        self.handle = None
        self.active_token = None
        if handle is not None:
            handle.cancel()
        cleanup = self.cleanup
        self.cleanup = None
        if cleanup is not None:
            cleanup()


@dataclass(slots=True)
class PyrolyzeMountAdvertisementBinding(SlotCallBinding):
    host: SlotCallBindingHost
    request: PyrolyzeMountAdvertisementRequest | None = None
    staged_request: PyrolyzeMountAdvertisementRequest | None = None
    advertisement: PyrolyzeMountAdvertisement | None = None

    @classmethod
    def bind(
        cls,
        host: SlotCallBindingHost,
        request: PyrolyzeMountAdvertisementRequest,
    ) -> PyrolyzeMountAdvertisementBinding:
        binding = cls(host=host)
        binding.stage(request)
        return binding

    def exposed_value(self) -> PyrolyzeMountAdvertisementRequest | None:
        if self.staged_request is not None:
            return self.staged_request
        return self.request

    def stage(self, request: PyrolyzeMountAdvertisementRequest) -> None:
        self.staged_request = request

    def commit(self) -> None:
        request = self.staged_request
        if request is None:
            return
        self.advertisement = self.host.publish_slot_call_mount_advertisement(request)
        self.request = request
        self.staged_request = None

    def rollback(self) -> None:
        self.staged_request = None

    def deactivate(self) -> None:
        self.staged_request = None
        self.request = None
        self.advertisement = None
        self.host.withdraw_slot_call_mount_advertisement()

    def retained_advertisement(self) -> PyrolyzeMountAdvertisement | None:
        return self.advertisement


class SlotCallSemanticsHandler:
    def can_handle(self, result: object) -> bool:
        raise NotImplementedError

    def bind(
        self,
        host: SlotCallBindingHost,
        result: object,
        previous: SlotCallBinding | None,
    ) -> SlotCallBinding:
        raise NotImplementedError


class ExternalStoreHandler(SlotCallSemanticsHandler):
    def can_handle(self, result: object) -> bool:
        return isinstance(result, ExternalStoreRef)

    def bind(
        self,
        host: SlotCallBindingHost,
        result: object,
        previous: SlotCallBinding | None,
    ) -> SlotCallBinding:
        ref = cast(ExternalStoreRef[Any], result)
        if isinstance(previous, ExternalStoreBinding):
            previous.rebind(ref)
            return previous
        return ExternalStoreBinding.bind(host, ref)


class PyrolyzeMountAdvertisementHandler(SlotCallSemanticsHandler):
    def can_handle(self, result: object) -> bool:
        return isinstance(result, PyrolyzeMountAdvertisementRequest)

    def bind(
        self,
        host: SlotCallBindingHost,
        result: object,
        previous: SlotCallBinding | None,
    ) -> SlotCallBinding:
        request = cast(PyrolyzeMountAdvertisementRequest, result)
        if isinstance(previous, PyrolyzeMountAdvertisementBinding):
            previous.stage(request)
            return previous
        return PyrolyzeMountAdvertisementBinding.bind(host, request)


class SlotValueHandler(SlotCallSemanticsHandler):
    def can_handle(self, result: object) -> bool:
        return not isinstance(
            result,
            (
                ExternalStoreRef,
                PyrolyzeMountAdvertisementRequest,
                UseEffectRequest,
                UseEffectAsyncRequest,
            ),
        )

    def bind(
        self,
        host: SlotCallBindingHost,
        result: object,
        previous: SlotCallBinding | None,
    ) -> SlotCallBinding:
        if isinstance(previous, SlotValueBinding):
            previous.rebind(result)
            return previous
        return SlotValueBinding(value=result)


class UseEffectHandler(SlotCallSemanticsHandler):
    def can_handle(self, result: object) -> bool:
        return isinstance(result, UseEffectRequest)

    def bind(
        self,
        host: SlotCallBindingHost,
        result: object,
        previous: SlotCallBinding | None,
    ) -> SlotCallBinding:
        request = cast(UseEffectRequest, result)
        if isinstance(previous, UseEffectBinding):
            previous.stage(request)
            return previous
        return UseEffectBinding.bind(host, request)


class UseEffectAsyncHandler(SlotCallSemanticsHandler):
    def can_handle(self, result: object) -> bool:
        return isinstance(result, UseEffectAsyncRequest)

    def bind(
        self,
        host: SlotCallBindingHost,
        result: object,
        previous: SlotCallBinding | None,
    ) -> SlotCallBinding:
        request = cast(UseEffectAsyncRequest, result)
        if isinstance(previous, UseEffectAsyncBinding):
            previous.stage(request)
            return previous
        return UseEffectAsyncBinding.bind(host, request)


SLOT_CALL_HANDLERS: tuple[SlotCallSemanticsHandler, ...] = (
    ExternalStoreHandler(),
    PyrolyzeMountAdvertisementHandler(),
    UseEffectAsyncHandler(),
    UseEffectHandler(),
    SlotValueHandler(),
)


def select_slot_call_handler(result: object) -> SlotCallSemanticsHandler:
    matches = [handler for handler in SLOT_CALL_HANDLERS if handler.can_handle(result)]
    if len(matches) != 1:
        raise TypeError(f"slot-call result matched {len(matches)} handlers instead of exactly one")
    return matches[0]
