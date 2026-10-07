"""L0 target callback outcomes; the pre-L0 trace stays separately preserved."""

from __future__ import annotations

import json

from transaction_failures import characterize

if __name__ == "__main__":
    observations = characterize()
    # These are the accepted protocol changes, not unconditional retry promises.
    assert [
        row["current"] for row in observations["apply"]["after_failure"]["participants"]
    ] == [1, 0, 1]
    assert observations["after_commit"]["after_failure"]["events"][-1] == [
        "participant_3",
        "after_commit",
    ]
    assert observations["rollback"]["after_failure"]["events"][-1] == [
        "participant_3",
        "after_rollback",
    ]
    assert observations["prepare_and_rollback"]["error"]["type"] == "ExceptionGroup"
    print(json.dumps(observations, indent=2, sort_keys=True))
