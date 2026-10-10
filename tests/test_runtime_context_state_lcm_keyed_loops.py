from __future__ import annotations

import pytest

from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted


def root_and_id():
    root = runtime.RenderContext()
    return root, runtime.SlotId(runtime.ModuleId("loop-faults"), 1)


def consume(root, slot_id, values, key_fn=lambda value: value):
    for item in root.keyed_loop(slot_id, values, key_fn=key_fn):
        with item.pass_scope():
            item.current_value()


def test_caught_duplicate_key_discards_outer_attempt() -> None:
    root, slot_id = root_and_id()
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            with pytest.raises(RuntimeError, match="duplicate key"):
                consume(root, slot_id, [1, 1])
    assert root.current.children_state == {}


def test_caught_normalization_failure_discards_outer_attempt() -> None:
    root, slot_id = root_and_id()
    error = ValueError("iteration")

    class Values:
        def __iter__(self):
            raise error

    with pytest.raises(RenderAttemptAborted) as caught:
        with root.pass_scope():
            with pytest.raises(ValueError):
                root.keyed_loop(slot_id, Values(), key_fn=lambda value: value)
    assert caught.value.__cause__ is error


@pytest.mark.parametrize("replace_in_key", [True, False])
def test_user_key_or_comparison_cannot_write_into_replacement(replace_in_key) -> None:
    root, slot_id = root_and_id()
    manager = root._transaction_manager

    def replace():
        manager.rollback(PASS_TX_KEY)
        manager.begin(PASS_TX_KEY)

    class Value:
        def __eq__(self, other):
            replace()
            return False

    with root.pass_scope():
        consume(root, slot_id, [Value()], key_fn=lambda value: 1)

    def key(value):
        if replace_in_key:
            replace()
        return 1

    with pytest.raises((RuntimeError, BaseExceptionGroup)):
        with root.pass_scope():
            consume(root, slot_id, [Value()], key_fn=key)
    assert manager.active_transaction_for(PASS_TX_KEY) is not None
    loop = root.current.children_state[slot_id]
    item = next(iter(loop.current.children_state.values()))
    assert item._selection is item.current._selection
    manager.rollback(PASS_TX_KEY)


def test_hash_during_membership_insertion_cannot_stage_replacement(monkeypatch) -> None:
    root, slot_id = root_and_id()
    manager = root._transaction_manager

    with root.pass_scope():
        consume(root, slot_id, [1], key_fn=lambda value: 7)
    loop = root.current.children_state[slot_id]
    state_type = type(root)
    original_lookup = state_type.get_registered_slot
    original_hash = runtime.SlotId.__hash__
    armed = False

    def lookup(state, item_id):
        nonlocal armed
        result = original_lookup(state, item_id)
        if item_id.key_path == (7,):
            armed = True
        return result

    def hash_slot(item_id):
        nonlocal armed
        result = original_hash(item_id)
        if armed and item_id.key_path == (7,):
            armed = False
            manager.rollback(PASS_TX_KEY)
            manager.begin(PASS_TX_KEY)
        return result

    # Arm after registry lookup: the next keyed hash inserts into membership.
    # Do not count key hashes, which tuple caching changes between interpreters.
    monkeypatch.setattr(state_type, "get_registered_slot", lookup)
    monkeypatch.setattr(runtime.SlotId, "__hash__", hash_slot)
    with pytest.raises((RuntimeError, BaseExceptionGroup)):
        with root.pass_scope():
            consume(root, slot_id, [2], key_fn=lambda value: 7)
    assert manager.active_transaction_for(PASS_TX_KEY) is not None
    assert loop.children_state is loop.current.children_state
    manager.rollback(PASS_TX_KEY)


def test_explicit_early_close_inside_successful_scope_keeps_prefix() -> None:
    root, slot_id = root_and_id()
    with root.pass_scope():
        loop = root.keyed_loop(slot_id, [1, 2], key_fn=lambda value: value)
        with loop.pass_scope():
            iterator = iter(loop)
            item = next(iterator)
            with item.pass_scope():
                item.current_value()
            iterator.close()
    loop_state = root.current.children_state[slot_id]
    assert len(loop_state.current.children_state) == 1


def test_caught_loop_body_failure_discards_prefix() -> None:
    root, slot_id = root_and_id()
    error = ValueError("loop body")
    with pytest.raises(RenderAttemptAborted) as caught:
        with root.pass_scope():
            with pytest.raises(ValueError):
                loop = root.keyed_loop(slot_id, [1, 2], key_fn=lambda value: value)
                with loop.pass_scope():
                    for item in loop:
                        with item.pass_scope():
                            item.current_value()
                        raise error
    assert caught.value.__cause__ is error
    assert root.current.children_state == {}


@pytest.mark.parametrize("started", [True, False])
def test_iterator_cannot_resume_after_its_execution_scope_exits(started) -> None:
    root, slot_id = root_and_id()
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            loop = root.keyed_loop(slot_id, [1, 2], key_fn=lambda value: value)
            with loop.pass_scope():
                iterator = iter(loop)
                if started:
                    item = next(iterator)
                    with item.pass_scope():
                        item.current_value()
            with pytest.raises(RuntimeError, match="loop execution scope"):
                next(iterator)
            iterator.close()


def test_retained_unexited_iterator_does_not_delay_outer_completion() -> None:
    root, slot_id = root_and_id()
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            iterator = iter(
                root.keyed_loop(slot_id, [1, 2], key_fn=lambda value: value)
            )
            item = next(iterator)
            with item.pass_scope():
                item.current_value()
    assert root._field_only_completion.active is None
    assert root.current.children_state == {}
    iterator.close()


def test_recursive_iteration_of_same_loop_is_rejected() -> None:
    root, slot_id = root_and_id()
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            iterator = iter(root.keyed_loop(slot_id, [1], key_fn=lambda value: value))
            next(iterator)
            with pytest.raises(RuntimeError, match="recursive keyed-loop"):
                consume(root, slot_id, [2])
            iterator.close()


def test_stale_iterator_cannot_join_new_attempt() -> None:
    root, slot_id = root_and_id()
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            iterator = iter(
                root.keyed_loop(slot_id, [1, 2], key_fn=lambda value: value)
            )
            next(iterator)
    with root.pass_scope():
        with pytest.raises(RuntimeError, match="finished"):
            next(iterator)
        consume(root, slot_id, [3])
    assert root._field_only_completion.last.published is True


@pytest.mark.parametrize("fail_in_hash", [True, False])
def test_hash_and_key_failures_preserve_original_cause(fail_in_hash) -> None:
    root, slot_id = root_and_id()
    error = ValueError("key failure")

    class Key:
        def __hash__(self):
            raise error

    def key(value):
        if not fail_in_hash:
            raise error
        return Key()

    with pytest.raises(RenderAttemptAborted) as caught:
        with root.pass_scope():
            with pytest.raises(ValueError):
                consume(root, slot_id, [1], key_fn=key)
    assert caught.value.__cause__ is error
    assert root.current.children_state == {}
