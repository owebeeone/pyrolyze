# Mount Advert Plan 02: Advertise Mount Implementation

## Purpose

This plan implements the real `advertise_mount(...)` behavior on top of the
phase-1 scaffolding.

The focus here is:

- the slotted helper itself
- caller/context ownership rules
- anchor-point behavior
- ensuring the caller container context, not a leaf, is the effective advert
  mount site


## Inputs

- [01_Api_And_Mount_Restructure.md](01_Api_And_Mount_Restructure.md)
- [MountAdvertsDagBuilder.md](../MountAdvertsDagBuilder.md)


## Scope

This phase covers:

- implementing `advertise_mount(...)`
- selecting the owning surface/caller context
- publishing anchor-point adverts from container/component structure
- dynamic key mapping/renaming
- initial dependency tracking for disappearing or retargeted adverts

This phase does **not** attempt the final Hydo stress matrix. That belongs to
phase 3.


## Key Rule To Prove

`advertise_mount(...)` must attach to the caller container/component context,
not a leaf expression site.

Reason:

- adverts are anchor points in structural order
- they need child insertion semantics
- they are invalid if treated as mere leaf effects

So phase 2 should explicitly reject advert publication from a context that does
not own structural child layout.


## Required Code Changes

## 1. Implement `advertise_mount(...)`

Files:

- [src/pyrolyze/api.py](../../src/pyrolyze/api.py)
- [src/pyrolyze/runtime/context.py](../../src/pyrolyze/runtime/context.py)
- likely new advert runtime helper module

Required behavior:

- `advertise_mount(...)` is exported as a `@pyrolyze_slotted` helper
- it returns `PyrolyzeMountAdvertisementRequest`
- it accepts runtime key objects
- it supports mapping/renaming from public key to translated target selector
- it supports `default=True`

Recommended source shape:

```python
advertise_mount(name=key("first_name"), target=Qt.mounts.widget(row=0, column=0))
```


## 2. Resolve Surface Owner And Anchor Site

Files:

- [src/pyrolyze/runtime/context.py](../../src/pyrolyze/runtime/context.py)

Required behavior:

- identify the structural caller context that owns child ordering
- store the advert at that structural owner
- preserve the exact anchor position of the advert call within that owner

Invalid forms should raise clearly:

- advert from a non-structural leaf-only context
- advert with no valid enclosing structural owner

This is the main place where the implementation must be stricter than a plain
"slotted helper returns a value" model.


## 3. Route Consumers To Advert Anchors

Files:

- advert DAG builder helper
- [src/pyrolyze/backends/mountable_engine.py](../../src/pyrolyze/backends/mountable_engine.py)

Required behavior:

- resolve public advert key -> provider
- translate public key payload -> native/backend selector payload
- insert routed children at the advert anchor site
- preserve consumer order within one anchor
- allow key renaming/mapping without coupling identity to the public key name

Examples this phase should support:

- public `first_name` -> backend `widget(row=0, column=0)`
- public `type_of_day` -> backend `widget(row=0, column=1)`
- caller-passed key object chooses which advert name the provider exposes


## 4. Initial Dependency Tracking

Files:

- advert registry / binding helper
- [src/pyrolyze/runtime/context.py](../../src/pyrolyze/runtime/context.py)

Required behavior:

- record provider-slot -> consumer-directive-slot reverse dependencies
- if an advert disappears, dirty dependents
- if an advert retargets to a different provider/anchor, dirty dependents
- if an advert stays semantically the same under a renamed public key mapping,
  avoid unnecessary remount where possible

This phase does not need the full stress matrix yet, but it does need one
correct invalidation path.


## Test Plan

Target: about `14` tests.

Suggested files:

- `tests/test_advertise_mount_runtime.py`
- `tests/test_advertise_mount_context_ownership.py`
- `tests/test_advertise_mount_anchor_order.py`
- `tests/test_advertise_mount_invalidation.py`

Coverage:

- `advertise_mount(...)` publishes from a structural owner
- leaf-context advert attempts raise
- anchor ordering is correct
- public keys can be passed as function parameters
- public keys can be remapped/renamed legally across rerender
- disappearing advert dirties dependents
- retargeted advert dirties dependents
- duplicate keys still raise under dynamic rerender inputs


## Exit Criteria

- `advertise_mount(...)` works through the existing slotted-helper lowering
- caller structural context is the effective advert mount owner
- advert anchors determine ordering
- public key renaming/mapping works
- disappearing/retargeted adverts dirty dependents correctly
