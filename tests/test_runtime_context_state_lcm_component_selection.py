from __future__ import annotations

import pytest
from typing import Any

from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.component_render import _enable_component_render
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY


def test_rerun_captures_argument_values_before_preparation_reentry(
    monkeypatch: Any,
) -> None:
    from pyrolyze.runtime.context_state_lcm import component_call_slot_context
    from pyrolyze.runtime.context_state_lcm._support import dirtyof

    root = runtime.RenderContext()
    _enable_component_render(root._state_mgr)
    slot_id = runtime.SlotId(runtime.ModuleId("rerun-snapshot"), 1)
    observed: list[int] = []

    def render(context: Any, dirty: Any, value: int) -> None:
        with context.pass_scope():
            observed.append(value)

    with root.pass_scope():
        slot = root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
        slot.invoke(render, (1,), {}, dirty_state=dirtyof(value=True))

    def clean(previous: Any) -> Any:
        slot._state_mgr._call_author_args = (2,)
        return dirtyof(value=False)

    monkeypatch.setattr(component_call_slot_context, "_clean_dirty_state", clean)
    with root.pass_scope():
        root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
        slot._state_mgr._rerun_child()
    assert observed == [1, 1]
    assert slot._state_mgr.current._call_author_args == (2,)


def test_argument_conversion_cannot_stage_into_replacement_transaction() -> None:
    root = runtime.RenderContext()
    _enable_component_render(root._state_mgr)
    slot_id = runtime.SlotId(runtime.ModuleId("conversion-token"), 1)

    def render(context: Any, value: Any) -> None:
        with context.pass_scope():
            pass

    with root.pass_scope():
        slot = root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
        slot.invoke(render, (1,), {})
    manager = root._state_mgr._transaction_manager
    replacement: Any = None

    class Argument:
        def to_frozen(self) -> int:
            nonlocal replacement
            manager.rollback(PASS_TX_KEY)
            replacement = manager.begin(PASS_TX_KEY)
            return 2

    try:
        with pytest.raises(RuntimeError, match="missing or replaced"):
            with root.pass_scope():
                root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
                slot.invoke(render, (Argument(),), {})
        assert manager.active_transaction_for(PASS_TX_KEY) is replacement
        assert id(slot._state_mgr._y_state) not in replacement.dirty_contexts
        assert slot._state_mgr.current._call_args == (1,)
    finally:
        manager.rollback(PASS_TX_KEY)


def test_failed_initial_selection_is_not_retained() -> None:
    root = runtime.RenderContext()
    _enable_component_render(root._state_mgr)
    retained = []
    with pytest.raises(ValueError, match="discard"):
        with root.pass_scope():
            slot = root._ensure_slot(
                runtime.SlotId(runtime.ModuleId("component-selection"), 1),
                runtime.ComponentCallSlotContext,
            )
            slot.invoke(lambda context: None, (), {})
            retained.append(slot)
            assert slot.child_context is not None
            assert slot._state_mgr.current._selection.child is None
            raise ValueError("discard")
    assert retained[0].child_context is None
    assert root._state_mgr.current.children_state == {}


def test_factory_failure_does_not_install_partial_selection() -> None:
    root = runtime.RenderContext()
    _enable_component_render(root._state_mgr)
    retained = []

    def fail_factory(**kwargs: object) -> object:
        raise ValueError("factory failed")

    with pytest.raises(ValueError, match="factory failed"):
        with root.pass_scope():
            slot = root._ensure_slot(
                runtime.SlotId(runtime.ModuleId("component-selection"), 1),
                runtime.ComponentCallSlotContext,
            )
            retained.append(slot)
            slot._state_mgr.invoke(
                lambda context: None, (), {}, render_context_factory=fail_factory
            )
    selection = retained[0]._state_mgr.current._selection
    assert (selection.identity, selection.schema, selection.child) == (
        None,
        (0, ()),
        None,
    )


def test_failed_replacement_preserves_accepted_child() -> None:
    root = runtime.RenderContext()
    _enable_component_render(root._state_mgr)
    slot_id = runtime.SlotId(runtime.ModuleId("component-selection"), 1)

    def render(context: object) -> None:
        pass

    with root.pass_scope():
        slot = root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
        slot.invoke(render, (), {})
    child = slot.child_context
    accepted = slot._state_mgr.current._selection
    candidates = []

    def fail(context: object) -> None:
        candidates.append(context)
        raise ValueError("replacement failed")

    with pytest.raises(ValueError, match="replacement failed"):
        with root.pass_scope():
            root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
            slot.invoke(fail, (), {})
    assert slot.child_context is child
    assert slot._state_mgr.current._selection is accepted
    assert candidates[0]._state_mgr._mounted_callback is None


def test_failed_candidate_cleanup_drains_subscriptions() -> None:
    from pyrolyze.runtime.slot_call_semantics import ExternalStoreRef

    root = runtime.RenderContext()
    _enable_component_render(root._state_mgr)
    events = []

    def render(context: object) -> None:
        with context.pass_scope():
            binding = context._ensure_slot(
                runtime.SlotId(runtime.ModuleId("component-selection"), 2),
                runtime.SlotCallSlotContext,
            )
            binding.evaluate(
                lambda: ExternalStoreRef(
                    "candidate",
                    lambda callback: lambda: events.append("unsubscribe"),
                    lambda: 1,
                ),
                (),
                {},
            )

    with pytest.raises(ValueError, match="discard"):
        with root.pass_scope():
            slot = root._ensure_slot(
                runtime.SlotId(runtime.ModuleId("component-selection"), 1),
                runtime.ComponentCallSlotContext,
            )
            slot.invoke(render, (), {})
            candidate = slot.child_context
            raise ValueError("discard")
    assert events == ["unsubscribe"]
    assert candidate._state_mgr._mounted_callback is None


def test_explicit_retirement_is_discarded_with_parent_failure() -> None:
    root = runtime.RenderContext()
    _enable_component_render(root._state_mgr)
    slot_id = runtime.SlotId(runtime.ModuleId("component-selection"), 1)
    with root.pass_scope():
        slot = root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
        slot.invoke(lambda context: None, (), {})
    child = slot.child_context
    with pytest.raises(ValueError, match="discard retirement"):
        with root.pass_scope():
            root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
            slot.deactivate()
            assert child._state_mgr._mounted_callback is not None
            raise ValueError("discard retirement")
    assert slot.child_context is child
    assert child._state_mgr._mounted_callback is not None


def test_retirement_cleanup_failure_keeps_publication_and_detaches_child() -> None:
    from pyrolyze.runtime.slot_call_semantics import ExternalStoreRef

    root = runtime.RenderContext()
    _enable_component_render(root._state_mgr)
    events = []
    error = ValueError("unsubscribe failed")

    def render(context: object) -> None:
        with context.pass_scope():
            for index in (2, 3):
                binding = context._ensure_slot(
                    runtime.SlotId(runtime.ModuleId("component-selection"), index),
                    runtime.SlotCallSlotContext,
                )

                def cleanup(index: int = index) -> None:
                    events.append(index)
                    if index == 2:
                        raise error

                binding.evaluate(
                    lambda: ExternalStoreRef(
                        index, lambda callback: cleanup, lambda: 1
                    ),
                    (),
                    {},
                )

    with root.pass_scope():
        slot = root._ensure_slot(
            runtime.SlotId(runtime.ModuleId("component-selection"), 1),
            runtime.ComponentCallSlotContext,
        )
        slot.invoke(render, (), {})
    child = slot.child_context
    with pytest.raises(ValueError) as caught:
        with root.pass_scope():
            pass
    assert caught.value is error
    assert events == [2, 3]
    assert child._state_mgr._mounted_callback is None
    assert slot.child_context is None
    completion = root._state_mgr._field_only_completion
    assert completion.last.published is True
    with pytest.raises(RuntimeError, match="not ready"):
        with root.pass_scope():
            pass
