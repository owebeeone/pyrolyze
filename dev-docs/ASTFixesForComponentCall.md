# AST Fixes For Component Call

## Purpose

This document describes the redesign needed to clean up component-call lowering and runtime dispatch.

The current split between:

- `leaf_call(...)`
- `container_call(...)`
- `component_call(...)`

is not coherent enough for the compiler to target reliably.

The fix is:

- the compiler chooses between `leaf_call(...)` and `container_call(...)` purely by syntax
- the runtime decides whether the callable is an ordinary helper or a `ComponentRef`
- `CompValue` is removed from these call surfaces
- dynamic dirty transport uses `DM`-backed values and `Args`-shaped carriers, matching the `slot_expr` direction

## Current Compiler Special Indicators

The current compiler uses a mixture of syntax checks, annotation checks, runtime metadata, return-contract checks, and helper-name sets.

The important current indicators are:

### Syntax-triggered forms

- `with mount(...):`
- `call_native(factory)(...)`
- keyed-loop `keyed(...)`

These are recognized from AST shape and should remain syntax-driven where appropriate.

### Decorator and source-alias sets

Collected from source imports and decorator names:

- `_REACTIVE_DECORATORS = {"pyrolyze", "reactive_component"}`
- `_SLOTTED_DECORATORS = {"pyrolyze_slotted"}`
- `_EVENT_HANDLER_TYPES = {"PyrolyzeHandler", "PyrolyteHandler"}`

These currently feed:

- reactive component detection
- slotted helper detection
- event-handler parameter detection

### Callable-kind classification

Current compiler callable kinds:

- `_CALLABLE_KIND_COMPONENT_REF`
- `_CALLABLE_KIND_SLOT_CALLABLE`
- `_CALLABLE_KIND_PLAIN_CALLABLE`

These are inferred from:

- source annotations:
  - `ComponentRef[...]`
  - `SlotCallable[...]`
  - `Callable[...]`
- runtime annotations / resolved type hints for imports
- local assignment propagation through `callable_kinds`
- local return-kind propagation through `callable_return_kinds`

### Runtime metadata

Current imported symbol discovery uses:

- `_pyrolyze_meta`
  - imported component refs
- `_pyrolyze_slotted`
  - imported slotted helpers

This is a good direction and should be preferred over helper-name matching.

### Return-contract detection

Current imported helper detection also uses runtime return annotations for:

- `ExternalStoreRef`
- `PyrolyzeMountAdvertisementRequest`
- `UseEffectRequest`
- `UseEffectAsyncRequest`

This is how many imported plain-call / slot-backed helpers are detected today.

### Special helper-name sets

Current compiler still uses name-driven sets for:

- `_MOUNT_HELPERS = {"mount"}`
- `mount_helper_names`

and then:

- `_collect_mount_helper_names(...)`
- `_is_mount_call(...)`

This is the “name nonsense” path and is one of the main things to remove.

### Stored lowering tables

The current lowering pipeline also carries:

- `component_param_names`
- `component_event_params`
- `top_level_component_names`
- `slotted_helper_names`
- `callable_kinds`
- `callable_return_kinds`

Some of these are legitimate module-level facts.
Some are currently overused as compiler heuristics when runtime metadata should own the behavior instead.

## What This Design Removes

This design removes compile-time distinction between runtime component kinds.

The compiler should not try to decide whether a callable is:

- a “component call”
- a “container component”
- a mount point
- an advert point

from ad hoc helper-name tables or shallow callable-kind heuristics.

Instead:

- syntax decides only:
  - bare call statement => `leaf_call(...)`
  - `with` call statement => `container_call(...)`
- helper contracts / metadata decide:
  - slot-backed call behavior
  - event-handler behavior
  - dynamic component dirty-state construction
- runtime decides what actually happens after the call begins

In particular, the compiler should stop making a separate compile-time “component call vs container component call” choice.

## To Be Destroyed

The following current compiler/runtime special cases are not part of the desired end-state and should be removed rather than preserved:

- `with app_context_override[...](...):`
  - this is no longer the desired spec
  - it should not remain in the “special syntax that compiler must keep” bucket
- `CompValue` as a public/runtime call-surface transport
- `mount_helper_names` / helper-name-based mount recognition
- compiler-side distinction between `component_call(...)` and `container_call(...)` for `ComponentRef`s

## Core Rule

The compiler only needs to know this:

- bare call statement:
  - `BBB()`
  - lower as `leaf_call(...)`
- `with` call statement:
  - `with AAA():`
  - lower as `container_call(...)`

That is the entire lowering rule.

The compiler should not try to classify an `@pyrolyze` function or `ComponentRef` as:

- leaf
- container
- mount
- advert

Those are runtime consequences of what happens when the callable executes, not compile-time source categories.

## Why The Current `component_call(...)` Split Is Broken

Today the compiler lowers `ComponentRef` calls through a separate `component_call(...)` path.

That is problematic because:

- the compiler cannot soundly decide whether a `ComponentRef` should be treated as a “plain component call” or a “container component call”
- runtime behavior depends on the actual callable and metadata, not just the static annotation
- the public split between `component_call(...)` and `container_call(...)` is based on runtime history, not on a clean source-level rule

The correct source-level distinction is:

- `with ...:` => container form
- bare statement call => leaf form

## Target Runtime Model

Public compiler-emitted call surfaces should become:

- `leaf_call(...)`
- `container_call(...)`

and nothing else for component invocation.

At runtime:

- if the callable is not a `ComponentRef`
  - `leaf_call(...)` and `container_call(...)` keep their ordinary helper semantics
- if the callable is a `ComponentRef`
  - both call paths route into shared component-boundary machinery internally

So the runtime distinction becomes:

- syntax chooses the public entry point
- runtime decides whether component-specific behavior applies

## Meaning Of The Public Surfaces

### `leaf_call(...)`

Compiler emits `leaf_call(...)` for:

- bare call statements such as `BBB()`
- plain statement helpers like `advertise_mount(...)`
- any bare `ComponentRef` call

This means:

- there is no nested caller body
- the call is executed immediately
- if the callable is a `ComponentRef`, runtime still creates/reuses a retained child component boundary internally

### `container_call(...)`

Compiler emits `container_call(...)` for:

- `with AAA():`
- any `with` use of a `ComponentRef`

This means:

- the call opens a nested caller body
- the returned object must support context-manager usage
- if the callable is a `ComponentRef`, runtime still creates/reuses a retained child component boundary internally

### `component_call(...)`

`component_call(...)` should stop being a compiler-emitted public surface.

During migration it may continue to exist internally as a compatibility wrapper or shared helper entry point, but the end-state design should not require the compiler to emit it.

## Runtime Responsibilities For `ComponentRef`

When `leaf_call(...)` or `container_call(...)` sees a `ComponentRef`, runtime must:

1. read `_pyrolyze_meta`
2. resolve the underlying runtime function
3. reuse or replace retained child state by call identity
4. build the callee dirty state
5. manage child-owned event handlers
6. manage commit/rollback correctly
7. preserve authored app-context and root app-context behavior

This is the same retained child-component boundary logic regardless of whether the source form was:

- `BBB()`
- `with AAA():`

The difference between the two public surfaces is only whether the caller contributes a nested body.

## Dynamic Dirt Transport

The old `CompValue[T]` transport:

```python
@dataclass(frozen=True, slots=True)
class CompValue(Generic[T]):
    value: T
    dirty: bool = False
```

should not remain the primary call-surface contract.

It is a legacy transport from the old hidden-dirty model.

The new direction should match `slot_expr`:

- local dirt lives in `DM`
- direct reads use `__pyr_dm.bind.name`
- structured dirt transport uses parallel carriers

For component-like calls whose parameter names are not known statically, the compiler should pass:

- normal value args/kwargs in the ordinary call shape
- a parallel `Args` carrier named `__pyr_dyn_dirty_args`

Conceptually:

```python
__pyr_ctx.leaf_call(
    __pyr_slot_1,
    emit,
    formatted_text,
    maxwidth=width,
    __pyr_dyn_dirty_args=__pyr_Args.capture(
        __pyr_dm.bind.formatted_text,
        maxwidth=__pyr_dm.bind.width,
    ),
)
```

or in `with` form:

```python
with __pyr_ctx.container_call(
    __pyr_slot_1,
    wrap,
    title,
    children=body,
    __pyr_dyn_dirty_args=__pyr_Args.capture(
        __pyr_dm.bind.title,
        children=__pyr_dm.bind.body,
    ),
):
    ...
```

At runtime:

- `_pyrolyze_meta.param_names` provides formal parameter names
- the value call already provides actual values
- `__pyr_dyn_dirty_args` provides parallel dirt
- runtime builds the real `DirtyStateContext` for the child boundary

## Metadata Requirements

`ComponentMetadata` should carry parameter names directly:

```python
@dataclass(frozen=True, slots=True)
class ComponentMetadata(Generic[P]):
    name: str
    _func: Callable[..., None]
    param_names: tuple[str, ...] = ()
    packed_kwargs: bool = False
    packed_kwarg_param_names: tuple[str, ...] = ()
```

`pyrolyze_component_ref(...)` should populate `param_names` from the original decorated function signature when `param_names` is empty.

That keeps runtime parameter-name discovery cheap and avoids runtime `inspect.signature(...)` during invocation.

## Why Names Are Needed

The main reason to resolve parameter names at runtime is not ordinary Python invocation.

The main reason is:

- building the correct child `DirtyStateContext`

For dynamic `ComponentRef` calls, runtime must know which dirt entry belongs to which formal parameter.

That is why `__pyr_dyn_dirty_args` exists.

## `advertise_mount(...)`

`advertise_mount(...)` is not a container form.

It remains a bare statement call.

So compiler lowering should treat it like a leaf-form statement call, not a container-form call.

Consumer syntax remains:

```python
with mount(...):
    ...
```

Producer syntax remains:

```python
advertise_mount(...)
```

## `mount(...)` Recognition Is Also Broken

Current compiler behavior recognizes `mount(...)` through a collected helper-name set:

- `state.mount_helper_names`
- `_collect_mount_helper_names(...)`
- `_is_mount_call(...)`

That is too weak.

It means `mount(...)` is currently treated as special because its call name appears in a tracked helper-name set, not because it is recognized through a stronger source contract.

That is inconsistent with the intended direction for other special helper forms, where detection should follow:

- source contract
- annotation/return contract
- or explicit special-form recognition

not ad hoc helper-name matching.

### Required fix

As part of the broader component/call cleanup, `mount(...)` recognition should be moved away from helper-name collection and onto a proper special-form contract.

The compiler should recognize mount syntax because it is the reserved mount directive form, not because the callee name happened to be imported under a matching alias.

This matters because the current call-surface cleanup is trying to make the compiler decide call behavior from syntax and stable contracts, not from fragile name tables.

This does **not** mean ordinary runtime mount/advert behavior becomes compile-time classification.

It means:

- the compiler may still recognize the reserved `with mount(...):` directive form
- but it should not do so through `mount_helper_names`
- and it should not treat “mount point” as a general callable kind for component lowering

## Additional Required Cleanup

The call cleanup work therefore includes:

- removing `ComponentRef`-specific compiler heuristics that choose between runtime call backends
- removing `CompValue` from the public/runtime call-surface model
- moving dynamic component dirt transport to `DM` + `Args`
- replacing `mount_helper_names`-style recognition with proper special-form detection for `mount(...)`
- removing the obsolete `with app_context_override[...](...)` compiler special form from the end-state design

## Consolidation Plan

### Phase 1: Stabilize Tests

Before changing runtime structure, add and keep passing tests for:

- bare `ComponentRef` stable identity rerender
- bare `ComponentRef` identity replacement
- `with ComponentRef(...)` stable identity rerender
- `with ComponentRef(...)` identity replacement
- rollback on failure for both forms
- event-handler ownership/retention for both forms
- app-context propagation for both forms

### Phase 2: Add Metadata And Dynamic Dirt Support

Implement:

- `ComponentMetadata.param_names`
- `pyrolyze_component_ref(...)` auto-population of `param_names`
- `__pyr_dyn_dirty_args` support in runtime component-boundary handling

Do this first while keeping current public method compatibility.

### Phase 3: Unify Runtime Component Boundary Logic

Extract shared retained child-component machinery so that:

- `leaf_call(...)` can route `ComponentRef` calls through it
- `container_call(...)` can route `ComponentRef` calls through it

At this point the compiler still chooses only by syntax:

- bare call => `leaf_call(...)`
- `with` call => `container_call(...)`

### Phase 4: Remove Compiler Emission Of `component_call(...)`

Once runtime supports `ComponentRef` through both public syntax-based entry points, compiler lowering should stop emitting `component_call(...)`.

At that point:

- bare `ComponentRef` calls lower to `leaf_call(...)`
- `with ComponentRef(...):` lowers to `container_call(...)`

### Phase 5: Remove `CompValue` From These Call Surfaces

Once the above is stable:

- remove `CompValue` from `leaf_call(...)` / `container_call(...)` / supporting component-boundary internals
- use:
  - raw values
  - `DM` reads
  - `Args`
  - `__pyr_dyn_dirty_args`
  - explicit dirty-state objects where needed

This keeps dirt transport aligned with `slot_expr` and the newer runtime model.

## End State

Compiler rule:

- `BBB()` => `leaf_call(...)`
- `with AAA():` => `container_call(...)`

Runtime rule:

- ordinary helper => ordinary leaf/container behavior
- `ComponentRef` => retained child-component boundary behavior

Dirty transport rule:

- no `CompValue`-driven public model
- `DM` as authoritative local dirt
- `Args` / `__pyr_dyn_dirty_args` for dynamic parallel dirt transport

This is the coherent model that removes the current `component_call(...)` ambiguity.
