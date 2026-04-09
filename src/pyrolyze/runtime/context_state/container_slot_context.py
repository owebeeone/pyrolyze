from __future__ import annotations

from .rerunnable_slot_context import RerunnableSlotContextStateMgr


class ContainerSlotContextStateMgr(RerunnableSlotContextStateMgr):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.owner.expects_native_root = False
        self.owner.committed_native_root = False
        self.owner._pass_committed_native_root = False
        self.owner.site_metadata = ()
