from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from pyrolyze.hooks import use_state
from pyrolyze.runtime import (
    ModuleRegistry,
    RenderContext,
    SlotId,
    TraceChannel,
    TraceRecord,
    UiBackendAdapter,
    UiNode,
    UiNodeBinding,
    UiNodeId,
    UiNodeSpec,
    UiOwnerCommitState,
    configure_trace,
    emit_trace,
    reconcile_owner,
    reset_trace,
    trace_enabled,
)


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.runtime_trace")
_STATE_SLOT = SlotId(_MODULE_ID, 1, line_no=10, is_top_level=True)
_OWNER_SLOT = SlotId(_MODULE_ID, 2, line_no=11, is_top_level=True)


def _button_spec(node_id: UiNodeId, *, label: str = "Run") -> UiNodeSpec:
    return UiNodeSpec(
        node_id=node_id,
        kind="button",
        props={"label": label, "enabled": True, "tone": "default", "visible": True},
        event_props={"on_press": None},
    )


@dataclass
class _TraceBinding(UiNodeBinding):
    spec: UiNodeSpec
    attached: list[UiNode] = field(default_factory=list)

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: dict[str, Any],
        changed_events: dict[str, Callable[..., None] | None],
    ) -> None:
        self.spec = next_spec

    def place_child(self, child: UiNode, index: int) -> None:
        if child in self.attached:
            self.attached.remove(child)
        self.attached.insert(index, child)

    def detach_child(self, child: UiNode) -> None:
        if child in self.attached:
            self.attached.remove(child)

    def dispose(self) -> None:
        self.attached.clear()


@dataclass
class _TraceBackend(UiBackendAdapter):
    backend_id: str = "trace-test"

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        parent_binding: Any | None,
    ) -> _TraceBinding:
        del parent_binding
        return _TraceBinding(spec=spec)

    def can_reuse(self, current: UiNode, next_spec: UiNodeSpec) -> bool:
        return current.spec.kind == next_spec.kind

    def assert_ui_thread(self) -> None:
        return None

    def post_to_ui(self, callback: Callable[[], None]) -> None:
        callback()


def test_trace_controller_emits_only_enabled_channels() -> None:
    records: list[TraceRecord] = []
    reset_trace()
    try:
        configure_trace(enabled={TraceChannel.INVALIDATION}, sink=records.append)

        emit_trace(TraceChannel.INVALIDATION, "queued", slot="state")
        emit_trace(TraceChannel.RECONCILE, "owner_commit", owner="root")

        assert trace_enabled(TraceChannel.INVALIDATION) is True
        assert trace_enabled(TraceChannel.RECONCILE) is False
        assert records == [
            TraceRecord(
                channel=TraceChannel.INVALIDATION,
                event="queued",
                fields={"slot": "state"},
            )
        ]
    finally:
        reset_trace()


def test_render_context_emits_invalidation_flush_and_boundary_records() -> None:
    records: list[TraceRecord] = []
    setters: list[Callable[[int], None]] = []
    ctx = RenderContext()
    reset_trace()
    try:
        configure_trace(
            enabled={
                TraceChannel.INVALIDATION,
                TraceChannel.FLUSH,
                TraceChannel.BOUNDARY,
            },
            sink=records.append,
        )

        def render() -> None:
            with ctx.pass_scope():
                _, pair = ctx.call_plain(
                    _STATE_SLOT,
                    use_state,
                    0,
                    result_shape=("tuple", 2),
                )
                _count, setter = pair
                setters[:] = [setter]

        ctx.mount(render)
        records.clear()

        setters[0](1)
        ctx.run_pending_invalidations()

        invalidation = [record for record in records if record.channel == TraceChannel.INVALIDATION]
        flush = [record for record in records if record.channel == TraceChannel.FLUSH]
        boundary = [record for record in records if record.channel == TraceChannel.BOUNDARY]

        assert [record.event for record in invalidation] == ["queued"]
        assert invalidation[0].fields["source_slot"] == _STATE_SLOT
        assert [record.event for record in flush] == ["start", "end"]
        assert [record.event for record in boundary] == ["start", "end"]
    finally:
        reset_trace()


def test_reconcile_owner_emits_summary_trace_record() -> None:
    records: list[TraceRecord] = []
    backend = _TraceBackend()
    owner = UiOwnerCommitState(owner_id=_OWNER_SLOT)
    parent = _TraceBinding(spec=_button_spec(UiNodeId(owner_slot_id=_OWNER_SLOT, region_index=99)))
    reset_trace()
    try:
        configure_trace(enabled={TraceChannel.RECONCILE}, sink=records.append)

        reconcile_owner(
            owner,
            (_button_spec(UiNodeId(owner_slot_id=_OWNER_SLOT, region_index=1)),),
            backend=backend,
            parent_binding=parent,
        )

        assert records == [
            TraceRecord(
                channel=TraceChannel.RECONCILE,
                event="owner_commit",
                fields={
                    "owner_id": _OWNER_SLOT,
                    "previous_count": 0,
                    "next_count": 1,
                    "created": 1,
                    "reused": 0,
                    "updated": 0,
                    "replaced": 0,
                    "removed": 0,
                },
            )
        ]
    finally:
        reset_trace()
