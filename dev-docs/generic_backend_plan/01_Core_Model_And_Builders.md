# Generic Backend Plan 01: Core Model And Builders

## Purpose

This phase establishes the generic backend's immutable snapshot model,
lightweight builder layer, and mount-spec compatibility machinery.

The goal is to make the backend generator real enough for end-to-end tests
without yet solving every ergonomics detail of generated author code.


## Inputs

- [GenericApiGenerator.md](../GenericApiGenerator.md)
- [MountExtendedTestCases.md](../MountExtendedTestCases.md)


## Scope

This phase covers:

- immutable snapshot types such as `PyroArgs`, `PyroMountBucket`, and
  `PyroNode`
- mutable builder counterparts such as `PyroNodeBuilder`
- generation tracking on mounted nodes
- mount compatibility metadata and inserter-side compatibility checks
- the declarative generator spec model
- a minimal backend engine wrapper that can freeze mounted state into snapshots

This phase does **not** complete:

- generated source modules
- generated public author callables
- the full test harness convenience layer
- large advert stress suites or migration of existing tests


## Design Contract To Preserve

- snapshot values remain immutable and easy to assert against
- mutable work happens in builder objects, not in the snapshot dataclasses
- compatibility failures happen in generated mount inserter paths
- strict compatibility checking is enabled by default
- generation means "last changed in this apply cycle", not merely "last
  visited"


## Required Code Changes

## 1. Add Core Snapshot Types

Suggested new module:

- `src/pyrolyze/testing/generic_backend/model.py`

Required additions:

- `PyroArgs`
- `PyroMountEntry`
- `PyroMountBucket`
- `PyroNode`

Required behavior:

- all snapshot types are immutable
- `PyroNode` includes `generation`
- snapshot equality is structural
- mounts normalize into deterministic bucket ordering

Red tests first:

- snapshot objects compare structurally
- generation participates in equality
- mount bucket ordering is deterministic


## 2. Add Builder Types

Suggested new module:

- `src/pyrolyze/testing/generic_backend/builders.py`

Required additions:

- `PyroMountEntryBuilder`
- `PyroMountBucketBuilder`
- `PyroNodeBuilder`
- `to_builder()` bridge on immutable types where useful

Required behavior:

- builders can be created from scratch
- builders can be created from existing immutable snapshots
- `build()` freezes into immutable snapshot values
- no mutation leaks back into the source immutable object

Why this phase does it now:

- it gives the generator a cheap mutable working shape
- it avoids inventing a heavier schema/buffer layer
- it makes generation-aware diff assertions possible later

Red tests first:

- `to_builder().build()` round-trips exactly
- editing a builder does not mutate the original snapshot
- builder-produced snapshots preserve normalized ordering


## 3. Add Declarative Spec Types

Suggested new module:

- `src/pyrolyze/testing/generic_backend/specs.py`

Required additions:

- `NodeGenSpec`
- `ParamSpec`
- `PropSpec`
- `MountSpec`
- `MountParam`
- mount-interface enum values

Required behavior:

- one spec fully describes one generated backend node kind
- mount specs can declare:
  - accepted child type/base
  - exact-kind vs base-compatible matching
  - keyed vs non-key params
  - default participation
  - current-value readback support

Red tests first:

- spec validation rejects duplicate node names
- spec validation rejects invalid mount param layouts
- accepted child/base metadata is preserved exactly


## 4. Add Generated Mountable Base Classes

Suggested new module:

- `src/pyrolyze/testing/generic_backend/runtime.py`

Required additions:

- a small generated-mountable base class
- strict inserter-side compatibility checks
- generation bumping when a real mutation happens

Required behavior:

- new nodes take the current generation
- real inserts/updates bump the node generation
- no-op apply paths do not bump generation
- wrong child type raises `PyrolyzeMountCompatibilityError`

Important rule:

- compatibility checking should happen in inserter/setter methods themselves,
  not in a later generic validation pass

Red tests first:

- valid child type mounts successfully
- invalid child type fails immediately
- no-op reapply leaves generation unchanged
- changed apply bumps generation


## 5. Add Minimal Engine Wrapper

Suggested new module:

- `src/pyrolyze/testing/generic_backend/engine.py`

Required additions:

- wrapper that binds generated specs to `MountableEngine`
- `initial_generation`
- explicit `generation` override on apply
- snapshot extraction helper

Required behavior:

- default apply uses current wrapper generation
- repeated apply increments generation only when asked by the harness later
- mounted roots can be frozen into `PyroNode` snapshots

Red tests first:

- initial generation is respected
- explicit generation override is respected
- frozen snapshot matches live mounted structure


## Test Plan

Target: about `18` tests.

Suggested files:

- `tests/test_generic_backend_model.py`
- `tests/test_generic_backend_builders.py`
- `tests/test_generic_backend_specs.py`
- `tests/test_generic_backend_runtime.py`

Coverage:

- immutable snapshot shape
- builder round-trip behavior
- mount spec validation
- compatibility rejection
- generation bump semantics


## Exit Criteria

- immutable snapshot and builder layers exist and are test-covered
- generated mountable runtime can enforce child compatibility
- generation tracking works for create, change, and no-op cases
- mounted state can be frozen into deterministic `PyroNode` snapshots
