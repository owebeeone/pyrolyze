"""Hook runtime primitives for state/effect/lifecycle semantics."""

from __future__ import annotations

import asyncio
import inspect
from contextvars import Token
from dataclasses import dataclass, field
from typing import Any, Callable

from .core import StateVar
from .dispatcher import reset_active_runtime, set_active_runtime
from .external_store import ExternalStoreBinding



def _noop_invalidate() -> None:
    return None


@dataclass
class _EffectSlot:
    deps: tuple[Any, ...] | None = None
    cleanup: Callable[[], None] | None = None
    initialized: bool = False


@dataclass
class _ExternalStoreSlot:
    subscribe_fn: Callable[[Callable[[], None]], Callable[[], None]]
    get_snapshot_fn: Callable[[], Any]
    get_version_fn: Callable[[], Any] | None
    is_equal_fn: Callable[[Any, Any], bool] | None
    unsubscribe: Callable[[], None] | None = None
    snapshot: Any = None
    version: Any = None
    initialized: bool = False

    def equals(self, left: Any, right: Any) -> bool:
        if callable(self.is_equal_fn):
            return bool(self.is_equal_fn(left, right))
        return left == right


@dataclass
class _StoreSlot:
    binding: ExternalStoreBinding
    initialized: bool = False


@dataclass
class ComponentHooksRuntime:
    """Per-component hook runtime with deterministic slot ordering."""

    runtime_ctx: Any = None
    invalidate: Callable[[], None] = _noop_invalidate

    _state_slots: list[StateVar] = field(default_factory=list)
    _effect_slots: list[_EffectSlot] = field(default_factory=list)
    _mount_slots: list[Callable[[], None]] = field(default_factory=list)
    _unmount_slots: list[Callable[[], None]] = field(default_factory=list)
    _external_store_slots: list[_ExternalStoreSlot] = field(default_factory=list)
    _store_slots: list[_StoreSlot] = field(default_factory=list)

    _state_index: int = 0
    _effect_index: int = 0
    _mount_index: int = 0
    _unmount_index: int = 0
    _external_store_index: int = 0
    _store_index: int = 0

    _mount_executed: bool = False
    _runtime_token: Token[Any | None] | None = None

    def begin_render(self) -> None:
        self._clear_active_runtime()
        self._runtime_token = set_active_runtime(self)

        self._state_index = 0
        self._effect_index = 0
        self._mount_index = 0
        self._unmount_index = 0
        self._external_store_index = 0
        self._store_index = 0

    def end_render(self) -> None:
        try:
            if self._mount_executed:
                return

            for mount_hook in self._mount_slots:
                mount_hook()
            self._mount_executed = True
        finally:
            self._clear_active_runtime()

    def use_state(self, initial: Any) -> tuple[Any, Callable[[Any], None]]:
        if self._state_index == len(self._state_slots):
            self._state_slots.append(StateVar(initial))

        slot = self._state_slots[self._state_index]
        self._state_index += 1
        return slot.value, slot.set

    def use_effect(self, effect_fn: Callable[[], Any], *, deps: list[Any]) -> None:
        if self._effect_index == len(self._effect_slots):
            self._effect_slots.append(_EffectSlot())

        slot = self._effect_slots[self._effect_index]
        self._effect_index += 1

        next_deps = tuple(deps)
        changed = (not slot.initialized) or (slot.deps != next_deps)
        if not changed:
            return

        if callable(slot.cleanup):
            slot.cleanup()
            slot.cleanup = None

        result = effect_fn()
        if inspect.isawaitable(result):
            asyncio.run(result)
            result = None

        if callable(result):
            slot.cleanup = result

        slot.deps = next_deps
        slot.initialized = True

    def use_mount(self, fn: Callable[[], None]) -> None:
        if self._mount_index == len(self._mount_slots):
            self._mount_slots.append(fn)
        else:
            self._mount_slots[self._mount_index] = fn
        self._mount_index += 1

    def use_unmount(self, fn: Callable[[], None]) -> None:
        if self._unmount_index == len(self._unmount_slots):
            self._unmount_slots.append(fn)
        else:
            self._unmount_slots[self._unmount_index] = fn
        self._unmount_index += 1

    def use_external_store(
        self,
        subscribe: Callable[[Callable[[], None]], Callable[[], None]],
        get_snapshot: Callable[[], Any],
        get_version: Callable[[], Any] | None = None,
        is_equal: Callable[[Any, Any], bool] | None = None,
    ) -> Any:
        if self._external_store_index == len(self._external_store_slots):
            slot = _ExternalStoreSlot(
                subscribe_fn=subscribe,
                get_snapshot_fn=get_snapshot,
                get_version_fn=get_version,
                is_equal_fn=is_equal,
            )
            self._external_store_slots.append(slot)
            self._wire_external_store_slot(slot)
        else:
            slot = self._external_store_slots[self._external_store_index]
            if (
                slot.subscribe_fn is not subscribe
                or slot.get_snapshot_fn is not get_snapshot
                or slot.get_version_fn is not get_version
                or slot.is_equal_fn is not is_equal
            ):
                self._dispose_external_store_slot(slot)
                slot.subscribe_fn = subscribe
                slot.get_snapshot_fn = get_snapshot
                slot.get_version_fn = get_version
                slot.is_equal_fn = is_equal
                slot.snapshot = None
                slot.version = None
                slot.initialized = False
                self._wire_external_store_slot(slot)

        self._external_store_index += 1

        current_snapshot = slot.get_snapshot_fn()
        current_version = slot.get_version_fn() if callable(slot.get_version_fn) else None

        if not slot.initialized or not slot.equals(slot.snapshot, current_snapshot):
            slot.snapshot = current_snapshot
        slot.version = current_version
        slot.initialized = True
        return slot.snapshot

    def use_store(self, source: Any, *, ctx: Any = None, adapter: str | None = None) -> Any:
        if self._store_index == len(self._store_slots):
            slot = _StoreSlot(
                binding=ExternalStoreBinding(invalidate=self.invalidate, runtime_ctx=self.runtime_ctx)
            )
            self._store_slots.append(slot)
        else:
            slot = self._store_slots[self._store_index]

        self._store_index += 1

        if not slot.initialized:
            slot.initialized = True
            return slot.binding.bind(source=source, ctx=ctx, adapter=adapter)

        return slot.binding.update_inputs(source=source, ctx=ctx, adapter=adapter)

    def unmount(self) -> None:
        for slot in self._effect_slots:
            if callable(slot.cleanup):
                slot.cleanup()
                slot.cleanup = None

        for slot in self._external_store_slots:
            self._dispose_external_store_slot(slot)

        for slot in self._store_slots:
            slot.binding.unbind()

        for unmount_hook in self._unmount_slots:
            unmount_hook()

        self._clear_active_runtime()

    def _wire_external_store_slot(self, slot: _ExternalStoreSlot) -> None:
        slot.snapshot = slot.get_snapshot_fn()
        slot.version = slot.get_version_fn() if callable(slot.get_version_fn) else None
        slot.initialized = True

        def _listener() -> None:
            next_snapshot = slot.get_snapshot_fn()
            next_version = slot.get_version_fn() if callable(slot.get_version_fn) else None

            if slot.initialized:
                if callable(slot.get_version_fn) and next_version == slot.version:
                    return

                if slot.equals(slot.snapshot, next_snapshot):
                    slot.version = next_version
                    return

            slot.snapshot = next_snapshot
            slot.version = next_version
            slot.initialized = True
            self.invalidate()

        slot.unsubscribe = slot.subscribe_fn(_listener)

    @staticmethod
    def _dispose_external_store_slot(slot: _ExternalStoreSlot) -> None:
        if callable(slot.unsubscribe):
            slot.unsubscribe()
        slot.unsubscribe = None

    def _clear_active_runtime(self) -> None:
        if self._runtime_token is not None:
            reset_active_runtime(self._runtime_token)
            self._runtime_token = None


__all__ = ["ComponentHooksRuntime"]
