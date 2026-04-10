# Lifecycle Nuovo Transaction Plan

This plan is extracted from [`LifecycleNuovoTransaction.md`](dev-docs/LifecycleNuovoTransaction.md).
It contains the implementation-oriented phased work, separated from the design
discussion.

## Phase 1: Rename and Wrap

1. Rename current `TransactionManager` to `GroupTransactionManager`
2. Introduce new top-level `TransactionManager`
3. Implement:
   - lazy `GroupTransactionManager` creation
   - explicit manager `tx_groups`
   - group-based `begin`, `validate`, `commit_only`, `commit`, `rollback`,
     `enlist`, `drop`
   - no-argument `begin`, `commit`, `rollback` for “all groups”
   - context-manager form for `begin(...)`
   - keep multi-group operations as ordered independent group operations, not
     atomic coupled transactions
4. Preserve existing behavior for the default case by routing everything through:
   - `DEFAULT_TRANSACTION`

This phase should be almost entirely mechanical.

## Phase 2: Add `tx_group` to Field Specs

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

## Phase 3: Group-Aware Working State

1. Replace single:
   - `working_record`
   - `working_tx_id`

with per-group working state
2. Route reads/writes through the field’s `tx_group`
3. Keep current/published storage shared
4. Keep one unified public `working` view
5. Preserve hot-path performance by compiling `tx_group` into getter/setter
   dispatch tables rather than looking it up dynamically from `FieldSpec` on
   every access
6. Prefer class-local compiled `tx_index` slots and per-instance indexed
   transaction state storage over repeated hash-map lookups by group key

This is the first substantive behavior change.

## Phase 4: Tests

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
- multi-group `begin/commit/rollback` remain ordered independent operations
  rather than atomic coupled operations
- application code can use `validate(...)` + `commit_only(...)` to implement
  coupled transaction policy outside lifecycle core
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
