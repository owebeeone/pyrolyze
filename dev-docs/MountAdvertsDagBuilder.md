# Mount Adverts DAG Builder

## Purpose

This document proposes a runtime design for `advertise_mount(...)`.

The goal is to let a component or wrapper expose a public mount surface that
forwards into one of its descendants, including dynamic and parameterized
families such as:

- `cell(row, column)`
- `corner(corner=...)`
- `pane(index=...)`

The motivating shape is the example in `scratch/advertise_mount_example.py`:

- an inner component advertises mounts
- an outer component consumes some of them and may re-advertise others
- authored `mount(...)` stays the user-facing selection mechanism

The design target here is:

- no new `mount(...)` AST transform work
- slot-backed lifecycle for advertisements
- dynamic advertised mount families
- deterministic teardown when an advertised mount disappears
- explicit invalidation of dependents when cross-mount routing changes
- fully dynamic rerun legality: advertised keys, defaults, and mappings may
  change across rerenders as long as the resulting surface is legal for that
  pass


## Requirements And Motivation

### 1. Mount API Normalization

Different libraries expose different mount names.

`advertise_mount(...)` should let a Pyrolyze component normalize those names so
that authored code can target one public key while the implementation maps that
key to the native/backend selector it actually uses.


### 2. Architectural Assist

If multiple implementation variants expose the same public advertised keys, a
caller can swap them in and out without changing outer `mount(...)` usage.

That makes advertised mounts a composition tool, not just a forwarding trick.


### 3. Parameter Drilling Minimization

If slots/mounts are advertised directly by the builder, callers do not need
mount-shaping parameters drilled through every intermediate layer.

Those parameters stay in the scope that actually owns the layout/build
decision.


## Current Reality

Today the mount runtime assumes:

- `mount(...)` lowers to retained `MountDirective`
- explicit mount selection is resolved against the immediate parent
- `_flatten_child_attachments(...)` resolves selectors too early for any
  descendant-forwarding scheme
- component boundaries do not survive as first-class emitted nodes; the emitted
  tree is still mostly `UIElement | MountDirective`

That means `advertise_mount(...)` cannot be implemented as "ambient mount state
can see through descendants." The runtime needs one more structural pass before
ordinary native mount flattening.

The good news is that the runtime already has most of the lifecycle machinery:

- `@pyrolyze_slotted` expression calls already lower to `call_plain(...)`
- plain-call slots can receive `PlainCallRuntimeContext`
- plain-call bindings already support `commit()`, `rollback()`, and
  `deactivate()`
- unvisited slots already deactivate automatically at commit time
- the scheduler already has an invalidation path that can dirty a slot, its
  ancestor contexts, and its owner boundary

So the missing piece is not "invent a second mount system." The missing piece
is a DAG-building pass plus a binding/registry layer for advertised surfaces.


## Core Model

### Natural Tree

The natural tree is the emitted tree before any advertised-mount routing is
applied.

It is the only tree that may be used to discover advertisement providers.

This constraint matters. It is what keeps the routing graph acyclic.


### Advertised Surface

An advertised surface is a public mount API exposed by one source-level
component/container boundary.

Each surface contains:

- zero or more advertised selector families
- at most one advertised default
- one unique provider per public advertised key/family

The advertised surface is dynamic across rerenders.

The keys themselves are runtime Python values:

- they may be passed as function parameters
- they may be produced by key factories
- they may change across rerenders


### Consumer

A consumer is an existing `MountDirective` whose selector list includes one or
more advertised selectors.

Example:

```python
with mount(cell(row=0, column=1), default):
    CQPushButton("Top Right")
```


### Provider

A provider is an `advertise_mount(...)` slot that exposes one public selector
family and translates it into an inner/native selector on a strict natural
descendant.

It is also an anchor point.

Routed children are inserted at the advertisement site, not merely "somewhere
inside the descendant target."


### DAG Edge

A DAG edge is a routed attachment from a consumer subtree to a provider's
natural descendant target.

The node still has:

- one natural parent in the natural tree
- one mounted parent after routing

The mounted parent may differ from the natural parent.


## Proposed Public Shape

The public authored shape should remain ordinary Python plus existing
`mount(...)`.

Recommended direction:

```python
with CQGridLayout(w=2, h=2):
    advertise_mount(
        name=cell(row=0, column=0),
        target=Qt.mounts.widget(row=0, column=0),
        default=True,
    )
```

Important points:

- Public advertised keys should not be raw native `MountSelector` names.
- They should be their own runtime selector/key family, for example via
  `mount_key(...)`, `key(...)`, or a generated selector factory.
- Reusing raw native selector names would create ambiguous resolution between
  "advertised public mount" and "immediate native mount on the current parent."

So phase 1 should use a distinct advertised-selector family, even if it is just
another `SlotSelector` subclass.

The public key should also be renameable/mappable.

That is one of the core values of the feature:

- wrapper public key `first_name`
- mapped to implementation selector `Qt.mounts.widget(row=0, column=0)`


## Is A Slotted Helper Enough?

Yes, but only if it returns a new plain-call semantics object.

No, if it returns only a plain data object and expects the runtime to notice it
magically.

Recommended shape:

```python
@pyrolyze_slotted
def advertise_mount(
    name: object,
    *,
    target: SlotSelector | None = None,
    default: bool = False,
    ctx: PlainCallRuntimeContext,
) -> PyrolyzeMountAdvertisementRequest:
    ...
```

This is enough to avoid AST transform changes because:

- bare slotted helper expressions already lower through `call_plain(...)`
- `call_plain(...)` already supports runtime-context injection through
  `PlainCallRuntimeContext`
- the plain-call layer already supports custom binding behavior by adding a new
  result type and a new semantics handler

So the runtime addition is:

- `PyrolyzeMountAdvertisementRequest`
- `PyrolyzeMountAdvertisementBinding`
- `PyrolyzeMountAdvertisementHandler`

`PyrolyzeMountAdvertisementRequest` is the better shape than a plain
`PyrolyzeMountAdvertisement` value because the binding needs lifecycle hooks:

- `commit()` to publish the surface entry
- `rollback()` to discard staged changes
- `deactivate()` to unregister the advertisement and dirty dependents

The runtime context is useful for:

- stable slot identity
- local storage
- explicit invalidation
- a surface-owner identity derived from the current slot and owner boundary

So the answer to "is a slotted function enough?" is:

- yes for syntax/lowering
- no if it only returns plain inert data
- yes if it returns a new request/binding type handled by `call_plain(...)`


## DAG Builder

### Why A New Pass Is Needed

Current native flattening resolves selectors against one immediate parent.

That is too early for advertised routing because a consumer may need to attach
to a strict descendant provider, not the immediate parent mountable.

So the runtime needs:

1. collect committed advertisements for the natural subtree
2. resolve advertised selectors against that collected surface
3. build routed edges from consumers to providers
4. only then perform ordinary local/native mount flattening


### Output Shape

The builder does not need to expose a user-visible graph type.

Internally it should produce something equivalent to:

- a routed child assignment per consumer subtree
- a concrete mounted parent node
- a translated native selector on that mounted parent
- an advertisement anchor site on that mounted parent subtree
- dependency edges from provider slots to consumer directive slots

After that, the existing mount engine can continue to work on local/native
mount points.


### Recommended Build Rule

The builder must freeze provider discovery against the natural tree only.

That means:

- collect providers from the unre-routed subtree
- do not let provider lookup see nodes that only become reachable through an
  already-routed advertised edge

This is the key acyclicity rule.


## Why Cycles Do Not Appear

There is a valid acyclicity argument here, but it depends on one constraint.

Let:

- `T` be the natural emitted tree before advertised routing
- every provider target be a strict descendant in `T` of the surface that
  advertises it
- provider lookup operate only on `T`, never on already-routed output

Then:

- every natural edge goes from a node to a strict natural descendant
- every advertised edge also goes from a consumer site to a strict natural
  descendant in `T`
- natural depth strictly increases along every edge

So a cycle is impossible.

### Blind Spot In The Informal Argument

The informal "it always branches downward" argument is not strong enough by
itself.

The actual requirement is stronger:

- advertised targets must be chosen from the natural tree only

If the builder is allowed to resolve providers from already-routed output, the
proof breaks.

So the DAG claim is sound, but only under the natural-tree-only provider rule.


## Legality Rules

The runtime should enforce these rules explicitly.

### Duplicate Public Keys Are Illegal

Within one advertised surface:

- the same public advertised key/family may not be published from two
  different sites
- this should be a hard runtime error
- this should behave like duplicate function parameter names, not last-wins

This rule also applies to parameterized families:

- two different `cell(...)` providers in the same surface are illegal even if
  they might target different descendants

One surface gets one provider per public family.


### Only One Advertised Default

Within one advertised surface:

- at most one `default=True` advertisement is valid

If the default disappears on rerender, dependents that used advertised-default
resolution must be dirtied and re-resolved.


### Provider Must Target A Strict Natural Descendant

An advertised provider must target a node/mount site that is:

- inside the same natural subtree
- a strict natural descendant of the surface owner

Do not allow:

- self-targeting
- ancestor-targeting
- provider discovery through already-routed advertised edges


### Selector Translation Must Be Total For The Advertised Family

If a public family is parameterized, the provider must define the parameter
translation completely.

For example:

- `cell(row, column)` is valid
- half-translated or partially inferred parameter families are not


## Runtime Pieces

### 1. Advertised Selector Family

Add a public `SlotSelector` family for advertised/public mounts.

This can be:

- `mount_key(...)` plus parameterized helpers
- or a dedicated `AdvertisedMountSelector`

The important part is namespace separation from native `MountSelector`.


### 2. Mount Advertise Binding

Add a new plain-call result/binding pair:

- `PyrolyzeMountAdvertisementRequest`
- `PyrolyzeMountAdvertisementBinding`

Binding responsibilities:

- stage current advertisement
- publish on commit
- withdraw on deactivate
- dirty dependents if the advertisement disappears
- dirty dependents if target translation changes
- dirty dependents if `default=True` status changes


### 3. Surface Registry

Add a registry keyed by surface owner.

Each surface owner needs:

- published advertisement entries
- one optional default entry
- reverse dependencies: provider slot -> consumer directive slots

This registry can live in a runtime helper owned by the render boundary or in
app context. It does not need to be part of the public API.


### 4. Mount Advert DAG Builder

Add a builder that consumes:

- natural emitted subtree
- advertised surface registry

and produces:

- routed consumer assignments
- dependency edges
- rewritten/native-local mount routing inputs


## Algorithm Sketch

Recommended order:

1. Build the natural subtree as usual.
2. Commit all `advertise_mount(...)` plain-call slots for that pass.
3. Collect the committed advertised surface for the subtree owner.
4. Validate:
   - duplicate public keys
   - duplicate defaults
   - illegal non-descendant targets
5. Walk the natural subtree and resolve advertised selectors in `MountDirective`
   nodes.
6. For each consumer:
   - try advertised selectors left-to-right
   - if an advertised selector matches, translate it to the provider's inner
     native selector
   - splice the routed contribution at the provider's advertisement anchor
     point
   - record reverse dependency from provider slot to consumer directive slot
   - route the consumer subtree to that provider target
   - leave native/default fallback selectors available if earlier advertised
     selectors are not viable
7. After routing is frozen, perform the existing native/local mount flattening.


## Critical Blind Spots

These are the places where the design can still go wrong if not handled
explicitly.

### 1. Component Boundaries Are Not Retained As Public Emitted Nodes

The current emitted tree does not keep component nodes as first-class public
elements.

A no-AST-change plan therefore depends on one of:

- slot-id ancestry being sufficient to reconstruct surface ownership
- or adding an internal-only boundary marker at runtime

This is a real implementation risk. It is not fatal, but it needs proof in
tests early.


### 2. Ordering Should Be Anchor-Based

Ordering is mostly resolved by the advertisement-site anchor rule.

If a component does:

```python
with row():
    text("hello")
    advertise_mount(name=key("first_name"), default=True)
    text("hope you have a")
    advertise_mount(name=key("type_of_day"), default=True)
```

then routed children for `first_name` and `type_of_day` should appear at those
two anchor sites in that order.

That is the correct intuitive behavior.

The only remaining ordering question is local to one anchor:

- if multiple routed contributions target the same anchor, preserve the natural
  consumer order within that anchor bucket


### 3. Routed Identity Must Not Be Tied To Public Key Names

Today child slot ids are resolved from the mounted parent slot id plus index.

Cross-mounted children complicate that because:

- the natural emission site and the mounted parent differ
- public key names are intentionally renameable/mappable
- rerenders may legally remap one public key to a different inner/native
  selector or provider anchor

So the runtime should not treat the public advertised key name as attachment
identity.

The safer rule is:

- a routed attachment is identified by:
  - consumer directive slot
  - resolved provider/anchor slot
  - translated target selector identity
- pure renaming of the public key should not force a remount if the resolved
  provider/anchor and translated target are unchanged
- changing the resolved provider/anchor should be allowed to detach/remount if
  required by backend placement semantics


### 4. Advertised Default Precedence Must Be Specified

If a surface publishes an advertised default, the runtime needs a clear rule
for how it interacts with:

- explicit native selectors
- explicit advertised selectors
- fallback `default`
- no explicit selector at all

Phase 1 should keep this simple:

- explicit advertised/native selector list wins
- advertised default only participates where the current surface is selecting
  its own public default
- disappearing advertised default dirties dependents


### 5. Diagnostics Need To Name Both Sides

A failure message must mention:

- the consumer selector that was requested
- the surface owner it resolved against
- the provider slot or family that failed or disappeared

Anything less will be hard to debug.


## No-AST-Change Assessment

Avoiding an AST transform change looks realistic.

Reasons:

- bare slotted helper expressions already lower to `call_plain(...)`
- `call_plain(...)` already injects `PlainCallRuntimeContext`
- new plain-call result/binding types are already a supported runtime pattern

So the likely compiler delta is:

- zero lowering changes
- possibly zero detection changes if `advertise_mount` is exported from
  `pyrolyze.api` already marked as `_pyrolyze_slotted`
- optional return-type detection if we want better diagnostics or future
  specialized handling for `PyrolyzeMountAdvertisementRequest`

That is a strong advantage of this approach.


## Difficulty Estimate

This is medium-hard runtime work, not compiler-heavy work.

Rough rating:

- runtime/architecture difficulty: `7.5/10`
- compiler difficulty: `2.5/10`
- overall difficulty: `7.5/10`

Why it is still non-trivial:

- the hard part is the DAG builder and dependency invalidation
- not the syntax
- not the initial slot lifecycle plumbing

The two highest-risk areas are:

- proving the natural-tree-only DAG invariant in real nested examples
- preserving deterministic reuse semantics when children route across the
  natural tree while public keys remain renameable


## Test Plan

Target: about `42` new tests.

That is enough to pin the new behavior without exploding the suite.

### 1. Plain-Call / Binding Tests: 6 tests

- `advertise_mount(...)` bare expression call lowers and runs through
  `call_plain(...)`
- `PyrolyzeMountAdvertisementRequest` commits and publishes
- rollback restores prior published state
- deactivate withdraws published state
- target/default changes dirty dependents
- return-annotation/detection path works if we choose to enable it


### 2. Surface Registry Tests: 8 tests

- one advertised family publishes successfully
- duplicate public family names raise
- duplicate defaults raise
- parameterized family publishes with correct signature/identity
- disappear-on-rerender withdraws publication
- re-advertise with same identity but new target updates in place
- public key can be passed as a function parameter
- public key rename/mapping updates legally across rerender


### 3. DAG Builder Pure Tests: 12 tests

- one-hop advertised routing into descendant target
- parameterized family translation
- multi-selector fallback with advertised selector then native/default fallback
- advertised default routing
- re-advertised mount from nested wrapper
- provider chosen only from natural tree
- self-targeting rejected
- ancestor-targeting rejected
- no-provider-found error names consumer and surface
- dependency edges recorded for every resolved consumer
- anchor-point ordering between two advertisement sites
- multiple consumers into one anchor preserve consumer order


### 4. Invalidation And Teardown Tests: 8 tests

- disappearing provider dirties dependent consumer slots
- changed translation dirties dependent consumer slots
- unvisited consumer slot deactivates and detaches
- unvisited provider slot withdraws and dirties dependents
- provider unchanged does not dirty dependents
- dirtying provider boundary schedules rerender through existing invalidation
  path
- rollback during provider update restores previous dependents/surface
- legal dynamic surface change reroutes dependents without duplicate/leak state


### 5. Mount Engine Integration Tests: 6 tests

- Hydo or equivalent fake backend end-to-end routed child attachment
- routed child reuse across rerender
- routed child retarget from one provider instance to another
- parameterized routed mount instance identity
- advertised default end-to-end
- mixed native and advertised mounts in one subtree


### 6. End-To-End Host Tests: 2 tests

- one real toolkit smoke test for PySide6
- one real toolkit smoke test for Tkinter or Dear PyGui, whichever is cheapest
  to run in CI


## Recommended Phase Order

1. Add advertised selector family and plain-call binding support.
2. Add surface registry with duplicate/default enforcement.
3. Build a pure DAG-builder helper and test it heavily with synthetic trees.
4. Integrate the builder ahead of native mount flattening.
5. Add invalidation wiring for disappearing/changed providers.
6. Prove one fake backend and one real backend end-to-end.


## Bottom Line

The idea is viable.

The strongest version of it is:

- `advertise_mount(...)` is a slot-backed plain-call helper
- it publishes a dynamic public mount surface
- a DAG builder routes consumers to descendant providers before ordinary native
  flattening
- provider discovery is frozen against the natural tree only

That last rule is the one that makes the DAG argument actually hold.
