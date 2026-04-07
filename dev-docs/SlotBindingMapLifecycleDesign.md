# Slot Binding Map Lifecycle Design

## Status

Proposed.

## Purpose

The goal is to make lifecycle management uniform and testable.

Right now, lifecycle-managed state is spread across many slot classes and many
different fields. That makes correctness hard to verify because each slot type
needs bespoke tests for staged state, committed state, rollback, and teardown.

The design below unifies that story so lifecycle can be verified once at the
mechanism level instead of by re-testing every field on every slot class.

This design has three parts. They are also the intended implementation order.

## 1. Lifecycle normalization with `Freezable` context data

### Goal

Normalize lifecycle-managed state for all slot owners behind one model:

- staged state
- committed state
- commit
- rollback
- deactivate

### Design

Introduce one base class for lifecycle-managed context data:

```python
class Freezable:
    _frozen: bool

    def freeze(self) -> None: ...
    def unfreeze(self) -> None: ...

    def __setattr__(self, name: str, value: object) -> None: ...
```

```python
@dataclass(slots=True)
class SlotContextDataBase(Freezable):
    bindings: dict[Hashable, SlotBindingBase] = field(default_factory=dict)
```

Each slot context keeps:

- committed data
- staged data for the current pass

Conceptually:

```python
committed_data: SlotContextDataBase
staged_data: SlotContextDataBase | None
```

Each slot class that needs lifecycle-managed state gets its own specialized
`SlotContextDataBase` subclass.

The same class is used for both:

- committed data, which is frozen
- staged data, which is not frozen

Proposed variants:

```python
@dataclass(slots=True)
class EventHandlerSlotContextData(SlotContextDataBase):
    committed_callback: Callable[..., Any] | None = None
    committed_key: object | None = None
    staged_callback: Callable[..., Any] | None = None
    staged_key: object | None = None
```

```python
@dataclass(slots=True)
class SlotExprSlotContextData(SlotContextDataBase):
    call_sites: dict[Hashable, CallSiteContext] = field(default_factory=dict)
    staged_call_site_ids: tuple[Hashable, ...] = ()
    post_commit_callbacks: tuple[Callable[[], None], ...] = ()
```

```python
@dataclass(slots=True)
class SlotCallSlotContextData(SlotContextDataBase):
    function_identity: Any = None
    schema: tuple[int, tuple[str, ...]] = (0, ())
    last_args: tuple[Any, ...] = ()
    last_kwargs: tuple[tuple[str, Any], ...] = ()
```

```python
@dataclass(slots=True)
class DirectiveSlotContextData(SlotCallSlotContextData):
    committed_selectors: tuple[SlotSelector, ...] = ()
```

```python
@dataclass(slots=True)
class AppContextOverrideSlotContextData(SlotContextDataBase):
    declared_keys: tuple[AppContextKey[Any], ...] = ()
    committed_values: tuple[Any, ...] = ()
    committed_lookup: AppContextLookup = EMPTY_APP_CONTEXT_LOOKUP
    pending_values: tuple[Any, ...] = ()
    pending_lookup: AppContextLookup = EMPTY_APP_CONTEXT_LOOKUP
    pending_initialized: bool = False
```

```python
@dataclass(slots=True)
class ContainerSlotContextData(SlotContextDataBase):
    expects_native_root: bool = False
    committed_native_root: bool = False
```

```python
@dataclass(slots=True)
class ComponentCallSlotContextData(SlotContextDataBase):
    component_identity: Any = None
    schema: tuple[int, tuple[str, ...]] = (0, ())
    last_runtime_func: Callable[..., Any] | None = None
    last_bound_receiver: object = _BOUND_METHOD_SELF_MISSING
    last_args: tuple[Any, ...] = ()
    last_kwargs: dict[str, Any] = field(default_factory=dict)
    last_plain_args: tuple[Any, ...] = ()
    last_plain_kwargs: dict[str, Any] = field(default_factory=dict)
    last_dirty_state: DirtyStateContext | None = None
    pending_dirty_state: DirtyStateContext | None = None
    uses_dirty_state_api: bool = False
    packed_kwargs: bool = False
    packed_kwarg_param_names: tuple[str, ...] = ()
    param_names: tuple[str, ...] = ()
```

```python
@dataclass(slots=True)
class LeafSlotContextData(SlotContextDataBase):
    last_args: tuple[Any, ...] = ()
    last_kwargs: tuple[tuple[str, Any], ...] = ()
```

The point of these variants is to make the slot-class differences precise:

- every slot gets one lifecycle-managed data shape
- each shape carries only the fields that are actually committed/rolled back
- bindings live in the same place for all of them
- slot-specific state remains explicit instead of being hand-waved into one
  giant generic object

### Result

All slot owners follow the same shape:

- committed data is frozen
- begin pass creates or refreshes a staged unfrozen copy
- mutate only staged data during the pass
- commit freezes staged data and promotes it
- rollback by discarding staged data
- deactivate by closing both committed and staged resources

This is the base normalization step. Without it, the later binding work stays
fragmented.

## 2. Call-site binding and refcount management

### Goal

Preserve the current good property of call-site contexts:

- immutable contexts
- shared bindings
- commit/rollback behavior that does not leak staged state

### Design

`CallSiteContext` already works differently from mutable slot contexts:

- it is immutable
- replacing it creates a new context object
- bindings can temporarily be shared across context copies

That is why call-site bindings need refcounted ownership.

This part formalizes that into one explicit binding model:

```python
class SlotBindingBase(ABC):
    def accepted(self) -> None: ...
    def close(self, replaced_by: SlotBindingBase | None = None) -> None: ...
```

For call-site contexts:

- staged bindings are not yet accepted
- commit calls `accepted()` on newly committed bindings
- rollback closes staged-only bindings
- replacement closes the old binding with `replaced_by=new`
- removal closes the old binding with `replaced_by=None`

### Result

Call-site lifecycle becomes explicit and testable:

- commit
- rollback
- replacement
- removal

This is the place where refcounting belongs.

The normalized call-site form should mirror the same pattern:

```python
@dataclass(slots=True)
class CallSiteContextData(SlotContextDataBase):
    function_identity: Any
    last_args: CallSiteArgs
    invoke_state: CallSiteInvokeState
```

and `CallSiteContext` becomes the immutable owner of one `CallSiteContextData`
instance instead of several separate lifecycle-managed fields.

## 3. Promote `RuntimeSiteMetadata` into bindings

### Goal

Make metadata lifecycle follow the same machinery as other retained resources.

### Design

`RuntimeSiteMetadata` is currently returned by:

```python
def site_metadata(self, *, slot_path: SlotIdPath) -> tuple[RuntimeSiteMetadata[Any], ...]
```

The runtime should treat that as proposed binding input, not as already-live
state.

Per site, metadata is canonicalized into a map by key:

```python
dict[Hashable, RuntimeSiteMetadata[Any]]
```

Then runtime materializes metadata bindings from that map and manages them
through the same staged/committed lifecycle as other bindings.

That gives the right semantics:

- new key on commit -> accepted
- same key, same binding -> retained
- same key, new binding -> old closed with replacement, new accepted
- staged then rolled back -> closed without acceptance
- removed site -> closed with no replacement

### Result

`RuntimeSiteMetadata` stops being passive capture-only data and becomes part of
the same lifecycle model as the rest of the retained runtime state.

## Why this order

This order matters.

1. Normalize slot lifecycle state first.
2. Formalize call-site binding lifecycle second.
3. Move metadata into that binding model third.

If we start with metadata bindings first, we will keep rebuilding the same
commit/rollback rules in several places.

If we normalize the state model first, the rest becomes a small number of
mechanical transitions.

## Verification target

The point of this design is not abstraction for its own sake.

The point is:

- lifecycle behavior becomes unified
- lifecycle behavior becomes mechanically verifiable
- correctness can be tested at the mechanism level

That means fewer tests that say:

- “field X on slot class A rolled back correctly”
- “field Y on slot class B closed correctly”

and more tests that say:

- staged data is not accepted
- committed data is accepted exactly once
- replacement closes the old resource correctly
- rollback closes staged-only resources
- deactivation closes committed resources

That is the value of the unification.
