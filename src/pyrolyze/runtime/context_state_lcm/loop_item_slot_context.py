from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .rerunnable_slot_context import RerunnableSlotContextStateMgr
from ._support import _SlotCallResult, _structured_dirty_projection
from .context_base import PASS_TX_KEY
from .field_only_render import _field_only_completion
from .lifecycle_adapter import local_store, managed, managed_context


@dataclass(frozen=True, slots=True)
class _LoopItemSelection:
    value: Any = None
    dirty: Any = True
    initialized: bool = False


@managed_context
class LoopItemSlotContextStateMgr(RerunnableSlotContextStateMgr):
    _selection: _LoopItemSelection = managed(
        default_factory=_LoopItemSelection, compare="identity", tx_key=PASS_TX_KEY
    )
    _legacy_selection: _LoopItemSelection = local_store(
        default_factory=_LoopItemSelection
    )

    def _selection_record(self) -> _LoopItemSelection:
        if getattr(_field_only_completion(self), "keyed_loop_selection_enabled", False):
            return self._selection
        return self._legacy_selection

    def current_value(self) -> Any:
        self.require_active_scope()
        selection = self._selection_record()
        return _SlotCallResult(
            dirty=selection.dirty,
            value=selection.value,
        )

    def update_current(self, value: Any) -> None:
        completion = _field_only_completion(self)
        owner = None
        if getattr(completion, "keyed_loop_selection_enabled", False):
            completion.require_resource_owner()
            owner = completion.active
        selection = self._selection_record()
        dirty = _structured_dirty_projection(
            previous=selection.value,
            current=value,
            initialized=selection.initialized,
        )
        record = _LoopItemSelection(value, dirty, True)
        if owner is not None:
            owner._require_open()
            owner._require_identity()
            self._selection = record
        else:
            self._legacy_selection = record
