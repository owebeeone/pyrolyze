from __future__ import annotations

from dataclasses import dataclass

from Studio.app.models import StudioState
from Studio.app.reducers import create_initial_state


@dataclass(slots=True)
class Store:
    value: StudioState

    @classmethod
    def create(cls, start_root: str = "") -> "Store":
        return cls(value=create_initial_state(start_root))
