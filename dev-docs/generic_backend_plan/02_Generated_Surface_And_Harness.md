# Generic Backend Plan 02: Generated Surface And Harness

## Purpose

This phase turns the core model into a usable test backend API.

The goal is to support both generated-source and direct-runtime modes, expose
real Pyrolyze callables, and provide the convenience harness needed for
rerender and advert tests.


## Inputs

- [GenericApiGenerator.md](../GenericApiGenerator.md)
- [MountExtendedTestCases.md](../MountExtendedTestCases.md)
- [01_Core_Model_And_Builders.md](01_Core_Model_And_Builders.md)


## Scope

This phase covers:

- `BuildPyroNodeBackend(...)`
- direct callable generation
- generated source module generation
- selector/helper family generation
- `backend.context(...)`
- `run_pyro_ui(...)`
- `run_pyro(...)`
- generation-aware rerender controls

This phase does **not** complete:

- the full advert-heavy matrix
- migration of existing suites
- broad adapter-shape stress permutations


## Design Contract To Preserve

- support both generated source and direct callable objects
- generated source is the default for compiler-facing tests
- the helper layer stays thin and close to real authored Pyrolyze code
- `ctx.run()` auto-increments generation by default
- `ctx.run(generation=...)` can force a specific apply generation for tests


## Required Code Changes

## 1. Add The Top-Level Backend Builder

Suggested new module:

- `src/pyrolyze/testing/generic_backend/api.py`

Required additions:

- `BuildPyroNodeBackend`
- `backend.pyro_func(name)`
- `backend.pyro_class(name)`
- `backend.selector_family(name)`
- `backend.engine(...)`
- `backend.context(...)`
- `backend.source_module_text()`

Required behavior:

- one backend spec produces all required runtime/testing artifacts
- tests can choose source mode or direct mode from one spec
- selector families are exposed where mounts require them

Red tests first:

- backend exposes all generated functions/classes
- selector helpers round-trip correctly
- source text is generated deterministically


## 2. Add Direct Runtime Callable Generation

Suggested modules:

- `src/pyrolyze/testing/generic_backend/api.py`
- `src/pyrolyze/testing/generic_backend/runtime.py`

Required behavior:

- generated functions can emit real `UIElement` values
- direct mode does not depend on codegen/import machinery
- readable annotations are preserved where practical

Red tests first:

- direct-mode `text`, `row`, and `grid` functions emit valid UI
- generated annotations are present enough for readable author usage
- direct mode and source mode describe the same backend kinds


## 3. Add Generated Source Module Support

Suggested modules:

- `src/pyrolyze/testing/generic_backend/sourcegen.py`
- optional loader helper under `src/pyrolyze/testing/generic_backend/`

Required behavior:

- generate ordinary public Pyrolyze source
- support loading through the existing compiler/testsupport path
- avoid hand-written compiler internal names in generated source

Recommended support:

- emit module text
- emit helper import prelude
- load transformed namespace for compiler-facing tests

Red tests first:

- generated source compiles
- loaded namespace exposes expected functions/classes
- source-mode output matches direct-mode output for a simple backend


## 4. Add Snapshot Helpers

Suggested modules:

- `src/pyrolyze/testing/generic_backend/snapshots.py`

Required additions:

- `run_pyro_ui(...)`
- `run_pyro(...)`

Required behavior:

- emitted-tree snapshots are normalized and immutable
- mounted snapshots are normalized and immutable
- mounted snapshots include generation
- helper output never depends on backend instance ids

Red tests first:

- identical authored trees produce identical snapshots
- mounted snapshots preserve bucket keys and order
- generation is visible in mounted snapshots


## 5. Add The Generation-Aware Harness

Suggested modules:

- `src/pyrolyze/testing/generic_backend/harness.py`

Required additions:

- `backend.context(...)`
- harness `get()`
- harness `run(generation: int | None = None)`
- harness `ui()`
- harness `graph()`
- harness `generation`

Required behavior:

- `get()` uses the current harness generation
- `run()` increments generation by `1` when no override is provided
- `run(generation=n)` uses generation `n` and updates harness state
- the harness can expose both emitted UI and mounted graph snapshots

Red tests first:

- initial generation is configurable
- default rerender increments generation
- explicit generation override works
- later auto-increment continues from the explicit value


## Test Plan

Target: about `16` tests.

Suggested files:

- `tests/test_generic_backend_api.py`
- `tests/test_generic_backend_sourcegen.py`
- `tests/test_generic_backend_snapshots.py`
- `tests/test_generic_backend_harness.py`

Coverage:

- source-mode and direct-mode parity
- callable/class/helper lookup
- snapshot normalization
- generation-aware rerender controls


## Exit Criteria

- a test can define one backend spec and obtain usable Pyrolyze callables
- both source and direct runtime modes work
- emitted-tree and mounted-graph snapshots are available
- rerender generation control is test-covered and stable
