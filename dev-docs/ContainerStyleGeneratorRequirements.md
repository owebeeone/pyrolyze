# Container Style Generator Requirements

## Purpose

This document defines the requirements for the next generic-backend testing
surface used to validate mount-style behavior independently of any one live UI
toolkit.

The immediate driver is a real PySide6 bug where a stable nested container
surface is misplaced after conditional sibling churn. That bug is currently
captured by a red PySide6-native test and should remain red until the generic
test platform and the runtime fix are both in place.

This document is only about the testing/generator requirements. It is not an
implementation plan for the bug fix itself.


## Problem Statement

PyRolyze currently has a gap between:

- backend-independent graph/mount tests
- real-backend conformance tests

The current generic backend is strong enough to verify:

- emitted source shape
- mounted graph shape
- generation visibility
- broad mount legality

It is not yet strong enough to verify:

- exact mount-style placement semantics
- stable survivor placement under sibling churn
- nested ordered surface behavior
- mutation-policy differences across adapter styles
- operation-level replay invariants

As a result, a real backend can regress even while the generic backend still
reports success.


## Goals

1. Provide a backend-independent test platform that can model all supported
   mount API styles.
2. Make mount-style mutation behavior testable without relying on PySide6,
   tkinter, or any other specific toolkit.
3. Support exact testing of mutation sequences that can cause placement drift,
   survivor misordering, duplicate attachment, rollback corruption, or stale
   retained children.
4. Support deterministic narrative tests and Monte Carlo fuzzing using the same
   underlying model.
5. Make fuzz failures replayable as stable regression tests.
6. Close the current blind spot where final graph shape can look correct while
   placement semantics are wrong.


## Non-Goals For This Cycle

1. Do not migrate all existing tests into the new matrix immediately.
2. Do not require every high-level PyRolyze test to run against every mount
   style in this cycle.
3. Do not replace real-backend conformance tests.
4. Do not fix the current PySide6 bug as part of this requirements document.
5. Do not collapse all backend-specific learnings into one fake universal
   policy. Policy variation must remain expressible.


## Core Requirement

The generic backend builder must be extended so that it can generate and drive
container/mount surfaces that faithfully represent every supported mount API
style that PyRolyze claims to support.

The resulting test surface must be able to express:

- the authored tree
- the mounted graph
- the active mount-style contract
- the sequence of placement/mutation operations
- the final committed state after each render pass


## Supported Mount Styles

The platform must support all currently supported mount styles, including at
least:

1. Ordered append/place/sync style mounts
2. Anchor-before placement style mounts
3. Keyed mounts
4. Single-child mounts
5. Nested ordered container surfaces
6. Mixed surfaces where one authored wrapper can be replayed against different
   backend mount styles
7. Rollback-capable and non-snapshot fallback variants where behavior differs
8. Optional readback/current-value surfaces where the runtime depends on them

If PyRolyze supports more mount styles than are listed here, the implementation
should treat this list as incomplete and extend it rather than narrowing the
claimed runtime surface.


## Interface Requirement

When this work reaches testing, the platform must support a single generated
interface that exposes all supported container/mount styles.

That interface must let a test assert not only that a tree is legal, but that:

- the mount API exercised only the expected mount style
- no unintended fallback style was used
- the placement/mutation log is consistent with the declared style

This is a critical requirement because otherwise the generic backend can appear
to pass while silently routing behavior through a simpler style than the real
backend uses.


## Mutation-Sequence Requirements

The first test wave must focus on mutation sequences, not broad app scenarios.

The platform must support deterministic tests for at least these cases:

1. Conditional sibling replacement before a stable mounted child
2. Conditional sibling replacement after a stable mounted child
3. Remove-one-preserve-one sibling churn
4. Reorder surviving siblings
5. Nested ordered surface retained across sibling churn
6. Replace-one-preserve-one within the same parent surface
7. No-op rerender preserving placement and generation
8. Rollback restoring last committed placement
9. Equivalent final-shape rerender converging to the same committed result as a
   fresh render of that shape

These tests must assert more than final tree shape.


## Required Assertions

For deterministic mutation-sequence tests, the platform must support asserting:

1. Emitted authored UI shape
2. Mounted graph shape
3. Mount bucket order
4. Placement order within each relevant surface
5. Stable survivor placement after churn
6. No zombie retained children
7. No duplicate retained children
8. No illegal placement operations for the active style
9. Generation locality
10. Final committed state equivalence against a fresh render of the same final
    authored shape


## Operation Log Requirement

The generic backend must expose an operation log rich enough to diagnose mount
style behavior directly.

At minimum, the log must be able to represent:

- create
- attach
- detach
- replace
- place at index
- place before anchor
- keyed insert/update/remove
- rollback restore
- no-op replay

The operation log must be deterministic and suitable for:

- direct test assertions
- snapshotting
- fuzz failure replay
- debugging regressions without a live backend


## Policy Variation Requirement

The test platform must support configurable mutation policies because runtime
behavior may legitimately vary based on:

- mount style
- backend learnings
- adapter behavior
- rollback capability
- change count / churn volume

This is important because some backends or adapter surfaces may deliberately
change mutation strategy under churn.

The generic backend must therefore support pluggable or configurable policies
for:

- ordered replay
- anchor-before replay
- snapshot/restore rollback
- fallback rollback
- style-specific placement behavior
- churn-sensitive mutation strategy where applicable

Policy must be part of the test identity, so a failure can always report:

- mount-point profile identity
- mount style
- active mutation policy
- mutation sequence
- seed, when fuzzed


## Monte Carlo Fuzzer Requirement

The platform must include a Monte Carlo mutation fuzzer built on the same model
as the deterministic tests.

The fuzzer must vary:

- mount-point profile identity
- branch toggles
- sibling insertion/removal
- reorder operations
- nested surface structure
- keyed vs non-keyed placement
- rollback injection where legal
- mutation policy
- mount style

The fuzzer must assert invariants, not just absence of crashes.

Required invariants include:

1. Final committed graph equals a fresh render of the same final authored state
2. Surviving retained children preserve legal placement for the active style
3. No zombie or duplicate retained nodes remain
4. Generation changes remain local to actually changed nodes
5. Rollback restores the previous committed state when triggered
6. Operation log stays legal for the chosen mount style and policy


## Fuzzer Replay Requirement

Every fuzz failure must be replayable.

The platform must record enough information to reproduce a failure exactly:

- seed
- mount-point profile identity
- mount style
- mutation policy
- authored starting state
- mutation sequence
- emitted UI snapshot
- mounted graph snapshot
- operation log

The replay form must be usable to promote a fuzz-discovered failure into a
fixed deterministic regression test.


## Conformance Layer Requirement

This work does not remove the need for real-backend tests.

Instead, the intended layering is:

1. Generic backend deterministic mutation tests
2. Generic backend Monte Carlo fuzzing
3. Real-backend conformance tests for selected high-value scenarios and
   fuzz-discovered seeds

This keeps the semantic contract durable even if one live backend is removed in
the future.


## Gap-Closing Requirements

The new platform must close the testing gaps exposed by the current failure.

Specifically, it must prevent the following blind spots:

1. Tests that verify final graph shape but not placement semantics
2. Tests that verify one mount style while the real backend uses another
3. Tests that verify only creation and simple reorder, but not survivor
   placement under branch churn
4. Tests that cannot express nested ordered surfaces
5. Tests that cannot vary mutation behavior by policy
6. Tests that cannot convert random failures into fixed regressions


## Relationship To Existing Tests

The existing red PySide6-native regression test should remain in place as the
real-backend proof of the current bug.

The new generic test platform should produce a parallel deterministic test for
the same behavioral failure class.

Once the new platform is mature enough, older mount-point tests that provided
false confidence should be reviewed and deprecated only when a stronger
replacement clearly subsumes their intended coverage.


## Minimum Deliverables For This Cycle

1. Extend the generic backend builder to expose all supported mount styles
2. Add one interface surface capable of expressing those styles
3. Add deterministic mutation-sequence tests for the current failure class
4. Add operation-log assertions
5. Add a Monte Carlo mutation fuzzer
6. Add fuzz replay support
7. Add a parallel backend-independent regression for the current PySide6 bug


## Success Criteria

This cycle is successful when:

1. The generic backend can express all supported mount styles
2. The new deterministic mutation tests can model the current failure class
3. The fuzzer can explore the same behavioral space and emit replayable seeds
4. Tests can assert that only the intended mount style was exercised
5. The platform closes the specific blind spot that let stable-survivor
   placement regress unnoticed
