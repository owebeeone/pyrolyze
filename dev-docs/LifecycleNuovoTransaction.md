# Lifecycle Nuovo Transaction Design

## Why

The current lifecycle transaction model assumes one active transaction domain for
all transactional fields on a context.

That is good enough for simple publication semantics, but it is too coarse for
the runtime context graph work now underway.

The immediate motivating case is:

- we want to run a pass that uses transient scratch state
- we do **not** want that to imply a publication mutation
- we want the authoritative published graph to remain unchanged unless the
  publication transaction is explicitly active

In other words, we need to be able to say:

- these fields participate in the publication transaction
- these other fields participate in a pass/scratch transaction

and then choose which transaction groups are active for a given operation.

This lets us support:

- publish-only work
- pass-only work
- combined publish+pass work

without hardcoding those semantics into every field kind.

## Core Idea

Add a `tx_group` field-spec attribute.

Every transactional field belongs to a transaction group.

Default:

- `tx_group=DEFAULT_TRANSACTION`

That keeps existing lifecycle declarations simple. Only fields that need
different transaction behavior need to specify another group.

`tx_group` should be any `Hashable`, not just `str`.

Why:

- application code may want to use its own stable keys
- string names are fine as the lifecycle default
- but the lifecycle core should not force all applications into one naming
  convention

So the effective contract is:

- `tx_group: Hashable`

with lifecycle default:

- `DEFAULT_TRANSACTION = "default_transaction"`

Examples:

```python
value: int = managed(default=0)
```

implicitly means:

```python
from collections.abc import Hashable

DEFAULT_TRANSACTION: Hashable = "default_transaction"

value: int = managed(default=0, tx_group=DEFAULT_TRANSACTION)
```

and application code can define semantic aliases:

```python
from collections.abc import Hashable

PUBLISH_TRANSACTION: Hashable = "publish_transaction"


def publish_transient(*, tx_group: Hashable | None = None, **kwds):
    if tx_group is None:
        tx_group = PUBLISH_TRANSACTION
    return transient(tx_group=tx_group, **kwds)
```

Then:

```python
traversal_state: TravState | None = publish_transient(
    default=None,
    working_default_factory=TravState,
)
```

## Naming

The current single-group `TransactionManager` should be renamed:

- `GroupTransactionManager`

It remains the transaction engine for one transaction group.

Then introduce a new top-level:

- `TransactionManager`

This new `TransactionManager` owns a map of group managers and routes lifecycle
operations by `tx_group`.

## Manager Split

### `GroupTransactionManager`

This is the current transaction manager behavior with a new name.

Responsibilities:

- maintain one active transaction for one group
- maintain the nested begin counter for that group
- enlist dirty contexts for that group
- track validation for that group
- commit / rollback for that group

This class should stay as close as possible to the current implementation.

### `TransactionManager`

This becomes the top-level multi-group coordinator.

Responsibilities:

- maintain `dict[Hashable, GroupTransactionManager]`
- maintain the allowed `tx_groups` universe for that manager
- create group managers on demand, but only for allowed groups
- route begin/commit/rollback/enlist/drop by group

Constructor shape:

```python
TransactionManager(tx_groups={PUBLISH_TRANSACTION, PASS_TRANSACTION})
```

Semantics:

- `DEFAULT_TRANSACTION` is always implicitly supported
- so `tx_groups={PUBLISH_TRANSACTION, PASS_TRANSACTION}` means the full set:
  - `{DEFAULT_TRANSACTION, PUBLISH_TRANSACTION, PASS_TRANSACTION}`
- asking the manager to operate on an unknown group is an error

This keeps the transaction-group universe explicit and predictable while
avoiding boilerplate repetition of `DEFAULT_TRANSACTION`.

## API Shape

### Field Specification

Add:

- `tx_group: Hashable = DEFAULT_TRANSACTION`

to transactional lifecycle fields:

- `managed`
- `binding`
- `owned`
- `transient`

It is probably harmless to allow it on all lifecycle fields, but it only has
meaning for fields that use working/current transactional state.

For the first pass, applying it only to transactional kinds is clearer.

### Transaction Manager API

The new top-level `TransactionManager` should accept group names explicitly.

Recommended initial API:

```python
from collections.abc import Hashable

GROUP_A: Hashable = "group_a"
GROUP_B: Hashable = "group_b"

manager.begin()
manager.begin(GROUP_A)
manager.begin(GROUP_A, GROUP_B)
manager.commit()
manager.commit(GROUP_A)
manager.rollback()
manager.rollback(GROUP_A, GROUP_B)
```

Semantics:

- `begin()` means begin all registered groups
- `commit()` means commit all active registered groups
- `rollback()` means rollback all active registered groups
- passing group names limits the operation to the named groups
- `begin(A, B)` is just syntactic sugar for independent begins of `A` and `B`
- `commit(A, B)` is just ordered independent commits of `A` and `B`
- `rollback(A, B)` is just ordered independent rollbacks of `A` and `B`

So the API supports both:

- explicit group control
- convenient “all groups” operation

If an explicit group is not in the manager's supported `tx_groups` set, the
operation must fail immediately.

Importantly, multi-group operations are **not** atomic coupled operations.

That means:

- one group may successfully commit while another later group fails
- successful groups are not retroactively rolled back
- cross-group all-or-nothing behavior remains application policy

### Context Manager Form

`begin(...)` should also support Python context-manager usage.

Conceptually:

```python
with manager.begin(GROUP_A):
    ...
```

Semantics:

- `__enter__` begins the named group or groups
- clean `__exit__` commits those same group or groups
- exceptional `__exit__` rolls back those same group or groups

This is important because it gives application code explicit lexical control
over group lifetime and nesting.

For example:

```python
with manager.begin(GROUP_A):
    with manager.begin(GROUP_B):
        work()
```

Then:

- `GROUP_B` exits before `GROUP_A`
- clean exit commits `GROUP_B` before `GROUP_A`
- exceptional exit rolls back `GROUP_B` before `GROUP_A`

This helper is still only lexical convenience.

It does **not** add atomic cross-group commit semantics.

So on clean exit:

- `commit(B)` runs
- then `commit(A)` runs

and if `commit(B)` succeeds but `commit(A)` later fails:

- `B` remains committed
- `A` fails according to its own group semantics
- no automatic rollback of `B` occurs

## Manager `tx_groups`

Each `TransactionManager` has an explicit `tx_groups` set.

This is the set of supported non-default transaction groups for that manager.

Effective supported group universe:

- `{DEFAULT_TRANSACTION} ∪ tx_groups`

This gives us:

- stable semantics for `begin()`, `commit()`, and `rollback()` with no args
- predictable manager behavior
- no hidden runtime group growth
- easier testing and reasoning

This is intentionally manager-local rather than a mutable process-global
registry.

## Why `begin()` Should Mean "All Groups"

Once the manager has an explicit `tx_groups` set, `begin()` with no
parameters becomes well-defined:

- begin all groups in `{DEFAULT_TRANSACTION} ∪ tx_groups`

That is worth supporting because it matches the common “start the full lifecycle
transaction envelope” use case while still allowing more selective calls where
needed.

The implementation can still create per-group managers lazily, but the manager's
declared group universe defines the target group set for `begin()`, `commit()`,
and `rollback()`.

## Low-Level API Exposure For Application Policy

The lifecycle core should expose enough low-level transaction API for
application/runtime code to build stricter coupled semantics if it wants them.

This is important because:

- lifecycle core intentionally keeps groups independent
- but application code may still want validate-all / commit-selected behavior

So the low-level API should include:

- `validate(...)`
- `commit_only(...)`
- `commit(...)`
- `rollback(...)`

Where:

- `commit(...)` is the normal convenience path and performs validation as needed
- `commit_only(...)` performs the commit path only and assumes validation has
  already been handled by the caller

This allows application code to do things like:

1. `validate(A, B)`
2. decide whether to proceed
3. `commit_only(A, B)`

or:

1. `validate(A, B)`
2. `commit_only(A)`
3. `rollback(B)`

without requiring lifecycle core to own that policy.

Related useful inspection surface may include:

- active/open state per group
- dirty-context inspection per group
- deferred retained-resource bookkeeping visibility

The exact inspection API can be small, but the design should not block an
application from implementing coupled transaction policy above the lifecycle
layer.

## Field Semantics

The important separation is:

- field group selection
- transaction semantics

The lifecycle core only needs to know:

- which group a field belongs to
- which group manager to use for that field’s working state

It does **not** need to hardcode application policies like:

- `PASS_TRANSACTION implies PUBLISH_TRANSACTION`
- `PUBLISH_TRANSACTION may commit without PASS_TRANSACTION`

Those policies can be implemented by application code or by higher-level runtime
conventions.

## Unified `working` View

`self.working` remains one unified working view, just like today.

Grouped transactions do **not** imply a split public working-view API.

Rules:

- for field `f` with group `G`
  - if `G` has working state active and `f` has a working value, `self.working.f`
    returns that working value
  - otherwise `self.working.f` returns the current value
- writing `self.working.f = ...` still requires group `G` to be active
- thaw / working initialization for frozen or transient state still only occurs
  when the field's own transaction group is active

So the public semantics stay familiar:

- reads from `working` fall back to current when no working value exists
- writes require an active transaction

The only change is that "active transaction" is now resolved per field group.

## Working State Routing

Each transactional field must resolve its working state through the manager for
its own `tx_group`.

That means lifecycle state accessors need to stop assuming one global:

- `working_record`
- `working_tx_id`

Instead, they need group-aware working storage.

Conceptually:

- current/published state remains per context field
- working state becomes per context field group

The likely shape is:

- one current record
- per-group working records

This keeps published state unified while allowing multiple transactional working
channels.

## Enlistment Model

Enlistment remains context-based, but it is no longer global.

Old model:

- a context is enlisted once in the single active transaction

New model:

- a context is enlisted once per active transaction group

That means the unit of enlistment is:

- context + group

not:

- one global context enlistment
- one enlistment per field

This is important because multiple fields on the same context may belong to the
same transaction group. We only want to enlist that context once for that
group’s transaction.

So:

- first write/promotion to a field in group `G`
  - creates or promotes the context working state for `G`
  - enlists the context in `G`
- subsequent writes to fields in `G`
  - do not re-enlist
- writes to fields in a different group `H`
  - may separately enlist the same context in `H`

### Likely Context State Structures

The current lifecycle state uses:

- `working_record: Record | None`
- `working_tx_id: int | None`

The grouped form should generalize this to:

- `working_records: dict[Hashable, Record]`
- `working_tx_ids: dict[Hashable, int]`

Conceptually:

- current/published state stays unified
- working/enlistment state becomes group-indexed

This is the minimal structural change needed to support grouped enlistment.

### Hot Path Constraint

Grouped transaction routing affects the hottest lifecycle paths, especially:

- `working.x`
- `working.x = value`
- default-view reads/writes that promote to working state

So the implementation must avoid per-access dynamic `FieldSpec` lookups for
`tx_group`.

Required approach:

- compile `tx_group` into the field getter/setter tables at decoration time
- field accessors should already know the field's group when invoked
- do **not** fetch `spec = __field_specs__[name]` and then read `spec.tx_group`
  on every hot-path access

That means the grouped version of lifecycle should preserve the current style:

- table-driven dispatch first
- group-aware runtime routing second

The expected runtime overhead should then be limited to the actual group working
state lookup, for example:

- `working_records[group]`
- `working_tx_ids[group]`

Preferred implementation:

- assign each used `tx_group` a stable class-local slot index at
  `managed_context` decoration time
- compile field dispatch tables with that `tx_index`
- store per-group transaction state in indexable per-instance storage

Conceptually, the generated lifecycle state class would carry:

- `__class_tx_groups__: tuple[Hashable, ...]`
- `__class_tx_group_to_index__: dict[Hashable, int]`

and each context state instance would carry something like:

- `_tx_state_by_index: list[_LifecycleTxState]`

where `_LifecycleTxState` is the per-group transaction working state for that
context instance.

Then hot-path field access can use:

- precompiled `tx_index`
- direct indexed state access

instead of repeated hash lookups by group name.

This is the cleanest grouped-transaction implementation because the index is
compiled per class and field, not discovered dynamically through the manager on
every access.

## Validation and Commit Ordering

Validation and commit ordering are group-local by default.

That means:

- each active group manager validates its own enlisted contexts
- each active group manager commits its own contexts in its own ordering

Failure in one group does **not** imply rollback of other groups by default.

So the default semantics are:

- validate group A
- commit or rollback group A according to group A's outcome
- validate group B
- commit or rollback group B according to group B's outcome

For no-argument `begin()/commit()/rollback()` and multi-group calls like:

- `begin(GROUP_A, GROUP_B)`

the lifecycle core does **not** promise a special semantic ordering contract
beyond matching the manager's own begin/close implementation.

If application code needs a specific order, it should express that order with
explicit nesting:

```python
with manager.begin(GROUP_A):
    with manager.begin(GROUP_B):
        work()
```

That gives the application precise control over which group exits first.

If the application wants cross-group all-or-nothing behavior, it must provide
that policy itself. The expected pattern is:

- validate all relevant groups first
- decide whether to proceed
- then commit or rollback groups explicitly

That coupling belongs in application code or higher-level runtime policy, not
in lifecycle field semantics.

### Validator and Order-Key Group Scope

`commit_validator` and `commit_order_key` need group scope as well.

Rule:

- if no group is specified, they apply to `DEFAULT_TRANSACTION`

That keeps existing declarations simple while allowing explicit group behavior
when needed.

For example, conceptually:

```python
must_pass = commit_validator(default=validate_publish, tx_group=PUBLISH_TRANSACTION)
rank = commit_order_key(default=(0,), tx_group=PUBLISH_TRANSACTION)
```

This means:

- validator/order metadata is evaluated against the specified transaction group
- unspecified group means default-group behavior

### Commit-Specific Function Lifetime Rule

If commit-specific functions are introduced, for example:

- `on_before_commit`
- `on_after_commit`
- `on_after_rollback`

then `on_after_commit` creates one important retained-resource rule:

- `previous` must remain valid for all post-commit handlers

That means old `binding` / `owned` values referenced by `previous` must not be
finally released until all post-commit handlers for that group have completed.

So the lifecycle engine should:

1. capture `previous`
2. apply the committed current state
3. run all post-commit handlers for that group
4. only then release deferred old retained values

And the deferred release must happen in a `finally` path so cleanup still occurs
if any post-commit handler raises.

This specifically means:

- old `binding` / `owned` values may need deferred release bookkeeping during
  commit
- final `dec_ref()` / teardown must occur after post-commit handlers
- cleanup must still happen exactly once if handlers raise

### Commit-Specific Function Representation

Commit-specific functions should be declared as lifecycle field kinds:

- `on_before_commit`
- `on_after_commit`
- `on_after_rollback`

They should **not** be stored as ordinary current/working value fields.

Instead, they should compile at decoration time into runner tables, following
the same compiled-dispatch approach used for context-aware factories.

Conceptually:

- `__class_ftable_before_commit_runners__: dict[Hashable, tuple[Runner, ...]]`
- `__class_ftable_after_commit_runners__: dict[Hashable, tuple[Runner, ...]]`
- `__class_ftable_after_rollback_runners__: dict[Hashable, tuple[Runner, ...]]`

This is the least intrusive implementation because:

- no fake storage is introduced for hook declarations
- ephemeral values like `previous` can be supplied at dispatch time
- dispatch stays fast and table-driven

### Commit-Specific Function Parameters

These hook functions should use the same injected-runner machinery as
`default_factory` / `working_default_factory`, but with hook-specific allowed
parameter sets.

Recommended injected parameters:

- `on_before_commit`
  - `self`
  - `current`
  - `working`
  - `tx_group`
- `on_after_commit`
  - `self`
  - `previous`
  - `current`
  - `tx_group`
- `on_after_rollback`
  - `self`
  - `current`
  - `tx_group`

For `on_after_rollback`, `current` is just the ordinary current view after the
rollback for that group, which is also the current state that existed before and
during that transaction for that group.

### Commit-Specific Function Exceptions

Hook functions should use ordinary Python exception behavior.

Meaning:

- if one hook raises, that exception propagates normally
- if multiple hooks raise during one grouped operation, the lifecycle layer may
  raise an `ExceptionGroup`
- no additional custom hook-exception wrapper is needed

### Hook Aggregation and Inheritance

Commit-specific functions use **Option B**:

- hook fields aggregate by distinct field name
- same field name overrides normally
- different field names all run
- execution order follows the normal lifecycle merged field order derived from
  MRO
- no additional implicit chaining is performed

This is intentionally "principled messy":

- deterministic
- inspectable
- aligned with normal lifecycle field inheritance rules

Examples:

- base defines:
  - `publish_a`
  - `publish_b`
- child overrides:
  - `publish_a`
- child adds:
  - `publish_c`

Effective execution order is the MRO-merged field order with:

- `publish_a` resolved to the child override
- `publish_b` retained from the base
- `publish_c` added by the child

Same-name overrides must not change `tx_group`. If a derived hook field reuses
the same name with a different `tx_group`, that should be an error.

## Initial Implementation Plan

### Phase 1: Rename and Wrap

1. Rename current `TransactionManager` to `GroupTransactionManager`
2. Introduce new top-level `TransactionManager`
3. Implement:
   - lazy `GroupTransactionManager` creation
   - explicit manager `tx_groups`
   - group-based `begin`, `commit`, `rollback`, `enlist`, `drop`
   - no-argument `begin`, `commit`, `rollback` for “all groups”
   - context-manager form for `begin(...)`
4. Preserve existing behavior for the default case by routing everything through:
   - `DEFAULT_TRANSACTION`

This phase should be almost entirely mechanical.

### Phase 2: Add `tx_group` to Field Specs

1. Add `tx_group` to:
   - `LifecycleField`
   - `FieldSpec`
   - field constructors (`managed`, `binding`, `owned`, `transient`)
   - grouped validator/order declarations
   - grouped commit-specific hook declarations
2. Default it to:
   - `DEFAULT_TRANSACTION`
3. Merge it through inheritance rules

At this stage, lifecycle declarations can start specifying alternate groups even
if runtime behavior still defaults to one group in many places.

### Phase 3: Group-Aware Working State

1. Replace single:
   - `working_record`
   - `working_tx_id`

with per-group working state
2. Route reads/writes through the field’s `tx_group`
3. Keep current/published storage shared
4. Keep one unified public `working` view

This is the first substantive behavior change.

### Phase 4: Tests

Add tests for:

- default behavior remains unchanged with no custom group
- pass-only transaction mutates transient scratch without changing published state
- publish-only transaction leaves pass-group transient fields inactive
- combined publish+pass begin works when both groups are explicitly started
- nested begin counts are tracked independently per group
- rollback/commit affect only the named groups
- `self.working` reads per-field working state across all active groups
- validator/order metadata uses default group when unspecified
- unknown groups fail immediately against manager `tx_groups`
- context-manager `begin(...)` commits on clean exit and rolls back on exception
- post-commit handlers can observe `previous` binding/owned values before final
  release
- deferred release of previous binding/owned values happens after all post-commit
  handlers complete
- deferred release still happens exactly once when a post-commit handler raises
- commit-specific hooks compile to group runner tables, not ordinary stored
  current/working fields
- commit-specific hooks aggregate by distinct field name and run in MRO-derived
  merged field order
- same-name commit-specific hook overrides may not change `tx_group`

## Immediate Application Use Case

This design exists mainly to support runtime context state managers that need:

- transient pass-local scratch
- optional publication mutation

Specifically:

- a readonly traversal pass should still be able to allocate transient state
- that transient state should disappear when the pass ends
- the published graph should remain immutable unless the publication group is
  active

That is the direct pressure driving this feature.

## Non-Goals for the First Pass

Not part of the first implementation:

- automatic coupling between groups
- cross-group rollback on single-group validation failure
- group inheritance rules beyond explicit field declaration
- special hardcoded semantics for “publish” vs “pass”

Those can be layered later once the generic grouped-transaction machinery is in
place.
