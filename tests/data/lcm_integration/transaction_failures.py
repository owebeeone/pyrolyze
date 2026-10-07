"""Observe manager callback delivery; this is not the L0 acceptance contract."""

from __future__ import annotations

import argparse
from collections.abc import Hashable
from dataclasses import dataclass, field
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import Any

from yidl_lifecycle.transaction_yidl import DEFAULT_TRANSACTION, TransactionManager


@dataclass(slots=True)
class Participant:
    name: str
    events: list[list[str]]
    failures: set[str] = field(default_factory=set)
    current: int = 0
    working: int | None = 1
    staged: int | None = None
    token: int | None = None

    def _visit(self, phase: str) -> None:
        self.events.append([self.name, phase])
        if phase in self.failures:
            raise RuntimeError(f"{self.name}: {phase} failed")

    def commit_order_key_for(
        self, tx_key: Hashable = DEFAULT_TRANSACTION
    ) -> tuple[object, ...]:
        return ()

    def requires_validation_for(self, tx_key: Hashable = DEFAULT_TRANSACTION) -> bool:
        return False

    def validate_commit_for(self, tx_key: Hashable = DEFAULT_TRANSACTION) -> bool:
        return True

    def _prepare_commit_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self._visit("prepare")
        self.staged = self.working

    def _apply_prepared_commit_tx_by_key(
        self, tx_key: Hashable, tx_token: int | None
    ) -> None:
        self._visit("apply")
        assert self.staged is not None
        self.current = self.staged
        self.working = self.staged = self.token = None

    def _after_commit_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self._visit("after_commit")

    def _rollback_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self._visit("rollback")
        self.working = self.staged = self.token = None

    def _after_rollback_tx_by_key(self, tx_key: Hashable, tx_token: int | None) -> None:
        self._visit("after_rollback")


def _error(exc: BaseException) -> dict[str, Any]:
    result: dict[str, Any] = {"type": type(exc).__name__, "message": str(exc)}
    if exc.__context__ is not None:
        result["context"] = _error(exc.__context__)
    if isinstance(exc, BaseExceptionGroup):
        result["exceptions"] = [_error(child) for child in exc.exceptions]
    return result


def _observe(
    manager: TransactionManager,
    participants: list[Participant],
    events: list[list[str]],
) -> dict[str, Any]:
    transaction = manager.active_transaction_for(DEFAULT_TRANSACTION)
    return {
        "active_token": None if transaction is None else transaction.tx_id,
        "events": list(events),
        "participants": [
            {
                "name": participant.name,
                "current": participant.current,
                "working": participant.working,
                "staged": participant.staged,
                "token": participant.token,
            }
            for participant in participants
        ],
    }


def _scenario(
    failures: tuple[tuple[int, str], ...], *, rollback: bool = False
) -> dict[str, Any]:
    manager = TransactionManager()
    events: list[list[str]] = []
    participants = [
        Participant(f"participant_{index + 1}", events) for index in range(3)
    ]
    for index, phase in failures:
        participants[index].failures.add(phase)
    manager.begin(DEFAULT_TRANSACTION)
    for participant in participants:
        participant.token = manager.enlist(participant, DEFAULT_TRANSACTION)
    result: dict[str, Any] = {}
    try:
        if rollback:
            manager.rollback(DEFAULT_TRANSACTION)
        else:
            manager.commit(DEFAULT_TRANSACTION)
    except Exception as exc:
        result["error"] = _error(exc)
    result["after_failure"] = _observe(manager, participants, events)

    # Recovery is explicit restaging, not proof that failed cleanup repaired itself.
    events.clear()
    manager.begin(DEFAULT_TRANSACTION)
    for index, participant in enumerate(participants):
        participant.failures.clear()
        participant.working = index + 10
        participant.token = manager.enlist(participant, DEFAULT_TRANSACTION)
    manager.commit(DEFAULT_TRANSACTION)
    result["after_explicit_restaging"] = _observe(manager, participants, events)
    return result


def characterize() -> dict[str, Any]:
    return {
        "prepare": _scenario(((1, "prepare"),)),
        "apply": _scenario(((1, "apply"),)),
        "after_commit": _scenario(((0, "after_commit"),)),
        "rollback": _scenario(((0, "rollback"),), rollback=True),
        "after_rollback": _scenario(((0, "after_rollback"),), rollback=True),
        "prepare_and_rollback": _scenario(((1, "prepare"), (0, "rollback"))),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--historical-manager-source",
        type=Path,
        help="Load a trusted local pre-L0 manager source for historical reproduction",
    )
    options = parser.parse_args()
    if options.historical_manager_source is not None:
        module = ModuleType("_historical_lifecycle_transaction")
        sys.modules[module.__name__] = module
        exec(
            compile(
                options.historical_manager_source.read_text(encoding="utf-8"),
                str(options.historical_manager_source),
                "exec",
            ),
            module.__dict__,
        )
        global TransactionManager, DEFAULT_TRANSACTION
        TransactionManager = module.TransactionManager
        DEFAULT_TRANSACTION = module.DEFAULT_TRANSACTION
    source = json.dumps(characterize(), indent=2, sort_keys=True) + "\n"
    if options.output is None:
        print(source, end="")
    else:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(source, encoding="utf-8")


if __name__ == "__main__":
    main()
