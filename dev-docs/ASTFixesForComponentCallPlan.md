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

### Phase A0: Introduce Runtime Container/Mount Dispatch

Goal:
- make containerization vs mount emission a runtime decision independent of the old `component_call(...)` path

Rationale:
- `with CF(...):` is the only compiler-visible container form
- runtime must decide whether the invoked callable:
  - behaves like an ordinary container helper
  - creates a retained child component boundary
  - emits a `MountDirective`
- a mount is structurally a kind of container, so the public compiler surface should still be only `container_call(...)`

Runtime rule:
- `container_call(...)` is the single runtime entry point for all `with ...:` calls
- after invocation begins, runtime decides whether the result path is:
  - native/container helper behavior
  - retained `ComponentRef` child-boundary behavior
  - `MountDirective` emission

Important consequence:
- `mount(...)` should not need a separate compiler-lowered `open_directive(...)` path once this seam exists
- the runtime branch should be driven by callable contract and emitted-node behavior, not helper-name matching

Changes:
- define a runtime dispatch seam inside `container_call(...)` for:
  - ordinary container helper
  - `ComponentRef`
  - `PyrolyzeMountFunction`
- treat `MountDirective` as a runtime-emitted container outcome
- leave `advertise_mount(...)` on the slot-call path
  - it already resolves through `PyrolyzeMountAdvertisementRequest` -> `PyrolyzeMountAdvertisement`
- keep this phase independent of removing `component_call(...)`
  - the purpose is to create the runtime target first

#### A0 Concrete Runtime Shape

The current `container_call(...)` branch point in `runtime/context.py` is:

1. `ComponentRef` / `_pyrolyze_meta` => `_PyrolyzeContainerCallHandle`
2. native-context helper => `_NativeContainerCallHandle`
3. ordinary helper => `_ContainerCallHandle`

Phase A0 should replace this ad hoc split with one explicit dispatch function,
for example conceptually:

```python
def _resolve_container_runtime_mode(raw_callable, *, args, kwargs, dirty_state):
    ...
```

which returns one of:

- `ContainerRuntimeMode.COMPONENT_REF`
- `ContainerRuntimeMode.MOUNT`
- `ContainerRuntimeMode.NATIVE_CONTAINER`
- `ContainerRuntimeMode.PLAIN_CONTAINER`

and a corresponding handle payload.

The important design point is:

- `container_call(...)` remains the only public/runtime entry point for `with ...:`
- mode selection is entirely runtime-owned

#### A0 Handle Strategy

Do not try to invent unrelated public APIs.

Instead:

- keep `container_call(...) -> context manager handle`
- preserve the existing handle pattern
- unify dispatch behind a small number of internal handles

Concretely:

- `_PyrolyzeContainerCallHandle`
  - retained child `ComponentRef` behavior
- `_ContainerCallHandle`
  - plain helper behavior
- `_NativeContainerCallHandle`
  - current native-context helper behavior
- introduce one mount-specific handle only if needed, for example:
  - `_MountContainerCallHandle`

If the existing `DirectiveSlotContext` can be adapted cleanly, the mount handle
may simply wrap that path at runtime instead of inventing a completely new slot type.

The requirement is not “one handle only.” The requirement is:

- one public entry surface
- runtime-selected handle/behavior

#### A0 Dispatch Order

Dispatch should be explicit and stable.

Recommended order:

1. `ComponentRef`
   - if `_component_call_key(...)` + runtime func resolution succeeds
   - choose retained component-boundary handling

2. `PyrolyzeMountFunction`
   - if callable contract indicates mount
   - choose runtime mount-directive handling

3. native container helper
   - if first parameter is a native/runtime context
   - choose `_NativeContainerCallHandle`

4. plain helper
   - fallback `_ContainerCallHandle`

Why this order:

- `ComponentRef` is the strongest semantic contract
- mount is a distinct runtime contract and should be recognized before generic native/plain helper fallback
- native/plain fallback remains the last branch

#### A0 Mount Runtime Behavior

The mount path should emit `MountDirective` as a committed runtime result.

Conceptually, runtime should do the equivalent of today’s `DirectiveSlotContext`
without needing compiler-only `open_directive(...)`.

That means the mount branch must own:

- selector validation/normalization
- retained mount slot identity
- child-body capture
- commit/rollback of the retained `MountDirective`

So the mount handle must:

1. enter a nested scope for the `with` body
2. retain selectors for the call site
3. on commit, publish:

```python
MountDirective(
    selectors=...,
    children=...,
    slot_id=...,
)
```

4. on rollback, restore the previous directive state

#### A0 Relationship To Existing `DirectiveSlotContext`

Phase A0 does not require deleting `DirectiveSlotContext` immediately.

The lowest-risk implementation is:

- preserve `DirectiveSlotContext` as the retained mount-state owner
- stop requiring the compiler to call `open_directive(...)`
- let `container_call(...)` runtime mount dispatch create/use a `DirectiveSlotContext` internally

So A0 should be viewed as:

- move mount selection into runtime
- not necessarily rewrite the retained directive slot storage on the first pass

That keeps the change scoped.

#### A0 Relationship To `component_call(...)`

This phase must not be blocked on removing `component_call(...)`.

The deliverable is:

- `container_call(...)` has a proper runtime dispatch seam for both:
  - retained `ComponentRef`
  - runtime mount

Only after that should compiler emission stop targeting `component_call(...)`.

That sequencing matters because it gives the compiler a real runtime target.

#### A0 Implementation Sequence

1. Introduce explicit runtime dispatch classification in `container_call(...)`.
2. Add contract check for `PyrolyzeMountFunction`.
3. Route mount contract to a runtime mount handle.
4. Make that mount handle produce retained `MountDirective` output using existing directive slot machinery where possible.
5. Add runtime tests for:
   - plain container helper
   - `with ComponentRef(...):`
   - `with mount(...):`
6. Only after those are green, begin changing compiler lowering.

#### A0 Test Matrix

Minimum new tests:

- `test_runtime_container_call_dispatches_plain_container_helper`
- `test_runtime_container_call_dispatches_component_ref`
- `test_runtime_container_call_dispatches_mount_contract`
- `test_runtime_mount_container_call_retains_mount_directive_on_rerender`
- `test_runtime_mount_container_call_rolls_back_on_failure`

Important assertions:

- container mode is selected by runtime contract, not helper name
- `MountDirective` appears in committed UI
- rerender keeps mount slot identity stable
- rollback restores previous committed directive state
- advert bindings continue to flow through slot-call semantics, untouched by this change

Tests:
- runtime container-call tests that prove:
  - ordinary container helpers still work
  - `with ComponentRef(...):` still works through `container_call(...)`
  - `with mount(...):` can emit `MountDirective` through runtime dispatch
- emitted-node assertions remain:
  - `UIElement`
  - `MountDirective`
  - `PyrolyzeMountAdvertisement`

Completion gate:
- runtime has one clear `container_call(...)` dispatch seam for containerization vs mount emission
- mount behavior is representable as a runtime branch, not a compiler-only lowering trick
- runtime tests prove retained `MountDirective` behavior through `container_call(...)`

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
- rely on the runtime dispatch seam introduced in Phase A0
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

1. add the Phase A0 runtime dispatch seam inside `container_call(...)`
2. add `PyrolyzeMountFunction`
3. update `mount(...)` to return it
4. add `ComponentMetadata.param_names`
5. add tests for those contracts before changing compiler lowering

That gives a clear runtime/typing contract before removing the compiler’s helper-name and mount-special-case logic.
