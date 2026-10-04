# Lifecycle Nuovo Factory Feature Design

## Goal

Introduce a new declarative factory concept for `lifecycle.py` that can derive
field values from the context instance while still using the existing
`default_factory` surface rather than introducing a parallel baseline-default
API.

This context-aware factory concept applies to both:

- `default_factory`
- `working_default_factory`

Both factory hooks should use the same injected-parameter rules and the same
compiled runner model.

The motivating use case is self-referential initialization such as:

```python
managed(default_factory=lambda self: self.x + self.y)
```

or, for transaction-local scratch:

```python
transient(working_default_factory=lambda working: ContextStagedState())
```

The aim is to preserve a declarative programming model while making a small
class of common state derivations much easier to express, with minimal API
growth.

## Design Intent

This feature is intended to reduce imperative initialization boilerplate, not to
replace normal methods with hidden computation graphs.

The constraints should therefore be:

- small surface area
- explicit supported parameter names
- deterministic resolution rules
- immediate failure on bad ordering or cycles
- no "magic" fallback to arbitrary local variables or ambient globals

## Existing Initializer Surface

Today the relevant lifecycle initializer knobs are:

- `default`
- `default_factory`
- `initial_working`

Only `default_factory` is currently a factory.

This proposal adds a new family of factories that may request selected context
views as parameters.

## Proposed Concepts

### 1. Context-Aware Factory Hooks

A lifecycle field may declare a factory hook that can receive one of a small
number of special context parameters.

The two hooks in scope are:

- `default_factory`
- `working_default_factory`

Example:

```python
managed(default_factory=lambda self: self.x + self.y)
```

The factory is still declarative: it is attached to the field spec and invoked
by lifecycle machinery, not user code.

### 2. Supported Context Parameters

Only the following parameter names should be recognized:

- `self`
  - the default view of the context
- `working`
  - the working view
- `current`
  - the current view

Nothing else should be injected.

That means:

- `lambda self: ...` is valid
- `lambda current: ...` is valid
- `lambda working: ...` is valid
- `lambda ctx: ...` is not special and should not be injected

This keeps the semantics narrow and readable.

## Recommendation: Inspect First, Do Not Probe by Failure

The implementation should not attempt:

```python
try:
    return factory()
except MissingParameterException:
    ...
```

That approach is too magical and couples runtime behavior to arbitrary
user-level exceptions.

Instead:

1. inspect the callable signature once
2. determine whether it requests supported special parameters
3. call it with exactly those arguments
4. reject unsupported required parameters

So the correct model is signature-driven dispatch, not optimistic invocation.

The same resolution model should apply to both:

- `default_factory`
- `working_default_factory`

## Proposed Factory Resolution Rules

Given either factory callable:

1. Inspect its named parameters.
2. Allowed required positional-or-keyword / keyword-only parameter names are:
   - `self`
   - `working`
   - `current`
3. Build the call kwargs from those names only.
4. If any other required parameter exists, raise a `TypeError`.
5. If the callable has `*args` or `**kwargs`, do not use them for injection.
6. Call the function with explicit keyword arguments only.

Example:

```python
lambda self: ...
```

receives:

```python
factory(self=<default view>)
```

Example:

```python
def f(current, working): ...
```

receives:

```python
factory(current=<current view>, working=<working view>)
```

## Where This Feature Makes Sense

### Good Fit

- `default_factory`-like state derivation from existing fields
- immutable/frozen aggregate construction
- pass-local scratch derived from existing context state
- lifecycle-managed derived setup that would otherwise require imperative
  "if None then initialize" code

### Risky But Sometimes Useful

- `managed` current/default value derivation from other committed fields
- frozen snapshot defaults based on other state

### Probably Not Suitable

- arbitrary resource construction with hidden side effects
- binding/owned retained resource allocation by incidental reads
- complex logic that effectively wants a method, not a declarative field

## Separate Semantics by Field Kind

This feature should not mean the same thing for every field kind.

### `transient`

This is the best initial target.

A transaction-local factory is a natural fit for transient pass scratch because:

- the value disappears after transaction end
- lazy materialization is unsurprising
- there is no published-state ambiguity

This aligns well with a proposed:

- `working_default_factory`

for `transient` only.

### `managed`

This is much trickier.

If a managed working default is created lazily on first field access, behavior
becomes dependent on incidental access patterns.

That makes mutation timing difficult to reason about.

So for `managed`, there are really two different concepts:

1. derive the baseline/default value
2. derive a transaction working value

Only the first is appropriate for a context-aware baseline factory in the initial
feature.

A managed per-transaction working default would require a separate, explicit
concept tied to enlistment or first working materialization. That should not be
smuggled into this feature.

### `binding` / `owned`

Not a good initial target.

Self-aware or working-default factories for retained resource fields risk:

- hidden resource allocation
- rollback/commit surprises
- lifetime semantics coupled to access patterns

That is too much magic for an initial declarative feature.

## Proposed API Surface

### Preferred Option: Extend `default_factory`

Keep:

- `default_factory=...`

but allow it to request `self`, `working`, or `current`.

This is the smallest API surface increase and is fully incremental.

Examples:

```python
managed(default_factory=lambda self: FrozenContextSubtreeState())
```

```python
transient(default_factory=lambda self: None)
```

Rationale:

- adding a parameter to the factory is an explicit authored choice
- zero-arg factories keep their existing semantics
- no separate baseline-default knob is required
- the runtime path can stay fast if the invocation strategy is compiled once

## Recommended Initial Scope

Keep the first implementation small:

1. Extend `default_factory`
   - zero-arg behavior remains unchanged
   - computes baseline/current default value
   - may request `self`, `current`, `working`
2. Add `working_default_factory`
   - allowed on `transient` only
   - provides tx-local lazy value creation
   - may request `self`, `current`, `working`
3. Do not add support for `binding` or `owned`

This keeps the feature incremental and avoids unnecessary API growth.

## Invocation Semantics

### Parameterized `default_factory`

Used when the field has no explicitly supplied constructor value.

It computes the field's baseline value for the context instance.

Recommended rules:

- evaluate after const/basic constructor wiring is available
- do not guarantee arbitrary field ordering
- if required dependent fields are unavailable, fail immediately

This is acceptable because the intent is "works or fails fast".

### `working_default_factory`

Used only for `transient` and only when:

- a transaction is active
- the transient field has no working value yet

It should materialize a fresh transaction-local scratch value.

Like `default_factory`, it may request:

- `self`
- `current`
- `working`

After commit or rollback:

- transient value disappears as usual

## Cycle Detection

Cycle detection is required.

Example bad case:

```python
a = managed(default_factory=lambda self: self.b)
b = managed(default_factory=lambda self: self.a)
```

or:

```python
scratch = transient(working_default_factory=lambda working: working.scratch)
```

Minimum acceptable behavior:

- maintain a per-context stack/set of `(field_name, mode)` currently being
  resolved
- if the same field is re-entered during its own factory resolution, raise a
  clear `RuntimeError`

Suggested error:

- `"lifecycle factory cycle detected while resolving field 'x'"`

The system does not need to recover. Immediate failure is fine.

## Ordering Semantics

This feature should not promise full dependency sorting between fields.

Instead:

- fields resolve on demand
- if a field depends on another field that is not yet available, it fails
- this is acceptable and keeps the model simple

That matches the user's experience from datatrees:

- usually it works
- otherwise it fails immediately and visibly

## Interaction With Views

The meaning of injected parameters should be:

- `self`
  - the default/public view
- `current`
  - committed/current view
- `working`
  - working view

For baseline/default `default_factory`, `working` may or may not be meaningful
depending on field kind and active transaction state. The implementation should
document this clearly.

For `transient(working_default_factory=...)`, all three views are meaningful
inside an active transaction.

### Required View Closure

To keep context-aware factories and lifecycle code predictable, the current and
working views should be closed under `.current` and `.working`.

Required identities:

- `self.current.current is self.current`
- `self.current.working is self.working`
- `self.working.current is self.current`
- `self.working.working is self.working`

The default/public view should also navigate to those same canonical sibling
views:

- `self.current` -> current view
- `self.working` -> working view

This avoids asymmetry where an injected view behaves differently depending on
which view object the factory happened to receive first.

The consequence is that context-aware factories may freely navigate between
current and working views using normal attribute access rather than relying on
special injected-only behavior.

## Example: Useful Pattern

```python
@managed_context
class Example:
    x: int = managed(default=1)
    y: int = managed(default=2)
    total: int = managed(default_factory=lambda self: self.x + self.y)
```

## Example: Transaction Scratch

```python
@managed_context
class Example:
    staged: dict[str, int] | None = transient(
        default=None,
        working_default_factory=dict,
    )
```

or with context-aware access:

```python
transient(
    default=None,
    working_default_factory=lambda current: {"generation": current.generation},
)
```

## Implementation Notes

Likely internal machinery:

- extend `FieldSpec` with:
  - compiled `default_factory` runner metadata
  - `working_default_factory`
  - compiled `working_default_factory` runner metadata
- inspect supported parameter names at class-decoration time
- compile a static invocation strategy once
- add a guarded resolution path with cycle detection
- keep resolution code centralized rather than scattering per-kind special cases

## Summary

This feature is worth exploring because it can reduce imperative
initialization boilerplate without giving up declarative guardrails.

The safe initial version is:

- explicit parameter names only
- signature-driven invocation
- compile the invocation runner at decoration time
- cycle detection
- parameterized `default_factory` for baseline/default derivation
- `working_default_factory` for `transient` only

That keeps the model small, predictable, and aligned with the broader goal of
constraining stateful code into a limited set of tested lifecycle semantics.
