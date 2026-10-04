# Single-Cohort Render Completion Amendment

## Status And Authority

Status: **DRAFT for dual Consistency/Safety review; no runtime changes.**
Date: 2026-10-03. The user chose one completion cohort for a render attempt,
including nested rendering. Other transaction keys retain application-specific
completion rules. This is a deliberate change from the earlier holder-first
compatibility decision, not a claim that the original runtime behaved this way.

SC2 activation refinement (2026-10-04): the operator selected the private
graph-level field-only gate in `history/lifecycle-integration/PytoLifecyleIntegSC2.md`. That addendum controls
SC2's activation and live-test transition: existing unactivated routes and
historical expectations remain live until SC3. The selected outer ownership
contract below is unchanged; a field-only acceptance is not broad activation.

This amendment controls the completion-owner portions of
`dev-docs/PytoLifecyleIntegPlan.md` and
`dev-docs/PytoLifecyleIntegI3aPlan.md`. Historical reviews remain evidence for
their exact revisions, not acceptance of this amendment. Construction remains
accepted through I1b; I3a implementation is still stopped. Acceptance here would
approve a gated design only, not a roll-build or default-runtime switch.

### Exact Supersession

For render-owned lifecycle candidate values, the following clauses are replaced:

| Earlier Locations | Superseded Rule | Replacement |
| --- | --- | --- |
| Integration plan: Migration First, Checkpoint, Architecture Contract / Existing Boundaries First; One Manager Later, Construction And Initialization, I1, I2, U1/U2 | Preserve nested render managers throughout holder replacement; unify only afterward | One stable manager per root graph; nested renders receive it before initialization. Introduce this through the gated checkpoints below, not a private-slot patch |
| Integration plan: Completion Contract, Proposed Key Assignment, Boundary Ownership, Child Failure Compatibility (D2), Context Pass Orchestration, I0, I2, I3, I5, Test Strategy, Acceptance Checklist, Decisions Required Before Execution (D1/D2) | Preserve early child publication and caught-child recovery | Nested success remains provisional. A failed entered pass poisons the participating render attempt even if caught; outer success cannot publish it |
| Integration plan: Deferred Post-Integration Work (D1), U1/U2 | Outer render publication is a deferred alternative; later unification must preserve independent nested completion | Outer render-value publication is the selected target. No savepoints, child-selective completion, per-child keys, or replacement cohorts are required |
| Integration plan: Existing TM Limits To Respect, final paragraph | Single outer publication-key design is deferred | Its render-owned-value deferral is replaced by the selected outer `PASS_TX_KEY` owner. The same paragraph's prohibition on inferring all-key/whole-graph atomicity from one manager remains |
| Integration plan: Resources And Bindings, Field And Hook Migration Map, Replacement And Deletion Ledger, I4, I5, I6, Test Strategy, Acceptance Checklist | Independent call-site/render publication is the final compatibility requirement | Render-owned resources must eventually participate in the outer decision through supported adapters. Their current separate implementation remains an explicit migration gate, not the selected end state |
| Integration plan: Event Callback Selection, final deactivation paragraph | I5/I6 must not move retirement to outer success | The render-owned removal decision follows the outer attempt after the SC3/D5 audit. Callback visibility, dispatch closure lifetime, supported cleanup, and the ban on field writes from after-commit remain; unrelated accepted removal still has its own owner |
| I3a addendum: Status And Authority; Completion And Local Pass Contract; Permission And Isolation Gates; Canonical Test Package; Implementation Steps And Exit | No manager sharing/library design; preserve earlier published child UI and local caught recovery | This amendment permits the bounded sharing/owner design; replace those two acceptance outcomes with the new observations below. Other I3a field/writer/removal gates remain |

The replacement is limited to values and actions participating in the same
render attempt. It does not repeal independent root isolation, key permissions,
constructor rules, callback equality, or the prohibition on duplicate field
authority. D2's broader throw-site inventory/savepoints, D3's lifetime/refcount
redesign, and D4/L0's generic failure-draining proposal remain separate. D5 is
affected only where local completion must move to the outer decision; do not
infer approval of a new resource delivery/retirement order without its audit.

SC3-L0 refinement (2026-10-04): `dev-docs/PytoLifecyleIntegSC3-L0Plan.md` names
the exact preparation/after-eligibility clauses it proposes to supersede in
the pinned Phase F-1 plan. Its design gate controls only those bounded D4
differences. The generic library implementation and private consumer still
need their own acceptance; this does not grant D5 or resource activation.

## Evidence And Baseline

Planning source: Pyrolyze `4a2b416afa8dbc7d6c21f4263f2964c69c086676`.
Read dependency code at the committed views below, not dirty working files:

| Repository | Revision |
| --- | --- |
| yidl-lifecycle | `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4` |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` |

`dev-docs/history/lifecycle-integration/PytoLifecyleIntegI3aPreflight.md` records the failed-candidate
publication, permission, and borrowed-entry probes. Its JSON baselines are
historical characterization and must not be rewritten as the target contract.
The final focused preflight passed 29 tests; the full default suite had 819
passes, 13 existing failures, and 20 skips. The broader decomposed subset had
41 passes and 14 existing failures. No runtime edits produced those results.

Two concrete source facts underpin the design:

- `render_context.py::_run_boundary` already distinguishes an outer scheduler
  boundary from nested rendering and coordinates generation at the outer one.
  Its constructor nevertheless allocates a manager for every render context.
- `transaction_yidl.py::GroupTransactionManager` counts nested begins per key;
  inner successful commits only reduce the count. Rollback closes the whole key.
  `TransactionManager.commit(*keys)` completes keys sequentially, not atomically.

Source inspection also found local resource acceptance and callback delivery in
`context_base.py::end_pass`, `render_context.py::end_pass`, component handler
completion, and the legacy `CallSiteContextManager`. Sharing a manager alone
does not migrate those actions or establish whole-render effect atomicity.

## Scope And Vocabulary

- A **root graph** owns one stable lifecycle manager, reused between attempts.
  Different roots have different managers.
- A **render attempt** is one outer scheduled boundary invocation, or one
  standalone outer pass/publication scope. Nested invocations join it.
- A **local pass** performs context-specific reset, visitation, validation, and
  candidate UI assembly. Its successful exit is not publication.
- A **completion owner** is a Pyrolyze-private execution object for one attempt.
  It owns the explicit render key begin and final commit/rollback decision.
- `PASS_TX_KEY` is the existing semantic key for this first migration. Other
  keys remain configured and protected, but are not activated or finished by
  this owner implicitly. This is not a universal default-key transaction.

Each queued independently scheduled rerender starts its own attempt after the
previous one has finished. A scheduler flush is not one batch transaction.
The same child, when invoked inside a parent attempt, is only a borrower.
Do not give that child a different manager just to make its local exit publish.

No new author-facing decorator, context option, transaction-key API, enum,
YIDL grammar, or dynamic key registration is proposed by this bounded amendment.
The original no-library-change assumption was refuted by the SC1 dual review.
On 2026-10-04 the operator authorized the bounded ownership observation and
stale-scope fencing in `history/lifecycle-integration/PytoLifecyleIntegSC1-RemPlan-1.md`. That prerequisite
requires fresh Code/State review; it does not authorize a generic manager
redesign or live render wiring.

## Ownership And Admission

Put the private execution owner in a cohesive module such as
`src/pyrolyze/runtime/context_state_lcm/render_attempt.py`, not in YIDL and not
in a generic resource utility. It is a dataclass with behavior; its storage
contains manager/transaction identity, entered local scope handles, a failure
cause, and completion bookkeeping. It never contains copied field values,
child maps, dirty snapshots, or participant commit callbacks.

The scheduler-root state manager holds the active owner reference. Direct leaf
and structural pass entry resolve the same root and use the same ownership
path; scheduler activity alone is not proof that an owner exists.

1. With no owner, require `PASS_TX_KEY` to be inactive before starting an outer
   attempt. Reject an already-active externally started key before resetting
   local state, starting a generation, or rendering. Arbitrary borrowed external
   transactions have no supported completion contract in this checkpoint.
2. Create the owner, begin `tm.begin(PASS_TX_KEY)` exactly once, and retain the
   returned `LifecycleTransaction` object. Check it against the manager's public
   `active_transaction_for(PASS_TX_KEY)` when admitting later scopes.
3. With an owner, require the same root manager and same active transaction
   object. Admit the scope without another TM begin. An identity mismatch is
   a boundary violation and poisons the owned attempt; never adopt a replacement
   token or silently start a fresh transaction inside it.
4. Ordinary local scoped re-entry into the same active context remains a no-op;
   it neither resets values nor adds another completion claim. Direct duplicate
   `begin_pass` remains a diagnostic, even with an empty child map.
5. Successful borrower exit removes its own local handle only. The outer owner
   may complete only after all genuinely entered borrower scopes have exited.
   A leaked borrower blocks publication and sends the owner to failure cleanup;
   it does not authorize guessing that the borrower succeeded.
6. An attempt cannot replace itself while unwinding or publishing. Completion
   callbacks that render synchronously must be deferred/rejected at this private
   boundary, not attach to a finishing token. Subsequent scheduled work runs
   under a new owner after teardown.

Nested TM counts remain a library feature, but this integration does not create
a second begin for each local pass. One owner plus tracked local scope exits
is sufficient. No public claim is made about asynchronous/parallel rendering.

## Local Pass And Failure Rules

Keep `_pass_active` or equivalent local scope storage distinct from key activity.
`require_active_scope` means this context entered a local pass. A private key
predicate is used for managed write permissions and publication-scope admission.
Fix `pass_scope`, `_PassScopeHandle`, `_finish_context_pass`, direct native leaf
execution, directive handles, keyed-loop handles, and derived overrides together.

Actual entry resets own candidate UI and visitation exactly once. Success does
domain validation/UI assembly and releases local activity without committing.
The completion owner, not `_pass_started_tx` on every context, owns the TM.
Remove `_pass_started_tx` only once all old callers use the new owner; do not
leave two competing completion mechanisms active.

An exception escaping an entered local pass or an entered render callback, an
explicit `rollback_pass`, or a failure during local exit marks the owner failed
before cleanup can itself raise. Keep the first failure cause; later cleanup
errors must not replace it. An exception caught entirely inside user code before
any pass reports failure is not automatically observable or classified here.
A no-op nested scope still lets an escaping error reach its real enclosing scope.

Failure is sticky for that attempt. Catching the child exception, rendering a
fallback, successful sibling work, and later local exits cannot clear it. Failed
candidates may remain working until outer completion, but public readers use
`current`; no later outer commit is allowed. There is no child-local restoration
or fresh-token recovery inside the poisoned attempt.

At outer exit:

- If a body exception is propagating, preserve it and discard owned unpublished
  candidates once. Clean up entered local handles in reverse entry order.
- If the body returns normally but the owner is failed, discard once and raise
  a private `RenderAttemptAborted(RuntimeError)` chained from the first cause.
  Do not silently report render success to the scheduler/generation tracker.
- On clean success with no open borrowers, request one explicit-key TM commit.
  No parent/child field-transfer loops or generated private callbacks are used.
- Always clear the active-owner reference and local completion bookkeeping.
  Unexpected missing/replaced TM identity must be reported, never passed to a
  replacement transaction's rollback. An externally completed owned token is
  unsupported corruption; do not claim its already-published values were undone.

These are pre-publication render-failure rules, not a new generic transaction
rollback API. Cleanup may discard candidates but cannot undo externally applied
effects. A cleanup failure is a reported failure and a reuse-readiness gate;
clearing the manager/owner reference alone is not proof that all fields/resources
are clean. No automatic retry after incomplete cleanup is certified.

## Publication, Generation, And Keys

Candidate UI traversal reads the default/working facade. APIs named
`committed_ui`, `own_committed_ui`, and `own_committed_ui_entries`, plus published
debug/visitor readers, use lifecycle `current`. Parent candidate assembly must
not accidentally use those published readers; separate its internal traversal
explicitly. Replace whole membership maps rather than mutating current dicts.

For a supported clean field-only attempt, finish local assembly first, complete
the lifecycle render key, then commit the existing generation tracker, then
deliver published notifications. On failure before application, discard field
candidates and roll back that generation. Nested boundaries do neither tracker
completion nor published notification delivery.

The owner must distinguish pre-application failure from an exception during
application or after publication before it coordinates generation or cleanup.
The pinned TM does not report that phase through `commit`'s return/exception
surface and can stop after a participant/hook exception. Therefore:

- The first field-only proof must audit every enlisted participant: no user
  apply/after hooks or resource apply callbacks capable of throwing. A failing
  validator/preparation must still prove full discard with this actual tuple.
- Do not widen wiring to callback/resource-bearing routes on the assumption
  that a caught `tm.commit` exception means nothing was published. Such routes
  require the separately reviewed L0 phase/failure-completion prerequisite or
  another explicitly approved bounded mechanism first.
- Never call `rollback` after a known published completion, and never reset the
  generation tracker to fabricate undo after partially applied values. Such an
  unsupported outcome blocks reuse/activation and is reported as incomplete,
  not hidden by a normal-return golden.

Other keys keep existing semantics. The render owner passes `PASS_TX_KEY`
explicitly and neither begins nor finishes default/other spaces. No implicit
all-key `begin`, `commit`, or `rollback` calls are introduced. Unrelated active
keys are not poisoned by a render failure. If an application deliberately
requires atomic multi-key completion, that is a separate contract/design; the
current sequential multi-key API does not provide it.

### Non-Render Registration And Callback Work

The user clarified that registration, attachment, and callback-originated work
can be independently accepted outside rendering. Multiple keys are semantic
permission/completion spaces on the root manager, not multiple nested render
cohorts. An independently completed registration is not undone because a later
render fails. Render-driven removal must remain provisional until that render's
outer decision; immediate detachment cannot be repaired by membership rollback.

SC3's writer audit must name the actual field/registry, entry point, governing
key, and completion owner for both directions. A field has one governing key;
different entry points do not give the same field two independent overlays.
Where both paths touch the same accepted registry, settle explicit write
authorization and removal ordering before routing it live. Do not silently
activate another key, finish its transaction, introduce a new key API, or assume
that independent key completion alone protects a stale render-time removal.
This is a concrete audit requirement, not certification that current registries
already implement the policy or that cross-key transactions are atomic.

## Resource And Field Migration Gates

This amendment chooses the target owner; it does not magically absorb legacy
resource behavior. SC2's field-only proof is not whole-graph acceptance.

Before production-route sharing, inventory every local resource acceptance,
retirement, notification, registry mutation, and external context-manager exit.
Classify it as candidate assembly, rollback cleanup, or published delivery and
show its dependency on accepted lifecycle values. The target is one outer
publication decision for participating render-owned actions. Keep existing
resource ownership/refcount algorithms unless a separate change is approved.
If delaying an action changes subscription/cancellation semantics beyond that
owner shift, stop and discuss its exact old/new sequence before implementation.

In particular, `CallSiteContextManager` still uses `pyrolyze.lifecycle` and
legacy current/working records. It cannot receive a YIDL manager by injection
alone. I4 must replace that authority with supported lifecycle fields/adapters
before it joins the root attempt. Do not infer completion from membership
discard or call `accepted()` at local exit and label it provisional.

Out-of-pass `_invoke_dirty` and `_site_metadata` writes remain permission gates
from the I3a preflight. Keep their current authority and snapshots until a
writer policy is approved and proven. One cohort does not make an ordinary
field rollback-sensitive or permit a managed write on an inactive key.
Visitation remains per local invocation, not a transaction-lifetime transient.
Any later dirty-policy change must preserve invalidations arriving during a
pass rather than consume them accidentally at publication.

## Implementation Checkpoints

This is a reviewed-design sequence, not an unqualified roll-build instruction.
Runtime implementation needs subsequent authorization and TDD. Every checkpoint
states what it does not accept; none may falsely label I3a complete.

### SC1: Private Completion Owner And Local Scope Mechanics

Add the private dataclass/owner with one explicit key begin, identity admission,
borrower tracking, sticky failure, and exactly-once pre-publication finish.
Test against the real lifecycle manager with narrow failure/recognition tests;
do not invent a replacement TM. Initially keep it off unreviewed live resource
paths. SC1 now requires the approved manager ownership prerequisite: observe
sole ownership without publication, fence stale scope callbacks by original
transaction identity, and reject same-key completion reentry. Recheck both
normal and exceptional validation outcomes before certifying reuse.

Cover caught failure, no-op re-entry, leaked borrower, replaced/missing token,
externally active admission rejection, repeated attempts, and cleanup errors.
Accept private mechanics only. Independent code/state review precedes wiring.

### SC2: Canonical Field-Only Render Proof

Use actual root, native leaf, and a resource-free nested component through the
decomposed path. Share the scheduler-root manager in constructor inputs; do not
allocate then patch discarded managers. Route scheduler outer boundaries,
standalone passes, and `publish_write_scope` through the same owner.
Fix local activity and candidate/current reads with their callers as one change.

Write `tests/data/lcm_integration/common_pass_single_cohort.py` and its target
JSON baseline in the existing subprocess harness. Add red target observations
first; retain original/preflight snapshots as historical evidence. No expected
output is obtained by normalizing the two runtimes into equality.

Once the approved behavior changes, replace the current-checkout assertion of
the old decomposed preflight outcome with the target fixture. Preserve the old
script/JSON and source revision for historical reproduction; do not regenerate
it, leave a known-red legacy expectation in the live suite, or hide it behind
an unexplained skip. Keep original-runtime characterization runnable unchanged.

#### Live-Test Transition Ledger

All entries remain unchanged during this design checkpoint and SC1's unwired
mechanics. Transition them in the same implementation checkpoint that changes
their route, never in advance to make a baseline green:

| Live Entry | Checkpoint And Disposition |
| --- | --- |
| `test_context_factories_keep_nested_render_completion_independent` in `tests/test_runtime_context_state_lcm_context_base.py` | SC2 constructor wiring: replace the independent-manager assertion with the root-manager sharing assertion. Keep independent-root isolation as a separate invariant |
| `test_scope_activity_tracks_transaction_state` in that file | SC2 local-scope wiring: active key alone is not local activity; require a genuine entered scope for `require_active_scope`. Preserve a narrow external-active-key rejection diagnostic |
| `_run_leaf_pass` in `tests/test_runtime_context_state_lcm_leaf_rerender.py` | SC2 standalone routing: use the supported outer pass/attempt path instead of externally beginning the TM; retain the existing order/UI success assertions and prove repeated local resets |
| `test_common_pass_preflight_baseline[bare_refactor_lcm]` | SC2: retire its old-current-checkout assertion in favor of the target canonical fixture; retain the old script/JSON as historical reproduction. The original parameter stays live |
| `test_lcm_integration_characterization_baseline[bare_refactor_lcm]` and `baselines/bare_refactor_lcm.json` | Before any changed caught-failure route runs this mixed-resource fixture, split its supported target observations from still-unmigrated resource cases. Preserve the old whole observation at its source revision. Target abort expectations belong to the new canonical fixture; unaffected observations stay live. A still-unmigrated production route keeps its existing expectation until SC3/I4 actually replace it; never mask this with an unconditional skip |

Historical reproduction uses the Pyrolyze source and fixture at
`bad7b1c7eaae6b09eaede3803f036a1cbb9d05d7`, with the pinned dependencies above.
Export the whole repository at that revision into a temporary directory using
`git archive`, then run its documented harness with the pinned source exports.
Do not run its historical expected JSON against a changed current runtime and
call the approved difference one of the unrelated 13/14 failures. Original and
monolithic-runtime characterization remain live and unchanged.

During the transition also audit the rest of the focused suite for key-activity
or direct TM-begin assumptions; this ledger is the known minimum, not permission
to leave a newly discovered opposite-contract assertion unexplained.

Acceptance requires the scenarios below and the field-only participant audit.
It accepts render-value ownership for the proof only, not callback/resource
routes, snapshot removal, full I3a, or default activation. Do not enable broader
production paths or half-wire mixed old/new owners before SC3's gates are met.

### SC3: Publication Adapters And Bounded Live Routing

Finish the affected resource/notification audit, settle any pending L0/D5
prerequisite, and move participating local delivery to the outer decision
without duplicating lifecycle field preparation/publication. Record each
removed local completion caller and each remaining resource-specific method.
Call-site legacy holders remain I4 work and cannot be claimed as migrated.

If a live route still owns a separate resource publication or an unclassified
throwing apply/after callback, stop its activation; keep it explicitly unmigrated.
Do not solve that gap with savepoints, per-slot TMs, snapshots, or a broad new
lifetime policy. Review each bounded adapter implementation independently.

### SC4: Resume And Complete I3a

With completion ownership proven, return to the common value/writer migration:
settle dirty and site-metadata policies, remove `_pass_child_order` and
`_pass_child_dirty` only when lifecycle discard and domain cleanup actually
replace them, and complete the existing field/access/deletion ledger.

I3a accepts only after those gates and canonical observations pass. Continue
I3b/I3c/I4 afterward; switching defaults, broad debt repair, and full graph
atomicity are not implied by a successful SC2 or SC3.

## Required Canonical Observations

Use generic-backend authored paths when needed and direct small observations
for local mechanics. Do not duplicate success assertions in bespoke unit tests.
The target fixture records manager identity, local activity, candidate/current
values, generation visibility, and completion-call observations without writes
to generated private state or mocked transaction semantics.

| Scenario | Required Result |
| --- | --- |
| Clean parent/leaf/nested component | Same root manager; nested successful local exit leaves current values old; outer success publishes every participating candidate once |
| Child emits then raises; parent catches | Owner stays failed; current UI stays old; outer normal return raises abort with original cause; no candidate is published |
| Child succeeds; parent later raises | Both child and parent candidate UI/membership are discarded; neither success was published early |
| Later sibling succeeds after caught failure | Still failed; sibling does not make the attempt committable |
| Subsequent fresh attempt | Empty local scope/owner state, new transaction identity; successful rendering works after complete cleanup |
| Borrowed entry with empty child map | Resets local own UI/visitation despite active key; no duplicate TM begin; duplicate direct begin diagnoses |
| Published readers during rendering | Public committed readers show current; internal parent assembly sees candidates |
| Standalone leaf rerender and multiple queued boundaries | Each outer invocation owns one completion; nested calls do not; flush is not one batch |
| Different root graphs | Managers/attempts isolated; a failure in one never finishes another's key |
| Other semantic key | Its fields reject render-key-only writes; an independently active other key survives render commit/rollback and retains its own completion owner |
| Validation/preparation failure in supported field-only proof | No field application, complete discard, no advanced committed generation, original error retained, next attempt succeeds |

Narrow diagnostics must also test entry/reset failure, identity corruption,
leaked handles, rollback cleanup failure, and post-publication no-fictitious-undo
guard behavior. A real throwing apply/after-hook scenario belongs to the L0
prerequisite and blocks widening the route; do not replace it with a mock that
makes the pinned TM appear to have a phase-aware outcome API.

## Review And Verification

Settle this document, precedence notices, and the preflight characterization at
one exact Pyrolyze commit. Run fresh peer-blind Consistency/Safety reviewers
against committed dependency views. Review is of the gated amendment only;
there is no new public surface freeze requiring a Surface-axis walkthrough.
File complete reports verbatim and resolve all P0/P1/P2 before acceptance.

Exclude dirty lazy/mutable lifecycle work, YIDL extraction/document/paper work,
and parent/unrelated submodule changes. No dependency edits, parent pointer,
tags, push, merge, worktree, or default switch are authorized here.

For implementation checkpoints, use the focused five-file suite documented in
`dev-docs/history/lifecycle-integration/PytoLifecyleIntegI3aPreflight.md`, adding the canonical target entry;
run the full default and broader decomposed suites and classify exact failure
name deltas. Keep the existing 13/14 failure debt visible. Documentation-only
review acceptance is not a new full-suite green claim.
