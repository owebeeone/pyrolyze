# AST Fixes For Calling Components And Slots

## Problem

Two Phase 5 compiler gaps are now pinned by red tests:

1. Annotated local `ComponentRef` calls can still fail to lower when the value comes from a lookup.
2. Slotted or hook-like calls such as `use_grip(...)` are not lowered correctly when they appear inside a larger expression.

These show up today as:

- `PYR-E-PHASE5-COMPONENT-CALL` for code like:

```python
emit: ComponentRef[[dict[str, Any]]] = EMITTERS["leaf"]
emit(kwds={"label": label})
```

and also for:

```python
emit: ComponentRef[[str]] = EMITTERS["leaf"]
emit(label=label)
```

- missing `call_plain(...)` lowering for code like:

```python
value = use_grip(STORE) or "clock"
count = int(use_grip(STORE) or 0)
```

## Desired Behavior

### ComponentRef Variables

If a local name is explicitly annotated as `ComponentRef[...]`, then a call through that name should lower as a component call, even if the runtime value came from:

- a dict lookup
- an attribute read
- another variable

The lowering should not require the initializer expression itself to be a direct named component reference.

### Slotted / Hook Calls In Expressions

If a call is recognized as a slotted helper or a hook-like plain call with dirty-return semantics, the compiler should be able to lower it even when it is nested inside:

- boolean operators
- unary/binary operators
- coercions like `int(...)`
- tuple/list/dict literals
- function arguments
- comparisons

The lowered code must preserve:

- source evaluation order
- Python short-circuit behavior
- single evaluation of the slotted call
- correct dirty binding

## Root Cause

### 1. ComponentRef Local Calls

Current Phase 5 lowering keys component call rewriting off:

- a named call target
- `state.component_param_names[call_name]`

The first condition is satisfied by:

```python
emit(...)
```

But the second is not, because `component_param_names` is populated for known component definitions, not for local annotated aliases like `emit`.

The compiler already records callable kind from `AnnAssign`, so it knows `emit` is a `ComponentRef`. It does not currently carry parameter names alongside that local callable-kind information.

### 2. Slotted Calls In Larger Expressions

Current lowering handles:

- assignment forms like `value = use_grip(...)`
- statement-expression calls

It does not hoist recognized slotted/hook calls out of enclosing expressions before the rest of the expression is lowered.

As a result, code like:

```python
value = use_grip(STORE) or "clock"
```

never passes through the `call_plain(...)` lowering path for the inner call.

## Proposed Fix

This work should now be treated as two adjacent compiler phases:

- Phase C:
  - lower slot-bearing expressions to `slot_expr`
  - reject walrus/comprehension forms in slot-bearing expressions
- Phase CA:
  - fix annotated local `ComponentRef` alias/lookup calls whose parameter names are not recoverable from the current static table
  - specifically patterns like:

```python
emit: ComponentRef[[dict[str, Any]]] = EMITTERS["leaf"]
emit(kwds={"label": label})
```

## Fix A / Phase CA: Runtime-Resolved Dynamic ComponentRef Calls

The chosen solution for indirect `ComponentRef` calls is:

- keep the current static path for direct named component calls
- keep using the existing `leaf_call(...)` / `container_call(...)` runtime surfaces
- add a dynamic dirty-args path for valid `ComponentRef` calls whose parameter names cannot be resolved statically

This is preferred over trying to infer parameter names from `ComponentRef[[...]]` annotations, because those annotations carry argument types, not source parameter names.
It also avoids runtime `inspect.signature(...)` work, because `ComponentRef` values already carry `_pyrolyze_meta`, and that metadata should be the authoritative source of parameter names and component kind.

### Trigger

If Phase 5 sees:

- a call through a local/name typed as `ComponentRef[...]`
- but `state.component_param_names` has no entry for that name

then it should lower to the existing component call path with dynamic dirty args instead of raising `PYR-E-PHASE5-COMPONENT-CALL`.

### Lowering shape

Conceptually, for a leaf component call:

```python
__pyr_ctx.leaf_call(
    __pyr_slot_1,
    emit,
    label=label,
    __pyr_dyn_dirty_args=__pyr_Args.capture(label=__pyr_dm.bind.label),
)
```

or for packed kwargs:

```python
__pyr_ctx.leaf_call(
    __pyr_slot_1,
    emit,
    kwds={"label": label},
    __pyr_dyn_dirty_args=__pyr_Args.capture(
        kwds={"label": __pyr_dm.bind.label},
    ),
)
```

Exact helper signature is flexible, but the important part is:

- compiler preserves slot id and dirt information
- compiler passes dynamic dirt as an `Args`-shaped parallel carrier
- runtime resolves parameter names and component kind from `ComponentRef._pyrolyze_meta`
- runtime builds the callee dirty state from metadata plus `__pyr_dyn_dirty_args`

### Runtime resolution

The existing `leaf_call(...)` / `container_call(...)` machinery should:

1. read `_pyrolyze_meta` from the runtime `ComponentRef`
2. recover:
   - component kind (`leaf` vs `container`)
   - ordered parameter names
3. map runtime `Args` + `kwargs` onto those parameter names
4. map `__pyr_dyn_dirty_args` onto those same parameter names
5. construct the correct callee dirty state object
6. dispatch through the existing `leaf_call` / `container_call` machinery

This should support:

- functions
- bound methods
- callable objects / functors
- class constructor-like callables where that is already valid in runtime

It should not require Python signature inspection in the normal `ComponentRef` path. All supported `ComponentRef` values should already have the needed metadata through `pyrolyze_component_ref(...)`.

### Why names are needed

The key problem is not ordinary Python invocation. The runtime already knows how to call a function with positional and keyword arguments.

The missing piece is dirty-state construction.

For dynamic `ComponentRef` calls, `leaf_call(...)` and `container_call(...)` need to know which dirt flag belongs to which formal parameter name so they can build the callee dirty state correctly.

That is why the dynamic fallback should pass:

- normal value arguments
- parallel `__pyr_dyn_dirty_args`

instead of trying to pre-build a statically shaped dirty-state object in the compiler.

### Dynamic dirty transport

For dynamic `ComponentRef` calls, the compiler should preserve the current value-side argument structure and add a parallel `__pyr_dyn_dirty_args` carrier.

Conceptually:

```python
emit: ComponentRef[[str, int], None] = EMITTERS["leaf"]
emit(formatted_text, maxwidth=width)
```

lowers roughly to:

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

At runtime:

- metadata provides the formal parameter names
- value args bind to those names
- `__pyr_dyn_dirty_args` binds to those same names
- the runtime builds the real callee dirty-state object from that mapping

### Leaf and container dispatch

There are currently two `ComponentRef` call families:

- leaf
- container

The dynamic helper should use metadata to decide which path to take.

Leaf example:

```python
emit: ComponentRef[[str], None] = EMITTERS["leaf"]
emit(label)
```

lowers roughly to:

```python
__pyr_ctx.leaf_call(
    __pyr_slot_1,
    emit,
    label,
    __pyr_dyn_dirty_args=__pyr_Args.capture(__pyr_dm.bind.label),
)
```

Container example:

```python
wrap: ComponentRef[[str], None] = CONTAINERS["card"]
wrap(title, children=body)
```

lowers roughly to:

```python
__pyr_ctx.container_call(
    __pyr_slot_1,
    wrap,
    title,
    children=body,
    __pyr_dyn_dirty_args=__pyr_Args.capture(
        __pyr_dm.bind.title,
        children=__pyr_dm.bind.body,
    ),
)
```

Then runtime:

- reads `_pyrolyze_meta`
- resolves parameter names
- builds the correct dirty state
- continues through the existing `leaf_call(...)` or `container_call(...)` path

### Why this is the chosen solution

- handles dict lookups and other indirect refs naturally
- avoids overloading `ComponentRef[[...]]` annotations with information they do not actually contain
- uses existing `_pyrolyze_meta` instead of runtime signature inspection
- keeps dirty-state construction where it belongs: inside the existing leaf/container runtime boundary
- matches the intended dynamic function-table use case
- keeps the static path fast for direct component refs

## Fix B / Phase C: Hoist Recognized Slotted Calls Out Of Enclosing Expressions

Add an expression-rewrite pass in Phase 5 that:

1. walks expression trees
2. finds recognized slotted/hook calls
3. replaces each with a temporary name
4. emits setup statements before the enclosing statement

For:

```python
value = use_grip(STORE) or "clock"
```

lower roughly to:

```python
__pyr_value_dirty, __pyr_tmp_1 = __pyr_ctx.call_plain(...)
value = __pyr_tmp_1 or "clock"
```

For:

```python
count = int(use_grip(STORE) or 0)
```

lower roughly to:

```python
__pyr_count_dirty, __pyr_tmp_1 = __pyr_ctx.call_plain(...)
count = int(__pyr_tmp_1 or 0)
```

### Scope

This hoisting should apply to:

- assignment RHS expressions
- return expressions
- call arguments
- container literals
- conditional expressions

It should not rewrite arbitrary side-effecting calls. It should only trigger for calls already recognized by the compiler as:

- slotted helpers
- hook-like imported helpers resolved by return contract/runtime signature

### Ordering constraints

Hoisted temporaries must preserve left-to-right evaluation order.

For boolean operators and comparisons, the compiler must preserve Python semantics. The simplest safe first cut is:

- only hoist inside expression forms where the slotted call itself is always evaluated
- add explicit boolean short-circuit support carefully after that if needed

However, the current failing `use_grip(...) or fallback` case does always evaluate the left side, so it is safe to support immediately.

## Implementation Outline

### Part 1: Dynamic ComponentRef Calls

1. Teach Phase 5 to distinguish:
   - direct named component calls with known parameter names
   - indirect `ComponentRef` calls with unresolved parameter names
2. Extend `leaf_call(...)` / `container_call(...)` to accept dynamic dirty args.
3. Lower unresolved-but-valid `ComponentRef` calls to those existing helpers instead of raising.
4. Reuse existing component child bookkeeping once runtime metadata resolution succeeds.

### Part 2: Slotted Expression Hoisting

1. Add expression hoisting helper for recognized slotted/hook calls.
2. Run it before normal assignment/return lowering for enclosing expressions.
3. Reuse existing `call_plain(...)` lowering logic for the extracted call.
4. Rewrite the original expression to reference the temporary value.

## Test Plan

Red tests already added:

- `test_phase5_lowers_component_ref_variable_call_from_annotated_lookup`
- `test_phase5_lowers_component_ref_variable_call_from_annotated_lookup_with_named_kwarg`
- `test_phase5_hoists_use_grip_inside_or_expression`
- `test_phase5_hoists_use_grip_inside_int_coercion_expression`

Additional tests to add during the fix:

- `ComponentRef` alias propagated through one more local variable
- `ComponentRef[[dict[str, Any]]]` imported alias case
- `use_grip(...)` inside function-call arguments
- `use_grip(...)` inside tuple construction
- `use_grip(...)` inside comparison/coercion combinations

## Recommended Order

1. Fix indirect `ComponentRef` lowering first with the runtime-resolved path.
2. Add expression hoisting for `use_grip(...)` / slotted calls next.
3. Expand regression coverage after both red tests go green.

## Non-Goals

This doc does not propose:

- changing runtime semantics
- widening support to arbitrary dynamic call targets
- changing backend behavior

This is specifically a Phase 5 AST/lowering fix.
