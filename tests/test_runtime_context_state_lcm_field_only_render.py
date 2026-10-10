from __future__ import annotations

from typing import Any

import pytest
from collections.abc import Hashable
from dataclasses import replace

from pyrolyze.api import UIElement
from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted
from yidl_lifecycle.transaction_yidl import TransactionManager


def _root() -> Any:
    root = runtime.RenderContext()
    return root


def test_lifecycle_pass_does_not_capture_legacy_child_order() -> None:
    root = _root()
    with root.pass_scope():
        runtime.LeafSlotContext(
            root, root, runtime.SlotId(runtime.ModuleId("order"), 1), seen_in_pass=True
        )
    with root.pass_scope():
        assert not hasattr(root, "_pass_child_order")






def test_entry_reset_error_preserves_error_and_allows_clean_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _root()
    state = root
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
    state = root
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
    manager = root._transaction_manager
    with pytest.raises(RuntimeError, match="missing or replaced"):
        with root.pass_scope():
            manager.rollback(PASS_TX_KEY)
            replacement = manager.begin(PASS_TX_KEY)
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    assert not root.is_scope_active()
    with pytest.raises(RuntimeError, match="not ready for reuse"):
        with root.pass_scope():
            pass
    manager.rollback(PASS_TX_KEY)


def test_direct_local_success_cannot_publish_before_lexical_scope_exit() -> None:
    root = _root()
    with pytest.raises(ValueError, match="later body failed"):
        with root.pass_scope():
            root.own_ui_state = (
                UIElement(kind="candidate", props={}, children=()),
            )
            root.end_pass()
            assert root.current.ui_state == ()
            raise ValueError("later body failed")
    assert root.current.ui_state == ()


def test_explicit_local_rollback_poison_survives_normal_scope_exit() -> None:
    root = _root()
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            root.rollback_pass()
    assert root.current.ui_state == ()


def test_nested_root_cannot_attach_without_an_owned_component() -> None:
    root = _root()
    with pytest.raises(RuntimeError, match="owned component"):
        runtime.RenderContext(scheduler_root=root)




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
    original = slot_type._managed_context_cls.__init__

    def record_init(self: Any, **kwargs: Any) -> None:
        initialized.append(self)
        original(self, **kwargs)

    monkeypatch.setattr(slot_type._managed_context_cls, "__init__", record_init)
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            with pytest.raises(RuntimeError, match="ownership"):
                slot_type(other, root, _id(1), seen_in_pass=True)
    assert initialized == []
    assert root.current.children_state == {}
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
    assert root.current.children_state == {}








@pytest.mark.parametrize("execution", ("publication", "native", "reentry"))
def test_early_local_end_waits_for_enclosing_execution_and_preserves_error(
    execution: str,
) -> None:
    root = _root()
    with root.pass_scope():
        leaf = root._ensure_slot(_id(1), runtime.LeafSlotContext)
        leaf.invoke_native(_emit, ("old",), {}, context_param="context")
    tracker = root.get_app_context(root._generation_tracker_key)
    generation = tracker.committed_generation_id
    context = leaf if execution == "native" else root
    current_ui = context.current.ui_state
    error = ValueError("original execution failure")

    def finish_then_fail(active: Any) -> None:
        _emit(active, "candidate")
        active.end_pass()
        assert active.current.ui_state == current_ui
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
                else root.publish_write_scope()
            )
            with scope:
                finish_then_fail(root)
    assert caught.value is error
    assert context.current.ui_state == current_ui
    assert tracker.committed_generation_id == generation
    with context.pass_scope():
        _emit(context, "retry")


def test_noop_reentry_cannot_write_into_replacement_transaction() -> None:
    root = _root()
    state = root
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
    assert nested.current.children_state == {}
    assert nested._slots_by_id == {}
    assert not nested.debug_is_active(_id(3))
    with root.pass_scope():
        replacement = _component(root)
    assert replacement is not component


def test_publication_only_nested_discard_clears_reuse_cache() -> None:
    root = _root()
    retained = []

    def render(context: Any) -> None:
        with context.publish_write_scope():
            leaf = runtime.LeafSlotContext(context, context, _id(9), seen_in_pass=True)
            retained.extend((context, leaf))

    with pytest.raises(ValueError, match="discard publication-only root"):
        with root.pass_scope():
            component = root._ensure_slot(_id(2), runtime.ComponentCallSlotContext)
            component.invoke(render, (), {})
            raise ValueError("discard publication-only root")
    nested, discarded = retained
    assert nested.current.children_state == {}
    assert nested._slots_by_id == {}
    assert root._slots_by_id == {}
    with pytest.raises(RuntimeError, match="installed child"):
        with nested.pass_scope():
            pytest.fail("discarded child must not execute")
    assert discarded.current.ui_state == ()
    with root.pass_scope():
        replacement = _component(root).child_context
    assert replacement is not nested


@pytest.mark.parametrize("clear", (False, True))
def test_publication_only_registry_removal_restored_after_discard(
    clear: bool,
) -> None:
    root = _root()
    with root.pass_scope():
        component = _component(root)
    nested = component.child_context
    leaf = nested._slots_by_id[_id(3)]
    with pytest.raises(ValueError, match="discard registry removal"):
        with root.pass_scope():
            root._ensure_slot(_id(2), runtime.ComponentCallSlotContext)
            with nested.publish_write_scope():
                if clear:
                    nested.clear_registered_slots()
                else:
                    nested.unregister_slot(_id(3))
                raise ValueError("discard registry removal")
    assert nested._slots_by_id[_id(3)] is leaf
    assert nested.current.children_state[_id(3)] is leaf




@pytest.mark.parametrize("nested", (False, True))
def test_colliding_direct_constructor_rejected_before_attachment(
    nested: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root()
    with root.pass_scope():
        component = _component(root)
    child = component.child_context
    callback = child._mounted_callback
    root._scheduler.request(child)
    current_ui = root.current.ui_state
    tracker = root.get_app_context(root._generation_tracker_key)
    generation = tracker.committed_generation_id
    initialized = []
    original = runtime.LeafSlotContext._managed_context_cls.__init__

    def record_init(self: Any, **kwargs: Any) -> None:
        initialized.append(self)
        original(self, **kwargs)

    monkeypatch.setattr(runtime.LeafSlotContext._managed_context_cls, "__init__", record_init)

    def replace() -> None:
        with root.publish_write_scope():
            with pytest.raises(RuntimeError, match="replacement is not admitted"):
                runtime.LeafSlotContext(root, root, _id(2), seen_in_pass=True)

    with pytest.raises(RenderAttemptAborted):
        if nested:
            with root.pass_scope():
                root._ensure_slot(_id(2), runtime.ComponentCallSlotContext)
                replace()
        else:
            replace()
    assert initialized == []
    assert root.current.children_state[_id(2)] is component
    assert root._slots_by_id[_id(2)] is component
    assert component.child_context is child
    assert child._mounted_callback is callback
    assert tuple(root._scheduler.queue) == (child,)
    assert root.current.ui_state == current_ui
    assert tracker.committed_generation_id == generation
    with root.pass_scope():
        assert root._ensure_slot(_id(2), runtime.ComponentCallSlotContext) is component


def test_leaf_removal_with_staged_sibling_discards_to_original_membership() -> None:
    root = _root()
    with root.pass_scope():
        original = root._ensure_slot(_id(1), runtime.LeafSlotContext)
        original.invoke_native(_emit, ("old",), {}, context_param="context")
    with pytest.raises(ValueError, match="discard removal"):
        with root.pass_scope():
            root._ensure_slot(_id(1), runtime.LeafSlotContext)
            sibling = root._ensure_slot(_id(3), runtime.LeafSlotContext)
            sibling.invoke_native(_emit, ("keep",), {}, context_param="context")
            original.deactivate()
            assert tuple(root.children_state) == (_id(3),)
            raise ValueError("discard removal")
    assert root.current.children_state == {_id(1): original}
    assert sibling.current.ui_state == ()


@pytest.mark.parametrize("inside", (False, True))
def test_duplicate_owned_root_rejected_before_lifecycle_initialization(
    inside: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pyrolyze.runtime.context_state_lcm.context_base import ContextBaseStateMgr

    root = _root()
    tracker = root.get_app_context(root._generation_tracker_key)
    with root.pass_scope():
        component = _component(root)
    generation = tracker.committed_generation_id
    current_ui = root.current.ui_state
    initialized = []
    original = ContextBaseStateMgr.__init__

    def record_init(self: Any, **kwargs: Any) -> None:
        initialized.append(self)
        original(self, **kwargs)

    def reject_duplicate() -> None:
        with monkeypatch.context() as patch:
            patch.setattr(ContextBaseStateMgr, "__init__", record_init)
            with pytest.raises(RuntimeError, match="owned"):
                runtime.RenderContext(owner_slot=component, scheduler_root=root)

    if inside:
        with pytest.raises(RenderAttemptAborted):
            with root.pass_scope():
                root._ensure_slot(_id(2), runtime.ComponentCallSlotContext)
                child = component.child_context
                callback = child._mounted_callback
                root._scheduler.request(child)
                reject_duplicate()
    else:
        child = component.child_context
        callback = child._mounted_callback
        root._scheduler.request(child)
        reject_duplicate()
    assert initialized == []
    assert component.child_context is child
    assert child._mounted_callback is callback
    assert tuple(root._scheduler.queue) == (child,)
    assert root.current.ui_state == current_ui
    assert tracker.committed_generation_id == generation
    with root.pass_scope():
        reused = root._ensure_slot(_id(2), runtime.ComponentCallSlotContext)
    assert reused is component


@pytest.mark.parametrize("inside", (False, True))
@pytest.mark.parametrize(
    "entry", ("mount", "boundary", "pass", "begin", "publish", "refresh", "construct")
)
def test_uninstalled_owned_root_cannot_execute_or_propagate_ui(
    entry: str, inside: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root()
    with root.pass_scope():
        component = root._ensure_slot(_id(2), runtime.ComponentCallSlotContext)
        uninstalled = runtime.RenderContext(owner_slot=component, scheduler_root=root)
    tracker = root.get_app_context(root._generation_tracker_key)
    generation = tracker.committed_generation_id
    ran = []

    def callback() -> None:
        ran.append(True)

    monkeypatch.setattr(uninstalled, "_mounted_callback", callback)

    def enter() -> None:
        with pytest.raises(RuntimeError, match="owned render"):
            if entry == "mount":
                uninstalled.mount(lambda: ran.append(False))
            elif entry == "boundary":
                uninstalled._run_boundary()
            elif entry == "pass":
                with uninstalled.pass_scope():
                    callback()
            elif entry == "begin":
                uninstalled.begin_pass()
            elif entry == "publish":
                with uninstalled.publish_write_scope():
                    callback()
            elif entry == "construct":
                runtime.LeafSlotContext(
                    uninstalled, uninstalled, _id(8), seen_in_pass=True
                )
            else:
                uninstalled._refresh_committed_ui_from_children()

    if inside:
        with pytest.raises(RenderAttemptAborted):
            with root.pass_scope():
                root._ensure_slot(_id(2), runtime.ComponentCallSlotContext)
                enter()
    else:
        enter()
    assert ran == []
    assert component.child_context is None
    assert uninstalled._mounted_callback is callback
    assert (
        root.current.ui_state == component.current.ui_state == ()
    )
    assert root.debug_pending_boundaries() == ()
    assert tracker.committed_generation_id == generation
    with root.pass_scope():
        _component(root)




def test_published_generation_survives_local_scratch_cleanup_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pyrolyze.runtime.context_state_lcm.context_base import ContextBaseStateMgr

    root = _root()
    state = root
    tracker = state.get_app_context(state._generation_tracker_key)
    failure = ValueError("scratch cleanup failed")

    def fail_cleanup(self: Any, *, published: bool) -> None:
        assert published
        raise failure

    monkeypatch.setattr(ContextBaseStateMgr, "_clear_field_only_pass", fail_cleanup)
    with pytest.raises(ValueError) as raised:
        with root.pass_scope():
            _emit(root, "published")
    assert raised.value is failure
    assert state.current.ui_state[0].kind == "published"
    assert tracker.committed_generation_id == 1
    assert tracker.active_generation_id is None
    with pytest.raises(RuntimeError, match="not ready for reuse"):
        with root.pass_scope():
            pytest.fail("quarantined graph entered")
    assert tracker.committed_generation_id == 1


@pytest.mark.parametrize("bool_raises", (False, True))
def test_after_error_and_local_cleanup_never_test_exception_truthiness(
    bool_raises: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pyrolyze.runtime.context_state_lcm.context_base import ContextBaseStateMgr
    from pyrolyze.runtime.app_context import GenerationTracker

    truth_checks = []
    commits = []

    class Primary(ValueError):
        def __bool__(self) -> bool:
            truth_checks.append(True)
            if bool_raises:
                raise AssertionError("exception truthiness evaluated")
            return False

    primary, cleanup = Primary("after failed"), LookupError("local cleanup failed")

    class Participant:
        def commit_order_key_for(self, tx_key: Hashable) -> tuple[object, ...]:
            return ()

        def requires_validation_for(self, tx_key: Hashable) -> bool:
            return False

        def _prepare_commit_tx_by_key(self, tx_key: Hashable, token: int) -> None:
            pass

        def _apply_prepared_commit_tx_by_key(
            self, tx_key: Hashable, token: int
        ) -> None:
            pass

        def _after_commit_tx_by_key(self, tx_key: Hashable, token: int) -> None:
            raise primary

    def fail_cleanup(self: Any, *, published: bool) -> None:
        assert published
        raise cleanup

    original = GenerationTracker.commit

    def record_commit(self: GenerationTracker) -> int:
        commits.append(True)
        return original(self)

    root = _root()
    state = root
    tracker = state.get_app_context(state._generation_tracker_key)
    monkeypatch.setattr(ContextBaseStateMgr, "_clear_field_only_pass", fail_cleanup)
    monkeypatch.setattr(GenerationTracker, "commit", record_commit)
    with pytest.raises(ExceptionGroup) as caught:
        with root.pass_scope():
            _emit(root, "published")
            state._transaction_manager.enlist(Participant(), PASS_TX_KEY)
    assert caught.value.exceptions == (primary, cleanup)
    assert truth_checks == []
    assert commits == [True]
    assert tracker.committed_generation_id == 1
    assert tracker.active_generation_id is None
    assert state._field_only_completion.active is None
    assert state._field_only_local_scope is None
    assert state.current.ui_state[0].kind == "published"
    with pytest.raises(RuntimeError, match="reuse"):
        with root.pass_scope():
            pytest.fail("quarantined graph entered")
    assert commits == [True]


@pytest.mark.parametrize("attribute", ("tx_key", "tx_id"))
@pytest.mark.parametrize("reentry", (False, True))
def test_token_relabeling_before_local_entry_is_sticky_after_restoration(
    attribute: str,
    reentry: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pyrolyze.runtime.context_state_lcm.context_base import ContextBaseStateMgr

    root = _root()
    state = root
    completion = state._field_only_completion
    tracker = state.get_app_context(state._generation_tracker_key)
    entered = []
    resets = []
    begin = ContextBaseStateMgr._begin_field_only_pass

    def record_reset(self: Any) -> None:
        resets.append(True)
        begin(self)

    monkeypatch.setattr(ContextBaseStateMgr, "_begin_field_only_pass", record_reset)
    with pytest.raises(RuntimeError):
        with completion.attempt_scope():
            scope = root.pass_scope() if reentry else completion.attempt_scope()
            with scope:
                token = completion.active.transaction
                original = getattr(token, attribute)
                setattr(token, attribute, object() if attribute == "tx_key" else 999)
                try:
                    with pytest.raises(RuntimeError):
                        with root.pass_scope():
                            entered.append(True)
                            _emit(root, "candidate")
                finally:
                    setattr(token, attribute, original)
                with pytest.raises(RuntimeError):
                    with root.pass_scope():
                        entered.append(True)
    assert entered == []
    assert resets == ([True] if reentry else [])
    assert state.current.ui_state == ()
    assert tracker.committed_generation_id == 0
    assert tracker.active_generation_id is not None
    assert completion.last.published is None
    assert completion.last.publication_uncertain
    assert not completion.last.reuse_ready
    with pytest.raises(RuntimeError, match="reuse"):
        with root.pass_scope():
            pytest.fail("restoration rehabilitated the owner")


@pytest.mark.parametrize(
    "corruption", ("boolean_id", "empty_after_failure", "success_with_failure")
)
def test_contradictory_terminal_evidence_cannot_complete_generation(
    corruption: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pyrolyze.runtime.context_state_lcm.render_attempt import (
        RenderAttemptIncomplete,
    )

    root = _root()
    state = root
    manager = state._transaction_manager
    completion = state._field_only_completion
    tracker = state.get_app_context(state._generation_tracker_key)
    original = TransactionManager.commit_only
    supplied = ValueError("retained record failure")
    calls = []

    def corrupt(self: TransactionManager, tx_key: Hashable) -> int | None:
        calls.append(tx_key)
        result = original(self, tx_key)
        token = completion.active.transaction
        if corruption == "boolean_id":
            token.tx_id = True
        else:
            changes = {"failures": (supplied,)}
            if corruption == "empty_after_failure":
                changes.update(publication_started=False, after_actions_complete=False)
            token._completion = replace(token.completion, **changes)
        return result

    monkeypatch.setattr(TransactionManager, "commit_only", corrupt)
    with pytest.raises((RenderAttemptIncomplete, ExceptionGroup)) as caught:
        with root.pass_scope():
            _emit(root, "published")

    def contains(error: BaseException, target: BaseException) -> bool:
        return (
            error is target
            or isinstance(error, BaseExceptionGroup)
            and any(contains(child, target) for child in error.exceptions)
        )

    if corruption != "boolean_id":
        assert contains(caught.value, supplied)
    assert completion.last.published is None
    assert completion.last.publication_uncertain and not completion.last.reuse_ready
    assert state.current.ui_state[0].kind == "published"
    assert tracker.committed_generation_id == 0
    assert tracker.active_generation_id is not None
    for entry in (root.pass_scope, state.publish_write_scope):
        with pytest.raises(RuntimeError, match="reuse"):
            with entry():
                pytest.fail("contradictory evidence admitted another write")
    assert calls == [PASS_TX_KEY]
