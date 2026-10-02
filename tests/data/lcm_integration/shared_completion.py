"""Observe completion isolation for generated fields on one shared TM/key."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from yidl_lifecycle.lifecycle import lifecycle, managed
from yidl_lifecycle.transaction_yidl import DEFAULT_TRANSACTION, TransactionManager


@lifecycle
class Probe:
    value: int = managed(default=0)


def _pair() -> tuple[TransactionManager, Probe, Probe]:
    manager = TransactionManager()
    return (
        manager,
        Probe(transaction_manager=manager),
        Probe(transaction_manager=manager),
    )


def _observe(
    manager: TransactionManager, parent: Probe, child: Probe
) -> dict[str, object]:
    return {
        "parent": {"current": parent.current.value, "effective": parent.value},
        "child": {"current": child.current.value, "effective": child.value},
        "active": manager.active_transaction_for(DEFAULT_TRANSACTION) is not None,
        "begin_count": manager.begin_count,
    }


def characterize() -> dict[str, object]:
    result: dict[str, object] = {}

    manager, parent, child = _pair()
    manager.begin(DEFAULT_TRANSACTION)
    parent.value = 10
    manager.begin(DEFAULT_TRANSACTION)
    child.value = 20
    manager.commit(DEFAULT_TRANSACTION)
    result["nested_child_commit"] = _observe(manager, parent, child)
    manager.rollback(DEFAULT_TRANSACTION)
    result["subsequent_parent_rollback"] = _observe(manager, parent, child)

    manager, parent, child = _pair()
    manager.begin(DEFAULT_TRANSACTION)
    parent.value = 10
    child.value = 20
    child.commit(DEFAULT_TRANSACTION)
    result["direct_child_commit"] = _observe(manager, parent, child)

    manager, parent, child = _pair()
    manager.begin(DEFAULT_TRANSACTION)
    parent.value = 10
    manager.begin(DEFAULT_TRANSACTION)
    child.value = 20
    manager.rollback(DEFAULT_TRANSACTION)
    result["caught_child_rollback"] = _observe(manager, parent, child)
    try:
        parent.value = 30
    except RuntimeError as exc:
        result["parent_continuation_error"] = str(exc)
    else:
        result["parent_continuation_error"] = None

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    source = json.dumps(characterize(), indent=2, sort_keys=True) + "\n"
    if options.output is None:
        print(source, end="")
    else:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(source, encoding="utf-8")


if __name__ == "__main__":
    main()
