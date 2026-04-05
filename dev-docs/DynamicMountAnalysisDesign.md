# Dynamic Mount Analysis Design

## Purpose

This document describes the runtime-driven analysis model for mount fuzzing.

The key realization is:

- we already have the dependency graph
- it is the runtime slot/context graph

So the problem is not “invent a second graph”.

The problem is:

- instrument the existing slot graph so emitted nodes, selected mounts, adverts,
  and `use_stored(KEY)` inputs can be mapped back onto concrete runtime graph
  nodes

The goal is to make the existing active graph answer questions like:

- if mount choice at `X` changes, which active sites `Y` and `Z` are affected?
- which current emitted objects become incompatible?
- do we need to:
  - change downstream emitted node types,
  - choose a different mount,
  - or replace/prune a subtree?

This is the information needed to drive realistic mount fuzzing.

## Why runtime analysis is the right level

The static-analysis attempt was too hard for the value:

- keyed-loop expansion creates many runtime instances from one authored site
- `use_stored(...)` decides concrete structure at runtime
- branch-selected mount / advert activation depends on values
- the mount environment we care about is the active one, not every possible one

For fuzzing, the source of truth should therefore be:

- the active realized graph for one concrete state

not a full static approximation of every possible graph.

## Requirements

### 1. Use the existing slot/context graph as the dependency graph

We do not need a second abstract dependency graph.

The runtime already has:

- structural ownership
- parent/child slot relationships
- keyed-loop expansion
- retained boundary identity

That graph is already the dependency graph we care about.

So the analysis system should build on:

- the existing slot/context graph
- plus added attribution metadata

not on a separate reconstructed graph model.

### 2. Explain compatibility, not just structure

The analysis must be able to say:

- site `Y` currently emits type `LeafAB00`
- site `Y` is attached through mount `M`
- if upstream mount selection changes from `M` to `N`,
  `LeafAB00` is no longer compatible

So the analysis must connect:

- site identity
- selected mount
- current emitted type
- compatibility reason

### 3. Work over the actual realized graph

The graph must be built from the actual runtime execution of a concrete shape
state.

That means it must incorporate:

- actual keyed-loop keys
- actual executed branches
- actual active advertisements
- actual selected mounts
- actual emitted node/container types

### 4. Map `use_stored(KEY)` to concrete runtime instances

One `KEY` is not enough by itself.

The same external store key may be realized under multiple parent contexts.

So the analysis must track something like:

- store key
- plus full runtime slot-id path

This is the crucial identity for shape-driven fuzzing.

It lets us say:

- `use_stored("B")` contributed to this concrete realized subtree
- and that subtree existed under this exact runtime structural path

So the analysis must be able to record:

- `StoreKey`
- `SlotIdPath`

together.

### 5. Support inactive but authored sites where useful

We still want stable site identity and explainable gaps, so analysis-oriented
helpers should let us identify authored sites that are currently inactive.

But the primary graph is the active graph.

The important thing is:

- if a site is inactive, we may want to know it exists
- if a site is active, we must know exactly what it depends on

### 6. Stay close to real runtime behavior

The analysis path should be as close as possible to the real runtime path.

The fuzz harness should not rely on a radically separate execution mode that
would hide real mount behavior.

Compiler/lowering changes are acceptable when they improve:

- site identity
- observability
- controllable inactive-site behavior

But the mount decisions should still come from the real runtime path.

## Explicit site-tagging intrinsics

We still want explicit site tagging for analysis-oriented shape functions.

The purpose of these helpers is:

- stable site naming
- explicit site kind
- clear lowering hooks
- clear runtime analysis hooks

Examples:

```python
component_call(sd.top_leaf_call)

with mount_call(sd.body_mount, selector):
    ...

advert_call(sd.body_advert)
```

If site disambiguation is needed:

```python
with mount_call(sd.body_mount, selector, site="other_body_mount"):
    ...
```

The exact names are open. The important requirement is:

- the runtime can say which active graph nodes came from which authored sites

## Site identity

Keyed loops still require two identity levels:

- static site identity
- runtime site-instance identity

So the analysis model should use something like:

```python
@dataclass(frozen=True, slots=True)
class RuntimeSiteId:
    static_site_id: str
    key_path: tuple[object, ...]
```

That lets one authored site expand into many active runtime sites.

### Slot-id path matters, not just one slot id

For this design, one `SlotId` is not enough.

We need the full runtime path of slot ids leading to the active site, because:

- repeated logical sites may appear under different parents
- the same store key may be used in multiple places
- keyed loops already distinguish instances through path-like identity

So the practical runtime identity is closer to:

```python
@dataclass(frozen=True, slots=True)
class RuntimeSitePath:
    slot_id_path: tuple[SlotId, ...]
```

and for stored-shape attribution:

```python
@dataclass(frozen=True, slots=True)
class StoreUsageInstance:
    key: object
    slot_id_path: tuple[SlotId, ...]
```

This is the level at which we can say that a particular `use_stored(KEY)` call
fed a particular active subtree.

## Related runtime issue: container-call nullification

One related but separate issue is how container-form helpers can suppress entry
into a structural `with` site.

That topic has been split out into:

- `dev-docs/ContainerCallNullifierDesign.md`

It is related because inactive container sites affect the active graph, but it
is not itself the mount-dependency graph problem.

## Proposed attribution model

The analysis should enrich the existing slot/context graph with attribution
records rather than constructing an entirely separate graph.

The first useful additions are:

```python
@dataclass(frozen=True, slots=True)
class ActiveMountEnv:
    available_native_mounts: tuple[object, ...]
    advertised_mounts: tuple[object, ...]
    default_advertised_mount: object | None


@dataclass(frozen=True, slots=True)
class ActiveSiteAttribution:
    runtime_site_id: RuntimeSiteId
    slot_id_path: tuple[SlotId, ...]
    store_usages: tuple[StoreUsageInstance, ...]
    selected_mount: object | None
    active_advertisements: tuple[object, ...]
    emitted_type: str | None
    emitted_object_identity: object | None


@dataclass(frozen=True, slots=True)
class MountDependencyEdge:
    source_site_id: RuntimeSiteId
    affected_site_id: RuntimeSiteId
    reason: str
```

This is only a sketch, but it captures the actual requirement:

- what slot/context node this is
- which stored-shape inputs fed it
- which mount/advert choices were active there
- what it emitted
- what downstream active sites depend on it

### Important consequence

The central instrumentation target is:

- mapping `use_stored(KEY)` to `slot_id_path`

Once we have that, the slot graph plus emitted/mount attribution becomes much
more useful:

- changing a store entry tells us which realized subtrees are driven by it
- changing a mount on one attributed site tells us which downstream sites are at
  risk
- rerender-vs-fresh mismatches can be explained in terms of actual active
  dependencies, not only visual tree diffs

## What the graph must answer

Given a change at an active site `X`, the graph should make it possible to ask:

1. Which downstream active sites depend on `X`'s selected mount or advert state?
2. Which of those sites have current emitted objects that are no longer valid?
3. Is the incompatibility due to:
   - mount-name mismatch
   - selector/value mismatch
   - accepted-child-type mismatch
   - advert/default routing change
4. What repair choices exist?
   - keep the child and choose a different mount
   - keep the mount and change the child type
   - drop or replace a subtree

That is the core value of the dynamic analysis.

## Relationship to backend metadata

Runtime analysis does not replace backend compatibility metadata.

The split should be:

- runtime analysis tells us:
  - which active sites exist
  - which mount was selected
  - which emitted type is currently present
  - which sites depend on which upstream choices

- backend metadata tells us:
  - which emitted types are compatible with which mount points

So compatibility is determined by combining:

- the active graph
- backend compatibility rules

## Relationship to fuzzing

This is enough to drive the fuzz system.

The fuzz harness can:

1. build one concrete external state
2. run the authored shape
3. capture:
   - slot/context graph
   - store-key-to-slot-path attribution
   - emitted-node / selected-mount / advert attribution
4. mutate one mount/advert or one structural choice
5. use the attributed slot graph to understand which active sites are affected
6. rerender incrementally
7. render fresh
8. compare results

The active graph is then used for:

- legality checks
- choosing meaningful mutations
- explaining failures
- reducing “why did this subtree move?” debugging time

## First implementation slice

The smallest useful first step is:

1. instrument `use_stored(KEY)` so runtime analysis records:
   - `KEY`
   - current `slot_id_path`
2. record, for active runtime sites:
   - selected mount
   - active advertisements
   - emitted object/type identity
3. tie those records back onto the existing slot/context graph
4. use the attributed slot graph in one first mount-aware fuzz harness

That is enough to prove the direction before designing richer dependency-edge
types.
