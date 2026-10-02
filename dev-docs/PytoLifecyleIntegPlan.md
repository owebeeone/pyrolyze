# Pyrolyze YIDL Lifecycle Integration Plan

## Status And Purpose

Proposed continuation of the LCM migration on `lcm-resume`.

The objective is to replace Pyrolyze's handwritten transactional state engine
with `yidl_lifecycle`-decorated classes. Installing the decorator underneath the
old engine is not the end state. The migration must remove duplicate state,
field snapshots, field restoration, per-slot transaction ownership, and
class-name-based child commit/rollback dispatch.

This document updates the integration direction in
`dev-docs/ContextLifecyleMetaprogrammingPlan.md` and
`dev-docs/LifecyleAdoptionPatterns.md`. Their behavioral goals remain useful, but
their references to `pyrolyze.lifecycle`, record internals, and transactional
`binding()` fields do not describe the extracted library exactly.

This is a plan, not authorization to implement, switch the default runtime, or
change public semantics. The decision gates below must be resolved before a
roll-build is advertised as ready.

## Checkpoint

The resumed checkpoint consists of:

- Pyrolyze commit `9b72263`: YIDL lifecycle integration and current LCM work.
- `yidl-lifecycle` commit `cdf0854`: direct AST execution, parameterized
  `local_store` factories, regeneration tooling, and refreshed goldens.
- Parent checkout commit `a20f8cf`: those two submodule revisions.

Verification at that checkpoint:

- The seven focused LCM test files passed: 32 tests.
- The `yidl-lifecycle` suite passed: 264 tests, with 46 skipped.
- The full Pyrolyze regression suite and current performance were not checked.
- Other workspace/submodule changes were deliberately not included.

Treat these as results for the tested working checkout, not proof that all
dependencies are reproducible from the parent commit alone. Record the YIDL and
Astichi revisions and any dirty dependency changes during preflight.

## Current Implementation

There are two LCM paths, not one completed integration:

| Path | Current Role | Remaining Scaffolding |
| --- | --- | --- |
| `src/pyrolyze/runtime/context_lcm.py` | Default `lcm` implementation | Decorated helper states mirrored into legacy attributes, `_lcm_sync`, per-slot `_lcm_txm`, manual publication |
| `src/pyrolyze/runtime/context_bare_refactor_lcm.py` and `src/pyrolyze/runtime/context_state_lcm/` | Decomposed migration path | Partly decorated state managers, imperative subclasses, manual pass/resource dispatch |
| `src/pyrolyze/runtime/context_original.py` | Compatibility reference | Original runtime semantics |

The implementation target is the decomposed LCM path. Do not independently
finish both LCM implementations. Keep the current default and original paths as
references until the decomposed path passes the integration acceptance tests.

Concrete unfinished work includes:

- `ContextBaseStateMgr.end_pass()` and `rollback_pass()` dispatching resource
  operations by the child owner's class name.
- `_pass_child_order` and `_pass_child_dirty` storing rollback information.
- `_invoke_dirty` and `_seen_in_pass` remaining ordinary mutable fields in some
  decorated subclasses.
- `ContextBaseStateMgr.is_scope_active()` treating an active shared pass
  transaction as proof that this particular context's pass is active.
- Shared-TM installation through `_bootstrap_transaction_manager_bad_program`.
- Graph attachment through `_attach_to_graph_bad_program` factory side effects.
- `RenderContextStateMgr` allocating a TM even for nested render contexts that
  already belong to a scheduler root.
- `CallSiteContextManager` importing the legacy lifecycle, allocating a private
  TM, and accessing legacy `current_record` / `working_record` internals.
- Slot-call, event-handler, component-child, and app-context-override classes
  retaining their own committed/pending fields or resource commit methods.

## Architecture Contract

### One Manager, Several Transaction Spaces

One root render/scheduler graph owns one `yidl_lifecycle.TransactionManager`.
Every lifecycle participant in that graph receives the same object at
construction, including nested render contexts, call-site collections, and
transactional resource adapters. Independent root graphs have independent TMs.

A shared TM does not imply one transaction key or one write permission.
Lifecycle fields belong to a `tx_key`; state-changing writes require that key's
transaction to be active. Objects enlist on mutation or supported lazy working
materialization, and the TM visits enlisted participants rather than walking
the entire context graph to publish fields.

Use the current key vocabulary consistently:

- `tx_key`: semantic transaction space, potentially any hashable object.
- `tx_index`: a generated class's local index for that key; indexes need not be
  identical in different generated classes.
- Transaction token: identity of a particular active transaction, not its key.

Pass actual keys to the TM. Do not dispatch graph-wide operations using a
class-local index, or translate `DEFAULT_TRANSACTION` into a string literal.

### Division Of Responsibility

| Owner | Responsibilities |
| --- | --- |
| YIDL lifecycle | Facades, field storage, enlistment, conversion/staging, commit/rollback, supported transient and owned semantics |
| Root boundary coordinator | Explicit key activation, transaction lifetime, completion/error handling, generation coordination |
| Pyrolyze context classes | Rendering, child discovery/order, graph validation, UI assembly, invalidation, domain hooks |
| Pyrolyze resource classes/adapters | Subscription/effect/mount behavior and resource-specific acceptance/retirement |

Do not move slot terminology or graph traversal into generic YIDL code. Do not
introduce a second generic field-level transaction engine in Pyrolyze.

The following are legitimate domain operations, not forbidden bookkeeping:

- Marking a visited slot during rendering.
- Computing the next child map and next UI before publication.
- Validating fixed structure and native-root requirements.
- Adapting an external effect or subscription to the lifecycle hook boundary.
- Explicit resource deactivation when the domain requires it.

The following must disappear from the migrated path:

- Copying committed fields into `_pass_*` fields solely to undo assignments.
- Manually moving staged callbacks/arguments into committed fields.
- Calling each child state's commit/rollback to publish its decorated fields.
- Mirroring lifecycle values into another authoritative attribute store.

## Transaction And Scope Semantics

### Proposed Key Assignment

The following restores the separation described by the adoption document. It
is a proposed integration contract to verify in I0, not a claim about today's
partially migrated declarations.

| State | Key Or Storage | Lifetime |
| --- | --- | --- |
| Published child membership/order, UI, invocation inputs, callback selection, override values | `managed` / supported `owned`, `DEFAULT_TRANSACTION` | Survives successful publication; previous current state survives failure |
| Visitation, staged callback queue, local pass-active marker, genuinely transaction-local scratch | `transient`, `PASS_TX_KEY` | Exists during the pass transaction and is cleared at its end |
| Owner, parent identity, slot identity, immutable configuration | `const` or constructor `initvar` | Construction/lifetime data |
| Inert memoization/helper storage | `local_store` or justified ordinary shared storage | Survives transactions without changing rollback-visible results |

Published state is currently also assigned to `PASS_TX_KEY` in
`src/pyrolyze/runtime/context_state_lcm/context_base.py` and the component invocation record. Moving
it to the default key must be coupled to explicit publication-key activation;
changing field declarations alone would make existing writes illegal.

Not every field beginning with `_pass_` belongs in a transient. Remove redundant
snapshots first. Do not hide authoritative state in `local_store` merely to
avoid an active-transaction error.

### Global Key Activity Is Not Local Scope Activity

There are separate questions:

1. Does the graph's TM have an active transaction for this field's key?
2. Is this particular context currently executing its local render/pass scope?

A sibling slot must not pass `require_active_scope()` merely because another
slot has activated `PASS_TX_KEY` on the shared TM. Preserve local scope tracking
with a context-local declaration or scope object. A transient active/depth
marker is a candidate; select its exact semantics after characterizing current
scope entry and re-entry behavior.

Likewise, one field's transient lifetime is its transaction-key lifetime, not
automatically the duration of an individual function call. A child can execute
multiple local passes inside one outer transaction. Reinitialize per-invocation
scratch explicitly or keep it in ordinary function locals; do not create a
private TM just to obtain automatic cleanup at each child return.

### Boundary Ownership

Proposed graph-boundary sequence:

1. The outer boundary explicitly activates `DEFAULT_TRANSACTION` and
   `PASS_TX_KEY` on the graph TM.
2. Local pass scopes open/close their local activity markers and perform domain
   work. They do not commit the publication key on return.
3. Finalize the candidate graph/UI and validate domain invariants while current
   remains unchanged. Pruning updates working membership; irreversible
   retirement of old resources waits for publication.
4. Publish the default-key participants through the TM's validation and
   prepare/apply machinery.
5. Finish pass-key scratch and release local boundary bookkeeping.
6. Deliver post-publication notifications/effects under the agreed hook policy.

Before publication, failure rolls back the boundary-owned active keys. After
publication, a notification failure must not pretend that committed state can
be restored by another rollback. Drain-first failure handling and grouped error
reporting are the intended Phase F-1 contract, not a guarantee of the pinned TM.
The lifecycle prerequisite L0 below must reconcile and verify that contract
before the new coordinator or migrated hooks depend on it.

Nested boundaries and locally completed child passes must not finalize the
outer publication transaction. If a nested failure is caught and the outer
render continues, the required recovery semantics need an explicit decision:
the current TM does not supply arbitrary per-child savepoints. Do not introduce
manual field snapshots to fake them.

Only finish transactions this coordinator owns. Joining an already active
transaction does not confer permission to commit it.

### Existing TM Limits To Respect

- `tm.begin()`, `tm.commit()`, and `tm.rollback()` without keys currently target
  all configured spaces. Use explicit keys at integration call sites.
- `tm.active_transaction` refers to the default space. Use
  `active_transaction_for(key)` for key-specific checks.
- Multi-key commit currently completes keys separately. It is not one atomic
  prepare-all/apply-all operation across keys.
- Nested begin counts are not savepoints; rollback is not a local child undo.
- In the pinned `yidl-lifecycle` runtime, prepare/apply/after-commit dispatch and
  rollback/after-rollback dispatch can stop at the first participant exception.
  Manager teardown still clears its active transaction. It does not attempt
  skipped participants' callbacks or provide the complete drain-first/grouped
  failure contract required by its Phase F-1 design.

An early failing after-commit hook can therefore skip another participant's
mandatory retirement even though its values were published. An early rollback
failure can skip remaining cleanup. Neither a manager reset nor an unchanged
next render repairs this automatically. Do not remove legacy delivery/cleanup
mechanisms on the assumption that the missing capability already exists.

Consequently, atomic published state belongs to one publication key in this
plan. The pass key is scratch, not a second collection of independently
published authoritative fields. Specify scratch completion and notification
failure handling explicitly rather than relying on an unqualified multi-key
commit.

## Construction And Initialization

Allocate the TM only at the scheduler/root ownership boundary. Resolve it from
the supplied parent/root for all subsequent constructions and pass the existing
`transaction_manager=` constructor argument to generated lifecycle classes.

Expected construction shape, illustrative rather than a new public API:

```python
root_tm = TransactionManager(tx_keys=(PASS_TX_KEY,))
root_state = RootState(owner=root, transaction_manager=root_tm)
slot_state = SlotState(
    owner=slot,
    parent_state_mgr=root_state,
    transaction_manager=root_tm,
)
```

Include every additional key actually used by the graph; do not silently create
unknown spaces. Do not eagerly allocate a throwaway per-slot manager and replace
it later through `_y_state` internals.

Factory evaluation remains the generated constructor's responsibility. Named
factory dependencies, including `local_store` factory parameters, are available.
Initialization must not patch the manager midway through those evaluations.

Graph registration/attachment is a separate domain action after construction.
Move it out of `_attach_to_graph_bad_program` factories into an explicit
construction/attachment path that can register provisional membership and
retire it on failure. This is not user `__init__`/`__post_init__` chaining.

## Resources And Bindings

Distinguish three independent behaviors:

1. Staging replacement of a reference in its holder.
2. Committing/rolling back the referenced object's own state on the shared TM.
3. Accepting and retiring the referenced resource.

Current `yidl_lifecycle.binding()` validates and directly stores a shared
reference; it does not stage reference replacement or automatically enlist its
referent. Current `owned()` stages references/maps and integrates
`BindingBase` acceptance/lifetime behavior. Sharing a TM is not sufficient to
turn an arbitrary `BindingBase` into a transaction participant.

For each resource category, select one explicit implementation:

- A lifecycle-decorated participant on the shared TM for its internal mutable
  state.
- A supported owned reference/map for transactional replacement and lifetime.
- A narrow Pyrolyze adapter/hook for external behavior that cannot be expressed
  as ordinary field publication.

These can be combined. Do not rename `binding()` to `owned()` mechanically:
existing `SlotCallBinding` and legacy call-site binding classes do not all
implement the extracted library's ownership contract.

`SlotCallBinding.commit()` can mean "run an effect", not "publish a decorated
field". Such domain methods need deliberate hook integration, not indiscriminate
deletion or a relocated loop over every graph object.

`CallSiteContextManager` must be migrated too. Remove its private transaction
manager and legacy record access, preserve its public/domain behavior, and
express its context membership and visitation through the shared lifecycle
model. Explicit legacy reference counting must not coexist accidentally with
intrinsic-reference ownership of the same resource.

Do not rely on immediate garbage collection for observable unsubscribe,
cancellation, or graph removal. Audit owner/parent/resource reference cycles.
Retire old resources only after a successful replacement, and provisional
resources on failure, preserving required ordering and idempotence.

A generic lifecycle `close()` protocol, generalized `derived` fields, and new
YIDL grammar are not prerequisites to be invented during this integration.
If existing facilities cannot preserve a resource's required semantics, stop
and propose the smallest library extension before adding a local workaround.
The known TM failure-completion gap is an explicit instance of this rule: L0
owns its reconciliation in `yidl-lifecycle`, not a replacement Pyrolyze callback
engine. I4 cannot transfer mandatory resource completion to hooks until that
prerequisite passes.

## Field And Hook Migration Map

| Area | Intended Migration | Remove |
| --- | --- | --- |
| Base context subtree/UI | Managed publication state; use current for the previous published view | Child-order/UI snapshots used only for rollback |
| Dirty and seen flags | Classify independently: rollback-sensitive published flags vs local-pass markers | `_pass_child_dirty` restoration loops |
| Leaf/rerunnable inputs | Managed identity/schema/arguments with immutable values or declared thaw/freeze | Duplicate last/pending argument stores |
| Event handlers | Managed callback/key; stable dispatch reads the committed selection | Manual staged-to-committed copying |
| Slot-call resources | Shared-TM participant/adapter plus explicit replacement policy | Per-slot managers and generic child resource dispatch |
| Slot-expression sites | Lifecycle-owned membership and transient visitation/notification data | Legacy call-site record access and private pass TM |
| Component child context and owned handlers | Transactional child/resource membership with publication-aware retirement | `_pass_owned_event_handler_order` rollback snapshots |
| App-context overrides | Managed values/lookup selection; domain hooks for observable drip/link behavior | `_pass_committed_values` / `_pass_committed_lookup` restore code |
| Registries and caches | Classify by observability; managed if failed work must undo membership | Treating visible graph membership as an inert cache |

Compute candidate UI and graph values before publication. Validation hooks
check constraints; after-commit hooks handle effects/notifications, not new
writes into the publication transaction being finalized.

Transient queues may already be cleared by lifecycle before an after-hook runs.
Specify how notification batches survive until delivery: for example, consume
pass-key data while it is still active, or extract an immutable domain event
batch into the boundary coordinator's locals. Do not duplicate old field values
under the label of a notification batch.

## Implementation Slices

Each slice uses red/green/refactor, removes the corresponding obsolete mechanism,
and has a separately reviewable result. A slice that merely introduces decorated
fields alongside the old authoritative state is incomplete.

### I0: Baseline And Semantic Decision Gate

1. Record repository revisions, dirty dependencies, interpreter, and import-hook
   setup. Verify the extracted generated base against its YIDL sources.
2. Re-run the focused baseline, then the relevant broader runtime tests and full
   Pyrolyze suite. Separate pre-existing failures from integration regressions.
3. Inventory every TM allocation, legacy lifecycle import, direct record access,
   duplicate publication field, and manual resource commit/rollback call in the
   target dependency path, including `call_site_context.py`.
4. Build a per-field inventory recording observability, key, local scope,
   constructor source, mutation style, and replacement/retirement behavior.
5. Characterize parent failure after a child finishes, nested render boundaries,
   caught child failure, repeated passes, and external update/deactivation paths.
6. Confirm the publication/pass split and outer-boundary ownership against those
   results. Discuss any actual semantic change before continuing.
7. Characterize multi-participant prepare/apply/hook/rollback failures against
   the Phase F-1 intended contract. Record the known pinned fail-fast limitation
   and approve the smallest lifecycle-owned L0 scope before dependent work.

Exit: a recorded baseline, approved boundary/key semantics, and a concrete
resource-category mapping. A needed savepoint or unresolved ownership contract
blocks the affected later slice; it is not permission to rebuild the legacy
engine inside an adapter.

### L0: Lifecycle Failure-Completion Prerequisite

This is a separately committed `yidl-lifecycle` checkpoint, not Pyrolyze domain
logic. I0 must approve its scope and any unresolved policy choices before code
changes. It reconciles the existing Phase F-1 manager contract with the pinned
implementation; review-loop acceptance of this plan does not authorize it.

1. Specify phase-draining and failure reporting for prepare, unexpected apply,
   after-commit, rollback, and after-rollback. Preserve the original failure
   context when cleanup also fails; do not let a first callback exception hide
   skipped mandatory work or be mistaken for successful completion.
2. Implement the approved lifecycle-owned correction and its failure tests in
   `yidl-lifecycle`. Do not introduce a Pyrolyze-wide loop over participant
   classes as a substitute for manager behavior.
3. Verify three enlisted participants with an early throwing after-commit hook:
   later hooks/retirement are attempted once, values remain committed, failure
   reporting preserves context, and the key is completed without fictitious
   undo.
4. Verify early rollback-callback and after-rollback failures independently:
   later participants still receive cleanup and after-rollback attempts. Check
   owned-key/token cleanup, error aggregation, and recovery by a subsequent
   transaction. A broken participant's incomplete cleanup must be reported,
   not assumed repaired by resetting the manager.
5. Verify prepare failure prevents publication while all required cleanup is
   attempted, and unexpected apply failure follows the explicitly approved
   Phase F-1 drain/report policy. Do not claim atomic undo after publication.

Exit: an approved, tested lifecycle failure-completion contract and recorded
library revision. The new I2 coordinator and the I4/I6 hook migrations cannot
complete without this evidence. Existing single-participant hook tests are not
sufficient; Pyrolyze's eventual integration fixture must also prove local-scope
cleanup and recovery when library failures cross the root boundary.

### I1: Shared TM Construction And Local Scope Safety

1. Separate context-local pass activity from shared key activity before enabling
   live nested-TM sharing. Preserve each local entry/exit, per-invocation scratch
   reset, visitation, candidate UI finalization, and the completion-ownership
   rules approved in I0. An active sibling/parent key must not suppress them.
2. Allocate only for an independent scheduler/root graph; nested render contexts
   reuse their scheduler root's manager.
3. Thread the existing constructor parameter through base/derived state-manager
   factories without writing generated private slots after construction.
4. Remove `_bootstrap_transaction_manager_bad_program` and its dummy field.
5. Move graph-attachment factory side effects to explicit provisional attachment.
6. Prepare an injected shared-TM construction seam for call-site participants;
   migrate their actual legacy implementation in I4 rather than passing an
   incompatible TM to it.

Verification: same-manager identity across two slots and a nested render context;
different independent roots; no per-slot allocation or manager replacement in
the migrated state construction path. Preserve existing owner/initvar/factory
behavior and constructor failure cleanup.

At this same checkpoint, run a nested authored component that emits native UI
directly, then rerender with changed input: exactly the new emission remains.
Include nested child removal and a failing nested pass followed by recovery.
Verify local scope entry/exit independently of TM identity, repeated-pass reset,
and that a joined local scope does not finalize an outer-owned transaction.
Constructor seams may be preparatory work, but I1 is not complete while live
sharing still relies on `is_scope_active()` returning graph-wide key activity.

### I2: Key Boundaries And Local Scope Control

1. Introduce or adapt a small runtime-only boundary coordinator at the root.
   Keep key/lifetime behavior explicit rather than represented by new mode tags.
   L0's verified failure-completion contract is a prerequisite.
2. Move published base/component fields to the approved publication key and
   activate it explicitly wherever legitimate domain writes occur.
3. Integrate the local scope controls already made operational in I1 with the
   separate publication/pass-key coordinator. Do not postpone local pass reset
   or finalization to this checkpoint after enabling sharing in I1.
4. Remove child publication commits; local scope exit computes candidate domain
   state without finalizing the root transaction.
5. Give out-of-render invalidation/deactivation paths explicit authorized scopes.
   Replace broad `publish_write_scope()` behavior according to the I0 decision.

Verification: pass-only and publication-only write gating; sibling scope remains
inactive; child exit leaves root publication open; repeated local passes reset
their own scratch; failures leave no stale tokens/local scope markers. An
unqualified TM call must not silently open every space.

### I3: Decorated Value State Becomes Authoritative

1. Migrate leaf/rerunnable argument and identity state, then event-handler
   callback/key state, using the existing decomposed class boundaries.
2. Preserve stable event dispatch identity and committed-callback visibility.
3. Classify dirty flags and visitation separately; remove manual dirty snapshots.
4. Build candidate child maps/UI through field assignments or declared
   thaw/freeze behavior. Never mutate a current collection in place and expect
   rollback to undo it.
5. Remove duplicate committed/pending fields and restoration for these values.

Verification: canonical rerender sequence, unchanged-call elision, identity
comparison, callback replacement, and failure after one child completes.
Current values remain old until root publication; rollback restores them by
discarding working state, not by an application copy loop.

### I4: Call Sites And External Resource Participants

Prerequisite: L0's multi-participant failure-completion evidence. Do not move
mandatory retirement or delivery to lifecycle hooks on the fail-fast baseline.

1. Migrate `_CallSitePassContext` / `CallSiteContextManager` from the legacy
   lifecycle and record internals to supported shared-TM fields/facades.
2. Implement the I0 resource mapping for slot value, external store, effect,
   async effect, and mount-advertisement bindings in their owning modules.
3. Preserve resource-specific behavior through lifecycle hooks/participants;
   resolve acceptance, subscription, cancellation, and replacement timing.
4. Remove private call-site/per-slot TMs and generic slot binding commit/rollback
   dispatch once their replacements are covered.
5. Make staged-site visitation and post-publication notifications explicit,
   accounting for transient cleanup timing.

Verification: shared-manager identity includes call sites; provisional resources
are retired on failure; committed resources survive failure; successful
replacement retires the old resource once; effects/async effects and mount
notifications occur at the approved boundary and preserve exception behavior.
No hidden legacy TM or explicit-refcount/intrinsic-refcount double release.

### I5: Child Ownership And Component Boundaries

1. Migrate component identity/schema, child render context, and owned handler
   membership away from `local_store` where they affect published behavior.
2. Use the approved owned/participant adapter mapping for child lifetimes.
3. Preserve child identity across successful unchanged renders and recreate only
   when the domain requires replacement.
4. Retire unseen/replaced committed children after publication; release new
   provisional children on failure without destroying the previous graph.
5. Remove owned-handler order snapshots and manual rollback reconstruction.

Verification: nested context shares root TM, child failure and parent failure,
handler reorder/removal, identity preservation, and cancellation/unsubscribe
ordering. Include a failure after staging removal of an existing child.

### I6: Overrides, Registries, And Publication Notifications

Prerequisite: the same L0 contract remains verified for the integrated hooks;
after-publication failure must not skip later participants' required work.

1. Migrate override values and lookup selection to authoritative decorated state.
2. Keep fixed-key validation and drip/subscription semantics in domain code;
   replace rollback restoration with lifecycle state and approved domain hooks.
3. Audit slot registries, mount-advertisement maps, generation tracking, queued
   invalidations, and post-commit queues for failure-visible side effects.
4. Coordinate candidate graph/UI validation, default-key publication, pass-key
   cleanup, generation publication, and notification delivery explicitly.
5. Delete class-name dispatch in base end/rollback passes after every participant
   category has migrated. Keep only rendering and domain-finalization work.

Verification: failed overrides preserve published values and subscription links;
failed graph/mount validation publishes nothing; successful UI and generation
agree; notification failures do not trigger fictitious post-publication undo.
Recovery by the next render must work after every tested failure path.

### I7: Canonical Runtime Routing And Scaffolding Removal

1. Run the canonical integration scenarios through the decomposed path and the
   approved compatibility reference in isolated Python processes.
2. Verify all runtime-export consumers, visitor traversal, compiler-generated
   calls, slot-expression paths, and the generic backend harness.
3. Point the canonical `lcm` runtime surface at the completed implementation;
   make its implementation identity/export metadata accurate.
4. Retire `_LifecycleSlotMixin`, `_lcm_sync`, duplicate helper-state wrappers,
   and the superseded monolithic implementation after consumers/tests move.
5. Preserve the explicit original-runtime fallback until its removal is approved.
   Do not rewrite unrelated refactor variants merely to make the matrix pass.

Verification: default and explicit selection, runtime exports, equivalent public
UI/graph behavior, full Pyrolyze suite, and no remaining migrated-path parallel
transaction engine. Tests importing `context_lcm` directly must be reviewed;
setting an environment variable alone does not reroute such tests.

### I8: Performance, Documentation, And Final Acceptance

1. Measure cold import/decorator materialization separately from construction,
   normal access, first-write enlistment, unchanged rerender, commit, and rollback.
2. Reuse lifecycle constructor benchmarks rather than creating another competing
   constructor benchmark. Measure small and larger real context graphs and
   touched subsets; report actual timings without invented release thresholds.
3. Verify only affected participants receive lifecycle publication callbacks.
   Domain rendering may still traverse children; do not confuse that with TM
   commit traversal.
4. Update the old LCM/adoption documents, runtime-selection documentation, and
   integration commands to reflect the actual extracted library and resource
   policy.
5. Record known limitations and any explicitly approved semantic differences.

Exit: the acceptance checklist below is satisfied and checkpoint results are
reproducible. Astichi/native-backend optimization and package extraction are
separate projects, not hidden completion requirements here.

## Test Strategy

Successful end-to-end behavior belongs in canonical integration fixtures and
snapshots. Prefer the existing `pyrolyze.testing.generic_backend.PyroRenderHarness`
for authored components, graph changes, mounts, and rerenders. Extend existing
fixtures where they already express the behavior; do not duplicate the same
success assertions in a second bespoke suite.

Use narrow tests for manager identity, key permissions, local scope checks,
callback cardinality, and diagnostics that the integration fixture cannot
express clearly. New generic lifecycle behavior requires lifecycle-owned tests
and generated-source goldens in `yidl-lifecycle`; Pyrolyze's fixtures own the
application integration behavior.

The canonical integration scenario should cover:

1. Root, two sibling slots, nested component render context, and call-site state
   all sharing the root TM.
2. Successful render, unchanged rerender, child reorder/removal, and callback
   replacement while preserving stable object/dispatch identity where required.
3. Failure after an earlier child finishes: published UI, callback, child
   membership, and invocation arguments retain their previous values.
4. Replacing/removing an owned resource followed by failure; no old resource is
   irreversibly retired before publication.
5. Independent pass/publication permissions and a sibling whose local scope is
   not active despite graph-wide key activity.
6. External-store/effect/async-effect/mount behavior and override subscription
   changes through success, failure, and later recovery.
7. Notification/hook failure after publication: committed results remain
   committed, cleanup runs, and the error preserves useful context.
8. A three-participant prepare failure proving that earlier participants do not
   publish before all required publication-key preparations succeed.
9. Three enlisted participants where the first after-commit hook raises: later
   mandatory retirement/notification hooks are still attempted, committed state
   stays published, and error reporting preserves the failure context.
10. Early rollback-callback and after-rollback failures with later participants'
    cleanup observable, local scopes exited, owned keys finalized, and a
    subsequent transaction/render able to recover. These complement L0's
    lifecycle-owned mechanics tests rather than duplicate their assertions.

Characterize nested/caught failure before asserting savepoint-like behavior.
Compare public observables, not internal generated class names, slot layouts,
or legacy record implementations. Never regenerate expected snapshots just to
hide an unapproved semantic change.

Runtime selection must happen before imports, preferably in isolated processes.
The default selector currently chooses the monolithic `lcm` path, while focused
state-manager tests import the decomposed path directly. Both facts must remain
visible in test reports until I7.

## Verification Commands

Run from the Pyrolyze repository root in an environment with its declared test
dependencies and the authored-source import hook available. This local checkout
uses neighboring editable repositories:

```sh
PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  uv run --with pytest --with pytest-cov python -m pytest -q \
  tests/test_runtime_context_lcm_phase3.py \
  tests/test_runtime_context_lcm_phase4.py \
  tests/test_runtime_context_lcm_phase5.py \
  tests/test_runtime_context_lcm_phase6.py \
  tests/test_runtime_context_state_lcm_context_base.py \
  tests/test_runtime_context_state_lcm_slot_expr.py \
  tests/test_runtime_context_state_lcm_leaf_rerender.py
```

Representative broader checks, expanded according to the slice inventory:

```sh
PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  PYROLYZE_CONTEXT_IMPL=bare_refactor_lcm \
  uv run --with pytest --with pytest-cov python -m pytest -q \
  tests/test_runtime_call_site_context.py \
  tests/test_app_context_override_context.py \
  tests/test_mount_advert_binding.py \
  tests/test_generic_backend_harness.py

PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  uv run --with pytest --with pytest-cov python -m pytest -q
```

These commands are examples for the local checkout, not claims that the broader
checks already pass. Inventory direct imports and selector overrides before
calling any run a cross-implementation parity run. Avoid changing lockfiles or
dependency revisions unintentionally while repairing the test environment.

From the neighboring `yidl-lifecycle` repository, check its generated base and
run its canonical suite when library-owned behavior changes:

```sh
PYTHONPATH=src:../yidl/src:../astichi/src \
  uv run python -m yidl_lifecycle.regenerate_lifecycle_base

PYTHONPATH=src:../yidl/src:../astichi/src \
  uv run python -m pytest -q
```

## Roll-Build And Change Boundaries

Before a roll-build, complete I0's decisions, commit this plan as requested,
verify clean relevant repositories, and agree a tag prefix. Do not interpret
writing this plan as a roll-build request.

For each implementation slice:

1. Add/adjust the canonical scenario or narrow failing assertion first.
2. Implement the smallest coherent change and remove its superseded mechanism.
3. Run focused checks and the applicable regression suites.
4. Review observable behavior and stop for unapproved semantic changes.
5. Commit/tag only when the slice's stated exit criteria are satisfied.

Commit library changes in `yidl-lifecycle`, consumer changes in Pyrolyze, and
record corresponding parent submodule revisions separately. Do not absorb
unrelated YIDL, Astichi, or workspace modifications into this integration.

The expected implementation requires no new YIDL grammar. A missing generic
facility must be discussed and specified in its owning project before a slice
can depend on it. Do not restore `pyrolyze.lifecycle` as an integration shortcut.

## Acceptance Checklist

- [ ] Every independent root graph allocates exactly one TM; nested contexts,
  slots, call sites, and transactional resource participants share it.
- [ ] Publication/pass keys have approved, tested lifetimes and write permissions.
- [ ] Local context scope activity is distinct from shared TM activity.
- [ ] Live nested TM sharing and local entry/reset/finalization pass together at
  I1, including changed native emissions, child removal, and failure recovery.
- [ ] Decorated state is authoritative; no `_lcm_sync` or duplicate field engine.
- [ ] Field rollback occurs through lifecycle, not manual value restoration.
- [ ] Resource acceptance/retirement and external side effects preserve approved
  success/failure ordering without a generic child-type dispatch loop.
- [ ] No migrated-path private call-site/per-slot TM or legacy record access.
- [ ] Graph construction does not patch lifecycle managers or attach through
  hidden default-factory side effects.
- [ ] Canonical fixtures prove whole-boundary failure and recovery, not only
  isolated per-slot commits.
- [ ] L0's lifecycle-owned multi-participant failure contract is verified before
  I2/I4/I6 rely on resilient cleanup/delivery; failing callbacks do not silently
  skip later participants' mandatory work.
- [ ] Runtime selection, public exports, broader regressions, and the full suite
  pass with approved differences explicitly recorded.
- [ ] Performance results and remaining limitations are documented separately
  from claims of semantic completion.

## Decisions Required Before Execution

1. Confirm the publication/pass split against baseline behavior. In particular,
   decide whether an earlier child pass remains provisional until its outer
   render boundary succeeds.
2. Decide caught nested-failure semantics: abort the owning boundary or require
   a separately specified savepoint facility. Do not silently choose either.
3. Approve the resource-category mapping, including transaction participation,
   reference replacement, and legacy-refcount versus intrinsic-reference
   ownership. A `binding()` field's current implementation alone does not settle
   the required Pyrolyze resource behavior.
4. Pin generation/notification/retirement ordering and post-publication error
   behavior before removing the corresponding legacy hooks.

Once these decisions are recorded, the slices can be assessed individually for
roll-build readiness. The existing passing focused tests are a starting point,
not evidence that these unresolved graph-wide cases already work.
