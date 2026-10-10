# Lifecycle Integration Goldens

These fixtures exercise the final lifecycle runtime with automatic root
completion. They no longer replay retired engines or activate private rollout
checkpoints. See `dev-docs/LifecycleCompatibilityRetirement.md` for the coverage
mapping and the distinction between current code and historical evidence.

## Coverage

- Construction: inherited field uniqueness, manager injection, completed
  initialization before attachment, and detached constructors.
- Single-cohort completion: publication, abort, caught failure, retry, uncertain
  outcomes, and protocol fault delivery.
- Invocation and selection: leaf arguments, slot-call elision, callbacks,
  component replacement, keyed items, directives, overrides, and pass revisions.
- Resource ownership: subscriptions, effects, async operations, mount
  advertisements, expression resources, cleanup, and retained identity.
- Override read acknowledgment: publication provenance and notification fencing.

`callback_selection.py` is shared observation scaffolding used by the callback
selection golden, not a separate old-engine replay. `shared_completion.py` is a
library capability observation. `transaction_failures.py` and its historical
JSON preserve a pinned protocol trace; the live acceptance target is
`transaction_completion_outcomes.py`.

## Run

From this repository root in the configured workspace environment:

```sh
../.venv/bin/python -m pytest tests/test_lcm_integration_characterization.py -q
```

The installed pytest plugin supplies the compiler import hook. Do not register
that plugin twice. Dynamic authored fixtures use `load_transformed_namespace`.

Each script prints structured observations; pytest compares JSON values, not
formatting. Normal test execution never rewrites expected files. Do not update
baselines merely to hide an unapproved semantic change. Narrow unit tests retain
fault injection and diagnostics that these canonical traces cannot express.

## Historical Evidence

Unused original/bare/monolithic runtime snapshots and their old comparison
scripts were removed during compatibility retirement. Their source revisions
and filed review records remain in Git history and
`dev-docs/history/lifecycle-integration/`.

The pinned historical transaction-manager trace can still be inspected without
changing a checkout:

```sh
../.venv/bin/python tests/data/lcm_integration/transaction_failures.py \
  --historical-manager-source <(git -C ../yidl-lifecycle show \
    371dfa530a975c27f7a6c09a7648f7f00532ab29:src/yidl_lifecycle/transaction_yidl.py)
```

This executes trusted local Python source; do not supply untrusted files.
