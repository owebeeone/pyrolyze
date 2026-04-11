# Lifecycle Adoption Patterns

## Purpose

This document captures the decision process used to move
`pyrolyze/src/pyrolyze/runtime/context_state/context_base.py`
toward the lifecycle-based shape in
`pyrolyze/src/pyrolyze/runtime/context_state_lcm/context_base.py`.

The goal is not to mechanically transliterate legacy fields into lifecycle
fields. The goal is to redesign each `*StateMgr` around clear state semantics
so that:

- the field kind is obvious and defensible
- boundary publication and rollback semantics are explicit
- redundant scratch state is removed instead of preserved
- the generated lifecycle machinery is used directly instead of bypassed
- future refactors operate on a constrained, declarative state model

`ContextBaseStateMgr` is the first worked example. The same process should be
applied to the remaining state manager classes.

## Migration Mindset

Treat the legacy `context_state/*` module as a behavioral reference, not a
schema to copy verbatim.

For each legacy field or cluster of fields, ask:

1. Is this authoritative published state after a successful boundary pass?
2. Is this pass-local scratch that must disappear when the pass closes?
3. Must this survive rollback?
4. Is it a retained resource or binding with commit/rollback semantics?
5. Is it truly just a cache or helper that is not authoritative?
6. Can this value be derived from `owner`, `self.current`, or another field?
7. Is this field actually needed, or is it legacy bookkeeping that can be removed?

Only after answering those questions should a lifecycle field kind be chosen.

## Field Classification Rules

### `const`

Use `const` for values that are fixed for the lifetime of the state manager and
do not participate in transaction semantics.

Use it when:

- the value comes from `owner` at construction time
- the value should never roll back or commit
- mutation would be a bug

`ContextBaseStateMgr` examples:

- `_generation_tracker_key`
- `_render_context`

Pattern:

```python
_generation_tracker_key: AppContextKey[GenerationTracker] = const(
    default_factory=lambda self: self.owner._generation_tracker_key_const
)
_render_context: RenderContext = const(
    default_factory=lambda self: self.owner.render_context
)
```

Rule:

- If a field is just "copied once from owner and never meaningfully changes",
  start by trying `const`.

### `managed`

Use `managed` for authoritative published state that has a current value and a
working value inside a transaction.

Use it when:

- the value is part of the boundary-visible committed state
- failed work must roll back cleanly
- successful work publishes a new snapshot

Prefer grouping related published fields into one semantic state unit when they
belong to the same logic unit and share the same lifecycle boundary.

`ContextBaseStateMgr` example:

- legacy fields:
  - `_children`
  - `_committed_ui`
  - `_own_committed_ui`
  - `_own_committed_ui_entries`
- lifecycle shape:
  - `_subtree: FrozenContextSubtreeState = managed(...)`

Why those fields were grouped:

- they describe one published subtree snapshot
- rollback wants to restore them as one unit
- commit wants to publish them as one unit
- they share the same published lifetime
- a single state unit makes the ownership boundary explicit

Pattern:

```python
@freezable_dataclass(frozen_type="FrozenContextSubtreeState")
class ContextSubtreeState:
    children: list[tuple[SlotId, SlotContext]] = field(default_factory=list)
    own_ui: list[UiNode] = field(default_factory=list)
    own_ui_entries: list[UiSnapshotEntry] = field(default_factory=list)
    ui: list[UiNode] = field(default_factory=list)


@frozen_dataclass(mutable_type=ContextSubtreeState)
class FrozenContextSubtreeState:
    pass


_subtree: FrozenContextSubtreeState = managed(default=FrozenContextSubtreeState())
```

Alternative pattern:

- use a freezable record when the unit is fundamentally a value snapshot
- use a nested `@managed_context` class when the unit is better modeled as a
  modular state object with its own lifecycle fields and behavior boundary

Rules:

- Group fields only when they represent one semantic state unit.
- The test is not "do these values usually change together".
- The test is "would these values belong to the same modular state object if we
  were designing this subsystem cleanly from scratch".
- Fields in one grouped state unit should share the same lifetime and ownership
  boundary.
- Do not create arbitrary "bucket" structs just to reduce line count.
- If rollback/commit naturally reason about one immutable published snapshot,
  use a freezable record.
- If the grouped unit wants its own internal lifecycle field semantics, prefer
  a nested managed-context class instead of forcing it into a freezable shape.
- If a field stands on its own, keep it as its own field.

### `transient`

Use `transient` for pass-local scratch that exists only while a transaction in
that field's transaction group is active.

Use it when:

- the value is created during a pass
- the value must not survive commit/rollback as authoritative state
- the value should disappear when the transaction ends

`ContextBaseStateMgr` examples:

- `_scope_active`
- `_staged_state`

Patterns:

```python
_scope_active: bool = transient(default=False, tx_group=PASS_TX_GROUP)

_staged_state: ContextStagedState | None = transient(
    default=None,
    working_default_factory=ContextStagedState,
    tx_group=PASS_TX_GROUP,
)
```

Rules:

- Use a direct scalar transient for a single scalar value.
- Do not introduce a one-field dataclass for a scalar transient. The removed
  `ContextPassControl(scope_active: bool)` wrapper is the example of what not
  to do.
- Use `working_default_factory` when a transient value should be absent by
  default and lazily materialized only inside an active transaction.
- Keep transient records small and semantically tight. `ContextStagedState`
  exists because `ui` and `ui_entries` are staged and consumed together.

### `binding`

Use `binding` for retained external references whose identity matters and whose
accept/release behavior is transactional.

Use it when:

- the field holds a borrowed retained object
- commit/rollback must control replacement
- identity comparison is the right semantic

This was not the primary classification problem in `ContextBaseStateMgr`, but
other slot classes will need it for slot-call and external-store bindings.

### `owned`

Use `owned` for retained child/resource ownership when the state manager is the
logical owner of the lifetime.

Use it when:

- the field owns the resource or child
- rollback must discard newly staged owned values
- commit publishes the new owned value as the authoritative one

Current guidance:

- use `owned` to document ownership intent
- do not invent extra local scratch around owned values unless lifecycle truly
  cannot express the needed sequencing

### `local_store`

Use `local_store` only for inert helpers and caches that are intentionally not
authoritative boundary state.

Use it when all of the following are true:

- rollback should not restore it
- commit should not publish it
- losing or keeping it does not change observable boundary semantics
- it is genuinely just a helper cache, memo, or implementation convenience

Strong rule:

- If a field affects visible structure, visible UI, dirty propagation, retained
  bindings, or child ownership, it is not `local_store`.

`ContextBaseStateMgr` outcome:

- no `local_store` field was justified during the initial classification pass

Do not create a `LocalCache` record preemptively "for leftovers". Leftovers must
be re-justified one by one.

### Remove The Field

This must always be an available outcome.

`ContextBaseStateMgr` example:

- `_literal_initialized`
- `_literal_index`
- `lit_dirty(...)`

These were removed because the actual dirty semantics were already derivable
from slot-expression initialization and binding presence. Preserving the fields
would have carried legacy bookkeeping forward without a real semantic need.

Rules:

- Before assigning a lifecycle kind, prove the field is still needed.
- If the runtime can derive the same fact from published state, working state,
  or existing call semantics, remove the field.

## Grouping Rules

### Prefer semantic records, not mechanical records

Create a dataclass only when the grouped fields form one meaningful state unit.

Good examples:

- `ContextSubtreeState`
  - published subtree state unit
- `ContextStagedState`
  - staged UI scratch produced and consumed as one pass-local unit

Bad examples:

- `ContextPassControl(scope_active: bool)`
  - one scalar wrapped in a struct for no semantic gain
- `ContextRollbackState(...)` that only mirrors published values already
  available via `self.current`

### Prefer `self.current` over explicit "prior committed" scratch

If rollback logic needs the previously published value, first ask whether that
value is already available from `self.current.<field>`.

For published state:

- do not copy "prior committed" values into transient scratch unless there is a
  real semantic reason
- prefer reading the current published snapshot directly

For `ContextBaseStateMgr`, this means values such as a prior committed native
root should be rewritten to use the current managed state rather than copied
into a separate transient rollback record.

## Parent Definitions And Inheritance

Lifecycle field declarations are inherited through the managed context MRO.

Base definition:

```python
@managed_context
class StateMgrBase:
    owner: Any = const()
```

Implications for derived classes:

- `ContextBaseStateMgr` already has `owner`
- do not redeclare `owner` unless you are intentionally overriding it
- do not manually assign `owner` in `__init__`
- construct the state manager with the generated constructor:
  `_state_mgr_cls(owner=self)`

The lifecycle decorator merges field specs across the MRO. A derived override is
only valid when it preserves the field semantics:

- same kind
- same compare semantics
- same `tx_group`
- compatible freeze/thaw/state semantics
- annotation narrowed or equal

Practical rule:

- put genuinely shared fields in the parent managed class
- only override in a child when narrowing or replacing defaults, not when
  changing the semantic meaning of the field

## Constructor Rules

When a class is decorated with `@managed_context`, lifecycle generates the
constructor behavior through `_ManagedContextBase.__init__(**values)`.

That constructor:

- accepts lifecycle field values as keyword arguments
- creates the lifecycle state object
- resolves defaults and default factories
- builds current and working views

Migration rules:

- do not write a custom `__init__` just to assign lifecycle fields
- do not call `super().__init__(owner)` from a child state manager in the LCM
  path
- instantiate with keyword arguments only for true constructor inputs

For `ContextBaseStateMgr`, the correct usage is:

```python
self._state_mgr = self._state_mgr_cls(owner=self)
```

Everything else should come from field defaults or default factories.

## Transaction Group Rules

Do not assign a non-default transaction group casually. Use a named group only
when the field truly participates in a different transaction lifecycle.

`ContextBaseStateMgr` example:

```python
PASS_TX_GROUP = "context_pass"
```

Use `PASS_TX_GROUP` for pass-local transient state because:

- pass scratch should exist only during the pass
- published subtree state should remain in managed published state
- pass scratch and published snapshots have different lifetimes

Rules:

- published authoritative state usually stays in the default transaction group
- pass-local scratch uses the pass transaction group
- name the constant for the group and keep the name stable

## Worked Example: `ContextBaseStateMgr`

Legacy imperative fields in
`pyrolyze/src/pyrolyze/runtime/context_state/context_base.py`:

- `_generation_tracker_key`
- `_render_context`
- `_children`
- `_scope_active`
- `_pass_child_order`
- `_pass_child_dirty`
- `_committed_ui`
- `_own_committed_ui`
- `_own_committed_ui_entries`
- `_pass_committed_ui`
- `_pass_own_committed_ui`
- `_pass_own_committed_ui_entries`
- `_staged_ui`
- `_staged_ui_entries`
- `_pass_committed_native_root`

Lifecycle redesign decisions:

- `_generation_tracker_key`
  - `const`
  - fixed owner-derived configuration
- `_render_context`
  - `const`
  - fixed owner-derived configuration
- `_children`, `_committed_ui`, `_own_committed_ui`, `_own_committed_ui_entries`
  - grouped into one managed freezable snapshot
  - one published subtree state
- `_scope_active`
  - direct transient scalar in `PASS_TX_GROUP`
  - not authoritative, not worth a struct
- `_staged_ui`, `_staged_ui_entries`
  - grouped transient scratch in `ContextStagedState`
  - one pass-local staging unit
- `_pass_*` rollback scratch
  - do not automatically preserve as new transient fields
  - first ask whether the data should come from `self.current` or from other
    more semantically correct lifecycle fields
- `_literal_*`
  - removed
  - legacy bookkeeping was unnecessary once the actual dirty semantics were
    re-checked

Important:

- the current `context_state_lcm/context_base.py` file is still an intermediate
  migration step
- the field semantics are being locked in before the method bodies are rewritten
- method bodies that still refer to legacy owner fields are scaffolding, not the
  final lifecycle usage pattern

## Anti-Patterns

Do not do these during migration:

- Copy every legacy field directly into lifecycle with the same shape.
- Keep a handwritten `__init__` that assigns lifecycle-managed fields.
- Invent `local_store` containers for fields you have not classified.
- Wrap a scalar in a dataclass just because it was convenient.
- Mirror published state into transient "prior committed" scratch when
  `self.current` already expresses the same thing.
- Preserve a legacy field without re-proving that the runtime still needs it.
- Use `Any` where the real type is available and stable.

## Repeatable Checklist

For each state manager class:

1. List every legacy field and every helper record it uses.
2. For each field, decide whether it is `const`, `managed`, `binding`,
   `owned`, `transient`, `local_store`, or removable.
3. Ask whether related fields form one semantic record or should remain
   separate.
4. Replace owner-copied fixed values with `const(default_factory=...)`.
5. Replace published mutable state units with `managed`, using either a
   freezable record or a nested managed-context class depending on whether the
   unit is better modeled as a snapshot or a modular lifecycle object.
6. Replace pass-local scratch with `transient`, and use a non-default
   `tx_group` only when the lifetime truly differs.
7. Eliminate one-field wrapper dataclasses.
8. Eliminate explicit rollback copies of values that should come from
   `self.current`.
9. Remove the handwritten state-manager `__init__` unless it is doing
   something lifecycle cannot express.
10. Verify the context object still constructs the manager via the generated
    constructor, typically `_state_mgr_cls(owner=self)`.
11. Re-question whether any remaining field is actually needed.
12. Only after the field semantics are stable, rewrite the methods to use
    `self.current`, `self.working`, and transaction-group-aware transient state.

## Short Version

The pattern is:

- classify every field by semantics, not by legacy name
- use `const` for fixed owner-derived configuration
- use `managed` for published boundary state
- use `transient` for pass scratch
- use `local_store` only for true caches
- remove fields that are no longer semantically necessary
- inherit shared lifecycle fields from the parent managed class
- let `@managed_context` generate the constructor
- use grouped state units only for real semantic modules
- choose freezable when the unit is snapshot-like
- choose nested managed-context when the unit wants its own lifecycle surface
- prefer `self.current` over transient copies of previously committed state

If we follow those rules consistently, the remaining `*StateMgr` migrations
should become slower in the short term but much cleaner, more uniform, and much
safer to refactor afterward.
