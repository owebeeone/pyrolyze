# SC3-L0 Lifecycle Completion Contract

## Status And Authority

Status: **Design accepted at Pyrolyze `715a0074625844afae05d08afc86557d196bdecd`
after fresh Consistency/Safety GO/GO and originating-reviewer closure; no
implementation yet**. Reports and exact dependency tuple are recorded in
`history/lifecycle-integration/PytoLifecyleIntegSC3-L0Plan-ReviewLoop.md`. Acceptance covers this bounded
library design only, not implementation, private consumer adoption, or activation.
Date: 2026-10-04. The operator approved the original proposal: a reviewed,
bounded lifecycle-library prerequisite before resource publication adapters.

This specializes the L0 requirement in `PytoLifecyleIntegPlan.md` and the
phase-awareness gate in `PytoLifecyleIntegSingleCohortPlan.md`. It changes the
completion failure and preparation-write contract, not lifecycle field meanings,
key membership,
ownership/refcounts, marker signatures, YIDL grammar, or resource algorithms.
`PytoLifecyleIntegSC3.md` supplies the actual caller/writer audit and evidence.

Document acceptance approves this library design only. Runtime implementation
and its exact accepted tuple need a separate gate; no SC3 live resource route,
I3a completion, or default activation is accepted by either checkpoint.

### Exact Phase F-1 Supersession

The reference is `yidl-lifecycle/dev-docs/YidlTransactionalYidlPhaseF-1Plan.md`
at library revision `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`. Line numbers
below identify that historical revision, not a moving working copy. This draft
does not claim its pinned implementation already implements Phase F-1 draining.

The unchanged working-copy document now lives in
`yidl-lifecycle/dev-docs/history/transactional-rollout/YidlTransactionalYidlPhaseF-1Plan.md`.
The original path above remains the path to use at the pinned revision.

| Historical Clause | Replacement In This L0 Contract |
| --- | --- |
| Manager Commit Pipeline, lines 666-667 and preparation loop 691-704: every participant gets a prepare attempt after a preparation failure | Stop dependent preparation at its first failure; discard every captured participant, including unprepared ones, then drain eligible after-rollback actions |
| After-commit loop 712-716 and relevant-participant wording 735-740 | Run after-commit for participants whose application returned normally; failed applications receive pending discard and, only after successful discard, after-rollback instead |
| After-rollback loop 750-754 over all dirty participants | Run after-rollback only for participants whose pending discard returned normally; failure skips that participant's dependent after action, not independent participants' cleanup |
| Drain-first generalization 639-642, 664 and 764-769 | Drain independent application, discard, and eligible after actions; dependent preparation remains stop-on-failure. Retain all actually occurring errors, without inventing errors from deliberately unattempted dependent work |

These are the bounded D4 policy differences submitted for design acceptance.
They supersede only the listed preparation/eligibility clauses; fixed keys,
two-phase storage, continued unexpected application, original errors, and
independent generated-hook draining remain. Design GO accepts these differences
only as a design, not blanket Phase F-1 implementation acceptance or D5 timing.
The integration plan's L0 requirement reads through this table; the
single-cohort amendment still leaves the library implementation as a separate
checkpoint.

## Baseline And Ownership

Library baseline: yidl-lifecycle
`335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`. Consumer baseline: Pyrolyze
`407592f6a52f54e55833c4b1cfe7cae62959dfa3`. YIDL and Astichi remain pinned to
`95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` and
`387ca5e1da76204ee60922094734c13ee36383c0`, respectively.

The library owns `src/yidl_lifecycle/transaction_yidl.py`, core preparation/write
boundaries in `src/yidl_lifecycle/yidl/lifecycle_core.yidl`, and the effective
generated hook helpers in `src/yidl_lifecycle/yidl/lifecycle_managed.yidl`.
The complete decorator overrides core hook matchers with managed-layer helpers:
`TransactionHookHelperCall`, `AfterCommitHelperMethodCall`,
`AfterRollbackHelperMethodCall`, and their per-key helper resources must be
covered, not only the core `TransactionHookCall`. Generated managed/owned and
transient writer paths must use the same candidate-write boundary. The scope
also includes the generated decorator artifact, documentation, narrow tests,
and generated goldens.
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
| `discard_complete` | The selected pending-discard phase was entered and every required discard returned normally, including an entered empty phase; false when discard was not entered. In the partial-apply path its obligation is the failed-application subset, not undo of current values |
| `after_actions_complete` | The selected eligible after-action dispatch was entered and all its actions returned normally, including an entered empty dispatch; false if that dispatch was not entered or any eligible action failed |
| `ownership_preserved` | The manager retained the original transaction and its completion authority throughout; no replacement, unexpected nested begin, or unsupported membership mutation occurred |
| `finalized` | This transaction's manager ownership/nesting was finalized; it does not certify field or resource cleanup |
| `failures` | Original failures in deterministic occurrence order, including contextual hook groups and later cleanup errors; no error is erased by resetting the key |

The record is installed before a completion call raises or returns, after its
finalization path. Nested nonfinal commits leave it `None`. A stale scoped exit
does not replace an already terminal record. A public `validate()` observation
alone does not finalize and does not publish a completion record.

All three phase-completion flags start false. An unentered application,
discard, or after-action phase does not become complete merely because its
participant set would be empty. A successful empty commit enters application
and after dispatch: `publication_complete=True`, `publication_started=False`,
`discard_complete=False`, `after_actions_complete=True`. Empty rollback enters
discard and after dispatch, not application. Explicit empty abort has the same
phase facts as empty rollback. Finalization and ownership are separate flags.

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

Preparation hooks may stage fields only within the candidate-write window
below. They may not add/drop another participant while completion is underway.
Reject membership changes before manager insertion/removal, with key/token
context. Once application begins, re-enlistment is rejected, including the same
participant from an after hook. Audit existing consumers before enforcing
these guards; a legitimate incompatible use is a stop-and-discuss boundary,
not permission to drop its work silently.

### Candidate-Write Boundary

Captured membership is not sufficient write permission. The final-completion
session tracks captured participants whose field preparation has not begun,
plus the currently executing before-commit hook window. Generated preparation
opens that window only around before-commit hook dispatch, closes it in a
`finally` before field conversion/staging, and irrevocably closes that target's
write permission before its first field is prepared. Field preparation is
once-only; no automatic re-preparation or field snapshots are introduced.

During final completion, a candidate write is allowed only while that hook
window is open and its target is a captured participant whose preparation
permission has not closed. This permits self-staging in before hooks and
staging a captured later participant before it is prepared. It rejects writes
to an already-prepared target, even from another participant's before hook.
Validation, order-key computation, conversion/staging, application, discard,
and after hooks have no candidate-write window. Other-key permissions and
ordinary writes outside final completion retain their existing rules.

Enforce the rule before changing working storage or invoking a materializing
factory/thaw. Put the manager-owned check in the common generated active/write
helper, passing the state participant identity and key; apply it to setters
and getter paths that create transactional working storage. An existing
working token or non-VOID value must not bypass it. Core preparation must notify
the session at the hook-to-field boundary; managed/owned/transient resources
must not introduce an alternate unchecked writer. This is bounded generated
library work, not a new marker or compiler feature.

Retained mutable working aliases must not be mutated once their target's write
permission closes, or from conversion/application/after callbacks. Only the
permitted before-hook window can mutate such candidates. Python payload aliases
cannot be intercepted by generated property guards: no proxy, defensive copy,
deep-freeze mechanism, or detection guarantee is added here. A callback mutating
a retained alias outside that window violates the callback contract and is not
certified by normal callback returns. Legacy custom participants must obey the
same write restriction; callbacks lacking a before/field boundary must not
stage candidates during their prepare callback. Audit incompatible consumers
and stop rather than silently certify their behavior.

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

Complete all application attempts before discarding failed applications. Then
dispatch each participant's eligible after callback in the fixed commit order:
after-commit for normal application, after-rollback for successful failed-apply
discard, neither for failed discard. This pins attempt/error order without
adding a resource-retirement timeline.

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

### Required Failure Traces

For A then B in both captured and commit order, with omitted callbacks
succeeding, the replacement policies above require these exact sequences:

| Case | Attempts Before Finalization | Original Errors |
| --- | --- | --- |
| A prepare throws `E_A`; B prepare would throw `E_B` | prepare A; discard A; discard B; after-rollback A; after-rollback B. B preparation and all application are unattempted | `E_A` only; do not claim to collect hypothetical `E_B` |
| A apply throws `E_A`; B apply succeeds | prepare A; prepare B; apply A; apply B; discard A; after-rollback A; after-commit B | `E_A`; append actual discard/after failures if any |
| Explicit rollback: A discard throws `E_A`; B discard succeeds | discard A; discard B; after-rollback B. A after-rollback is ineligible | `E_A`; append actual B after failure if any |

If B's before hook tries to change already-prepared A, the write check raises
before any candidate mutation. That is B's preparation failure: no application,
discard A and B, then eligible after-rollback callbacks. Rejecting the write
without changing ownership does not itself mark ownership lost. Retain its
field/participant/key/token context and permit another transaction only after
the discard/action/ownership evidence certifies clean completion.

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
original key is finalized and no replacement transaction was adopted. First
reject missing/incoherent evidence, `finalized=False`, or
`ownership_preserved=False`: quarantine without claiming publication certainty
or adopting a replacement. Only a record passing that authority check enters
the disjoint table below. Predicates refer to the record's named flags, not
the exception shape or guessed phase.

| Disjoint Evidence Predicate | Later Render-Owner Disposition |
| --- | --- |
| `publication_complete` and `after_actions_complete` | Full publication, including successful empty commit: clear local scratch/reconcile accepted caches, publish generation once; deliver only a reviewed outer-owned domain batch |
| `publication_complete` and not `after_actions_complete` | Full publication with action failure: generation must reflect the published values, not fabricate rollback; report failure and apply reviewed resource-readiness policy |
| not `publication_complete`, not `publication_started`, `discard_complete`, and `after_actions_complete` | Unpublished clean discard: discard candidates; rollback generation; clean subsequent attempt permitted, while preserving any original failure |
| not `publication_complete`, not `publication_started`, and not (`discard_complete` and `after_actions_complete`) | Unpublished incomplete cleanup: no published generation; preserve all errors; quarantine rather than automatically reuse |
| not `publication_complete` and `publication_started` | Partial/uncertain application: no claimed field undo or successful generation; quarantine, preserve evidence, and do not automatically retry |

In particular, `publication_started=False` alone never selects rollback.
Successful empty commit is publication-complete without invoking a callback.

| Terminal Case | `publication_started` | `publication_complete` | `discard_complete` | `after_actions_complete` | `ownership_preserved` | `finalized` | Consumer Generation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Empty successful final commit | False | True | False | True | True | True | Commit once |
| Empty explicit rollback | False | False | True | True | True | True | Roll back once |
| Pre-application validation/order/prepare abort; discard/actions succeed | False | False | True | True | True | True | Roll back once; retain original error |
| Full application; an eligible after-commit action fails | True | True | False | False | True | True | Commit once; action failure cannot undo it |
| Pre-application abort; required discard fails; all eligible after actions succeed | False | False | False | True | True | True | Roll back once; quarantine incomplete cleanup |

These example rows do not authorize reuse after missing evidence, ownership
loss, or partial application. An entered after phase can be complete while
discard is incomplete because the failed participant's after action was
ineligible; the predicates still deny reuse.

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

Pin entered/unentered phase flags for empty commit, empty rollback, and
pre-application abort. The later consumer golden owns their generation
decisions; manager tests own the record mechanics, not duplicate rendering
success assertions.

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

Use the complete decorator's managed-layer effective helper/contribution path
as well as any required core boundary. The generated output must show a
separate wrapper for each effective inherited/local after call. Include A
prepared before B, with B's before hook attempting writes to both A's previously
staged field and a previously untouched field in separate scenarios. Both must
reject before mutation/application, drain cleanup, and leave default/current
coherent. Preserve permitted before-hook self-staging and writes to a captured
later unprepared participant; reject conversion/after-hook candidate writes,
including existing-overlay and materializing-getter paths. No golden should
imply the library detects arbitrary retained-payload alias mutation.

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
the canonical fixture must include the empty commit/rollback/abort matrix;
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
