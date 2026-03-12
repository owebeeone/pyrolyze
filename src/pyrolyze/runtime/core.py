"""Runtime core primitives: state vars and scheduler."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class StateVar:
    """Mutable reactive state cell with subscriber lifecycle handling."""

    value: Any
    _subscribers: list[Callable[[Any], None]] = field(default_factory=list)

    def set(self, value: Any) -> None:
        self.value = value
        for subscriber in list(self._subscribers):
            subscriber(value)

    def subscribe(self, callback: Callable[[Any], None]) -> Callable[[], None]:
        self._subscribers.append(callback)

        def _unsubscribe() -> None:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

        return _unsubscribe


@dataclass
class Scheduler:
    """Deterministic scheduler with per-cycle dedupe and thread marshaling."""

    main_thread_id: Any
    _main_queue: list[Callable[[], None]] = field(default_factory=list)
    _off_thread_queue: list[Callable[[], None]] = field(default_factory=list)

    def invalidate(self, callback: Callable[[], None], *, origin_thread_id: Any) -> None:
        if origin_thread_id == self.main_thread_id:
            self._enqueue_unique(self._main_queue, callback)
            return

        self._enqueue_unique(self._off_thread_queue, callback)

    def flush_current_thread(self, *, current_thread_id: Any) -> None:
        if current_thread_id == self.main_thread_id:
            self.flush_main_thread()

    def flush_main_thread(self) -> None:
        for callback in self._off_thread_queue:
            self._enqueue_unique(self._main_queue, callback)
        self._off_thread_queue.clear()

        pending = list(self._main_queue)
        self._main_queue.clear()

        for callback in pending:
            callback()

    @staticmethod
    def _enqueue_unique(queue: list[Callable[[], None]], callback: Callable[[], None]) -> None:
        if callback in queue:
            return
        queue.append(callback)


__all__ = ["Scheduler", "StateVar"]
