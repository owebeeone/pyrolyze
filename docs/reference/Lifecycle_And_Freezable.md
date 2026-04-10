# Lifecycle And Freezable

`pyrolyze.lifecycle` and `pyrolyze.freezable` solve two related problems:

- `freezable` gives values an explicit mutable form and an explicit frozen form.
- `lifecycle` gives objects an explicit published form and an explicit working form.

That pairing is useful because declarative systems usually need both:

- a stable, authoritative snapshot that other code can safely observe
- a speculative or mutable form that can be edited, validated, committed, or rolled back

In practice:

- use `freezable` when you want a value-level mutable/frozen pair
- use `lifecycle` when you want object-level transaction semantics over fields
- use them together when your lifecycle-managed authoritative state should be stored as frozen snapshots, while the working state stays mutable

This document is a reference for the current public surface of:

- `pyrolyze.freezable`
- `pyrolyze.lifecycle`

It also includes practical design patterns for:

- pass scratch vs published state
- multiple transaction groups
- storing models as frozen snapshots
- transactional file persistence
- binding and owned resource management

## Why These Modules Exist

The core requirement is not "mutability" by itself. The real requirement is to separate different kinds of state clearly.

In PyRolyze-like systems you commonly need all of these at once:

- a published, authoritative state
- speculative working edits
- pass-local scratch state
- cached local helpers that should not participate in commit/rollback
- external resources that must be retained or released correctly

Imperative code tends to blur these roles together. One object grows fields like:

- `current_*`
- `pending_*`
- `_pass_*`
- `_cache_*`
- `_committed_*`
- `_staged_*`

That works for a while, but it becomes hard to answer simple questions:

- what rolls back?
- what survives a failed pass?
- what is visible outside the active transaction?
- what owns this resource?
- what order do commits happen in?

`lifecycle` turns those implicit rules into explicit declarations.

`freezable` complements that model by making value transitions explicit too:

- mutable value -> frozen snapshot
- frozen snapshot -> mutable working copy

That is especially useful when you want transient behavior decoupled from mutable behavior:

- transient state should exist only while a transaction group is active
- mutable model editing should happen in a thawed working value
- published model storage should remain frozen and stable until commit

## Mental Model

### `freezable`

Think in terms of value pairs:

- mutable authoring form
- frozen snapshot form

The conversion boundary is explicit:

- `to_frozen()`
- `to_mutable()`
- `to_thawed()`

### `lifecycle`

Think in terms of field classes:

- `managed`: published transactional state
- `binding`: retained external resource with transactional replacement semantics
- `owned`: retained identity-owned resource with transactional replacement semantics
- `transient`: transaction-scoped overlay state
- `local_store`: non-transactional local cache/helper state
- `derived`: manually stored derived state that resets after commit/rollback/close
- `const`: fixed read-only value
- `static`: write-once value

Then think in terms of views:

- `self.current`: read-only published state
- `self.working`: working view for transactional reads and writes
- `self`: default view that reads current state unless a working overlay exists

Finally, think in terms of transaction groups:

- fields can belong to different groups
- groups can be started, committed, and rolled back independently
- this allows "published state" and "pass scratch" to be decoupled

## Freezable Reference

Public exports:

- `HintResolutionMode`
- `freezable_dataclass`
- `frozen_dataclass`
- `thawable_dataclass`
- `thawed_dataclass`

### Pairing Styles

There are two symmetric pairing styles.

### Mutable-First Pairing

Use:

- `@freezable_dataclass(...)`
- `@frozen_dataclass(...)`

This is the right choice when the mutable class is the natural authored form.

Example:

```python
from pyrolyze.freezable import freezable_dataclass, frozen_dataclass


@freezable_dataclass(frozen_type="FrozenTodo")
class Todo:
    title: str
    done: bool = False


@frozen_dataclass(mutable_type=Todo)
class FrozenTodo:
    pass


todo = Todo(title="Write docs")
frozen = todo.to_frozen()
editable = frozen.to_mutable()
editable.done = True
```

Properties of this style:

- the mutable class is a normal dataclass
- the frozen peer is a real `dataclass(frozen=True)`
- the pair is explicit in the type system

### Frozen-First Pairing

Use:

- `@thawable_dataclass(...)`
- `@thawed_dataclass(...)`

This is the right choice when the frozen class is the canonical storage form.

Example:

```python
from pyrolyze.freezable import thawable_dataclass, thawed_dataclass


@thawable_dataclass(thawed_type="EditableSettings")
class FrozenSettings:
    theme: str
    recent_files: tuple[str, ...]


@thawed_dataclass(frozen_type=FrozenSettings)
class EditableSettings:
    pass


frozen = FrozenSettings(theme="light", recent_files=("a.txt", "b.txt"))
editable = frozen.to_thawed()
editable.recent_files.append("c.txt")
next_frozen = editable.to_frozen()
```

### Deep Conversion

`freezable` can do deep conversion for:

- nested paired objects
- `list[...]` <-> `tuple[...]` normalization

By default:

- mutable-side `list[...]` often freezes to `tuple[...]`
- frozen-side `tuple[...]` often thaws to `list[...]`
- nested paired objects convert recursively by calling their conversion methods

Example:

```python
@freezable_dataclass(frozen_type="FrozenItem")
class Item:
    value: int


@frozen_dataclass(mutable_type=Item)
class FrozenItem:
    pass


@freezable_dataclass(frozen_type="FrozenBag")
class Bag:
    items: list[Item]
    labels: list[str]


@frozen_dataclass(mutable_type=Bag)
class FrozenBag:
    pass


bag = Bag(items=[Item(1), Item(2)], labels=["a", "b"])
frozen = bag.to_frozen()

assert isinstance(frozen.items, tuple)
assert isinstance(frozen.items[0], FrozenItem)
assert isinstance(frozen.labels, tuple)
```

### Decorator Parameters

#### `freezable_dataclass(...)`

Important parameters:

- `frozen_type`
- `slots=True`
- `freeze_params=True`
- `list_params=True`
- `hint_resolution=HintResolutionMode.STRICT_FRAME`

Meaning:

- `freeze_params=True` enables recursive paired-object conversion
- `list_params=True` enables list/tuple normalization
- `slots=True` gives slotted dataclasses by default

#### `frozen_dataclass(...)`

Important parameters:

- `mutable_type`
- `slots=True`
- `hint_resolution=...`

The decorator builds the frozen peer from the mutable dataclass fields.

#### `thawable_dataclass(...)`

Important parameters:

- `thawed_type`
- `slots=True`
- `freeze_params=True`
- `list_params=True`
- `hint_resolution=...`

This is the frozen-first mirror of `freezable_dataclass`.

#### `thawed_dataclass(...)`

Important parameters:

- `frozen_type`
- `slots=True`
- `hint_resolution=...`

### Inheritance

Freezable pairs preserve dataclass inheritance relationships.

If:

- `Child` inherits from `Base`
- `FrozenChild` is generated from `Child`
- `FrozenBase` is generated from `Base`

then `FrozenChild` inherits from `FrozenBase`.

That makes freezable pairs suitable for real model hierarchies, not just flat records.

### Hint Resolution Modes

`HintResolutionMode` controls how postponed annotations are resolved during conversion.

Modes:

- `STRICT_FRAME`
- `FRAME_WITH_FALLBACK`
- `STRICT_MODULE`

Guidance:

- use `STRICT_FRAME` when you want the most intuitive behavior for locally defined classes
- use `FRAME_WITH_FALLBACK` when you want portability with best-effort local support
- use `STRICT_MODULE` when portability matters more than local-scope forward references

If local forward references matter and the class is not module-level, `STRICT_MODULE` may not resolve them the way you want.

## Lifecycle Reference

Public exports:

- `FieldSpec`
- `BindingBase`
- `DEFAULT_TRANSACTION`
- `GroupTransactionManager`
- `LifecycleContext`
- `LifecycleTransaction`
- `LifecycleValidatorReturnedFalse`
- `Record`
- `TransactionManager`
- `binding`
- `commit_order_key`
- `commit_validator`
- `const`
- `derived`
- `lifecycle_field`
- `local_store`
- `managed`
- `managed_context`
- `on_before_commit`
- `on_after_commit`
- `on_after_rollback`
- `owned`
- `static`
- `transient`

### The Core Shape

Declare a lifecycle-managed class with `@managed_context` and field helpers.

Example:

```python
from pyrolyze.lifecycle import managed, managed_context, transient


@managed_context
class Counter:
    value: int = managed(default=0)
    seen_in_pass: bool = transient(default=False)
```

Instances behave like ordinary Python objects:

```python
counter = Counter()
```

But writes to transactional fields require an active transaction manager:

```python
from pyrolyze.lifecycle import TransactionManager

txm = TransactionManager()
counter = Counter(transaction_manager=txm)

with txm.begin():
    counter.value = 3
```

### Field Kinds

#### `managed(...)`

Use for authoritative published state.

Important parameters:

- `compare="value"` or `compare="identity"`
- `tx_group=...`
- `default=...`
- `default_factory=...`
- `initial_working=...`
- `freeze=...`
- `thaw=...`
- `state_factory=...`
- `state_copy=...`

Key behavior:

- published value lives in the current record
- writes stage into the working record for the field's transaction group
- commit publishes the working value
- rollback discards it

Example:

```python
@managed_context
class Counter:
    value: int = managed(default=0)
```

#### `binding(...)`

Use for retained resource references that follow transactional replacement semantics.

Identity comparison is used automatically.

Example uses:

- backend binding handles
- retained subscriptions
- temporary file replace bindings

On commit:

- the new binding is accepted
- the previous binding is released

On rollback:

- the staged binding is released

If the field annotation is a mapping of bindings, binding-map retain/release rules are applied per contained binding instance.

#### `owned(...)`

Use for owned identity-based resources.

At the lifecycle core level it currently shares the same field mechanics as `binding`, but the intent is stronger ownership semantics.

Use it when the field conceptually owns the object or subtree being retained.

Examples:

- child state objects
- owned resource nodes
- retained subordinate contexts

#### `transient(...)`

Use for transaction-scoped scratch or pass state.

Important parameters:

- `tx_group=...`
- `default=...`
- `default_factory=...`
- `working_default_factory=...`

`working_default_factory` is especially important for pass scratch:

- outside an active transaction the field resolves to its default
- inside an active transaction the field can lazily materialize a working-only value

Example:

```python
PASS = "pass"


@managed_context
class RenderPassState:
    visited: set[str] | None = transient(
        default=None,
        working_default_factory=set,
        tx_group=PASS,
    )
```

That means:

- no pass transaction active -> `visited` behaves like its default
- pass transaction active -> `visited` becomes a lazily created working set

#### `local_store(...)`

Use for non-transactional local caches and helpers.

This is intentionally outside commit/rollback semantics.

Good uses:

- memo caches
- helper closures
- lazily created local helpers
- runtime locals that can survive speculative work

Bad uses:

- authoritative published state
- values that must roll back
- resources whose visibility or ownership must stay transactional

#### `derived(...)`

Use for manually stored derived values that should reset after commit, rollback, or close.

This is useful when you want a lifecycle field for a cached derived value but do not want it to become durable published state.

#### `const(...)`

Read-only field initialized at construction time.

After construction it cannot be assigned.

#### `static(...)`

Write-once field.

It starts uninitialized unless you provide a default, and it can be assigned exactly once.

#### `commit_order_key(...)`

Declares a per-group commit ordering key.

The transaction manager sorts dirty contexts by `commit_order_key_for(group)`, highest first.

This is useful when resources must be committed in a known order.

#### `commit_validator(...)`

Declares a per-group validator callable.

The validator receives the context and returns:

- `True` to allow commit
- `False` to reject commit
- or it may raise an exception

If it returns `False`, `LifecycleValidatorReturnedFalse` is raised.

#### `on_before_commit(...)`

Declares a per-group pre-commit hook as a lifecycle field declaration.

It is not stored as ordinary current or working state. Instead it is compiled at
decoration time into a group-scoped runner table.

Supported injected parameters are:

- `self`
- `current`
- `working`
- `tx_group`

Use this when you want declarative hook registration rather than overriding the
instance method.

#### `on_after_commit(...)`

Declares a per-group post-commit hook as a lifecycle field declaration.

Like the other hook kinds, it is not stored as an ordinary lifecycle value
field. It is compiled into a runner table and invoked after the group's commit
has been applied.

Supported injected parameters are:

- `self`
- `previous`
- `current`
- `tx_group`

Important retained-resource rule:

- `previous` remains valid until all post-commit hook runners for that group
  have completed

That means replaced `binding` / `owned` values are released only after those
post-commit runners finish, and the cleanup still runs if a hook raises.

#### `on_after_rollback(...)`

Declares a per-group post-rollback hook as a lifecycle field declaration.

Supported injected parameters are:

- `self`
- `current`
- `tx_group`

### Views: Default, Current, and Working

Each managed instance exposes three views over the same state object:

- default view: `self`
- current view: `self.current`
- working view: `self.working`

Semantics:

- `self.current.field` always reads published state
- `self.working.field` reads the working value when present, otherwise published state
- `self.field` behaves like the ordinary authoring surface and normally reads through the same overlay rules

Current view is read-only:

```python
ctx.current.value = 10  # raises
```

Working view is the right place for explicit working mutations:

```python
with txm.begin():
    ctx.working.value = 10
```

And ergonomic nested mutable edits are supported when the field getter materializes the working value:

```python
with txm.begin():
    ctx.working.model.items.append("x")
```

### Default Factories

`lifecycle` supports contextual factories for both published defaults and transient working defaults.

Supported named parameters:

- `self`
- `current`
- `working`

Example:

```python
def build_triplet(self, current, working) -> tuple[int, int, int]:
    return (self.base, current.base, working.base)


@managed_context
class Example:
    triplet: tuple[int, int, int] = managed(default_factory=build_triplet)
    base: int = managed(default=7)
```

For transient pass state:

```python
def build_pass_items(self, current, working) -> list[int]:
    return [self.base, current.base, working.base]


@managed_context
class Example:
    base: int = managed(default=1)
    items: list[int] | None = transient(
        default=None,
        working_default_factory=build_pass_items,
    )
```

Factory cycles are detected and raise an error.

### Transaction Managers

There are two layers.

#### `GroupTransactionManager`

Use this only when you intentionally want a single group manager.

Responsibilities:

- begin one group
- enlist dirty contexts for one group
- validate one group
- commit one group
- rollback one group

#### `TransactionManager`

This is the normal entry point.

It coordinates multiple named transaction groups.

Example:

```python
PUBLISH = "publish"
PASS = "pass"

txm = TransactionManager(tx_groups={PUBLISH, PASS})
```

The default transaction group is always present:

- `DEFAULT_TRANSACTION`

So `tx_groups={PUBLISH, PASS}` means the manager knows:

- `DEFAULT_TRANSACTION`
- `PUBLISH`
- `PASS`

### Transaction Group Semantics

Transaction groups let different fields participate in different transactional domains.

This is the most important use case when you want transient behavior decoupled from mutable published behavior.

Example:

```python
PUBLISH = "publish"
PASS = "pass"


@managed_context
class DocumentState:
    model: "FrozenDocument" = managed(
        default_factory=lambda: FrozenDocument(title="", items=()),
        thaw=lambda frozen: frozen.to_thawed(),
        freeze=lambda thawed: thawed.to_frozen(),
        tx_group=PUBLISH,
    )
    visited_ids: set[str] | None = transient(
        default=None,
        working_default_factory=set,
        tx_group=PASS,
    )
```

Now you can do:

```python
with txm.begin(PASS):
    state.visited_ids.add("root")
```

without starting a publish transaction.

And independently:

```python
with txm.begin(PUBLISH):
    state.working.model.title = "Next title"
```

Or both:

```python
with txm.begin(PUBLISH, PASS):
    state.working.model.title = "Next title"
    state.visited_ids.add("root")
```

Important rule:

- multi-group operations are not coupled all-or-nothing transactions

If you commit multiple groups explicitly, they are committed independently in the order requested by the manager call.

That means one group may succeed while another later group fails.

When you use the context-manager form with multiple groups:

```python
with txm.begin(PUBLISH, PASS):
    ...
```

the groups are begun in the listed order and unwound in reverse order on scope exit.

### Manager API

Typical operations:

```python
txm.begin()
txm.begin(PUBLISH)
txm.begin(PUBLISH, PASS)

txm.validate()
txm.validate(PUBLISH)

txm.commit()
txm.commit(PUBLISH)
txm.commit(PUBLISH, PASS)

txm.rollback()
txm.rollback(PUBLISH)
```

No-argument forms target all configured groups for that manager, including `DEFAULT_TRANSACTION`.

Context manager form is supported:

```python
with txm.begin(PUBLISH):
    ...
```

For multiple groups:

```python
with txm.begin(PUBLISH, PASS):
    ...
```

For a multi-group scope, clean exit commits the groups in reverse lexical order and exceptional exit rolls them back in reverse lexical order.

Nested group scopes are also valid:

```python
with txm.begin(PUBLISH):
    with txm.begin(PASS):
        ...
```

### Commit Order and Validation

Each group may have:

- at most one `commit_order_key(...)`
- at most one `commit_validator(...)`

Example:

```python
PUBLISH = "publish"


def can_publish(ctx) -> bool:
    return ctx.path != ""


@managed_context
class OrderedContext:
    path: str = managed(default="", tx_group=PUBLISH)
    order_key: tuple[int, ...] = commit_order_key(default=(10,), tx_group=PUBLISH)
    validator: object | None = commit_validator(default=can_publish, tx_group=PUBLISH)
```

Commit flow for a group is:

1. validate all dirty contexts that require validation
2. sort dirty contexts by descending commit order key
3. apply commits

### BindingBase

`BindingBase` is the protocol for lifecycle-managed retained resources.

Public behavior:

- `ref_count`
- `is_accepted`
- `is_closed`
- `inc_ref()`
- `accepted()`
- `dec_ref()`
- `_close()` must be implemented by subclasses

Minimal example:

```python
from pyrolyze.lifecycle import BindingBase


class SubscriptionBinding(BindingBase):
    def __init__(self, unsubscribe):
        super().__init__()
        self._unsubscribe = unsubscribe

    def _close(self) -> None:
        self._unsubscribe()
```

Pattern:

- create the binding while staging a working value
- if commit accepts it, it becomes published
- if rollback discards it, the staged binding is released and closed

### Hooks and Extensibility

You can override these methods on managed classes:

- `before_commit(self, current, working)`
- `after_commit(self, previous, current)`
- `after_rollback(self, current)`

You can also declare hook fields:

- `on_before_commit(...)`
- `on_after_commit(...)`
- `on_after_rollback(...)`

Those hook declarations are compiled into group-scoped runner tables instead of
being stored as ordinary lifecycle value fields.

Hook field parameter injection supports:

- `self`
- `current`
- `working`
- `previous`
- `tx_group`

For `on_after_commit(...)`, replaced retained values from `binding(...)` and
`owned(...)` fields are released only after the post-commit hook runners for
that group have finished. Cleanup still happens if a hook raises.

You can also call:

- `commit_order_key()`
- `commit_order_key_for(group)`
- `requires_validation()`
- `requires_validation_for(group)`
- `validate_commit()`
- `validate_commit_for(group)`

These methods are useful when integrating lifecycle with broader application policy.

## Lifecycle + Freezable Together

This is the main pattern when you want authoritative state to stay frozen while working edits remain mutable.

Example:

```python
from pyrolyze.freezable import thawable_dataclass, thawed_dataclass
from pyrolyze.lifecycle import managed, managed_context


@thawable_dataclass(thawed_type="EditableDoc")
class FrozenDoc:
    title: str
    items: tuple[str, ...]


@thawed_dataclass(frozen_type=FrozenDoc)
class EditableDoc:
    pass


@managed_context
class DocumentContext:
    doc: FrozenDoc = managed(
        default_factory=lambda: FrozenDoc(title="", items=()),
        thaw=lambda frozen: frozen.to_thawed(),
        freeze=lambda editable: editable.to_frozen(),
    )
```

Usage:

```python
txm = TransactionManager()
ctx = DocumentContext(transaction_manager=txm)

with txm.begin():
    ctx.working.doc.title = "Hello"
    ctx.working.doc.items.append("A")
```

Semantics:

- published `ctx.current.doc` stays frozen
- reading `ctx.working.doc` during the transaction thaws to a mutable working value
- commit freezes the working value back into the published record

This is the clearest way to keep mutable editing and published storage separate.

## Recommended Patterns

### Pattern: Published Model + Pass Scratch

Use separate groups.

```python
PUBLISH = "publish"
PASS = "pass"


@managed_context
class AnalyzerState:
    model: FrozenDoc = managed(
        default_factory=lambda: FrozenDoc(title="", items=()),
        thaw=lambda value: value.to_thawed(),
        freeze=lambda value: value.to_frozen(),
        tx_group=PUBLISH,
    )
    seen_ids: set[str] | None = transient(
        default=None,
        working_default_factory=set,
        tx_group=PASS,
    )
```

Why this is good:

- pass state is not forced to imply publication mutation
- the mutable document edit path stays separate from traversal scratch
- application code can activate only the group it actually needs

### Pattern: Non-Transactional Local Helper

Use `local_store`.

```python
@managed_context
class Context:
    parser_cache: dict[str, object] = local_store(default_factory=dict)
```

Use this for:

- helper objects
- reusable caches
- closures

Do not use it for values that must participate in rollback.

### Pattern: Derived Cache That Resets

Use `derived`.

```python
@managed_context
class Context:
    value: int = managed(default=1)
    cache: dict[str, int] = derived(default_factory=dict)

    def refresh_cache(self) -> None:
        self.cache = {"value": self.value}
```

This is useful when you want lifecycle-managed storage for a derived value, but you do not want it to be durable authoritative state.

### Pattern: Transactional File Replace

This is one of the strongest uses of `binding`.

Use case:

- edit a model transactionally
- serialize it
- stage a temp-file replacement
- commit publishes the model and finalizes the file replace
- rollback cleans up the temp file

Example sketch:

```python
from pathlib import Path
import os
import tempfile

from pyrolyze.lifecycle import BindingBase, binding, commit_validator, managed, managed_context


class AtomicFileReplace(BindingBase):
    def __init__(self, target: Path, data: str) -> None:
        super().__init__()
        self.target = target
        fd, tmp = tempfile.mkstemp(dir=str(target.parent), prefix=target.name + ".", suffix=".tmp")
        self._tmp_path = Path(tmp)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)

    def accepted(self) -> None:
        super().accepted()
        os.replace(self._tmp_path, self.target)

    def _close(self) -> None:
        if self._tmp_path.exists():
            self._tmp_path.unlink()


def file_is_configured(ctx) -> bool:
    return ctx.path != ""


@managed_context
class PersistedDocument:
    path: str = managed(default="")
    doc: FrozenDoc = managed(
        default_factory=lambda: FrozenDoc(title="", items=()),
        thaw=lambda value: value.to_thawed(),
        freeze=lambda value: value.to_frozen(),
    )
    pending_write: AtomicFileReplace | None = binding(default=None)
    validator: object | None = commit_validator(default=file_is_configured)

    def stage_write(self) -> None:
        text = serialize_doc(self.working.doc)
        self.pending_write = AtomicFileReplace(Path(self.path), text)
```

Usage:

```python
with txm.begin():
    ctx.working.doc.title = "Saved"
    ctx.stage_write()
```

What this buys you:

- published model commit and durable file publication are staged together
- rollback releases the staged temp file binding
- commit accepts the binding and replaces the target file atomically

This is often better than writing the file in `after_commit`, because the temp-file resource itself participates in lifecycle management.

### Pattern: Retained Child or Subtree Ownership

Use `owned` when a field conceptually owns the retained identity.

Even though the current lifecycle core uses the same underlying binding machinery for `owned`, it is still useful to declare ownership explicitly in your model.

That keeps intent clear and leaves room for stronger future ownership-specific behavior.

## Choosing Between The Modules

Use `freezable` when:

- you need explicit mutable/frozen value pairs
- you want immutable snapshots for published state
- you want ergonomic working mutation with explicit freezing on publish

Use `lifecycle` when:

- fields need commit/rollback semantics
- values belong to different transactional domains
- you need validators, commit ordering, or resource retention

Use both together when:

- your authoritative state should be frozen
- your working state should be mutable
- your pass scratch should be transient and independently scoped

## Practical Recommendations

If you are building new declarative state with these modules:

- store authoritative models as frozen values
- thaw only on working access
- freeze on commit
- keep pass scratch in a separate transaction group
- use `local_store` only for truly non-transactional helpers
- use `binding` for staged external side effects and retained resources
- use `owned` to make ownership intent explicit
- treat multi-group commit as application-controlled coordination, not automatic atomic coupling

That combination gives you a clean split between:

- declarative published state
- ergonomic mutable working edits
- explicit scratch transactions
- explicit resource lifetimes

It is a good fit for runtime context graphs, model editors, file-backed state, and other systems where "what is authoritative" and "what is merely in progress" must remain separate.
