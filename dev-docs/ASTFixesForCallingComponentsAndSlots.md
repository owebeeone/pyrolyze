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

## Fix A: Runtime-Resolved Dynamic ComponentRef Calls

The chosen solution for indirect `ComponentRef` calls is:

- keep the current static path for direct named component calls
- add a dynamic fallback path for valid `ComponentRef` calls whose parameter names cannot be resolved statically

This is preferred over trying to infer parameter names from `ComponentRef[[...]]` annotations, because those annotations carry argument types, not source parameter names.

### Trigger

If Phase 5 sees:

- a call through a local/name typed as `ComponentRef[...]`
- but `state.component_param_names` has no entry for that name

then it should lower to a runtime helper instead of raising `PYR-E-PHASE5-COMPONENT-CALL`.

### Lowering shape

Conceptually:

```python
__pyr_ctx.component_call_dynamic(
    slot_id=__pyr_slot_1,
    component_ref=emit,
    args=(),
    kwargs={"label": label},
    dirty_kwargs={"label": __pyr_dirty_state.label},
)
```

or for packed kwargs:

```python
__pyr_ctx.component_call_dynamic(
    slot_id=__pyr_slot_1,
    component_ref=emit,
    args=(),
    kwargs={"kwds": {"label": label}},
    dirty_kwargs={"kwds": __pyr_dirtyof(label=__pyr_dirty_state.label)},
)
```

Exact helper signature is flexible, but the important part is:

- compiler preserves slot id and dirty information
- runtime resolves the callable signature

### Runtime resolution

The helper should:

1. inspect the component ref runtime object
2. prefer `_pyrolyze_meta` / known component metadata when available
3. otherwise fall back to `inspect.signature(...)`
4. recover ordered parameter names
5. dispatch through existing component-call machinery

This should support:

- functions
- bound methods
- callable objects / functors
- class constructor-like callables where that is already valid in runtime

### Why this is the chosen solution

- handles dict lookups and other indirect refs naturally
- avoids overloading `ComponentRef[[...]]` annotations with information they do not actually contain
- matches the intended dynamic function-table use case
- keeps the static path fast for direct component refs

## Fix B: Hoist Recognized Slotted Calls Out Of Enclosing Expressions

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
2. Add runtime helper, for example `component_call_dynamic(...)`.
3. Lower unresolved-but-valid `ComponentRef` calls to that helper instead of raising.
4. Reuse existing component child bookkeeping once runtime signature resolution succeeds.

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
