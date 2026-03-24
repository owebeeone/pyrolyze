# Hierarchical Context Management

## Purpose

This document proposes a hierarchical, reactive context mechanism for
Pyrolyze.

The goal is to support subtree-scoped values without prop drilling while still
remaining fully dynamic and rerender-safe.

This is not intended to be GRIP-specific, but GRIP is a strong motivator:

- a subtree may need a different consumer/home context policy
- a subtree may need a small derived context subgraph rather than one plain
  value
- descendants should be able to consume that scope implicitly

The same mechanism is also useful for:

- theme and formatting scope
- locale and translation scope
- form or validation scope
- routing or navigation scope
- request/session-scoped services
- feature flags and presentation policy


## Problem

Today Pyrolyze app context is effectively root-scoped:

- one root `AppContextStore`
- implicit dependence on root defaults
- no lexical subtree overrides
- no reactive invalidation for readers when a local context value changes

That is good for true app-wide singletons, but it is not enough for authored
render trees that need local contextual meaning.

Using explicit parameters for all of this creates several problems:

- prop drilling through layers that do not care about the value
- duplication of policy plumbing
- awkward APIs where structural helpers exist only to thread state through
- no natural way to swap subtree-local context behavior

What is needed is:

- inherited contextual values
- lexical override by subtree
- reactive readers
- compatibility with component boundaries and rerenders


## Design Goals

- Add a generic no-prop-drilling mechanism to Pyrolyze.
- Allow the same override mechanism to be used at root and in subtrees.
- Allow subtree-local overrides with ordinary authored structure.
- Make context readers reactive so they invalidate when the effective value
  changes.
- Allow local values to be created once per caller slot and then provided to
  descendants.
- Cross component boundaries cleanly.
- Stay generic enough that libraries like GRIP can build their own helpers on
  top of it.


## Non-Goals

- This is not a full dependency injection framework.
- This is not a replacement for ordinary explicit parameters when explicit
  parameters are clearer.
- This is not a permission to mutate arbitrary shared objects invisibly and
  expect Pyrolyze to notice.
- This is not specifically a GRIP context API, even though GRIP should be able
  to build directly on it.


## Proposed Public Shape

### 1. App Context Key

Keep `AppContextKey[T]` as the public key type.

It identifies one context value family.

If the existing runtime shape still requires a `factory`, that should be treated
as an implementation detail or compatibility field, not as the semantic source
of authored hierarchical defaults.

For hierarchical authored context, the recommended model is:

- keys are declarations only
- the effective root context is empty by default
- values appear only through lexical overrides

That keeps the feature honest and makes root bootstrapping use the same
mechanism as subtree overrides.


### 2. Reader Hook

Add a reactive reader hook:

```python
value = use_app_context(MY_KEY)
```

Recommended semantics:

- resolve the effective value for the requested `AppContextKey` from the
  current lexical app-context view
- if no provider for that key exists, fail deterministically
- subscribe the caller slot to changes in the effective provider for that key
- invalidate the caller when that effective value changes or disappears

This should feel like a scoped reactive read, not like a global lookup.

This hook should use the same broad binding model as `use_grip(...)`:

- every call site gets a retained slot
- the slot binds to the effective proxied app-context value for that key
- reevaluation happens only when the effective proxied key/value binding
  changes

So this is not "just read from a dictionary every render." It is a slot-backed
reactive read.

The key argument is intentionally dynamic:

- the runtime binds the reader slot to the current requested key
- if the requested key changes across rerenders, the slot rebinds like
  `use_grip(...)`
- if the requested key stays the same, reevaluation should be driven by changes
  to the effective provided value, not by plain re-reading every render

At runtime the resolved argument must be an `AppContextKey`.


### 3. Provider Form

The first cut should support exactly one lexical provider form:

```python
with app_context_override[MY_KEY](value):
    ...
```

and its generalized multi-key form:

```python
with app_context_override[KEY1, KEY2, KEY3](value1, value2, value3):
    ...
```

No alternate provider spellings should exist in phase 1.

The purpose of keeping this to one named helper is to make the semantics
obvious:

- this is a dedicated Pyrolyze context-override construct
- it is not an arbitrary context-manager protocol
- it maps directly to one retained runtime override node/slot kind

Recommended semantics:

- create subtree-local overrides for one or more fixed keys
- descendants see those overrides unless shadowed by a nearer provider
- when the provided value changes across rerenders, dependent readers are
  dirtied
- when the provider disappears, dependent readers are dirtied and re-resolve
  from the next visible ancestor provider, or fail if no provider remains

This is the core no-prop-drilling primitive.

The bracketed key set should be immutable for the lifetime of that provider
slot.

That means:

- the provider slot owns one fixed ordered tuple of key identities
- the corresponding values may change across rerenders
- changing the keys at the same slot is unsupported and should be rejected
- the initial key tuple binding is effectively a one-time structural decision
  for that slot
- arity must match exactly: `N` keys require `N` values

This avoids runtime rechaining complexity and keeps dependency tracking simple:

- reader binding is keyed by requested key
- provider binding is keyed by fixed provider slot plus fixed key tuple
- only value changes need ordinary reactive invalidation


### 4. Stable Local Helper

This document does not overload `use_local(...)` for hierarchical context
reads.

If Pyrolyze exposes a plain stable slot-local ownership helper, it should be a
separate hook with ordinary slot-local semantics rather than inherited context
lookup semantics.


## Core Model

### Root App Context

The effective authored app context should be empty at root.

That means:

- no authored `use_app_context(...)` read succeeds unless some ancestor
  `app_context_override[...]` provides the key
- application bootstrap can provide root-visible values by wrapping the app body
  in `app_context_override[...]`

This makes the root case and the subtree case use the same mechanism.

Pyrolyze may still keep separate internal runtime services for things like
generation tracking or host integration, but those should not define the
semantics of authored hierarchical app context.


### Effective App-Context View

Each runtime scope should have an effective app-context view.

Conceptually:

```python
class AppContextLookup(Protocol):
    def get(self, key: AppContextKey[T]) -> T: ...
    def has(self, key: AppContextKey[Any]) -> bool: ...
```

```python
@dataclass(slots=True)
class OverlayAppContextLookup(AppContextLookup):
    parent: AppContextLookup
    local_values: dict[AppContextKey[Any], object]
```

Lookup rules:

- if the key exists in the local overlay, use it
- if the local value for a key is `None`, treat this slot as transparent for
  that key and continue to the parent lookup
- otherwise ask the parent lookup
- the root parent is an empty lookup for authored hierarchical context

This is what makes context lexical rather than global.


### Provider Slot

`app_context_override[...]` should be backed by a retained runtime slot, not by
ephemeral imperative mutation.

The provider slot owns:

- the provided keys
- the committed provided values
- a local overlay lookup for its subtree
- dependency tracking for reader slots bound to that key

This is the part that gives the mechanism rerender safety.

Recommended naming direction:

- runtime slot/context kind: `AppContextOverrideSlotContext`
- runtime handle entrypoint on the current context:
  `open_app_context_override(keys=..., values=...)`

This makes it obvious in the runtime that the override is a first-class
lexical node, not just a helper that mutates a shared dictionary.


### Reader Dependency

`use_app_context(...)` should bind to the effective provider for the requested
key.

That means readers are effectively subscribed to a scoped reactive value source.

If any of the following happen, the reader should invalidate:

- the nearest visible provider for the key changes value
- the nearest visible provider disappears
- the nearest visible provider changes identity in a way that changes the
  effective value source
- the nearest visible provider changes from a concrete value to `None`, causing
  resolution to fall through to the parent provider chain

In other words, context reads should behave like external-store reads scoped by
lexical ancestry.


## Runtime Semantics

### Scope Inheritance

Every slot/context should inherit the effective app-context lookup from its
parent scope.

This must work through:

- native container scopes
- plain-call scopes
- loop scopes
- directive scopes
- component boundaries

The last point matters most.

When a child `RenderContext` is created for a component call, it must inherit
the owner slot's effective app-context lookup, not merely the scheduler root's
global store.

Otherwise lexical providers would stop working at component boundaries.


### Mount Interaction

App context must not participate in mount resolution.

In particular:

- native mount-point selection does not inspect app context
- `mount(...)` resolution remains structural and parent/export relative
- advert/export routing remains the only supported way to expose mount surfaces
  across boundaries

So app context can influence mounting only indirectly, for example:

- a component reads app context and chooses which mounts to advertise
- a component reads app context and chooses which native layout structure to
  emit

But the mount system itself should not treat app context as part of selector
resolution.


### Reactivity

Context reads are not plain dictionary reads.

They should be reactive in the same sense that a reader of an external store is
reactive:

- a slot reads `use_app_context(MY_KEY)`
- the runtime records which provider currently satisfies that read
- provider changes dirty the dependent slot
- rerender re-resolves the effective provider/value
- if the requested key changes, the reader slot rebinds to the new key

This is the property that makes the feature safe and useful for real apps.

Without this, `app_context_override[...]` would only be syntactic sugar over
hidden global state.


## Deactivation And Recovery

Provider slots are retained and have normal Pyrolyze slot lifecycle.

That gives the expected behavior:

- if a provider is not visited in a rerender, it deactivates
- its subscribers are dirtied
- readers rerender and re-resolve against the next visible provider, or fail if
  no provider remains

This should be treated as ordinary structural churn, not as an exceptional
condition.


## Recommended Authoring Pattern

The intended consumption pattern is:

```python
scope = use_app_context(SCOPE_KEY)
```

and the intended provision pattern is:

```python
with app_context_override[SCOPE_KEY](scope):
    ...
```

This creates a generic pattern:

- `app_context_override[...]` publishes values lexically
- `use_app_context(...)` consumes them reactively

At application bootstrap, the same mechanism can be used with multiple keys:

```python
with app_context_override[THEME_KEY, LOCALE_KEY, SESSION_KEY](
    theme,
    locale,
    session,
):
    AppBody()
```

That pattern is broad enough to support many libraries without every library
reinventing its own ambient-scope system.


## GRIP As A Motivator

GRIP is a strong example of why this matters.

A GRIP "context" may not just be one plain `GripContext`. It may be a
`GripContextLike` object that:

- has a consumer context
- has a home context
- may represent a matcher or other small subgraph

Pyrolyze should not special-case that.

Instead:

- GRIP can define one `AppContextKey[GripContextLike]`
- `app_context_override[...]` can publish it to a subtree
- GRIP helpers can read the current GRIP scope via `use_app_context(...)`

That keeps Pyrolyze generic while still making GRIP integration natural.


## Why This Is Better Than More Hidden Parameters

Pyrolyze already supports one hidden runtime parameter for plain-call helpers.
That is useful, but it is not enough on its own.

The missing abstraction is not "more invisible parameters on every helper."

The missing abstraction is:

- one inherited lexical value system
- one reactive read path
- one retained provider lifecycle

Once that exists, libraries can opt into it without each one needing its own
parallel ambient-context mechanism.


## Implementation Direction

### 1. Generalize App-Context Lookup

Current app-context access should move from "always ask the scheduler-root
store" to "ask the current scope's effective app-context lookup."

For authored hierarchical context, the root lookup should be empty.


### 2. Add A Retained Provider Slot

Add runtime support for a slot-backed provider form used by
`app_context_override[...]`.

It should:

- create/update one overlay binding
- track dependents for its keys
- dirty dependents when committed values change or disappear

Recommended first-cut runtime shape:

- one dedicated slot/context kind for override nodes
- one dedicated `ContextBase` entrypoint such as
  `open_app_context_override(...)`
- one compiler lowering path that targets only the named helper
  `app_context_override[...]`
- runtime validation that the number of values matches the number of fixed
  keys


### 3. Add Reactive Reader Binding

Add `use_app_context(...)` as the hook/helper that binds to the effective
provider for one key.

This can be implemented as:

- a specialized plain-call binding, or
- a thin wrapper over an external-store-like binding

The important part is the semantics, not the exact binding class choice.


### 4. Transparent `None`

Treat `None` in an override slot as "no local value for this key; fall through
to the parent provider chain."

This is useful because a provider slot can remain structurally present while
temporarily opting out for one key.

The tradeoff is important:

- with this rule, `None` is reserved and cannot also mean a real authored value
  for hierarchical context

If authored `None` values later matter, the design should move to an explicit
unset sentinel instead.

### 5. Cross Component Boundaries

When component child `RenderContext`s are created, they must inherit the
owner slot's effective app-context lookup.

This is a required part of the design, not a later enhancement.


## Likely Compiler/Runtime Impact

The reader hook fits the existing slotted plain-call model well.

The provider form is the one place likely to need a small structural extension,
because it is lexically scoped, emits no UI of its own, and needs one-time
slot-level key binding.

Reasonable implementation directions are:

- add a dedicated directive-style lowering for `app_context_override[...]`
- or generalize Pyrolyze lexical directives so this is not a one-off feature

Either way, the intended runtime model is the same:

- retained provider slot
- lexical subtree scope
- reactive dependents


## Example

```python
THEME_KEY = AppContextKey("theme", factory=lambda _host: DEFAULT_THEME)
LOCALE_KEY = AppContextKey("locale", factory=lambda _host: DEFAULT_LOCALE)


@pyrolyze
def Card(title: str):
    theme = use_app_context(THEME_KEY)
    with row():
        text(title, colour=theme.title_colour)


@pyrolyze
def App():
    with app_context_override[THEME_KEY, LOCALE_KEY](DARK_THEME, EN_AU):
        Card("inside themed scope")
```

`Card(...)` should see `DARK_THEME` only inside the lexical provider scope,
and the same mechanism can provide multiple root-visible context values without
threading them through every intermediate layer.


## Test Plan

### 1. Reader Resolution

- reader fails deterministically when no provider exists
- reader sees nearest local provider when one exists
- nested providers shadow outer providers for the same key
- provider value `None` falls through to the parent provider
- reader key changes across rerenders rebind the slot to the new key


### 2. Reactivity

- changing a provider value dirties dependent readers
- removing a provider dirties dependent readers
- reintroducing a provider rebinds readers correctly
- unrelated keys do not dirty readers of other keys
- in a multi-key provider, changing one value dirties only readers of that key


### 3. Structural Boundaries

- provider scope crosses native container boundaries
- provider scope crosses component boundaries
- provider scope works inside keyed loops and structural churn


### 4. Multi-Key Provider Shape

- `app_context_override[K1, K2](v1, v2)` publishes both keys from one provider
  slot
- value/key arity mismatch fails deterministically
- changing one provided value does not dirty readers of unrelated provided keys


### 5. Graph Stability

- first render and rerender to the same logical context layout produce the same
  effective reads
- rerender from dramatically different prior provider structure converges to
  the same result


## Bottom Line

Pyrolyze needs a hierarchical reactive context system, not just a bigger global
app-context dictionary.

The right generic shape is:

- `with app_context_override[KEY](value):` to publish values lexically
- `use_app_context(KEY)` to consume them reactively

That gives Pyrolyze a general no-prop-drilling mechanism that libraries like
GRIP can build on without Pyrolyze becoming GRIP-specific.
