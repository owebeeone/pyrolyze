# AST Fixes For Calling Slots Plan

## Purpose

This document turns the slot-call redesign from `ASTFixesForCallingSlots.md` into an execution plan.

The goal is to replace the current slot-bearing `plain_call` model with:

- a central dirt manager (`__pyr_dm`)
- a new `SlotExpr` runtime
- memoized `slot_call` evaluators
- structural dirty binding at `evaluate(...)`

while keeping the migration incremental enough to debug.

## Scope

This plan covers:

- runtime structures needed for the new model
- runtime-only tests that validate the model before compiler work starts
- compiler migration phases
- final removal of `plain_call`

This plan does not include:

- slot-bearing comprehensions
- slot-bearing walrus expressions

Those remain unsupported in Phase 1 of the design.

## High-Level Strategy

The migration should be done in four phases:

1. build the new runtime structures independently of the current compiler/lowering
2. move dirt handling onto the new dirt manager first
3. move slot-bearing expression lowering from `plain_call` to `SlotExpr`
4. remove `plain_call` completely

The key constraint is:

- do not start by rewriting the compiler to the new model
- first make the new runtime model directly testable without AST transformation

## Runtime Surfaces To Build

The new runtime surface should include at least:

- `Args[T]`
- `DM`
- `SlotExpr`
- memoized `slot_call` evaluators
- unevaluated/clean-shape support
- optional single-call fast-path support within the `SlotExpr` model

### Args

Conceptually:

```python
@dataclass(frozen=True)
class Args[T = Any]:
    args: tuple[T, ...]
    kwds: dict[str, T]

    def call(self, func: Callable[..., Any]) -> Any:
        return func(*self.args, **self.kwds)

    @classmethod
    def capture(cls, *args, **kwds) -> "Args[T]":
        return cls(tuple(args), dict(kwds))
```

Required properties:

- tuple-backed positional storage
- keyword storage
- one carrier shape for both value params and dirt params
- no special-case dirt carrier

### DM

The central dirt manager should conceptually provide:

- `__pyr_literal()`
- name lookup/bind
- structural bind
- structural unpack
- deletion
- structural dirty checks

Required behaviors:

- literals/constants/globals dirty on initial render only
- locals default dirty unless explicitly rebound
- `slot_expr.evaluate(...)` overrides default dirt for bound names
- tuple/list/dict dirt checks are structural

### SlotExpr

`SlotExpr` should provide:

- `slot_expr(value_lambda, dirty_lambda)`
- `.slot_call(call_id, func, args_lambda, dirt_args_lambda)`
- `.apply_dirt_sink(dm_or_sink)`
- `.evaluate(*names)`

Required behaviors:

- per-call-site memoization
- lazy evaluation
- `dirty()` must not force unevaluated branches
- same structural shape for `eval()` and `dirty()`
- one output name stores the full dirty structure
- many output names unpack dirty structure structurally
- allow an optimized single-call lowering/runtime path without changing semantics

### Slot Call Evaluator

Each evaluator must support:

- `eval()`
- `dirty()`

Required behaviors:

- memoized value result
- memoized dirty result
- no re-execution on repeated access
- clean dirt result for unevaluated path
- support the same return-shape families currently supported by `plain_call`

This includes at least:

- simple scalar returns
- tuple returns
- state-like returns
- effect-like returns
- storage-driven returns

## Phase A: Build Runtime Structures In Isolation

### Goal

Create the new runtime pieces without changing current compiler lowering.

### Deliverables

- `pyrolyze/src/pyrolyze/runtime/dirt.py`
- `pyrolyze/src/pyrolyze/runtime/slot_expr.py`
- `Args[T]`
- `DM`
- `SlotExpr`
- memoized evaluator implementation
- helper surface for unevaluated clean shape

### Phase A Tests

These tests should be runtime-only tests. They should not rely on transformed source.

Suggested files:

- `pyrolyze/tests/test_runtime_slot_expr.py`
- `pyrolyze/tests/test_runtime_dirt.py`
- optional: `pyrolyze/tests/test_runtime_slot_expr_shapes.py`

#### Args tests

- `Args.capture(1, 2, x=3)` stores tuple positional args and keyword args
- `Args.call(...)` correctly invokes plain functions
- value-side and dirt-side args have identical shape behavior

#### DM tests: literals and defaults

- `__pyr_literal()` is dirty on initial render
- `__pyr_literal()` is clean on rerender
- globals follow the same rule as literals
- ordinary locals default dirty unless rebound

#### DM tests: bind and lookup

- scalar bind writes dirt for a name
- tuple bind stores structured dirt under one name
- unpack bind writes structured dirt across multiple names
- rebinding a name replaces previous dirt
- shadowing semantics match value binding

#### DM tests: structural dirty checks

- scalar `False` is clean
- scalar `True` is dirty
- tuple with all-false entries is clean
- tuple with any true entry is dirty
- list with any dirty entry is dirty
- dict with any dirty value is dirty

#### DM tests: deletion

- deleting a tracked name removes it from the manager
- deleting an untracked name is a defined no-op or defined error, whichever is chosen
- deletion after rebinding behaves consistently

#### SlotExpr tests: single slot call

- `use_grip(STORE) or "clock"` shape
- `int(use_grip(STORE) or 0)` shape
- bare `value = use_grip(STORE)` through the single-call fast path
- fast-path single-call semantics match the general `slot_expr` path exactly
- direct scalar `slot_expr(...).evaluate("value")`
- single output name binds full dirty result under one name

#### SlotExpr tests: multiple slot calls

- `use_grip(A) + use_grip(B)`
- `use_grip(A) and use_grip(B)`
- `use_grip(A) or use_grip(B)`
- tuple/list/dict value construction from multiple slot calls

#### SlotExpr tests: lazy control flow

- `or` does not evaluate the right side when left is truthy
- `and` does not evaluate the right side when left is falsy
- conditional expression only evaluates the selected branch
- unevaluated branch dirt is clean
- `dirty()` does not force evaluation of untaken branches

#### SlotExpr tests: multi-result returns

- `use_state(3)` returns tuple-shaped value and tuple-shaped dirt
- `.evaluate("val", "func")` unpacks both value and dirt
- `.evaluate("result")` stores tuple-shaped value and tuple-shaped dirt under one name
- shape mismatch on evaluate raises

#### SlotExpr tests: nested slot-call arguments

- a later slot call consuming `v1.eval()` in its arg lambda
- matching dirt lambda consuming `v1.dirty()`
- nested dependency preserves memoization
- nested dependency preserves lazy evaluation

#### SlotExpr tests: rerender clean shape

- rerender with unchanged inputs yields clean scalar dirt
- rerender with unchanged tuple result yields clean tuple dirt of same shape
- rerender with skipped branch preserves clean shape

#### SlotExpr tests: component-style argument boundaries

- slot-bearing expression used as a component argument becomes its own slot expression
- it writes through the same `DM`
- call-site ids are distinct from surrounding slot-expression ids

#### SlotExpr tests: attribute/subscript dirt behavior

- attribute write followed by dirt lookup
- subscript write followed by dirt lookup
- structural updates propagate dirt in parallel with value updates

### Phase A Completion Gate

Phase A is complete when:

- runtime-only tests pass
- no compiler lowering has been changed yet
- the runtime API feels stable enough to target from the AST transformer

## Phase B: Move Dirt Handling To DM First

### Goal

Adopt the new dirt manager before replacing `plain_call`.

### Why

This isolates dirt-tracking migration from expression-lowering migration.

### Deliverables

- existing lowering writes dirt through `DM`
- compatibility path from current call model to the new dirt manager
- focused tests showing existing transformed behavior still works with `DM`

### Phase B Tests

These tests should target current transformed behavior but verify the new dirt manager semantics.

Suggested files:

- `pyrolyze/tests/test_ast_phaseX_dirty_manager_integration.py`
- plus updates to existing AST/compiler execution tests

#### Integration tests

- existing slotted call path updates `DM` instead of old hidden dirt channel storage
- rebinding and unpacking through transformed code land in `DM`
- deletion lowers to `__pyr_dm.__pyr_del(...)`
- attribute/subscript paths update `DM`

#### Golden expectations

- accept that some goldens may break
- only update goldens that are expected to remain valid under this phase
- do not chase unrelated golden fallout yet

### Phase B Completion Gate

Phase B is complete when:

- transformed code can use `DM` successfully while `plain_call` still exists
- expected goldens are updated
- unrelated goldens remain intentionally untouched

## Phase C: Replace Slot-Bearing Expression Lowering With SlotExpr

### Goal

Move slot-bearing expressions from `plain_call` lowering to `SlotExpr`.

### Deliverables

- AST transform for slot-bearing expressions produces:
  - value lambda
  - dirty lambda
  - `.slot_call(...)` chain
  - `.apply_dirt_sink(...)`
  - `.evaluate(...)`
- recursive extraction of nested slot-bearing calls
- unsupported diagnostics for:
  - slot-bearing walrus
  - slot-bearing comprehensions

### Phase C Subphases

#### Phase C1: Basic expression lowering

Cover:

- single slot-bearing call in expression
- boolean operators
- arithmetic/coercion wrappers
- conditional expressions
- optional compiler fast path for expressions that are exactly one slot-bearing call

#### Phase C2: Multi-call and structured returns

Cover:

- multiple slot calls in one expression
- tuple/list/dict structure
- `use_state(...)` style multi-result returns
- exact `evaluate(...)` shape matching

#### Phase C3: Nested slot-bearing args and component boundaries

Cover:

- recursive extraction for nested slot-bearing calls
- slot-bearing component arguments
- attribute/subscript dirt interactions where relevant

### Phase C Tests

Suggested files:

- `pyrolyze/tests/test_ast_slot_expr_rewrite.py`
- `pyrolyze/tests/test_ast_slot_expr_execution.py`
- updates to existing compiler golden tests

#### Rewrite tests

- transformed output contains `slot_expr(...)`
- transformed output contains `.slot_call(...)`
- transformed output contains `.apply_dirt_sink(...)`
- transformed output contains `.evaluate(...)`
- transformed output no longer lowers slot-bearing expressions through `plain_call`
- if a single-call fast path is emitted, it is still part of the `SlotExpr` runtime contract rather than a `plain_call` fallback

#### Execution tests mirroring doc examples

- `value = use_grip(STORE)` fast path
- `value = use_grip(STORE) or "clock"`
- `count = int(use_grip(STORE) or 0)`
- `total = use_grip(A) + use_grip(B)`
- `value = x if use_grip(STORE) else y`
- `val, func = use_state(3)`
- `result = use_state(3)` then keep tuple-shaped dirt under one name
- slot call with later arg lambda using prior evaluator result

#### Unsupported-form tests

- slot-bearing walrus raises at walrus location
- slot-bearing list comprehension raises
- slot-bearing dict comprehension raises

#### Golden expectations

- expect widespread golden breakage
- only fix goldens expected to work under the new slot-expression lowering
- do not burn time cleaning unrelated goldens during the migration

### Phase C Completion Gate

Phase C is complete when:

- slot-bearing expressions lower through `SlotExpr`
- unsupported forms fail with intentional diagnostics
- expected goldens are updated
- `plain_call` is no longer needed for slot-bearing expression lowering

## Phase D: Remove plain_call Completely

### Goal

Delete the old `plain_call` path and finish the migration.

### Deliverables

- all remaining lowering paths use `SlotExpr`
- `plain_call` removed
- compatibility shims removed
- dead tests removed or updated

### Phase D Tests

- search-based test or audit confirming no runtime/compiler path still targets `plain_call`
- full compiler execution suite where expected
- full relevant golden suite where expected
- regression check for all slot-expression examples from earlier phases

### Phase D Completion Gate

Phase D is complete when:

- `plain_call` no longer exists
- all intended lowering goes through `SlotExpr`
- expected goldens and regression tests pass

## Diagnostics

All new rejected-form diagnostics should follow the existing AST-transform error reporting style:

- stable error codes
- file/line/column location
- relevant node class
- suggested fix where applicable

Phase C must specifically add diagnostics for:

- slot-bearing walrus operators
- slot-bearing comprehensions

## Suggested Implementation Order

1. add runtime types and runtime-only tests
2. stabilize `DM`
3. stabilize `SlotExpr`
4. wire `DM` under current lowering
5. wire `SlotExpr` under new lowering
6. remove `plain_call`

## Stop Conditions

Pause and revise if:

- `DM` semantics become inconsistent with current compiler assumptions
- `SlotExpr` cannot represent one of the current `plain_call` return-shape families cleanly
- golden fallout suggests hidden dependence on `plain_call` behavior not covered in the design
- keyed loop + dirt interaction for attribute/subscript assignment proves materially different from the current assumptions

## Summary

The key discipline in this plan is:

- first make the new runtime model real
- then move dirt onto it
- then move expression lowering onto it
- then remove the old path

That keeps the redesign technically testable at every stage instead of trying to swap the entire compiler/runtime contract at once.
