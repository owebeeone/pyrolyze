# SC3-L0 Lifecycle Completion Contract

## Status And Authority

Status: **DRAFT for dual Consistency/Safety review; no implementation yet**.
Date: 2026-10-04. The operator approved the original proposal: a reviewed,
bounded lifecycle-library prerequisite before resource publication adapters.

This specializes the L0 requirement in `PytoLifecyleIntegPlan.md` and the
phase-awareness gate in `PytoLifecyleIntegSingleCohortPlan.md`. It changes the
completion failure contract, not lifecycle field meanings, key membership,
ownership/refcounts, marker signatures, YIDL grammar, or resource algorithms.
`PytoLifecyleIntegSC3.md` supplies the actual caller/writer audit and evidence.

Document acceptance approves this library design only. Runtime implementation
and its exact accepted tuple need a separate gate; no SC3 live resource route,
I3a completion, or default activation is accepted by either checkpoint.

## Baseline And Ownership

Library baseline: yidl-lifecycle
`335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`. Consumer baseline: Pyrolyze
`407592f6a52f54e55833c4b1cfe7cae62959dfa3`. YIDL and Astichi remain pinned to
`95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` and
`387ca5e1da76204ee60922094734c13ee36383c0`, respectively.

The library owns `src/yidl_lifecycle/transaction_yidl.py`, generated independent
hook dispatch in `src/yidl_lifecycle/yidl/lifecycle_core.yidl`, its generated
decorator artifact, documentation, narrow tests, and generated goldens.
Generic YIDL/Astichi compiler changes are not authorized. If existing holes
cannot express the needed hook wrapper, stop and propose that exact limitation.

Read committed dependency views. Existing uncommitted lazy/mutable marker,
harvester, generated-source, docs, and golden changes are not part of L0.
Implementation must preserve them, never revert or silently include them in
the accepted checkpoint. If separating generated artifacts requires merging
those unrelated features, stop and settle an explicit prerequisite tuple.

## Unchanged Compatibility Surface

- Existing `begin`, `validate`, `commit`, `commit_only`, `rollback`, `enlist`,
  `drop`, scope binding, token identity, explicit keys, and nested-count rules
  remain. Inner successful completion returns `None` and does not finalize.
- A clean final completion still returns its existing integer token. Multi-key
  results remain sequential tuples, not atomic whole-manager completion.
- Original transaction identity, not a latest-token lookup by key, fences
  retained scopes. A stale rollback cannot touch a replacement transaction.
- Keep legacy apply/rollback callback fallback where already supported. Missing
  optional prepare/after callbacks remain no-ops; missing required application
  or discard callback is a contextual failure, not a silent success.
- No public field marker/decorator option is added. The completion observation
  below is a low-level runtime-support API, not an author-facing transaction
  mode or a replacement for the manager's completion methods.

## Token-Bound Completion Observation

Add a read-only `LifecycleTransaction.completion` property, backed privately.
It is `None` until this specific transaction has terminal completion evidence.
It remains readable on the retained transaction after the manager clears its
active token. Never return another transaction's outcome for the same key.

The immutable `TransactionCompletion` is a frozen slotted dataclass with:

```python
@dataclass(frozen=True, slots=True)
class TransactionCompletion:
    tx_key: Hashable
    tx_id: int
    publication_started: bool
    publication_complete: bool
    discard_complete: bool
    after_actions_complete: bool
    ownership_preserved: bool
    finalized: bool
    failures: tuple[BaseException, ...]
```

These are independently observable facts, not an enum encoded in strings.
The library constructs coherent records; callers do not supply flags.

| Observation | Exact Meaning |
| --- | --- |
| `publication_started` | At least one application callback was invoked; set before invoking it, because a callback may mutate then raise |
| `publication_complete` | Every required application callback returned normally, or the successful application phase had no participants |
| `discard_complete` | Every required pending-value discard callback returned normally, or the discard phase had no participants; it never means undo of current values |
| `after_actions_complete` | Every eligible independent after action returned normally; attempting all actions despite errors does not make this true |
| `ownership_preserved` | The manager retained the original transaction and its completion authority throughout; no replacement, unexpected nested begin, or unsupported membership mutation occurred |
| `finalized` | This transaction's manager ownership/nesting was finalized; it does not certify field or resource cleanup |
| `failures` | Original failures in deterministic occurrence order, including contextual hook groups and later cleanup errors; no error is erased by resetting the key |

The record is installed before a completion call raises or returns, after its
finalization path. Nested nonfinal commits leave it `None`. A stale scoped exit
does not replace an already terminal record. A public `validate()` observation
alone does not finalize and does not publish a completion record.

When no application starts and discard succeeds, the outcome certifies no
manager-applied publication, even if an after-rollback action failed. When all
application succeeds and an after-commit action fails, it certifies publication
but not completion-action success. Partial or throwing application does not
certify that failed callbacks made no current-value mutation.

Ownership loss makes application certainty unavailable to the consumer even
if the record's local callback facts would otherwise look successful. Never
rollback a replacement token or claim externally published values were undone.

## Completion Algorithm

Use one cohesive internal dataclass/session with behavior to collect outcome
facts and original errors. Do not add a magic phase tag or a second callback
engine in Pyrolyze. Retain the original token throughout the manager operation.

### Participant And Order Boundary

At actual final completion, capture the dirty participant identity sequence in
enlistment order. Compute the existing descending commit-order-key ordering
once for preparation/application/after-commit. Equal keys retain enlistment
order. If key computation fails, no application begins; discard the captured
participants in enlistment order and report the ordering failure plus cleanup.

The final-completion guard covers validation, ordering, preparation,
application, and after/cleanup dispatch. Same-key begin/commit/rollback reentry
is rejected before it can mutate manager ownership; other keys remain separate.
Standalone `validate()` retains its existing observation/identity contract.

Preparation hooks may stage more fields of an already captured participant.
They may not add/drop another participant while completion is underway. Reject
membership changes before manager insertion/removal, with key/token context.
Once application begins, re-enlistment is rejected, including the same
participant from an after hook. No after hook may create a fresh working
overlay on the completing token. Audit existing consumers before enforcing
these guards; a legitimate incompatible use is a stop-and-discuss boundary,
not permission to drop its work silently.

### Validate And Prepare

For `commit`, validate before any preparation/application. Keep existing
validator aggregation. For `commit_only`, preserve its deliberate validation
bypass; Pyrolyze's owner already performs standalone validation first.

Stop dependent preparation after its first failure. There is no benefit in
continuing later conversions once no publication is allowed. Attempt discard
for every captured dirty participant, including ones not prepared, then attempt
every eligible after-rollback callback. Preserve the original validation,
ordering, or preparation failure ahead of cleanup errors.

### Apply And Unexpected Application Failure

Preparation success makes all captured participants application candidates.
Attempt each application once in the fixed commit order, even when an earlier
application unexpectedly raises. Record which callbacks returned normally and
which failed. Do not retry an application callback or roll back applied current
values. An application failure always prevents `publication_complete=True`.

For failed application participants, attempt their pending-value discard once
to clear remaining working/staged state. This is not current-value restoration.
Run after-commit only for participants whose application returned normally;
run after-rollback only for failed-application participants whose discard
returned normally. A failed discard blocks that participant's dependent after
action; still attempt other independent participants. Report the partial
outcome and every error. A consumer must not treat this as a successful render
or certify automatic reuse, even if later application succeeded.

This is the bounded unexpected-apply drain/report policy, not atomic undo or a
savepoint. Any callback contract that cannot clear only pending work through
its rollback callback must be identified before it can use this partial path.

### Explicit Rollback And Cleanup

Rollback attempts pending-value discard for all captured participants in
enlistment order, collecting failures instead of stopping at the first.
After-rollback dispatch follows in the same order for participants whose
discard returned normally. Do not run dependent after-rollback work for a
participant whose discard failed and then claim it was repaired.

Each library phase has one owner and exactly-once attempts. Finalize the
original manager key even when cleanup fails, but report incomplete cleanup
through the token record. This permits the manager to end its ownership; it
does not grant Pyrolyze permission to reuse damaged resources.

### Independent After Hooks Inside One Participant

Keep the current grouping/order of same-key generated hooks, including inherited
and local declarations. Wrap each independently declared after-commit and
after-rollback hook call in its own `try/except BaseException`, collect errors,
and raise them after all eligible hooks have been attempted. Preserve direct
method references; do not introduce `getattr` dispatch or hand-edit generated
code. Before-commit/conversion code remains stop-on-failure preparation.

Within a single user hook, its statements are not independent completion
actions; the generator cannot resume it after an exception. Domain batches
such as `_flush_post_commit` need their own later SC3-D5 adapter. Library
draining must not be advertised as repairing those batches.

## Error Contract

Retain original exception objects and their causes/tracebacks. Add concise
notes naming phase, participant/class, transaction key/token, and generated hook
method where applicable. Diagnostic text may name phases; those strings are
not runtime state tags.

Raise a sole failure unchanged. For multiple independent failures, use
`BaseExceptionGroup`, which yields `ExceptionGroup` for ordinary exceptions
and can also preserve `KeyboardInterrupt`/`SystemExit` during mandatory cleanup.
Keep the original preparation/body failure first and later errors in actual
attempt order. Preserve nested generated-hook groups rather than flattening
away method provenance or duplicating the same original exception.

The immutable completion record remains available regardless of the outward
exception shape. Multi-key wrappers continue completing independent keys and
aggregate contextual errors; they do not infer cross-key field atomicity.

## Consumer Contract (Later SC3 Checkpoint)

Pyrolyze retains the exact original `LifecycleTransaction`, then reads its
completion record after normal return or exception. It also verifies the
original key is finalized and no replacement transaction was adopted.

| Library Outcome | Later Render-Owner Disposition |
| --- | --- |
| No application, successful discard, actions complete, ownership preserved | Discard candidates; rollback generation; clean subsequent attempt permitted |
| No application, discard/action failure | No published generation; preserve original error and cleanup errors; quarantine incomplete cleanup, not automatic reuse |
| Full publication, actions complete | Clear local scratch/reconcile accepted caches, publish generation once; deliver only a reviewed outer-owned domain batch |
| Full publication, after-action failure | Values remain published; generation must reflect those values, not fabricate rollback; report delivery/cleanup failure and apply reviewed resource-readiness policy |
| Partial/uncertain application or ownership loss | No claimed field undo or successful generation; mark incomplete/quarantined, preserve the evidence; no automatic retry or live route acceptance |

Publication and reuse readiness are separate. The current SC2 implementation
uses `reuse_ready` to gate generation/cache completion and `first_failure` to
infer publication; those assumptions must be replaced in the later private
consumer checkpoint. Do not consume the new record by merely changing an
exception handler and leaving either inference in place.

This design does not choose D5's resource retirement/notification order.
Generation versus resource-hook visibility requires an explicit adapter
timeline before resource hooks are installed on live render participants.

## Implementation Checkpoints And Tests

### L0-1: Narrow Manager Outcome And Failure Protocol

Use TDD in `yidl-lifecycle/tests/test_transaction_yidl.py`. Capture the original
counterexamples first: early apply/after-commit/rollback/after-rollback failure,
preparation plus cleanup failure, missing callback, ordering failure, and original
token retained across nested success, final success, and stale scoped exits.

Implement token-bound observation, fixed ordering/membership guards, phase
draining and contextual error aggregation in the library manager. Add narrow
tests for mutation-before-application-error, other-key isolation, repeated same
exception, system-exception cleanup, late enlist/drop/reentry, and poisoned
cleanup. Do not duplicate existing clean-success golden assertions here.

### L0-2: Generated Independent Hook Failure Golden

Author a new canonical fixture such as
`tests/data/gold_src/yidl_transactional_completion_failures.py` in the library's
existing golden harness. Its inherited parent and derived class each declare
same-key after-commit/after-rollback hooks; the first throws, the second records
cleanup. Enlist another generated participant and exercise a conversion/prepare
failure independently. Record current/working outcomes, hook order/count,
key/token completion, useful grouped diagnostics, and a new transaction after
successful discard. Do not demonstrate recovery merely by overwriting stale
work after failed cleanup.

Add the per-hook wrappers through YIDL resources/contributions. Regenerate the
complete decorator and generated output plus existing human-inspection variants.
Review all changed source/goldens; no compiler patch or mechanical global
generated-source rewrite is a substitute for the declarative change.

### L0-3: Library Acceptance And Historical Probe Disposition

Run the library focused protocol/golden targets and full suite at a settled
tuple, then fresh dual Code/State implementation review. Reports must verify
the original counterexamples, generated inherited hook composition, partial
application reporting, key/ownership fencing, and no new marker semantics.

The Pyrolyze historical failure fixture currently pins the old library behavior.
Before consuming the new library tuple, preserve that historical observation
with explicit revision/reproduction and add a separately named target outcome.
Transition its current-library test in the same consumer checkpoint; do not
silently rewrite it or leave a newly changed expected failure classified as
unrelated baseline debt. The default 13/broader 14 debt remains separate.

### SC3-L0 Consumer: Private Owner Only

After library acceptance, update the private owner to use completion evidence,
not guessed phase or copied values. Extend the existing SC2 canonical fixture
for published-after-failure versus unpublished discard/generation outcomes;
narrow fault tests cover late ownership change, incomplete cleanup, missing
evidence, and exactly-once finalization. Re-run all SC1/SC2 original closures,
the focused suite, full default, and broader unactivated suites; review the
settled consumer tuple independently.

Resource admission stays blocked through this checkpoint. The next gate is
the concrete D5/category adapter design, not broad activation or snapshot
deletion. Each library/consumer checkpoint states its accepted scope and any
remaining failure/readiness limitations.

## Stop Conditions

Stop for operator discussion if implementation requires new marker/key syntax,
legacy refcount/ownership changes, compiler work, undo of current values,
unreviewed late-enlist semantics, or inclusion of unrelated dirty library
features to create the accepted generated artifact. Do not solve a blocked
route by copying fields, adding per-slot TMs, or inventing a Pyrolyze participant
dispatcher. No tags, push, merge, worktree, parent-pointer update, or selector
change is included in this design checkpoint.
