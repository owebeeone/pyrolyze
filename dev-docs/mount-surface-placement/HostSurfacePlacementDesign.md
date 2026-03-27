# Host Surface Placement Design

## Purpose

This document defines the additional design needed to extend
`pyrolyze.testing.generic_backend` so it can model host placement surfaces
separately from structural mounted-graph retention.

This is a companion to the mount-style expansion work. It exists because the
generic backend can now validate:

- concrete mount surface identity
- mutation policy identity
- deterministic mutation-sequence behavior
- seeded replay fuzzing over mount profiles

but it still does not model one critical failure class:

- a nested container child survives structurally
- while its placement within a parent-owned host surface drifts incorrectly

That is the class currently exposed by the red PySide6 nested-layout test.


## Problem Statement

The current generic backend primarily models:

1. authored UI shape
2. mounted graph shape
3. mount bucket ordering
4. selected mount-style and mutation-policy metadata

That is strong enough to catch many classes of bugs, but not all.

The remaining gap is that real backends often have a host-owned placement
surface whose ordering semantics are distinct from the logical mounted graph.

Examples:

- a `QBoxLayout` containing widgets and nested layouts
- a parent surface where a nested child occupies one host slot but owns its own
  interior child surface
- a retained mounted child whose subtree is structurally unchanged, but whose
  host placement is detached/reinserted incorrectly when a sibling branch
  changes

In these cases, the mounted graph can still look structurally valid while the
real host placement is wrong.


## Design Goal

Extend the backend generator and generic runtime so tests can assert both:

- structural mounted graph retention
- concrete placement order within parent-owned host surfaces

The design must stay backend-independent while being strong enough to express
the current PySide6 nested-layout placement failure without relying on PySide6.


## Core Concepts

### 1. Host Surface

A host surface is a parent-owned placement surface into which mounted children
are placed.

Examples:

- an ordered widget/layout surface
- an anchor-before action surface
- a keyed host surface

This is distinct from the logical mounted graph. A node can survive in the
graph while moving incorrectly within its host surface.


### 2. Placement Handle

Each child placed into a host surface needs a stable placement identity
separate from the node identity.

This is required because:

- the node may survive structurally
- the placement slot may still be detached/reinserted incorrectly


### 3. Mounted Child Kind

The generic backend must distinguish at least:

- widget-like child
- nested-container child

The current unresolved bug is specifically about a nested-container child
occupying one parent host slot while also owning its own interior surface.

This kind must be modeled at two levels:

- what kinds a host surface allows
- what kind each concrete placed entry actually is


### 4. Surface Placement Operations

The generic backend operation model must be extended so tests can assert host
placement behavior directly.

At minimum, operations should distinguish:

- structural child retention
- host-surface attach
- host-surface detach
- host-surface place-by-index
- host-surface place-before-anchor
- host-surface sync
- host-surface replace of a retained nested child slot


## Generator API Changes

The backend generator must expose host-surface semantics explicitly instead of
implicitly assuming that mount-style semantics fully describe placement.

### New Surface-Level Descriptors

Add generator-facing descriptors that augment mount-point profiles with host
placement semantics.

Possible shape:

```python
@dataclass(frozen=True, slots=True)
class HostSurfaceStyle:
    label: str
    ordered: bool = True
    supports_anchor_before: bool = False
    keyed: bool = False


@dataclass(frozen=True, slots=True)
class HostPlacementProfile:
    label: str
    allowed_child_kinds: tuple[Literal["widget", "nested_container"], ...]
    stable_slot_identity: bool = True
    separates_structure_from_placement: bool = True
```

These are not replacements for:

- `MountStyleVariant`
- `MountPointProfile`

They are additional descriptors layered on top of them.


### Extended Mount Profile

The concrete generator-facing mount profile should eventually bundle:

- mount style
- mutation policy
- host surface style
- host placement profile

Possible direction:

```python
@dataclass(frozen=True, slots=True)
class MountPointProfile:
    label: str
    style: MountStyleVariant
    mutation_policy: MountMutationPolicy
    small_delta_threshold: int | None = None
    host_surface_style: HostSurfaceStyle | None = None
    host_placement_profile: HostPlacementProfile | None = None
```

This lets one logical mount family expand into concrete surfaces such as:

- `child_ordered_index_widget_surface`
- `child_ordered_index_mixed_surface`
- `child_sync_preferred_nested_surface`


### Why This Belongs In The Generator

If host placement behavior is not represented in the generator surface:

- tests cannot request the exact surface class under examination
- snapshots cannot report which host surface contract was active
- operation logs cannot distinguish structural and placement regressions

So the generator must emit enough concrete metadata for the runtime and tests to
know which host placement contract is active.

The generator also needs a way for generated test nodes to declare what host
placement kind they occupy when attached to a host surface. This should be a
node-level declaration, not inferred only from the surface.


## Runtime Model Changes

The generic backend runtime must gain explicit host-surface state.

### Required Runtime State

For each mounted node:

- structural mounted children
- host surfaces owned by the node
- placement handles per host surface
- current placement order within each host surface

This should be represented separately from the existing mounted graph snapshot.


### Required Snapshot Additions

The immutable snapshot surface should eventually include:

- `host_surfaces`
- `host_surface_metadata`
- `host_surface_operations`

Possible shape:

```python
@dataclass(frozen=True, slots=True)
class PyroHostSurfaceEntry:
    placement_handle: object
    child_kind: HostPlacementChildKind
    child_node: PyroNode


@dataclass(frozen=True, slots=True)
class PyroHostSurface:
    surface_name: str
    entries: tuple[PyroHostSurfaceEntry, ...]
```

The exact names can change. The key point is that this snapshot must be
parallel to, not merged into, the structural mount buckets.

This is necessary because one surface may legally contain a mix of:

- widget-like entries
- nested-container entries

The current PySide6 `QBoxLayout` failure is exactly such a mixed surface.


### Required Operation Log Additions

The operation log should distinguish:

- `structural_attach`
- `structural_detach`
- `host_attach`
- `host_detach`
- `host_place_index`
- `host_place_before`
- `host_sync`

For nested-container children, tests must be able to see:

- parent host-surface placement movement
- independent child-surface structural retention


## Minimum First Surface To Implement

Do not start by modeling every possible host surface.

The first implementation target should be the exact analogue of the current
PySide6 bug:

- ordered parent host surface
- retained nested-container child occupying one parent slot
- sibling branch churn before or after that child
- stable child subtree survives structurally
- parent-surface placement of the nested child must remain legal

This gives the smallest useful generic surface that can express the current bug
class.


## First Required Tests

### 1. Structural vs Placement Divergence

Test that the structural graph can remain stable while host placement drifts.
This should be a red/green guardrail for the new surface model itself.


### 2. Retained Nested Child Before Trailing Sibling

Model:

- conditional top sibling
- stable nested-container child
- trailing sibling

Mutate:

- remove or replace the top sibling

Assert:

- nested child remains structurally mounted
- nested child still occupies the correct host placement slot ahead of the
  trailing sibling


### 3. Surface Switch Cleanup

Switch between two concrete mount surfaces and assert:

- stale host-surface entries are removed
- structural graph and host-surface placement both converge to the selected
  surface only


### 4. Replay Promotion

The fuzz harness must be able to replay:

- seed
- mount profile
- host surface profile
- mutation sequence
- structural snapshot
- host placement snapshot
- operation log


## Relation To Existing Work

This design extends, but does not replace:

- `ContainerStyleGeneratorRequirements.md`
- `mount-style-expansion/ContainerStyleGeneratorDesign.md`
- `mount-style-expansion/ContainerStyleGeneratorTestPlan.md`

Those documents define:

- mount styles
- mutation policy
- interface validation
- policy-driven replay/sync decisions

This document adds the missing layer:

- host placement surface semantics


## Phased Implementation Suggestion

### Phase A

- add generator-facing host-surface descriptors
- expose host-surface identity metadata in generated surfaces

### Phase B

- add runtime snapshot support for host surfaces
- add host-surface operation logging

### Phase C

- implement the first nested-container ordered host surface
- add deterministic regression tests for retained-slot stability

### Phase D

- extend seeded fuzz replay to host-surface placement assertions
- promote discovered failures into deterministic regressions


## Recommended Decision

The recommended design choice is:

- keep mount style, mutation policy, and host placement surface as distinct
  layers
- make all three explicit in the backend generator surface
- add the smallest host-surface runtime model that can express the current
  PySide6 nested-layout bug before broadening to more surface classes

That gives the project a realistic path to closing the last major blind spot in
the generic backend.
