"""External store binding lifecycle orchestration for adapter-based sources."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .adapters import (
    AdapterResolutionError,
    resolve_store_adapter,
    subscribe_adapter_registry_events,
)


@dataclass
class ExternalStoreBinding:
    """Manage source/ctx/adapter subscription lifecycle for one hook slot."""

    invalidate: Callable[[], None]
    runtime_ctx: Any = None

    _source: Any = None
    _ctx: Any = None
    _adapter_name: str | None = None
    _resolved_adapter_name: str | None = None
    _adapter_instance: Any = None
    _producer: Any = None
    _unsubscribe: Callable[[], None] | None = None
    _registry_unsubscribe: Callable[[], None] | None = None
    _snapshot: Any = None

    def bind(self, *, source: Any, ctx: Any = None, adapter: str | None = None) -> Any:
        self._source = source
        self._ctx = ctx
        self._adapter_name = adapter
        self._ensure_registry_listener()
        self._rebind()
        return self._snapshot

    def update_inputs(self, *, source: Any, ctx: Any = None, adapter: str | None = None) -> Any:
        if source is self._source and ctx == self._ctx and adapter == self._adapter_name:
            return self._snapshot

        self._source = source
        self._ctx = ctx
        self._adapter_name = adapter
        self._rebind()
        return self._snapshot

    def get_snapshot(self) -> Any:
        return self._snapshot

    def unbind(self) -> None:
        self._clear_store_subscription()

        if callable(self._registry_unsubscribe):
            self._registry_unsubscribe()
        self._registry_unsubscribe = None

    def _rebind(self) -> None:
        self._clear_store_subscription()

        record = resolve_store_adapter(self._source, explicit_adapter=self._adapter_name)
        adapter = record.adapter_factory()
        self._adapter_instance = adapter
        self._resolved_adapter_name = record.name

        normalized_ctx = self._ctx
        normalize_context = getattr(adapter, "normalize_context", None)
        if callable(normalize_context):
            normalized_ctx = normalize_context(self._ctx)

        producer = adapter.resolve_producer(self._source, self.runtime_ctx, normalized_ctx)
        self._producer = producer

        if producer is None:
            get_default = getattr(adapter, "get_default", None)
            self._snapshot = get_default(self._source) if callable(get_default) else None
            return

        self._snapshot = adapter.get_snapshot(producer)

        def _listener() -> None:
            self._snapshot = adapter.get_snapshot(producer)
            self.invalidate()

        self._unsubscribe = adapter.subscribe(producer, _listener)

    def _clear_store_subscription(self) -> None:
        if callable(self._unsubscribe):
            self._unsubscribe()
        self._unsubscribe = None
        self._producer = None
        self._adapter_instance = None

    def _ensure_registry_listener(self) -> None:
        if callable(self._registry_unsubscribe):
            return

        def _on_registry_change(event: str, adapter_name: str) -> None:
            del event
            if self._source is None:
                return

            if self._adapter_name is not None and adapter_name != self._adapter_name:
                return

            previous_snapshot = self._snapshot
            previous_resolved_name = self._resolved_adapter_name

            try:
                self._rebind()
            except AdapterResolutionError:
                self._clear_store_subscription()
                self._resolved_adapter_name = None
                self._snapshot = None

            if self._snapshot != previous_snapshot or self._resolved_adapter_name != previous_resolved_name:
                self.invalidate()

        self._registry_unsubscribe = subscribe_adapter_registry_events(_on_registry_change)


__all__ = ["ExternalStoreBinding"]
