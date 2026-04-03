# Call Site Context Design

## Problem

`slot_expr` currently creates a fresh runtime expression object on every render pass. That is fine for expression evaluation, but it is wrong for persistent slot-call lifecycle state.

The failure mode is:

```python
@pyrolyze_slotted
def const_or_value(select: bool):
    if select:
        return use_grip("A")
    return 10
```

If the first render returns an `ExternalStoreRef` and the next render returns `10`, the old external-store subscription must be deactivated. Today that state is owned by a transient `SlotCallEvaluator`, so the old binding is orphaned instead of closed.

The missing primitive is a persistent, transactional, slot-owned call-site state object.

## Goals

- Persist slot-call state across rerenders by call-site identity.
- Keep `SlotExpr` itself transient and recreatable each render.
- Make call-site updates transactional.
- Ensure staged state is either committed or rolled back.
- Ensure old state is closed when replaced.
- Ensure staged new state is closed on rollback.
- Ensure slot cleanup closes all call-site state.
- Keep the call-site state object immutable.

## Non-Goals

- This design does not change compiler lowering shape.
- This design does not remove `plain_call` by itself.
- This design does not redesign component/container call surfaces.

## Core Model

Introduce a new runtime module that owns persistent slot-call state:

- `CallSiteContext`
- `CallSiteContextManager`
- `CallSiteBindingBase`

The manager is owned by a slot/runtime context and keyed by call-site `SlotId`.

`SlotExpr` and other call evaluators do not own lifecycle state directly. They ask the slot context for the current call-site state and stage replacements through the manager.

## API Shape

### `CallSiteContext`

This should be an ABC.

Responsibilities:

- represent one immutable call-site state snapshot
- expose the state needed by the evaluator
- support `close()`

Conceptually:

```python
class CallSiteContext(ABC):
    binding: CallSiteBindingBase | None
    function_identity: Any
    last_args: CallSiteArgs
    invoke_dirty: bool

    @abstractmethod
    def close(self) -> None: ...
```

Concrete implementations should hold exactly:

- `binding`
- `function_identity`
- `last_args`
- `invoke_dirty`

They should be immutable. Updating means:

1. create a new instance, or
2. use `dataclasses.replace(...)`

The old instance is never mutated in place.

The first concrete implementation should be a frozen dataclass with those fields directly:

```python
@dataclass(frozen=True, slots=True)
class PlainCallSiteContext(CallSiteContext):
    binding: CallSiteBindingBase | None
    function_identity: Any
    last_args: CallSiteArgs
    invoke_dirty: bool
    _close_state: _CloseState

    def close(self) -> None:
        ...
```

### `CallSiteBindingBase`

Bindings referenced by immutable call-site contexts should sit behind a new ABC:

```python
@dataclass(slots=True, eq=False)
class CallSiteBindingBase(ABC):
    _call_site_ref_count: int = field(default=0, init=False, repr=False, compare=False)
    _call_site_closed: bool = field(default=False, init=False, repr=False, compare=False)

    def inc_ref(self) -> None:
        ...

    def dec_ref(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None: ...
```

This is the ownership primitive for transactional immutable contexts.

Rules:

- the base class owns the refcount
- if a new immutable call-site context reuses an existing binding, it calls `inc_ref()`
- when a context is closed, it calls `dec_ref()`
- when the binding refcount reaches zero, the base class calls the binding's abstract `close()`

For the plain-call runtime, a concrete reference-counted binding wrapper can delegate to the existing binding lifecycle:

- `commit()`
- `rollback()`
- `deactivate()`

The actual deactivate/cleanup path should only run when `dec_ref()` drops the count to zero.

### `CallSiteContextManager`

This should also be an ABC-backed runtime type, with one default implementation.

Responsibilities:

- lazily create current call-site contexts by `SlotId`
- track current and staged contexts
- commit or roll back transactional updates
- close replaced or abandoned contexts
- close all owned contexts on slot cleanup

Conceptually:

```python
class CallSiteContextManager:
    def get_current(self, slot_id: SlotId) -> CallSiteContext | None: ...
    def stage(self, slot_id: SlotId, context: CallSiteContext) -> None: ...
    def mark_visited(self, slot_id: SlotId) -> None: ...
    def begin_pass(self) -> None: ...
    def commit_pass(self) -> None: ...
    def rollback_pass(self) -> None: ...
    def close_all(self) -> None: ...
```

## Transaction Semantics

Each render pass is transactional.

### Begin Pass

At pass start:

- clear staged replacements
- clear visited markers

The current committed contexts remain intact.

### During Evaluation

When a call site is evaluated:

- mark it visited
- ask the manager for the current context for that `slot_id`
- if none exists, create one in open state
- if a new state is needed, build a new immutable context and stage it

When no state change is needed:

- continue using the current context
- no replacement is required

### Commit Pass

For each visited call site:

- if a staged replacement exists:
  - close the old committed context if present
  - promote the staged context to current

For each unvisited previously-current call site:

- close the current context
- remove it from current state

For each staged context that was committed:

- keep it as current and open

### Rollback Pass

For each staged replacement:

- close the staged new context
- discard it

The old committed current context remains current.

No unvisited deactivation from the failed pass is committed.

## Open/Closed State

When a `CallSiteContext` is first created, it is open.

`close()` must be idempotent.

Closing a context means:

- release its binding reference
- mark its close-state as closed

The binding itself then decides whether cleanup must actually run:

- if references remain, nothing else happens
- if refcount reaches zero, the binding deactivates subscriptions, cancels effects, withdraws adverts, and releases resources

## Slot Ownership

The `CallSiteContextManager` is owned by the expression slot context, not by the transient `SlotExpr` object.

That means:

- `SlotExpr` remains a transient expression evaluator
- persistent call-site state survives across rerenders of the same expression slot
- slot cleanup can close all call-site contexts deterministically

For one `slot_expr` site:

- the expression slot context has its own slot id
- the expression contains one or more call-site slot ids
- the manager belongs to the expression slot context
- the manager is keyed by the raw call-site slot ids inside that expression

This means manager lookup does **not** need resolved runtime slot ids.

Resolved slot ids are still relevant for host/render-context operations such as:

- invalidation routing
- render-context slot ownership
- advert publication/withdrawal

But the manager map itself should use the raw call-site slot ids because the owning expression slot context already defines the outer runtime namespace.

When the owning slot is deactivated:

- `CallSiteContextManager.close_all()` runs
- all current contexts are closed
- all staged contexts are closed

## Integration With `SlotExpr`

Current `SlotExpr` evaluator state includes:

- binding
- function identity
- last args
- last kwargs
- invoke dirty

Those fields should move into a concrete `CallSiteContext`.

Then `SlotCallEvaluator` becomes pass-local orchestration only:

- compute args
- compute should-invoke
- read current context from manager
- stage new context when needed
- expose current value/dirty for this pass

`SlotCallEvaluator` should no longer be the owner of persistent lifecycle state.

## Concrete Runtime Direction

Add a new module:

- `src/pyrolyze/runtime/call_site_context.py`

Initial contents:

- `CallSiteContext` ABC
- concrete immutable plain-call/slot-call context dataclass
- `CallSiteContextManager`

The first concrete context should hold:

- `binding: CallSiteBindingBase | None`
- `function_identity: Any`
- `last_args: CallSiteArgs`
- `invoke_dirty: bool`

This state corresponds to what `SlotCallEvaluator` currently persists, except that the binding is now reference-counted.

Because the context is frozen, close state must not be stored as a normal mutable field on the dataclass itself.

If close idempotence needs per-instance state, it should be represented by a referenced mutable object, for example:

- a tiny `_CloseState` object held by the frozen context
- or manager-owned closed-state tracking

The frozen context payload remains immutable; only the referenced close-state object may mutate.

## Suggested Commit Rules

For a staged replacement:

- the new immutable context is built before staging
- if it reuses an existing binding, it must already have called `binding.inc_ref()`
- on commit:
  - close old context
  - keep new as current

For rollback:

- close staged new context

For unvisited current entries:

- close on commit

Because closing releases a binding reference rather than blindly deactivating, commit and rollback remain safe even when old and new contexts share the same underlying binding.

## Tests Needed

Add a dedicated unit test suite:

- `tests/test_runtime_call_site_context.py`

Required tests:

1. lazy creation returns `None` before stage and current after commit
2. rollback closes staged new context and preserves old current
3. commit closes old current and promotes staged new
4. unvisited current context closes on commit
5. `close_all()` closes all current and staged contexts
6. `close()` is idempotent
7. multiple call sites are isolated by `SlotId`
8. reusing a binding across old/new immutable contexts increments and decrements refcount correctly
9. binding cleanup runs only when the last reference is released

Then integration tests:

- the compiled `const_or_value(select)` external-store case
- branch-sensitive deactivation across rerenders
- replacement from store-backed binding to plain value
- replacement back from plain value to store-backed binding

## Expected Outcome

After this lands:

- `slot_expr` can still be recreated every render
- persistent slot-call state survives by `SlotId`
- external-store subscriptions are properly torn down on value-family changes
- staged lifecycle transitions are atomic
- slot cleanup closes all call-site state
- immutable contexts can safely share bindings through explicit reference counting
