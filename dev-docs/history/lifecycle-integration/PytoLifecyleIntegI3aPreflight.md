# I3a Common Pass Preflight

## Status And Authority

Preflight performed on 2026-10-03. **Runtime migration stopped at the reviewed
permission/isolation gate, before any runtime source edits.** I3a is not
implemented or accepted by these observations.

At the time of these probes, authority was
`dev-docs/PytoLifecyleIntegPlan.md` and its reviewed addendum
`dev-docs/PytoLifecyleIntegI3aPlan.md`, at the accepted plan blob
`81d004dc44bc84516a3484e2a64be9667f0657bc`.
The addendum requires a bounded decision if compatibility needs new cohorts,
selective completion, savepoints, a library capability, or an invalidation
policy change. The caught-leaf reproduction below reaches that gate.

**Subsequent user decision (2026-10-03):** one outer render cohort replaces
independent nested publication and local caught-child recovery. The DRAFT
`dev-docs/PytoLifecyleIntegSingleCohortPlan.md` now supplies the current design
and exact supersession list; this document's reference outcomes and the final
alternative recommendation remain historical evidence, not the new target.
The probes and recorded test results are unchanged. Dirty/metadata gates remain.

New JSON baselines are observations of existing behavior, **not approval of the
decomposed runtime's failed-candidate publication**. They do not replace the
planned `common_pass.py` acceptance fixture or rewrite historical I0 baselines.

## Implementation And Dependency Tuple

Pyrolyze source: `4a2b416afa8dbc7d6c21f4263f2964c69c086676`, branch
`lcm-resume`. Tests and this evidence are uncommitted additions to that source.
Committed dependencies used for the verification below:

| Repository | Revision |
| --- | --- |
| yidl-lifecycle | `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4` |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` |

Parent checkout `a20f8cfb633a268925464eb27728d1934a70aea9` is context only.
Dependencies were exported with `git archive` into temporary source directories;
no worktrees, checkouts, library edits, or parent-pointer changes were made.
Uncommitted lazy/mutable lifecycle work, YIDL cleanup, and the separate paper
lane were excluded. The first working-dependency baseline also passed, but it
is not the settled verification tuple.

## Writer, Reader, And Completion Audit

Paths below are relative to the Pyrolyze repository root. Construction
declarations are in `src/pyrolyze/runtime/context_state_lcm/_base.py`; the
common pass implementation is in
`src/pyrolyze/runtime/context_state_lcm/context_base.py`.

| Value | Current Writers | Current Reads | Cohort / Completion Owner |
| --- | --- | --- | --- |
| `children_state` | `register_child`, `register_child_state_mgr`, `ensure_resolved_slot`; slot deactivation; component-child disposal | Default facade in traversal, cleanup, and UI assembly | Managed `PASS_TX_KEY`; render manager injected by `StateMgrBase.create`. The boundary that began the key finishes it; a borrowed child does not |
| `own_ui_entries_state`, `own_ui_state` | `begin_pass` reset; `call_native` tuple replacement | Default facade in staged lengths and `build_committed_ui`; public own-committed readers also use default | Same shared pass cohort as child membership |
| `ui_state` | `call_native`, `end_pass`, recursive UI refresh; component invocation/rerun/disposal; slot-call synchronization/deactivation; slot-expression synchronization/deactivation | Default facade in public committed readers, render debug UI, parent projections, and derived builders | Managed pass value. Component child render has an independent manager; its parent slot's projected UI uses the parent's cohort |
| `_invoke_dirty` | Constructor factory; owner setter; invalidation traversal of source/ancestors/component owner; `end_pass` clearing; `rollback_pass` snapshot restoration | Owner getter, dirty visitation/elision, and pass snapshot | Ordinary nontransactional lifecycle field today. Invalidation is allowed with no active key; clearing is pass bookkeeping and has no lifecycle discard owner yet |
| `_seen_in_pass` | Constructor factory; owner setter; pass-entry reset; slot resolution; rollback cleanup; owned-handler reset/cleanup | Unseen-child cleanup and owned-handler traversal | Ordinary nontransactional lifecycle field. Local visitation, not transaction-lifetime state; resource-handler uses remain I3b/I4 work |
| `_site_metadata` | Owner setter; `container_call`, `component_call`, and slot-call `evaluate` after site resolution | Owner/slot-call accessors and graph inspection | Nontransactional helper storage today. No publication/discard owner is defined for a managed replacement |
| `_pass_started_tx` | Entry and all normal completion paths | Owner-only key commit/rollback | Legitimate local completion-owner bookkeeping; retain |
| `_pass_child_order`, `_pass_child_dirty` | Entry snapshot, completion reset | Duplicate-entry guard, new-child cleanup, dirty restoration | Existing manual undo authority; retain until replacement satisfies the gates |

Concrete writer locations: `context_base.py` registration at 213-220, entry/
completion at 225-305, slot resolution at 334-359, refresh at 405, metadata at
503/601, and native emission at 664-672; `render_context.py` refresh at 217-223
and invalidation at 308-349; `slot_context.py` deactivation at 39-53;
`component_call_slot_context.py` at 182, 221/237, 298, and 307-315;
`slot_call_slot_context.py` at 53, 168, and 207;
`slot_expr_slot_context.py` at 95/103. Owner setters are in
`src/pyrolyze/runtime/context_bare_refactor_lcm.py` at 377-397.

Registration replaces maps rather than mutating lifecycle current maps in
place. However, registry removal, deactivation, binding/handler completion,
and independent render publication are domain effects, not undone merely by
discarding membership. No removal of those calls is justified by this audit.

### Cohorts And Scope Callers

- Ordinary slots and same-render rerunnable structural contexts use the render
  manager injected by `StateMgrBase.create`. A native leaf can enter a local
  pass without beginning or owning that manager's already-active pass key.
- Each nested component render constructs its own manager. Sharing a scheduler
  root is not sharing a transaction manager. Its earlier accepted publication
  must survive a later parent failure, as the existing characterization shows.
- Call-site collection/resource completion remains separate. This preflight
  does not migrate bindings, event callbacks, handlers, or invocation holders.
- `pass_scope`, `require_active_scope`, and `publish_write_scope` currently use
  key activity as local activity. A future local predicate needs a distinct
  key predicate for publication writes; it cannot be substituted everywhere.
- Affected callers include `_support.py`'s `_PassScopeHandle`,
  `_finish_context_pass`, directive cleanup, and keyed-loop completion;
  direct leaf invocation; component rerun/parent-refresh logic; directive and
  app-context-override begin/end/rollback overrides. Existing override
  `_scope_active` debt remains visible, not repaired by the preflight.

## Concrete Isolation Stop Gate

`tests/data/lcm_integration/common_pass_preflight.py` uses real root/leaf
contexts and lifecycle state, with no transaction mocks:

1. Publish a leaf emitting `old`.
2. Start a parent pass and emit `parent-candidate`.
3. Reinvoke the same leaf; it emits `failed`, then raises `ValueError`.
4. Catch that error in the parent and let the parent pass succeed.

| Observation | Original Reference | Decomposed LCM |
| --- | --- | --- |
| Before retry | Root and leaf show `old` | Root and leaf show `old` |
| Public leaf UI after catch | `old` | `failed` |
| Lifecycle current leaf UI after catch | Not applicable | `old` |
| Parent completion | Root shows `parent-candidate`, `old` | Root shows `parent-candidate`, `failed` |
| Leaf after parent completion | `old` | `failed` |

The decomposed leaf and root have the **same manager**. After the caught error,
the pass key is still active and the leaf's `_pass_started_tx` is false. Its
`rollback_pass` exits locally without discarding its managed candidates. The
parent later commits those candidates. Default-facade public UI access also
exposes the working candidate before that commit.

This is existing decomposed-path debt, not a regression from this preflight.
It nevertheless prevents a compatible I3a migration using the current cohort
and API. Fixing committed readers alone would conceal the candidate until
completion, but would not prevent its eventual publication.

In the pinned yidl-lifecycle repository,
`src/yidl_lifecycle/transaction_yidl.py` implements nested `begin`/`commit` as
depth counting on one `LifecycleTransaction`. `rollback` completes/discards
the entire key. `drop` removes enlistment records; it does not clear the
participant's working/staged values. There is no supported child-local
discard boundary in that API.

Consequently:

- Leaving the key active retains the failed leaf candidate.
- Rolling back the whole key discards the parent's candidate and closes the
  transaction needed for its permitted continuation.
- Nesting `begin` is not a savepoint.
- Calling generated participant rollback callbacks directly, resetting fields
  from current, or retaining replacement value snapshots would recreate an
  application transaction engine, contrary to the accepted plan.

The existing `characterize.py` caught-child case uses an independently managed
component render. Its green baseline does not prove this same-manager leaf
case is compatible.

## Permission And Local-Entry Gates

### Outside-Pass Dirty And Metadata Writes

The original and decomposed probes both permit `leaf.invoke_dirty = True`
outside a pass. Invalidation traversal also marks it dirty and schedules one
boundary. The decomposed pass key remains inactive. Its owner metadata setter
also accepts `("outside-pass",)` without a transaction.

A separate real generated declaration probes the proposed straightforward
`managed(..., tx_key=PASS_TX_KEY)` conversion of dirty and metadata storage.
Both writes raise `RuntimeError: writes require an active yidl transaction`;
current values remain unchanged. This proves marker-only conversion would
remove existing permissions.

Dirty invalidation intent and successful pass-local consumption/clearing need
an explicit policy. They may represent distinct facts, but this audit does not
authorize adding a second shadow flag or publishing a shared key just to write
one flag. The latter can publish unrelated candidates.

Source inspection also shows original site metadata is assigned eagerly by
container/component/slot calls, without restoration in pass rollback. The
outside-pass permission is reproduced; full metadata success/failure/read
timing is **not** yet covered by a migration acceptance fixture. Treating all
metadata as rollback-sensitive published state may tighten existing behavior
and requires an explicit classification, not an assumed marker conversion.

### Borrowed Transaction Does Not Mean Local Entry

The decomposed probe begins the pass key externally, stages an old own-UI
value, and enters `root.pass_scope()`. `is_scope_active()` already returns true,
so entry/reset is skipped; `stale` remains inside the scope. The scope correctly
does not finish the external key, but it also does not enter a local pass.

This supports the addendum's separate local-activity design. It does not solve
the discard or permission gates, and no partial predicate rewrite was made.

## Removal And Retention Ledger

No runtime declarations, methods, snapshots, completion owners, or resource
dispatch were removed or changed. `_pass_child_order`, `_pass_child_dirty`,
and their restoration loops remain visibly authoritative. `_pass_active` has
not been added. Original/monolithic references and runtime selection defaults
are untouched.

Unseen/new-child resource cleanup, current membership/order restoration,
metadata failure timing, and all scope exit recovery still require the planned
acceptance work after the gates are resolved. No whole-graph atomicity, manager
unification, failure draining, or stronger publication guarantee is claimed.

## Verification

- Five-file baseline before new observations: **27 passed in 3.64s** against
  working dependencies, then **27 passed in 8.69s** against committed exports.
- New harness entries initially failed because the two observation baselines
  did not exist. Baselines were authored after inspecting both outputs; this
  is characterization setup, not a red/green implementation of desired
  migration semantics.
- Five-file set with observations, committed exports: **29 passed in 9.99s**;
  final recheck after syntax/documentation checks: **29 passed in 10.14s**.
- Full default suite, committed exports: **819 passed, 13 failed, 20 skipped,
  1 warning in 41.57s**. Failure names match I1b's eleven visitor/export and
  two host-ordering cases; two added passes are preflight observations.
- Broader eight-file decomposed subset, committed exports: **41 passed,
  14 failed in 1.72s**, matching I1b's nine app-context-override, one mount-advert,
  one generation, and three event-UI failure names.

These counts do not mean the port is ready for default activation. Neither
the existing failures nor the newly observed migration blockers were fixed.
There has been no independent implementation acceptance review, commit, tag,
push, or merge for this preflight.

## Reproduction

From the Pyrolyze repository root, create read-only committed source exports:

```sh
snapshot=$(mktemp -d)
mkdir -p "$snapshot/yidl-lifecycle" "$snapshot/yidl" "$snapshot/astichi"
git -C ../yidl-lifecycle archive 1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4 src | tar -x -C "$snapshot/yidl-lifecycle"
git -C ../yidl archive 95a6e3e52fc3d710d25c5d59315e791a3ed75cc4 src | tar -x -C "$snapshot/yidl"
git -C ../astichi archive 387ca5e1da76204ee60922094734c13ee36383c0 src | tar -x -C "$snapshot/astichi"
export PYTHONPATH="src:$snapshot/yidl-lifecycle/src:$snapshot/yidl/src:$snapshot/astichi/src"
export PYTHONDONTWRITEBYTECODE=1
```

Inspect either runtime without rewriting a baseline:

```sh
env -u PYROLYZE_USE_CONTEXT_LCM PYROLYZE_CONTEXT_IMPL=original \
  ../.venv/bin/python tests/data/lcm_integration/common_pass_preflight.py
env -u PYROLYZE_USE_CONTEXT_LCM PYROLYZE_CONTEXT_IMPL=bare_refactor_lcm \
  ../.venv/bin/python tests/data/lcm_integration/common_pass_preflight.py
```

Focused verification:

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=short \
  tests/test_runtime_context_state_lcm_construction.py \
  tests/test_runtime_context_state_lcm_context_base.py \
  tests/test_runtime_context_state_lcm_slot_expr.py \
  tests/test_runtime_context_state_lcm_leaf_rerender.py \
  tests/test_lcm_integration_characterization.py
```

Full default and broader decomposed verification:

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=line
env -u PYROLYZE_USE_CONTEXT_LCM PYROLYZE_CONTEXT_IMPL=bare_refactor_lcm \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=line \
  tests/test_runtime_call_site_context.py \
  tests/test_app_context_override_context.py \
  tests/test_mount_advert_binding.py \
  tests/test_generic_backend_harness.py \
  tests/test_generic_backend_generation.py \
  tests/test_context_graph_phase5_component_call.py \
  tests/test_context_graph_phase8_scheduler.py \
  tests/test_visitor_context_graph.py
```

Exported dependencies are temporary; remove the owned export directory after
verification.

## Historical Bounded-Decision Recommendation (Superseded)

First decide how to preserve caught same-manager child failure: either authorize
designing a manager-owned isolated local completion/discard facility, or
authorize a bounded cohort remapping that preserves reference publication and
cleanup behavior. A per-context manager is not a one-line fix: current factories
inject the render manager and related parent-slot values/resources share its
completion boundary. Neither alternative is implemented or pre-approved here.

Separately pin dirty invalidation-versus-consumption policy and metadata
eager-versus-candidate semantics before changing their declarations. A partial
local-activity/read-facade checkpoint could be scoped explicitly, but cannot be
labeled complete I3a while failed candidates or removed permissions remain.

The recommendation is to settle the child-local discard boundary first, then
revise the addendum and its review scope. Do not remove the remaining manual
undo authority merely because the characterization tests are green.
