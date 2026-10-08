from __future__ import annotations

import pytest

from pyrolyze.api import UIElement, no_emit, validate_mount_selectors
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.completion_render import (
    _enable_completion_render,
)


def root_and_id():
    root = runtime.RenderContext()
    _enable_completion_render(root._state_mgr)
    return root, runtime.SlotId(runtime.ModuleId("completion-proof"), 1)


def test_no_emit_rejects_new_candidate_child() -> None:
    root, slot_id = root_and_id()
    with pytest.raises(RuntimeError, match="no_emit"):
        with root.pass_scope():
            with root.open_directive(
                slot_id, validate_mount_selectors, no_emit
            ) as scope:
                child = scope._ensure_slot(
                    runtime.SlotId(slot_id.module_id, 2), runtime.LeafSlotContext
                )
                with child.pass_scope():
                    child.call_native(UIElement, kind="candidate", props={})
    assert root.debug_ui() == ()


def test_callbacks_drain_system_failures_without_undoing_publication() -> None:
    root, _ = root_and_id()
    errors = (ValueError("first"), KeyboardInterrupt("second"))
    calls = []

    def fail(error):
        calls.append(str(error))
        raise error

    with pytest.raises(BaseExceptionGroup) as caught:
        with root.pass_scope():
            root.call_native(UIElement, kind="accepted", props={})
            for error in errors:
                root._enqueue_post_commit(lambda error=error: fail(error))
            root._enqueue_post_commit(lambda: calls.append("last"))
    assert calls == ["first", "second", "last"]
    assert caught.value.exceptions == errors
    assert root.debug_ui()[0].kind == "accepted"
    assert root._state_mgr._field_only_completion.last.published is True
    with pytest.raises(RuntimeError, match="not ready"):
        with root.pass_scope():
            pass


def test_callback_reentry_cannot_enqueue_or_render() -> None:
    root, _ = root_and_id()
    failures = []

    def callback():
        for operation in (
            lambda: root._enqueue_post_commit(lambda: None),
            root.begin_pass,
        ):
            with pytest.raises(RuntimeError) as caught:
                operation()
            failures.append(caught.value)

    with root.pass_scope():
        root._enqueue_post_commit(callback)
    assert len(failures) == 2


def test_independent_invalidation_survives_failed_render() -> None:
    root, slot_id = root_and_id()
    with root.pass_scope():
        child = root._ensure_slot(slot_id, runtime.LeafSlotContext)
        with child.pass_scope():
            pass
    with pytest.raises(ValueError, match="discard"):
        with root.pass_scope():
            root._state_mgr.queue_invalidation_from(child)
            root._enqueue_post_commit(lambda: pytest.fail("discarded callback"))
            raise ValueError("discard")
    assert root._state_mgr._scheduler.has_pending_work()
    assert root._queued_invalidations == [child]
    assert child._state_mgr._invoke_dirty


def test_lone_callback_failure_is_preserved() -> None:
    root, _ = root_and_id()
    error = ValueError("callback")

    def fail():
        raise error

    with pytest.raises(ValueError) as caught:
        with root.pass_scope():
            root._enqueue_post_commit(fail)
    assert caught.value is error


def test_caught_invalid_selector_aborts_outer_render() -> None:
    from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted

    root, slot_id = root_and_id()
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            with pytest.raises(TypeError, match="SlotSelector"):
                with root.open_directive(slot_id, lambda: (object(),)):
                    pass
    assert root._state_mgr.current.children_state == {}


def test_superseded_child_callback_is_not_delivered() -> None:
    root, slot_id = root_and_id()
    calls = []

    def render_old(context):
        with context.pass_scope():
            context._enqueue_post_commit(lambda: calls.append("old"))

    def render_new(context):
        with context.pass_scope():
            context._enqueue_post_commit(lambda: calls.append("new"))

    with root.pass_scope():
        slot = root._ensure_slot(slot_id, runtime.ComponentCallSlotContext)
        slot.invoke(render_old, (), {})
        slot.invoke(render_new, (), {})
        root._enqueue_post_commit(lambda: calls.append("root"))
    assert calls == ["new", "root"]


def test_effect_failure_does_not_skip_general_callbacks() -> None:
    from pyrolyze.runtime.slot_call_semantics import UseEffectRequest

    root, slot_id = root_and_id()
    calls = []
    error = ValueError("setup")

    def effect():
        calls.append("effect")
        raise error

    with pytest.raises(ValueError) as caught:
        with root.pass_scope():
            slot = root._ensure_slot(slot_id, runtime.SlotCallSlotContext)
            slot.evaluate(lambda: UseEffectRequest(effect, ()), (), {})
            root._enqueue_post_commit(lambda: calls.append("callback"))
    assert caught.value is error
    assert calls == ["effect", "callback"]


def test_expression_callback_is_discarded_on_outer_failure() -> None:
    root, slot_id = root_and_id()
    calls = []
    with pytest.raises(ValueError):
        with root.pass_scope():
            slot = root._ensure_slot(slot_id, runtime.SlotExprSlotContext)
            with slot.pass_scope():
                slot.append_slot_expr_post_commit_callback(
                    lambda: calls.append("expression")
                )
            raise ValueError("discard")
    assert calls == []


def test_incomplete_registry_reconciliation_blocks_observers(monkeypatch) -> None:
    from pyrolyze.runtime.context_state_lcm.completion_render import (
        _CompletionRenderCompletion,
    )

    root, _ = root_and_id()
    calls = []
    error = ValueError("registry")

    def fail(self):
        raise error

    monkeypatch.setattr(_CompletionRenderCompletion, "_reconcile_registry", fail)
    with pytest.raises(ValueError) as caught:
        with root.pass_scope():
            root._enqueue_post_commit(lambda: calls.append("observer"))
    assert caught.value is error
    assert calls == []
    assert root._state_mgr._field_only_completion.last.published is True


def test_selector_iteration_cannot_write_into_replacement_transaction() -> None:
    from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY

    root, slot_id = root_and_id()
    manager = root._state_mgr._transaction_manager

    class Selectors:
        def __iter__(self):
            manager.rollback(PASS_TX_KEY)
            manager.begin(PASS_TX_KEY)
            return iter(())

    with pytest.raises((RuntimeError, BaseExceptionGroup)):
        with root.pass_scope():
            with root.open_directive(slot_id, lambda: Selectors()):
                pass
    assert manager.active_transaction_for(PASS_TX_KEY) is not None
    assert root._state_mgr.current.children_state == {}
    assert not root._state_mgr._field_only_completion.last.reuse_ready
    manager.rollback(PASS_TX_KEY)
