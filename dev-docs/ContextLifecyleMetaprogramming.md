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
- copy-on-write state allocation or working-state promotion
- transaction bookkeeping
- generic diffing of binding maps
- metaprogramming and generated field-policy machinery

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

## Architectural direction

`freezable` was the beginning of lifecycle normalization, but it is no longer
the right center of the design.

The real problem is not “mutable peer vs frozen peer”. The real problem is:

- transaction-scoped mutation
- current vs working state
- `const` and `static` writes
- `binding` and `owned` lifecycle
- transient and retained local state
- commit/rollback/close ordering

Those concerns are broader than paired dataclass conversion.

### New architectural decision

`pyrolyze.lifecycle` should own lifecycle semantics directly.

That means:

- `pyrolyze.lifecycle` should not depend on `pyrolyze.freezable` for its core
  operation
- `pyrolyze.lifecycle` should not depend on dataclasses as the fundamental
  state model
- the primary mechanism should be declarative field policies compiled into
  descriptors and field-specific helpers
- `freezable` may remain as an optional utility for leaf values where
  freezing/thawing is convenient, but it is not part of the core lifecycle
  contract

In short:

- lifecycle is primary
- frozenness is an implementation detail

## Current experimental API

The current prototype lives in `pyrolyze.lifecycle`.

The next revision should converge on a declarative surface like:

```python
@managed_context
class Example:
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

- an internal managed-context base injected by the decorator
- a generated `Example_State` subclass carrying field tables and lifecycle state
- generated `Example_CurrentView` / `Example_WorkingView` subclasses that
  inherit the application class
- field descriptors with centralized getter/setter dispatch
- property-driven copy-on-write writes into a working record overlay
- commit/rollback/close lifecycle
- accepted/close lifecycle on binding fields
- normal Python method/descriptor resolution on `current` / `working`
- whole-value replacement for map-like fields in the first implementation

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

#### Universal binding base

Lifecycle-managed bindings should converge on one universal runtime base.

Best-guess v1 shape:

- `BindingBase`
- intrusive refcounting
- `inc_ref()`
- `dec_ref()`
- `accepted()`
- protected `_close()` hook

Semantics:

- a binding starts with `ref_count == 1`
- `inc_ref()` records an additional retained owner
- `dec_ref()` drops one retained owner
- when `ref_count` reaches zero, the base invokes `_close()` exactly once
- `accepted()` marks that the binding has survived commit at least once
- bindings do not need an external `was_committed` parameter
- teardown behavior derives from the binding's own accepted bit

That means:

- final release before `accepted()` implies rollback/uncommitted teardown
- final release after `accepted()` implies committed/live teardown

Recommended base properties:

- `ref_count`
- `is_accepted`
- `is_closed`

Recommended invariants:

- `inc_ref()` after close is an error
- `accepted()` after close is an error
- `dec_ref()` below zero is an error
- `_close()` runs exactly once and is not called directly by lifecycle code

Scope:

- use this base for retained runtime identity objects
- do not use this base for plain value data such as `UIElement`
- `UIElement`, `MountDirective`, and similar authored value objects remain
  plain data and do not gain lifecycle ownership semantics

Current runtime precedent:

- `CallSiteBindingBase` already carries the closest version of this model
- Phase `1.6 binding` should generalize that concept rather than invent a
  second competing lifecycle base

### `owned()`

Lifecycle-managed subordinate object with ownership/cascade intent.

Examples:

- `ComponentCallSlotContext.child_context`
- future owned retained subordinate contexts or handles

Best-guess relationship to the universal binding base:

- if an owned runtime object can be retained by multiple holders, it should
  likely subclass the same universal `BindingBase`
- if an owned runtime object is strictly single-owner and never shared, it may
  remain simpler than a refcounted binding
- the lifecycle system should prefer one retained-object model where practical,
  but it should not force refcounting onto plain structurally-owned values

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
- `dec_ref()` on rollback of provisional values
- `dec_ref()` on committed removal or replacement
- teardown behavior determined by the binding's own accepted bit

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
- provisional child released on rollback
- old committed child released on replacement

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
class ManagedSlotCallContext:
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

- field policy descriptors
- current/working handling
- transaction enlistment
- commit/rollback/close flow
- binding/resource lifecycle
- policy-specific proxies or helper objects where needed

## `context_lcm.py` binding guidance

`context_lcm.py` should use the universal binding base instead of defining new
bespoke retained-object protocols where possible.

Implementation hints:

- plain value nodes such as `UIElement` stay plain authored data
- retained runtime identity objects should move toward `BindingBase`
- `binding(...)` fields in lifecycle-managed contexts should hold:
  - a `BindingBase`
  - `None`
  - or a keyed container of `BindingBase`
- commit of a newly retained binding should call `accepted()`
- replacing or dropping a retained binding should call `dec_ref()`
- copying an existing retained binding into another holder should call
  `inc_ref()`
- rollback of an uncommitted replacement should call `dec_ref()`

Expected migration targets:

- `CallSiteBindingBase` should eventually collapse into, or subclass, the new
  universal base
- slot-call bindings should be adapted toward the same base over time
- backend node bindings should use the same retained-object model if they have
  persistent runtime identity and teardown requirements

Important constraint:

- `context_lcm.py` should not encode binding semantics itself beyond
  application-specific hooks
- the generic `inc_ref` / `dec_ref` / `accepted` behavior belongs in the
  shared lifecycle binding base

## Best-guess concrete API

The design should proceed with this concrete surface unless runtime migration
forces a correction.

```python
@managed_context
class ExampleContext:
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
- field write semantics belong to lifecycle field policies, not to
  dataclass-generated setters
- `freezable` may be used only for leaf-value normalization where convenient,
  for example freezing committed `kwargs`-like values after commit

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
2. if the context does not yet have a working record for this transaction:
   - create one
   - assign its transaction id
   - register the context in the transaction dirty set
3. perform the mutation

If the same context is written again in the same transaction:

- keep mutating the same working record

If a write occurs under a different active transaction while a working record is
still associated with another transaction:

- raise

This keeps the current implementation simple:

- no nested transactions
- no hidden cross-transaction working-state reuse

### Record model

The lifecycle engine should use records rather than whole cloned working
objects.

Conceptually:

```python
class LifecycleContext:
    current: Record
    working: Record | None
    _default_record: Record
```

With the following rules:

- `current` is the committed record
- `working` is a sparse overlay record for the active transaction
- `_default_record` is:
  - `working` if a working record exists
  - otherwise `current`
- ordinary field access goes through `_default_record`
- explicit committed reads use `self.current`
- explicit staged writes may use `self.working`, which lazily promotes the
  record if needed

This gives:

- no whole-object thaw/copy step
- only changed fields allocate working entries
- commit promotes only changed values and field state
- rollback discards only changed values and field state

### Field-policy access control

The lifecycle base should maintain a field-policy registry keyed by field name.

Conceptually:

```python
class LifecycleContext:
    __field_specs__: dict[str, FieldSpec]
    current: Record
    working: Record | None
    _default_record: Record
```

Each field spec defines behavior for:

- initialization
- read access
- write access
- commit
- rollback
- close

Handler selection should happen at class-decoration time, not dynamically in
the hot path.

That means:

- field parameters determine which getter/setter/commit/rollback helpers are
  bound into the field spec
- ordinary descriptor bodies should contain minimal logic
- the common path should be:
  - look up field spec by name
  - call the preselected helper for that field

The field spec may therefore contain handler references such as:

- `get_default`
- `get_current`
- `set_default`
- `commit_field`
- `rollback_field`
- `close_field`

If a field kind needs distinct current-vs-working behavior, it is acceptable to
have separate current and working helper variants. Those should still be chosen
when the class is decorated, not re-decided on every access.

The base class then exposes central dispatch points such as:

- `__get_field__(name)`
- `__set_field__(name, value)`
- `__get_current_field__(name)`
- `__get_field_state__(name)`
- `__get_current_field_state__(name)`

which select the concrete behavior for the field name.

The concrete helper functions should be introduced incrementally as the
primitive phases are implemented. The important point is that dispatch is
centralized while behavior remains field-specific.

These helpers should only be added when a new semantic behavior actually
requires them.

Do not create new helpers with identical semantics just to mirror field names
or phases. If `commit`, `rollback`, `copy`, or getter/setter behavior is the
same for multiple field configurations, those configurations should share the
same helper function.

The base class will then grow helpers such as:

- `_const_setter`
- `_static_setter`
- `_managed_value_setter`
- `_managed_identity_setter`
- `_managed_initial_setter`
- `_binding_scalar_setter`
- `_binding_map_setter`
- `_owned_scalar_setter`
- `_owned_map_setter`
- `_transient_setter`
- `_local_store_setter`
- `_derived_getter`

and matching getter helpers where field semantics require them.

For the first implementation, getters should stay simple.

That means:

- no rich getter-controller objects yet
- getters return plain field values
- getter specialization is only for access semantics such as:
  - current-vs-working visibility
  - unset-static handling
  - transient access rules
  - derived cache validation

If future map/controller behavior proves necessary, it can be added later
without changing the declarative field surface.

This is preferred to a single global `__setattr__` solution because:

- container/resource fields may eventually need specialized handling
- initialization rules differ by field kind
- some lifecycle fields require map-style mutation rather than scalar
  assignment

### Record and field runtime state

Some fields need per-instance runtime state beyond the stored value.

Examples:

- whether a `static` field has been initialized
- transient per-transaction visibility
- derived cache validity
- future field-local dirty bits or normalization state

The lifecycle base should therefore support sparse per-field runtime state.

Best-guess structure:

- `__field_specs__`
  immutable class-level metadata
- `current.values`
  committed field values
- `current.field_state`
  committed per-field runtime state
- `working.values`
  sparse working overrides for changed fields
- `working.field_state`
  sparse working runtime-state overrides for changed fields

Only fields that actually need extra state should allocate entries.

### Rollback model for field state

Rollback must restore both:

- working field values
- working field runtime state

So the design should treat field runtime state the same way it treats working
values, but within the record overlay model:

1. committed values and field state live in `current`
2. first mutation of field-local runtime state lazily clones the relevant entry
   into `working.field_state`
3. first mutation of a field value lazily stores an override in
   `working.values`
4. commit promotes `working.values` and `working.field_state` into `current`
5. rollback discards `working`

Fields without runtime state simply have no entry.

This keeps rollback generic and avoids ad hoc side bookkeeping in application
classes.

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
  - create or reuse the working record overlay
  - register in dirty context set
- later write in the same transaction:
  - continue mutating working state
- write under a different transaction while a working record is still open:
  - raise

The transaction manager is the source of truth for these checks.

For now, map-like lifecycle fields should also follow whole-value replacement.

That means:

- no getter-returned mutation controllers in the first implementation
- map updates happen by assigning a new mapping value
- commit/rollback still diff old vs new values for `binding` and `owned` maps

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

No, not as a core requirement.

True frozen classes were useful while the problem was framed as
“mutable/thawed peer vs frozen/current peer”. Once the design shifts to a
field-policy lifecycle engine, that framing becomes secondary.

What we actually need is:

- a stable current/working model
- transaction-scoped mutation control
- centralized field semantics
- a way to prevent or reject illegal writes

That can be achieved with:

- mutable record objects
- descriptor-driven write control
- transaction manager enforcement
- field-specific proxies for container/resource fields

### Best-guess conclusion

The lifecycle system should not depend on:

- true frozen classes
- paired dataclasses
- `freezable` as a foundation

Instead:

- `lifecycle` should own the setter/write-control story directly
- current and working state may both be mutable implementation objects
- legality of writes is enforced by lifecycle policy, not by dataclass
  frozenness
- `freezable` remains available only as an optional helper for leaf values that
  benefit from freezing

Examples where `freezable` may still be useful:

- committed `args` tuples
- committed `kwargs` mappings
- future leaf container values that benefit from structural freezing

But those are field-level optimizations, not lifecycle architecture.

## Prototype salvage

The current `pyrolyze.lifecycle` module is now best treated as a prototype, not
as an implementation to extend mechanically.

The parts that are still worth salvaging are:

- the transaction-manager concept
- the field taxonomy direction
- the independent lifecycle tests as semantic references
- binding lifecycle helper semantics such as `accepted()` and
  `close(was_committed=...)`

The parts that are likely not worth preserving are:

- the dependency on `pyrolyze.freezable`
- generated frozen/thawed state classes
- whole-object `_current` / `_working` cloning
- dataclass-centric state generation

So the implementation plan should assume:

- restart the core lifecycle implementation around records and field policies
- salvage semantics and tests where useful
- do not force source compatibility with the current prototype internals

## Proposed direction

1. Keep the declarative surface as the primary design.
2. Introduce a central transaction object with a dirty/open context set.
3. Make first-write copy-on-write the enlistment point into the transaction.
4. Add field-level value-control to `managed(...)`.
5. Keep class hooks for fixed-structure semantics.
6. Do not commit the design to true frozen classes yet.
   The API should remain compatible with either frozen or mutable backing state.

## Open issues

The design is now coherent enough to keep building, but a few issues should be
resolved deliberately before later phases rely on them too heavily.

### 1. Shared non-managed instance storage across stable views

The method-execution question is now resolved: current and working views should
be real generated subclasses of the application class so method lookup uses
normal Python resolution.

The remaining question is where non-managed instance attributes should live when
there are multiple real runtime objects sharing one lifecycle state:

- not in the managed current/working value dicts
- not copied through commit/rollback
- instead in a separate shared unmanaged store attached to the lifecycle state

Current best guess:

- managed storage is only for lifecycle-managed fields
- unmanaged storage is a separate shared store for ordinary instance
  attributes/caches
- `context`, `context.current`, and `context.working` all see the same
  unmanaged store
- unmanaged storage does not participate in commit/rollback

`static` fields are not part of unmanaged storage. They remain lifecycle field
concepts with one-time initialization semantics.

### 2. Name-resolution precedence

Adopted best guess:

- managed field names win over method names
- this includes `const`, `static`, and later lifecycle field kinds
- otherwise normal class resolution applies
- private/internal-name policy can remain conservative for now and be tightened
  later if needed

### 3. Non-function descriptors on application classes

The current direction is to rely on normal Python class behavior for:

- `@property`
- `classmethod`
- `staticmethod`
- ABC methods

The remaining question is whether any custom descriptors need special handling
beyond normal Python resolution, or whether they should simply be treated as an
unsupported edge case until a concrete need appears.

If a descriptor pattern is not explicitly described in this design, it should be
checked when encountered and resolved from the concrete use case rather than
abstractly anticipated.

### 4. Managed inheritance semantics

The current direction is:

- same-name field reappearance means **merge**, not blind replacement
- field kind must remain compatible according to narrowing rules
- annotation may narrow compatibly in a derived class
- `default` / `default_factory` may be replaced by the derived class
- other flag differences raise unless explicitly listed as overridable
- methods should continue to follow expected Python inheritance behavior

Best-guess v1 merge policy:

- exact same field kind is allowed subject to compatibility checks
- derived annotations may narrow the base annotation
- incompatible widening or unrelated type changes raise
- if there is doubt about a flag override, raise rather than guess

The standalone narrowing checks should live in:

- `pyrolyze.type_annotations`

Validation against real slot-context-style hierarchies is deferred until those
concrete cases appear during `context_lcm.py` migration.

### 5. Public vs internal wrapped-class identity

`@managed_context` now wraps plain application classes onto an internal base and
generates a separate state subclass. The remaining questions are:

- whether the wrapped class identity is acceptable for debugging and reprs
- whether any `super()` edge cases need to be handled explicitly
- whether pickle/serialization expectations matter for this layer

For now, this is a watchpoint rather than a blocker. It should be checked
against real `context_lcm.py` implementation experience and only escalated if
it causes practical issues.

### 6. `transaction_manager` representation

For now, keep this simple.

Current best guess:

- the manager holds the active transaction id
- lifecycle state tracks whether its staged values belong to that transaction
- a special constructor argument is acceptable in v1
- it may later become a real inherited `const()` field once the field taxonomy
  is implemented

## Stable-view state model

The current best guess is that a managed context should own a stable family of
runtime objects for its full lifetime:

- `context`
  the default/application-facing view
- `context.current`
  the committed read-only view
- `context.working`
  the staged working view
- `context.state`
  the shared lifecycle state object

The important part is that `current` and `working` are stable objects. They are
not created and destroyed per transaction. Only the underlying state changes.

### Shared storage

The shared state object should hold:

- `current_values`
  committed field values
- `working_values`
  sparse staged overrides
- `current_field_state`
  committed field runtime state
- `working_field_state`
  sparse staged runtime-state overrides
- transaction bookkeeping

### Read behavior

Best-guess semantics:

- `context.field`
  reads the default/working surface
- `context.current.field`
  always reads current value
- `context.working.field`
  reads the same logical working/default surface as `context.field`

This means:

- unqualified access is always the staged/default view
- the committed surface is only available explicitly via `.current`

The staged/default surface may still read through to committed values for fields
that do not yet have staged overrides, but it should not change conceptual mode
based on whether a staged override currently exists.

### Write behavior

Best-guess semantics:

- `context.field = value`
  writes through the default lifecycle rules
- `context.current.field = value`
  always fails
- `context.working.field = value`
  always stages into the working layer

## Adopted v1 transaction policy

The adopted v1 policy is:

1. transactions are explicit
   - `transaction_manager.begin()`
   - `transaction_manager.commit()`
   - `transaction_manager.rollback()`
2. writes to lifecycle-managed fields outside an active transaction raise
3. the first write to a managed field under an active transaction:
   - enlists the owning context in that transaction
   - materializes staged mutable state for that field from the committed value
     if the field policy requires it
4. subsequent writes in the same transaction reuse that staged value/state
5. commit merges staged state into committed state and clears staged state
6. rollback discards staged state and leaves committed state unchanged

This v1 policy intentionally does **not** auto-begin transactions on write.
The explicit transaction boundary is easier to reason about, easier to test, and
closer to the existing runtime transaction model.

### Commit behavior

Commit should:

1. merge `current_values` with `working_values`
2. apply per-field commit transforms or lifecycle hooks
3. replace `current_values` with the merged result
4. clear `working_values`
5. do the same for field runtime state

This keeps the commit boundary explicit while avoiding whole-object cloning.

### Rollback behavior

Rollback should:

- discard staged `working_values`
- discard staged `working_field_state`
- leave `current_values` and committed runtime state unchanged

### Allocation policy

The first implementation may simply allocate fresh merged dicts on commit.
Later optimization can keep the working dicts allocated and reuse them by
clearing them after commit or rollback.

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
