"""Adapter registry and SDK primitives for external store integration."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import count
from typing import Any, Callable

from .dispatcher import get_active_runtime


class AdapterError(RuntimeError):
    """Base adapter error with stable machine-readable code."""

    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


class AdapterRegistrationError(AdapterError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="PYR-E-ADAPTER-DUP")


class AdapterNotFoundError(AdapterError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="PYR-E-ADAPTER-NOT-FOUND")


class AdapterProtocolError(AdapterError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="PYR-E-ADAPTER-PROTOCOL")


class AdapterResolutionError(AdapterError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="PYR-E-ADAPTER-RESOLVE")


@dataclass(frozen=True)
class AdapterRegistryRecord:
    name: str
    matcher: Callable[[Any], int | None]
    adapter_factory: Callable[[], Any]
    order: int


_REGISTRY: dict[str, AdapterRegistryRecord] = {}
_ORDER_COUNTER = count(1)
_REGISTRY_LISTENERS: list[Callable[[str, str], None]] = []



def register_store_adapter(
    name: str,
    matcher: Callable[[Any], int | None],
    adapter_factory: Callable[[], Any],
) -> AdapterRegistryRecord:
    """Register an adapter with deterministic ordering semantics."""
    if name in _REGISTRY:
        raise AdapterRegistrationError(f"Adapter '{name}' is already registered.")

    if not callable(matcher):
        raise AdapterProtocolError("Adapter matcher must be callable.")

    if not callable(adapter_factory):
        raise AdapterProtocolError("adapter_factory must be callable.")

    adapter = adapter_factory()
    _validate_adapter_protocol(adapter)

    record = AdapterRegistryRecord(
        name=name,
        matcher=matcher,
        adapter_factory=adapter_factory,
        order=next(_ORDER_COUNTER),
    )
    _REGISTRY[name] = record
    _notify_registry_listeners(event="registered", adapter_name=name)
    return record



def unregister_store_adapter(name: str) -> None:
    if name not in _REGISTRY:
        raise AdapterNotFoundError(f"Adapter '{name}' is not registered.")
    del _REGISTRY[name]
    _notify_registry_listeners(event="unregistered", adapter_name=name)



def list_store_adapters() -> list[AdapterRegistryRecord]:
    return sorted(_REGISTRY.values(), key=lambda record: record.order)



def create_store_hook(adapter_name: str, hook_name: str | None = None) -> Callable[..., Any]:
    record = _get_record(adapter_name)

    generated_name = hook_name or f"use_{adapter_name}"

    def _generated_hook(source: Any, ctx: Any | None = None, adapter: Any | None = None) -> Any:
        runtime = get_active_runtime()
        selected_adapter = adapter if adapter is not None else record.name
        return runtime.use_store(source, ctx=ctx, adapter=selected_adapter)

    _generated_hook.__name__ = generated_name
    _generated_hook.__qualname__ = generated_name
    setattr(_generated_hook, "__pyrolyze_adapter_name__", record.name)
    return _generated_hook



def resolve_store_adapter(source: Any, explicit_adapter: str | None = None) -> AdapterRegistryRecord:
    """Resolve adapter by explicit choice or highest matcher score."""
    if explicit_adapter is not None:
        return _get_record(explicit_adapter)

    best: AdapterRegistryRecord | None = None
    best_score: int | None = None

    for record in list_store_adapters():
        try:
            score = record.matcher(source)
        except Exception as exc:
            raise AdapterResolutionError(
                f"Matcher for adapter '{record.name}' raised an exception: {exc}"
            ) from exc

        if score is None:
            continue

        if not isinstance(score, int):
            raise AdapterProtocolError(
                f"Matcher for adapter '{record.name}' must return int or None."
            )

        if best is None or score > int(best_score):
            best = record
            best_score = score

    if best is None:
        raise AdapterResolutionError("No adapter matched the provided source.")

    return best



def subscribe_adapter_registry_events(listener: Callable[[str, str], None]) -> Callable[[], None]:
    _REGISTRY_LISTENERS.append(listener)

    def _unsubscribe() -> None:
        if listener in _REGISTRY_LISTENERS:
            _REGISTRY_LISTENERS.remove(listener)

    return _unsubscribe



def _notify_registry_listeners(*, event: str, adapter_name: str) -> None:
    for listener in list(_REGISTRY_LISTENERS):
        listener(event, adapter_name)



def _get_record(name: str) -> AdapterRegistryRecord:
    if name not in _REGISTRY:
        raise AdapterNotFoundError(f"Adapter '{name}' is not registered.")
    return _REGISTRY[name]



def _validate_adapter_protocol(adapter: Any) -> None:
    required_methods = ("resolve_producer", "get_snapshot", "subscribe")
    for method_name in required_methods:
        method = getattr(adapter, method_name, None)
        if not callable(method):
            raise AdapterProtocolError(
                f"Adapter missing required callable '{method_name}'."
            )


__all__ = [
    "AdapterNotFoundError",
    "AdapterProtocolError",
    "AdapterRegistrationError",
    "AdapterResolutionError",
    "AdapterRegistryRecord",
    "create_store_hook",
    "list_store_adapters",
    "register_store_adapter",
    "resolve_store_adapter",
    "subscribe_adapter_registry_events",
    "unregister_store_adapter",
]
