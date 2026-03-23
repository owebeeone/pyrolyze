# Mount Advert Plan 01: API And Mount Restructure

## Purpose

This plan establishes the runtime and API scaffolding for mount adverts and
restructures mount flattening so advert routing happens before native/local
mount resolution.

This phase is intentionally structural:

- add the public/runtime types
- keep ordinary `mount(...)` behavior stable
- split the current one-pass flattening path into:
  1. natural tree collection
  2. advert-aware routing
  3. native/local mount flattening


## Inputs

- [MountAdvertsDagBuilder.md](../MountAdvertsDagBuilder.md)
- [MountSpecImplementationPlan.md](../MountSpecImplementationPlan.md)


## Scope

This phase covers:

- public API type additions for advert selectors and advert requests
- plain-call runtime binding support for advert requests
- advert-surface registry skeleton
- DAG-builder skeleton
- restructuring the mount engine so native mount flattening happens after a
  routing phase
- regression protection for ordinary `mount(...)` without adverts

This phase does **not** complete:

- the full user-facing `advertise_mount(...)` behavior
- container-anchor selection rules
- full advert dependency invalidation
- Hydo stress verification


## Design Contract To Preserve

- no new `mount(...)` AST transform work
- `@pyrolyze_slotted` remains the preferred integration path
- ordinary `mount(...)` with no adverts must behave exactly as it does today
- provider discovery must remain natural-tree-only
- advert keys remain ordinary Python runtime values


## Required Code Changes

## 1. Public API Additions

Files:

- [src/pyrolyze/api.py](../../src/pyrolyze/api.py)

Required additions:

- `PyrolyzeMountAdvertisement`
- `PyrolyzeMountAdvertisementRequest`
- public advert-key/selector base shape
- export stubs for `advertise_mount(...)` and any helper key factory chosen for
  phase 1

Important rule:

- use `Pyrolyze...` names for the new interface/result types

Open implementation choice:

- keys may be plain objects plus helper factories
- or a dedicated `SlotSelector` subclass family

The plan should not force a string-only key API.

Red tests first:

- API exports are present
- advert request/result types are importable
- plain `mount(...)` exports stay unchanged


## 2. Plain-Call Handler Expansion

Files:

- [src/pyrolyze/runtime/context.py](../../src/pyrolyze/runtime/context.py)

Required additions:

- `PyrolyzeMountAdvertisementBinding`
- `PyrolyzeMountAdvertisementHandler`
- request staging/commit/rollback/deactivate lifecycle

Responsibilities:

- stage advert publication during pass
- publish on commit
- withdraw on deactivate
- provide a stable slot-owned identity for the advert site

Why this phase does it now:

- it proves the no-AST-change direction early
- it gives phase 2 a supported lifecycle hook instead of ad hoc state

Red tests first:

- bare `@pyrolyze_slotted` advert expression lowers/runs via `call_plain(...)`
- commit publishes a staged advert
- rollback discards staged advert
- deactivate withdraws published advert


## 3. Extract A Routing Layer Above Native Flattening

Files:

- [src/pyrolyze/backends/mountable_engine.py](../../src/pyrolyze/backends/mountable_engine.py)
- likely new runtime/backends helper module

Required restructuring:

- preserve the current natural emitted tree
- separate "which child attaches where" from "how that mount point is applied"
- move current `_flatten_child_attachments(...)` responsibilities into two
  steps:
  1. advert-aware routing
  2. native/local mount flattening

Suggested helper split:

- `build_natural_mount_inputs(...)`
- `build_mount_advert_dag(...)`
- `flatten_native_mount_attachments(...)`

This is the key refactor for later phases. Without it, advert routing remains
coupled to the immediate-parent assumption.

Red tests first:

- no-advert trees still flatten identically to current behavior
- routed-layer skeleton can pass through ordinary trees unchanged
- ordinary mount-point errors remain unchanged when adverts are absent


## 4. Surface Registry Skeleton

Files:

- likely new runtime helper module
- possibly [src/pyrolyze/runtime/context.py](../../src/pyrolyze/runtime/context.py)

Required behavior:

- registry keyed by surface owner identity
- staged vs committed advert entries
- duplicate-key validation
- duplicate-default validation

Do not overbuild phase 1:

- dependency invalidation can stay minimal here
- phase 1 just needs correct publication semantics and legality checking

Red tests first:

- one surface can publish one advert
- duplicate advertised keys raise
- duplicate defaults raise
- unvisited advert slot disappears on commit


## 5. Optional Compiler Detection Improvement

Files:

- [src/pyrolyze/compiler/kernels/v3_14/rewrite.py](../../src/pyrolyze/compiler/kernels/v3_14/rewrite.py)

This phase should not require a lowering change.

Optional improvement only:

- detect `PyrolyzeMountAdvertisementRequest` return annotations so diagnostics
  and callable-kind reporting are sharper

This stays optional because the runtime path should work through the existing
slotted-helper lowering.


## Test Plan

Target: about `14` tests.

Suggested files:

- `tests/test_mount_advert_api.py`
- `tests/test_mount_advert_binding.py`
- `tests/test_mount_advert_registry.py`
- `tests/test_mount_advert_routing_passthrough.py`

Coverage:

- API exports
- request/binding lifecycle
- duplicate key/default validation
- pass-through parity for ordinary mount trees
- regression checks for existing mount flattening


## Exit Criteria

- advert request/binding lifecycle exists and is test-covered
- mount engine has a distinct advert-routing seam
- no-advert mount behavior is unchanged
- duplicate advertised key/default errors exist
- phase 2 can implement real `advertise_mount(...)` behavior without reopening
  the flattening architecture
