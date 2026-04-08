# Context Lifecycle Metaprogramming Plan

## Status

Proposed.

## Goal

Re-implement `runtime/context.py` using the lifecycle metaprogramming model
described in `dev-docs/ContextLifecyleMetaprogramming.md`.

The new implementation will live in:

- `pyrolyze/src/pyrolyze/runtime/context_lcm.py`

The target end state is:

- `context_lcm.py` is functionally equivalent to `context.py`
- `context_lcm.py` replaces `context.py` as the active runtime implementation
- `context.py` is preserved as `context_original.py`
- the runtime import surface can switch between the original and LCM versions
  during migration

`CallSiteContext` may be migrated in the same phase as `context.py` or in a
separate phase, whichever produces the least migration friction.

## Constraints

1. The migration must preserve existing runtime behavior.
2. Minor interface adjustments are acceptable only if they are small and do not
   break the existing test suite.
3. Every new lifecycle-library capability added to support `context.py` must
   also gain independent tests at the library level, not just parity tests
   through the runtime.
4. `context_lcm.py` must use `pyrolyze.lifecycle` as its exclusive lifecycle
   mechanism.
5. Declarative lifecycle definitions must remain central to implementation
   choices.
6. Application-specific logic must remain in the application class or classes,
   not in generic lifecycle helpers.
7. Implementation details from `runtime/context.py` must not leak into
   `pyrolyze.lifecycle`.

## Non-negotiable architecture rules

The following rules are strict.

### 1. `context_lcm.py` must build on `pyrolyze.lifecycle`

`context_lcm.py` is not allowed to reintroduce bespoke lifecycle plumbing that
duplicates the purpose of `pyrolyze.lifecycle`.

That means:

- no parallel hand-written current/working mechanism
- no alternative ad hoc commit/rollback framework
- no bespoke field-level lifecycle engine outside `pyrolyze.lifecycle`

If a lifecycle feature is needed by `context_lcm.py`, it must first be added to
`pyrolyze.lifecycle` and tested there independently.

### 2. Declarative lifecycle definitions remain central

The migration is only worthwhile if the runtime shapes are expressed
declaratively.

That means implementation decisions should favor:

- declarative field definitions
- declarative field policy
- declarative class hooks
- compile-time selection of field handlers from field parameters

and should avoid sliding back into large amounts of imperative lifecycle code in
`context_lcm.py`.

### 3. Application-specific logic stays in application classes

Generic library code should only express generic lifecycle mechanics.

Application-specific semantics must remain in the application class or classes,
for example:

- validation of fixed structure
- domain-specific invariants
- domain-specific normalization
- slot- or context-specific lifecycle hooks

This keeps the library generic and prevents the migration from hiding runtime
semantics inside generic helpers.

### 4. `pyrolyze.lifecycle` must remain domain-neutral

The lifecycle library must not encode `context.py`-specific concepts.

That means:

- no slot-specific terminology in generic lifecycle APIs
- no `kwargs`-specific or slot-tree-specific helper names baked into the
  library
- no generic helper behavior that depends on `SlotContext`,
  `RenderContext`, mount adverts, or other runtime-specific types

If `context_lcm.py` needs a capability, it should be added to
`pyrolyze.lifecycle` in generic lifecycle terms.

### 5. `pyrolyze.lifecycle` owns lifecycle semantics directly

The lifecycle library should not be architected as a thin wrapper around
`pyrolyze.freezable`.

That means:

- field semantics should live in lifecycle field policies/descriptors
- write control should be owned by lifecycle, not by dataclass frozenness
- the core implementation should not depend on generated frozen/thawed
  dataclass peers

`pyrolyze.freezable` may still be used as an optional utility for leaf-value
freezing, but it is not part of the core lifecycle contract.

### 6. Getter/setter handlers must stay minimal

Getter/setter logic should be selected when the class is decorated, not
rediscovered on every access.

That means:

- field specs should bind the concrete helpers to use for that field
- descriptor bodies should do as little work as possible
- new helper functions should be added only when a new semantic behavior
  actually appears
- helpers with identical behavior should be shared rather than duplicated for
  naming symmetry

## Strategy

The migration should proceed in parallel rather than as an in-place rewrite.

That means:

1. Keep the original runtime intact while the new implementation is built.
2. Develop `context_lcm.py` to feature parity under a switchable import.
3. Add narrow declarative lifecycle tests whenever the lifecycle library grows.
4. Add parity tests or run existing runtime tests against both implementations.
5. Only switch the default runtime once parity is established.

At every phase, `context_lcm.py` should solve lifecycle problems by extending
`pyrolyze.lifecycle`, not by bypassing it.

The existing `pyrolyze.lifecycle` module should be treated as a prototype.

The implementation should salvage semantics selectively, but it should not feel
obliged to preserve the current dataclass/freezable-centered internals.

The current best guess is that the lifecycle core should be restarted around:

- record overlays
- central field-policy dispatch
- mutable committed/working records

while preserving useful pieces such as:

- `TransactionManager`
- field-taxonomy semantics
- focused lifecycle tests where they still describe the right behavior

## Deliverables

### Runtime deliverables

- `pyrolyze/src/pyrolyze/runtime/context_lcm.py`
- `pyrolyze/src/pyrolyze/runtime/context_original.py`
- import switcher selecting the active runtime implementation

### Library deliverables

- expanded `pyrolyze.lifecycle`
- optional leaf-level `pyrolyze.freezable` usage only where justified
- focused lifecycle-library tests
- record-based lifecycle storage instead of whole-object current/working clones

### Test deliverables

- independent tests for declarative lifecycle features
- parity coverage for the migrated runtime contexts
- ability to run context-related tests against original and LCM implementations

## Import-switch design

The migration needs a low-risk switch between the two runtime implementations.

Proposed structure:

1. Move current implementation:
   - `runtime/context.py` -> `runtime/context_original.py`
2. Introduce:
   - `runtime/context_lcm.py`
3. Recreate:
   - `runtime/context.py`

`runtime/context.py` becomes a small switch module.

Conceptually:

```python
USE_LCM_CONTEXT = ...

if USE_LCM_CONTEXT:
    from .context_lcm import *
else:
    from .context_original import *
```

The exact switch mechanism can be:

- environment variable
- test-only toggle
- temporary local constant during migration

The key requirement is that:

- one import path remains stable for the rest of the runtime and tests
- switching implementations does not require broad code churn

## Phase plan

## Phase 0: Prepare the migration surface

### Tasks

1. Create this plan and keep it updated.
2. Move the current implementation to `context_original.py`.
3. Add the switch module in `context.py`.
4. Create the empty or scaffolded `context_lcm.py`.
5. Confirm the original implementation still passes through the switch.

### Exit criteria

- original runtime works unchanged under the switcher
- the rest of the codebase still imports `runtime.context`

## Phase 0.5: Restart the lifecycle prototype

The current `pyrolyze.lifecycle` implementation should not remain the active
architectural base for Phase 1.

This phase exists to make the restart explicit.

### Tasks

1. Treat the current `pyrolyze.lifecycle` implementation as a prototype.
2. Preserve only semantics worth keeping:
   - transaction-manager behavior
   - field-taxonomy direction
   - binding lifecycle semantics
   - focused lifecycle tests that still describe the right behavior
3. Remove or replace prototype internals that are no longer architectural
   matches:
   - `freezable` dependency
   - generated frozen/thawed state classes
   - whole-object current/working cloning
   - dataclass-centered core state generation
4. Re-center the module on:
   - `Record`
   - stable `context` / `context.current` / `context.working` views
   - central field-policy dispatch
   - separate managed and unmanaged shared storage

### Exit criteria

- `pyrolyze.lifecycle` is explicitly being rebuilt around records
- no future phase assumes the old dataclass/freezable-centered internals
- the remaining lifecycle tests are understood as semantic tests, not prototype
  implementation tests

## Phase 1: Build lifecycle primitives one at a time

Phase 1 should be split into narrow, test-first primitive phases.

`context_lcm.py` should not depend on a primitive until that primitive:

1. has a concrete declarative API
2. has focused independent tests
3. is expressed in generic lifecycle terms

This avoids one broad “build the whole lifecycle system” phase and makes it
clear which runtime migration slices are blocked by which missing primitives.

This phase sequence assumes that the lifecycle prototype restart in Phase 0.5
has already happened.

### Phase 1.1: field-policy engine and descriptors

#### Scope

- central field-policy registry
- descriptor installation and `__set_name__`
- decorator wrapping of plain classes onto an internal managed-context base
- generation of per-context `*_State` subclasses
- generation of per-context current/working view subclasses that inherit the
  application class
- generic per-field getter/setter dispatch
- compile-time binding of getter/setter/commit/rollback helpers into field specs
- policy hooks for init/read/write/commit/rollback/close
- `Record` abstraction for committed values and sparse working overlays
- `context`, `context.current`, and `context.working` stable-view semantics
- sparse per-record field-state for fields that need runtime state
- separate unmanaged shared storage for non-lifecycle instance attributes
- no getter-controller objects in the first implementation

#### Test requirements

- descriptor read/write tests
- field-policy dispatch tests
- inheritance tests for field policies
- plain-class `@managed_context` tests
- managed-context hierarchy merge tests using compatibility-merge semantics
- current/working view subclass tests
- normal Python method/property/classmethod/staticmethod resolution tests on
  current/working views
- unmanaged shared-store tests across stable views
- policy-specific helper invocation tests
- helper sharing tests where multiple field configs intentionally use the same
  behavior
- unqualified-access-is-default-working-surface tests
- explicit `current` read tests
- working-record copy-on-write tests
- rollback discard of working record and working field-state tests

#### Exit criteria

- `pyrolyze.lifecycle` has a generic field-policy engine
- later primitives build on records and field policies rather than on
  dataclass-specific mechanisms
- user classes do not need to inherit from a public lifecycle base
- method/property/classmethod/staticmethod behavior uses normal Python
  resolution through generated view subclasses
- handler selection occurs at decoration time rather than inside hot-path
  descriptor logic

### Phase 1.2: `TransactionManager`

#### Scope

- explicit active transaction id
- dirty/open context registry
- commit/rollback over changed contexts only
- shared generic transaction-manager support

#### Test requirements

- begin/commit/rollback transaction tests
- dirty-context enlistment tests
- changed-context-only commit tests
- no nested transaction tests for the first implementation

#### Exit criteria

- `pyrolyze.lifecycle` has a generic transaction manager
- lifecycle tests prove transaction behavior without runtime dependencies

### Phase 1.3: `const`

#### Scope

- constructor-only stable fields
- not part of current/working state
- not tracked for commit or rollback

#### Test requirements

- construction tests
- post-construction mutation rejection tests
- inheritance tests

#### Exit criteria

- `const()` is implemented and independently tested

### Phase 1.4: `static`

#### Scope

- late-initialized once-only fields
- not part of current/working state
- not committed or rolled back

#### Test requirements

- one-time assignment tests
- reassignment rejection tests
- interaction with commit/rollback tests

#### Exit criteria

- `static()` is implemented and independently tested

### Phase 1.5: `managed`

#### Scope

- ordinary lifecycle-managed fields
- copy-on-write writes
- current/working state behavior

#### Test requirements

- copy-on-write tests
- no-op write suppression tests
- commit/rollback state tests

#### Exit criteria

- `managed()` is implemented and independently tested

### Phase 1.6: `binding`

#### Scope

- scalar retained binding fields
- keyed binding maps
- accept/close lifecycle

#### Test requirements

- provisional commit tests
- rollback close tests
- committed replacement tests
- keyed binding-map diff tests

#### Exit criteria

- `binding()` is implemented and independently tested

### Phase 1.7: `owned`

#### Scope

- owned subordinate lifecycle objects
- replacement close behavior
- owner-close cascade behavior

#### Test requirements

- owned replacement tests
- owner close tests
- keyed owned-map tests if supported

#### Exit criteria

- `owned()` is implemented and independently tested

### Phase 1.8: `transient`

#### Scope

- pass/transaction-local state
- cleared on commit and rollback
- not part of committed state

#### Test requirements

- commit clear tests
- rollback clear tests
- non-persistence tests

#### Exit criteria

- `transient()` is implemented and independently tested

### Phase 1.9: `local_store`

#### Scope

- retained mutable cache/state
- survives commit and rollback
- cleared on close/deactivate only

#### Test requirements

- commit persistence tests
- rollback persistence tests
- close clear tests

#### Exit criteria

- `local_store()` is implemented and independently tested

### Phase 1.10: `derived`

#### Scope

- derived cached values
- invalidation/recompute support through class hooks

#### Test requirements

- derived cache update tests
- commit/rollback invalidation tests
- close behavior tests as needed

#### Exit criteria

- `derived()` is implemented and independently tested

### Phase 1.11: value control on `managed`

#### Scope

- `initial_working`
- compare policy
- freeze/thaw policy
- commit/thaw normalization if needed

#### Test requirements

- initial-working tests
- value-vs-identity comparison tests
- freeze/thaw normalization tests

#### Exit criteria

- managed-field value control is implemented and independently tested

### Phase 1.12: write-control enforcement

#### Scope

- transaction-scoped mutation enforcement
- stale working-copy rejection
- cross-transaction mutation rejection

#### Test requirements

- mutation without transaction tests
- stale working-copy tests
- cross-transaction misuse tests

#### Exit criteria

- write control is implemented and independently tested

### Phase 1 overall exit criteria

- the lifecycle library can express the context shapes needed by the first
  runtime migration slice
- all primitive lifecycle behaviors have focused tests
- the required behavior is available through declarative APIs rather than
  runtime-specific imperative fallback code
- transaction mechanics are represented generically rather than through
  `context.py`-specific terms
- the implementation is record-based rather than whole-object clone based

## Phase 2: Migrate `CallSiteContext` if needed first

This is optional as a standalone phase.

It should happen separately if it simplifies the main `context.py` migration.
It can happen inline with the main runtime migration if that is simpler.

### Why it may be separate

`CallSiteContext` already has:

- explicit commit/rollback
- immutable replacement semantics
- retained binding ownership

It is a strong fit for the declarative lifecycle model and may be a good place
to stabilize transaction/write-control semantics before reworking the larger
slot-context graph.

### Decision rule

Do this first only if it reduces overall migration risk.

Otherwise:

- keep it in the same phase as `context_lcm.py`
- or adapt it after the slot-context migration

## Phase 3: Migrate the simplest slot-context slices

Start with the contexts that introduce the fewest extra dimensions.

### Candidate first slices

1. `LeafSlotContext`
2. `EventHandlerSlotContext`
3. `ContainerSlotContext`

### Why these first

They exercise:

- plain value fields
- staged vs committed fields
- simple rollback
- simple close/deactivate

without immediately forcing:

- child render contexts
- keyed retained binding maps
- complex override semantics

### Exit criteria

- those context shapes exist in `context_lcm.py`
- behavior matches `context_original.py`
- focused parity tests pass
- `context_lcm.py` uses declarative lifecycle definitions rather than local
  bespoke lifecycle plumbing

## Phase 4: Migrate retained binding contexts

This phase brings in contexts where binding lifecycle is central.

### Target slices

1. `SlotCallSlotContext`
2. `SlotExprSlotContext`
3. optionally `CallSiteContext` if still pending

### Required semantics

- scalar binding lifecycle
- binding map lifecycle
- commit/rollback of retained resources
- integration with slot-expr pass behavior
- no whole-graph commit scan for localized updates

### Test requirements

- runtime parity tests for binding lifecycle
- independent lifecycle tests for binding map semantics
- proof that any new binding-oriented behavior was added to
  `pyrolyze.lifecycle` first, then consumed from `context_lcm.py`

## Phase 5: Migrate child-context and owned-child contexts

### Target slice

`ComponentCallSlotContext`

### Required semantics

- child render context as lifecycle-managed value/resource
- owned event-handler lifecycle
- rerender and replacement semantics
- close behavior for replaced child contexts

### Why this is later

This is the first slice that combines:

- ordinary values
- owned child contexts
- retained children created during runtime execution
- rollback-sensitive ownership

It should come after the simpler lifecycle machinery is already stable.

## Phase 6: Migrate fixed-structure and validation-heavy contexts

### Target slice

`AppContextOverrideSlotContext`

### Required semantics

- declared key/value arity invariants
- fixed-key shape validation
- committed/pending/current lookup semantics
- rollback restoration

This slice validates that the declarative library can express:

- class-level invariants
- custom commit-time validation
- nontrivial lifecycle state without bespoke field plumbing

## Phase 7: Achieve full parity and switch default implementation

### Tasks

1. Run the full relevant runtime suite against `context_lcm.py`.
2. Resolve remaining parity gaps.
3. Switch the default import path to `context_lcm.py`.
4. Keep the original implementation available behind the switch temporarily.
5. Once confidence is high, decide whether to retain the switch long-term or
   remove it.

### Exit criteria

- `context_lcm.py` passes the same runtime tests as the original implementation
- the default runtime path uses `context_lcm.py`

## Testing strategy

The testing strategy is intentionally two-layered.

### 1. Independent lifecycle tests

These validate the declarative library directly.

They should cover:

- current/working separation
- transaction enlistment
- dirty-context-only commit
- value-control policies
- binding lifecycle
- binding map lifecycle
- close semantics
- class-hook validation

These tests should not rely on the full runtime to prove the lifecycle
mechanism is correct.

### 2. Runtime parity tests

These validate that the migrated runtime behaves like the original runtime.

They should cover:

- all existing context-related tests
- any targeted new parity cases discovered during migration
- the ability to run both implementations under the same stable import path

## Known design risks

### 1. Declarative abstraction overhead

The lifecycle/metaprogramming layer adds runtime overhead.

That is acceptable only if:

- transaction enlistment avoids full-graph work
- only changed contexts are committed or rolled back
- optimization opportunities remain open behind the declarative API

### 2. Over-generalization

Not every runtime behavior should be metaprogrammed.

The migration should target:

- lifecycle-managed state

and not force:

- all runtime behavior
- all imperative operations

into the declarative library.

### 3. Freezable-centered backsliding

The migration fails architecturally if lifecycle semantics drift back into a
paired-dataclass or frozen/thawed-centric design.

The core engine must remain:

- field-policy-driven
- transaction-driven
- descriptor/proxy-based where needed

`freezable` should remain optional leaf support only.

### 4. Incremental extension of the wrong prototype

The migration also fails architecturally if the existing prototype is extended
piecemeal in ways that preserve its wrong center.

The core should be restarted when needed around:

- record overlays
- direct field-policy dispatch
- mutable current/working record storage

instead of preserving whole-object thaw/freeze machinery just because it
already exists.

### 5. Domain leakage into the lifecycle library

The migration fails architecturally if `pyrolyze.lifecycle` starts encoding
runtime-specific `context.py` details.

The library must remain usable for any complex lifecycle-managed system, not
just the Pyrolyze slot runtime.

### 6. Hidden semantic gaps

`context.py` has a lot of small behaviors that are easy to miss.

That is why the migration must be:

- phased
- parity-tested
- backed by independent lifecycle tests

## Success criteria

This plan is successful if:

1. `context_lcm.py` becomes the default runtime implementation.
2. The existing runtime behavior is preserved.
3. Lifecycle behavior is expressed declaratively rather than by repeated manual
   field plumbing.
4. New lifecycle features are testable independently of the full runtime.
5. Commit and rollback cost scale with changed contexts rather than with the
   size of the whole context graph.
6. `context_lcm.py` does not contain a parallel bespoke lifecycle framework.
7. Application-specific semantics remain visible in the application classes
   rather than being hidden inside generic helpers.
