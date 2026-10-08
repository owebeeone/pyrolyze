from __future__ import annotations

from dataclasses import dataclass

import pytest
from yidl_lifecycle.transaction_yidl import TransactionManager

from pyrolyze.runtime.call_site_context import (
    CallSiteArgs,
    CallSiteBindingBase,
    CallSiteContext,
    CallSiteContextManager,
)


@dataclass(slots=True, eq=False)
class _FailingBinding(CallSiteBindingBase):
    events: list[str]
    name: str
    error: BaseException | None = None

    def _close(self) -> None:
        self.events.append(self.name)
        if self.error is not None:
            raise self.error


def _context(binding: CallSiteBindingBase) -> CallSiteContext:
    return CallSiteContext(binding, None, CallSiteArgs())


def test_collection_uses_yidl_manager_and_has_no_direct_publication_escape() -> None:
    manager = CallSiteContextManager()
    assert type(manager._transaction_manager) is TransactionManager
    assert hasattr(type(manager._pass_context), "__yidl_lifecycle_definition__")
    assert not hasattr(manager, "replace_current")


def test_rollback_drains_cleanup_even_when_a_snapshot_retains_failed_contexts() -> None:
    manager = CallSiteContextManager()
    events: list[str] = []
    error = ValueError("first cleanup")
    first = _context(_FailingBinding(events, "first", error))
    second = _context(_FailingBinding(events, "second"))
    manager.begin_pass()
    manager.mark_visited("first")
    manager.mark_visited("second")
    manager.stage("first", first)
    manager.stage("second", second)

    with pytest.raises(ValueError) as caught:
        manager.rollback_pass()

    assert caught.value is error
    assert events == ["first", "second"]
    assert first.is_closed and second.is_closed
    assert manager.iter_current() == ()
    manager.close_all()
    assert events == ["first", "second"]


def test_failed_retirement_does_not_undo_published_selection_or_skip_cleanup() -> None:
    manager = CallSiteContextManager()
    events: list[str] = []
    error = ValueError("retirement")
    manager.begin_pass()
    for name in ("first", "second"):
        manager.mark_visited(name)
        manager.stage(
            name,
            _context(_FailingBinding(events, name, error if name == "first" else None)),
        )
    manager.commit_pass()
    manager.begin_pass()
    replacement = _context(_FailingBinding(events, "replacement"))
    manager.mark_visited("replacement")
    manager.stage("replacement", replacement)

    with pytest.raises(ValueError) as caught:
        manager.commit_pass()

    assert caught.value is error
    assert events == ["first", "second"]
    assert manager.get_current("replacement") is replacement
    assert replacement.is_accepted
    manager.close_all()
    assert events == ["first", "second", "replacement"]


def test_reselecting_a_current_context_after_a_pending_replacement_retains_it() -> None:
    manager = CallSiteContextManager()
    events: list[str] = []
    original = _context(_FailingBinding(events, "original"))
    manager.begin_pass()
    manager.mark_visited("site")
    manager.stage("site", original)
    manager.commit_pass()
    manager.begin_pass()
    manager.mark_visited("site")
    manager.stage("site", _context(_FailingBinding(events, "abandoned")))
    manager.stage("site", original)
    manager.commit_pass()

    assert events == ["abandoned"]
    assert manager.get_current("site") is original
    assert original.ref_count == 1
    assert not original.is_closed
    manager.close_all()
    assert events == ["abandoned", "original"]


def test_key_hash_cannot_stage_into_a_replacement_transaction() -> None:
    manager = CallSiteContextManager()
    events: list[str] = []
    candidate = _context(_FailingBinding(events, "candidate"))

    class ReplacingKey:
        replace: bool = True

        def __hash__(self) -> int:
            if self.replace:
                self.replace = False
                manager.rollback_pass()
                manager.begin_pass()
            return 1

    manager.begin_pass()
    with pytest.raises(RuntimeError, match="original call-site transaction"):
        manager.stage(ReplacingKey(), candidate)

    assert manager._staged == {}
    assert not candidate.is_closed
    manager.rollback_pass()
    candidate.close()


def test_nested_transaction_exit_does_not_retire_still_current_collection() -> None:
    manager = CallSiteContextManager()
    events: list[str] = []
    original = _context(_FailingBinding(events, "original"))
    candidate = _context(_FailingBinding(events, "candidate"))
    manager.begin_pass()
    manager.mark_visited("site")
    manager.stage("site", original)
    manager.commit_pass()
    manager.begin_pass()
    manager.mark_visited("site")
    manager.stage("site", candidate)
    manager._transaction_manager.begin()
    manager.commit_pass()
    assert manager.get_current("site") is original
    assert not original.is_closed
    assert events == []
    manager.rollback_pass()
    assert events == ["candidate"]
    assert manager.get_current("site") is original
    manager.close_all()
