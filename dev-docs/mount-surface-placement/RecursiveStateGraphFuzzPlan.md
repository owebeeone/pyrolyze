# Recursive State Graph Fuzz Plan

## Purpose

### Current Detection Checkpoint

`tests/test_pyside6_host_surface_fuzz.py` now runs a bounded, compiler-generated
panel against the real PySide6 host. The initial seed-19 probe drove 32 states covering optional
sibling insertion/removal, sibling order reversal, and label changes around a
retained nested layout. Every state checks actual layout item order against an
independent authored-order oracle and a fresh render. Nested layout identity is
checked across updates.

Both widget-only and mixed-surface replays now require zero mismatches. Before
the fix, the mixed replay detected identically wrong fresh/incremental placement
and the retained layout moving below its trailing sibling. The production Qt
box-layout adapter now reconciles widget and nested-layout mount routes in one
physical sequence. Existing layout items and child identities are retained;
stretch/alignment parameters remain attached to their mounted children. The
original native-host regression is unchanged and passes in focused checks.

This is a bounded detection slice, not completion of this recursive fuzz plan.
The generic simulator still does not model distinct mount routes sharing one
physical surface; arbitrary recursive generation, broader mount profiles, and
replay artifact persistence remain pending.

### Seeded Program History Checkpoint

The same test module additionally generates authored program structure from a
bounded node catalog: labels, buttons, line edits, widgets, group boxes, and
horizontal/vertical layouts. Program seeds vary group order, container types,
child types/counts, and conditional block placement. Four groups expose twenty
independent boolean inputs. The compiler lowers all generated bodies.

For each program, five seeded input combinations are rendered from fresh
contexts and recorded as recursive physical-tree snapshots. A retained context
then runs up to three rounds of eight random mutations, returning to each recorded
combination after each round. Comparison includes node kinds, names, text,
hierarchy, and physical child order, but excludes object identity. No authored
expected-order oracle is used. Mismatch records retain the program seed,
mutation seed, baseline inputs, and complete preceding mutation sequence.

Two generated program seeds exercise widget-only and mixed-layout correctness. Before the
fix, the latter found history dependence with identical unordered content,
isolating placement drift. Both now require zero mismatches, without an
authored-order oracle. Narrow Qt adapter checks additionally pin stretch,
alignment, removal, and one linear item scan at 10, 100, and 1,000 children.
This bounded random-program slice does not yet generate arbitrary recursive
depths, cover every mount profile, or persist replay artifacts to disk.

For larger local runs, set `PYROLYZE_FUZZ_MULTIPLIER=10` when running
`tests/test_pyside6_host_surface_fuzz.py`. This scales placement states and
history mutation rounds while retaining five baselines per program. The default
multiplier is one to keep routine regression cost bounded. The tenfold workload
with the time limit disabled has 4,800 history mutations, 600 baseline-return comparisons, and 640 placement
state checks in the successful-only variants (6,720 renders including fresh
renders and baseline setup).

### Rollback Fault Injection

Two additional mixed-layout program cases explicitly use lifecycle-backed
completion. Every mutation round attempts changed inputs with an exception
before controls are evaluated, and another exception after all children are
evaluated. Neither failure may change committed UI or the reconciled physical
tree. A successful baseline retry must then equal the independently recorded
fresh tree. Replay histories include the fault controls, not just input flags.

At multiplier ten with the time limit disabled these cases add 600 expected failed render attempts, 2,400
successful random mutations, and 300 baseline-return comparisons. The complete
fuzz module therefore performs 10,040 render attempts, including those expected
failures. This checks rollback of render selection; it does not claim rollback
of arbitrary external Qt side effects during authored evaluation.

### Fresh Seeds and Replay

Every pytest invocation chooses a fresh master seed from system entropy by
default. Program seeds, placement inputs, and history mutations are all derived
deterministically from that master seed. Each test prints its replay settings;
pytest includes the captured output in a failure report. Set
`PYROLYZE_FUZZ_SEED` to the reported integer and use the same
`PYROLYZE_FUZZ_MULTIPLIER`, with `PYROLYZE_FUZZ_SECONDS=0`, to replay the same
deterministic sequences without machine-speed-dependent stopping. The earlier fixed seeds
were detection probes, not the final coverage policy. The narrow generator
determinism check still uses fixed inputs intentionally.

### Routine Time Budget

`PYROLYZE_FUZZ_SECONDS` defaults to two seconds for the module's mutation work,
divided among the placement/history variants. Compilation and initial fresh
baseline construction are setup and reported separately from mutation work.
Each case must complete at least one check; the budget is soft, because checks
must finish their rollback/retry or comparison before stopping. The default
multiplier-one calibration on the development machine measured 1.88 seconds of
mutation work and 14.14 seconds for standalone pytest including imports/setup.

The multiplier scales both the time allowance and maximum iteration counts.
Zero seconds disables the deadline for fixed-count stress/replay runs. Timed
runs stop at deterministic sequence prefixes and do not claim to visit every
recorded baseline. Per-case output reports actual duration and completed checks.

### Simulator Negative Control

`tests/test_generic_backend_host_surface_runtime.py` now runs the same fixed-seed
32-state replay against healthy and intentionally faulty simulator profiles.
Logical child order is compared with physical host order. The healthy profile
must report zero differences; `STALE_NESTED_SYNC_APPEND` must produce a detected
controls-after-bottom mismatch. This replaces the contradictory assertion that
fault-injected output should be correct. It does not change simulator behavior
or relax the real Qt backend's zero-mismatch correctness tests. Seed 19 is pinned
for this known-fault detector, independently of the fresh-seed Qt exploration.
The detector does not import Qt and retains its inexpensive routine coverage.

### Backend Coverage Follow-Up

Keep the real Qt fuzz coverage. Broader backend coverage remains pending:
run equivalent supported logical scenarios and seed-derived input histories
through backend-specific adapters, compare each backend with its own fresh
baseline, and compare normalized logical results where cross-backend semantics
match. Do not equate toolkit class names, unsupported capabilities, or physical
geometry. Native host checks remain necessary alongside simulator checks.

This plan defines a replayable state-graph fuzzing strategy for PyRolyze
structural rerender correctness.

The goal is to keep the backend fixed and vary only the authored state graph.

One authored recursive PyRolyze renderer should be driven from external state
so that:

- structure varies broadly
- mount shapes vary broadly
- incremental rerender paths are exercised
- each incremental result is compared against a fresh render from the same
  external state

This is meant to catch:

- retained-child replay bugs
- host-surface ordering bugs
- mount insertion/removal drift
- subtree reuse/replacement mistakes
- dirty-state routing mistakes that only appear under structural change


## Requirements

### 1. Varying structure

The fuzzed program must exercise many structural formations, not just one fixed
shape.

At minimum it should be able to generate:

- plain leaf nodes
- plain container nodes
- nested container chains
- sibling lists
- mixed leaf/container sibling groups
- optional child omission/presence
- reordered children
- stable-child plus changed-trailing-sibling cases
- retained nested-container plus trailing-sibling cases

The generator should try to cover all relevant structural patterns that can
stress replay and host-surface placement.


### 2. Varying mount types

The fuzz must exercise all supported mount types/profile combinations that the
generic backend can express.

This includes:

- ordered/index replay mounts
- sync-preferred or no-replay mounts
- nested host-surface placements
- keyed or remapped mount styles where appropriate

Constraint:

- only legal parent/child combinations may be generated
- the backend should expose compatibility information directly so the generator
  can choose legal children without exploratory rejection


### 3. Bounded recursion

The generated graph must be recursive, but bounded.

Required controls:

- maximum depth
- maximum branching factor
- optional maximum total node count

The generator must guarantee termination and keep replay artifacts small enough
to inspect.


### 4. Predictable mutation

State mutation must be small, explicit, and replayable.

Each step should apply a small mutation such as:

- toggle one optional node
- change one node kind within a legal family
- swap one mount profile
- rename one leaf payload
- insert/remove one child
- move one child within siblings
- replace one subtree root with another legal node kind

The mutation policy should prefer local changes so that rerender locality is
actually exercised.


### 5. External state is the source of truth

The recursive PyRolyze renderer should read from external state rather than
owning the structure internally.

That state must live outside the authored PyRolyze code so the harness can:

- mutate it directly
- rerender incrementally
- create a fresh render from the exact same state

This is the core correctness principle:

- one state
- two render paths
- same result


### 6. Fresh-vs-incremental equivalence

After each mutation:

1. rerender the existing retained graph incrementally
2. render a fresh graph from the same current external state
3. compare them

Required comparisons:

- emitted `UIElement` tree
- generic-backend structural snapshot
- generic-backend mounted graph
- host-surface order snapshot
- host-surface child-kind snapshot

If generations are included in the comparison, the harness must compare them
using the intended locality rules rather than requiring literal equality across
fresh and rerender paths.


### 7. Size scaling

The same design must run at multiple sizes.

Suggested scales:

- tiny: depth 1-2, low branching
- medium: depth 3-4, moderate branching
- larger: depth 4-6 with bounded node count

This should allow:

- cheap deterministic CI coverage
- deeper local stress runs


### 8. Coverage of all mount profiles

The suite should eventually exercise all supported mount profiles, not just the
default ordered profile.

The harness must therefore be able to:

- enumerate available legal parent mount profiles
- choose among them during generation
- record the chosen profile in the replay artifact


## Core Design

## 1. Fixed backend, generated state

Do not randomize the backend structure.

Instead:

- define one intentionally rich generic backend
- make that backend expose all supported mount/profile families
- make the generated program vary only its external state/descriptor graph

Then use one fixed recursive PyRolyze renderer to interpret that state.

Why:

- replay is simpler
- failing artifacts are smaller
- debugging is easier
- legality filtering is easier
- extending coverage for new mount types is easier
- slot/dirt/runtime behavior is still exercised


## 2. One canonical backend capability matrix

The backend should be designed once and reused.

It should provide:

- a small set of node kinds
  - plain leaves
  - plain containers
  - nested-container-capable nodes
- all important mount profiles
- explicit compatibility information for which child kinds each mount accepts

The backend should be extensible:

- when a new mount type/profile is added
- add it here once
- the fuzz harness then gains access to it automatically

This is better than generating a random backend because:

- test failures remain interpretable
- compatibility rules stay explicit
- replay artifacts stay stable across time


## 3. One recursive authored renderer

The fuzz target should be a small authored PyRolyze program that recursively
renders nodes from external state.

Conceptually:

- one recursive component renders one node descriptor
- external-store or state-driven lookups determine:
  - node kind
  - payload
  - mount profile selection
  - children

This renderer may use:

- ordinary direct component calls
- `with` container calls
- keyed loops where needed
- mount/advert forms where needed

Each call site must have stable identity derived from the descriptor/node id.


## 4. Descriptor model

The external state should contain a recursive descriptor graph.

Suggested descriptor fields:

- `node_id`
- `node_kind`
- `payload`
- `children`
- `mount_profile`
- `enabled`
- optional `key`

The descriptor model should be legal-by-construction:

- parent kind determines allowed child families
- mount profile determines allowed placement surface
- node kind determines whether the renderer emits leaf or container structure


## 5. Stable identity

Every generated call site must be backed by a stable descriptor identity.

Required sources of identity:

- `node_id` for the recursive node itself
- child keys for child iteration when keyed structure is used
- stable mount profile labels for profile selection

This is necessary so the retained rerender path is actually meaningful.


## 6. Mutation model

A replay artifact should contain:

- initial descriptor/state
- an ordered list of small mutations

Each mutation should be one operation from a constrained set:

- `toggle_enabled(node_id)`
- `replace_payload(node_id, payload)`
- `replace_kind(node_id, new_kind)`
- `insert_child(parent_id, index, descriptor)`
- `remove_child(parent_id, child_id)`
- `move_child(parent_id, from_index, to_index)`
- `replace_subtree(node_id, descriptor)`
- `change_mount_profile(node_id, profile_label)`

Mutations must preserve legality.


## 7. Comparison surface

Each step should produce two snapshots:

- `rerendered`
- `fresh`

Required equality surfaces:

- normalized emitted tree
- normalized mounted graph
- host-surface order map
- host-surface child-kind map

Optional additional assertions:

- changed nodes receive new generation
- unchanged retained subtrees preserve prior generation


## Harness Design

## 1. Replay artifact

Every run must emit enough data to replay deterministically:

- seed
- backend/module name
- initial descriptor tree
- mutation list
- size limits


## 2. Execution loop

For one replay:

1. build backend/profile set
2. create initial descriptor/state
3. render once and keep retained context
4. for each mutation:
   - apply mutation to the external state
   - rerender retained context
   - render fresh from the same new state
   - compare snapshots


## 3. Size matrix

Each replay family should run over multiple bounded size settings.

Suggested matrix:

- shallow ordered
- shallow nested-host-surface
- medium mixed profile
- deeper mixed profile


## 4. Mount-profile matrix

The harness should be able to iterate the same descriptor/mutation design over:

- all ordered profiles
- all sync/no-replay profiles
- all nested-container host-surface profiles
- later, keyed/anchor-before families where supported


## Test Utility Support

The state-driving helpers should be shared.

`tests/external_store_test_utils.py` already exists and should likely be
expanded rather than bypassed.

Useful shared helpers here are:

- named/keyed external stores
- subscribe/get/unsubscribe logging
- state mutation helpers
- replay-friendly store setup

The fuzz harness should not duplicate ad hoc store scaffolding across tests.


## Proposed Test Layers

### Layer A: Deterministic narrative regressions

Keep explicit small tests for known bugs.

Examples:

- retained nested container above trailing sibling
- nested row above trailing label


### Layer B: Seeded descriptor fuzz

Add deterministic seeded fuzz using the recursive descriptor model.

This is the main replay-vs-fresh equivalence layer.


### Layer C: Profile cross-product replay

Replay the same descriptor/mutation artifact across multiple legal mount
profiles where possible.

This proves the generator is not overfit to one host-surface style.


## First Implementation Slice

Start with the minimum version that can catch the current failures.

### Slice 1

- one canonical backend with:
  - leaf kinds
  - container kinds
  - nested-container host-surface profile
  - at least one alternate mount profile
- recursive descriptor model with:
  - leaf nodes
  - container nodes
  - nested container children
  - trailing leaf siblings
- the current failing nested-container host-surface profile
- small mutation set:
  - toggle payload
  - insert/remove child
  - nested-container retention with sibling changes
- rerender-vs-fresh comparison of:
  - mounted graph
  - host-surface order
  - host-surface child kinds

This slice should be able to reproduce the existing:

- generic backend nested-container order bug
- PySide6 nested-layout order bug


### Slice 2

- add alternate mount profiles
- add mount-profile mutation
- add keyed child cases


### Slice 3

- add broader random subtree replacement
- add larger depth/branching runs
- add replay artifact persistence helpers


## Tk History Replay Checkpoint

`tests/test_tkinter_host_surface_fuzz.py` runs an isolated Tk worker to avoid
mixing Tk and Qt GUI stacks on macOS. Two seeded authored programs vary group
order, pack direction, label/button kinds, and twenty conditional nodes. Five
fresh baselines per program are compared with restored states after random
mutations. Mid-tree and post-tree exceptions verify lifecycle rollback leaves
accepted UI and physical placement unchanged before a successful retry.

The worker snapshots toolkit classes, text, and physical `pack_slaves()` order,
not Tcl-generated object paths. It uses the same seed, multiplier, and soft
mutation-time budget environment settings as Qt and prints replay settings
before executing. This checkpoint covers pack layouts; grid, notebook, and
cross-backend logical equivalence remain future coverage. DearPyGui is deferred.

## Exit Criteria

This plan is successful when:

- one recursive authored PyRolyze renderer can express many legal structures
- small mutations can be applied replayably
- each incremental rerender is checked against a fresh render from the same
  state
- the matrix covers all important mount profiles
- known host-surface placement bugs are either caught directly or reproduced by
  deterministic replay artifacts from this harness
