# AST Fixes For Component Call Plan

## Purpose

This plan corrects the current component-call and mount-lowering architecture.

It also absorbs the former slot-plan Phase CA work for dynamic annotated local
`ComponentRef` calls.

The target model is:

- the compiler chooses call lowering by syntax only
  - bare call statement => `leaf_call(...)`
  - `with` call statement => `container_call(...)`
- runtime decides whether the callable is:
  - an ordinary helper
  - a `ComponentRef`
  - a mount callable
  - an advert-producing helper
- mount detection uses the callable contract:

```python
def mount(*selectors: SlotSelector) -> PyrolyzeMountFunction:
```

- bespoke compiler mount lowering is removed
- `CompValue` is removed from public/runtime call surfaces in favor of `DM`, `Args`, and explicit dynamic dirt carriers

The goal is to stop encoding runtime behavior in compiler heuristics.

## Current Problems

### 1. The compiler distinguishes too many call kinds

Today the compiler reasons about:

- `leaf_call(...)`
- `container_call(...)`
- `component_call(...)`
- special `mount(...)` lowering

This is too much compiler knowledge. The compiler should only care about source syntax shape, not runtime component kind.

### 2. `mount(...)` detection is name-driven

The current pipeline uses:

- `_MOUNT_HELPERS`
- `mount_helper_names`
- `_collect_mount_helper_names(...)`
- `_is_mount_call(...)`

This is brittle and incorrect. A mount callable should be recognized by the `PyrolyzeMountFunction` contract, not by its name.

### 3. Mount handling is over-lowered in the compiler

The current `with mount(...):` path goes through bespoke compiler lowering to:

- `_lower_mount_with(...)`
- `open_directive(...)`

That pushes structural mount behavior into the compiler when runtime already has an emitted-node contract:

```python
EmittedNode = UIElement | MountDirective | PyrolyzeMountAdvertisement
```

Runtime should own mount behavior and emit `MountDirective` values as part of normal execution.

### 4. `component_call(...)` is a broken compiler-facing split

The compiler currently emits a dedicated `component_call(...)` path for `ComponentRef`s.

That is the wrong boundary. The compiler should not decide:

- component call
- container component call

It should decide only:

- bare statement call
- `with` call

### 5. `CompValue` is legacy dirt transport

`CompValue` is still threaded through runtime call surfaces:

- `leaf_call(...)`
- `container_call(...)`
- `component_call(...)`

This conflicts with the newer direction already established by `slot_expr`:

- local dirt in `DM`
- argument/value transport in `Args`
- dynamic dirt transport in a parallel `Args` carrier

### 6. `with app_context_override[...](...)` is obsolete

This syntax is not part of the desired end-state and should be removed rather than preserved.

## End-State Rules

### Compiler rules

The compiler should know only:

- bare call statement => `leaf_call(...)`
- `with` call statement => `container_call(...)`
- slot-bearing expressions => `slot_expr`

The compiler should not choose between:

- `component_call(...)`
- component-vs-container component behavior
- helper-name-based mount categories

### Runtime rules

Runtime should decide behavior after the call begins:

- non-component leaf helper
- non-component container helper
- `ComponentRef`
- mount callable
- advert-producing helper

For mounts, runtime should rely on:

- callable contract: `PyrolyzeMountFunction`
- emitted-node output: `MountDirective`

not on a compiler-only mount special path.

## Detection Contract Changes

### Mount detection

Mount callables should be recognized by the return contract:

```python
def mount(*selectors: SlotSelector) -> PyrolyzeMountFunction:
```

Required changes:

- add `PyrolyzeMountFunction` to the public API surface if it does not already exist
- change `mount(...)` to return `PyrolyzeMountFunction`
- teach compiler import/type discovery to recognize `PyrolyzeMountFunction`
- remove helper-name-based mount detection

### Component detection

Component detection should continue to use:

- `ComponentRef[...]`
- `_pyrolyze_meta`

But component detection should no longer force a separate compiler-emitted runtime call backend.

### Slot detection

Slot-bearing call detection can continue using existing contract-driven signals:

- `SlotCallable[...]`
- `@pyrolyze_slotted`
- imported helper return contracts

## Removal Targets

The following should be deleted by the end of this plan:

- `_MOUNT_HELPERS`
- `mount_helper_names`
- `_collect_mount_helper_names(...)`
- `_is_mount_call(...)` as name-based helper matching
- `_lower_mount_with(...)`
- compiler-emitted `component_call(...)`
- public/runtime `CompValue` call-surface usage
- `with app_context_override[...](...)` compiler special handling

## Execution Plan

### Phase 1: Introduce Runtime Contracts

Goal:
- replace name-based detection with explicit contracts

Changes:
- introduce `PyrolyzeMountFunction`
- update `mount(...)` to return `PyrolyzeMountFunction`
- extend `ComponentMetadata` with `param_names`
- populate `param_names` from the original decorated function signature

Tests:
- imported or aliased `mount` helper is recognized by contract, not by name
- `ComponentMetadata.param_names` is populated correctly
- existing component metadata tests pass

### Phase 2: Stop Emitting `component_call(...)`

Goal:
- make compiler lowering syntax-driven

Changes:
- bare `ComponentRef` calls lower to `leaf_call(...)`
- `with ComponentRef(...):` lowers to `container_call(...)`
- remove compiler-side choice between `component_call(...)` and `container_call(...)`

Tests:
- direct component rewrite tests now expect `leaf_call(...)`
- `with ComponentRef(...):` rewrite tests expect `container_call(...)`
- runtime identity/reuse tests for both forms still pass

### Phase 3: Move `ComponentRef` Semantics Fully Into Runtime

Goal:
- preserve retained child-component behavior without compiler specialization

Changes:
- `leaf_call(...)` handles `ComponentRef` through shared child-boundary logic
- `container_call(...)` handles `ComponentRef` through the same shared logic
- `component_call(...)` becomes an internal compatibility wrapper or is removed entirely

Tests:
- direct `ComponentRef` rerender reuse
- direct `ComponentRef` replacement
- `with ComponentRef(...):` rerender reuse
- `with ComponentRef(...):` replacement
- rollback on failure for both forms
- event-handler retention for both forms
- app-context propagation for both forms

### Phase 4: Add Dynamic Dirt Transport For Runtime ComponentRef Resolution

Goal:
- remove compiler dependence on static parameter-name tables for dynamic refs

Changes:
- add `__pyr_dyn_dirty_args` as the dynamic dirt carrier
- pass it alongside normal args/kwargs when static parameter-name lowering is not available
- use `ComponentMetadata.param_names` at runtime to construct callee dirty state

Tests:
- positional `__pyr_dyn_dirty_args` maps to the correct formal names
- named `__pyr_dyn_dirty_args` maps to the correct formal names
- annotated local `ComponentRef` lookup calls go green

### Phase 5: Remove Compiler Mount Special Lowering

Goal:
- stop lowering `mount(...)` through a bespoke compiler-only path

Changes:
- remove `_lower_mount_with(...)`
- stop lowering mount through `open_directive(...)` from the compiler
- lower `with mount(...):` through the same syntax-based container-call path used for other `with` forms
- let runtime detect `PyrolyzeMountFunction` and emit `MountDirective`

Tests:
- mount rewrite tests reflect container-form lowering instead of bespoke mount lowering
- runtime emits `MountDirective` correctly
- advert routing still works via `PyrolyzeMountAdvertisement`
- emitted-node contract remains:
  - `UIElement`
  - `MountDirective`
  - `PyrolyzeMountAdvertisement`

### Phase 6: Remove `CompValue` From Public Call Surfaces

Goal:
- align component/container/leaf call transport with the `slot_expr`/`DM` direction

Changes:
- remove `CompValue` from:
  - `leaf_call(...)`
  - `container_call(...)`
  - shared component-boundary helpers
- use:
  - raw values
  - `DM`
  - `Args`
  - `__pyr_dyn_dirty_args`

Tests:
- leaf helper rerender semantics remain correct
- container helper rerender semantics remain correct
- `ComponentRef` rerender semantics remain correct
- slot-expression integration remains green

### Phase 7: Remove Obsolete Special Forms

Goal:
- delete compiler/runtime detours that no longer belong in the model

Remove:
- `with app_context_override[...](...)`
- remaining helper-name-based mount recognition
- remaining public/compiler-facing `component_call(...)` usage

Tests:
- no active compiler lowering path still references removed surfaces
- docs and goldens reflect only the new model

## Test Inventory

### Contract detection tests

- `mount(...)` is recognized through `PyrolyzeMountFunction`
- aliased/imported mount helpers still lower correctly
- `ComponentMetadata.param_names` is populated from the original signature
- slot-helper detection still works unchanged

### Component runtime tests

- direct `ComponentRef` rerender reuse
- direct `ComponentRef` replacement
- `with ComponentRef(...):` rerender reuse
- `with ComponentRef(...):` replacement
- rollback on failure
- event-handler retention
- app-context propagation

### Dynamic dirt tests

- positional `__pyr_dyn_dirty_args`
- named `__pyr_dyn_dirty_args`
- dynamic local `ComponentRef` compiler tests

### Mount runtime tests

- runtime emits `MountDirective`
- advert routing still works
- emitted-node contract remains correct

### Regression tests

- slot-expression tests remain green
- component-call tests remain green
- mount advert tests remain green
- compiler goldens remain coherent after mount lowering changes

## Immediate Next Step

The safest first slice is:

1. add `PyrolyzeMountFunction`
2. update `mount(...)` to return it
3. add `ComponentMetadata.param_names`
4. add tests for the two contracts before changing compiler lowering

That gives a clear runtime/typing contract before removing the compiler’s helper-name and mount-special-case logic.
