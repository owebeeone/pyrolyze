# SC1 Bounded Ownership Remediation

Status: **implemented, pending fresh dual Code/State acceptance**. This does
not accept live render wiring, resource completion, field migration, or I3a.
The original SC1 implementation and reports are historical snapshots; this is
the controlling amendment for the corrected checkpoint.

## Boundary

Only `render_attempt.py`, its mechanics tests, the adjacent manager source/test,
and ownership/review documentation change. No live context call site imports
or invokes the private owner. The operator authorized this bounded manager
prerequisite on 2026-10-04 after the initial dual review refuted the
no-library-change assumption.

`require_sole_transaction_owner(transaction)` is a supported synchronous
nonpublishing manager observation: exact active token identity, same key, not
completing, and one outstanding begin. It does not validate, prepare, publish,
discard, enlist, or alter nesting. The private owner checks it on successful
finish, normal validation return, and discard after failures (including
exceptional validation). Missing/replaced tokens are never rolled back by the
old owner. An external same-key borrower blocks reuse certification.

Manager scope callbacks retain their original token. Stale normal exit raises;
stale exceptional exit is a no-op preserving the body error. Multi-key exits
retain every original token and aggregate failures while attempting each key.
Terminal callback reentry cannot begin/finish the same key; multi-key begin
checks all completion barriers before altering counts. Normal commit cannot
validate one token and then publish a replacement. This is not a lock, a new
key API, savepoints, per-child completion, or atomic cross-key publication.

Each local terminal transition is guarded before callbacks. Recursive finish,
abort, and owner completion during a local terminal callback poison the owner
without running that transition twice. Local release failure is recorded as
cleanup failure. First cause and additional cleanup/ownership errors remain
observable; ordinary sole-owner discard remains reusable. Opaque commit-phase
errors still block reuse and do not claim rollback of published values.

## Closure Matrix

| Prior Finding | Implementation And Counterexample |
| --- | --- |
| Code P2-1; State P2-1 | Real validator externally commits, discards, or replaces the token and then raises; retain its error, detect lost ownership, preserve actually published values/replacement, reject retry |
| Code P2-3; State P2-2 | Recursive finish/abort/finish-during-abort; callbacks/release run once, a caught callback error cannot publish, cleanup errors block reuse |
| Code P2-2 | Failed candidate plus external same-key begin; observe borrowing before rollback, refuse retry certification, stale normal/exceptional exits cannot complete a replacement |

Adjacent guards also cover owner finish during a local terminal callback and
same-key rollback callbacks attempting replacement/multi-key partial begin.
These are tests and claimed dispositions, not self-closure; reviewers must
verify the original counterexamples on the corrected tuple.

## Verification And Reproduction

Use committed dependency exports rather than dirty working copies. Lifecycle
revision is `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL/Astichi stay at the
SC1 pinned revisions in `PytoLifecyleIntegSC1.md`. Export the full lifecycle
repository for its pytest run because its pytest configuration prepends `src`.
Set `$snapshot` to the export root and use the existing Python 3.12 environment:

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

The focused gate passes **64 tests in 11.04s**, including 35 owner mechanics
cases and the unchanged 29-case baseline. Full default regression is
**854 passed, 13 failed, 20 skipped, 1 warning in 47.20s**. Broader decomposed
verification uses `PYROLYZE_CONTEXT_IMPL=bare_refactor_lcm` and the SC1 eight
paths: **41 passed, 14 failed in 2.48s**. Failure identities/clusters are
unchanged from the prior ledger, not fixed or waived here. A mistaken probe
using `bare` hit its interface-only scaffold (16 passed/39 failed); it is not
the decomposed gate and does not replace that evidence.

Manager mechanics pass **18 tests**. The complete clean lifecycle suite is
**273 passed, 1 failed, 46 skipped in 85.57s**. Its one failure is the Phase H
owned-field source golden (`value` vs `value__astichi_scoped_1`). The identical
failure was reproduced at prior lifecycle revision
`1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4` with the same YIDL/Astichi exports
(1 failed, 9 deselected in 6.09s). This is verified baseline debt, not a green
suite claim. No golden is regenerated to conceal a dependency mismatch.

Review tier is fresh dual Code/State because ownership/API assumptions changed.
No author-facing decorator/marker surface is frozen by this private integration
checkpoint. Reviewers inspect the exact committed tuple, exclude unrelated
lazy/static, compiler/paper, and parent work, and return independent reports.
Original reports remain verbatim. Remediation round 1 is pending acceptance;
the two-round architectural cap still applies.
