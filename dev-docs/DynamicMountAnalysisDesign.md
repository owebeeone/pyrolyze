# Dynamic Mount Analysis Design

## Purpose

This document describes the runtime-driven analysis model for mount fuzzing and
related graph-inspection tooling.

The key realization is:

- we already have the dependency graph
- it is the runtime slot/context graph

So the problem is not to invent a second graph.

The problem is:

- expose explicit intrinsic call intent to the compiler/runtime
- attach application-specific runtime metadata to active sites
- map active sites back to the stored-shape inputs that drove them

This is enough to support:

- mount / advert fuzzing
- graph visitors that need app-specific annotations
- stable explanation of “if X changes, Y and Z are now invalid”

## Why runtime analysis is the right level

The earlier static-analysis direction was too expensive for the value.

The hard cases are all runtime-shaped:

- keyed loops expand one authored site into many runtime instances
- `use_stored(...)` decides concrete structure at runtime
- branch-selected mount / advert activation depends on values
- the mount environment we care about is the active one, not every possible one

For fuzzing and graph inspection, the source of truth should therefore be:

- the active realized graph for one concrete state

not a full static approximation of every possible graph.

## Requirements

### 1. Explicit intrinsic helper wrapping

We need explicit wrappers so the compiler does not need to infer call intent
from provenance annotations, local-variable annotations, or import provenance.

The authored forms are:

```python
component(component_func, *args, **kwargs)
slotted(slotted_func, *args, **kwargs)
```

These are not choosing `component_call(...)` vs `container_call(...)`.

That choice is still determined by authored call shape:

- bare call form lowers as a direct component/slotted call
- `with ...:` form lowers as a container call

The wrapper only tells the compiler/runtime:

- “this callable is intentionally a PyRolyze intrinsic call target”

### 2. Wrapped call targets may provide dynamic resolution

If `component_func` or `slotted_func` is an instance of `PyrolyzeWrap`, the
runtime should resolve it before invocation.

The resolved call may provide:

1. `RuntimeSiteMetadata`
2. merged args / kwargs
3. `None` for the actual callable, meaning “do not make the call this pass”

This gives one mechanism for:

- app-specific runtime annotations
- helper-provided default args
- helper-provided arg rewriting
- nullified/inactive call sites

without requiring a special compiler path for each helper.

### 3. Metadata must be generic and visitor-visible

The metadata system is not only for mount fuzzing.

It should be a generic way to attach application-specific annotations to:

- slot sites
- slot-call bindings
- component/container/directive sites

The runtime graph visitor should be able to see:

- the active runtime site
- the full slot-id path
- the attached metadata entries

So the metadata model should stay generic:

```python
@dataclass(frozen=True, slots=True)
class RuntimeSiteMetadata(Generic[T]):
    key: Hashable
    value: T
```

This is intentionally not mount-specific.

### 4. We need a standard slot-id path type

One `SlotId` is not enough.

We need the full active runtime path, because:

- the same logical site can appear under different parents
- keyed loops already distinguish instances through path-like identity
- the same stored-shape key may be used in multiple places

So we need a standard runtime path structure:

```python
@dataclass(frozen=True, slots=True)
class SlotIdPath:
    items: tuple[SlotId, ...]
```

This should become the standard path object used by:

- runtime visitors
- mount / advert analysis
- stored-shape attribution
- any helper that wants to attach metadata to active graph sites

### 5. We need stored-shape attribution

For shape-driven fuzzing, we need to know which external shape input drove which
active runtime subtree.

So the system must be able to record:

- `use_stored(KEY)`
- plus `SlotIdPath`

That identity is the practical runtime identity for fuzzing:

- `KEY` tells us which external state object mattered
- `SlotIdPath` tells us which concrete realized runtime site it fed

### 6. Call-site nullification must be supported

If a `PyrolyzeWrap` resolves to:

- `func=None`

then the call is not made for that pass.

This applies equally to:

- component/direct call
- slotted call
- container call

The important rule is:

- the site is still evaluated when dirty
- the resolved callable may be `None`
- in that case the actual call is skipped

This lets helpers control active/inactive sites while still participating in
the normal runtime dirt path.

### 7. Stay close to the real runtime path

The analysis path should stay as close as possible to real execution.

Compiler/lowering changes are acceptable when they improve:

- explicit intent
- site identity
- observability

But mount selection, advert publication, and active-site shape should still
come from the real runtime path.

## Core API model

### Runtime metadata

```python
@dataclass(frozen=True, slots=True)
class RuntimeSiteMetadata(Generic[T]):
    key: Hashable
    value: T
```

This is the generic annotation payload attached to an active runtime site.

### Standard slot path

```python
@dataclass(frozen=True, slots=True)
class SlotIdPath:
    items: tuple[SlotId, ...]
```

This is the standard identity path for:

- active runtime sites
- stored-shape attribution
- visitor-visible graph annotations

### Resolved wrapped call

```python
@dataclass(frozen=True, slots=True)
class ResolvedPyrolyzeCall:
    func: Callable[..., Any] | None
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    metadata: tuple[RuntimeSiteMetadata[Any], ...] = ()
```

This is the runtime-normalized call target.

If `func is None`, the call is not made for that pass.

### Wrapped callable contract

```python
class PyrolyzeWrap(ABC):
    @abstractmethod
    def resolve(
        self,
        *,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        slot_id_path: SlotIdPath,
    ) -> ResolvedPyrolyzeCall: ...
```

This is the generic wrapper contract used by:

- `component(...)`
- `slotted(...)`
- future helper wrappers such as mount/advert fuzz helpers

The wrapper owns:

- arg / kwarg merging
- metadata emission
- nullification

### Authored helper markers

The authored helper markers are:

```python
component(component_func, *args, **kwargs)
slotted(slotted_func, *args, **kwargs)
```

If the first argument is a plain callable:

- the helper is only providing explicit intrinsic intent

If the first argument is a `PyrolyzeWrap`:

- the runtime resolves it first

## Compiler and lowering behavior

The compiler should treat `component(...)` and `slotted(...)` as explicit
intrinsic markers.

What they do **not** do:

- they do not decide between `component_call(...)` and `container_call(...)`

That still comes from authored syntax shape:

- bare call form:
  - lower through direct call machinery
- `with ...:` form:
  - lower through `container_call(...)`

So the rule is:

- helper marker supplies intent
- authored call shape supplies structural lowering form

This is important because it keeps the wrapper generic and avoids forcing a
container/component distinction into the wrapper name itself.

## Runtime analysis model

The existing slot/context graph remains the dependency graph.

The analysis system should enrich it with:

- `SlotIdPath`
- stored-shape usages
- selected mount
- active advertisements
- emitted object/type identity
- helper-provided `RuntimeSiteMetadata`

This is enough to answer:

- which active sites came from which stored-shape nodes?
- which helper-wrapped sites published analysis metadata?
- which downstream active sites depend on an upstream mount/advert choice?

## Stored-shape attribution

The central instrumentation target is:

- mapping `use_stored(KEY)` to `SlotIdPath`

Once we have that, the slot graph plus helper/site metadata becomes much more
useful:

- changing a store entry tells us which active runtime subtrees are driven by it
- changing a wrapped mount/helper site tells us which downstream sites are at
  risk
- rerender-vs-fresh mismatches can be explained in terms of actual active
  dependencies

The natural runtime shape is:

```python
@dataclass(frozen=True, slots=True)
class StoreUsageInstance:
    key: object
    slot_id_path: SlotIdPath
```

## Relationship to mount / advert fuzzing

This design is sufficient for mount / advert fuzz tooling.

Mount/advert fuzzing does not need a mount-specific metadata system.

It needs:

- explicit intrinsic call helpers
- call wrappers that can annotate and nullify
- active runtime site metadata
- stored-shape attribution
- backend compatibility metadata

Then a fuzz harness can:

1. build one concrete external shape state
2. run the authored shape
3. capture:
   - slot/context graph
   - `SlotIdPath`
   - store-key attribution
   - helper metadata
   - selected mount / active advertisements / emitted type
4. mutate one mount/helper/store choice
5. rerender incrementally
6. render fresh
7. compare results

## What the graph must answer

Given a change at an active site `X`, the graph should make it possible to ask:

1. Which downstream active sites depend on `X`?
2. Which of those sites have current emitted objects that are no longer valid?
3. Is the incompatibility due to:
   - mount-name mismatch
   - selector/value mismatch
   - accepted-child-type mismatch
   - advert/default routing change
   - helper-provided nullification / arg rewrite
4. What repair choices exist?
   - keep the child and choose a different mount
   - keep the mount and change the child type
   - drop or replace a subtree

## First implementation slice

The smallest useful first step is:

1. add `component(...)` and `slotted(...)` intrinsic markers
2. add `PyrolyzeWrap` + `ResolvedPyrolyzeCall`
3. add `RuntimeSiteMetadata`
4. add standard `SlotIdPath`
5. instrument `use_stored(KEY)` so runtime records:
   - `KEY`
   - `SlotIdPath`
6. expose attached metadata and `SlotIdPath` through the visitor graph

That is enough to prove the direction before designing richer dependency-edge
types or specialized fuzz wrappers.
