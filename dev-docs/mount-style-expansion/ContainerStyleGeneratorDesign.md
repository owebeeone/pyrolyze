# Container Style Generator Design

## Purpose

This document defines the design for expanding
`pyrolyze.testing.generic_backend` into a stronger mount-style test platform.

This is primarily a test-design document. It covers:

- the backend API generator surface changes
- the mount-style model we need
- how deterministic mutation-sequence tests should be expressed
- how Monte Carlo fuzzing should fit into the same platform
- how to avoid the testing gaps exposed by the current PySide6 regression

This document does not implement the fix for the current PySide6 bug. The red
PySide6 test should remain red until the generic surface and the runtime fix are
both ready.


## Problem Recap

We have a real backend failure where a stable nested ordered surface is
misplaced after sibling branch churn.

The generic backend did not catch it because:

1. it currently verifies graph/mount shape better than placement semantics
2. it does not yet expose all supported mount-style behavior strongly enough
3. it does not yet make mutation sequence a first-class assertion surface
4. it does not yet provide the operation-level traces needed to diagnose
   placement drift

This is not just one missing test. It is a missing test surface.


## Existing Relevant Surface

The existing generic backend already has some of the needed style axes:

- `MountSpec.interface`
  - `ORDERED`
  - `SINGLE`
  - `KEYED`
- `MountSpec.replay_kind`
  - includes support such as `MountReplayKind.ANCHOR_BEFORE`
- `MountSpec.prefer_sync`
  - already represents one mutation-policy dimension

These are real signals that the design intended multiple mount styles already.

At the moment, though, those knobs are only partially reflected in test power.
They do not yet produce a sufficiently rich platform for mutation-sequence and
placement-contract testing.


## Design Goals

1. Reuse the existing style axes where they already express real semantics.
2. Expand the generic backend without replacing its current readable source-mode
   and direct-mode usage.
3. Make mount style explicit and assertable.
4. Make mutation sequence a primary test object.
5. Support a deterministic test suite first.
6. Add Monte Carlo fuzzing on top of the same model, not as a parallel ad hoc
   system.
7. Keep the platform backend-independent while still leaving room for real
   backend conformance tests.


## Design Principle

We should not model mount style as a vague “bag of behavior.”

A mount surface must still declare one concrete operational contract for a given
generated mount point. Tests must be able to tell which contract is active.

At the same time, one generated backend interface should be able to expose
multiple mount surfaces, each with its own concrete style, so that the same
authored scenario can be replayed across styles.


## Recommendation: Singular Per Mount, Set Per Generated Interface

### Short answer

- Do **not** make one mount point’s style parameter a set.
- Do allow the **generator input** to request a set of mount-style variants so
  one generated interface can expose multiple concrete mount surfaces.

### Reasoning

If a single mount point carries a set of styles at runtime, the contract becomes
ambiguous:

- tests cannot prove which style was exercised
- operation logs become hard to interpret
- silent fallback becomes easier
- regressions can hide behind “still legal under some style”

That is the opposite of what we need.

Instead:

1. each generated mount point should still have one concrete style
2. the generator should be able to create several variant mount points or
   variant node specs from one source request
3. tests can then replay the same authored scenario against each concrete style

This keeps the contract precise while still enabling a matrix.


## Proposed API Direction

### Keep these existing fields

- `MountSpec.interface`
- `MountSpec.replay_kind`
- `MountSpec.prefer_sync`

These should remain the low-level concrete contract fields that describe one
generated mount surface.

### Add a higher-level style-expansion input

Add a generator-facing way to request multiple mount-style variants from one
logical mount description, plus mount-point profiles that bind concrete policy
to each generated surface.

This should live at the backend-builder/spec layer, not as an overloaded runtime
meaning for one mount point.

Possible shape:

```python
@dataclass(frozen=True, slots=True)
class MountStyleVariant:
    label: str
    interface: MountInterfaceKind
    replay_kind: MountReplayKind
    prefer_sync: bool = False


@dataclass(frozen=True, slots=True)
class MountPointProfile:
    label: str
    style: MountStyleVariant
    mutation_policy: str
    small_delta_threshold: int | None = None
```

And a generator expansion input such as:

```python
@dataclass(frozen=True, slots=True)
class MountVariantSpec:
    name: str
    accepted_kind: str | None = None
    accepted_base: str | None = None
    params: tuple[MountParam, ...] = ()
    default: bool = False
    profiles: tuple[MountPointProfile, ...] = ()
```

Or an equivalent builder API that expands one logical mount into many concrete
mounts.

The important idea is not the exact class name. The important part is the level:

- style expansion request at generation time
- concrete mount style at runtime


## Expansion Behavior

When the generator receives a style-expanded mount request, it should emit one
concrete mount surface per style variant.

Example:

- logical mount family: `child`
- concrete mount-point profiles:
  - ordered/index with place-only policy
  - ordered/anchor-before with anchor-preserving policy
  - ordered/none with sync-preferred policy
  - single
  - keyed

The generated backend interface might then expose concrete surfaces like:

- `child_ordered_index`
- `child_ordered_anchor`
- `child_sync_preferred`
- `child_single`
- `child_keyed`

or an equivalent grouping with explicit variant metadata.

The exact naming can be refined later, but the generated surface must satisfy:

1. each concrete mount point is unambiguous
2. tests can ask which style was used
3. operation logs can be verified against the chosen style


## Interface Requirement For Later Testing

When we get to testing this, the generated interface should support all relevant
styles in one testable surface.

The test must be able to assert:

1. the scenario ran against the intended style
2. only that style was exercised
3. no silent fallback style handled the mount

This is important enough to restate explicitly because it protects against the
generic backend “passing” while routing behavior through the wrong surface.


## Style Identity Requirement

Each concrete mount surface should carry explicit style identity metadata.

At minimum, the generic backend should expose:

- mount-point profile label
- style label
- mount interface kind
- replay kind
- prefer-sync flag
- any future policy knobs required to distinguish legal mutation behavior

This metadata must be available to:

- deterministic tests
- fuzz result records
- snapshot helpers
- operation log assertions


## Operation Log Expansion

The generic backend currently snapshots mounted graph state, but for this work
we need a richer operation trace.

The trace should capture at least:

- mount style identity
- create
- attach
- append
- place-by-index
- place-before-anchor
- sync
- detach
- replace
- keyed set/update/remove
- rollback restore
- no-op replay

This should be represented in a deterministic, snapshot-friendly form.


## Deterministic Mutation-Sequence Test Surface

The first implementation cycle should focus on a small, strong deterministic
suite that uses the expanded mount-style surface.

Required scenario family:

1. conditional sibling replacement before a stable retained child
2. conditional sibling replacement after a stable retained child
3. remove-one-preserve-one sibling churn
4. reorder surviving siblings
5. nested ordered surface retained across sibling churn
6. replace-one-preserve-one with trailing sibling stability
7. rollback restoring prior placement
8. same-final-shape rerender equivalence

Required assertions:

- final graph shape
- placement order
- operation log legality
- survivor stability
- no duplicates
- no zombies
- generation locality


## Monte Carlo Fuzzer Design

The fuzzer should be layered on top of the same concrete mount-style model.
Its configuration should be mount-point based, not backend-wide.

The unit under fuzz should be a concrete mount point or mount-point profile,
for example:

- `tkinter.Frame.pack`
- `tkinter.Frame.grid`
- `tkinter.PanedWindow.pane`
- a generated generic-backend mount-point variant representing the same surface

It should vary:

- mount-point identity
- mount style
- mutation sequence
- branch toggles
- insertion/removal positions
- nested surface structure
- keyed values
- rollback injection
- policy variation

The fuzzer must not be toolkit-specific. It should operate on the same generic
container-style platform as the deterministic tests.

The fuzzer configuration should therefore attach to mount-point profiles and
declare:

- the concrete mount-point identity under test
- style and replay contract
- mutation-policy knobs and thresholds
- legal mutation operations
- weighted operation distributions
- invariants required for that mount point

Every failing run must be replayable using:

- seed
- mount-point identity
- mount style identity
- policy identity
- authored initial state
- mutation sequence
- graph snapshot
- operation log


## Policy Layer

We also need to acknowledge that some behaviors may vary by backend learnings,
API learnings, or churn volume.

That means the platform must eventually support a policy layer distinct from
style identity.

Suggested split:

- style = structural mount contract
- policy = mutation strategy under that contract
- mount-point profile = a named concrete surface bundling mount-point identity,
  style, and policy for testing and generation

Examples:

- ordered/index with sync-preferred policy
- ordered/index with place-only policy
- ordered/anchor-before with anchor-preserving policy
- rollback via snapshot/restore
- rollback via old-state reapply
- `tkinter.Frame.pack` as ordered child-geometry plus sync-preferred,
  churn-sensitive policy
- `tkinter.PanedWindow.pane` as ordered/index replay with a different policy

This distinction is important because style should remain concrete and
assertable, while policy can vary independently.


## Relationship To Existing Generic Backend Tests

The current generic backend tests remain useful, but they are not enough.

They should continue to cover:

- basic source-mode generation
- basic direct-mode behavior
- selector family behavior
- broad advert routing
- compatibility failures
- generation visibility

The new mutation-style test surface should be added in parallel rather than
trying to force these existing tests to absorb all new complexity immediately.


## Relationship To Existing Real-Backend Tests

The existing red PySide6 regression remains the real-backend proof that the bug
exists.

The new generic style-expansion surface should produce a backend-independent
parallel regression for the same behavioral class.

Long term, the intended layering is:

1. generic deterministic mutation-sequence tests
2. generic Monte Carlo fuzzing
3. selected real-backend conformance tests for high-value scenarios and fuzz
   seeds


## Why Older Tests Missed This

The current failure likely slipped through because the earlier tests covered:

- broad ordered-mount legality
- graph shape
- some rerender behavior

But they did not strongly model:

- nested ordered surfaces
- stable retained child placement under sibling branch churn
- style identity verification
- operation-level placement assertions

This design explicitly addresses those gaps.


## Phasing

The requirements surface is broad, but the implementation should be phased.

### Phase 1

- reuse existing low-level fields
- add style-expansion request surface at generation time
- add mount-point profile / policy-facing API surface at generation time
- emit multiple concrete style variants
- expose style identity metadata
- expose policy/profile identity metadata

### Phase 2

- add deterministic mutation-sequence tests
- add operation-log assertions
- add interface-validation tests proving only the intended concrete surface is exercised
- reproduce current failure class generically

### Phase 3

- add rollback variants
- implement policy variation behavior behind the Phase 1 API

### Phase 4

- add Monte Carlo fuzzer over concrete mount-point profiles
- add seed replay

### Phase 5

- compare against older weaker mount-point tests
- deprecate only where a stronger replacement clearly subsumes them


## Recommended Decision

The recommended design choice is:

- keep concrete mount style singular per generated mount surface
- add a generation-time expansion mechanism that accepts multiple style variants
- treat policy as a parallel axis, not as style ambiguity

So the answer to the open question is:

Do we make that parameter a set?

- For one concrete mount surface: **no**
- For the generator request that expands into multiple concrete surfaces:
  **yes**

That gives us precision, replayability, and a real matrix without turning one
mount contract into an ambiguous union.
