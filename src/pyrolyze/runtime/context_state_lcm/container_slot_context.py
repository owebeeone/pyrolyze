from __future__ import annotations

from .context_base import PASS_TX_KEY
from .lifecycle_adapter import local_store, managed, managed_context
from .rerunnable_slot_context import RerunnableSlotContextStateMgr


@managed_context
class ContainerSlotContextStateMgr(RerunnableSlotContextStateMgr):
    _expects_native_root: bool = local_store(default=False)
    _committed_native_root: bool = managed(
        default=False, init=False, tx_key=PASS_TX_KEY
    )
