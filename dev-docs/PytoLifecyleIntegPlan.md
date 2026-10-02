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

Completion detail added on 2026-10-03 after the I0 investigation. The earlier
review-loop acceptance covered the preceding plan revision, not approval of
the outstanding semantic decisions or independent review of this revision.
The current completion-review status and exact reviewed tuples are recorded in
`dev-docs/PytoLifecyleIntegCompletionPlan-ReviewLoop.md`; a plan-level GO does not
authorize runtime execution or settle D1-D5.

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
`dev-docs/PytoLifecyleIntegI0Findings.md`, with the field/resource inventory in
`dev-docs/PytoLifecyleIntegI0Inventory.md`. The original runtime permits early
child publication and caught-child recovery; the proposed atomic outer-boundary
contract is therefore a decision, not an existing parity guarantee. I0's
approval gate remains open. No integration runtime changes have been made.

The current I0 evidence supersedes the historical focused-test result for
readiness assessment: 36 focused/characterization tests pass, but the full
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

### Completion Contract

For every migrated state category, the implementation must answer four
questions in the code and checkpoint report:

1. Which declaration is the sole authoritative value, and which facade is read
   while rendering versus while serving published behavior?
2. Which transaction key governs its writes, and which root boundary owns that
   key's completion?
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

Before publication, a failure that invalidates the owning boundary rolls back
its owned active keys. A contained child failure does not automatically
invalidate that boundary; apply the containment contract below. After
publication, a notification failure must not pretend that committed state can
be restored by another rollback. Drain-first failure handling and grouped error
reporting are the intended Phase F-1 contract, not a guarantee of the pinned TM.
The lifecycle prerequisite L0 below must reconcile and verify that contract
before the new coordinator or migrated hooks depend on it.

Nested boundaries and locally completed child passes must not finalize the
outer publication transaction. Catching a nested exception is neither proof of
safe recovery nor an automatic reason to abort. The current TM does not supply
arbitrary per-child savepoints. Do not introduce manual field snapshots to fake
containment that the lifecycle or domain candidate construction cannot provide.

Only finish transactions this coordinator owns. Joining an already active
transaction does not confer permission to commit it.

### Child Failure Containment

The earlier blanket recommendation to abort after every caught child failure
is superseded. Classify failures by phase, affected state/resources, and the
ability to leave a valid candidate, not by exception class alone. The concrete
throw-site policies still need I0 evidence and approval before implementation.

| Failure Situation | Required Containment / Proposed Boundary Treatment |
| --- | --- |
| Application error handled inside the child, with valid fallback output | Continue when the child's resulting candidate satisfies the domain contract; a handled error is not itself transaction failure |
| Child failure with no surviving candidate changes or provisional resources | Parent may recover if local bookkeeping is clean and retaining the previous child or producing fallback leaves a valid graph |
| Child failure after staging values, membership, UI, callbacks, or resource changes | Continue only if the complete failed attempt can be discarded while preserving earlier valid working changes; otherwise invalidate the owning boundary before publication |
| Structural or ownership failure | An isolated invalid child candidate may be discarded; uncertainty about the outer graph, transaction ownership, or shared state invalidates the boundary even if the exception is caught |
| Failure while containing/cleaning up a failed attempt | Do not certify local recovery; invalidate the boundary before publication and drain/report required cleanup under L0, retaining the original failure context |
| Validation/conversion rejection during commit preparation | Do not publish the candidate transaction; roll back owned work. This is not a late opportunity to ignore one child and continue applying the same candidate |
| Unexpected failure during commit application | Partial publication may already exist; drain/report according to L0 and identify incomplete application. Do not claim ordinary rollback restores the old graph |
| Notification or after-commit failure | Published values remain published; attempt required remaining completion and report failure rather than fictitious transaction undo |

Containment covers the entire child attempt, including framework work before
the child body: parent visitation, graph registration, candidate membership,
queued notifications, subscriptions, and provisional resource lifetime. A
failure before the child's first field assignment is not necessarily a
no-change failure.

For a partially staged attempt, the required recovery point is the **working
state at child entry**, not simply `.current`. An earlier successful child or
parent may already have staged valid changes. A child may also write shared or
ancestor state, so rolling back only that child's participant is insufficient
unless its write/ownership boundary has actually been proved isolated.

The existing I0 caught-failure fixture emits child UI before raising
`ValueError`. It establishes observed recovery, not safe containment under a
single shared TM. Conversely, a duplicate-key error in a fully isolated,
discardable child candidate need not poison an otherwise valid outer candidate.
Neither exception name alone determines the result.

Owning-boundary cancellation/interruption before publication should propagate
and end that boundary's owned work, not become fallback UI merely because a
broad catch exists. Task/resource-local cancellation needs its own containment
assessment; do not automatically equate it with cancellation of the whole
render. Post-publication interruption must still report the accepted state
accurately and attempt the required completion policy.

Inspect the throw sites before choosing a mechanism. Existing supported local
candidate construction may suffice for some cases. If a required recoverable
case needs a savepoint or another generic lifecycle facility, specify and
approve that facility in `yidl-lifecycle` before the dependent slice. A private
child TM or a restored Pyrolyze snapshot engine is not an approved workaround.

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
   one injected root TM, not a second decorated wrapper around a legacy object.
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
from .slot_context import SlotContextStateMgr


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
        callback_key = callback
        candidate = self
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

Preserve callback-key equality and dirty-forced selection semantics, but compare
the staging guard against the effective default/working candidate, not
`.current`. Several local passes may complete within one publication lifetime:
published A, then local selections B and A with `dirty=False`, must finish with
candidate A. Comparing only against published A on the second pass would skip
the assignment and incorrectly leave B staged. Dispatch still reads `.current`
throughout; candidate comparison does not expose staged callbacks to callers.

Identity comparison on the callback field avoids eliding a dirty-forced
replacement between distinct callable objects that compare equal. Keeping the
key initially makes that migration explicit; removing it is a separate
simplification only if the canonical fixture proves it has no independent role.

The dispatch closure's lifetime and references still require an ownership
audit. A stable callable is not inert if its closure retains a context. Do not
assume intrinsic reference counting alone provides timely retirement, or change
retained-handler behavior by introducing weak references without verification.

Deactivation is a domain operation: stage the inactive selection and membership
change before publication, then retire resources in the approved order. Do not
clear a published callback eagerly on a failed removal, write managed fields
from an after-commit hook, or retain `rollback_handler()` as a cleanup workaround.
The I5/I6 retirement checkpoints complete this part of the handler lifecycle.

### Context Pass Orchestration

`begin_pass()`, `end_pass()`, and `rollback_pass()` may remain as domain entry
points, but their responsibility must shrink as follows:

| Entry Point | Work That Remains | Work That Must Leave |
| --- | --- | --- |
| Local begin | Check/set this context's scope marker; reset this invocation's visitation and emission scratch | Allocate a private TM; snapshot current child order/dirty values; infer local activity from a global active key |
| Local successful end | Check structure; build candidate children/UI; stage membership and dirty results; exit local scope | Publish child fields; dispatch child commits by class; retire old children before root success |
| Local failed end | Exit local scope; report the failed attempt and its containment result so the owner can decide whether the candidate remains valid | Infer abort/recovery solely from exception type or whether it was caught; restore fields from saved copies; independently roll back a shared outer transaction |
| Root completion | Validate the candidate domain graph; finish owned keys through the TM; coordinate generation, retirement, and notifications | Walk every child to perform its generated field transfers; pretend published state can be undone after hook failure |

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

## Replacement And Deletion Ledger

Use `dev-docs/PytoLifecyleIntegI0Inventory.md` for the full field/resource
inventory. This ledger states the completion obligations rather than repeating
all field facts. State-manager filenames below are relative to
`src/pyrolyze/runtime/context_state_lcm/`; other paths are repository-relative.

| Existing Mechanism | Authoritative Replacement | Owning Checkpoint / Required Deletion |
| --- | --- | --- |
| `_transaction_manager_bootstrap_bad_program` and generated private-manager patch | Root TM injected before factory evaluation in every construction branch | I1: delete dummy declaration, factory, and private-slot assignment |
| Per-nested-render TM; per-slot TM defaults used as throwaway managers | Same root TM passed through construction factories | I1; I4 for legacy call sites: remove allocations, not just overwrite their results |
| `_attach_to_graph_bad_program` | Explicit provisional attachment after successful construction | I1: delete side-effect factory; failed attachment must leave no registered orphan |
| Graph-wide `is_scope_active()` and `_pass_started_tx` ownership inference | Context-local entry/reset/exit plus root boundary ownership | I1/I2: remove key-activity-as-local-scope test and child-owned publication completion |
| `_pass_child_order`, `_pass_child_dirty`; eager current-map edits | Managed candidate membership/UI and classified dirty fields | I3a: delete snapshots/restoration loops and current-collection mutation |
| `_committed_callback`, `_committed_key`, `_staged_callback`, `_staged_key`, `commit_handler()`, `rollback_handler()` | Managed callback/key; stable dispatch reads current selection | I3b: delete four stores, transfer/reset methods, and their dispatch callers |
| Eager `_last_args`, `_last_kwargs`, invocation identity/schema/site metadata | Managed invocation values or the existing frozen invocation record | I3c: delete eager publication and duplicated pending/current stores; keep dirty projection/evaluation logic |
| Legacy `current_record/working_record`, private call-site TM | Shared-TM collection with authoritative membership/visitation | I4a: delete direct record access and legacy ownership calls after both standalone/integrated expression paths migrate |
| Slot binding commit/rollback loops used for field transfer | Resource participant plus narrowly scoped external-effect hooks | I4b/I4c: delete generic loops; preserve only resource-specific delivery/cancellation/retirement |
| Component `_pass_owned_event_handler_order`, eager child disposal | Managed identity/child membership plus provisional/retired child handling | I5: delete reconstruction and eager disposal of the previous published child |
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
   Inventory concrete failure sites and their containment obligations: phase,
   writes to child/shared/ancestor state, resource/registration changes, cleanup,
   recovery owner, and the validity of retained-child/fallback output. Distinguish
   failure before changes, after staging, and during cleanup; do not assign one
   abort policy to every child exception.
6. Confirm the publication/pass split and outer-boundary ownership against those
   results. Discuss any actual semantic change before continuing.
7. Characterize multi-participant prepare/apply/hook/rollback failures against
   the Phase F-1 intended contract. Record the known pinned fail-fast limitation
   and approve the smallest lifecycle-owned L0 scope before dependent work.

Exit: a recorded baseline, approved boundary/key semantics, and a concrete
resource-category mapping. A needed savepoint or unresolved ownership contract
blocks the affected later slice; it is not permission to rebuild the legacy
engine inside an adapter.

Recorded work is baseline/inventory only, not an I0 pass tag: its approval exit
remains open. Resolve the decision register at the end of this document, retain
the observed original snapshots, and add approved target expectations rather
than silently rewriting the historical characterization.

The blanket abort recommendation in the historical I0 findings is superseded
by this document's child failure-containment contract. Keep the observations;
extend the evidence with per-failure recovery/abort decisions rather than treat
that earlier recommendation as approved policy.

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
library revision. The new I2 coordinator and the I4/I6 hook migrations cannot
complete without this evidence. Existing single-hook tests or manager-only
multi-participant tests are not sufficient; Pyrolyze's eventual integration
fixture must also prove per-action domain-batch draining, local-scope
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

Primary edits: `render_context.py`, `context_base.py`, `slot_context.py`, the
component/slot-expression state factories, and the runtime-only context factory
in `context_bare_refactor_lcm.py`. Trace callers rather than treating this as an
exhaustive file list. Construction of an independent root must allocate once;
nested construction and factories must pass the same object before defaults
run. Merely showing equal manager identity after construction is insufficient.

Minimum local-scope contract to settle against I0: entry to an inactive context
resets its own scratch; joining that already active local scope does not reset
or finalize it; a sibling with only a shared active key is not locally active;
all exit paths clear the owning local marker. If current callers require
recursive/reentrant local entry, specify that behavior before choosing a bool
versus depth implementation. A transaction-local field needs explicit local
reset even when the outer key remains active.

Keep I1 coherent with the approved boundary ownership. Introduce the minimum
ownership seam needed to prevent a newly shared child from completing its
parent's work at this checkpoint; I2 finishes the key split and all boundary
entry paths. Do not enable unsafe sharing with an I2 TODO beside a child commit.

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

The coordinator is a runtime object representing an owning boundary, not an
enum/magic mode tag. Pin the following in the implementation review:

| Boundary Event | Required Ownership Behavior |
| --- | --- |
| Independent root entry | Acquire the approved keys explicitly and record which transactions this boundary owns |
| Nested render/local entry | Join the existing coordinator; do not acquire completion rights from key activity alone |
| Local successful exit | Stage candidate domain results; leave the outer publication transaction open |
| Local failed exit | Report failure and containment before rethrowing; a proved contained attempt permits approved parent recovery, while an uncontained/uncertain attempt invalidates the owning boundary even if its exception is caught |
| Failure before publication | Roll back owned transactions and attempt required cleanup under L0; clear local markers in `finally` |
| Failure after publication | Drain/report remaining completion work; retain committed results; do not call rollback as an undo operation |

Audit direct `begin_pass`, scope-handle, scheduler flush, invalidation, and
deactivation entry points. A borrowed active transaction with no identifiable
coordinator is an unresolved ownership case, not automatic permission to finish
it. Settle its compatibility behavior before changing those callers.

The I0 parent-failure/caught-failure snapshots must first demonstrate the old
behavior; approved target fixtures must then demonstrate the chosen new
behavior. A successful nested render alone cannot prove ownership correctness.

The coordinator must distinguish an encountered exception from an invalid
candidate. A bare "some child raised" flag cannot encode that contract. Record
the effectful failure/containment outcome through the appropriate runtime
boundary behavior, not an exception-name whitelist or new passive mode tags.
Local recovery must not clear an independently recorded boundary-invalidating
failure from another attempt. Continuing rendering may be useful for error
reporting, but cannot turn an invalid candidate into an accepted transaction.

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
Current values remain old until root publication; rollback restores them by
discarding working state, not by an application copy loop.

Use three bounded commit/tag checkpoints under I3:

| Checkpoint | Edits And Deletions | Canonical Proof |
| --- | --- | --- |
| I3a: Common slot/value declarations | `_base.py`, `slot_context.py`, `context_base.py`, and affected derived declarations/factories: identity inputs, published dirty/site metadata, local visitation, candidate map/UI assignments; remove initializer-only storage and order/dirty snapshots | Root/sibling/nested construction, unchanged-call elision, repeated local reset, and failed candidate membership/UI with previous current values intact |
| I3b: Callback selection | `event_handler_slot_context.py` and its base dispatch callers: implement the expected shape; delete manual callback stores, `commit_handler`, `rollback_handler`; fix polymorphic UI assembly | Retained dispatch before/during/after success/failure; published A, then two local selections B and A with dirty=False in one outer transaction finish at A; dirty-forced distinct/equal callable case; staged callbacks remain invisible to dispatch |
| I3c: Invocation values | `leaf_slot_context.py`, `rerunnable_slot_context.py`, `slot_call_slot_context.py`, and related container/loop value declarations: managed input/identity/schema/site metadata; remove eager accepted-value assignment and duplicate snapshots | Unchanged elision, changed input, early child success followed by parent failure, recovery with the previous accepted invocation still authoritative |

Each checkpoint keeps the domain call/evaluation algorithms. I3c does not
pretend a managed `_binding` reference makes the referent transactional; that
resource migration belongs to I4. Audit mutable objects inside argument tuples
and frozen invocation records separately from the immutability of their holder.

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

Use the following resource checkpoints, each deleting its obsolete callers:

| Checkpoint | Scope | Replacement And Removal |
| --- | --- | --- |
| I4a: Call-site collection | `src/pyrolyze/runtime/call_site_context.py`, `src/pyrolyze/runtime/slot_expr.py`, `slot_expr_slot_context.py` | Inject shared TM; express collection/visitation through facades; remove private TM, direct record access, and hidden default allocation in both standalone and integrated expression paths |
| I4b: Value/subscription participants | Slot-call state and the owning slot-value/external-store binding modules | Separate holder replacement from referent state and subscription lifetime; remove manual field commit/restore; retire a replacement subscription only at the approved boundary |
| I4c: Effect/async/mount participants | Owning effect, async-effect, mount-advertisement modules and slot/expression dispatch callers | Stage request/dependency/advertisement state; keep resource-specific delivery/cancellation; remove generic participant loops once hooks cover that category |

Standalone slot-expression use may still own an independent manager. Injected
integration use may not. Test both through existing canonical fixtures rather
than deleting the standalone branch to simplify sharing.

For each resource, record who accepts it, who retires it, what happens to a new
candidate on failure, and whether callbacks can retain a cycle. Observable
cleanup cannot be delegated solely to `BindingBase.__del__`. If that requires
an unsupported library lifetime contract, stop and discuss it instead of adding
a second field engine or an unplanned generic `close()` protocol.

Resource-local delivery/retirement batches must also attempt later independent
actions after an earlier action raises, collecting failures with action/resource
context. I4 owns this domain-batch behavior; manager-level or generated-hook
draining cannot resume the remainder of one throwing domain function. Do not
turn the batch into a loop that publishes decorated fields or traverses all
graph participants. Respect dependent-action ordering and report an incomplete
throwing action rather than claim it was repaired or automatically retried.

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

Keep two bounded checkpoints: I5a makes component identity/schema, child
selection, and handler membership authoritative; I5b completes accepted-removal
and failed-candidate retirement. Primary scope is
`component_call_slot_context.py`, slot graph attachment/deactivation, and the
root registration callers. I5 is incomplete until both checkpoints pass.

Replacement algorithm to pin in the canonical scenario: construct/attach a
provisional child on the shared TM; stage its candidate selection; preserve the
old current child through validation; on failure retire only the provisional
child; on success retire the displaced current child exactly once. Repeated
reuse must preserve identity and must not enqueue duplicate retirement.

Delete `_pass_owned_event_handler_order` and reconstruction, eager disposal on
candidate identity change, and generic handler field completion. Keep recursive
domain deactivation only where it performs actual graph/resource teardown, not
child field publication. A retained event dispatch becomes inactive only under
the approved accepted-removal semantics, not on a rolled-back removal.

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

Use I6a for override values/lookup/subscription boundaries, and I6b for root and
directive registries, generation, completion batches, and final dispatcher
deletion. Primary files are `app_context_override_slot_context.py`,
`directive_slot_context.py`, `render_context.py`, and `context_base.py`.

Before I6b code, approve a concrete completion timeline: candidate graph/mount
validation, lifecycle publication, generation visibility, resource retirement,
pass-scratch cleanup, and observer delivery. I2 establishes boundary ownership;
I6 must not redefine it incidentally while fixing notifications. If the
existing generation service can fail during acceptance, validate/prepare its
candidate before irrevocable field publication or stop to resolve the gap.

Capture immutable delivery/retirement batches before their transient sources
are cleared, and explicitly drain their independent actions after a failed
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
with L0 ensuring a failing generated after-hook cannot skip later independent
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
11. Handled application failure with valid fallback, and an escaping child
    failure that demonstrably leaves no candidate/resource changes: approved
    recovery can publish the outer candidate without treating every exception
    as transaction abort.
12. Failure after child staging, with earlier valid working changes already
    present. Verify contained recovery preserves those earlier changes, or that
    the approved uncontained case prevents outer publication even when caught.
    Include child writes to shared/ancestor state and provisional resources;
    discarding only the child's own fields is not sufficient proof.
13. Cleanup failure during attempted child recovery: original and cleanup errors
    remain observable, later required cleanup is attempted, and an uncertain
    candidate cannot publish. Contrast an isolated discarded structural failure
    with a graph-wide invariant failure that invalidates the boundary.
14. Two independent actions in one domain delivery/retirement batch: the first
    throws and the second observably unsubscribes or cleans up a resource.
    Cover accepted completion and failed-candidate cleanup; assert exactly-once
    attempts, preserved publication/rollback outcomes, useful error context,
    finalized keys/local scopes, and subsequent-render recovery. Complement
    L0's generated same-participant/inherited-hook proof rather than duplicate
    its generic hook assertions.

Use the same exception type before and after staging to prove the policy is
effect/phase-based, not a type whitelist. Specify which retained-child/fallback
outcome is valid for each recoverable site; merely swallowing an exception is
not the expected result. Characterize cancellation at its owning boundary too.
Characterize nested/caught failure before asserting savepoint-like behavior.
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

The I0 snapshots are observations, not immutable expectations for the eventual
new target. Preserve their historical evidence; once a change is approved,
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

Checkpoint sequence after approval: I0, L0, I1, I2, I3a-I3c, I4a-I4c,
I5a-I5b, I6a-I6b, I7, I8. The subcheckpoints above are separately reviewable
commit/tag candidates, not permission to tag an umbrella slice complete while
its last checkpoint is unfinished. Use the agreed tag prefix and explicit
checkpoint suffix; do not invent a prefix in this document. A prerequisite
failure or material semantic question stops the affected sequence.

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
- [ ] Constructor declarations cover shared/derived slot state without chaining
  old initializer storage or allocating a second state wrapper.
- [ ] Stable event dispatch reads the published callback; manual callback
  transfer/reset methods and their callers are gone.
- [ ] Field rollback occurs through lifecycle, not manual value restoration.
- [ ] Resource acceptance/retirement and external side effects preserve approved
  success/failure ordering without a generic child-type dispatch loop.
- [ ] No migrated-path private call-site/per-slot TM or legacy record access.
- [ ] Graph construction does not patch lifecycle managers or attach through
  hidden default-factory side effects.
- [ ] Canonical fixtures prove whole-boundary failure and recovery, not only
  isolated per-slot commits.
- [ ] Child failures are classified by candidate validity and containment:
  recoverable attempts preserve earlier valid working changes, and uncontained
  or uncertain failures prevent publication even when caught.
- [ ] L0's lifecycle-owned multi-participant failure contract is verified before
  I2/I4/I6 rely on resilient cleanup/delivery; failing callbacks do not silently
  skip later participants' mandatory work.
- [ ] L0 covers independently declared same-key/inherited hooks inside one
  participant; I4/I6 separately drain independent domain-batch actions. An
  incomplete throwing action is reported, not mistaken for successful cleanup.
- [ ] Runtime selection, public exports, broader regressions, and the full suite
  pass with approved differences explicitly recorded.
- [ ] Performance results and remaining limitations are documented separately
  from claims of semantic completion.

## Decisions Required Before Execution

All entries below are **pending**. Recommendations are best guesses for the
completion plan, not decisions inferred from the request to write it.

| Decision | Evidence / Recommendation | Blocks |
| --- | --- | --- |
| D1: Publication and key split | I0 original/monolithic permit early child publication. Recommend one outer publication boundary on `DEFAULT_TRANSACTION`, with `PASS_TX_KEY` for scratch only; an earlier child stays provisional until outer success. This intentionally changes that reference behavior. | I0 exit, live sharing ownership in I1, I2 and later acceptance expectations |
| D2: Child failure containment | I0 permits caught-child recovery, but its fixture stages UI before raising. Classify concrete sites by phase/effects and prove which leave a valid candidate: contained failures may recover; uncontained or uncertain failures invalidate the owning boundary even if caught. Specify any required savepoint/equivalent in the library first, without a snapshot workaround. | I0 exit, I1/I2 nested failure/containment behavior, and affected resource checkpoints |
| D3: Resource contract | Approve the category mapping in the I0 inventory: holder replacement, referent participation, acceptance, deterministic retirement, and one refcount/lifetime policy per resource. A nontransactional `binding()` declaration does not settle these questions. | Affected I4/I5 checkpoints and their constructor/attachment seams |
| D4: Library failure completion | Approve L0's prepare cleanup, unexpected-apply draining, after-hook/rollback draining between participants and between independently declared same-key/inherited hooks, error grouping/context, and partial-apply hook eligibility. I4/I6 own per-action domain-batch draining separately. Recommend the existing Phase F-1 intent: attempt required remaining work and report failure, never fictitious undo of applied values. | L0; I2/I4/I6 completion mechanisms |
| D5: Observable completion ordering | Agree generation visibility, accepted-child/resource retirement, scratch clearing, and observer delivery. Recommend preparing domain candidates before field publication and delivering notifications only after accepted graph/generation are coherent. Exceptions after publication cannot undo accepted values. | Hook/resource activation in I4/I5 and final I6 timeline |

D1/D2 approval must name the behavioral differences from the baseline. D2 must
give per-failure containment/recovery evidence, valid fallback/retained-child
outcomes, and the treatment of uncertainty and cleanup failure; it must not
collapse into "any child exception aborts" or "caught means safe". D3 must record
concrete resource responsibilities, not simply approve the word "owned". D4 must
settle error delivery and partial-apply hook eligibility before tests encode
them. D5 must give an ordered timeline, including reentry and cleanup failure,
before the old completion paths are removed.

Also resolve any borrowed-transaction entry discovered in I1/I2: identify its
existing owner or discuss the compatibility policy. This is part of boundary
ownership, not a reason to finish keys that happen to be active.

Once these decisions are recorded, the slices can be assessed individually for
roll-build readiness. The existing passing focused tests are a starting point,
not evidence that these unresolved graph-wide cases already work.
