from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass, field, replace
from typing import NoReturn

import pytest

from pyrolyze.runtime.context_state_lcm.lifecycle_adapter import (
    TransactionManager,
    managed,
    managed_context,
)
from pyrolyze.runtime.context_state_lcm.render_attempt import (
    RenderAttemptAborted,
    RenderAttemptIncomplete,
    _RenderAttempt,
)

RENDER_KEY = object()
OTHER_KEY = object()


@managed_context
class RenderValues:
    value: int = managed(RENDER_KEY, default=1)
    other: int = managed(OTHER_KEY, default=2)


@dataclass
class _LocalPass:
    events: list[str] = field(default_factory=list)

    def reset(self) -> None:
        self.events.append("reset")

    def finish(self) -> None:
        self.events.append("finish")

    def abort(self) -> None:
        self.events.append("abort")


def _raise_cleanup() -> NoReturn:
    raise LookupError("cleanup failed")


def _raise_exit() -> NoReturn:
    raise ValueError("local exit failed")


def _manager() -> TransactionManager:
    return TransactionManager(tx_keys=(RENDER_KEY, OTHER_KEY))


def test_local_success_does_not_complete_owned_transaction() -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    local = _LocalPass()
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with attempt:
        with attempt.scope(
            local,
            manager=manager,
            on_enter=local.reset,
            on_exit=local.finish,
            on_abort=local.abort,
        ):
            values.working.value = 9
            assert attempt.is_scope_active(local)
        assert not attempt.is_scope_active(local)
        assert manager.active_transaction_for(RENDER_KEY) is attempt.transaction
        assert values.current.value == 1
    assert local.events == ["reset", "finish"]
    assert values.current.value == 9
    assert manager.active_transaction_for(RENDER_KEY) is None
    assert attempt.finished and attempt.reuse_ready
    with pytest.raises(RuntimeError, match="already finished"):
        attempt.finish()


def test_caught_child_failure_poison_is_sticky_and_preserves_first_cause() -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    child = _LocalPass()
    sibling = _LocalPass()
    failure = ValueError("child failed")
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(RenderAttemptAborted) as aborted:
        with attempt:
            try:
                with attempt.scope(
                    child,
                    manager=manager,
                    on_enter=child.reset,
                    on_exit=child.finish,
                    on_abort=child.abort,
                ):
                    values.working.value = 9
                    raise failure
            except ValueError:
                pass
            with attempt.scope(
                sibling,
                manager=manager,
                on_enter=sibling.reset,
                on_exit=sibling.finish,
                on_abort=sibling.abort,
            ):
                values.working.value = 10
            attempt.fail(RuntimeError("later failure"))
    assert aborted.value.__cause__ is failure
    assert attempt.first_failure is failure
    assert values.current.value == 1
    assert values.working.value == 1
    assert manager.active_transaction_for(RENDER_KEY) is None
    assert child.events == ["reset", "abort"]
    assert sibling.events == ["reset", "finish"]
    assert attempt.reuse_ready


def test_scoped_reentry_is_noop_but_direct_duplicate_begin_is_error() -> None:
    manager = _manager()
    local = _LocalPass()
    with _RenderAttempt.start(manager, RENDER_KEY) as attempt:
        with attempt.scope(
            local,
            manager=manager,
            on_enter=local.reset,
            on_exit=local.finish,
            on_abort=local.abort,
        ):
            with attempt.scope(
                local,
                manager=manager,
                on_enter=local.reset,
                on_exit=local.finish,
                on_abort=local.abort,
            ):
                assert attempt.is_scope_active(local)
            assert local.events == ["reset"]
    assert local.events == ["reset", "finish"]

    with pytest.raises(RenderAttemptAborted):
        with _RenderAttempt.start(manager, RENDER_KEY) as attempt:
            scope = attempt.begin_scope(
                local,
                manager=manager,
                on_enter=local.reset,
                on_exit=local.finish,
                on_abort=local.abort,
            )
            with pytest.raises(RuntimeError, match="already active"):
                attempt.begin_scope(
                    local,
                    manager=manager,
                    on_enter=local.reset,
                    on_exit=local.finish,
                    on_abort=local.abort,
                )
            scope.finish()


def test_noop_reentry_error_reaches_real_enclosing_scope() -> None:
    manager = _manager()
    local = _LocalPass()
    failure = ValueError("nested error")
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(ValueError) as raised:
        with attempt:
            with attempt.scope(
                local,
                manager=manager,
                on_enter=local.reset,
                on_exit=local.finish,
                on_abort=local.abort,
            ):
                with attempt.scope(
                    local,
                    manager=manager,
                    on_enter=local.reset,
                    on_exit=local.finish,
                    on_abort=local.abort,
                ):
                    raise failure
    assert raised.value is failure
    assert local.events == ["reset", "abort"]
    assert attempt.first_failure is failure


def test_leaked_scopes_abort_in_reverse_entry_order() -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    events: list[str] = []
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(RenderAttemptAborted, match="aborted"):
        with attempt:
            for name in ("parent", "child"):
                attempt.begin_scope(
                    object(),
                    manager=manager,
                    on_enter=lambda: None,
                    on_exit=lambda: None,
                    on_abort=lambda name=name: events.append(name),
                )
            values.working.value = 9
    assert events == ["child", "parent"]
    assert values.current.value == 1
    assert manager.active_transaction_for(RENDER_KEY) is None


@pytest.mark.parametrize("replace", (False, True))
def test_lost_owned_token_never_adopts_or_rolls_back_replacement(replace: bool) -> None:
    manager = _manager()
    local = _LocalPass()
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    manager.rollback(RENDER_KEY)
    replacement = manager.begin(RENDER_KEY) if replace else None
    with pytest.raises(RenderAttemptIncomplete):
        with attempt:
            pass
    assert manager.active_transaction_for(RENDER_KEY) is replacement
    assert not attempt.reuse_ready
    assert local.events == []
    if replace:
        manager.rollback(RENDER_KEY)


def test_borrower_rejects_different_manager_before_local_reset() -> None:
    manager = _manager()
    other_manager = _manager()
    local = _LocalPass()
    with pytest.raises(RenderAttemptAborted):
        with _RenderAttempt.start(manager, RENDER_KEY) as attempt:
            with pytest.raises(RuntimeError, match="different transaction manager"):
                with attempt.scope(
                    local,
                    manager=other_manager,
                    on_enter=local.reset,
                    on_exit=local.finish,
                    on_abort=local.abort,
                ):
                    pytest.fail("must not enter")
    assert local.events == []


def test_external_active_key_is_rejected_without_begin_or_reset() -> None:
    manager = _manager()
    external = manager.begin(RENDER_KEY)
    with pytest.raises(RuntimeError, match="already active"):
        _RenderAttempt.start(manager, RENDER_KEY)
    assert manager.active_transaction_for(RENDER_KEY) is external
    assert manager.commit(RENDER_KEY) == external.tx_id


def test_explicit_local_abort_and_exit_failure_discard_candidates() -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    local = _LocalPass()
    with pytest.raises(RenderAttemptAborted):
        with _RenderAttempt.start(manager, RENDER_KEY) as attempt:
            scope = attempt.begin_scope(
                local,
                manager=manager,
                on_enter=local.reset,
                on_exit=local.finish,
                on_abort=local.abort,
            )
            values.working.value = 9
            scope.abort(ValueError("explicit abort"))
    assert values.current.value == 1
    with pytest.raises(ValueError, match="local exit failed"):
        with _RenderAttempt.start(manager, RENDER_KEY) as attempt:
            with attempt.scope(
                local,
                manager=manager,
                on_enter=local.reset,
                on_exit=_raise_exit,
                on_abort=local.abort,
            ):
                values.working.value = 10
    assert values.current.value == 1
    assert manager.active_transaction_for(RENDER_KEY) is None


def test_entry_failure_runs_local_cleanup_and_preserves_original_error() -> None:
    manager = _manager()
    local = _LocalPass()
    with pytest.raises(ValueError, match="local exit failed"):
        with _RenderAttempt.start(manager, RENDER_KEY) as attempt:
            with attempt.scope(
                local,
                manager=manager,
                on_enter=_raise_exit,
                on_exit=local.finish,
                on_abort=local.abort,
            ):
                pytest.fail("must not enter")
    assert local.events == ["abort"]
    assert attempt.reuse_ready


def test_cleanup_error_keeps_primary_failure_and_blocks_reuse() -> None:
    manager = _manager()
    primary = ValueError("body failed")
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(ExceptionGroup) as raised:
        with attempt:
            attempt.begin_scope(
                object(),
                manager=manager,
                on_enter=lambda: None,
                on_exit=lambda: None,
                on_abort=_raise_cleanup,
            )
            raise primary
    assert raised.value.exceptions[0] is primary
    assert isinstance(raised.value.exceptions[1], LookupError)
    assert attempt.first_failure is primary
    assert attempt.finished and not attempt.reuse_ready
    assert manager.active_transaction_for(RENDER_KEY) is None


def test_local_cleanup_failure_is_not_reported_twice_on_outer_exit() -> None:
    manager = _manager()
    primary = ValueError("body failed")
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(ExceptionGroup) as raised:
        with attempt:
            with attempt.scope(
                object(),
                manager=manager,
                on_enter=lambda: None,
                on_exit=lambda: None,
                on_abort=_raise_cleanup,
            ):
                raise primary
    assert raised.value.exceptions[0] is primary
    assert len(raised.value.exceptions) == 2
    assert not attempt.reuse_ready


def test_failed_cleanup_does_not_skip_remaining_open_scopes() -> None:
    manager = _manager()
    events: list[str] = []
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(ExceptionGroup):
        with attempt:
            attempt.begin_scope(
                object(),
                manager=manager,
                on_enter=lambda: None,
                on_exit=lambda: None,
                on_abort=lambda: events.append("parent aborted"),
            )
            attempt.begin_scope(
                object(),
                manager=manager,
                on_enter=lambda: None,
                on_exit=lambda: None,
                on_abort=_raise_cleanup,
            )
    assert events == ["parent aborted"]
    assert manager.active_transaction_for(RENDER_KEY) is None
    assert not attempt.reuse_ready


def test_replaced_transaction_on_borrower_entry_is_rejected_before_reset() -> None:
    manager = _manager()
    local = _LocalPass()
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(RenderAttemptIncomplete):
        with attempt:
            manager.rollback(RENDER_KEY)
            replacement = manager.begin(RENDER_KEY)
            with pytest.raises(RuntimeError, match="missing or replaced"):
                with attempt.scope(
                    local,
                    manager=manager,
                    on_enter=local.reset,
                    on_exit=local.finish,
                    on_abort=local.abort,
                ):
                    pytest.fail("must not enter")
    assert manager.active_transaction_for(RENDER_KEY) is replacement
    assert local.events == []
    assert not attempt.reuse_ready
    manager.rollback(RENDER_KEY)


def test_external_nested_begin_cannot_turn_finish_into_success() -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(RenderAttemptIncomplete) as raised:
        with attempt:
            manager.begin(RENDER_KEY)
            values.working.value = 9
    assert raised.value.__cause__ is attempt.first_failure
    assert "external nested begin" in str(attempt.first_failure)
    assert values.current.value == 1
    assert manager.active_transaction_for(RENDER_KEY) is None
    assert not attempt.reuse_ready


def test_external_publication_is_reported_as_incomplete_not_undone() -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(RuntimeError, match="completion is incomplete"):
        with attempt:
            values.working.value = 9
            manager.commit(RENDER_KEY)
    assert values.current.value == 9
    assert attempt.publication_uncertain
    assert not attempt.reuse_ready


def test_nested_owner_scope_cannot_publish_before_outer_exit() -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(RuntimeError, match="owner has already been entered"):
        with attempt:
            values.working.value = 9
            with attempt:
                pytest.fail("must not enter")
    assert values.current.value == 1
    assert manager.active_transaction_for(RENDER_KEY) is None


def test_finishing_callbacks_cannot_admit_render_scope() -> None:
    manager = _manager()
    rejected: list[str] = []
    attempt = _RenderAttempt.start(manager, RENDER_KEY)

    def abort() -> None:
        with pytest.raises(RuntimeError, match="finishing"):
            attempt.begin_scope(
                object(),
                manager=manager,
                on_enter=lambda: rejected.append("reset"),
                on_exit=lambda: None,
                on_abort=lambda: None,
            )
        rejected.append("rejected")

    with pytest.raises(RenderAttemptAborted):
        with attempt:
            attempt.begin_scope(
                object(),
                manager=manager,
                on_enter=lambda: None,
                on_exit=lambda: None,
                on_abort=abort,
            )
    assert rejected == ["rejected"]


def test_repeated_attempts_and_other_keys_remain_independent() -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    other = manager.begin(OTHER_KEY)
    values.working.other = 20
    first = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(RenderAttemptAborted):
        with first:
            values.working.value = 10
            first.fail(ValueError("failed first attempt"))
    assert first.reuse_ready
    assert manager.active_transaction_for(OTHER_KEY) is other
    assert values.current.other == 2
    with first.next_attempt() as second:
        assert second.transaction is not first.transaction
        values.working.value = 11
    assert values.current.value == 11
    assert manager.active_transaction_for(OTHER_KEY) is other
    assert manager.commit(OTHER_KEY) == other.tx_id
    assert values.current.other == 20


@dataclass
class _FaultParticipant:
    manager: TransactionManager
    validate_error: BaseException | None = None
    prepare_error: BaseException | None = None
    apply_error: BaseException | None = None
    after_error: BaseException | None = None
    rollback_error: BaseException | None = None
    on_validate: Callable[[], None] | None = None
    events: list[str] = field(default_factory=list)

    def commit_order_key_for(self, tx_key: Hashable) -> tuple[object, ...]:
        return ()

    def requires_validation_for(self, tx_key: Hashable) -> bool:
        return self.validate_error is not None or self.on_validate is not None

    def validate_commit_for(self, tx_key: Hashable) -> bool:
        self.events.append("validate")
        if self.on_validate is not None:
            self.on_validate()
        if self.validate_error is not None:
            raise self.validate_error
        return True

    def _prepare_commit_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self.events.append("prepare")
        if self.prepare_error is not None:
            raise self.prepare_error

    def _apply_prepared_commit_tx_by_key(
        self, tx_key: Hashable, tx_token: int | None
    ) -> None:
        self.events.append("apply")
        if self.apply_error is not None:
            raise self.apply_error

    def _after_commit_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self.events.append("after")
        if self.after_error is not None:
            raise self.after_error

    def _rollback_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self.events.append("rollback")
        if self.rollback_error is not None:
            raise self.rollback_error

    def _after_rollback_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self.events.append("after rollback")


def test_real_validation_failure_discards_generated_field_candidates() -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    participant = _FaultParticipant(
        manager, validate_error=ValueError("validation failed")
    )
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(ExceptionGroup, match="validation failed"):
        with attempt:
            values.working.value = 9
            manager.enlist(participant, RENDER_KEY)
    assert participant.events == ["validate", "rollback", "after rollback"]
    assert values.current.value == 1
    assert attempt.reuse_ready


def test_validator_reported_failure_prevents_commit_even_without_raising() -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    failure = ValueError("validation poisoned attempt")
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    participant = _FaultParticipant(manager, on_validate=lambda: attempt.fail(failure))
    with pytest.raises(RenderAttemptAborted) as aborted:
        with attempt:
            values.working.value = 9
            manager.enlist(participant, RENDER_KEY)
    assert aborted.value.__cause__ is failure
    assert participant.events == ["validate", "rollback", "after rollback"]
    assert values.current.value == 1


@pytest.mark.parametrize("phase", ("prepare_error", "apply_error", "after_error"))
def test_commit_failure_uses_recorded_outcome_without_second_completion(
    phase: str,
) -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    failure = ValueError("commit failed")
    participant = _FaultParticipant(manager, **{phase: failure})
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(ValueError) as raised:
        with attempt:
            values.working.value = 9
            manager.enlist(participant, RENDER_KEY)
    assert raised.value is failure
    assert attempt.publication_uncertain is (phase == "apply_error")
    assert attempt.finished
    assert attempt.reuse_ready is (phase == "prepare_error")
    assert participant.events.count("rollback") == (0 if phase == "after_error" else 1)
    assert values.current.value == (1 if phase == "prepare_error" else 9)
    if phase != "prepare_error":
        with pytest.raises(RuntimeError, match="not ready for reuse"):
            attempt.next_attempt()
    with pytest.raises(RuntimeError, match="already finished"):
        attempt.finish()


@pytest.mark.parametrize(
    "corruption",
    (
        "missing",
        "wrong_key",
        "wrong_id",
        "not_finalized",
        "ownership_lost",
        "conflicting_flags",
        "invalid_flag",
        "invalid_failures",
    ),
)
def test_missing_or_incoherent_evidence_quarantines_published_values(
    corruption: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    original = manager.commit_only
    calls = []

    def corrupt(self: TransactionManager, tx_key: Hashable) -> int | None:
        calls.append(tx_key)
        result = original(tx_key)
        record = attempt.transaction.completion
        assert record is not None
        changes = {
            "wrong_key": {"tx_key": OTHER_KEY},
            "wrong_id": {"tx_id": record.tx_id + 1},
            "not_finalized": {"finalized": False},
            "ownership_lost": {"ownership_preserved": False},
            "conflicting_flags": {"discard_complete": True},
            "invalid_flag": {"publication_complete": 1},
            "invalid_failures": {"failures": ("not an exception",)},
        }
        attempt.transaction._completion = (
            None if corruption == "missing" else replace(record, **changes[corruption])
        )
        return result

    monkeypatch.setattr(TransactionManager, "commit_only", corrupt)
    with pytest.raises(RenderAttemptIncomplete, match="completion evidence"):
        with attempt:
            values.working.value = 9
    assert values.current.value == 9
    assert attempt.publication_uncertain and not attempt.reuse_ready
    assert calls == [RENDER_KEY]
    with pytest.raises(RuntimeError, match="already finished"):
        attempt.finish()
    assert calls == [RENDER_KEY]


def test_missing_evidence_after_error_preserves_primary_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager = _manager()
    failure = ValueError("after failed")
    participant = _FaultParticipant(manager, after_error=failure)
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    original = manager.commit_only

    def corrupt(self: TransactionManager, tx_key: Hashable) -> int | None:
        try:
            return original(tx_key)
        finally:
            attempt.transaction._completion = None

    monkeypatch.setattr(TransactionManager, "commit_only", corrupt)
    with pytest.raises(ExceptionGroup) as raised:
        with attempt:
            manager.enlist(participant, RENDER_KEY)
    assert raised.value.exceptions[0] is failure
    assert isinstance(raised.value.exceptions[1], RenderAttemptIncomplete)
    assert participant.events == ["prepare", "apply", "after"]
    assert not attempt.reuse_ready


def test_replacement_after_finalization_cannot_supply_completion_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager = _manager()
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    original = manager.commit_only
    replacements = []

    def replace_owner(self: TransactionManager, tx_key: Hashable) -> int | None:
        result = original(tx_key)
        replacements.append(manager.begin(tx_key))
        return result

    monkeypatch.setattr(TransactionManager, "commit_only", replace_owner)
    with pytest.raises(RenderAttemptIncomplete):
        with attempt:
            pass
    assert attempt.transaction.completion.finalized
    assert manager.active_transaction_for(RENDER_KEY) is replacements[0]
    assert attempt.published is None and not attempt.reuse_ready
    manager.rollback(RENDER_KEY)


def test_manager_rollback_failure_is_reported_and_blocks_reuse() -> None:
    manager = _manager()
    primary = ValueError("render failed")
    participant = _FaultParticipant(
        manager, rollback_error=LookupError("rollback failed")
    )
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(ExceptionGroup) as raised:
        with attempt:
            manager.enlist(participant, RENDER_KEY)
            raise primary
    assert raised.value.exceptions[0] is primary
    assert isinstance(raised.value.exceptions[1], LookupError)
    assert participant.events == ["rollback"]
    assert not attempt.reuse_ready
    assert manager.active_transaction_for(RENDER_KEY) is None


@pytest.mark.parametrize("action", ("commit", "discard", "replace"))
def test_validator_exception_after_ownership_loss_blocks_reuse(action: str) -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    primary = ValueError("validator failed after external completion")
    replacements: list[object] = []

    def validate() -> None:
        if action == "commit":
            manager.commit_only(RENDER_KEY)
        else:
            manager.rollback(RENDER_KEY)
            if action == "replace":
                replacements.append(manager.begin(RENDER_KEY))
        raise primary

    participant = _FaultParticipant(manager, on_validate=validate)
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(ExceptionGroup) as raised:
        with attempt:
            values.working.value = 9
            manager.enlist(participant, RENDER_KEY)
    assert primary in raised.value.exceptions[0].exceptions
    assert attempt.first_failure is raised.value.exceptions[0]
    assert attempt.publication_uncertain and not attempt.reuse_ready
    assert values.current.value == (9 if action == "commit" else 1)
    assert manager.active_transaction_for(RENDER_KEY) is (
        replacements[0] if replacements else None
    )
    with pytest.raises(RuntimeError, match="not ready for reuse"):
        attempt.next_attempt()
    if replacements:
        manager.rollback(RENDER_KEY)


def test_failed_attempt_with_external_borrower_cannot_certify_reuse() -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises((RenderAttemptIncomplete, ExceptionGroup)):
        with attempt:
            old_scope = manager.begin(RENDER_KEY)
            values.working.value = 9
            attempt.fail(ValueError("render failed"))
    assert values.current.value == 1
    assert not attempt.reuse_ready
    with pytest.raises(RuntimeError, match="not ready for reuse"):
        attempt.next_attempt()
    replacement = manager.begin(RENDER_KEY)
    values.working.value = 10
    with pytest.raises(RuntimeError, match="stale yidl transaction scope"):
        old_scope.__exit__(None, None, None)
    assert values.current.value == 1
    assert manager.active_transaction_for(RENDER_KEY) is replacement
    manager.rollback(RENDER_KEY)


def test_recursive_local_finish_poison_prevents_publication_when_caught() -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    calls: list[str] = []

    def finish() -> None:
        calls.append("finish")
        if len(calls) == 1:
            scope.finish()

    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(RenderAttemptAborted):
        with attempt:
            scope = attempt.begin_scope(
                object(),
                manager=manager,
                on_enter=lambda: None,
                on_exit=finish,
                on_abort=lambda: calls.append("abort"),
            )
            values.working.value = 9
            with pytest.raises(RuntimeError, match="already completing"):
                scope.finish()
    assert calls == ["finish", "abort"]
    assert attempt.first_failure is not None
    assert values.current.value == 1


@pytest.mark.parametrize("recursive_finish", (False, True))
def test_recursive_local_abort_preserves_primary_and_blocks_reuse(
    recursive_finish: bool,
) -> None:
    manager = _manager()
    primary = ValueError("body failed")
    calls: list[str] = []

    def abort() -> None:
        calls.append("abort")
        if len(calls) == 1:
            if recursive_finish:
                scope.finish()
            else:
                scope.abort(primary)

    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    with pytest.raises(ExceptionGroup) as raised:
        with attempt:
            scope = attempt.begin_scope(
                object(),
                manager=manager,
                on_enter=lambda: None,
                on_exit=lambda: calls.append("finish"),
                on_abort=abort,
            )
            raise primary
    assert calls == ["abort"]
    assert raised.value.exceptions[0] is primary
    assert "already completing" in str(raised.value.exceptions[1])
    assert attempt.first_failure is primary
    assert not attempt.reuse_ready


def test_rollback_callback_cannot_start_replacement_during_cleanup() -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    entered: list[bool] = []

    class Participant(_FaultParticipant):
        def _rollback_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
            with pytest.raises(RuntimeError, match="completing"):
                manager.begin(RENDER_KEY)
            entered.append(True)

    with pytest.raises(RenderAttemptAborted):
        with attempt:
            values.working.value = 9
            manager.enlist(Participant(manager), RENDER_KEY)
            attempt.fail(ValueError("failed"))
    assert entered == [True]
    assert attempt.reuse_ready
    assert values.current.value == 1


def test_local_callback_cannot_finish_owner_before_local_release() -> None:
    manager = _manager()
    values = RenderValues(transaction_manager=manager)
    attempt = _RenderAttempt.start(manager, RENDER_KEY)
    calls: list[str] = []

    def finish() -> None:
        calls.append("finish")
        with pytest.raises(RuntimeError, match="local render scope is completing"):
            attempt.finish()
        assert not attempt.finished

    with pytest.raises(RenderAttemptAborted):
        with attempt:
            scope = attempt.begin_scope(
                object(),
                manager=manager,
                on_enter=lambda: None,
                on_exit=finish,
                on_abort=lambda: calls.append("abort"),
            )
            values.working.value = 9
            scope.finish()
    assert calls == ["finish"]
    assert values.current.value == 1
    assert attempt.reuse_ready
