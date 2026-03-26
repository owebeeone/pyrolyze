# Container Style Generator Test Plan

## Purpose

This document defines the test plan for the mount-style expansion work around
`pyrolyze.testing.generic_backend`.

The aim is to create one strong platform for mount-style and mutation-sequence
testing that can:

- catch backend-independent placement/retention bugs early
- support fuzzing and replay
- remain useful even if a specific live backend is removed later


## Success Condition

The work is successful when the backend-independent platform can express the
same behavioral failure class as the current red PySide6 regression and when the
eventual runtime fix makes the real PySide6 regression go green.

So yes, in theory, during this process the red PySide6 test should go green,
but only after:

1. the generic test platform is strong enough to model the bug class
2. the runtime/backend bug itself is fixed

The generic platform alone does not make the PySide6 test green. It gives us
the durable contract and earlier detection.


## Testing Layers

### 1. Deterministic Generic Mutation Tests

These are the first priority for this cycle.

They should validate:

- final mounted graph
- placement order
- operation log legality
- survivor stability
- generation locality

### 2. Generic Monte Carlo Fuzzing

This is the second priority.

It should explore the same mutation and style space and produce replayable
failures.

### 3. Real-Backend Conformance

This remains necessary for selected scenarios and for promoted fuzz seeds.

The existing red PySide6 regression stays as the current real-backend proof.


## Phase 1 Test Scope

Phase 1 should focus on deterministic mutation-sequence tests and the style
expansion surface itself.

Do not start with broad migration of all existing tests.


## API Surface Tests

The generator/backend API tests should cover:

1. one logical mount request can expand into multiple concrete style variants
2. each concrete generated mount surface reports its style identity
3. each concrete generated mount surface reports its mount-point profile/policy identity
4. style and profile identity are visible in snapshots/logs
5. style expansion does not silently collapse multiple requested styles into one
   fallback surface
6. one concrete mount surface still has one unambiguous style


## Interface Validation Tests

These should land in Phase 2.

The generated interface should support all relevant styles in one surface.

When that lands, tests must verify:

1. the authored scenario chose the intended concrete style
2. only that style was exercised
3. no unintended fallback style handled the mount

This should be treated as a required assertion layer, not an optional extra.


## Deterministic Mutation-Sequence Matrix

For this cycle, the highest-value deterministic scenarios are:

1. Conditional sibling replacement before a stable retained child
2. Conditional sibling replacement after a stable retained child
3. Remove-one-preserve-one sibling churn
4. Reorder surviving siblings
5. Nested ordered surface retained across sibling churn
6. Replace-one-preserve-one with trailing sibling stability
7. Rollback restoring prior placement
8. Same-final-shape rerender equivalence

Each scenario should initially be exercised against the relevant style variants,
not necessarily every style in the system.


## Mount Styles To Exercise

The expanded platform should eventually support all mount styles, but the first
wave of tests should explicitly cover at least:

1. Ordered/index replay
2. Ordered/anchor-before replay
3. Ordered/sync-preferred replay
4. Single mount
5. Keyed mount
6. Nested ordered surfaces
7. Optional readback/current-value surfaces where mount behavior depends on them


## Required Assertions Per Deterministic Test

Each deterministic test should assert:

1. emitted authored tree is the expected shape
2. mounted graph is the expected shape
3. concrete style identity matches the intended style
4. placement order matches the intended order
5. surviving retained children keep legal placement
6. no zombie children remain
7. no duplicate retained children remain
8. operation log only contains operations legal for the intended style
9. generation only changes on affected nodes
10. final committed state matches a fresh render of the same final authored
    shape


## Operation Log Tests

The operation log should be asserted directly in focused tests.

Initial required log coverage:

1. create
2. attach
3. append
4. place-by-index
5. place-before-anchor
6. sync
7. detach
8. replace
9. rollback restore
10. no-op replay

For keyed mounts, also verify:

1. keyed insert
2. keyed update
3. keyed remove
4. bucket identity stability


## Monte Carlo Fuzzer Plan

After the deterministic suite is in place, add a Monte Carlo fuzzer that varies:

1. mount-point profile identity
2. mount style
3. mutation sequence
4. branch toggles
5. reorder operations
6. insertion/removal positions
7. nested surface structure
8. keyed values
9. rollback injection
10. mutation policy

The fuzzer should assert invariants rather than screenshots or toolkit-specific
effects.


## Fuzzer Invariants

Required invariants:

1. final committed graph matches a fresh render of the same final authored state
2. surviving retained children preserve legal placement under the intended style
3. no zombie children remain
4. no duplicate retained children remain
5. generation updates stay local to changed nodes
6. rollback restores the previous committed state where supported
7. operation log remains legal for the intended style and active policy


## Fuzzer Replay Tests

Every fuzz failure must be replayable.

The replay format must capture:

1. seed
2. mount-point profile identity
3. style identity
4. policy identity
5. starting state
6. mutation sequence
7. mounted graph snapshot
8. operation log

There should also be focused tests for replay itself:

1. replay reproduces the same failure
2. replay reproduces the same graph and log
3. replay can be promoted into a deterministic regression


## Policy Variation Tests

Because mutation behavior may vary by API learnings, backend learnings, or churn
volume, the test platform must eventually cover policy as a separate axis.

Initial policy-oriented tests should verify:

1. ordered/index with place-only behavior
2. ordered/index with sync-preferred behavior
3. ordered/anchor-before behavior
4. rollback via snapshot/restore
5. rollback via fallback reapply

These can be added after the first deterministic style tests land.


## Gap-Closing Checks

The test plan must explicitly close the gaps that let the current bug escape.

Add checks ensuring we are no longer only testing:

1. final graph shape without placement semantics
2. one style while the real backend uses another
3. creation and reorder without survivor churn
4. flat ordered surfaces without nested ordered surfaces
5. static examples without mutation-sequence coverage
6. deterministic cases without fuzz exploration


## Existing Test Review

During this process, identify the existing older mount-point test that gave
false confidence.

Do not remove it immediately.

Instead:

1. build a parallel stronger replacement on the new platform
2. extend the replacement until it fully covers the intended failure class
3. only then deprecate the older test if the new one clearly subsumes it


## Immediate Deliverables

1. Style-expansion API tests
2. Style identity metadata tests
3. Deterministic mutation-sequence tests for the current failure class
4. Operation-log assertions for those tests
5. A parallel backend-independent regression for the current red PySide6 bug


## Deferred Deliverables

1. Full Monte Carlo fuzzing
2. Replay promotion tooling
3. Broader policy matrix
4. Wide migration of older mount-point or adapter tests
