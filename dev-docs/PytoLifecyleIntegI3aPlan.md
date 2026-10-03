# I3a: Common Pass And Value Migration Addendum

## Status And Authority

**Current authority amendment (2026-10-03):**
`dev-docs/PytoLifecyleIntegSingleCohortPlan.md` supersedes this addendum's
preservation of independent child publication/caught-child recovery and its
prohibition on the bounded render-manager sharing design. It selects one outer
completion owner and sticky render-attempt failure, not savepoints or selective
child completion. That DRAFT needs independent review before runtime changes.
This document's field permissions, read-facade split, local resets, removal
gates, and outstanding I3a work still apply where not explicitly replaced.
The earlier acceptance ledger/reports certify only their exact historical
revision, not the new contract.

Status: **DRAFT for focused Consistency/Safety review.** This is a plan-only
checkpoint, not authorization to implement or evidence that I3a is complete.

The controlling document is `dev-docs/PytoLifecyleIntegPlan.md`, especially
Migration First, Completion Contract, I2, and I3a. This addendum makes the next
checkpoint concrete; it does not supersede those contracts. I1b accepted
construction and post-construction attachment only. Dirty/seen/site metadata
and pass publication were expressly left unfinished in
`dev-docs/PytoLifecyleIntegI1bEvidence.md`.

Implement only the decomposed path: `src/pyrolyze/runtime/context_state_lcm/`
and its owner facade in `src/pyrolyze/runtime/context_bare_refactor_lcm.py`.
Original and monolithic LCM remain behavioral references. Do not switch the
runtime default, unify managers, repair unrelated failures, migrate callbacks
or resources, or change YIDL/Astichi/library APIs in this checkpoint.

## Baseline

Planning source: Pyrolyze `5af937343ef3e557667d96bbf6830acce555353a`.
Controlling plan blob: `81d004dc44bc84516a3484e2a64be9667f0657bc`.
Committed dependency views: yidl-lifecycle
`1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4`, YIDL
`95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`, Astichi
`387ca5e1da76204ee60922094734c13ee36383c0`.

The five-file command below passed **27 tests in 4.41s** during drafting.
That run used the working dependencies, including uncommitted lazy/mutable
library changes. Those changes and the independent paper-writing lane are
excluded from this document review. Reviewers use committed dependency views;
an implementation checkpoint must separately settle its actual dependency
tuple and rerun verification. The older full-suite/decomposed-suite failures
remain recorded debt, not newly reproduced or repaired here.

## What Must Disappear

`ContextBaseStateMgr` already declares managed child membership and UI values,
but its pass methods still preserve `_pass_child_order` and
`_pass_child_dirty`. `is_scope_active()` currently means that the manager's
`PASS_TX_KEY` is active, not that this context entered a pass. Consequently a
borrowed transaction can skip local entry/reset, and the child-order tuple is
an unreliable re-entry guard when the child map is empty.

The goal is lifecycle-owned candidate publication/discard, plus explicit local
pass bookkeeping. It is not moving render traversal into the transaction
manager or replacing one application snapshot engine with another.

## Field And Access Contract

Before edits, record each affected declaration, every writer, read facade,
manager/key cohort, and completion owner. The following classification is the
target; the permission/isolation gates below are mandatory, not assumptions.

| Value | Authority And Access | Compatibility Requirement |
| --- | --- | --- |
| Owner/render/parent/slot identity | Existing I1b declarations and constructor inputs | Keep existing const versus writable overrides and attachment order; no initializer changes |
| `children_state` | Existing managed map, `PASS_TX_KEY`; candidate reads while rendering, `current` reads for published membership | Replace whole maps; never mutate a current dict in place. Restore membership and insertion order by lifecycle discard, not a saved key tuple |
| `ui_state`, `own_ui_state`, `own_ui_entries_state` | Existing managed tuples, `PASS_TX_KEY` | Assemble candidates in domain code; public committed-UI methods read `current`. Failed unpublished candidates do not alter those values |
| `_invoke_dirty` | Published invalidation flag with pass-local candidate clearing | Lifecycle owns rollback-sensitive clearing. Preserve invalidation writes outside a pass and their visibility; choose its declaration/key only after the writer/cohort probe |
| `_seen_in_pass` | Local visitation, not a published value or a transaction-lifetime transient | Keep one ordinary nontransactional lifecycle field; reset at each actual local entry, preserve existing rollback cleanup values. Do not depend on TM completion to reset it |
| `_site_metadata` | Published invocation/site selection, candidate during a pass | Migrate to managed storage only with identified publication owner and preserved out-of-pass permissions. I3c still owns other invocation fields |
| Local pass activity and completion ownership | Nontransactional lifecycle helper storage | Add `_pass_active: bool`; retain `_pass_started_tx: bool` as ownership, not a value snapshot. Both start false |

The default lifecycle facade can expose working values. Therefore an API named
`committed_ui` must not merely read the default facade during an active pass.
Audit `build_committed_ui`, child traversal, UI synchronization, owner property
delegation, and derived overrides so candidate assembly and published readers
are distinct. Do not change the resource acceptance point as a side effect.

## Completion And Local Pass Contract

1. Local activity and key activity are separate predicates. `is_scope_active`
   and `require_active_scope` describe this context's local pass. A private key
   predicate checks `active_transaction_for(PASS_TX_KEY)` for write permission
   and `publish_write_scope`; changing the local predicate must not make that
   helper start/finish a transaction just because no local pass was entered.
2. `pass_scope` activates once for a context that is locally inactive, even if
   another participant has already activated its key. Re-entry through the
   same context's scope handle stays a no-op, as in the original runtime.
   Direct duplicate `begin_pass` still raises, including an empty child map.
3. Entry sets local activity, records whether this boundary began the key,
   resets visitation and candidate own UI once, and performs no published-value
   snapshot. If entry fails after beginning the key, its owner must finish that
   key and reset local bookkeeping; a borrower cannot finish it.
4. Success retains existing child discovery/removal, native validation, UI
   assembly, and unmigrated resource dispatch order. Candidate assignments
   occur before the existing owner completes its key. A borrower exits only
   its local pass; it must not commit another boundary's enlisted work.
5. Failure preserves existing resource cleanup timing, then discards migrated
   candidate values through the identified completion owner. A borrower must
   have an evidenced owner/path that provides the required discard; local exit
   alone is not discard. Do not call generated participant callbacks directly.
6. Finish local bookkeeping exactly once at the actual completion/failure exit,
   not before an exception handler still needs it. Audit `_PassScopeHandle`,
   `_finish_context_pass`, direct leaf execution, and derived begin/end/rollback
   overrides together. Do not attempt rollback of an already-finished key after
   a commit/after-hook exception or erase the distinction between pre-publication
   failure and failure after publication. D4 remains separate; this checkpoint
   does not promise failure draining or undo of an applied commit.

### Permission And Isolation Gates

The existing API's nested `begin`/`commit` counts are not savepoints, and
`rollback(PASS_TX_KEY)` discards all enlisted participants on that key. A dirty
or metadata setter may also run while no pass is active. Neither fact is fixed
by changing a field marker alone.

The first implementation step must trace these concrete cases:

- Parent pass and same-manager rerunnable child's local pass; identify who
  finishes each candidate category, including a caught child failure.
- Independently managed nested render publishes, then its parent fails. The
  nested render's accepted UI/invocation remains published as in the reference.
- `queue_invalidation_from` and the owner `invoke_dirty` setter outside a pass,
  inside an active pass, and during failure recovery.
- Site metadata writes in `container_call`, slot-call execution, and owner
  setters; read behavior before, during, and after the publication boundary.
- Unseen/new child cleanup and `deactivate` outside rendering; membership
  discard is not proof that subscriptions, registries, or effects were undone.

Record the smallest supported path using the existing cohorts/API. Do not open
and commit a shared key around one dirty setter to publish unrelated candidates,
assign generated private slots, create per-field managers/keys, or invent a
second flag/value snapshot. Do not discard an earlier independently published
child merely to make a parent rollback easy.

If preserving one of those paths requires savepoints, selective participant
completion, new cohorts, a new library capability, or a different invalidation
policy, **stop before changing that path and request a bounded decision**. Keep
the unmigrated authority visibly intact. Partial progress can be committed only
as explicitly partial; it cannot be labeled I3a accepted/completed. This is the
controlling plan's existing stop gate, not approval to defer a regression.

## Removal And Retention Ledger

Delete `_pass_child_dirty` and its copy/restore loop only after all affected
dirty writers satisfy the gates. Delete `_pass_child_order` only after cleanup
uses existing lifecycle current membership for provenance and discard restores
membership/order without its saved tuple. A temporary traversal of
`current.children_state` for domain cleanup is allowed; persisting a replacement
snapshot for undo is not.

Keep child visitation/reset, UI computation, invalidation scheduling, and
resource-specific `commit_binding`/`rollback_binding`, `commit_handler`/
`rollback_handler`, and owned-handler dispatch until I3b/I4 replace their
categories. Do not delete a mixed dispatch loop wholesale or claim these domain
methods disappeared. `_pass_started_tx` remains legitimate owner bookkeeping.

Audit references in `_base.py`, `context_base.py`, `slot_context.py`,
`render_context.py`, `_support.py`, the owner facade, and affected derived
overrides. Extend declarations only where inheritance actually regenerates
them; do not independently decorate competing slotted MI branches. Do not turn
this checkpoint into migration of callback stores or invocation-argument stores.

## Canonical Test Package

Add `tests/data/lcm_integration/common_pass.py` and
`baselines/common_pass.json`, using the existing subprocess/JSON harness in
`tests/test_lcm_integration_characterization.py`. Successful end-to-end
observations belong here, not duplicated in bespoke tests. Keep the existing
I0 snapshots unchanged; they record historical differences, not permission to
silently fix adjacent debt. Original behavior supplies compatibility evidence;
the new golden also observes lifecycle current/working separation explicitly.

The fixture must record:

1. Empty and nonempty local passes, no-op same-context scoped re-entry, and
   repeated passes after success and failure, including visitation resets.
2. Existing/new/removed child membership and insertion order, plus root and
   independently published child UI, before/during/after accepted and rejected
   candidates. Observe public committed readers as well as candidate readers.
3. Initial dirty state, outside-pass invalidation, candidate clearing, failure
   discard, later rerender, and unchanged-call elision. Keep dirty writes
   observable without snapshot restoration.
4. Site metadata selection on success/failure and after recovery, with its
   writer and completion boundary identified.
5. Same-manager borrowed entry/exit without finishing its owner's transaction;
   caught child failure and early independent child publication followed by
   parent failure. Distinguish local exit from actual publication/discard.

Use the generic backend for authored UI paths and small direct observations for
local bookkeeping. Narrow bespoke tests are allowed for duplicate begin and
failure injection at entry/exit, where a success golden cannot express the
diagnostic. A red test that needs a semantic change triggers discussion, not
baseline regeneration. If the reference and decomposed runtime already disagree
outside this category, log that debt separately; do not require equality of
unrelated output or normalize away a migration regression.

## Implementation Steps And Exit

1. Settle the implementation/dependency tuple, rerun the focused baseline, and
   file the writer/cohort audit and concrete permission/isolation probes. No
   marker conversion precedes resolution of its gate.
2. Add the canonical observations and narrow diagnostic probes first; run the
   smallest target and capture the intended red failures, distinguishing known
   baseline debt from the new migration expectations.
3. Separate local pass activity from key activity and update all affected scope
   callers/overrides. Verify borrowed activity, empty passes, no-op re-entry,
   exact ownership, and supported recovery before migrating published values.
4. Migrate candidate access/publication and compatible dirty/site metadata
   declarations, then delete the obsolete snapshots and restoration. Preserve
   resource-domain calls and external invalidation permissions.
5. Rerun focused and full regression suites, record known failure-name deltas,
   and inspect the deletion ledger. Review the committed bounded implementation
   independently before proceeding to I3b. No tag/roll-build is implied here.

I3a is complete only when the entire common category meets its field/access
contract, snapshot removal is real, current/working visibility and failure
compatibility are proven, and the new evidence explicitly identifies remaining
I3b/I3c/I4 authority. A green construction baseline alone is not completion.

Focused command, from the Pyrolyze repository root:

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=short \
  tests/test_runtime_context_state_lcm_construction.py \
  tests/test_runtime_context_state_lcm_context_base.py \
  tests/test_runtime_context_state_lcm_slot_expr.py \
  tests/test_runtime_context_state_lcm_leaf_rerender.py \
  tests/test_lcm_integration_characterization.py
```

Use the same clean-selector environment for the full `python -m pytest` run.
Run the broader decomposed subset recorded in the I1b evidence separately and
classify its existing failures; do not claim runtime activation from these
focused gates. No implementation/test files are changed by accepting this plan.
