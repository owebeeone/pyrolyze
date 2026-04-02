# AST Fixes For Calling Slots Plan

## Purpose

This document turns the slot-call redesign from `ASTFixesForCallingSlots.md` into an execution plan.

## Current Status

Completed:

- Phase A
- Phase AA
- Phase AB
- Phase AC
- Phase B

Active:

- Phase C

Remaining:

- Phase D

The goal is to replace the current slot-bearing `plain_call` model with:

- a central dirt manager (`__pyr_dm`)
- slot-context-owned literal/initial-render dirt
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

The migration should be done in staged phases:

1. build the new runtime structures independently of the current compiler/lowering
2. complete the first runtime-parity layer for `SlotExpr`
3. finish the remaining runtime-only parity gaps
4. finish the remaining identity and host-integration parity gaps
5. move dirt handling onto the new dirt manager first
6. move slot-bearing expression lowering from `plain_call` to `SlotExpr`
7. remove `plain_call` completely

The key constraint is:

- do not start by rewriting the compiler to the new model
- first make the new runtime model directly testable without AST transformation

## Runtime Surfaces To Build

The new runtime surface should include at least:

- `Args[T]`
- `DM`
- `SlotExpr`
- memoized `slot_call` evaluators
- function providers for callable value/dirt
- unevaluated/clean-shape support
- optional single-call fast-path support within the `SlotExpr` model
- use of the existing slot-context literal surface for constant/global dirt

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

- name lookup
- a `bind` object used for assignment-shaped writes and deletes
- structural dirty checks

Required behaviors:

- literals/constants/globals dirty on initial render only via slot-context `literal(...)`
- locals default dirty unless explicitly rebound
- `slot_expr.evaluate(...)` overrides default dirt for bound names
- tuple/list/dict dirt checks are structural

### SlotExpr

`SlotExpr` should provide:

- `slot_expr(value_lambda, dirty_lambda)`
- `.slot_call(call_id, func_provider, args_lambda, dirt_args_lambda)`
- `single_call(func_provider, args_lambda, dirt_args_lambda)`
- `.apply_dirt_sink(dm_or_sink)`
- `.evaluate(*names)`

Required behaviors:

- per-call-site memoization
- lazy evaluation
- callable dirt support through the function provider
- callable dirt is only evaluated if no other reinvocation reason already applies
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

- slot-context `literal(...)` is dirty on initial render
- slot-context `literal(...)` is clean on rerender
- globals follow the same rule as literals
- ordinary locals default dirty unless rebound

#### DM tests: bind and lookup

- scalar bind writes dirt through `dm.bind.name = ...`
- tuple bind stores structured dirt under one name through `dm.bind.result = (...)`
- unpack bind writes structured dirt across multiple names through tuple assignment on `dm.bind`
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

- deleting a tracked name with `del dm.bind.name` removes it from the manager
- deleting an untracked name is a defined no-op or defined error, whichever is chosen
- deletion after rebinding behaves consistently

#### SlotExpr tests: single slot call

- `use_grip(STORE) or "clock"` shape
- `int(use_grip(STORE) or 0)` shape
- bare `value = use_grip(STORE)` through the single-call fast path
- fast-path single-call semantics match the general `slot_expr` path exactly
- literal function provider is the common fast path
- lambda-backed function provider supports dynamic callable dirt
- stable inputs do not reinvoke the callable
- dirty function binding reinvokes even when args are stable
- direct scalar `slot_expr(...).evaluate("value")`
- single output name binds full dirty result under one name

#### SlotExpr tests: multiple slot calls

- `use_grip(A) + use_grip(B)`
- `use_grip(A) and use_grip(B)`
- `use_grip(A) or use_grip(B)`
- tuple/list/dict value construction from multiple slot calls
- callable dirt can be supplied independently of value-arg dirt

#### SlotExpr tests: lazy control flow

- `or` does not evaluate the right side when left is truthy
- `and` does not evaluate the right side when left is falsy
- conditional expression only evaluates the selected branch
- unevaluated branch dirt is clean
- `dirty()` does not force evaluation of untaken branches
- eager forms like `any((a, b))` keep both call sites reachable

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
- external stores do not refresh without notification
- external stores refresh without reinvocation after notification

#### SlotExpr tests: component-style argument boundaries

- slot-bearing expression used as a component argument becomes its own slot expression
- it writes through the same `DM`
- call-site ids are distinct from surrounding slot-expression ids

#### SlotExpr tests: attribute/subscript dirt behavior

- attribute write followed by dirt lookup
- subscript write followed by dirt lookup
- structural updates propagate dirt in parallel with value updates

#### SlotExpr tests: handler parity and callable dirt

- plain value handler reinvokes when function dirt is true
- external store handler reinvokes source when function dirt is true
- use-effect handler reinvokes source when function dirt is true
- async-effect handler reinvokes source when function dirt is true
- mount-advert handler reinvokes source when function dirt is true

#### Compiler-lowering tests for provider choice

- direct recognized slot-helper calls lower to `LiteralFunctionProvider(...)`
- dynamic callable identity lowers to `LambdaFunctionProvider(...)`
- dynamic callable dirt lowers to `LambdaFunctionProvider(...)`
- ordinary direct calls do not lower to `LambdaFunctionProvider(...)` accidentally

### Phase A Completion Gate

Phase A is complete when:

- runtime-only tests pass
- no compiler lowering has been changed yet
- the runtime API feels stable enough to target from the AST transformer

Phase A does not include:

- shared `plain_call` handler extraction/reuse
- staged lifecycle/handler parity
- callable-dirt parity
- real call-site `SlotId`
- `invoke_dirty` parity
- `PlainCallRuntimeContext` parity

## Phase AA: Runtime Lifecycle And Handler Parity

### Goal

Bring `SlotExpr`/`SlotCallEvaluator` up to the first runtime-parity layer needed before compiler migration starts.

This phase is intentionally larger than Phase A and captures the work that should not be claimed as part of the initial foundations checkpoint.

### Deliverables

- staged per-pass `SlotExpr` commit/rollback behavior
- staged deactivation of previously-live but now-unvisited call sites
- extraction or reuse of the `plain_call` handler/binding infrastructure from `runtime/context.py`
- memoization behavior matching `plain_call` semantics for:
  - stable-input elision
  - dirty-arg reinvocation
  - callable-dirt reinvocation
  - external-store refresh without reinvocation after notification
- provider-based callable optimization:
  - `LiteralFunctionProvider`
  - `LambdaFunctionProvider`
- runtime tests covering handler parity and callable dirt

### Phase AA Tests

Suggested additions to:

- `pyrolyze/tests/test_runtime_slot_expr.py`
- optional: `pyrolyze/tests/test_runtime_slot_expr_lifecycle.py`

#### Reachability and deactivation tests

- `use_grip(A) or use_grip(B)`:
  - first pass reaches `B`
  - second pass skips `B`
  - `B` deactivates only after successful commit
- `use_grip(A) and use_grip(B)`:
  - symmetric reachability behavior
- `any((use_grip(A), use_grip(B)))`:
  - both call sites remain reachable every pass
- explicit `if`/assignment form equivalent to the short-circuit version matches liveness semantics

#### Exception and staging tests

- one call site evaluates, later expression step raises
- staged dirty bindings are not committed
- staged deactivations are not committed
- previously committed call-site state remains intact

#### Handler parity tests

- plain value handler parity
- external store handler parity:
  - no reinvoke on stable inputs
  - no refresh without notification
  - refresh without reinvoking original callable after notification
- use effect handler parity:
  - post-commit run
  - cleanup on deactivation
- async effect handler parity:
  - post-commit start
  - cancellation on deactivation
- mount advertisement handler parity:
  - publish on commit
  - withdraw on deactivation

#### Callable-dirt and provider tests

- stable inputs do not reinvoke the callable
- callable dirt reinvokes even when args are stable
- literal function provider is the common fast path
- lambda-backed function provider supports dynamic callable dirt
- direct stable call sites do not accidentally use the lambda-backed provider

### Phase AA Completion Gate

Phase AA is complete when:

- `SlotExpr` reuses the shared handler family instead of a local duplicate
- handler-family parity is green in direct runtime tests
- staged commit/rollback behavior is verified
- callable-dirt support is green in direct runtime tests
- provider optimization is implemented and covered by tests

## Phase AB: Remaining Runtime-Only Parity Gaps

### Goal

Finish the remaining `plain_call` parity items that do not require real
compiler-generated call-site identity or real host integration.

### Deliverables

- `invoke_dirty` parity
- `PlainCallRuntimeContext` parity or an explicit documented replacement
- registration/deactivation pairing on commit boundaries
- avoidance of unnecessary retained raw-result references
- fast-path/general-path parity for `single_call(...)` vs `slot_call(...)`

### Phase AB Tests

Suggested additions to:

- `pyrolyze/tests/test_runtime_slot_expr.py`
- optional: `pyrolyze/tests/test_runtime_slot_expr_lifecycle.py`

#### Reachability and deactivation tests

- `use_grip(A) or use_grip(B)`:
  - first pass reaches `B`
  - second pass skips `B`
  - `B` deactivates only after successful commit
- `use_grip(A) and use_grip(B)`:
  - symmetric reachability behavior
- `any((use_grip(A), use_grip(B)))`:
  - both call sites remain reachable every pass
- explicit `if`/assignment form equivalent to the short-circuit version matches liveness semantics

#### Exception and staging tests

- one call site evaluates, later expression step raises
- staged dirty bindings are not committed
- staged deactivations are not committed
- previously committed call-site state remains intact

#### Remaining plain-call parity tests

- `invoke_dirty` forces reinvocation in `SlotExpr`
- runtime-context injection parity for callables that request it
- `single_call(...)` and `slot_call(...)` have identical reinvocation and lifecycle behavior

#### Registration pairing tests

- no committed registration without later possible deactivation
- lifecycle changes appear only after successful commit

### Phase AB Completion Gate

Phase AB is complete when:

- the remaining runtime-only semantic gaps relative to `plain_call` are closed or explicitly documented as intentional differences
- `invoke_dirty` and runtime-context behavior are covered by tests
- pairing and retained-reference behavior are covered by tests
- the only remaining parity gaps are call-site identity and host integration
- the runtime surface is trustworthy enough to begin compiler migration

## Phase AC: Identity And Host Integration Parity Gaps

### Goal

Finish the remaining `plain_call` parity items that require:

- real call-site identity
- real host/runtime integration

### Deliverables

- call-site identity carried as a real compiler-generated `SlotId`
- real runtime host integration for invalidation and mount-advert publication, or an explicit documented shim-equivalence boundary
- proof that runtime identity is keyed by `SlotId`, not evaluator parameter naming
- proof that fast-path and general-path evaluation use identical host semantics

### Phase AC Tests

Suggested additions to:

- `pyrolyze/tests/test_runtime_slot_expr.py`
- optional: `pyrolyze/tests/test_runtime_slot_expr_lifecycle.py`

#### Call-site identity tests

- each `slot_call` carries a persistent call-site `SlotId`
- evaluator parameter name changes do not change runtime identity
- different `SlotId`s do change runtime identity
- cached binding reuse and deactivation are keyed by `SlotId`

#### Host integration or shim-equivalence tests

- external-store invalidation reaches the real runtime host, or the shim is proven equivalent
- mount-advert publish/withdraw uses the real runtime host, or the shim is proven equivalent
- post-commit callbacks use the real runtime host, or the shim is proven equivalent
- `single_call(...)` and `slot_call(...)` use the same host path

### Phase AC Completion Gate

Phase AC is complete when:

- runtime identity is carried by real `SlotId`
- host behavior is integrated or explicitly justified by shim-equivalence tests
- no remaining `plain_call` parity gap depends on runtime identity or host behavior

## Phase B: Move Dirt Handling To DM First

### Goal

Adopt the new dirt manager before replacing `plain_call`.

### Why

This isolates dirt-tracking migration from expression-lowering migration.

### Deliverables

- existing lowering writes dirt through `DM`
- compatibility path from current call model to the new dirt manager
- focused tests showing existing transformed behavior still works with `DM`
- explicit boundary rule:
  - keep `__pyr_dirty_state` as the caller/callee transport parameter
  - materialize `__pyr_dm = __pyr_dm_from_dirty_state(__pyr_dirty_state)` at function entry
  - use `__pyr_dm.bind.*` for in-function dirt reads and writes
- direct slotted-call lowering writes dirty results straight into `__pyr_dm.bind.*`
- delete lowering mirrors value deletion with:
  - `del name`
  - `del __pyr_dm.bind.name`
- golden coverage includes a dedicated delete case

### Phase B Tests

These tests should target current transformed behavior but verify the new dirt manager semantics.

Suggested files:

- `pyrolyze/tests/test_ast_phaseX_dirty_manager_integration.py`
- plus updates to existing AST/compiler execution tests

#### Integration tests

- transformed output initializes `__pyr_dm` from incoming `__pyr_dirty_state`
- existing slotted call path updates `DM` instead of old hidden dirt channel storage
- rebinding and unpacking through transformed code land in `DM`
- deletion lowers to `del __pyr_dm.bind.name`
- direct slotted assignments no longer require intermediate dirty temp locals before writing to `DM`
- attribute/subscript paths update `DM`
- child/component/container calls still project outgoing dirt through `dirtyof(...)` in Phase B

#### Golden expectations

- accept that some goldens may break
- only update goldens that are expected to remain valid under this phase
- do not chase unrelated golden fallout yet

### Phase B Completion Gate

Phase B is complete when:

- transformed code can use `DM` successfully while `plain_call` still exists
- expected goldens are updated
- compiler-emitted slotted assignments bind dirty results directly into `DM`
- compiler-emitted deletes mirror into `del __pyr_dm.bind.name`
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
- compiler-emitted call sites use the current provider API:
  - `LiteralFunctionProvider(...)` by default
  - `LambdaFunctionProvider(...)` only for genuinely dynamic callable identity or callable dirt
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
- transformed output contains the correct provider choice for each call site
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
Callable provider selection rule for compiler lowering:

- `LiteralFunctionProvider(...)` is the default and expected lowering
- use `LiteralFunctionProvider(func_ref)` when the compiler already knows the slot-bearing callable as one direct stable reference
- use `LambdaFunctionProvider(func_lambda, dirt_lambda)` only when callable identity or callable dirt depends on dynamic lowered state
- do not emit `LambdaFunctionProvider(...)` for ordinary direct slot-helper calls just because it is more general

This rule should be treated as part of the optimization contract, not as an optional implementation detail.
