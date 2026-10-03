from __future__ import annotations

from typing import Any

import pytest

from pyrolyze.api import UIElement
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.field_only_render import (
    _enable_field_only_render,
)
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted


def _root() -> Any:
    root = runtime.RenderContext()
    _enable_field_only_render(root._state_mgr)
    return root


@pytest.mark.parametrize(
    "slot_type",
    (
        runtime.SlotExprSlotContext,
        runtime.SlotCallSlotContext,
        runtime.EventHandlerSlotContext,
        runtime.DirectiveSlotContext,
        runtime.AppContextOverrideSlotContext,
        runtime.ContainerSlotContext,
        runtime.KeyedLoopSlotContext,
    ),
)
def test_gate_rejects_resource_slots_before_construction(slot_type: type[Any]) -> None:
    root = _root()
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            with pytest.raises(RuntimeError, match="not admitted"):
                slot_type(root, root, runtime.SlotId(runtime.ModuleId("gate"), 1))
    assert root._slots_by_id == {}
    assert root._state_mgr.current.children_state == {}


def test_late_activation_rejected_even_after_empty_legacy_pass() -> None:
    root = runtime.RenderContext()
    with root.pass_scope():
        pass
    with pytest.raises(RuntimeError, match="fresh graph"):
        _enable_field_only_render(root._state_mgr)


def test_entry_reset_error_preserves_error_and_allows_clean_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _root()
    state = root._state_mgr
    error = ValueError("reset failed")

    def fail_reset(self: Any) -> None:
        raise error

    with monkeypatch.context() as patch:
        patch.setattr(type(state), "_begin_field_only_pass", fail_reset)
        with pytest.raises(ValueError) as caught:
            with root.pass_scope():
                pytest.fail("entry should not reach the body")
    assert caught.value is error
    assert not state.is_scope_active()
    assert state._transaction_manager.active_transaction_for(PASS_TX_KEY) is None
    with root.pass_scope():
        pass


def test_adapter_cleanup_failure_quarantines_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _root()
    state = root._state_mgr
    error = ValueError("adapter cleanup failed")

    def fail_cleanup(self: Any, *, published: bool) -> None:
        raise error

    with monkeypatch.context() as patch:
        patch.setattr(type(state), "_clear_field_only_pass", fail_cleanup)
        with pytest.raises(ExceptionGroup) as caught:
            with root.pass_scope():
                raise RuntimeError("body failed")
    assert caught.value.exceptions[0].args == ("body failed",)
    assert caught.value.exceptions[1] is error
    assert not state.is_scope_active()
    with pytest.raises(RuntimeError, match="not ready for reuse"):
        with root.pass_scope():
            pass


def test_lost_transaction_blocks_retry_and_does_not_clear_replacement() -> None:
    root = _root()
    manager = root._state_mgr._transaction_manager
    with pytest.raises(RuntimeError, match="missing or replaced"):
        with root.pass_scope():
            manager.rollback(PASS_TX_KEY)
            replacement = manager.begin(PASS_TX_KEY)
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    assert not root._state_mgr.is_scope_active()
    with pytest.raises(RuntimeError, match="not ready for reuse"):
        with root.pass_scope():
            pass
    manager.rollback(PASS_TX_KEY)


def test_direct_local_success_cannot_publish_before_lexical_scope_exit() -> None:
    root = _root()
    with pytest.raises(ValueError, match="later body failed"):
        with root.pass_scope():
            root._state_mgr.own_ui_state = (
                UIElement(kind="candidate", props={}, children=()),
            )
            root.end_pass()
            assert root._state_mgr.current.ui_state == ()
            raise ValueError("later body failed")
    assert root._state_mgr.current.ui_state == ()


def test_explicit_local_rollback_poison_survives_normal_scope_exit() -> None:
    root = _root()
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            root.rollback_pass()
    assert root._state_mgr.current.ui_state == ()


def test_nested_root_cannot_attach_without_an_owned_component() -> None:
    root = _root()
    with pytest.raises(RuntimeError, match="owned component"):
        runtime.RenderContext(scheduler_root=root)


def test_component_retirement_remains_gated() -> None:
    root = _root()
    slot_id = runtime.SlotId(runtime.ModuleId("retirement"), 1)
    with root.pass_scope():
        component = root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
        component.invoke(lambda context: None, (), {})
    with pytest.raises(RuntimeError, match="retirement is not admitted"):
        with root.pass_scope():
            pass
    assert root._slots_by_id[slot_id] is component


def _id(index: int) -> Any:
    return runtime.SlotId(runtime.ModuleId("sc2.remediation"), index)


def _emit(context: Any, value: str) -> None:
    context.call_native(UIElement, kind=value, props={}, children=())


def _component(parent: Any) -> Any:
    component = parent._ensure_slot(_id(2), runtime.ComponentCallSlotContext)

    def render(context: Any) -> None:
        with context.pass_scope():
            leaf = context._ensure_slot(_id(3), runtime.LeafSlotContext)
            leaf.invoke_native(_emit, ("nested",), {}, context_param="context")

    component.invoke(render, (), {})
    return component


@pytest.mark.parametrize(
    "slot_type", (runtime.LeafSlotContext, runtime.SlotExprSlotContext)
)
def test_constructor_rejects_mismatched_parent_and_render_before_allocation(
    slot_type: type[Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root()
    other = runtime.RenderContext()
    initialized = []
    original = slot_type._state_mgr_cls.__init__

    def record_init(self: Any, **kwargs: Any) -> None:
        initialized.append(self)
        original(self, **kwargs)

    monkeypatch.setattr(slot_type._state_mgr_cls, "__init__", record_init)
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            with pytest.raises(RuntimeError, match="ownership"):
                slot_type(other, root, _id(1), seen_in_pass=True)
    assert initialized == []
    assert root._state_mgr.current.children_state == {}
    assert root._slots_by_id == other._slots_by_id == {}


@pytest.mark.parametrize("scheduler", (None, "other"))
def test_owned_render_requires_its_activated_scheduler_root(scheduler: Any) -> None:
    root = _root()
    other = runtime.RenderContext()
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            component = root._ensure_slot(_id(2), runtime.ComponentCallSlotContext)
            with pytest.raises(RuntimeError, match="scheduler ownership"):
                runtime.RenderContext(
                    owner_slot=component,
                    scheduler_root=None if scheduler is None else other,
                )
    assert component.child_context is None
    assert root._state_mgr.current.children_state == {}


def test_owned_render_cannot_be_activated_as_a_standalone_graph() -> None:
    root = runtime.RenderContext()
    with root.pass_scope():
        component = root._ensure_slot(_id(2), runtime.ComponentCallSlotContext)
        nested = runtime.RenderContext(owner_slot=component)
    with pytest.raises(RuntimeError, match="scheduler root"):
        _enable_field_only_render(nested._state_mgr)


@pytest.mark.parametrize("operation", ("deactivate", "dispose", "ancestor"))
@pytest.mark.parametrize("inside", (False, True))
def test_retirement_rejected_before_component_or_scheduler_mutation(
    operation: str, inside: bool
) -> None:
    root = _root()
    with root.pass_scope():
        parent = root._ensure_slot(_id(1), runtime.LeafSlotContext)
        with parent.pass_scope():
            component = _component(parent)
    nested = component.child_context
    callback = nested._state_mgr._mounted_callback
    scheduler = root._state_mgr._scheduler
    scheduler.request(nested)
    pending = tuple(scheduler.queue)
    current_ui = root._state_mgr.current.ui_state
    tracker = root._state_mgr.get_app_context(root._state_mgr._generation_tracker_key)
    generation = tracker.committed_generation_id

    def retire() -> None:
        if operation == "dispose":
            component._state_mgr._dispose_child_context()
        elif operation == "ancestor":
            parent.deactivate()
        else:
            component.deactivate()

    if inside:
        with pytest.raises(RenderAttemptAborted):
            with root.pass_scope():
                root._ensure_slot(_id(1), runtime.LeafSlotContext)
                with pytest.raises(RuntimeError, match="retirement is not admitted"):
                    retire()
    else:
        with pytest.raises(RuntimeError, match="retirement is not admitted"):
            retire()
    assert component.child_context is nested
    assert nested._state_mgr._mounted_callback is callback
    assert tuple(scheduler.queue) == pending
    assert parent._state_mgr.current.children_state[_id(2)] is component._state_mgr
    assert root._state_mgr.current.children_state[_id(1)] is parent._state_mgr
    assert root._state_mgr.current.ui_state == current_ui
    assert tracker.committed_generation_id == generation


def test_omitted_ancestor_cannot_orphan_a_queued_component() -> None:
    root = _root()
    with root.pass_scope():
        parent = root._ensure_slot(_id(1), runtime.LeafSlotContext)
        with parent.pass_scope():
            component = _component(parent)
    nested = component.child_context
    root._state_mgr._scheduler.request(nested)
    callback = nested._state_mgr._mounted_callback
    with pytest.raises(RuntimeError, match="retirement is not admitted"):
        with root.pass_scope():
            pass
    assert root._state_mgr.current.children_state[_id(1)] is parent._state_mgr
    assert component.child_context is nested
    assert nested._state_mgr._mounted_callback is callback
    assert tuple(root._state_mgr._scheduler.queue) == (nested,)


@pytest.mark.parametrize("execution", ("publication", "native", "reentry"))
def test_early_local_end_waits_for_enclosing_execution_and_preserves_error(
    execution: str,
) -> None:
    root = _root()
    with root.pass_scope():
        leaf = root._ensure_slot(_id(1), runtime.LeafSlotContext)
        leaf.invoke_native(_emit, ("old",), {}, context_param="context")
    tracker = root._state_mgr.get_app_context(root._state_mgr._generation_tracker_key)
    generation = tracker.committed_generation_id
    context = leaf if execution == "native" else root
    current_ui = context._state_mgr.current.ui_state
    error = ValueError("original execution failure")

    def finish_then_fail(active: Any) -> None:
        _emit(active, "candidate")
        active.end_pass()
        assert active._state_mgr.current.ui_state == current_ui
        assert tracker.committed_generation_id == generation
        raise error

    with pytest.raises(ValueError) as caught:
        if execution == "native":
            leaf.invoke_native(finish_then_fail, (), {}, context_param="context")
        else:
            root.begin_pass()
            scope = (
                root.pass_scope()
                if execution == "reentry"
                else root._state_mgr.publish_write_scope()
            )
            with scope:
                finish_then_fail(root)
    assert caught.value is error
    assert context._state_mgr.current.ui_state == current_ui
    assert tracker.committed_generation_id == generation
    with context.pass_scope():
        _emit(context, "retry")


def test_noop_reentry_cannot_write_into_replacement_transaction() -> None:
    root = _root()
    state = root._state_mgr
    manager = state._transaction_manager
    entered = False
    with pytest.raises(RuntimeError, match="missing or replaced"):
        with root.pass_scope():
            manager.rollback(PASS_TX_KEY)
            replacement = manager.begin(PASS_TX_KEY)
            with root.pass_scope():
                entered = True
                _emit(root, "foreign candidate")
    assert not entered
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    assert not state._field_only_completion.last.reuse_ready
    manager.commit(PASS_TX_KEY)
    assert state.current.ui_state == ()


def test_discard_reconciles_retained_new_nested_root_cache() -> None:
    root = _root()
    with pytest.raises(ValueError, match="discard new component"):
        with root.pass_scope():
            component = _component(root)
            nested = component.child_context
            raise ValueError("discard new component")
    assert root._slots_by_id == {}
    assert nested._state_mgr.current.children_state == {}
    assert nested._slots_by_id == {}
    assert not nested.debug_is_active(_id(3))
    with root.pass_scope():
        replacement = _component(root)
    assert replacement is not component
