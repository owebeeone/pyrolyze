# Generic Backend Plan 03: Advert Stress Suites

## Purpose

This phase uses the generated backend to build the broad advert and dynamic
mount test matrix described in [MountExtendedTestCases.md](../MountExtendedTestCases.md).

The goal is to make the generic backend prove itself on the hard,
change-heavy advert tests before any broad migration of existing suites.


## Inputs

- [GenericApiGenerator.md](../GenericApiGenerator.md)
- [MountExtendedTestCases.md](../MountExtendedTestCases.md)
- [01_Core_Model_And_Builders.md](01_Core_Model_And_Builders.md)
- [02_Generated_Surface_And_Harness.md](02_Generated_Surface_And_Harness.md)


## Scope

This phase covers:

- readable wrapper advert-routing cases
- dynamic public-key remapping cases
- dramatic keyed/grid rerender cases
- compatibility-failure cases
- generation-visibility assertions

This phase does **not** aim to:

- migrate existing suites broadly yet
- delete every existing Hydo or unit test
- replace narrow compiler golden tests
- overfit the generator to one backend-specific behavior


## Design Contract To Preserve

- broad advert tests should read like ordinary Pyrolyze author code
- the same authored test should be runnable against multiple backend shapes
- source-mode coverage should be used for compiler-facing paths
- direct-mode coverage is acceptable for focused engine/replay stress
- generation assertions should prove change locality, not just graph shape


## Required Test Work

## 1. Readable Narrative Cases

Suggested file:

- `tests/test_generic_backend_mount_advert_readable.py`

Required cases:

- `fred/main` style routed insertion
- advertised default case
- rename-only rerender case
- remove-one-advert keep-one-advert case

Red tests first:

- emitted UI anchor order
- mounted graph insertion order
- same-input rerender graph equality


## 2. Keyed Rotation And Reshape Cases

Suggested file:

- `tests/test_generic_backend_mount_advert_rotation.py`

Required cases:

- 2x2 grid rotation
- reverse-order rotation
- sparse grid disappearance
- grid growth
- grid shrink

Red tests first:

- pass-1 snapshot matches expected layout
- changed rerender relocates only the intended buckets
- equivalent rerender preserves graph equality


## 3. Dynamic Remap And Adapter Cases

Suggested file:

- `tests/test_generic_backend_mount_advert_remap.py`

Required cases:

- public key rename with stable translated target
- caller-provided key object
- one public mount remapped to different backend selectors
- one authored wrapper replayed against ordered, keyed, and single-mount
  backends

Red tests first:

- rename-only remap leaves mounted graph unchanged
- real target remap changes only the affected nodes
- adapter-shape replay stays legal


## 4. Compatibility Failure Cases

Suggested file:

- `tests/test_generic_backend_mount_compatibility.py`

Required cases:

- exact-kind accepts valid child and rejects invalid child
- base-kind accepts subclass-compatible child
- advert-routed invalid child still fails
- compatible first pass, incompatible rerender
- optional debug mode with compatibility checks disabled

Important assertion rule:

- failures should come from the generated inserter path and raise
  `PyrolyzeMountCompatibilityError`


## 5. Generation Visibility Cases

Suggested file:

- `tests/test_generic_backend_generation.py`

Required cases:

- initial render stamps generation `0` by default
- `run()` increments to `1`
- `run(generation=n)` override is respected
- unchanged retained subtree keeps prior generation
- changed or rerouted nodes take the new generation

Why this matters:

- it proves change locality
- it makes rerender bugs easier to inspect
- it gives a cheap assertion surface beyond structural equality


## Future TODO: Migrate Appropriate Existing Tests

Migration targets:

- broad advert-routing tests
- dynamic rerender matrix tests
- adapter-shape stress tests

Do not migrate:

- narrow compiler transformation golden tests
- tiny unit tests clearer without a generated backend

Migration strategy:

- add generated-backend equivalents first
- compare clarity and coverage
- then retire redundant ad hoc scaffolds only where the generated version is
  clearly better

This is deliberately out of scope for the first framework rollout. The
framework should be proven extensively on new and parallel coverage before it
starts replacing existing suites.


## Test Plan

Target: about `20` tests in the first pass, with room to expand.

Suggested files:

- `tests/test_generic_backend_mount_advert_readable.py`
- `tests/test_generic_backend_mount_advert_rotation.py`
- `tests/test_generic_backend_mount_advert_remap.py`
- `tests/test_generic_backend_mount_compatibility.py`
- `tests/test_generic_backend_generation.py`

Coverage:

- readable routed insertion
- dynamic remap behavior
- keyed rotation reshaping
- compatibility rejection
- generation-aware rerender assertions


## Exit Criteria

- the generated backend can express the "crazy" advert cases cleanly
- at least one source-mode advert suite and one direct-mode advert suite pass
- compatibility failures are asserted through the generated backend
- generation visibility is asserted in rerender-heavy cases


## Completion Note

When the framework is complete and stable enough for broader adoption, add
documentation in the appropriate checked-in docs surfaces:

- developer-facing design and maintenance notes under `dev-docs/`
- user-facing or author-facing guidance under `docs/` where applicable
