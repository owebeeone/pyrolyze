# Host Surface Placement Plan

## Purpose

This document converts the host-surface-placement design into a concrete
implementation plan.

It is a follow-on track to the completed mount-style / mutation-policy
roll-build. Its purpose is to close the remaining blind spot where a real
backend can preserve structural mounted-graph shape while still drifting to the
wrong host placement order.


## Scope

This plan covers:

- generator-facing API additions for host placement surfaces
- generic-backend runtime and snapshot changes
- deterministic and fuzz testing for host placement semantics

This plan does not include the direct PySide6 runtime fix itself, except as a
conformance target.


## Roll-Build Baseline

This plan is a follow-on roll-build track.

It starts from the already completed mount-style / mutation-policy sequence,
whose latest checkpoint is:

- `roll-build-phase5-complete`

This host-surface-placement work should be executed as a new roll-build
sequence layered on top of that baseline, not as an implicit continuation of the
earlier phases.


## Success Condition

The work is successful when all of the following are true:

1. the generic backend can model a retained nested-container child occupying one
   stable slot in a parent-owned ordered host surface
2. tests can assert host placement order separately from structural graph
   retention
3. the current PySide6 nested-layout bug class can be expressed generically
4. a generic deterministic or fuzz-discovered regression would have caught the
   current failure class before the real backend test did


## Non-Goals

1. Do not model every backend host surface in the first cycle
2. Do not replace the existing real-backend conformance tests
3. Do not remove older generic tests unless the new surface clearly subsumes
   them
4. Do not broaden into unrelated visual/layout modeling beyond host placement
   ordering


## Work Breakdown

### Phase 0A: Surface Cookbook

Goal:

- document, with concrete examples, how to define and reason about the various
  testable host/mount surfaces in the backend generator

Deliverables:

1. `HostSurfacePlacementCookbook.md`
2. example generator specs for each important surface family
3. example structural snapshots
4. example host-surface placement snapshots
5. example operation logs

Minimum cookbook coverage:

1. plain ordered widget-child surface
2. nested-container child occupying one stable parent slot
3. anchor-before surface
4. keyed surface
5. sync-preferred ordered surface
6. combined structural-surface and host-surface examples

Each example should state:

- the generator-side definition
- the intended mounted-graph shape
- the intended host placement shape
- the bug family it is designed to expose

Stop/go rule:

- stop if the cookbook examples reveal that the current descriptor vocabulary is
  still too vague to define the target surfaces precisely

Completion gate:

- the cookbook covers every currently intended first-wave surface family and is
  concrete enough that an implementer could write the generator-side test
  surface without inventing new semantics during implementation


### Phase 0B: PySide6 Failure Analysis

Goal:

- document the current red PySide6 nested-layout bug precisely enough that the
  generic host-surface design can be evaluated against it

Deliverables:

1. `PySide6NestedLayoutFailureAnalysis.md`
2. authored structure for the failing scenario
3. expected structural mounted graph
4. expected host placement order
5. actual incorrect host placement order
6. gap analysis explaining why the current generic backend still misses it
7. a mapping from the real bug to the first generic host-surface profile that
   should express it

The document should be explicit about:

- stable nested child identity
- sibling churn before/after the retained child
- why structural retention and host placement drift diverge

Stop/go rule:

- stop if the analysis shows the proposed first host-surface profile still does
  not faithfully represent the red PySide6 bug class

Completion gate:

- the analysis is checked against the current red test and current runtime path
  and clearly identifies the exact generic host-surface profile that should be
  able to express the same failure class


### Phase A: Generator Surface

Goal:

- make host placement surface semantics explicit in the backend generator API

Deliverables:

1. generator-facing host-surface descriptor types
2. mount-point profile support for host-surface descriptors
3. validation rules for legal combinations
4. generated metadata exposing host-surface identity

Concrete API direction:

- add `HostSurfaceStyle`
- add `HostPlacementProfile`
- extend `MountPointProfile` to carry both

Minimum acceptance tests:

1. one logical mount can expand into multiple concrete host-surface variants
2. each concrete generated surface reports host-surface identity
3. host-surface identity does not collapse silently across variants

Stop/go rule:

- stop if the API shape cannot describe the current PySide6 nested-layout
  surface without special-casing PySide6 names directly


### Phase B: Generic Runtime Surface

Goal:

- represent host placement surfaces separately from structural mounted children

Deliverables:

1. runtime state for host surfaces
2. placement handles or equivalent stable host-slot identity
3. host-surface snapshots
4. host-surface operation logging

Required runtime concepts:

- parent-owned host surface
- surface-level allowed child kinds
- per-entry concrete child kind: widget vs nested container
- placement handle identity
- host placement order

Minimum acceptance tests:

1. structural child retention can differ from host placement movement
2. empty host surfaces are cleaned up correctly
3. host-surface snapshots remain deterministic

Stop/go rule:

- stop if the runtime model cannot represent “retained nested child, wrong host
  slot” separately from ordinary child-list reordering


### Phase C: First Concrete Surface

Goal:

- implement the smallest useful host placement surface that matches the
  unresolved bug class

Target surface:

- ordered parent host surface
- mixed child kinds in one parent surface
- one nested-container child occupies one parent slot among widget-like siblings
- nested child also owns its own internal ordered surface

Deliverables:

1. one generic host-surface profile for nested ordered container children
2. deterministic retained-slot regression tests
3. interface-validation tests for host-surface identity
4. a first red test that encodes the generic equivalent of the current PySide6
   nested-layout failure before the runtime implementation turns it green

Minimum deterministic tests:

1. branch churn before retained nested child
2. branch churn after retained nested child
3. retained nested child stays before trailing sibling
4. surface switch cleanup removes stale host placement

Stop/go rule:

- stop if this surface cannot express the current PySide6 bug shape directly

Completion gate:

- the generic equivalent of the current PySide6 bug exists as a red-to-green
  deterministic regression and is strong enough to distinguish structural
  retention from host placement order


### Phase D: Seeded Replay Fuzzing

Goal:

- extend replay-driven fuzzing from structural/mount-profile assertions to
  host-placement assertions

Deliverables:

1. seeded host-surface replay helper
2. fuzz invariant checks over host placement snapshots
3. replay artifact format including host-surface state

Required replay data:

- seed
- mount profile identity
- host surface identity
- mutation sequence
- structural snapshot
- host placement snapshot
- operation log

Minimum fuzz invariants:

1. final structural graph matches fresh render
2. final host placement order matches fresh render
3. retained nested child preserves legal host slot
4. no stale host placement entries remain

Stop/go rule:

- stop if replay artifacts are not strong enough to reproduce a discovered host
  placement failure deterministically


### Phase E: Real-Backend Conformance Link

Goal:

- prove the new generic surface meaningfully covers the real bug family

Deliverables:

1. map the existing red PySide6 regression to the generic host-surface test
   shape
2. identify any residual backend-specific behavior still not modeled
3. decide whether another generic surface class is required before the PySide6
   fix

Acceptance condition:

- the generic test shape and the real PySide6 test should fail for the same
  authored scenario class


## Detailed Task List

### 0A1. Write The Surface Cookbook

Tasks:

1. define the canonical surface examples
2. include generator-side code samples
3. include structural and host-placement expectations
4. annotate each example with the class of bug it should catch

Output:

- `HostSurfacePlacementCookbook.md`


### 0B1. Write The PySide6 Failure Analysis

Tasks:

1. capture the current failing authored structure
2. capture expected vs actual placement order
3. explain exactly where current generic coverage stops
4. define the minimal generic host-surface profile that would need to exist to
   catch the same bug

Output:

- `PySide6NestedLayoutFailureAnalysis.md`


### A1. Define Descriptor Types

Tasks:

1. add host-surface descriptor dataclasses in the generic-backend spec layer
2. document valid values and combinations
3. add validation tests

Output:

- spec-layer API patch
- focused spec validation tests


### A2. Extend Expansion Logic

Tasks:

1. make logical mount profiles expand across host-surface variants
2. ensure generated surface names and metadata stay deterministic
3. preserve the one-concrete-surface-per-runtime-contract rule

Output:

- expansion logic patch
- generator metadata tests


### B1. Add Host Surface Snapshot Types

Tasks:

1. add immutable snapshot types for host surfaces and host entries
2. extend builders to round-trip them
3. keep them separate from structural mounts

Output:

- model/builders patch
- snapshot round-trip tests


### B2. Add Host Surface Runtime Tracking

Tasks:

1. add runtime state for host surfaces
2. track placement handles for retained children
3. clean up empty/stale host surfaces correctly

Output:

- runtime patch
- cleanup/regression tests


### B3. Add Host Surface Operation Log

Tasks:

1. log host attach/detach/place/sync operations
2. keep operation order deterministic
3. ensure structural operations remain distinguishable

Output:

- operation-log patch
- legality assertion tests


### C1. Implement Nested Ordered Host Surface

Tasks:

1. model nested-container child occupying one parent slot
2. model child interior surface independently
3. preserve host-slot identity across rerenders

Output:

- concrete host-surface runtime support
- deterministic retained-slot tests


### C2. Port Current Failure Class

Tasks:

1. write the generic equivalent of:
   - conditional top sibling
   - stable nested row
   - trailing label
2. land this first as a red test before runtime changes for the host-surface
   model are made green
3. assert:
   - structural retention
   - host placement order
   - fresh-render equivalence

Output:

- canonical generic regression test for the PySide6 bug family


### D1. Extend Fuzz Replay Format

Tasks:

1. add host-surface identity to replay records
2. add host placement snapshot to replay records
3. add helper to rerun failing seed as deterministic test data

Output:

- fuzz helper patch
- replay tests


### E1. Evaluate Old Tests

Tasks:

1. compare new host-surface tests against older weaker mount-point tests
2. document which older tests are still uniquely valuable
3. deprecate only where the new surface clearly subsumes the old test

Output:

- review note or follow-up cleanup change


## Test Matrix

### Deterministic First Wave

Run each relevant scenario across:

1. widget-child host surface
2. nested-container host surface
3. ordered/index replay
4. ordered/sync-preferred policy

Minimum scenario set:

1. top-sibling removal before retained nested child
2. trailing-sibling stability after retained nested child
3. surface switch cleanup
4. no-op rerender on retained nested child


### Fuzz First Wave

Seeded fuzz should vary:

1. `show_top`
2. selected mount profile
3. selected host-surface profile
4. number of rerender steps

Keep the first fuzz cycle intentionally small and replayable.


## Verification Commands

Focused work should be verified with:

```bash
uv run --with pytest pytest tests/test_mount_point_runtime.py -q
uv run --with pytest pytest tests/test_generic_backend_mount_style_expansion.py -q
uv run --with pytest pytest tests/test_generic_backend_mount_fuzz.py -q
```

New host-surface-specific tests should get their own focused commands once
introduced.

Repo-local regression remains:

```bash
uv run --with pytest --with pytest-cov pytest -q
```

with the currently known exception that the red PySide6 regression remains red
until its runtime fix lands.


## Recommended Execution Order

1. Phase 0A
2. Phase 0B
3. Phase A
4. Phase B
5. Phase C
6. Phase D
7. Phase E
8. only then fix the real PySide6 runtime bug against the stronger generic
   contract, unless a smaller runtime fix is needed earlier for investigation


## Stop Conditions

Stop and revise if:

1. host-surface descriptors turn out not to be expressive enough for nested
   retained-container bugs
2. the runtime model cannot keep structural and placement state separate
3. replay artifacts cannot reproduce discovered failures
4. the generic host-surface model still cannot express the current PySide6 bug
   class after Phase C


## Final Note

This plan is intentionally narrower than a full layout engine simulation.

The aim is not to recreate Qt, Tk, or other backends. The aim is to model the
minimum backend-independent semantics needed to catch host placement drift when
structural mounted-graph snapshots alone are insufficient.
