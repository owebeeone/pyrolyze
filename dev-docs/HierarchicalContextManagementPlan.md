# Hierarchical Context Management Plan

## Purpose

This document breaks the hierarchical app-context work into an implementation
order that keeps the surface testable from the start and avoids mixing syntax,
runtime, and reactivity concerns in one jump.

The main constraints for the first implementation are:

- provider syntax is `with app_context_override[K1, K2, ...](v1, v2, ...):`
- reader syntax is `use_app_context(key)`
- provider keys are structurally fixed at the slot
- reader keys are dynamic and slot-reactive, like `use_grip(...)`
- authored hierarchical app context is empty at root by default
- `None` means "fall through to parent" for a provided key
- mount resolution does not read app context
- when provided app-context values change, only readers of the changed keys are
  notified


## Rollout Order

The implementation should proceed in this order:

1. AST surface and golden tests only
2. Runtime surface skeleton with no real user reads
3. Per-key reactive value stream plumbing
4. Provider/reader runtime integration
5. Documentation pass after behavior is stable
6. Structural and rerender stress coverage as deferred follow-on work

The important rule is: do not start with the full runtime. Lock the authored
surface and lowering shape first.


## Phase 1: AST Surface And Golden Tests

### Goal

Teach the compiler to understand the new syntax and lower it into explicit
runtime calls, without yet needing the full semantics to be implemented.

### Scope

- recognize `with app_context_override[...] (...):`
- reject unsupported forms cleanly
- keep `use_app_context(key)` as an ordinary slotted plain-call helper surface
- add golden/lowered-source tests
- add parser/lowering diagnostics before runtime behavior exists

### First-Cut Constraints

- provider helper name is fixed: `app_context_override`
- provider form is only valid in `with ...:` Pyrolyze structural position
- subscripts must resolve to a static key tuple shape
- allowed key syntax in `[]`:
  - `NAME`
  - `module.NAME`
  - `Class.NAME`
- rejected in `[]`:
  - calls
  - indexing
  - lambdas
  - conditionals
  - arbitrary computed expressions
- value arity must match key arity in lowering validation if it can be checked
  statically; otherwise runtime must validate it

### Lowering Target

The provider should lower to one dedicated runtime entrypoint.

Recommended target:

```python
if (
    __pyr_dirty_expr_for_provider_args
    or __pyr_dirty_expr_for_statements
    or __pyr_ctx.visit_slot_and_dirty(__pyr_slot)
):
    with __pyr_ctx.open_app_context_override(__pyr_slot, __pyr_keys_tuple, *values) as __pyr_ctx_N:
        ...
```

where:

- the lowering should use the normal PyRolyze guard pattern rather than an
  unconditional `with`
- provider argument dirty checks must participate in the guard
- nested body dirty checks must participate in the guard
- slot dirty state must participate in the guard
- the runtime entrypoint should receive the provider slot identity in the same
  way other retained structural nodes do
- `__pyr_keys_tuple` is a compiler-produced tuple of resolved key references
- the runtime owns validation and retained provider lifecycle

This matters because provider lifetime is structural and retained:

- it must only reopen when the normal structural guard says the slot is dirty
- it must not bypass the ordinary rerender/commit path
- it should align with existing `with` lowerings such as mounts and containers

### Tests

Add golden/AST tests for:

- simple one-key provider
- multi-key provider
- nested providers
- lowering includes the correct dirty guard shape
- invalid computed provider keys
- invalid provider use outside supported `with` position
- invalid `with ... as ...` usage
- lowering shape across component and loop bodies

### Exit Criteria

- golden tests pass
- diagnostics are clear
- no real user-facing runtime semantics are required yet


## Phase 2: Runtime Surface Skeleton

### Goal

Add the runtime types and entrypoints needed for the lowered surface to run,
without yet trying to finish selective notification.

### Scope

- add `app_context_override` helper surface in `pyrolyze.api`
- add `use_app_context` helper surface
- add retained override slot/context kind
- add runtime entrypoint:
  - `open_app_context_override(keys=..., values=...)`
- thread effective app-context lookup through ordinary scope inheritance
- thread effective app-context lookup across component child `RenderContext`
  creation

### Runtime Types

Recommended additions:

- `AppContextOverrideSlotContext`
- `AppContextOverrideBinding` or equivalent retained binding object
- `AppContextLookup` protocol
- `OverlayAppContextLookup`

The provider slot should own:

- fixed key tuple
- committed value tuple
- effective local overlay view
- per-key subscriber tracking handles

### Root Model

- authored hierarchical app-context root lookup is empty
- internal runtime services may still exist separately
- application bootstrap uses the same provider mechanism as subtrees

### `None` Semantics

- if a local override value is `None`, that key is transparent at that slot
- lookup falls through to the parent provider chain
- this means authored `None` is reserved unless later replaced by an explicit
  unset sentinel

### Exit Criteria

- lowered provider syntax can execute through a retained runtime node
- scope inheritance works across lexical and component boundaries
- behavior may still be coarse-grained internally


## Phase 3: Per-Key Reactive Stream Primitive

### Goal

Introduce the minimal per-key notification primitive so provider changes only
invalidate readers of the keys that actually changed.

### Scope

- copy the existing stream primitive into Pyrolyze
- do not depend on another repository for this runtime feature
- keep the copied implementation local to Pyrolyze for now
- use the copied primitive as the per-key change notification backbone

### Recommended Placement

- `pyrolyze/src/pyrolyze/runtime/drip.py`

This keeps the primitive close to the runtime and leaves open the option of
factoring it out later if it proves broadly reusable.

### Why This Is Needed

The provider slot can expose multiple keys:

```python
with app_context_override[K1, K2, K3](v1, v2, v3):
    ...
```

If only `K2` changes, readers of `K1` and `K3` should not be dirtied.

That means the runtime needs one change channel per effective key, not one
monolithic "the context changed" signal.

### Runtime Model

Recommended direction:

- one stream per effective key at a provider slot
- reader binding subscribes only to the stream for its current effective key
- provider commit compares old vs new values per key
- only changed keys emit notifications
- removed keys emit notifications for the affected key
- keys whose value remains equal do not notify

### Equality Policy

First cut should use straightforward equality semantics:

- changed if `old != new`
- unchanged if `old == new`

If that later proves too weak for some values, refine then. Do not overdesign
the first version.

### Exit Criteria

- copied stream primitive exists in Pyrolyze runtime
- per-key notifications are possible
- unrelated key reads are not dirtied by unrelated key changes


## Phase 4: Provider And Reader Integration

### Goal

Hook `use_app_context(key)` up to the retained provider chain and per-key
notification streams.

### Scope

- make `use_app_context(key)` a slot-backed reactive helper
- validate that the argument is an `AppContextKey`
- bind reader slots to:
  - current requested key
  - current effective provider slot
  - current per-key stream for that provider
- rebind on:
  - requested key change
  - effective provider change
  - provider disappearance

### Reader Semantics

`use_app_context(key)` should behave like `use_grip(...)` at a high level:

- first evaluation resolves and subscribes
- later rerenders reuse binding when possible
- if the requested key changes, rebind to the new key
- if the provider/value changes for the same key, invalidate through the stream

### Failure Cases

Add deterministic errors for:

- non-`AppContextKey` reader arguments
- missing provider for a requested key
- invalid provider arity
- changing provider key tuple at the same slot

### Exit Criteria

- dynamic reader keys work
- fixed provider keys work
- selective per-key invalidation works


## Phase 5: Structural And Rerender Coverage (Deferred)

### Goal

Prove that the mechanism behaves correctly across structural churn and component
boundaries.

This phase is intentionally not part of the first implementation push.

It should remain a follow-on verification phase after the core surface and
selective per-key invalidation model have landed and stabilized.

### Coverage Areas

- nested providers with shadowing
- multi-key providers
- parent fallthrough via `None`
- provider removal and reintroduction
- reader key change across rerenders
- component boundary inheritance
- keyed-loop structural churn
- same final logical context after fresh render vs rerender from a very
  different prior shape

### Mount Boundary Checks

Add explicit tests that app context does not affect mount resolution directly.

Examples:

- changing app context does not change a native mount match unless the emitted
  exported mount surface changes
- `mount(...)` continues to resolve structurally
- exported/advertised mounts remain the only supported cross-boundary mount
  mechanism

### Exit Criteria

- context semantics are stable under rerender
- selective invalidation remains correct under churn
- mount behavior remains structurally isolated from app context


## Documentation Follow-Up

Once the implementation is stable:

- update `pyrolyze/dev-docs/HierarchicalContextManagement.md`
- add user-facing docs under `pyrolyze/docs/` if the API is ready to expose
- document the reserved `None` semantics clearly
- document the provider/reader asymmetry clearly:
  - provider keys are structural and fixed
  - reader keys are dynamic and slot-reactive


## Suggested Test Breakdown

Approximate first-pass test count:

- Phase 1 AST/golden tests: `10`
- Phase 2 runtime scaffolding tests: `8`
- Phase 3 per-key stream tests: `10`
- Phase 4 reader/provider integration tests: `14`
- Phase 5 structural/rerender tests: `16`

Total first-pass estimate: about `58` tests.


## Risk Notes

### 1. Component Boundary Leakage

If child `RenderContext`s continue to read only the scheduler-root store, the
feature will appear to work inside one lexical component body and then silently
break across component calls.


### 2. Over-Notification

If provider commits notify one coarse "context changed" channel, the system
will work functionally but create unnecessary rerenders. The copied stream
primitive is intended specifically to avoid that.


### 3. Reader/Provider Symmetry Confusion

It is easy to accidentally make both sides fixed-key or both sides dynamic-key.
That is not the intended model.

The intended asymmetry is:

- provider keys fixed structurally at the slot
- reader key dynamic like `use_grip(...)`


## Bottom Line

Implement this in layers:

1. syntax and golden tests
2. retained override runtime shape
3. copied per-key stream primitive
4. reactive reader binding
5. structural stress coverage

That keeps the risk down and makes the selective per-key notification model a
first-class part of the plan instead of an afterthought.
