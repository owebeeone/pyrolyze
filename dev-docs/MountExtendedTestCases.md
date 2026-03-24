# Mount Extended Test Cases

## Purpose

This document defines the non-Medusa end-to-end advert and dynamic mount test
matrix for the generated backend from
[GenericApiGenerator.md](GenericApiGenerator.md).

The goal is to grow coverage in a deliberate order:

- start with the most readable authored cases
- add one new source of structural difficulty at a time
- layer generation and failure assertions onto already-readable tests
- leave the full randomized brutality to a separate design:
  [MountMedusaDesign.md](MountMedusaDesign.md)


## Why This Is Split

The old single document mixed together:

- easy narrative advert cases
- medium-difficulty rerender and compatibility cases
- the eventual randomized stress monster

That made it harder to tell what should be implemented first.

This document is now the progressive rollout plan. Medusa is separate because
it is a design problem in its own right, not just "more tests".


## Test Style

These tests should prefer the generated helper surface over raw
`UIElement(...)` construction whenever possible.

Preferred style:

```python
backend = BuildPyroNodeBackend(SPECS)

text = backend.pyro_func("text")
row = backend.pyro_func("row")
grid = backend.pyro_func("grid")
```

Assertions should use:

- `run_pyro_ui(...)` for emitted-tree assertions
- `run_pyro(...)` for mounted-graph assertions


## General Rules

- authored tests should read like ordinary Pyrolyze author code
- each stage should add only one main new difficulty at a time
- same-input rerender equality should be asserted early and often
- negative legality tests should use stable and explicit failures
- do not jump to Medusa until the staged suites below are solid


## Progressive Order

The suites below are intentionally ordered from easiest to hardest.

Treat this numbered order as the recommended roll-build phase order for the
non-Medusa mount advert test expansion.

Implementation rule:

- complete one numbered stage cleanly before opening the next
- if a stage exposes a required semantics change instead of a missing test or
  correctness bug, stop and consult rather than mutating semantics to satisfy
  the stage


### 1. Readable Narrative Routing

This is the first implementation target.

Purpose:

- prove the generated backend is readable enough to replace ad hoc scaffolds
- prove advert anchors route children to the obvious insertion site

Required cases:

- simple wrapper advert routing
- advertised default case
- two advert anchors in one container
- same-input rerender graph equality

Expected assertions:

- emitted UI anchor order is obvious
- mounted graph shows routed children in the expected place
- same logical input produces the same mounted graph on rerender

Suggested file:

- `tests/test_generic_backend_mount_advert_readable.py`


### 2. Public Key Remap Without Target Change

This is the first dynamic case because it is still easy to reason about.

Purpose:

- prove public mount naming can change without changing the translated graph

Required cases:

- rename one public key while target stays the same
- caller-provided public key object
- semantically equal key-family values recreated on rerender

Expected assertions:

- mounted graph stays unchanged when translated target stays unchanged
- no unnecessary remounts caused only by public naming changes

Suggested file:

- `tests/test_generic_backend_mount_advert_remap.py`


### 3. Keyed Rotation And Relocation

This is the first real shape-changing suite.

Purpose:

- prove keyed advert targets can move legally across rerenders
- prove no zombie routed attachments remain after relocation

Required cases:

- 2x2 grid rotation by one step
- reverse-order rotation
- equivalent rerender equality
- sparse disappearance

Expected assertions:

- pass 1 snapshot matches expected buckets
- rerender relocates only the intended buckets
- equivalent rerender preserves exact graph equality

Suggested file:

- `tests/test_generic_backend_mount_advert_rotation.py`


### 4. Multi-Param Mount Families

This stage adds mount-selector richness without adding randomization.

Purpose:

- prove the generated backend can express keyed and non-keyed selector data

Required cases:

- zero keyed params
- one keyed param
- multiple keyed params
- additional non-key value params

Examples:

- `grid_point(row, column)`
- `grid_point(row, column, colour="red")`

Expected assertions:

- keyed identity changes only when keyed params change
- non-key value changes do not masquerade as key changes

Suggested file:

- `tests/test_generic_backend_mount_selector_families.py`


### 5. Generation Visibility

Generation assertions should be added after the structural cases are readable.

Purpose:

- prove change locality, not just final shape

Required cases:

- initial render stamps generation `0` by default
- `run()` increments generation
- `run(generation=n)` override is respected
- unchanged subtree keeps its previous generation
- changed or rerouted nodes take the new generation

Suggested file:

- `tests/test_generic_backend_generation.py`

Note:

- this suite should reuse simple routing and keyed-rotation scenarios rather
  than inventing a new structural test language


### 6. Compatibility Failure Cases

This is the first intentionally negative suite.

Purpose:

- prove invalid child-to-mount connections fail deterministically

Required cases:

- exact-kind accepts valid child and rejects invalid child
- base-kind accepts subclass-compatible child
- advert-routed invalid child still fails
- compatible first pass, incompatible rerender
- optional debug mode with compatibility checks disabled

Expected failure:

- `PyrolyzeMountCompatibilityError`

Important rule:

- failure should come from the generated mount inserter path, not from vague
  incidental backend behavior

Suggested file:

- `tests/test_generic_backend_mount_compatibility.py`


### 7. Branching And Removal Churn

This is where the tree starts to become genuinely annoying.

Purpose:

- prove multiple sibling routed branches behave well under add/remove churn

Required cases:

- two sibling advertised branches
- one branch disappears while another remains
- provider disappears
- consumer subtree disappears
- reorder of sibling consumer branches

Expected assertions:

- no zombie routed children remain
- surviving branches keep stable placement
- rerender converges to the same final graph as a fresh render of that shape

Suggested file:

- `tests/test_generic_backend_mount_branching.py`


### 8. Adapter Shape Replay

This is harder because one authored test is replayed against multiple backend
shapes.

Purpose:

- prove the same logical wrapper behavior can be checked against multiple mount
  interface shapes

Required shapes:

- ordered mount backend
- keyed mount backend
- single-mount backend
- anchor-before backend

Expected assertions:

- same authored wrapper remains legal where intended
- translated mounted graph matches each backend shape's contract

Suggested file:

- `tests/test_generic_backend_mount_adapter_replay.py`


### 9. Current-Value Readback

This is last because it requires more backend behavior than pure structural
snapshot tests.

Purpose:

- prove retain-effective logic and detect over-application of writes

Required cases:

- rerender with no effective value change performs no write
- advert-driven rerender does not over-apply updates
- adapter switches do not leak stale current-value state

Suggested file:

- `tests/test_generic_backend_mount_readback.py`


## Assertion Strategy

Every suite should state explicitly which assertion level it cares about.

### Emitted Tree

Use when proving:

- anchor order
- retained advert structure
- readability of generated author code

### Mounted Graph

Use when proving:

- routed placement
- cleanup
- bucket identity
- graph equality across rerender
- per-node generation changes

### Failure

Use when proving:

- invalid child attachment is rejected
- rejection happens at the expected layer
- the raised error identifies the mount and the incompatible child kind

### Dual

Use for the most important advert suites:

- emitted tree proves structural intent
- mounted graph proves backend reality


## Snapshot Rules

Mounted graph snapshots should include:

- node kind
- generation
- args
- kwargs
- mount bucket keys
- ordered entry placement
- translated selector identity where relevant

Do not rely on `repr(...)` of mutable live backend objects.


## Rollout Advice

- implement Stage 1 fully before opening Stage 2
- add generation assertions only after the underlying structural case is
  already easy to read
- keep Medusa out of the critical path until Stages 1 through 7 are stable
- treat adapter replay and readback as later confidence multipliers, not as
  blockers for the earlier advert suites


## Future TODO: Migration

Broad test migration is still deferred.

Good later migration candidates:

- broad advert-routing tests
- dynamic rerender matrix tests
- adapter-shape stress tests

Poor migration candidates:

- narrow compiler golden tests
- tiny runtime unit tests that are clearer without a generated backend


## Bottom Line

The easy work should stay easy.

This document is the staged path:

1. readable routing
2. simple remap
3. keyed relocation
4. selector richness
5. generation assertions
6. compatibility failures
7. branching churn
8. adapter replay
9. readback

After that, use [MountMedusaDesign.md](MountMedusaDesign.md) for the genuinely
brutal randomized convergence tests.
