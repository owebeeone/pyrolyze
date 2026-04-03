from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Generic, TypeVar

from pyrolyze.runtime import ExternalStoreRef


T = TypeVar("T")


@dataclass(slots=True)
class StoreProbe(Generic[T]):
    key: str
    initial_value: T
    log: list[tuple[object, ...]]
    value: T = field(init=False)
    listeners: list[Callable[[], None]] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.value = self.initial_value

    def ref(self) -> ExternalStoreRef[T]:
        return ExternalStoreRef(
            identity=self.key,
            subscribe=self.subscribe,
            get=self.get,
        )

    def subscribe(self, listener: Callable[[], None]) -> Callable[[], None]:
        self.log.append(("subscribe", self.key))
        self.listeners.append(listener)
        active = True

        def unsubscribe() -> None:
            nonlocal active
            if not active:
                return
            active = False
            self.log.append(("unsubscribe", self.key))
            self.listeners.remove(listener)

        return unsubscribe

    def get(self) -> T:
        self.log.append(("get", self.key, self.value))
        return self.value

    def notify(self, value: T) -> None:
        self.value = value
        for listener in list(self.listeners):
            listener()
