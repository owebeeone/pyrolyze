# Pyrolyze YIDL Lifecycle Integration Plan

## Status And Purpose

Proposed continuation of the LCM migration on `lcm-resume`.

The objective is to replace Pyrolyze's handwritten transactional state engine
with `yidl_lifecycle`-decorated classes. Installing the decorator underneath the
old engine is not the end state. The migration must remove duplicate state,
field snapshots, field restoration, and class-name-based child field-transfer
dispatch. The current completion direction is the single-cohort amendment
below; the earlier holder-first sequence is retained as historical planning.

### Current Completion Authority (2026-10-04)

The user subsequently chose **one outer render completion owner, including
nested work**, while retaining multiple semantic transaction keys and their
write permissions. `dev-docs/PytoLifecyleIntegSingleCohortPlan.md` is the current
DRAFT amendment snapshot and gives the exact supersession table, gated
implementation sequence, and acceptance observations. Its gated design,
private SC1 owner, and private SC2 field-only proof have now passed review;
the exact implementation tuple and scope are recorded in
`dev-docs/history/lifecycle-integration/PytoLifecyleIntegSC2-ReviewLoop.md`. SC3's concrete resource/notification
and registration/removal audit is now recorded in
`dev-docs/PytoLifecyleIntegSC3.md`; its first bounded library prerequisite is
`dev-docs/PytoLifecyleIntegSC3-L0Plan.md`, accepted as a design at Pyrolyze
`715a0074625844afae05d08afc86557d196bdecd` after dual review and original-finding
closure; its exact scope/tuple are in the adjacent review ledger. The library
implementation and private consumer adoption are not yet accepted.
Neither document activates resource routes or authorizes snapshot deletion.
Other keys retain application-specific completion; no atomic multi-key
operation is assumed.

Where the earlier body below requires independent nested publication,
caught-child recovery without outer abort, or postpones render-manager sharing
until U1/U2, those rules are superseded as enumerated in the amendment. They
must not be used to reject the newly chosen target or to accept incompatible
runtime behavior. Historical review reports remain unchanged. I1b construction
acceptance is intact; full I3a completion and broad runtime activation are not
accepted. The privately gated SC2 proof is accepted only at its recorded tuple.
Resource lifetime, dirty/metadata permissions, and generic failure-draining
gates not replaced by the amendment remain mandatory.

This document updates the integration direction in
`dev-docs/history/legacy-lifecycle/ContextLifecyleMetaprogrammingPlan.md` and
`dev-docs/history/legacy-lifecycle/LifecyleAdoptionPatterns.md`. Their behavioral goals remain useful, but
their references to `pyrolyze.lifecycle`, record internals, and transactional
`binding()` fields do not describe the extracted library exactly.

This is a plan, not authorization to implement, switch the default runtime, or
change public semantics. The decision gates below must be resolved before a
roll-build is advertised as ready.

Completion detail added on 2026-10-03 after the I0 investigation. The earlier
review-loop acceptance covered the preceding plan revision, not approval of
the outstanding semantic decisions or independent review of this revision.
Historical completion-review tuples are recorded in
`dev-docs/history/lifecycle-integration/PytoLifecyleIntegCompletionPlan-ReviewLoop.md`. The user-directed scope
and sequencing revisions below supersede that acceptance for the current plan;
historical reports remain unchanged. The holder-first campaign is recorded in
`dev-docs/history/lifecycle-integration/PytoLifecyleIntegHolderFirstPlan-ReviewLoop.md`.

### Migration First: Scope Decision

On 2026-10-03 the user deferred the stronger outer publication guarantee and
recast D2/D3 as minimal migration compatibility requirements, with broader
failure-containment and resource-lifetime work after integration.

The integration replaces state authority, not the existing runtime contract:

- Preserve existing publication boundaries, including an earlier child's
  publication surviving a later parent failure where the compatibility
  reference does that. Do not hold every child provisional until outer success.
- Preserve caught-child recovery and existing exception/cleanup behavior at the
  affected sites. Do not add blanket abort, savepoints, or a new comprehensive
  containment policy as migration prerequisites.
- Replace holder storage and field transfer while preserving existing resource
  acceptance, subscription, cancellation, reference-counting, and retirement
  behavior. Resource-specific domain methods may remain; they are not a second
  field-storage engine.
- Record pre-existing defects as explicit debt. Do not silently repair them,
  skip their tests, or defer regressions caused by the migration.

The user subsequently chose **holder replacement first, manager unification
afterward**. Preserve today's manager/key cohort and completion owners during
I1-I8. Replace manual holders with lifecycle authority at their existing
boundaries, without making separate boundaries share a transaction as part of
the replacement. An existing implicit manual-holder boundary may obtain a
lifecycle-owned manager when it is decorated; document that mapping, rather
than introducing application snapshots or participant-selective TM callbacks.

One shared graph TM remains a future target, not a holder-integration acceptance
criterion. Its unresolved isolation mechanism belongs to U1/U2 below. A shared
key can complete unrelated enlisted work; passing the same manager is not proof
of compatibility. Do not silently impose outer atomicity or call temporary
boundary-specific managers the final unified architecture.

D4's library failure-completion proposal and D5's completion ordering remain
separate pending decisions. They do not authorize the deferred D1-D3 hardening.
Any approved D4/D5 behavioral difference must be identified separately from the
compatibility baseline, not attributed implicitly to integration.
The post-integration work is listed separately below and is not part of the
integration roll-build sequence.

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

I0 baseline and characterization are now recorded in
`dev-docs/history/lifecycle-integration/PytoLifecyleIntegI0Findings.md`, with the field/resource inventory in
`dev-docs/history/lifecycle-integration/PytoLifecyleIntegI0Inventory.md`. The original runtime permits early
child publication and caught-child recovery. Preserve those observations as
the migration compatibility contract; the atomic outer-boundary alternative is
deferred. I0's bounded completion probe is sufficient to choose the holder-first
sequence; the shared-TM/key mechanism is no longer its execution gate. Remaining
resource/hook decisions gate only work that depends on those contracts.

The subsequent bounded shared-completion preflight is recorded in the findings
document and `tests/data/lcm_integration/shared_completion.py`. Generated parent
and child instances on the same manager/key cannot currently complete
independently: nested commit only reduces depth, direct child commit publishes
both, and child rollback discards both. No compatible isolation mechanism has
yet been approved. The user chose not to extend that API now. U1/U2 live sharing
remains blocked on a later API/ownership design; I1-I8 retain the existing
completion cohorts. This is not approval of stronger publication or containment
guarantees.

The current I0 evidence supersedes the historical focused-test result for
readiness assessment: 37 focused/characterization tests pass, but the full
default suite has 13 existing failures and the broader decomposed-path subset
has 14. See the findings document for exact targets and provenance. These are
not permission to skip tests or call the eventual runtime switch complete.

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

### Existing Boundaries First; One Manager Later

For holder integration, retain the manager/key cohort of each existing
completion boundary. Nested render contexts currently have their own manager;
rerunnable slots within a render context use that context's manager; call-site
collections own their pass manager. Do not unify those cohorts in I1-I8.
Explicit constructor injection must preserve those identities, not patch a
generated private slot midway through factory evaluation.

The later U1/U2 target is one manager per root graph, with compatible completion
isolation. Independent root graphs remain independent. That target is not
implemented or required by holder-first acceptance.

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
| Existing completion boundary / its TM owner | Explicit key activation and completion ownership at existing publication boundaries, error handling, generation coordination |
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

### Completion Contract

For every migrated state category, the implementation must answer four
questions in the code and checkpoint report:

1. Which declaration is the sole authoritative value, and which facade is read
   while rendering versus while serving published behavior?
2. Which transaction key governs its writes, and which existing boundary owns
   completion without publishing or discarding another boundary's work?
3. Which remaining method is domain work rather than field transfer or undo?
4. Which old fields, methods, dispatch branches, and callers were deleted?

A wrapper around the old state manager is not completion. Nor is replacing a
manual transfer loop with an equally generic Pyrolyze hook loop. Lifecycle
owns field preparation/publication/discard; a resource adapter owns only the
external behavior of its resource. Hooks must not copy the decorated fields
back into a legacy authoritative store.

Do not target a percentage line-count reduction. Judge the result by removal
of duplicate authority and transaction responsibility. Rendering and resource
algorithms may remain substantial after the bookkeeping is gone.

## Transaction And Scope Semantics

### Proposed Key Assignment

The following classifies storage roles, not a mandatory graph-wide key split.
I0/I2 must map these roles to existing keys and completion ownership that preserve the
compatibility reference's publication timing. The proposed universal
`DEFAULT_TRANSACTION` publication / `PASS_TX_KEY` scratch split is deferred
where it would change that timing.

| State | Key Or Storage | Lifetime |
| --- | --- | --- |
| Published child membership/order, UI, invocation inputs, callback selection, override values | `managed` / supported `owned`, key selected for compatible completion ownership | Publishes at its existing accepted boundary; failure discards only still-unpublished work within that boundary |
| Visitation, staged callback queue, local pass-active marker, genuinely transaction-local scratch | `transient` on the applicable key, or explicit per-invocation locals | Cleared/reset at the existing pass or transaction boundary, not necessarily outer root completion |
| Owner, parent identity, slot identity, immutable configuration | `const` or constructor `initvar` | Construction/lifetime data |
| Inert memoization/helper storage | `local_store` or justified ordinary shared storage | Survives transactions without changing rollback-visible results |

Published state is currently also assigned to `PASS_TX_KEY` in
`src/pyrolyze/runtime/context_state_lcm/context_base.py` and the component invocation record. Moving
it to another key requires compatible completion ownership and explicit
activation. Do not move it to the default key just to implement the now-deferred
outer atomicity proposal; changing declarations alone can make writes illegal
or change which participants publish together.

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
scratch explicitly or keep it in ordinary function locals. Retaining an
existing independent completion boundary is different from inventing a manager
solely to reset scratch on each function return.

### Boundary Ownership

Migration boundary requirements:

1. Identify the existing owner and publication point for each migrated value.
   Preserve that owner's current manager/key cohort; root success is not the
   only allowed publication point.
2. Activate keys explicitly and preserve local pass entry, reset, and exit.
   Existing successful child completion may publish that child's values before
   its parent finishes. Preserve that observation without completing unrelated
   parent/sibling work merely because it shares a manager or key.
3. Replace field preparation/publication/discard with lifecycle operations at
   those same boundaries. Keep existing domain graph validation, resource
   acceptance, and notification ordering unless a separate change is approved.
4. On failure, perform the existing boundary's cleanup and propagation behavior.
   Do not undo already published child values or introduce a new outer abort
   policy. Preserve existing caught-child recovery.
5. Exit local scope markers and reset applicable scratch without treating shared
   key activity as proof of local ownership.

Only finish transactions the completing boundary owns. Joining an already
active transaction does not confer permission to commit or roll back it. The
holder replacement must demonstrate the compatibility observations in I0
without changing completion cohorts. The current API cannot isolate arbitrary
participants on a shared key; U1/U2 must address that limitation separately.
If holder replacement itself cannot preserve an affected boundary, stop that
checkpoint to discuss the smallest compatibility mechanism. Do not resolve the
conflict by silently adopting deferred outer atomicity.

After publication, rollback cannot undo accepted values. Drain-first failure
handling and grouped reporting remain D4/L0's separately proposed Phase F-1
contract, not a guarantee of the pinned TM. Verify it before migrated hooks
depend on it; this is not permission to redesign D2/D3 during integration.

### Child Failure Compatibility (D2)

Minimum migration requirements:

- Retain the I0 parent-failure and caught-child-recovery observations at the
  affected boundaries, including the case that stages child UI before raising.
- Preserve existing handling, propagation, fallback/retained-child outcomes,
  and cleanup calls. Do not replace caught recovery with automatic graph abort.
- Test that holder replacement does not newly publish/discard unrelated
  work, leak local scope state, or prevent the next supported render.
- Distinguish a pre-existing failure-handling defect from a migration regression.
  Record the former as debt; resolve the latter before completing its slice.

The comprehensive phase/effect classification, candidate-validity policy,
savepoints, and stronger recovery/abort guarantees move to post-integration
work. They are not I0/I1/I2 exit requirements. No new Pyrolyze snapshot engine or
private child TM may be introduced to claim that deferred guarantee.

This does not certify the existing handling as safe for every throw site.
Preserving observed recovery is a compatibility objective, not proof of full
containment. If compatibility itself requires an unsupported library facility,
discuss that bounded requirement rather than making the whole hardening project
a migration prerequisite.

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

Do not infer graph-wide atomicity from one manager or a multi-key commit. Preserve
the existing publication boundaries and specify scratch completion explicitly.
The single outer publication-key design is deferred, not an assumption used to
simplify migration tests.

## Construction And Initialization

Allocate or resolve the TM at the **existing completion ownership boundary**.
Pass the existing `transaction_manager=` constructor argument to generated
lifecycle classes before factories run. Do not change nested-render or
call-site manager allocation policy while replacing holders.

Expected construction shape, illustrative rather than a new public API:

```python
root_tm = TransactionManager(tx_keys=(PASS_TX_KEY,))
root_state = RootState(owner=root, transaction_manager=root_tm)
slot_state = SlotState(
    owner=slot,
    parent_state_mgr=root_state,
    transaction_manager=root_tm,
)
# A nested render retains its independent completion cohort during integration.
child_tm = TransactionManager(tx_keys=(PASS_TX_KEY,))
child_state = NestedRenderState(owner=child, transaction_manager=child_tm)
```

Include every key used by that boundary; do not silently create unknown spaces.
Do not eagerly allocate a throwaway per-slot manager and replace it later through
`_y_state` internals. Legitimate boundary managers are retained, not overwritten.

Factory evaluation remains the generated constructor's responsibility. Named
factory dependencies, including `local_store` factory parameters, are available.
Initialization must not patch the manager midway through those evaluations.

Graph registration/attachment is a separate domain action after construction.
Move it out of `_attach_to_graph_bad_program` factories into an explicit
construction/attachment path, preserving existing registration and failure
cleanup behavior. This is not user `__init__`/`__post_init__` chaining or a new
graph-wide provisional-resource guarantee.

### Constructor Inheritance Prerequisite

`SlotContextStateMgr` and several leaf subclasses currently initialize ordinary
attributes in handwritten `__init__` methods. Decorating an ordinary subclass
does not harvest those assignments as fields, and generated constructors do
not chain the old initializers. Therefore adding `@managed_context` only to
`EventHandlerSlotContextStateMgr` would leave its base construction incomplete.

Before a value-state subclass becomes authoritative:

1. Declare the shared slot construction data on the appropriate base: owner,
   resolved render/root context, parent, slot identity, context configuration,
   and any required site metadata.
2. Separate immutable identity from mutable invocation metadata; do not make
   metadata `const` simply because it was previously assigned in `__init__`.
3. Declare dirty/seen state according to the approved published/local-pass
   classification, including initialization and reset at each local pass.
4. Verify the resolved field set for both ordinary slot subclasses and the
   multiple-inheritance rerunnable/context path. There must be one state and
   one correctly injected boundary TM, not a second decorated wrapper around a
   legacy object.
5. Construct through the existing state-manager factory, then perform explicit
   graph attachment. Remove base/subclass initializer calls whose sole role was
   populating the now-declared fields.

Thread the injected manager through both `SlotContextStateMgr` construction
branches, including the branch that currently calls `StateMgrBase` directly.
It is insufficient to update only the `ContextBaseStateMgr` branch.

## Expected End-State Shapes

These sketches describe the intended runtime-only consumer shape after the
relevant prerequisites. They are not current implementations, complete modules,
new public APIs, or permission to bypass the decision gates.

### Event Callback Selection

The first readily inspectable value migration is the event handler. After the
shared slot declarations above exist, its additional state should look like:

```python
import os
from typing import Any, Callable

from .lifecycle_adapter import local_store, managed, managed_context
from ._support import _BOUND_METHOD_SELF_MISSING
from .slot_context import SlotContextStateMgr


def _callback_key_for(callback: Callable[..., Any]) -> object:
    bound_self = getattr(callback, "__self__", _BOUND_METHOD_SELF_MISSING)
    bound_func = getattr(callback, "__func__", None)
    if bound_self is not _BOUND_METHOD_SELF_MISSING and callable(bound_func):
        return ("bound_method", id(bound_self), bound_func)
    return callback


@managed_context
class EventHandlerSlotContextStateMgr(SlotContextStateMgr):
    _callback: Callable[..., Any] | None = managed(
        default=None, init=False, compare="identity"
    )
    _callback_key: object | None = managed(default=None, init=False)
    _dispatch: Callable[..., None] | None = local_store(default=None)

    def stage_callback(
        self, *, callback: Callable[..., Any], dirty: bool
    ) -> Callable[..., None]:
        callback_key = _callback_key_for(callback)
        candidate = self.current
        if (
            dirty
            or candidate._callback is None
            or candidate._callback_key != callback_key
        ):
            self._callback = callback
            self._callback_key = callback_key
        return self._dispatch_callable()

    def _dispatch_callable(self) -> Callable[..., None]:
        if self._dispatch is None:

            def dispatch(*args: Any, **kwargs: Any) -> None:
                callback = self.current._callback
                if callback is None:
                    if os.environ.get("PYROLYZE_ENV") == "prod":
                        return
                    raise RuntimeError("event handler is inactive")
                callback(*args, **kwargs)

            self._dispatch = dispatch
        return self._dispatch
```

Staging is permitted only inside the approved publication write boundary. A
stable dispatch callable always reads `.current`: it must not invoke a new
callback merely because render work has staged one. The lifecycle manager
publishes or discards that selection; this class has no `commit_handler()` or
`rollback_handler()` and no separate committed/staged callback attributes.

Preserve the reference's callback-key policy, including receiver identity and
function identity for bound methods, and dirty-forced selection. Distinct
value-equal receivers must still select different handlers; repeated bound
method objects from the same receiver/function retain the same key.

For holder-only compatibility, compare the staging guard against `.current`,
as the original and monolithic references do. Published A followed by pending B
then A, both with `dirty=False`, currently publishes B on success and keeps A
on failure. This is baseline debt, not desirable new semantics. The previous
effective-candidate proposal (which ends at A on success) is deferred as a
separate behavioral correction requiring approval. Keep historical observations
distinct from any later approved target. Dispatch reads `.current` throughout;
unpublished selection remains invisible to callers.

Identity comparison on the callback field avoids eliding a dirty-forced
replacement between distinct callable objects that compare equal. Keeping the
key initially makes that migration explicit; removing it is a separate
simplification only if the canonical fixture proves it has no independent role.

Preserve the dispatch closure's existing lifetime and retained-handler behavior.
Do not introduce weak references or rely on intrinsic reference counting to
replace existing explicit cleanup. Broader ownership/cycle auditing is deferred
D3 work; a new retention regression caused by migration is not deferred.

Deactivation remains a domain operation at its existing accepted-removal
boundary. Preserve callback visibility and resource cleanup timing; do not
write managed fields from an after-commit hook or retain `rollback_handler()`
solely to transfer/reset decorated values. I5/I6 migrate those responsibilities
without moving every retirement to outer root success.

### Context Pass Orchestration

`begin_pass()`, `end_pass()`, and `rollback_pass()` may remain as domain entry
points, but their responsibility must shrink as follows:

| Entry Point | Work That Remains | Work That Must Leave |
| --- | --- | --- |
| Local begin | Check/set this context's scope marker; reset this invocation's visitation and emission scratch | Change completion cohorts; snapshot current child order/dirty values; infer local activity from a global active key |
| Local successful end | Check structure; build candidate children/UI; complete lifecycle values at this context's existing publication point where applicable; preserve domain cleanup; exit local scope | Manually transfer decorated fields; dispatch field commits by child class; complete unrelated parent/sibling work |
| Local failed end | Preserve existing cleanup/recovery/propagation; discard owned unpublished work through lifecycle; exit local scope | Restore decorated fields from saved copies; introduce blanket abort; independently roll back unrelated shared work |
| Root completion | Perform existing validation and complete root-owned work through the TM; preserve generation, retirement, and notification ordering | Walk every child to perform generated field transfers; claim already published children are undone after parent/hook failure |

Candidate collections must be newly assembled values or use declared supported
working conversion. Reading `.current` provides the previous graph; mutating
that graph in place defeats rollback. The coordinator may retain an immutable
event/retirement batch for completion, but not a second snapshot engine for
decorated fields.

For event-handler children, UI assembly must use the existing polymorphic
committed-UI/entry interface rather than assume every state manager has a
`ui_state` field. Adding dummy UI state to an event handler solely to satisfy
that assumption is not the intended fix.

## Resources And Bindings

Distinguish three independent behaviors:

1. Staging replacement of a reference in its holder.
2. Committing/rolling back the referenced object's own state at its boundary.
3. Accepting and retiring the referenced resource.

Current `yidl_lifecycle.binding()` validates and directly stores a shared
reference; it does not stage reference replacement or automatically enlist its
referent. Current `owned()` stages references/maps and integrates
`BindingBase` acceptance/lifetime behavior. Sharing a TM is not sufficient to
turn an arbitrary `BindingBase` into a transaction participant.

### Minimum Resource Compatibility (D3)

For each affected category, record its current holder, referent state, and
domain cleanup calls. Select the smallest compatible replacement for storage:

- A lifecycle-decorated participant on its existing boundary TM for internal mutable
  state.
- A managed holder or supported owned reference/map for reference replacement;
  use `owned` only where its acceptance/lifetime contract is already compatible.
- A narrow Pyrolyze adapter/hook for external behavior that cannot be expressed
  as ordinary field publication.

These can be combined. Do not rename `binding()` to `owned()` mechanically:
existing `SlotCallBinding` and legacy call-site binding classes do not all
implement the extracted library's ownership contract.

`SlotCallBinding.commit()` can mean "run an effect", not "publish a decorated
field". Such domain methods need deliberate hook integration, not indiscriminate
deletion or a relocated loop over every graph object.

`CallSiteContextManager` must be migrated too. Retain its independent pass
manager during holder integration, remove legacy record access, preserve its
public/domain behavior, and express membership and visitation through lifecycle
model. Preserve the resource's existing lifetime policy: do not remove explicit
reference-count calls or add a second release merely because its holder changes.

Preserve observable unsubscribe, cancellation, graph removal, and acceptance/
retirement ordering at the existing boundaries. Existing domain cleanup methods
may remain; delete their field-transfer responsibility, not the resource
operation itself. Do not substitute garbage collection for explicit cleanup.
Tests must detect migration-created leaks, early disposal, or double release;
they need not establish a new universal lifetime contract or repair all existing
reference cycles.

Unified ownership/refcount policy, comprehensive cycle auditing, stronger
deterministic-retirement guarantees, and redesign of resource failure behavior
are post-integration D3 work. A concrete incompatibility introduced by the holder
replacement still blocks that affected checkpoint, not the entire hardening
programme.

A generic lifecycle `close()` protocol, generalized `derived` fields, and new
YIDL grammar are not prerequisites to be invented during this integration.
If existing facilities cannot preserve a resource's current semantics, stop the
affected checkpoint and discuss the smallest compatibility extension. Do not
make a broader lifetime redesign a prerequisite or add a second field engine.
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
| Slot-call resources | Boundary-owned participant/adapter plus compatible replacement policy | Duplicate holder transfer and generic child field dispatch; boundary managers remain until U1/U2 |
| Slot-expression sites | Lifecycle-owned membership and transient visitation/notification data on the existing independent pass boundary | Legacy record access and manager implementation, not independent completion ownership; retain a lifecycle-owned pass TM until U2 |
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

## Replacement And Deletion Ledger

Use `dev-docs/history/lifecycle-integration/PytoLifecyleIntegI0Inventory.md` for the full field/resource
inventory. This ledger states the completion obligations rather than repeating
all field facts. State-manager filenames below are relative to
`src/pyrolyze/runtime/context_state_lcm/`; other paths are repository-relative.

| Existing Mechanism | Authoritative Replacement | Owning Checkpoint / Required Deletion |
| --- | --- | --- |
| `_transaction_manager_bootstrap_bad_program` and generated private-manager patch | Existing boundary TM injected before factory evaluation | I1a: delete dummy declaration, factory, and private-slot assignment |
| Per-slot TM defaults used as throwaway managers | Existing render manager passed through construction factories | I1a: remove discarded allocations; retain independent nested-render/call-site boundary managers until U1/U2 |
| `_attach_to_graph_bad_program` | Explicit attachment after successful construction | I1: delete side-effect factory; preserve existing failure cleanup and introduce no new registered orphan |
| Graph-wide `is_scope_active()` and `_pass_started_tx` ownership inference | Context-local entry/reset/exit plus explicit existing-boundary ownership | I1/I2: remove key-activity-as-local-scope test and accidental completion of unrelated work; preserve legitimate child publication |
| `_pass_child_order`, `_pass_child_dirty`; eager current-map edits | Managed candidate membership/UI and classified dirty fields | I3a: delete snapshots/restoration loops and current-collection mutation |
| `_committed_callback`, `_committed_key`, `_staged_callback`, `_staged_key`, `commit_handler()`, `rollback_handler()` | Managed callback/key; stable dispatch reads current selection | I3b: delete four stores, transfer/reset methods, and their dispatch callers |
| `_last_args`, `_last_kwargs`, invocation identity/schema/site metadata | Managed invocation values or the existing frozen invocation record | I3c: replace value stores/transfers at their existing acceptance points; keep dirty projection/evaluation logic |
| Legacy `current_record/working_record` | Authoritative lifecycle membership/visitation on the existing call-site pass boundary | I4a: delete record access; retain independent pass TM and compatible domain ownership calls until separately migrated |
| Slot binding commit/rollback loops used for field transfer | Resource participant plus narrowly scoped external-effect hooks | I4b/I4c: delete generic loops; preserve only resource-specific delivery/cancellation/retirement |
| Component `_pass_owned_event_handler_order` used for value restoration | Managed identity/child membership plus existing domain cleanup | I5: delete field snapshots/reconstruction; preserve child retirement timing rather than defer it to root success |
| Override committed/pending/snapshot tuples and lookup copies | Managed value/lookup selection plus domain subscription hooks | I6a: delete transfer/restore stores; never emit rollback-visible notifications during staging |
| Directive `_pass_committed_selectors` and eager selector publication | Candidate selectors validated with mount/UI projection | I6b: delete selector snapshots and restore loops |
| Child-class-name commit/rollback dispatch in base pass methods | Enlisted field publication plus resource-local hooks | Delete each migrated branch at its checkpoint; I6b deletes the dispatcher when the final category is gone |
| Monolithic helper states, `_LifecycleSlotMixin`, `_lcm_sync`, `_lcm_txm` | Completed decomposed implementation under canonical `lcm` routing | I7: remove superseded engine and callers, not a second parallel implementation |

Checkpoint reports must list the actual removed symbols/callers and the
canonical scenario proving their replacement. Search the active dependency
path, not only the edited file: deleting a method while leaving a caller in
base pass dispatch is not completion. Original/reference implementations may
retain their engines until their separately approved retirement; distinguish
them from migrated-path remnants in the search report.

A partially migrated generic dispatcher may temporarily retain branches for
unmigrated categories only. Name those categories in the checkpoint report;
never route migrated fields through both lifecycle and the old dispatcher.

## Implementation Slices

Each slice uses red/green/refactor, removes the corresponding obsolete mechanism,
and has a separately reviewable result. A slice that merely introduces decorated
fields alongside the old authoritative state is incomplete.

### I0: Baseline And Migration Compatibility Gate

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
   Record the affected sites' existing publication, recovery, and cleanup
   behavior. A comprehensive throw-site containment inventory is deferred D2
   work, not the exit gate for replacing holders.
6. Pin the compatibility reference where runtimes disagree, then record existing
   manager/key ownership and preserve those publication points. Do not
   require the deferred universal publication/pass split or outer atomicity.
   Discuss any unavoidable semantic change before continuing.
7. Characterize multi-participant prepare/apply/hook/rollback failures against
   the Phase F-1 intended contract. Record the known pinned fail-fast limitation
   and approve the smallest lifecycle-owned L0 scope before dependent work.

Exit: a recorded baseline, existing boundary/key ownership for the affected
slices, and a minimal holder/referent/domain-cleanup mapping. Broad containment,
savepoint, and lifetime redesign are not exit requirements. An unsupported
compatibility requirement blocks the affected later slice; it is not permission
to rebuild the legacy field engine inside an adapter.

Recorded work is baseline/inventory and the shared-completion limitation, not
an integration pass tag. The user approved retaining existing boundaries first.
Retain
the observed original snapshots, and add approved target expectations rather
than silently rewriting the historical characterization.

The blanket abort recommendation in the historical I0 findings and the later
outer-atomicity/containment proposal are superseded for integration by the
migration-first scope decision. Keep the observations; do not treat historical
recommendations as approved runtime changes.

### L0: Lifecycle Failure-Completion Prerequisite

This is a separately committed `yidl-lifecycle` checkpoint, not Pyrolyze domain
logic. I0 must approve its scope and any unresolved policy choices before code
changes. It reconciles the existing Phase F-1 manager contract with the pinned
implementation; review-loop acceptance of this plan does not authorize it.

The SC3 specialization is `dev-docs/PytoLifecyleIntegSC3-L0Plan.md`. Its Exact
Phase F-1 Supersession table proposes the precise bounded D4 policy differences
for preparation and after-action eligibility. If accepted, that table controls
these requirements where they differ from historical Phase F-1 wording; it
does not accept the library implementation, resource routing, or D5 timing.

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
6. Verify independent completion actions inside one generated participant,
   not only draining between participants. A throwing first same-key
   after-commit hook must not skip a second independently declared hook; apply
   the same requirement to after-rollback hooks, including inherited/local
   hook composition. Preserve deterministic order, exactly-once attempts, and
   hook/participant/key context in collected failures. A throwing action may
   remain incomplete and reported; later independent actions must be attempted.

The manager can drain other participants, but cannot resume a generated
callback after an internal hook call has unwound it. Lifecycle-owned generated
after-hook invocation must therefore drain its independently declared hooks
and report collected failures at that boundary. This makes Phase F-1's existing
all-after-hooks requirement explicit; it is not supplied by a manager-only
dispatch correction. It does not require continuing dependent preparation or
arbitrary statements inside an individual throwing hook.

Use the actual manager implementation in `yidl-lifecycle`'s
`src/yidl_lifecycle/transaction_yidl.py`. Locate the existing failure tests and
golden harness there before adding coverage. Narrow protocol tests own callback
draining/error aggregation; generated lifecycle goldens own observable staged
field behavior and per-hook composition. Require generated coverage with two
same-key hooks on one participant, first throwing and second recording cleanup,
plus another enlisted participant. Cover commit and rollback, with inherited
and local hooks composed. Assert state outcomes, exactly-once attempts, useful
error context, finalized keys/tokens, and subsequent-transaction recovery. Do
not copy the entire Pyrolyze I0 probe into a second success suite.

Exit: an approved, tested lifecycle failure-completion contract and recorded
library revision. I4/I6 mechanisms depending on this stronger contract cannot
activate without this evidence. Holder-only replacements preserving existing
domain cleanup calls do not require L0 first. Existing single-hook tests or manager-only
multi-participant tests are not sufficient; Pyrolyze's eventual integration
fixture must also prove per-action domain-batch draining, local-scope
cleanup and recovery when library failures cross the root boundary.

### I1: Construction Seams At Existing Boundaries

Do not enable new nested-manager sharing in this slice.

**I1a: Explicit manager injection before initialization.**

1. Add a runtime-only state-manager construction entry point used by the owner
   facade factories. Resolve the same render-boundary manager that the current
   bootstrap factory installs; pass it through `transaction_manager=` before
   generated initialization. An independent render still allocates its own TM.
2. Cover ordinary and decorated derived construction, including the rerunnable
   multiple-inheritance path. Direct generated constructors remain available,
   but callers wanting boundary resolution must use the construction entry point
   or explicitly supply the manager.
3. Remove `_bootstrap_transaction_manager_bad_program` and its dummy field.
   No replacement may write generated state internals or allocate then overwrite
   a throwaway manager.
4. Preserve owner/initvar/default-factory behavior and each boundary's existing
   identity. Verify that an initialization factory observes the injected manager.

This is the next bounded implementation checkpoint. It is a constructor
prerequisite, not completion of holder migration or manager unification.

**I1b: Explicit attachment, with common slot declarations in I3a.**

Move graph registration out of `_attach_to_graph_bad_program` factories once
common slot inputs are declared. Construct fully, then attach through the
runtime-only factory. Preserve existing failure cleanup and registration order;
do not introduce root-wide provisional resources. Include both ordinary-slot
and rerunnable branches. Do not delete side-effect factories before every
construction caller has an explicit attachment path.

Verification: the root and its existing rerunnable participants share their
current manager; independently completed nested renders and call-site collections
retain theirs; independent roots remain independent. Existing native emissions,
child removal, failed pass/recovery, and characterization snapshots must not
change. Manager count reduction is not this slice's exit criterion.

Primary edits: `_base.py`, `context_base.py`, the owner factory in
`context_bare_refactor_lcm.py`, then common/derived slot constructors in I1b.
Do not broaden this checkpoint into RenderContext TM policy changes.

### I2: Existing Local Boundary Audit

This audit runs alongside the affected holder checkpoints, not ahead of every
holder migration and not as a shared-manager rollout.

1. Record each affected value's existing begin/publish/discard owner and cohort.
   Retain existing keys and explicit-key completion calls.
2. Separate local pass entry/reset/exit from transaction-key activity where the
   replacement requires it. Preserve existing supported re-entry behavior;
   characterize it before choosing a bool/depth implementation.
3. Replace field transfer at the existing accepted boundary with lifecycle
   completion. A temporary boundary method may call its own manager; it must
   not copy decorated fields or invoke generated callbacks directly.
4. Preserve out-of-render invalidation/deactivation permissions and resource
   cleanup timing. Do not change blanket failure policies to simplify storage.
5. Delete a class-dispatch branch only when its corresponding migrated category
   has a complete lifecycle path. Unmigrated resource-domain branches may remain.

Verification: unchanged call elision, repeated local passes, failed candidate
discard, accepted earlier child surviving later parent failure, caught-child
recovery, and later supported rerender. Never finish an unrelated boundary's
work. Preserve the historical reference observations without silently correcting
other decomposed-path defects.

A borrowed active transaction without an identifiable completion owner requires
a bounded discussion at the affected site. It does not authorize savepoints,
participant-selective commit, global abort, or forcing every value onto the
default key. U1/U2 own future shared-manager isolation.

### I3: Decorated Value State Becomes Authoritative

1. Finish shared slot declarations, then event-handler callback/key state and
   leaf/rerunnable argument and identity state, using the existing decomposed
   class boundaries. Constructor inheritance is a prerequisite, not an assumed
   capability of decorating an ordinary subclass.
2. Preserve stable event dispatch identity and committed-callback visibility.
3. Classify dirty flags and visitation separately; remove manual dirty snapshots.
4. Build candidate child maps/UI through field assignments or declared
   thaw/freeze behavior. Never mutate a current collection in place and expect
   rollback to undo it.
5. Remove duplicate committed/pending fields and restoration for these values.

Verification: canonical rerender sequence, unchanged-call elision, identity
comparison, callback replacement, and failure after one child completes.
Current values change at their existing publication boundary; already published
children may remain changed after a parent failure. Discard still-unpublished
values through lifecycle, not an application copy loop.

Use three bounded commit/tag checkpoints under I3:

| Checkpoint | Edits And Deletions | Canonical Proof |
| --- | --- | --- |
| I3a: Common slot/value declarations | `_base.py`, `slot_context.py`, `context_base.py`, and affected derived declarations/factories: identity inputs, published dirty/site metadata, local visitation, candidate map/UI assignments; remove initializer-only storage and order/dirty snapshots | Root/sibling/nested construction, unchanged-call elision, repeated local reset, and failed candidate membership/UI with previous current values intact |
| I3b: Callback selection | `event_handler_slot_context.py` and its base dispatch callers: implement the compatibility shape; delete manual callback stores, `commit_handler`, `rollback_handler`; fix polymorphic UI assembly | Retained dispatch before/during/after success/failure; equal-but-distinct bound receivers use identity keys; A then pending B/A ends at B on success and A on failure until a separate fix is approved; dirty-forced distinct/equal callable selection; staged callbacks remain invisible until publication |
| I3c: Invocation values | `leaf_slot_context.py`, `rerunnable_slot_context.py`, `slot_call_slot_context.py`, and related container/loop value declarations: managed input/identity/schema/site metadata; remove duplicate snapshots/transfers while preserving acceptance timing | Unchanged elision, changed input, early child success followed by parent failure, and recovery with the reference's accepted invocation still authoritative |

Each checkpoint keeps the domain call/evaluation algorithms. I3c does not
pretend a managed `_binding` reference makes the referent transactional; that
resource migration belongs to I4. Audit mutable objects inside argument tuples
and frozen invocation records separately from the immutability of their holder.

Checkpoint update, 2026-10-08: bounded I3b selection stores/callers and a separate
private handler-enabled proof are accepted at
`6be1b8f610c13eda18a451688377370cb1dbb087`; see
[the exact scope and evidence](PytoLifecyleIntegCallbacks.md). The retained
unactivated component failure route still needs its small local-discard
compatibility adapter. This does not complete I3a/I5 or activate resource routes.
The bounded I3c leaf argument checkpoint is accepted after Code/State GO/GO at
`b188301216486aee3b43c1ecc7b7fe89307d0273`; see
[invocation scope and evidence](PytoLifecyleIntegInvocation.md). Slot-call values
and binding selection are the next bounded checkpoint through the single-cohort
amendment. Other I3c/I4 work and default-runtime activation remain gated.

### I4: Call Sites And External Resource Participants

Conditional prerequisite: L0's failure-completion evidence before relying on
its stronger guarantees. Preserve existing domain calls while approval is
pending. Do not move
mandatory retirement or delivery to lifecycle hooks on the fail-fast baseline.

1. Migrate `_CallSitePassContext` / `CallSiteContextManager` from the legacy
   lifecycle and record internals to supported fields/facades on existing cohorts.
2. Implement the minimal I0 holder/referent mapping for slot value, external
   store, effect, async effect, and mount-advertisement bindings in their owning
   modules, without redesigning their lifetime policy.
3. Preserve resource-specific behavior through lifecycle hooks/participants or
   retained domain methods; map existing acceptance, subscription, cancellation,
   and replacement timing rather than redesign it.
4. Retain existing call-site/per-slot completion cohorts until U1/U2; remove generic slot binding commit/rollback
   dispatch once their replacements are covered.
5. Make staged-site visitation and post-publication notifications explicit,
   accounting for transient cleanup timing.

Verification: unchanged manager/cohort ownership, including call sites; resource acceptance,
failure cleanup, replacement, effects/async effects, and mount notifications
match their existing boundaries and cardinality. Include early child acceptance
followed by parent failure; do not expect root rollback to undo it.
No hidden legacy TM or explicit-refcount/intrinsic-refcount double release.

Use the following resource checkpoints, each deleting its obsolete callers:

| Checkpoint | Scope | Replacement And Removal |
| --- | --- | --- |
| I4a: Call-site collection | `src/pyrolyze/runtime/call_site_context.py`, `src/pyrolyze/runtime/slot_expr.py`, `slot_expr_slot_context.py` | Retain independent pass completion; express collection/visitation through facades; remove direct record access and duplicate authority in standalone and integrated paths without changing legacy referent ownership |
| I4b: Value/subscription participants | Slot-call state and the owning slot-value/external-store binding modules | Separate holder replacement from referent state and subscription lifetime; remove manual field commit/restore; retire a replacement subscription only at the approved boundary |
| I4c: Effect/async/mount participants | Owning effect, async-effect, mount-advertisement modules and slot/expression dispatch callers | Stage request/dependency/advertisement state; keep resource-specific delivery/cancellation; remove generic participant loops once hooks cover that category |

Standalone and integrated slot-expression use retain their current independent
call-site pass completion. Test both through existing canonical fixtures;
unifying their manager with the render manager is U1/U2 work.

For each affected resource, record the current acceptance/cleanup calls and
keep them observable after replacing its holder. Do not replace explicit
cleanup with `BindingBase.__del__`, change reference-counting policy, or add a
generic `close()` protocol. A migration-created cleanup/retention incompatibility
requires bounded discussion; broader lifetime guarantees and cycle repair are
deferred D3 work, not a new exit requirement.

If D4's stronger completion contract is approved, resource-local delivery/retirement
batches must also attempt later independent
actions after an earlier action raises, collecting failures with action/resource
context. I4 owns this domain-batch behavior; manager-level or generated-hook
draining cannot resume the remainder of one throwing domain function. Do not
turn the batch into a loop that publishes decorated fields or traverses all
graph participants. Respect dependent-action ordering and report an incomplete
throwing action rather than claim it was repaired or automatically retried.

### I5: Child Ownership And Component Boundaries

1. Migrate component identity/schema, child render context, and owned handler
   membership away from `local_store` where they affect published behavior.
2. Use the compatible holder/participant mapping; keep existing child-lifetime
   operations without imposing a new `owned()` contract on arbitrary children.
3. Preserve child identity across successful unchanged renders and recreate only
   when the domain requires replacement.
4. Preserve accepted child removal/replacement and failure cleanup at their
   existing boundaries, including cleanup before outer success where that is
   current behavior. Do not introduce root-wide provisional child lifetimes.
5. Remove owned-handler order snapshots and manual rollback reconstruction.

Verification: nested context retains its current independent TM, child failure and parent failure,
handler reorder/removal, identity preservation, and cancellation/unsubscribe
ordering. Include a failure after staging removal of an existing child.

Keep two bounded checkpoints: I5a makes component identity/schema, child
selection, and handler membership authoritative; I5b migrates existing
accepted-removal and failed-candidate cleanup. Primary scope is
`component_call_slot_context.py`, slot graph attachment/deactivation, and the
root registration callers. I5 is incomplete until both checkpoints pass.

Pin the existing replacement algorithm in the canonical scenario before moving
its holder to lifecycle: construction/attachment, selection acceptance, old
child retirement, and failed-attempt cleanup. Preserve their timing and identity
behavior. Do not impose the previous proposal's "all children provisional until
root success" rule or repair existing lifetime defects as part of this move.

Delete `_pass_owned_event_handler_order` where it only reconstructs decorated
values, and delete generic handler field completion. Keep recursive domain
deactivation and retirement calls with their existing timing. A retained event
dispatch's inactive transition must match the compatibility reference, not a
new graph-wide rollback guarantee.

### I6: Overrides, Registries, And Publication Notifications

Conditional prerequisite: the L0 contract must be verified before integrated
hooks depend on its stronger guarantees. Pending D4 approval, preserve existing
domain completion calls rather than claiming new draining guarantees.

1. Migrate override values and lookup selection to authoritative decorated state.
2. Keep fixed-key validation and drip/subscription semantics in domain code;
   replace rollback restoration with lifecycle state and approved domain hooks.
3. Audit slot registries, mount-advertisement maps, generation tracking, queued
   invalidations, and post-commit queues for failure-visible side effects.
4. Coordinate existing graph/UI validation, each owning boundary's publication,
   scratch cleanup, generation publication, and notification delivery explicitly.
   Do not replace the existing sequence with one outer atomic commit.
5. Delete class-name dispatch in base end/rollback passes after every participant
   category has migrated. Keep only rendering and domain-finalization work.

Verification: override/graph/mount failure observations and subscription links
match the compatibility reference, including any earlier child publication;
successful UI/generation and supported subsequent-render recovery remain intact.
Notification failures do not trigger fictitious post-publication undo. Record
pre-existing defects separately instead of imposing a new "publishes nothing"
guarantee on every failure.

Use I6a for override values/lookup/subscription boundaries, and I6b for root and
directive registries, generation, completion batches, and final dispatcher
deletion. Primary files are `app_context_override_slot_context.py`,
`directive_slot_context.py`, `render_context.py`, and `context_base.py`.

Before I6b code, record the existing completion timeline: graph/mount validation,
lifecycle publication at each accepted boundary, generation visibility,
resource retirement, scratch cleanup, and observer delivery. Settle D5 changes
separately and explicitly; I6 must not redefine I2's compatible ownership while
fixing notifications. If generation acceptance has an existing failure gap,
record it as debt; a new gap caused by migration must be resolved. D5 must not
silently reintroduce the deferred single outer publication guarantee.

Capture delivery/retirement batches before transient sources are cleared.
If the D4 proposal is approved, explicitly drain independent actions after a failed
entry with action/resource context in collected errors. Capturing or iterating
a batch is not proof that later actions survive an earlier exception; this
domain delivery guarantee belongs to I4/I6, not automatically to the TM.
Preserve independently arriving invalidations rather than
discarding every queued event after a failed candidate. Observers must see a
coherent accepted graph and generation. Reentrant writes during completion
need an explicit domain gate or deferred boundary; the manager being active
inside an after-hook is not authorization to stage more publication work.

I6b's deletion report must show no migrated-category class-name completion
dispatch, override snapshots/pending-to-current transfers, or directive
selector restore loop. Domain graph projection and callback delivery remain,
with approved L0 behavior ensuring a failing generated after-hook cannot skip later independent
hooks or participants. I4/I6 separately ensure a failing domain-batch action
cannot skip later independent actions inside that batch.

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

Address I0's concrete decomposed-path blockers at their owning checkpoints:
local scope access in I1/I2, event-handler UI projection in I3b, and generation
relocation/mount routing in I6b. The monolithic visitor/export mismatch is
covered by I7's actual routing and public-interface verification, not by
patching a second engine indefinitely.

The two baseline host/reconciliation ordering failures need separate triage
before final full-suite acceptance. Do not silently expand this integration
into an unrelated host rewrite, weaken their assertions, or call the full
suite green while they remain failing. Record an approved separate correction
or a scope decision explicitly if they block release.

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

## U1/U2: Later Manager Unification

These are not holder-integration slices or implicit authorization to change the
transaction library. Finish and verify authoritative holder replacement first,
then create a separate bounded design/review package.

- **U1: Completion isolation.** Specify how one manager preserves existing
  independently accepted parent/child/call-site boundaries. The committed
  shared-completion probe demonstrates that depth, separate object instances,
  and a common key do not provide isolation. Discuss any library API change;
  never use private generated callbacks or Pyrolyze field snapshots to emulate it.
  Outer atomicity is a separate deferred D1 choice, not the presumed solution.
- **U2: Wiring and permissions.** Once U1's mechanism is approved and tested,
  inject one root manager into nested renders, slots, and call-site participants;
  remove retained boundary allocations. Verify independent roots, local scope
  activity, write permissions, repeated passes, early child publication, caught
  failure, and resource cleanup without completing unrelated work.

The retained manager/cohort inventory is U1's input. Holder acceptance must
report this debt explicitly, not claim the original one-TM objective complete.

## Deferred Post-Integration Work

Start this work only after authoritative lifecycle storage has replaced the
legacy holders/field engine and the integration acceptance evidence is recorded.
It requires separate plans, semantic approval, and tests; it is not included in
I0-I8 or automatically authorized by an integration roll-build.

1. **D1: Stronger publication guarantee.** Consider one outer publication
   boundary, with successful children provisional until outer success and one
   publication key distinct from scratch. Specify the intentional change from
   today's early child publication, key/lifetime consequences, and new failure
   expectations. Do not claim multi-key atomicity from one shared TM.
2. **D2: Stronger failure containment.** Inventory concrete throw sites by phase,
   child/shared/ancestor writes, registration, subscriptions, cleanup, and
   candidate validity. Decide recovery versus abort per situation rather than
   exception type or whether it was caught. If partially staged child recovery
   needs a savepoint, its restoration point is the working state at child entry,
   including earlier valid changes, not simply `.current`. Specify any generic
   facility in `yidl-lifecycle`; do not recreate Pyrolyze snapshots. Include
   cancellation, containment failures, and retained-child/fallback validity.
3. **D3: Resource-lifetime hardening.** Evaluate unified ownership/refcount policy,
   comprehensive cycle auditing, deterministic retirement, and cleanup failure
   behavior per resource category. Keep holder replacement, referent transaction
   participation, and external acceptance/retirement distinct. Only adopt an
   expanded `owned`/adapter contract when a concrete consumer requires it.

Track existing defects with their baseline evidence and owning follow-up.
Deferral is not certification that the current behavior is correct in every
case. A regression introduced while replacing holders remains an integration
blocker at the affected checkpoint; a known pre-existing defect is not silently
turned into a migration exit requirement.

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

The canonical integration scenario should cover the cases below. D4/L0 draining
assertions (7-10 and 14) become target contracts only after that separate decision
is approved; they do not imply broader D2/D3 hardening or change earlier child
publication. Preserve the existing characterization evidence alongside any
explicitly approved D4 difference.

1. Root, two sibling slots, nested component render context, and call-site state
   retaining their current completion cohorts; no throwaway manager patching.
2. Successful render, unchanged rerender, child reorder/removal, and callback
   replacement while preserving stable object/dispatch identity where required.
3. Failure after an earlier child finishes: preserve the reference's published
   UI, callback, membership, and invocation observations. In particular, do not
   change an accepted earlier child back to its old values on parent failure.
4. Replacing/removing a resource followed by failure: acceptance, retirement,
   and cleanup cardinality/timing match the existing resource behavior. Detect
   migration-created early disposal, leaks, or double release, not a new
   root-wide provisional-resource guarantee.
5. Existing transaction-space write permissions and a sibling whose local scope
   is not active despite graph-wide key activity; no completion of unrelated
   enlisted work as a side effect of sharing a TM.
6. External-store/effect/async-effect/mount behavior and override subscription
   changes through success, failure, and later recovery.
7. Notification/hook failure after publication: committed results remain
   committed, cleanup runs, and the error preserves useful context.
8. A three-participant prepare failure at one applicable transaction boundary:
   no participant of that transaction applies before its required preparation
   succeeds. This proves that boundary's library protocol, not graph-wide
   atomicity or undo of children already published at earlier boundaries.
9. Three enlisted participants where the first after-commit hook raises: later
   mandatory retirement/notification hooks are still attempted, committed state
   stays published, and error reporting preserves the failure context.
10. Early rollback-callback and after-rollback failures with later participants'
    cleanup observable, local scopes exited, owned keys finalized, and a
    subsequent transaction/render able to recover. These complement L0's
    lifecycle-owned mechanics tests rather than duplicate their assertions.
11. Existing handled application failure, retained-child/fallback behavior, and
    caught-child recovery, including the I0 child that stages UI before raising.
    Preserve those outcomes rather than adding a new automatic abort policy.
12. Holder-replacement compatibility with earlier accepted children and still-unpublished
    parent/sibling changes: completing or failing one existing boundary must not
    newly publish/discard another boundary's work. Keep separate cohorts and exercise the existing
    supported recovery sequence without claiming new savepoint semantics.
13. Existing child cleanup and cancellation paths: preserve propagation and
    observable cleanup, with separately approved D4 differences explicit. Record
    baseline defects rather than requiring a new candidate-validity or
    comprehensive containment classification here.
14. Two independent actions in one domain delivery/retirement batch: the first
    throws and the second observably unsubscribes or cleans up a resource.
    Cover accepted completion and failed-candidate cleanup; assert exactly-once
    attempts, preserved publication/rollback outcomes, useful error context,
    finalized keys/local scopes, and subsequent-render recovery. Complement
    L0's generated same-participant/inherited-hook proof rather than duplicate
    its generic hook assertions.

Nested/caught failure and cancellation tests characterize and preserve the
selected compatibility reference. Comprehensive effect/phase classification
and new savepoint-like recovery assertions belong to deferred D2 coverage.
Compare public observables, not internal generated class names, slot layouts,
or legacy record implementations. Never regenerate expected snapshots just to
hide an unapproved semantic change.

Runtime selection must happen before imports, preferably in isolated processes.
The default selector currently chooses the monolithic `lcm` path, while focused
state-manager tests import the decomposed path directly. Both facts must remain
visible in test reports until I7.

### Checkpoint Evidence

Keep one canonical source for each successful end-to-end contract. Extend the
existing context, call-site, effect, scheduler, override, and mount harnesses
where possible. Add source/golden output only where it demonstrates newly
generated library behavior; do not add Pyrolyze goldens merely to freeze generic
generated private names that the integration does not depend on.

For every checkpoint, record:

- The initial failing target and whether it expresses an approved contract or
  an existing implementation bug.
- Focused and applicable regression results, runtime selector, repository
  revisions, and any dirty dependencies that affected the run.
- The authoritative declarations and removed fields/methods/callers from the
  ledger; a scoped source-search result identifying any remaining legacy paths.
- Public success/failure/recovery observations from the canonical fixture, and
  any intentionally unresolved resource categories.

The I0 snapshots are observations used to pin the selected migration reference,
not proof that all existing behavior is correct. Preserve their historical
evidence; once a separate change is approved,
identify the new target expectation and rationale explicitly in fixture docs.
Do not keep the obsolete monolithic engine executable forever just to reproduce
an old snapshot after I7 removes it.

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

The I0 characterization target is:

```sh
PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  uv run --with pytest --with pytest-cov python -m pytest -q \
  tests/test_lcm_integration_characterization.py
```

Its fixture setup, isolated selectors, and explicit snapshot regeneration are
documented in `tests/data/lcm_integration/README.md`. It is a baseline probe,
not yet the final integration acceptance fixture. The source pytest plugin is
automatically discovered in the I0 environment; do not register it again with
an explicit `-p` argument.

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

Holder-first sequence after plan review: I0 evidence, I1a constructor injection,
I1b with I3a common declarations, I3b callbacks, I3c invocation values,
I4a-I4c resources, I5a-I5b membership, I6a-I6b overrides/registries, I7 routing,
I8 evidence. I2 audits accompany each affected checkpoint. L0 is conditional on
approval and dependent hook work, not a universal holder prerequisite. U1/U2
are separate post-holder work. The subcheckpoints above are separately reviewable
commit/tag candidates, not permission to tag an umbrella slice complete while
its last checkpoint is unfinished. Use the agreed tag prefix and explicit
checkpoint suffix; do not invent a prefix in this document. A prerequisite
failure or material semantic question stops the affected sequence.

The expected implementation requires no new YIDL grammar. A missing generic
facility must be discussed and specified in its owning project before a slice
can depend on it. Do not restore `pyrolyze.lifecycle` as an integration shortcut.

## Acceptance Checklist

- [ ] Existing boundary manager/key cohorts and completion timing are preserved;
  every retained manager has a documented owner and future unification task.
- [ ] Boundary keys have tested lifetimes, write permissions, and completion
  ownership; no new sharing publishes/discards unrelated work.
- [ ] Local context scope activity is distinct from shared TM activity.
- [ ] Explicit constructor injection replaces private-slot patching without
  changing nested-render/call-site completion cohorts.
- [ ] Decorated state is authoritative; no `_lcm_sync` or duplicate field engine.
- [ ] Constructor declarations cover shared/derived slot state without chaining
  old initializer storage or allocating a second state wrapper.
- [ ] Stable event dispatch reads the published callback; manual callback
  transfer/reset methods and their callers are gone.
- [ ] Field rollback occurs through lifecycle, not manual value restoration.
- [ ] Resource acceptance/retirement and external side effects preserve approved
  success/failure ordering without a generic child-type dispatch loop.
- [ ] No migrated-path legacy record access; temporary independent managers are
  explicit completion owners, not a duplicate value engine.
- [ ] Graph construction does not patch lifecycle managers or attach through
  hidden default-factory side effects.
- [ ] Canonical fixtures preserve early child publication, parent failure, and
  caught-child recovery observations at the selected compatibility boundaries.
- [ ] No migration-created failure/recovery/resource regression is deferred;
  pre-existing defects and stronger D1-D3 guarantees are separate follow-up work.
- [ ] L0's lifecycle-owned multi-participant failure contract is verified before
  dependent I4/I6 hooks rely on new resilient cleanup/delivery; failing callbacks do not silently
  skip later participants' mandatory work.
- [ ] Where the approved stronger hook contract is activated, L0 covers independently declared same-key/inherited hooks inside one
  participant; I4/I6 separately drain independent domain-batch actions. An
  incomplete throwing action is reported, not mistaken for successful cleanup.
- [ ] Runtime selection, public exports, broader regressions, and the full suite
  pass with approved differences explicitly recorded.
- [ ] Performance results and remaining limitations are documented separately
  from claims of semantic completion.

## Decisions Required Before Execution

The user has settled the D1-D3 scope and holder-first sequencing: preserve
current behavior and existing completion cohorts, then address manager
unification separately. D4/D5 remain **pending**; earlier plan-level
review acceptance did not approve their proposed semantic changes.

| Decision | Evidence / Recommendation | Blocks |
| --- | --- | --- |
| D1: Publication compatibility; stronger guarantee deferred | Scope settled: retain accepted publication points and existing cohorts, including early child publication surviving later parent failure. Do not force universal default-key publication/pass-key scratch or hold every child provisional. Shared-TM isolation is U1/U2 work. | Holder regressions gate affected checkpoints; neither U1/U2 nor outer atomicity is a holder prerequisite |
| D2: Minimum failure compatibility | Scope settled: retain affected sites' existing handling, caught recovery, propagation, cleanup, and subsequent-render behavior. Characterize migration regressions; record existing defects. Comprehensive classification, savepoints, and stronger recovery/abort policy are deferred. | A migration-created incompatibility blocks its affected checkpoint; the deferred hardening inventory is not an I0 exit gate |
| D3: Minimum resource compatibility | Scope settled: map affected holders/referents and existing domain acceptance/cleanup calls; replace field storage without changing lifetime policy or retirement timing. Keep resource-specific methods where needed. Unified ownership/refcount policy, broad cycle repair, and stronger deterministic retirement are deferred. | Compatible holder replacement and existing resource behavior gate affected I4/I5 work, not a broader lifetime redesign |
| D4: Library failure completion | Approve L0's prepare cleanup, unexpected-apply draining, after-hook/rollback draining between participants and between independently declared same-key/inherited hooks, error grouping/context, and partial-apply hook eligibility. I4/I6 own per-action domain-batch draining separately. Recommend the existing Phase F-1 intent: attempt required remaining work and report failure, never fictitious undo of applied values. | L0 and only mechanisms relying on the new contract; preserve existing domain cleanup otherwise |
| D5: Observable completion ordering | Pending: pin generation visibility, resource retirement, scratch clearing, and observer delivery at the existing boundaries. Any proposed change needs explicit approval and must not implicitly reintroduce D1 outer atomicity or D3 lifetime redesign. Exceptions after publication cannot undo accepted values. | Affected hook/resource activation and final I6 timeline |

D1-D3 no longer require approval of stronger semantics before integration.
Their minimum compatibility evidence must name the selected reference, existing
completion points, holder/referent responsibilities, and removed state-transfer
mechanisms. A concrete conflict introduced by sharing or holder replacement
still needs discussion at the affected checkpoint. Do not certify full
containment/lifetime safety or silently fix existing bugs.

D4 must settle error delivery and partial-apply hook eligibility before tests
encode its changed outcomes. D5 must record the existing timeline, including
reentry and cleanup failure, and identify any separately approved change before
replacing its completion paths. Neither decision expands the deferred D1-D3
work automatically.

Also resolve any borrowed-transaction entry discovered in I1/I2: identify its
existing owner or discuss the compatibility policy. This is part of boundary
ownership, not a reason to finish keys that happen to be active.

Once these decisions are recorded, the slices can be assessed individually for
roll-build readiness. The existing passing focused tests are a starting point,
not evidence that these unresolved graph-wide cases already work.
