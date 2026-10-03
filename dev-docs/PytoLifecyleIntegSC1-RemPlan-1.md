# SC1 Review Dispositions And Scope Gate

## Status

Blocked before remediation pending an explicit manager-observation decision.
Both reviewers returned NO-GO at Pyrolyze
`84d4ab6116e0a743394a6269f09e026607402d80`. No finding is self-closed and no
remediation patch or architectural remediation round has been completed.
SC1 remains unaccepted and unwired. SC2 cannot begin on this checkpoint.

## Merged Finding Map

| Root | Reviewer Findings | Disposition | Required Closure Evidence |
| --- | --- | --- | --- |
| Exceptional validation skips identity certification | Code P2-1; State P2-1 | Accept. Recheck ownership on the validation-exception path before reuse certification. Preserve the validator failure, quarantine lost ownership, and never touch a replacement | Parameterized real-manager validator commit/discard/replace followed by failure; ordinary validation failure remains cleanly reusable; published current values are not fabricated back to old values |
| Recursive local terminal callbacks bypass poison/cleanup accounting | Code P2-3; State P2-2 | Accept. Guard each local terminal transition before callbacks, reject recursive/competing finish or abort, release once, and account for bookkeeping failures | Recursive finish, abort, and finish-during-abort; one callback invocation; caught failure still prevents publication; primary cause survives; cleanup failure blocks reuse |
| Failed discard cannot certify sole ownership with an external borrower | Code P2-2 | Accept. The approved pinned public interface is insufficient for the requested certificate; return to the scope/design gate before extending the manager or changing reuse semantics | Poisoned attempt plus external same-key begin; after discard, its stale scope must not be able to publish the next attempt; ordinary sole-owner discard still supports another attempt |

The two independently reproduced shared roots are blind convergence, not
five independent architectural problems. The additional Code finding exposes
a library-observation prerequisite the implementation plan incorrectly treated
as unnecessary.

## Why The Third Root Needs A Decision

The pinned `TransactionManager.active_transaction_for(key)` proves token
identity, but a nested begin returns the same object and increments a count.
`begin_count` is public only for the default key; there is no public per-key
nonpublishing ownership observation for the render key. The clean success path
detects extra nesting through `commit_only` returning `None`, but that is not
an admissible probe for poisoned candidates because it can publish them.

On failed discard, rollback clears the count before the private owner can
observe the borrowed scope. The old scope's callbacks are key-bound, not fenced
against a later transaction identity, so its eventual exit can complete the
next attempt. The review demonstrates this against the real pinned manager.

Rejected workarounds:

- Do not read `_get_group_manager`, `_group_managers`, or transaction scope
  callback internals as a substitute supported interface.
- Do not temporarily commit failed candidates to discover nesting.
- Do not certify every failed attempt reusable, nor silently make every failed
  render permanently unusable; the reviewed design requires ordinary retry.
- Do not add replacement managers, per-context keys, or savepoints to evade
  the single-cohort decision.

Recommended next decision: authorize a bounded, separately tested
yidl-lifecycle ownership-observation/stale-scope-fencing prerequisite. Its exact
shape must let the owner certify sole ownership without publishing and prevent
an old transaction scope from completing a different transaction. A per-key
count alone must not be claimed sufficient without checking callback-time
borrowing and stale exits. The accepted design's "no generic library API change
is needed" assertion must be amended if that prerequisite is approved.

This is not permission to implement a generic manager redesign. The alternative
is an explicitly reviewed narrowing of the reuse guarantee. The lane owner
requests a decision rather than silently picking either route.

## Remediation And Re-Review After The Decision

Add all closure tests first and reproduce the failures. Land one merged patch
covering the approved prerequisite and the two bounded helper corrections, with
focused/full/broader evidence at a new settled dependency tuple. If shared API
or ownership architecture changes, use a fresh dual Code/State review round;
do not carry the old reviewer proofs across that changed boundary.

The original reports remain filed verbatim. Existing live routing, historical
assertions, resource/registration gates, and unrelated dirty repository work
remain untouched. No acceptance, activation, or I3a completion follows from
passing the current 26 mechanics tests.
