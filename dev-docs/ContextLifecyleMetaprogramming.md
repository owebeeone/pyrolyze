# Context Lifecycle Metaprogramming

## Status

Proposed.

## Purpose

Pyrolyze runtime lifecycle management is currently expressed in many different
ways:

- current vs staged fields
- begin/commit/rollback methods on structural contexts
- retained binding objects with bespoke lifecycle
- call-site immutable replacement and refcounting
- deactivate paths that perform teardown outside commit/rollback

This document proposes a single declarative lifecycle system that can express
the current `CallSiteContext` and slot-context shapes with minimal boilerplate.

The design goal is not just to reduce code. The goal is to make lifecycle:

- explicit
- local
- testable
- transaction-scoped
- efficient for localized rerenders

## Genericity requirement

The lifecycle library must remain generic.

Implementation details from `runtime/context.py` must not leak into
`pyrolyze.lifecycle`.

That means:

- no slot-specific terminology in the lifecycle API
- no field names like `slot_id`, `kwargs`, `mounted_callback`, or `SlotContext`
  baked into lifecycle helpers
- no runtime-context-specific assumptions in field policies

The lifecycle library should describe only generic lifecycle concepts such as:

- current vs working state
- transactions
- commit
- rollback
- close
- bindings
- owned resources
- transient state
- derived state
- local stores

## Tradeoffs

This design is not free.

Compared to the current hand-written lifecycle code, a declarative system adds:

- descriptor/property indirection
- copy-on-write state allocation
- transaction bookkeeping
- generic diffing of binding maps
- metaprogramming and generated state classes

So the first implementation will likely be slower in the small than a tightly
hand-written fast path.

The reason to pursue it is not that the abstraction is automatically faster.
The reason is that a declarative lifecycle model creates optimization leverage.

Once field kinds and lifecycle policies are declared uniformly, the runtime can
optimize centrally instead of re-solving the same problems in every slot class.
That creates room for:

- commit/rollback over only changed contexts
- field-kind-specific fast paths
- specialized scalar vs binding-map handling
- precomputed metadata and generated accessors
- different backing implementations behind the same API

This means the design should be used for lifecycle-managed state, not as a goal
to metaprogram all runtime behavior. Imperative runtime behavior can remain
hand-written while the lifecycle state beneath it becomes declarative.

## Design goals

The lifecycle system should:

1. Let the application declare lifecycle-managed state in one place.
2. Preserve current/working separation without hand-written copy code.
3. Enlist only changed objects into a transaction.
4. Visit only changed objects on commit or rollback.
5. Support lifecycle-managed bindings/resources uniformly.
6. Support fixed-structure validation hooks for cases like
   `AppContextOverrideSlotContext`.
7. Support inherited context shapes like the current slot-context hierarchy.
8. Make field-level lifecycle policy declarative rather than ad hoc.

## Current experimental API

The current prototype lives in `pyrolyze.lifecycle`.

It exposes:

```python
@managed_context
class Example(LifecycleContext):
    transaction_manager: TransactionManager = inherited_const()
    slot_id: SlotId = const()
    declared_keys: tuple[str, ...] = static(default_factory=tuple)
    title: str = managed(default="untitled")
    binding: Binding | None = binding(default=None)
    owned_child: ChildContext | None = owned(default=None)
    bindings: dict[str, Binding] = binding(default_factory=dict)
    seen_in_pass: bool = transient(default=False)
    runtime_locals: dict[str, object] = local_store(default_factory=dict)
```

and the decorated class gets:

- generated frozen current state
- generated thawed working state
- property-driven copy-on-write writes
- commit/rollback/close lifecycle
- accepted/close lifecycle on binding fields
- copy-on-write mapping access for binding maps

The prototype proves that the shape is viable, but it is still intentionally
small. It does not yet encode all the lifecycle semantics needed by the real
runtime.

## Field taxonomy

The lifecycle system should use the following field kinds.

### `const()`

Constructor-only, never changes, not lifecycle-managed.

Examples:

- `transaction_manager`
- `slot_id`
- `parent`
- `render_context`

### `static()`

Late-initialized, then fixed forever, not part of current/working lifecycle.

Example:

- `declared_keys`

Best-guess semantics:

- initially unset or defaulted
- assignable exactly once
- not committed or rolled back
- close does not mutate it

### `managed()`

Ordinary lifecycle-managed value.

Examples:

- `function_identity`
- `schema`
- `last_args`
- `last_kwargs`
- `committed_native_root`

Best-guess semantics:

- whole-value replacement
- copy-on-write tracked
- commit/rollback controlled
- equality defaults to value equality

### `binding()`

Lifecycle-managed attached resource, or keyed map of attached resources.

Examples:

- `SlotCallSlotContext.binding`
- future site metadata maps
- retained effect/subscription handles

### `owned()`

Lifecycle-managed subordinate object with ownership/cascade intent.

Examples:

- `ComponentCallSlotContext.child_context`
- future owned retained subordinate contexts or handles

### `transient()`

Pass/transaction-local state. Cleared on commit and rollback. Not part of the
committed snapshot.

Examples:

- `seen_in_pass`
- `_staged_call_site_ids`
- `_staged_post_commit_callbacks`
- `_pass_owned_event_handler_order`

### `local_store()`

Retained mutable cache/state outside commit/rollback.

Examples:

- `_runtime_locals`
- `_runtime_locals_by_slot_id`

Semantics:

- survives commit and rollback
- not diffed
- not copied on write
- cleared only on deactivate/close

### `derived()`

Derived cached value, not source-of-truth state.

Examples:

- `_committed_ui`
- `_committed_lookup`
- `_pending_lookup`

Best-guess semantics:

- stored, not recomputed on every read
- invalidated or recomputed by class hooks
- not authored directly as primary lifecycle state

## Current runtime gotchas the design must capture

Looking at `runtime/context.py` and `runtime/call_site_context.py`, the generic
system must cover at least these dimensions.

### 1. Plain current/working values

Examples:

- `function_identity`
- `schema`
- `last_args`
- `last_kwargs`
- `committed_native_root`
- `component_identity`

These are ordinary lifecycle-managed values.

### 2. Single retained bindings

Examples:

- `SlotCallSlotContext.binding`
- `CallSiteContext.binding`
- potential future single `RuntimeSiteMetadata`-derived attachments

These need:

- `accepted()` when newly committed
- `close(was_committed=False)` on rollback of provisional values
- `close(was_committed=True)` on committed removal or replacement

### 3. Keyed binding maps

Examples:

- future `RuntimeSiteMetadata` keyed by metadata key
- future generalized binding maps on slot contexts

These need:

- copy-on-write updates
- commit diffing by key
- rollback close of provisional entries
- no list-position semantics

### 4. Nested owned objects as lifecycle-managed values

Examples:

- `ComponentCallSlotContext.child_context`

These behave like owned subordinate lifecycle objects:

- new child accepted on commit
- provisional child closed on rollback
- old committed child closed on replacement

### 5. Fixed-structure validation

Examples:

- `AppContextOverrideSlotContext`

This introduces a class-level semantic hook:

- key arity must match value arity
- fixed declared keys cannot change once established

This is not a generic field policy. It is a class-specific commit-time
validation.

### 6. Fields with lifecycle-specific value control

Some values are not ordinary defaults. They depend on lifecycle phase.

Examples:

- an `is_initial` or `invoke_dirty` style field that should be:
  - `True` for the first mutable working state of a never-committed object
  - `False` once committed
  - `False` for later thawed copies

This requires declarative value control, not just `default=...`.

### 7. Transient pass state

The current runtime uses many pass-local fields that are cleared once the pass
ends and are not part of committed lifecycle state.

Examples:

- `seen_in_pass`
- `_pass_child_order`
- `_pass_child_dirty`
- `_staged_ui`
- `_staged_ui_entries`

These should be expressed as `transient()` fields.

### 8. Retained local stores

The runtime also uses retained mutable caches that are not committed or rolled
back.

Examples:

- `_runtime_locals`
- `_runtime_locals_by_slot_id`

These should be expressed as `local_store()` fields.

## Declarative model

The target model is:

```python
@managed_context
class ManagedSlotCallContext(LifecycleContext):
    slot_id: SlotId = const()
    invoke_dirty: bool = managed(initial_working=True, freeze=bool)
    function_identity: object | None = managed(default=None)
    schema: tuple[int, tuple[str, ...]] = managed(default=(0, ()))
    binding: SlotBindingBase | None = binding(default=None)
    site_bindings: dict[Hashable, SlotBindingBase] = binding(default_factory=dict)
```

and:

```python
@managed_context
class ManagedComponentCallContext(ManagedSlotContext):
    component_identity: object | None = managed(default=None)
    child_context: ManagedRenderContext | None = owned(default=None)
    owned_handlers: dict[SlotId, EventHandlerBinding] = owned(default_factory=dict)
```

The application class is the source of truth for:

- field names
- field kinds
- defaults and lifecycle value-control
- class-specific validation or lifecycle hooks

The library is responsible for:

- generated state classes
- current/working handling
- transaction enlistment
- commit/rollback/close flow
- binding/resource lifecycle
- property descriptors

## Best-guess concrete API

The design should proceed with this concrete surface unless runtime migration
forces a correction.

```python
@managed_context
class ExampleContext(LifecycleContext):
    transaction_manager: TransactionManager = inherited_const()
    slot_id: SlotId = const()
    declared_keys: tuple[str, ...] = static(default_factory=tuple)
    invoke_dirty: bool = managed(
        default=False,
        initial_working=True,
        compare="value",
        freeze=bool,
    )
    last_kwargs: dict[str, object] = managed(
        default_factory=dict,
        freeze=frozendict,
        thaw=dict,
    )
    binding_handle: Binding | None = binding(default=None)
    owned_child: ChildContext | None = owned(default=None)
    pass_seen: bool = transient(default=False)
    runtime_locals: dict[str, object] = local_store(default_factory=dict)
    committed_ui: tuple[object, ...] = derived(default_factory=tuple)
```

### Best-guess policy choices

- `binding()` is the standard attached retained-resource field.
- `owned()` is the standard subordinate owned-resource field.
- `managed()` handles plain dict/list/tuple state by whole-value replacement.
- freeze/thaw policy on `managed()` is enough for now; no separate
  `managed_map()` or `managed_list()` is needed.
- `static()` means assign once after construction, then immutable forever.
- `derived()` means cached derived value maintained by class hooks.
- `transaction_manager` is a generic shared runtime service, not an
  application-specific lifecycle field.

## Transaction model

The lifecycle system should optimize for localized rerenders.

If a large context graph exists but only a small region is touched, commit and
rollback should only visit the changed objects.

### Central transaction

The runtime already has a central notion of transaction/generation:

- `RenderContext._run_boundary()` opens the outer transaction
- `GenerationTracker.begin()/commit()/rollback()` manages the active generation

The lifecycle system should align with that model instead of inventing per-node
implicit transactions.

Conceptually:

```python
class LifecycleTransaction:
    tx_id: int
    dirty_contexts: dict[int, LifecycleContext]
```

The best-guess implementation choice is:

- use the active generation id as the lifecycle transaction id
- keep transaction state in a shared `TransactionManager`
- allow exactly one active lifecycle transaction at a time
- reject nested lifecycle transactions for the first implementation

Conceptually:

```python
class TransactionManager:
    active_transaction: LifecycleTransaction | None

    def begin(self) -> LifecycleTransaction: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def enlist(self, context: LifecycleContext) -> None: ...
```

All lifecycle-managed contexts participating in one runtime graph share one
transaction manager.

The best-guess structural model is:

- `transaction_manager` is an inherited `const` field on `LifecycleContext`
- application classes do not need to redeclare or manage it directly
- the manager stores transaction-specific state so that transaction mechanics do
  not leak into unrelated application fields

### Copy-on-write enlistment

On first write in a transaction:

1. ensure there is an active transaction
2. if the context does not yet have a working copy for this transaction:
   - create one
   - assign its transaction id
   - register the context in the transaction dirty set
3. perform the mutation

If the same context is written again in the same transaction:

- keep mutating the same working object

If a write occurs under a different active transaction while a working copy is
still associated with another transaction:

- raise

This keeps the current implementation simple:

- no nested transactions
- no hidden cross-transaction working-state reuse

### Commit and rollback cost

Commit and rollback should only walk:

- the dirty/open transaction set

not:

- the full context graph

This is the main performance reason to base the design on central transaction
enlistment rather than whole-graph scans.

### Write control

Best-guess write control rules:

- write to `managed`, `binding`, `owned`, or `transient` without an active
  transaction:
  - raise
- first write in the active transaction:
  - copy on write
  - register in dirty context set
- later write in the same transaction:
  - continue mutating working state
- write under a different transaction while a working copy is still open:
  - raise

The transaction manager is the source of truth for these checks.

## Value control

`managed(...)` needs to express more than plain `default=...`.

Some fields are lifecycle-controlled values.

Examples:

- `is_initial`
- `invoke_dirty`
- future fields that are true only for first mutable construction

The API should support declarative value-control policies.

Conceptually:

```python
is_initial: bool = managed(
    default=False,
    initial_working=True,
    committed_default=False,
    thawed_default=False,
)
```

This means:

- the first working state for a never-committed context sees `True`
- the committed state stores `False`
- later thawed copies also see `False`

This should be field policy, not hand-written mutation logic.

Value control may also grow to include:

- copy-on-write suppression for equal values
- identity-based equality for resource-like values
- normalized commit value
- derived thaw value

The important point is that these are field semantics and should be declared at
the field site.

Best-guess defaults:

- `managed()` uses value equality by default
- `binding()` and `owned()` use identity comparison
- `managed()` may specify `compare="identity"` when needed
- freeze is write-protection/normalization, not a separate lifecycle concept

## Binding model

Bindings are lifecycle-managed resources.

The minimal interface remains:

```python
class LifecycleBinding(Protocol):
    def accepted(self) -> None: ...
    def close(self, *, was_committed: bool) -> None: ...
```

For a scalar binding field:

- new provisional binding committed:
  - `accepted()`
- new provisional binding rolled back:
  - `close(was_committed=False)`
- old committed binding replaced:
  - old binding `close(was_committed=True)`
  - new binding `accepted()`
- close of the owning context:
  - committed binding `close(was_committed=True)`

For binding maps the same semantics apply per key.

Best-guess ordering rules:

- on rollback:
  - close provisional owned objects before provisional bindings
- on commit replacement:
  - accept new resources before closing replaced committed resources
- on owner close:
  - close owned objects before attached bindings

These choices are intended to be compatible with the current runtime shape,
where subordinate retained objects should tear down before outer attached
resources.

## Class hooks

The declarative library should remain generic, but it still needs class hooks.

Examples:

- `before_commit(current, working)`
- `after_commit(previous, current)`
- `after_rollback(current)`
- `before_close(current)`

These hooks let classes encode:

- fixed-structure validation
- derived state normalization
- application-specific invariants

This is how the design naturally handles `AppContextOverrideSlotContext`
without teaching the generic library about app-context semantics.

## Context graph mapping

The declarative model is not limited to call sites.

It can describe much of the slot-context graph directly:

### Slot-call style

- ordinary values
- single binding
- future metadata binding map
- transient pass flags
- local runtime stores

### Container style

- ordinary structural flags
- future metadata binding map
- possible binding-managed container handles
- transient pass-local staging
- derived committed UI

### Component-call style

- ordinary values
- child context as owned resource
- owned event-handler map
- derived committed UI

### Override style

- static declared key structure
- ordinary committed/pending values
- class-level validation hooks
- derived cached lookup values

The slot-context object may still own imperative behavior, but the lifecycle
state can become declarative.

## Do we need true frozen classes?

This is an open design question.

### Option A: keep true frozen classes

Pros:

- hard write protection for committed state
- clearer debugging of illegal mutation
- simpler mental model for current vs working
- aligns naturally with `freezable` / `thawable`

Cons:

- more generated types
- more conversion machinery
- object churn at freeze boundaries
- some logic may become conversion-aware unnecessarily

### Option B: use mutable dataclasses with write control

Pros:

- simpler generated types
- no need for true frozen peers
- committed vs working can be enforced by descriptor and transaction rules
- field-level write control may already provide enough protection

Cons:

- write protection becomes policy, not type-level guarantee
- accidental mutation bugs may be harder to catch
- debugging current-vs-working mistakes becomes less obvious

### Best-guess conclusion

The transaction model is the primary requirement. True frozen classes are a
secondary implementation choice.

If transaction-scoped write control is strong enough, mutable dataclasses may
be sufficient:

- current state may be mutable by type
- but writes can only occur through managed descriptors under an active
  transaction
- direct writes outside the transaction protocol should raise

That means the design should not depend on true frozen classes.

The lifecycle library should be able to support both implementations:

- true frozen current state plus thawed working state
- mutable current/working dataclasses with transaction-controlled writes

The rest of the declarative API should stay the same.

The current best guess is:

- start with true frozen current state if that simplifies implementation
- do not make the API depend on true frozen classes
- keep the option to move to mutable backing state with strict write control if
  profiling shows that to be a better runtime trade

## Proposed direction

1. Keep the declarative surface as the primary design.
2. Introduce a central transaction object with a dirty/open context set.
3. Make first-write copy-on-write the enlistment point into the transaction.
4. Add field-level value-control to `managed(...)`.
5. Keep class hooks for fixed-structure semantics.
6. Do not commit the design to true frozen classes yet.
   The API should remain compatible with either frozen or mutable backing state.

## Why this is worth doing

If this works, lifecycle code stops being hand-written across:

- `CallSiteContext`
- `SlotCallSlotContext`
- `ContainerSlotContext`
- `ComponentCallSlotContext`
- future metadata-binding owners

and becomes:

- declarative field definitions
- transaction enlistment
- generic commit/rollback/close machinery
- small class-specific hooks for true semantic differences

That is the right level of abstraction for the complexity the runtime now has.
