# Generic API Generator

## Purpose

This document proposes a generated test backend and API surface for Pyrolyze.

The goal is to make end-to-end tests cheap to author while still exercising:

- real `@pyrolyze` functions
- real compiler lowering
- real runtime/context behavior
- real mountable-engine routing and remount logic
- arbitrarily varied backend mount interfaces

The core idea is:

- define one declarative backend specification
- generate mountable classes, specs, and author-facing Pyrolyze callables from it
- run tests against either emitted `UIElement` trees or mounted backend nodes

This should become the standard "generic anything" backend for dynamic
mount/routing tests in the same way Hydo is the standard fake toolkit for
stable mountable-engine tests today.

Recommended package placement:

- `pyrolyze.testing.generic_backend`

Rationale:

- it is clearly not part of the production runtime surface
- it is still part of the packaged `pyrolyze` namespace
- it matches the existing placement of `pyrolyze.testing.hydo`
- external projects such as `grip-py` can depend on it without importing a
  name that reads as internal-only


## Motivation

Current tests split across several layers:

- compiler-only shape tests
- runtime/context tests
- mountable-engine tests
- Hydo integration tests

That is good for isolation, but it is weak when the thing being tested is
deeply cross-layer, like:

- `advertise_mount(...)`
- generated mount selector families
- dynamic routing
- rerender legality under dramatic structure changes
- adapter shape changes for one logical mount point

What is missing is a cheap way to say:

- "give me a backend with a `row`, `grid`, `text`, `widget`, `menu`, `pane`"
- "make these mount points ordered, keyed, anchor-based, or sync-preferred"
- "give me the real Pyrolyze author callables for that generated surface"
- "now run the whole thing and assert on the mounted graph"


## Design Goals

- One generator input should define:
  - mountable class shape
  - backend `UiWidgetSpec` registration
  - author-facing Pyrolyze callables
  - optional selector/key helpers
- Generated author code should stay public-surface Pyrolyze source, not
  compiler-internal `__pyr_*` code.
- Tests must be able to choose the assertion level:
  - emitted `UIElement` tree
  - mounted backend graph
  - both
- The backend must be able to model multiple mount adapter styles:
  - ordered append/place/sync
  - keyed mounts
  - anchor-before placement
  - single mounts
  - optional current-value readback
- The backend graph must be deterministic and cheap to snapshot.
- The framework must make dynamic mount API tests easier to read than the raw
  runtime scaffolding.


## Non-Goals

- This is not intended to replace Hydo completely.
- This is not a production toolkit backend.
- This is not a generic code generator for shipping user-facing UI libraries.
- The first version does not need full author-surface static typing fidelity.
- It does need mount compatibility enforcement that is strong enough for tests
  to assert that invalid child-to-mount connections fail deterministically.


## Core Model

### 1. Runtime Node Value

The generated backend should mount into a stable generic node shape.

Recommended direction:

```python
@dataclass(frozen=True, slots=True)
class PyroArgs:
    args: tuple[Any, ...] = ()
    kwargs: frozendict[str, Any] = frozendict()
```

```python
@dataclass(frozen=True, slots=True)
class PyroMountEntry:
    placement_id: object
    node: PyroNode
```

```python
@dataclass(frozen=True, slots=True)
class PyroMountBucket:
    key: PyroArgs
    values: PyroArgs
    entries: tuple[PyroMountEntry, ...] = ()
```

```python
@dataclass(frozen=True, slots=True)
class PyroNode:
    node_type: str
    generation: int
    args: tuple[Any, ...] = ()
    kwargs: frozendict[str, Any] = frozendict()
    mounts: frozendict[object, tuple[PyroMountBucket, ...]] = frozendict()
```

Notes:

- `node_type` is the generated semantic/backend kind.
- `generation` is the last apply/mutation generation for this node, not a
  global render count copied blindly onto every node.
- `args`/`kwargs` preserve constructor/state identity as authored.
- `mounts` is the normalized mounted result, not the raw backend method log.
- One mount point may have multiple buckets because keyed mounts naturally
  expand into several instances.

Recommended semantics:

- new nodes are created with the current generation
- existing nodes updated by a setter, prop apply, or mount inserter also take
  the current generation
- nodes not changed in a rerender keep their previous generation

This makes `generation` a cheap "which nodes changed in this cycle" marker for
tests.


### 2. Generated Mountable Class

Each generated class should be mutable internally so the generic
`MountableEngine` can drive it, but it should expose a deterministic snapshot as
`PyroNode`.

Recommended pattern:

- generated mountable instances keep:
  - constructor args/kwargs
  - current effective prop state
  - current `generation`
  - per-mount-point mounted children/buckets
  - optional operation log for debugging
- a `to_pyro_node()` method projects the live mutable object into immutable
  `PyroNode`

The generated mutator/inserter methods should bump `generation` whenever they
perform a real change. Pure no-op reapplication should leave `generation`
unchanged.


### 3. Generated Author Callable

For every generated kind, the generator should emit or construct a real public
Pyrolyze callable.

The author-facing shape should stay the same as ordinary library code:

```python
@pyrolyze
def row(*, gap: int = 0) -> None:
    call_native(UIElement)(kind="row", props={"gap": int(gap)})
```

The generator may create these from source strings or from ordinary Python
functions registered with `pyrolyze_component_ref(...)`.

Recommendation:

- generate real source when the test needs compiler coverage
- allow direct runtime callable construction when compiler coverage is not the
  point of that test


## Generator Input Model

### Node Specification

One `NodeGenSpec` should fully describe one generated backend/API element.

Recommended shape:

```python
@dataclass(frozen=True, slots=True)
class NodeGenSpec:
    name: str
    base_name: str | None = None
    constructor: tuple["ParamSpec", ...] = ()
    props: tuple["PropSpec", ...] = ()
    methods: tuple["MethodSpec", ...] = ()
    mounts: tuple["MountSpec", ...] = ()
    events: tuple["EventSpec", ...] = ()
```

The important rule is that one spec drives all layers:

- generated mountable class
- generated `UiWidgetSpec`
- generated Pyrolyze callable
- generated test helpers


### Parameter Specification

The generator does not need a full static type system.

It does need:

- Python annotation expression
- constructor/prop/method role
- default repr
- whether the value affects identity

And for mount compatibility, it also needs:

- a way to express accepted child class or accepted child base
- enough runtime metadata to reject invalid child attachments with a stable,
  assertable error


### Mount Specification

This is the most important part for advert and routing tests.

One logical mount point must be able to generate different backend adapter
surfaces.

Recommended mount interface enum:

- `single_mount`
- `ordered_mount_append_only`
- `ordered_mount_place_index`
- `ordered_mount_anchor_before`
- `keyed_mount`
- `sync_only`
- `sync_preferred`

Each `MountSpec` should also describe:

- accepted child kind/base
- default participation
- keyed params vs non-key params
- whether current mounted value can be read back
- whether compatibility is exact-kind or base-compatible

Compatibility is not optional in the first increment.

If a generated mount only accepts `Ctext`, then attempting to mount `Cmenu` or
`Crow` into it must fail in a deterministic and testable way. The generator
should therefore emit enough information for the generated mount inserter
methods to check eagerly and raise something like
`PyrolyzeMountCompatibilityError`.

The check should happen in the concrete mount inserter path itself:

- `add_child(...)`
- `insert_child(...)`
- `set_cell(...)`
- `set_layout(...)`
- `sync_children(...)`

That keeps failure local, immediate, and easy to reason about in tests.

Type checking may be made temporarily disableable for targeted debugging or
diagnostic runs, but the default test/backend mode should be strict checking
enabled.

Example:

```python
MountSpec(
    name="cell",
    accepted="Ctext",
    interface="keyed_mount",
    params=(
        MountParam("row", int, keyed=True, call_style="positional"),
        MountParam("column", int, keyed=True, call_style="positional"),
        MountParam("colour", str, keyed=False, call_style="keyword"),
    ),
    default=True,
)
```


## Generated Backend Surface

### Build Object

Recommended top-level builder:

```python
backend = BuildPyroNodeBackend(node_specs)
```

Expected outputs:

- `backend.mountable_specs`
- `backend.engine()`
- `backend.pyro_func(name)`
- `backend.pyro_class(name)`
- `backend.selector_family(name)` or similar helper lookup
- `backend.source_module_text()` for compiler-driven tests


### Standard Runtime Types

The generated backend module should export:

- generated node classes
- generated author callables
- generated selector helper families where requested
- snapshot helpers
- a test runner


## `run_pyro(...)`

The framework should provide a simple evaluator for test assertions.

Recommended split:

### 1. `run_pyro_ui(...)`

Input:

- emitted `UIElement` tree or render context

Output:

- normalized immutable tree suitable for source/runtime assertions

Use when:

- the test is about compiler or context behavior only


### 2. `run_pyro(...)`

Input:

- generated backend engine plus emitted root
- or a mounted root node

Output:

- `PyroNode`
- or a tuple/list of `PyroNode` roots

Use when:

- the test is about end-to-end mounting/routing behavior
- the test wants to inspect which nodes changed in a rerender


### 3. `context(...)`

The framework should expose a small test harness object for rerender-driven
tests:

```python
ctx = backend.context(component, *args, initial_generation=0, **kwargs)
first = run_pyro(ctx.get())
second = run_pyro(ctx.run().get())
third = run_pyro(ctx.run(generation=10).get())
```

Expected capabilities:

- initial render
- rerender with auto-incremented generation by default
- rerender with explicit generation override for targeted tests
- access to emitted UI
- access to mounted backend graph
- current generation introspection

Recommended API shape:

```python
ctx = backend.context(component, initial_generation=0)

ctx.generation == 0
first = ctx.get()              # applies generation 0
ctx.generation == 0

second = ctx.run()             # applies generation 1
ctx.generation == 1

third = ctx.run(generation=7)  # applies generation 7 explicitly
ctx.generation == 7

fourth = ctx.run()             # applies generation 8
ctx.generation == 8
```

This gives tests a simple default story while still allowing exact generation
control when asserting retained vs changed nodes.


## Compiler Coverage Modes

The generator should support two modes.

### Mode A: Direct Runtime Construction

Fastest.

Good for:

- engine behavior
- mount adapter replay
- graph equality


### Mode B: Generated Source Module

Generate ordinary Pyrolyze source and load it through:

- `emit_transformed_source(...)`
- `load_transformed_namespace(...)`

Good for:

- compiler/lowering coverage
- author-surface ergonomics
- ensuring generated helper signatures are valid authored Pyrolyze

Recommendation:

- the framework should make both modes available from one spec


## Mount Adapter Shapes To Support

The generator must make backend variety cheap.

Minimum set:

### Ordered Child Mount

- `add_child(child)`
- `insert_child(index, child)`
- `sync_children(children)`
- optional `detach_child(child)`


### Keyed Mount

- `set_cell(row, column, child, *, colour="red")`
- keyed args contribute to bucket identity
- non-key args remain values metadata
- child compatibility is still enforced before routing or placement


### Anchor-Before Mount

- `insert_before(anchor, child)`
- optional fallback rebuild/sync


### Single Mount

- `set_layout(layout)`
- `set_title_bar(widget)`


### Current-Value Readback

Some mounts/props should optionally expose a current-value reader so tests can
exercise retain-effective logic too.


## Suggested Internal Structure

### `PyroNodeBackendBuilder`

Consumes the declarative spec and emits:

- runtime mountable classes
- `UiWidgetSpec` registration
- author callables
- source text if requested
- compatibility validators for each generated mount surface
- strict-by-default compatibility checks wired into generated mount inserters


### `PyroNodeTestHarness`

Owns:

- a render context
- optional mounted backend engine
- current emitted tree
- current mounted graph
- current generation counter

Provides:

- `get()`
- `run(generation: int | None = None)`
- `ui()`
- `graph()`
- `generation`

Recommendation:

- `get()` uses the current harness generation
- `run()` increments generation by `1` when no override is supplied
- `run(generation=n)` sets the harness generation to `n` for that pass

Direct engine-style tests should have a matching control:

```python
engine = backend.engine(initial_generation=0)
engine.apply(root, generation=3)
```

If the real engine entry point does not accept `generation` directly, the test
backend wrapper should provide that adapter layer.


### `PyroSnapshot`

One normalized immutable snapshot layer shared by:

- `run_pyro_ui(...)`
- `run_pyro(...)`

This keeps assertions stable and readable.

Mounted snapshots should preserve `generation` by default so tests can assert
change locality directly.


## Lightweight Immutable Builder Direction

The mounted snapshot types should stay immutable.

That said, the generated backend still needs a cheap way to:

- build new nodes incrementally
- derive a mutable working copy from an existing immutable node
- commit the result back to an immutable `PyroNode`

Recommended pattern:

```python
@dataclass(slots=True)
class PyroNodeBuilder:
    node_type: str
    generation: int
    args: list[Any]
    kwargs: dict[str, Any]
    mounts: dict[object, list[PyroMountBucketBuilder]]

    def build(self) -> PyroNode:
        ...
```

```python
@dataclass(slots=True)
class PyroMountBucketBuilder:
    key: PyroArgs
    values: PyroArgs
    entries: list[PyroMountEntryBuilder]

    def build(self) -> PyroMountBucket:
        ...
```

And the immutable side should provide a lightweight bridge:

```python
builder = pyro_node.to_builder()
builder.generation = 7
updated = builder.build()
```

Why this direction:

- it keeps snapshots immutable and assertable
- it avoids mutating the immutable value in place
- it stays much lighter than introducing a full schema/buffer system
- it gives the backend a natural place to stage mount edits before freezing

The first implementation does not need elaborate copy-on-write machinery.
Straightforward `to_builder()` plus `build()` is enough.


## Relationship To Existing Test Assets

### Hydo

Hydo remains the hand-written reference fake toolkit for:

- explicit mountable behavior
- general mountable-engine confidence

The generic generator is complementary:

- Hydo is curated and semantic
- the generator is arbitrary and combinatorial


### Existing Mount Advert Tests

The intention is to migrate appropriate cases from ad hoc runtime scaffolds to
the generated backend.

That means:

- keep a small number of narrow unit tests
- move broad behavioral matrices onto the generated backend


## Recommended First Increment

Build the first version small.

### Phase 1

- ordered mounts
- keyed mounts
- single mounts
- exact-kind and base-kind mount compatibility checks
- temporary opt-out switch for compatibility checks for debugging only
- `generation` tracking on generated nodes
- harness-level generation control with auto-increment and explicit override
- source generation for simple nodes
- `run_pyro(...)`
- `run_pyro_ui(...)`


### Phase 2

- anchor-before mounts
- current-value readback
- mixed mount adapter shapes in one generated backend
- compiler-mode source generation for the full backend module


## Test Cases This Enables

With this backend generator, tests like these become cheap:

- wrapper advert routing with dynamic public keys
- grid-cell advert families rotating across rerenders
- one public mount remapped to different backend selectors
- default advert movement between anchor points
- mount adapter shape changes for the same logical public API
- mixed native and advertised mounts in one subtree
- invalid child attachment cases that must raise compatibility errors
- "which nodes changed this rerender" assertions via `generation`


## Design Decisions

### 1. Generated source vs direct callable objects

Support both.

Use generated source as the default for compiler-facing tests and direct
callable construction for narrower runtime/engine tests.


### 2. Type fidelity

Generate enough fidelity for:

- compiler annotation inference
- readable author call sites
- mount compatibility enforcement in the generated backend

Do not turn the generator into a full schema compiler.


### 3. Snapshot format

Prefer structured immutable values over repr strings.

Tests should be able to assert against:

- node kind
- args
- kwargs
- normalized mount buckets
- generation

without depending on backend instance ids.

The mutable working shape should therefore live in builder types, while the
asserted snapshot stays immutable.


## Bottom Line

The right design is one level above Hydo:

- one declarative backend spec
- generated classes/specs/callables
- one harness that can render or mount
- one normalized assertion model

That gives us a cheap way to write real Pyrolyze tests for very dynamic mount
and advert behavior without hand-building a new fake toolkit for every case.
