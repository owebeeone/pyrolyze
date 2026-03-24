# Mount Extended Test Cases

## Purpose

This document proposes a broad end-to-end test matrix for mount adverts and
related dynamic mount behavior using the generated backend from
[GenericApiGenerator.md](GenericApiGenerator.md).

The goal is to test the real mechanism with authored Pyrolyze functions rather
than only narrow runtime or engine scaffolds.


## Why This Exists

The current advert tests are good at proving:

- the slot lifecycle
- retained anchor behavior
- static-key routed mounting
- some Hydo graph stability

They are still weak at proving:

- dynamic function arguments changing mount APIs
- dynamic backend adapter changes for the same public mount
- deeply nested wrapper behavior expressed as ordinary authored code
- keyed rerender reshaping that is easy for a human to reason about
- rejection paths where the wrong child type is mounted into a constrained
  mount point
- exactly which nodes were mutated in a given rerender cycle

The generated backend should make those tests small, explicit, and cheap.


## Test Style

These tests should use the generated helper layer rather than raw
`UIElement(...)` construction wherever possible.

Preferred authored style:

```python
backend = BuildPyroNodeBackend(SPECS)

text = backend.pyro_func("text")
row = backend.pyro_func("row")
grid = backend.pyro_func("grid")

text_cls = backend.pyro_class("text")
```

Assertions should use:

- `run_pyro_ui(...)` for emitted-tree expectations
- `run_pyro(...)` for mounted backend expectations


## Core Helper Expectations

The generated framework should make these forms possible:

```python
ctx = backend.context(component, initial_generation=0)
run_pyro(ctx.get())
run_pyro(ctx.run().get())
run_pyro(ctx.run(generation=7).get())
run_pyro_ui(ctx.get())
```

And also direct mount/mountable-engine tests:

```python
engine = backend.engine()
mounted = engine.mount(run_pyro_ui(ctx.get()))
snapshot = run_pyro(mounted)
```


## Coverage Groups

### 1. Simple Wrapper Advert Routing

This is the first readability target.

Example shape:

```python
def my_mount(v: int):
    return mount_key(("my_key", v))


@pyrolyze
def fred():
    with row():
        text("hello")
        advertise_mount(name=my_mount(1), default=True)
        text("world")
        advertise_mount(name=my_mount(2))
        text("!")


@pyrolyze
def main():
    with fred():
        with mount(my_mount(1)):
            text("Mr Smith")
            text(" and Mrs Smith your")
        with mount(my_mount(2)):
            text("just changed forever")
```

Expected assertions:

- emitted UI anchor order is obvious
- mounted backend output shows routed children inserted at the two advert sites
- rerender with the same logical input produces the same graph snapshot


### 2. Dynamic Grid Rotation

This should be the signature high-variation case.

Example family:

```python
def my_mount(v: int):
    return mount_key(("cell", v))


@pyrolyze
def bob(w: int, h: int, positions=((0, 0), (0, 1), (1, 0), (1, 1))):
    with grid(w, h):
        for i, pos in keyed(enumerate(positions), key=lambda item: item[1]):
            advertise_mount(name=my_mount(i), target=grid_point(*pos))
```

Then:

- a wrapper consumes those public mounts
- a rerender rotates the `positions`
- routed children move legally without zombie state

Assertions should cover:

- first pass mounted graph
- rerender mounted graph
- exact equality for equivalent passes
- expected relocation only for changed passes


### 3. Dynamic Public Key Remapping

Tests where public keys themselves change.

Cases:

- one public key renamed while target remains the same
- one caller-chosen key object passed into the provider
- public key family values recreated each rerender but semantically equal

Expected result:

- graph unchanged when the translated target is unchanged
- no unnecessary remount when only public naming changes


### 4. Dynamic Backend Adapter Flips

One logical public mount should be able to target different backend adapter
shapes across rerenders.

Examples:

- ordered child mount -> keyed mount
- keyed mount -> single mount
- sync-preferred ordered mount -> place-by-index ordered mount

These are not realistic toolkit changes, but they are excellent stress tests.

The generator should make them possible from one spec family so that the same
authored test can be replayed against multiple backend shapes.


### 5. Multiple Keyed Params And Value Params

The backend generator must support mount points with:

- zero keyed params
- one keyed param
- multiple keyed params
- additional non-key params

Test cases should include:

- `grid_point(row, column)`
- `grid_point(row, column, colour="red")`
- one keyed param changing
- non-key value changing while key identity stays stable


### 6. Current-Value Readback

Some tests should intentionally use mount/prop shapes where the backend can
read current mounted values.

Purpose:

- prove retain-effective logic
- prove that advert-driven rerenders do not over-apply writes
- prove adapter switches do not leak stale value state


### 7. Type Compatibility Rejection

The generated backend must let tests assert mount compatibility failures.

Required cases:

- exact-kind mount accepts `text` and rejects `menu`
- base-kind mount accepts `text` and `button` because both inherit `widget`
- advert-routed mount still rejects the wrong child kind after translation
- rerender that changes provider target from compatible to incompatible fails
  deterministically

The failure should not be a vague backend crash. It should be a stable and
assertable error such as `PyrolyzeMountCompatibilityError`, raised directly by
the generated mount inserter path that received the invalid child.

Strict compatibility checking should be the default mode for the generated
backend. If the framework exposes a temporary "disable compatibility checks"
switch for debugging, that should be tested separately and should not weaken
the default behavior.


### 8. Generation Tracking

The generated backend should expose a per-node `generation` field so tests can
see which mounted nodes were actually changed in a rerender.

Required cases:

- initial render stamps all created nodes with the initial generation
- rerender without structural change only bumps nodes that actually change
- rerender with advert target movement bumps the affected parents and retained
  nodes that were rewritten
- explicit generation override on `ctx.run(generation=...)` is reflected in the
  changed nodes


## Concrete Test Matrix

### Group A: Readable Narrative Cases

These are the tests future contributors should understand first.

1. `fred/main` wrapper routing
2. simple advertised default case
3. rename-only rerender case
4. remove-one-advert keep-one-advert case


### Group B: Keyed Rotation Cases

1. 2x2 grid rotation by one step
2. 2x2 grid reverse order
3. sparse grid where one cell disappears
4. grid grows from 2x2 to 3x2
5. grid shrinks from 3x2 to 2x2


### Group C: Adapter Shape Stress

1. ordered mount backend
2. keyed backend
3. single-mount backend
4. anchor-before backend
5. same authored wrapper test run against all of the above


### Group D: Change-Heavy Cases

1. provider key changes
2. provider target changes
3. provider adapter shape changes
4. consumer order changes
5. consumer subtree disappears
6. provider disappears


### Group E: Compatibility Failures

1. direct invalid child type into constrained mount
2. advert-routed invalid child type into constrained mount
3. same public key remapped from compatible target to incompatible target
4. compatible on first pass, incompatible on rerender
5. exact-kind acceptance vs base-kind acceptance
6. debug mode with compatibility checks disabled


### Group F: Generation Visibility

1. initial render generation is `0` by default
2. rerender auto-increments to `1`
3. explicit rerender generation override to a non-sequential value
4. unchanged subtree keeps old generation
5. moved/rerouted subtree gets the new generation where mutation occurred


## Assertion Strategy

Every test should choose one or more of these assertion levels explicitly.

### Emitted Tree Assertion

Use when proving:

- anchor order
- retained `MountDirective` structure
- generated author code readability


### Mounted Graph Assertion

Use when proving:

- routed placement
- cleanup
- mount bucket identity
- graph equality across rerender
- per-node generation changes


### Failure Assertion

Use when proving:

- invalid child attachment is rejected
- rejection happens at the expected layer
- the raised error identifies the mount and the incompatible child kind
- the default strict mode crashes immediately on invalid insertion


### Dual Assertion

Use for the most important advert tests:

- emitted tree proves structural intent
- mounted graph proves backend reality


## Snapshot Shape

Mounted graph snapshots should include:

- node kind
- node generation
- args
- kwargs
- per-mount-point bucket keys
- ordered entry placement
- translated selector identity

Do not rely on reprs of mutable live backend objects.


## Example Assertions

### Wrapper Insertion

Expected mounted result should read like:

```python
{
    default: [
        (
            run_pyro(row),
            [
                text("hello"),
                text("Mr Smith"),
                text(" and Mrs Smith your"),
                text("world"),
                text("just changed forever"),
                text("!"),
            ],
        )
    ]
}
```

The exact helper syntax may differ, but the readability bar is important:

- the expected result should look like the authored layout
- not like raw runtime internals


### Rotating Grid

Pass 1:

- cell 0 in `(0, 0)`
- cell 1 in `(0, 1)`
- cell 2 in `(1, 0)`
- cell 3 in `(1, 1)`

Pass 2:

- same logical children
- new routed target buckets after rotation
- stable identity where keyed routing allows it
- generation only changes on nodes actually rewritten by the rerender


### Generation Override

Example expectation should read like:

```python
ctx = backend.context(crazy, initial_generation=10)

first = run_pyro(ctx.get())
second = run_pyro(ctx.run())
third = run_pyro(ctx.run(generation=25))
```

With assertions such as:

- first-pass nodes have generation `10`
- second-pass changed nodes have generation `11`
- unchanged retained nodes keep their previous generation
- third-pass changed nodes have generation `25`


### Compatibility Failure

Example expectation should read like:

```python
with pytest.raises(PyrolyzeMountCompatibilityError):
    run_pyro(ctx.get())
```

The important property is that the test can deliberately build an invalid graph
and assert the failure, rather than relying on incidental backend behavior.


## Future TODO: Migrate Existing Tests

This framework should eventually replace ad hoc test scaffolding where it
improves clarity, but only after the generated backend has been proven
extensively on dedicated new coverage first.

Future good migration candidates:

- broad advert-routing tests
- dynamic rerender matrix tests
- adapter-shape stress tests

Still poor migration candidates:

- narrow compiler golden tests
- tiny runtime unit tests that are clearer without a generated backend


## Recommended Rollout

### Phase 1

Add the generic backend generator with enough shapes to express:

- `text`
- `row`
- `grid`
- one keyed mount family
- one ordered mount family
- one exact-kind constrained mount
- one base-kind constrained mount
- strict-by-default inserter-side compatibility checking
- node generation stamping
- `ctx.run(generation=...)` override support


### Phase 2

Port the current advert integration tests that are already easiest to read in
author code.


### Phase 3

Add the dramatic rotation/remap/removal matrix and use it as the main advert
confidence suite.


### Phase 4

Expand the compatibility-failure matrix so dynamic remaps and rerenders are
covered alongside the positive cases.


## Risks To Watch

### 1. The helper layer becomes a DSL of its own

Keep it thin.

The generated helpers should stay close to:

- real Pyrolyze author code
- real backend mount semantics


### 2. Snapshots become too magical

Keep the snapshot format explicit and structural.


### 3. Too much migration too early

Do not rewrite every existing test immediately.

Treat migration as follow-on work after the framework has earned confidence.


## Bottom Line

The generated backend is the right place for the "crazy" tests:

- real Pyrolyze functions
- real rerenders
- dynamic keys
- dynamic mount targets
- dynamic adapter shapes

That should become the primary home for the hard advert tests, while the
existing small unit tests remain as narrow guards around individual compiler,
runtime, and mount-engine details.
