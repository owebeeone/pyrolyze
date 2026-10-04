# Lifecycle Feature Update For State Manager Refactor

## Status

Proposed.

## Purpose

This document defines the lifecycle features that must be added or clarified in
`pyrolyze.lifecycle` so that the runtime `*StateMgr` classes can be refactored
onto a declarative lifecycle API.

The goal is not to preserve the current handwritten runtime structure. The goal
is to preserve the public `runtime.context` behavior while moving authoritative
state management into `lifecycle.py`.

This document is narrower than `ContextLifecyleMetaprogramming.md`.

That document describes the lifecycle direction in general. This document
describes the concrete feature set required for the current `context_bare_refactor`
and `runtime/context_state/*` decomposition to become a real lifecycle-backed
implementation.

## Terminology

Avoid the vague word **ambient** here. What older drafts called an “ambient”
transaction is **auto-joining**: nested scopes share a single active
`LifecycleTransaction` by **counting** `TransactionManager.begin()` / `commit()` —
each `begin` increments a depth counter, each `commit` decrements; only the
**outermost** balancing `commit` runs validation and applies commits (and
`rollback` tears down the whole joined attempt). Inner scopes do not allocate a
second transaction object; they only participate in that join count.

## Problem statement

The current `*StateMgr` split is useful because it separates the public context
surface from the internal state machinery. However, the managers are still
mostly imperative state machines.

The current problems are:

- too much authoritative state is still expressed as ordinary mutable Python
  attributes
- many fields that should be lifecycle-managed are still effectively behaving
  like ad hoc mutable state
- `local_store` has been used as a migration escape hatch rather than a narrow
  cache/helper mechanism
- the current transaction model in `lifecycle.py` is too flat for the render
  graph
- `binding` and `owned` do not yet express the distinct semantics needed by the
  graph
- graph commit ordering is not a first-class lifecycle concept

The `*StateMgr` split gives us a stable boundary:

- public API lives in `runtime.context`
- internal behavior lives in `runtime/context_state/*`

Once that boundary exists, `lifecycle.py` must provide the state model needed to
replace the imperative state in the managers.

## Design goals

The lifecycle update must make it possible to:

1. Express slot-context state declaratively.
2. Keep the public `runtime.context` API stable while refactoring internals.
3. Represent render-attempt-local state without leaking it into authoritative
   committed state.
4. Join nested child renders into one transactional unit when they occur inside
   the same boundary call chain.
5. Preserve rollback safety for child render contexts, mount directives,
   bindings, and app-context overrides.
6. Keep `local_store` small and honest: helper/cache only, never authoritative.
7. Support graph-aware commit ordering: children before parents.
8. Distinguish shared retained resources from exclusively owned structural
   resources.

## Non-goals

This document does not require:

- immediate deletion of the handwritten `*StateMgr` logic
- full elimination of imperative helper methods
- full replacement of runtime-specific helper algorithms inside
  `runtime/context_state/*`
- forcing pure values into `freezable.py` before the lifecycle contract is
  correct

The first requirement is semantic correctness and a declarative state model.

## Core design

## Auto-joined transaction model

The current `TransactionManager` model is not sufficient for the render graph.

Today it is:

- explicit
- single-active
- flat
- context-enlistment oriented
- not graph-ordered

The render graph needs:

- one auto-joined transaction per outermost boundary render attempt
- nested child boundaries entered synchronously during that render attempt join
  the same transaction
- later scheduled sibling boundaries get separate transactions
- the outermost boundary is the only commit/rollback authority for that render
  attempt

This is the correct scope because:

- a child render inside a parent boundary must roll back if the parent fails
- a later unrelated boundary rerender must not be coupled to an earlier one

### Important clarification from the current runtime

The runtime already supports nested boundary execution today.

In `context_original.py`:

- `ComponentCallSlotContext.invoke()` can call `child_context._run_boundary()`
  synchronously during a parent render
- `RenderContext._run_boundary()` already distinguishes outermost vs nested
  boundaries using scheduler-active state
- only the outermost boundary performs transaction begin/commit/rollback on the
  current generation tracker

So the required lifecycle direction is not:

- explicit nested independent lifecycle transactions

and not even necessarily:

- explicit nested `begin()` calls that "join"

The simpler alignment is:

- outermost boundary begins lifecycle transaction
- nested boundaries run under the already-active transaction
- outermost boundary alone validates and commits or rolls back

In other words, auto-joining nested boundaries into one transaction is already
part of the runtime control flow.
What is missing is lifecycle support for the semantics of that joined render
attempt.

### Required auto-joined transaction behavior

When entering `RenderContext._run_boundary()`:

1. If there is no auto-joined lifecycle transaction on the current execution path:
   - create one
   - mark this boundary as the transaction root
2. If an auto-joined lifecycle transaction already exists:
   - do not create a nested independent transaction
   - nested work runs under the existing auto-joined transaction

When exiting `RenderContext._run_boundary()`:

1. If this boundary only ran under an already-active transaction:
   - do not commit
   - do not roll back independently
2. If this boundary is the root of the auto-joined transaction:
   - successful exit performs validation, then commit
   - escaping exception performs rollback

This means the lifecycle transaction scope is:

- dynamic boundary subtree for one render attempt

not:

- per field
- per slot
- whole tree for a whole scheduler flush

### Consequence for lifecycle implementation

`lifecycle.py` does not need to become the primary detector of nested boundary
entry.

The lower-risk design is:

- runtime keeps deciding outermost vs nested boundary
- runtime calls lifecycle begin only at the outermost boundary
- nested boundaries simply execute while the auto-joined lifecycle transaction is
  already active
- runtime calls lifecycle validate+commit or lifecycle rollback only at the
  outermost boundary exit

This keeps lifecycle focused on state semantics instead of duplicating scheduler
boundary tracking.

## State classes required by the graph

Every lifecycle-backed context state manager should be able to express four
distinct classes of state.

### 1. Published state

This is the authoritative visible state.

Properties:

- visible outside an active transaction
- survives successful commit
- used for `.current`
- should preferably be immutable snapshots for pure value aggregates

Examples:

- committed UI snapshots
- committed selectors
- committed native root
- committed app-context override values
- retained current binding / child context ownership

### 2. Working state

This is a sparse overlay for the current auto-joined transaction.

Properties:

- created lazily on first authoritative write
- visible to unqualified/default access during the active transaction
- discarded on rollback
- merged into published state on commit

Examples:

- next committed selector set
- replacement binding
- replacement child context
- next committed app-context override values

### 3. Transient state

This is pass-local state for the active auto-joined transaction only.

Properties:

- writable only while the auto-joined transaction is active
- visible only during that transaction
- cleared on both commit and rollback
- never authoritative after the transaction ends

This is what the earlier discussion called "pass scratch". No new field kind is
required. `transient` is the correct lifecycle concept.

Examples:

- `_pass_child_order`
- `_pass_child_dirty`
- `_staged_ui`
- `_staged_ui_entries`
- `_pending_values`
- `_pending_lookup`
- `_pending_initialized`
- `pending_dirty_state`
- `expects_native_root`

### 4. Local cache

This is shared mutable helper state that does not participate in transactional
publication.

Properties:

- not committed or rolled back
- survives failed speculative work
- cleared only by close or explicit reset
- never authoritative

This is what `local_store` is for.

Examples:

- runtime locals
- dispatch closures
- call-site manager internals
- inert memo caches

## Lifecycle field kinds and their required semantics

## `managed`

`managed` must represent published plus working-overlay value state.

Required behavior:

- published value in committed storage
- working overlay per auto-joined transaction
- unqualified/default reads see working if present, otherwise published
- `.current` reads always see published
- commit installs working into published
- rollback discards working

This is the default authoritative value kind.

## `transient`

`transient` must mean transaction-local pass state.

Required behavior:

- no durable authoritative meaning after transaction end
- written only during auto-joined transaction
- cleared on both commit and rollback
- not used as a fallback source of truth for published state

Important clarification:

For the `*StateMgr` refactor, the existing `transient` model is good enough if
the field default is chosen to preserve the distinctions the runtime actually
needs.

Recommended rule:

- use `default=None` when `None` can mean "not evaluated this pass"
- otherwise use an explicit sentinel such as `UNSET` / `NOT_SET`

This gives the required state detectability:

- not evaluated this pass
- evaluated this pass and produced an empty value
- evaluated this pass and produced a non-empty value

So `transient` does not need a new field kind or a separate "scratch" concept.
The implementation may retain a baseline default internally as long as the
observable semantics remain:

- transaction-local writes
- reset to the sentinel/default after commit and rollback
- no authoritative publication

## `local_store`

`local_store` must be treated narrowly.

Required behavior:

- never authoritative
- never a substitute for missing `managed` or `transient` semantics
- never used for retained structural ownership
- never used for committed snapshots

If a field affects published UI, retained resources, or visible context
semantics, it must not be `local_store`.

## `binding`

`binding` represents a shared retained resource.

Required behavior:

- identity-based replacement
- staged replacement during auto-joined transaction
- accept new binding only at commit
- release old binding only at commit
- release staged new binding on rollback
- shared ownership via intrusive refcounting

The common base remains:

- `BindingBase`
- `inc_ref()`
- `dec_ref()`
- `accepted()`
- protected `_close()`

Final close behavior derives from the accepted bit rather than a passed
parameter.

## `owned`

`owned` is not just another name for `binding`.

`owned` represents exclusive structural ownership.

Required behavior:

- exclusive ownership semantics
- staged replacement during auto-joined transaction
- newly created owned values must be torn down on rollback
- old owned values must not be torn down until replacement commits
- commit publishes the new owner/value atomically
- rollback restores old owner/value atomically

Current assessment:

For the current refactor pass, the existing `owned` behavior is good enough if
application logic treats the owned value as single-owner by convention.

That means:

- owned values are expected not to be shared across multiple owned locations
- rollback tears down a newly staged owned value
- commit tears down the replaced prior owned value
- child-before-parent commit ordering still matters for structural safety

So, for now, `owned` is partly documentation of intent rather than a fully
enforced exclusivity mechanism.

Possible later hardening:

- commit-time exclusivity checks such as `ref_count == 1`
- stronger owned-specific hooks distinct from shared binding hooks
- explicit diagnostics when an owned value is observed in multiple locations

Those checks are intentionally deferred. The immediate migration goal is to use
`owned` as the declared lifecycle kind and rely on application logic to uphold
single-owner discipline.

Typical examples:

- child render context
- structurally owned retained helper objects that are not shared bindings

`owned` needs stronger teardown semantics than `binding`.

## `static`

`static` remains late-initialized then fixed.

For the context graph, this is appropriate for fields such as:

- fixed declared key sets

It is not part of the auto-joined transaction model except for one-time
initialization rules.

## `const`

`const` remains constructor-only or inherited fixed identity.

Typical examples:

- `slot_id`
- `parent`
- `render_context`
- scheduler-root injected transaction manager

## Graph commit model

The graph does not only need transactions. It needs graph-aware commit order.

### Required ordering

Commit must happen in postorder:

- children before parents

Why:

- parent publication often depends on finalized child publication
- parent committed UI snapshots are derived from child committed UI
- owned child contexts must be finalized before parent structural publication

Rollback must unwind staged graph changes consistently:

- discard working overlays
- discard transient state
- roll back staged binding and owned resource changes
- keep `local_store`

### Required parent/child rules

1. Parent published UI must not be installed before child publication is
   finalized.
2. Deactivation of unseen children must be staged during the transaction, not
   finalized immediately.
3. Mount/directive structural publication must happen as one local committed
   result, not as several unrelated side effects.
4. Parent publication that depends on child UI must run after child commit.

## Validation phase

The graph also needs a pre-commit validation phase.

Simple value fields may not care, but structural contexts do.

Examples:

- mount directive `no_emit` validation
- fixed-key validation in app-context override
- structural ownership invariants
- selector normalization or structural shape checks

### Required lifecycle phases

At minimum, `lifecycle.py` should support these conceptual phases for an
auto-joined transaction:

1. stage writes
2. validate staged state
3. commit children before parents
4. publish derived committed snapshots
5. clear transients

Rollback is:

1. discard staged working state
2. tear down staged binding/owned values as appropriate
3. clear transients
4. preserve local caches

The exact API shape may differ, but those semantic phases are required.

> **Lifecycle implementation update:** Transaction support for **ordered commit** (`commit_order_key` + `LifecycleTransaction.commit_order()`) and for **pre-commit validation** (separate `validator_contexts` enlistment, all validators run before any apply, full `rollback` on failure, failures reported as an `ExceptionGroup`) is **corrected** in `pyrolyze.lifecycle`; nestable `begin()` with balancing outer `commit()` / `rollback()` is also in place. Wiring outermost render boundaries to call begin/validate/commit/rollback on that manager remains the integration work described above.

## Required lifecycle API additions

The following capabilities should be added to `lifecycle.py`.

## 1. Auto-joined transaction support aligned with outermost-boundary control

`TransactionManager` must be able to support:

- outermost transaction root
- already-active auto-joined transaction visibility during nested boundary work
- one final commit/rollback authority

This can be implemented by:

- extending `TransactionManager`
- adding a thin `JoinedTransactionManager` (or similar façade)
- or factoring auto-join logic around the existing manager

The exact class layout is less important than the semantics.

Required API properties:

- enter root transaction
- know whether a transaction is already active
- commit only from root
- rollback only from root

The preferred first implementation is:

- no explicit nested lifecycle `begin()`
- nested boundary execution simply observes an already-active transaction
- outermost boundary remains the only lifecycle transaction owner

## 2. Transaction membership by touched context

Contexts should continue to enlist lazily, but membership must now be attached
to the auto-joined transaction rather than to ad hoc local commit scopes.

Required behavior:

- context enlists on first authoritative staged write
- context stays enlisted for transaction lifetime
- transient-only activity may also need enlistment if validation/cleanup depends
  on it

## 3. Distinct `owned` semantics

The current implementation treats `binding` and `owned` similarly, but that is
acceptable for the first refactor pass as long as:

- application logic treats owned values as single-owner by convention
- rollback tears down newly staged owned values
- commit tears down replaced prior owned values
- postorder finalization is preserved

Stronger exclusivity enforcement is deferred. Future hardening may add owned-
specific checks or hooks, but this is not required to begin the declarative
manager migration.

## 5. Pre-commit validation hooks

Contexts need a way to validate staged state before commit.

Required hook shape, conceptually:

- `validate_commit()`
- or field/class hooks with equivalent semantics

This should run:

- after staging is complete
- before authoritative publication

Validation failure must:

- abort the auto-joined transaction
- trigger rollback

## 6. Graph commit ordering support

The lifecycle engine must support ordering constraints between enlisted
contexts.

At minimum it needs:

- parent/child ordering metadata
- or a manager-driven way to commit children before parents

The runtime graph already knows parent relationships. `lifecycle.py` should
provide a way to use that information during commit.

## 7. Working/current view policy aligned with auto-joined transactions

The view model should be:

- `context.field` is the default authoritative surface
- `context.current.field` is published only
- `context.working.field` is explicit working/default transaction surface

During an active auto-joined transaction:

- unqualified/default access should read working if present, else published
- `.current` must remain published

This part is mostly aligned already, but it must remain true when the auto-joined
transaction model is fully wired from outermost boundaries.

## State manager field classification rules

The following rules should drive the `*StateMgr` refactor.

## Fields that must not be `local_store`

Anything authoritative or structurally published must not use `local_store`.

Examples:

- `binding`
- `child_context`
- committed values/selectors
- committed native root
- committed UI snapshots
- any value that affects public context semantics after commit

## Fields that should be `transient`

Any per-attempt staging state should be `transient`.

Examples:

- `_pass_child_order`
- `_pass_child_dirty`
- `_pass_committed_*`
- `_staged_ui*`
- `_pending_*`
- `expects_native_root`
- pass-local dirty snapshots

## Fields that should be `managed`

Any authoritative visible committed state should be `managed`.

Examples:

- committed selectors
- committed override values
- committed native root
- retained slot-call argument snapshots if they affect reuse decisions
- retained component-call argument snapshots if they affect reuse decisions

## Fields that should be `owned`

Any exclusive structural child/resource should be `owned`.

Examples:

- child render context
- other exclusive structural child runtime objects

## Fields that should remain `local_store`

Only inert helpers and caches.

Examples:

- runtime locals
- dispatch closures
- call-site manager internals
- memoization caches safe to preserve after rollback

## Context-class migration implications

This section gives the expected declarative direction for the major state
manager families.

## `ContextBaseStateMgr`

Likely lifecycle split:

- `const`
  - `render_context`
- `local_store`
  - child registration maps
  - literal initialization helpers if they are purely local helper state
- `transient`
  - `_pass_child_order`
  - `_pass_child_dirty`
  - `_staged_ui`
  - `_staged_ui_entries`
  - pass-local committed UI rebuild inputs
- `managed`
  - `_own_committed_ui`
  - `_own_committed_ui_entries`
  - `_committed_ui`

Important note:

If child registration maps affect graph commit ordering or active child
membership semantics, they may need stronger semantics than plain
`local_store`. This should be evaluated during the concrete migration.

## `EventHandlerSlotContextStateMgr`

Likely lifecycle split:

- `const`
  - `slot_id`
  - `parent`
  - `render_context`
- `managed`
  - committed callback
  - committed key
- `transient`
  - seen-in-pass
  - pending/staged callback
  - pending dirty flag
- `local_store`
  - dispatch closure

## `SlotExprSlotContextStateMgr`

Likely lifecycle split:

- `local_store`
  - call-site context manager
  - runtime locals by slot id
- `transient`
  - staged call-site ids
  - staged post-commit callbacks
- `managed` or `binding`
  - whichever retained current output/binding identity actually needs to survive
    commit

## `SlotCallSlotContextStateMgr`

Likely lifecycle split:

- `managed`
  - function identity
  - schema
  - last args
  - last kwargs
- `binding`
  - retained slot binding
- `local_store`
  - runtime locals
- `transient`
  - invalidation staging
  - mount advertisement staging if not directly part of authoritative published
    state

## `DirectiveSlotContextStateMgr`

Likely lifecycle split:

- `managed`
  - committed selectors
- `transient`
  - pending selectors
  - pending emitted-child detection
- `managed` derived publication
  - committed `MountDirective` snapshot, if represented directly

This is one of the places where pre-commit validation is required.

## `ContainerSlotContextStateMgr`

Likely lifecycle split:

- `managed`
  - committed native root
- `transient`
  - expects native root

## `ComponentCallSlotContextStateMgr`

Likely lifecycle split:

- `managed`
  - component identity
  - schema
  - last runtime func
  - last bound receiver
  - last args/kwargs
  - last plain args/kwargs
  - last dirty state
  - packed kwarg metadata
- `owned`
  - child context
- `transient`
  - pending dirty state
  - pass-owned-event-handler order

This class is one of the main reasons `owned` semantics must differ from
`binding`.

## `AppContextOverrideSlotContextStateMgr`

Likely lifecycle split:

- `static`
  - declared keys
- `managed`
  - committed override values
  - committed authored lookup
- `transient`
  - pending values
  - pending lookup
  - pending initialized

This class needs validation before commit and is a strong driver for
pre-commit lifecycle hooks.

## Call-site context migration implications

`CallSiteContext` and its manager fit the same lifecycle model:

- published call-site visibility/current map
- working overlay for staged replacements
- transient visited-in-pass state
- local cache for helper maps if needed
- `binding` for retained call-site owned resources

This should converge on the same declarative lifecycle API rather than remain a
parallel bespoke state machine.

## Freezable integration

`freezable.py` should be used only where it helps represent published immutable
snapshots.

That means:

- pure value aggregates may use freeze/thaw helpers
- `managed` fields may opt into `freeze` / `thaw`
- bindings and owned resources should not be forced through freezable mechanics
- transient and local caches should not depend on freezable semantics

The lifecycle contract remains primary.

## Recommended implementation sequence

## Phase A: feature support in `lifecycle.py`

1. Introduce outermost-boundary-controlled auto-joined transaction semantics.
2. Add validation hooks.
3. Add graph commit ordering support.
4. Standardize sentinel/default conventions for pass-local `transient` fields.
5. Keep `owned` as a documented single-owner convention for now; defer
   exclusivity checks.

## Phase B: field classification pass over `runtime/context_state/*`

1. Inventory every manager field.
2. Mark each as:
   - `const`
   - `static`
   - `managed`
   - `binding`
   - `owned`
   - `transient`
   - `local_store`
3. Remove all uses of `local_store` that are carrying authoritative state.

## Phase C: declarative migration one manager at a time

Suggested order:

1. `EventHandlerSlotContextStateMgr`
2. `DirectiveSlotContextStateMgr`
3. `ContainerSlotContextStateMgr`
4. `SlotExprSlotContextStateMgr`
5. `SlotCallSlotContextStateMgr`
6. `AppContextOverrideSlotContextStateMgr`
7. `ComponentCallSlotContextStateMgr`
8. `ContextBaseStateMgr`
9. `RenderContextStateMgr`

The order can change, but the main idea is:

- migrate the classes that exercise one lifecycle concept cleanly
- leave the largest structural orchestrators until the field semantics are
  proven

## Acceptance criteria

This lifecycle feature update is complete when:

1. `*StateMgr` authoritative state can be declared using lifecycle field kinds
   instead of ad hoc Python attributes.
2. `local_store` is used only for caches/helpers.
3. Nested child renders no longer commit independently from the outer boundary
   render attempt.
4. `owned` is declared and used as a single-owner convention, with application
   logic upholding exclusivity for now.
5. mount/directive and app-context override validation can run before
   publication.
6. parent publication occurs only after child publication is finalized.
7. the public `runtime.context` API remains stable while internal state becomes
   lifecycle-backed.

## Short version

The missing lifecycle features are:

- auto-joined transactions rooted at outermost boundaries
- pre-commit validation
- graph-aware commit ordering
- strict discipline that `local_store` is never authoritative

Those features are what will let the `*StateMgr` classes stop being imperative
state machines and become declarative lifecycle-backed state definitions behind
the existing public context API.
