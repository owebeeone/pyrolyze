# Random Program Placement Fuzz Design

## Purpose

This document defines a constrained random-program fuzzing design for PyRolyze
that can exercise:

- rerender vs fresh-render equivalence
- host-surface placement semantics
- advertised mount-point routing
- mixed widget and nested-container surfaces

The goal is not to generate arbitrary Python. The goal is to generate valid
PyRolyze components from a controlled grammar that can be compiled, rendered,
rerendered under state changes, and compared against a fresh render of the same
final state.


## Core Principle

For every generated program and mutation sequence, the primary oracle is:

```text
rerender(final state) == fresh_render(final state)
```

The compared result must include:

1. structural mounted graph
2. host-surface placement order
3. host-surface child kinds
4. optionally host-surface operation traces for debugging

This is the same correctness principle already used in earlier generic backend
work. The difference here is that the code itself is randomly generated within
defined bounds.


## Non-Goals

1. Do not generate arbitrary Python ASTs
2. Do not generate random side effects or event handlers beyond controlled state
   transitions
3. Do not let the generator invent new mount or surface semantics outside the
   supported catalog
4. Do not use randomness to avoid defining scenario families clearly


## Why Random Code Generation Is Needed

Hand-written tests found one important bug family, but they cover only the
authored scenarios we happened to think of.

The generic backend should also be able to generate many legal component shapes
that vary along:

- number of siblings
- position of the retained nested child
- number and shape of state-driven branches
- advertised mount routing
- mount style / host surface profile
- rerender mutation sequence

That is the gap this design addresses.


## Design Overview

The fuzzer should generate three things:

1. a constrained program specification
2. PyRolyze source code for that spec
3. a replayable mutation sequence over a finite state space

Then the harness should:

1. compile the generated source
2. mount initial state
3. run a sequence of state updates
4. after each step, compare rerendered output to a fresh render of the same
   final state


## Randomness Model

Randomness must be constrained on explicit dimensions. It should never be “pick
any syntax tree.”

The generator should sample from:

1. size profile
2. state profile
3. shape-function table
4. mount-routing profile
5. surface profile
6. mutation sequence

Each generated program must record all chosen dimensions in its replay artifact.


## Dimension 1: Size Profile

The generator should choose a size profile up front. This bounds the amount of
structure and the number of branch points.

Suggested initial table:

| Profile | Max top-level slots | Max nested rows | Max branch sites | Max states |
| --- | --- | --- | --- | --- |
| `tiny` | 3 | 1 | 1 | 1 |
| `small` | 5 | 1 | 2 | 2 |
| `medium` | 7 | 2 | 3 | 3 |

First implementation should start with `tiny` and `small`.


## Dimension 2: State Profile

The generator must create a finite state model with deterministic transitions.

Initial supported state kinds:

1. boolean
   - values: `False`, `True`
2. small enum
   - values: `0..n-1`, with `n <= 3`
3. bounded counter parity view
   - derived branch condition only; no unbounded numeric behavior

The generated program should define states only through a bounded table such as:

```text
state_0: bool
state_1: enum(3)
```

Mutation sequences should then choose next values from the legal domain.

This keeps replay deterministic and comparable.


## Dimension 3: Shape Function Table

The generator should not build random statements directly. It should choose from
a catalog of shape functions that each produce a known family of authored UI
shapes.

Each shape function must declare:

1. required state inputs
2. produced child kinds
3. possible structural shapes
4. compatible host surfaces
5. whether it can contain advertised mounts

### Initial Shape Function Table

#### `stable_text`

Produces one stable widget child.

Examples:

```python
text("page", "Page size: 50")
```

Properties:

- child kind: `widget`
- no state dependency
- valid in any ordered widget/mixed surface


#### `conditional_text_swap`

Produces one widget child whose content changes with state while the slot stays
occupied.

Examples:

```python
if show_top:
    text("top", "Top")
else:
    text("top", "Top changed")
```

Properties:

- child kind: `widget`
- state dependency: boolean or enum branch
- same slot count before/after


#### `conditional_text_presence`

Produces a widget child that may appear/disappear entirely.

Examples:

```python
if show_banner:
    text("banner", "Banner")
```

Properties:

- child kind: `widget`
- state dependency: boolean
- changes sibling count


#### `retained_row`

Produces one nested-container child with a stable internal shape.

Examples:

```python
with row("controls"):
    text("minus", "-")
    text("count", "Count")
    text("plus", "+")
```

Properties:

- child kind: `nested_container`
- may contain its own child surface
- central to the PySide6 bug family


#### `conditional_row_content`

Produces one retained nested row whose internal children change with state.

Examples:

```python
with row("controls"):
    if compact:
        text("count", "Count")
    else:
        text("minus", "-")
        text("count", "Count")
        text("plus", "+")
```

Properties:

- parent child kind: `nested_container`
- internal surface changes across rerenders
- useful after the first implementation wave


#### `advertised_mount_region`

Produces a region whose children are routed through `advertise_mount(...)` and
`mount(...)`.

Examples:

```python
if use_alt_surface:
    advertise_mount(BODY, target=ALT, default=True)
else:
    advertise_mount(BODY, target=MAIN, default=True)
with mount(BODY):
    text("body", "Body")
```

Properties:

- exercises advertised mount routing
- must be explicitly included because mount adverts are a separate stress area


## Dimension 4: Mount Routing Profile

The generated program must be able to exercise both direct and advertised mount
paths.

### Initial Routing Modes

1. `direct_default_mount`
   - ordinary default child mount point
2. `single_advertised_region`
   - one advertised mount target selected by state
3. `nested_advertised_region`
   - parent advert plus nested row advert

The first implementation should at minimum include:

- direct default mount
- one advertised region that can switch between two concrete mount families


## Dimension 5: Surface Profile

The generator must select a supported host-surface profile explicitly. It should
not infer this from the program structure alone.

Initial supported profiles:

1. `reference_ordered_mixed`
   - ordered parent surface
   - mixed widget + nested-container children
   - reference reconciliation
2. `buggy_ordered_mixed`
   - same authored surface contract
   - stress reconcile mode such as `stale_nested_sync_append`
3. `reference_ordered_widget_only`
   - ordered widget-only surface
4. `advertised_ordered_mixed`
   - ordered mixed surface with advertised mount routing

This lets the same generated program family run against:

- normal reference semantics
- a known bug-shaped reconcile mode
- advertised mount routing variants


## Dimension 6: Mutation Sequence

Mutation sequences should be generated separately from source generation.

Each sequence should:

1. start from a valid initial state
2. choose a bounded number of steps
3. set the full state tuple explicitly at each step
4. record every state tuple in the replay artifact

Suggested initial ranges:

- step count: `4..32`
- state tuple sampled from the product of legal state domains


## Program Specification Model

The random code generator should first produce a structured program spec, not
source text directly.

Possible direction:

```python
@dataclass(frozen=True, slots=True)
class RandomProgramSpec:
    size_profile: str
    surface_profile: str
    routing_mode: str
    states: tuple[StateSpec, ...]
    top_level_slots: tuple[SlotSpec, ...]
```

Where each `SlotSpec` chooses a shape function and its parameters, for example:

```python
SlotSpec(
    kind="conditional_text_swap",
    name="top",
    state_ref="state_0",
)
```

This spec is the real fuzz target. Source generation is a rendering step from
that spec.


## Source Generation Rules

The source generator should render a `RandomProgramSpec` into PyRolyze code
using the same backend-generator and transformed-source pipeline already used in
the generic backend tests.

Requirements:

1. deterministic formatting from the spec
2. stable generated names
3. explicit imports only from the supported generated backend module and
   `pyrolyze.api`
4. no dynamic Python features such as `eval`, computed identifiers, or random
   control flow in the generated program itself

Generated code should be boring and explicit. The randomness must live in the
spec, not in runtime behavior.


## Advertised Mount Coverage

The design must intentionally exercise advertised mount points.

### Minimum Advertised Mount Scenarios

1. switch between two concrete mount families on the same logical region
2. nested advertised mount inside a retained row
3. parent advert changes while nested child remains retained

The generated spec must be able to request:

- no adverts
- one advert region
- two advert regions

This is important because mount routing can alter which surface implementation
is actually exercised, and that is part of the testing goal.


## Initial Scenario Families

The first generator version should focus on a small table of scenario families.

### Family A: Mixed Ordered Parent, Stable Row

Shape:

```text
widget branch
widget stable
nested retained row
widget trailing
```

States:

- 1 or 2 booleans

Why:

- directly targets the PySide6 bug family


### Family B: Mixed Ordered Parent With Advert Region

Shape:

```text
widget branch
advertised body region
nested retained row
widget trailing
```

States:

- body routing selector
- one content selector

Why:

- ensures advertised mounts participate in host-surface comparisons


### Family C: Widget-Only Ordered Parent Control Family

Shape:

```text
widget branch
widget stable
widget trailing
```

Why:

- control group to distinguish mixed-surface-only failures from generic ordered
  replay bugs


## Comparison Oracle

For each generated program and each mutation step after the first:

1. run rerender to final state
2. run fresh render to final state
3. compare:
   - structural mounted state
   - host surface orders
   - host surface child kinds

When operation logs are enabled, record them for diagnostics but do not require
full equality as the primary oracle in the first implementation.


## Replay Artifact Requirements

Every failing run must emit enough information to replay deterministically.

Required fields:

1. seed
2. size profile
3. surface profile
4. routing mode
5. generated program spec
6. generated source text
7. mutation sequence
8. rerender snapshot summary
9. fresh snapshot summary
10. host-surface operation logs when available

The generated source text should be preserved because it is the easiest thing to
turn into a pinned regression test.


## Failure Classification

The harness should classify failures at least as:

1. compile failure
2. mount failure
3. rerender failure
4. structural mismatch
5. host placement mismatch
6. child-kind mismatch
7. advertised mount routing mismatch

This will help distinguish generator bugs from reconciliation bugs.


## First Implementation Plan

### Step 1

Implement `RandomProgramSpec` and a deterministic source renderer for Family A
only.

### Step 2

Add a replay harness that:

- compiles the generated source
- applies random state tuples
- compares rerender vs fresh

### Step 3

Add surface-profile selection between:

- `reference_ordered_mixed`
- `buggy_ordered_mixed`

This should be enough to show the generator can discover the same bug family.

### Step 4

Add advertised mount coverage via Family B.

### Step 5

Add replay artifact persistence and seed replay helpers.


## Stop Conditions

Stop and revise the design if any of the following happens:

1. generated programs are too unconstrained to diagnose failures
2. source generation becomes more complex than the surface semantics being
   tested
3. advertised mount routing cannot be represented cleanly in the structured
   spec
4. rerender vs fresh comparisons are not sufficient because both paths share a
   bugged implementation without an independent oracle


## Success Condition

This design is successful when the resulting system can:

1. generate replayable PyRolyze source for constrained surface families
2. vary size, state, shape, and mount-routing dimensions explicitly
3. compare rerender vs fresh placement behavior, not just structural graphs
4. expose the retained nested-row placement bug family through the generated
   surface profiles
5. produce artifacts that can be promoted into deterministic regression tests
