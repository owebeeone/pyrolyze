# SC1: Private Render Completion Mechanics

## Status And Boundary

Implemented, pending independent Code/State acceptance review. Review tier:
dual, because this checkpoint owns transaction completion and failure state.
Controlling design: `PytoLifecyleIntegSingleCohortPlan.md` as accepted at
`3c8a8167830c3c057b91f4ad7b2a0679d13e9ba5`. Implementation base:
`0ab81be3a83eb8a5f3f1ab426353c9eb90c758a7`.

This checkpoint adds only a private owner module and narrow mechanics tests.
It does not wire root/nested renders, resource completion, registration,
generation tracking, dirty/metadata policies, or field migration. The existing
live-test transition ledger remains unchanged. I3a and SC2 are not complete;
there is no selector/default activation, manager-library change, or roll-build.

## Private Implementation

`src/pyrolyze/runtime/context_state_lcm/render_attempt.py` provides:

- `_RenderAttempt.start(manager, tx_key)`: reject an externally active key,
  begin that key once, and retain the actual `LifecycleTransaction` identity.
- `scope(...)`: register a genuinely entered local scope, invoke its reset
  once, and finish local assembly without completing the transaction. Scoped
  re-entry for the same context is a no-op. `begin_scope(...)` instead rejects
  a direct duplicate, even if the context has no children.
- `fail(cause)`: preserve the first reported failure. Caught exceptions,
  successful siblings, and fallback writes cannot clear it.
- `finish(...)`: reject duplicate completion/re-entrant ownership, unwind
  leaked scopes in reverse entry order, and complete only the explicit key.
  Other active keys are neither begun nor finished.
- `reuse_ready` / `next_attempt()`: successful completion or complete discard
  permits a new attempt. Incomplete cleanup, token corruption, or an
  unclassified publication failure does not. SC2 must retain that failed owner
  rather than bypass this readiness check with an unconditional fresh start.

Scope callbacks describe local reset, successful local exit, and local abort;
they are not participant commit callbacks or copied field/dirty/map snapshots.
No root-global registry or new public lifecycle API is introduced here. The
helper accepts an explicit key so it need not import the heavy context classes;
SC2 supplies the existing `PASS_TX_KEY` when wiring the real root.

### Completion And Errors

The pinned public manager permits explicit `validate(key)` followed by
`commit_only(key)`. Validation runs while the owner still knows publication has
not started. On validation failure the owner discards its own transaction,
preserves the validator exception, and includes any cleanup failure. A validator
that reports failure through the owner without raising also blocks publication.

`commit_only` does not report whether an exception arose during prepare, apply,
or after hooks. The owner therefore preserves that exception, marks publication
uncertain, performs no speculative rollback, and blocks reuse. The preparation
failure test proves that the real manager discards generated candidates; the
owner still cannot certify that phase through the generic exception surface.
Apply/after failure tests deliberately show already-applied values remaining,
not fictional undo. Those tests are adversity probes, not approval to wire
throwing/resource participants before L0/SC3.

Missing/replaced transaction identity yields `RenderAttemptIncomplete` and
uncertain publication. An external commit can already have changed current
values; the helper does not label that a successful pre-publication rollback.
It never adopts or rolls back a replacement. A normal-return poisoned attempt
whose owned transaction can be discarded raises `RenderAttemptAborted`, chained
from the first cause. Escaping body exceptions remain primary. Exception groups
preserve additional cleanup errors without reporting the same local cleanup
exception twice, and cleanup continues across remaining local scopes.

An extra external begin of the same token is also diagnosed: `commit_only`
returning `None` means no application occurred. The owner discards its still-
owned transaction but cannot certify the external borrower's reuse contract.
None of these checks supplies savepoints, cross-key atomicity, or parallel/
asynchronous rendering semantics.

## Tests And Participant Audit

`tests/test_runtime_context_state_lcm_render_attempt.py` uses the actual pinned
`TransactionManager`, not a replacement manager or mocked transaction methods.
The generated `RenderValues` class has one managed integer for the render key
and one for an unrelated key, with no user apply/after callbacks, resources,
conversions, or external notifications. Protocol participants inject validation,
prepare, apply, after, and rollback failures into that real manager.

The narrow tests cover local success remaining provisional, caught-failure
poisoning/first cause, scoped no-op re-entry, direct duplicate admission,
escaping no-op errors, reverse leak cleanup, lost/replaced/external tokens,
wrong-manager admission, external publication, explicit abort, entry/exit
failure, cleanup failure/continuation, finishing callback rejection, duplicate
owner entry, repeated attempts, and independent keys. Canonical authored render
success remains SC2 work; no duplicate end-to-end golden is added prematurely.

Red evidence: collection initially failed because the owner module did not
exist. Subsequent narrow regressions reproduced duplicate cleanup reporting,
token-loss misclassification, nested-owner entry, and an incorrect
pre-publication claim after an external commit before their fixes.

The pinned decorator cannot currently generate an underscore-prefixed user
class name without a name-mangling error. The fixture uses `RenderValues`;
fixing that unrelated library defect is not part of SC1.

## Reproduction

Run from the Pyrolyze repository with Python 3.12 and the existing workspace
test environment. Export dependency `src` trees as documented in
`PytoLifecyleIntegI3aPreflight.md`; do not use the dirty dependency checkouts:

| Dependency | Pinned Revision |
| --- | --- |
| yidl-lifecycle | `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4` |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` |

After setting `$snapshot` to those read-only exports:

```sh
export PYTHONPATH="src:$snapshot/yidl-lifecycle/src:$snapshot/yidl/src:$snapshot/astichi/src"
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM \
    PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider -q --tb=short \
    tests/test_runtime_context_state_lcm_render_attempt.py \
    tests/test_runtime_context_state_lcm_construction.py \
    tests/test_runtime_context_state_lcm_context_base.py \
    tests/test_runtime_context_state_lcm_slot_expr.py \
    tests/test_runtime_context_state_lcm_leaf_rerender.py \
    tests/test_lcm_integration_characterization.py
```

Full regression uses the same environment with no test-path arguments and
`--tb=line`. The broader decomposed subset uses the eight test paths recorded
in the preflight with `PYROLYZE_CONTEXT_IMPL=bare_refactor_lcm`; the environment
selector does not change the checked-in default.

Verification results and exact implementation/review tuple are recorded in the
adjacent SC1 review-loop ledger after the gates finish. Existing 13 default-
suite and 14 broader decomposed failures are not fixed or waived by this
checkpoint. No live failure expectation is rewritten into the target semantics.

## Next Gate

Independent Code/State review must accept these private mechanics before SC2.
SC2 supplies the canonical field-only render fixture and actual root/local-
scope wiring. Resource and registration completion remain separately gated;
accepting this owner alone cannot authorize those paths or claim I3a complete.
