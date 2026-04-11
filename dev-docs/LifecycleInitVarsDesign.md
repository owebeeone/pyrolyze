# Lifecycle InitVars Design

## Purpose

This document proposes `InitVar` support for `pyrolyze.lifecycle`.

Field-kind refactors (Phases 1A and 1B) are specified in [LifecycleGeneratedKindHelpers.md](LifecycleGeneratedKindHelpers.md).

The immediate driver is the `context_state_lcm` adoption work. Some lifecycle
fields are naturally `const`, but their default values depend on constructor
inputs that are not real runtime state. Those values should not force
handwritten constructors on `@managed_context` classes.

The goals are:

- lifecycle kind behavior is described in one place
- `@managed_context` remains in full control of construction
- semantic state stays declared as lifecycle fields
- constructor-only inputs can be expressed declaratively
- immutable initialization context can be retained when requested

## Relationship to `LCKind` (Phases 1A and 1B)

Constructor-only initvars are **not** lifecycle field kinds. They do not use
`FieldSpec.kind`, `lifecycle_field`, or the `LCKind` / `LC_*` surface.

Lifecycle field kinds, Phase 1A integration, Phase 1B generated helpers, and the
archived Phase 1A hierarchy sketch live in
[LifecycleGeneratedKindHelpers.md](LifecycleGeneratedKindHelpers.md).

## `InitVarSpec` (constructor-only metadata type)

Each `initvar(...)` declaration on a `@managed_context` class materializes as a
first-class **`InitVarSpec`** (exact runtime class name TBD), **separate from**
[`FieldSpec`](#fieldspecinit):

| Concern | `FieldSpec` | `InitVarSpec` |
| --- | --- | --- |
| Lifecycle kind | `kind: type[LCKind]` | none (not an `LCKind`) |
| Stored in `current` / `working` | yes | no |
| `compare`, `tx_group`, `freeze` / `thaw`, … | per kind | not applicable |
| Constructor kw | when `init=True` | always (initvars *are* constructor parameters) |
| Consumed by factories / hooks | via injection | via injection (direct names + `initvars`) |

**Fields on `InitVarSpec` (proposed):**

- `name: str` — attribute name on the managed context class
- `annotation: Any` — resolved type hint (same spirit as `FieldSpec.annotation`)
- `default: Any` — optional; mutually exclusive with `default_factory` where the same `MISSING` conventions apply
- `default_factory: Callable[..., Any] | object` — optional; if present, used only at construction time (not Nuovo lifecycle factory injection unless we explicitly extend initvar factories later)

**Collection and validation:**

- `@managed_context` collects `InitVarSpec` entries in a dedicated structure (for example `__initvar_specs__: dict[str, InitVarSpec]`) parallel to `__field_specs__`
- duplicate names between initvars and lifecycle fields are rejected
- names in `LIFECYCLE_RESERVED_FIELD_NAMES` are rejected for initvars as well as fields
- static pass determines whether any factory or hook requests each initvar or `initvars`; declared initvars with no requestors fail (see [Dead declarations are errors](#dead-declarations-are-errors))

The public `initvar()` helper returns a value the decorator recognizes (for example a sentinel or a pre-built `InitVarSpec` after name binding), analogous to how field helpers feed `lifecycle_field`.

**Why not a subclass of `LCKind`:** initvars are not stored, not transactional, and must never be installed into field ftables. Keeping a dedicated type avoids overloading `FieldSpec.kind` or stretching `LCKind` to cover non-fields.


## Problem

We need all of the following:

1. managed contexts must not define their own `__init__`
2. some field defaults depend on constructor-only inputs
3. some constructor inputs may still be useful after construction, but only as
   immutable context, not as lifecycle-managed state

Current workarounds such as:

- custom constructors
- `*_seed` fields
- constructor plumbing that forwards semantic values directly

all obscure the field model and violate the adoption rules.

## Proposed Feature

Add `initvar(...)` declarations to `@managed_context`.

These are constructor parameters that:

- are accepted by the generated lifecycle constructor
- may be consumed by field factories
- are not lifecycle fields
- may be retained in an immutable `initvars` object when requested

This starts from the intent of `dataclasses.InitVar`, but it is not identical.
Here, initvars may survive construction as immutable initialization context.

## Core Semantics

### What an initvar is

An initvar is:

- constructor input metadata
- not part of `current`
- not part of `working`
- not committed or rolled back
- not part of lifecycle snapshots

### What survives

If any consumer requests initvars, lifecycle materializes a retained immutable
`initvars` object.

That object:

- is frozen / immutable
- is not a lifecycle field
- is not assignable
- is available to factory injection
- may also be available to non-initialization factories if they explicitly
  request it

If no consumer requests initvars, the `initvars` object is not created.

### Dead declarations are errors

If a class declares initvars and nothing requests them, construction setup is
invalid and lifecycle should raise.

Reason:

- declared initvars should represent real initialization dependencies
- silent dead initvars are design mistakes

So:

- initvars declared
- no factory or hook requests them
- raise during class setup or first construction

## Proposed API

### Declaration helper

```python
def initvar(*, default=MISSING, default_factory=MISSING) -> Any: ...
```

Rules:

- not a lifecycle field kind
- constructor metadata only
- supports `default`
- supports `default_factory`
- does not support `tx_group`
- does not support `compare`
- does not support `freeze` / `thaw`
- does not support `working_default_factory`

### Reserved user-defined names

Lifecycle should export a single reserved-name tuple:

```python
LIFECYCLE_RESERVED_FIELD_NAMES: tuple[str, ...] = (
    "self",
    "current",
    "working",
    "previous",
    "tx_group",
    "initvars",
)
```

This tuple should be used to reject:

- lifecycle field names
- initvar names

Reason:

- these names are part of the injection namespace
- allowing users to declare them would create ambiguous or unstable factory
  behavior
- reserving them now avoids later source-breaking collisions

Separate policy:

- names beginning with `_` should be governed by a separate validation rule if
  desired
- `_`-prefix rejection is a namespace/style rule, not part of the semantic
  reserved injected-name set

### `FieldSpec.init`

`FieldSpec` also needs:

```python
init: bool = True
```

Meaning:

- `init=True`: the generated managed-context constructor accepts this lifecycle
  field as a keyword-only parameter
- `init=False`: the field is not accepted as a constructor parameter and must
  come from declaration-time defaults or other initialization logic

Rules:

- all lifecycle field constructor parameters are keyword-only
- no lifecycle field constructor parameters are positional
- initvars are also keyword-only

### Example

```python
@managed_context
class ContextBaseStateMgr(StateMgrBase):
    render_context_state_mgr: InitVar[Any | None] = initvar(default=None)
    render_context: InitVar[Any | None] = initvar(default=None)

    _render_context_state_mgr: Any | None = const(
        default_factory=lambda self, render_context_state_mgr, render_context: (
            render_context_state_mgr
            if render_context_state_mgr is not None
            else (
                render_context._state_mgr
                if render_context is not None and hasattr(render_context, "_state_mgr")
                else None
            )
        )
    )
```

The semantic field is `_render_context_state_mgr`.
The initvars are constructor context, not runtime state.

## Retained `initvars` Object

### Shape

When needed, lifecycle builds a frozen dataclass object named:

- `initvars`

Its fields are the declared initvars.

### Freezable normalization

If the caller passes a mutable `freezable_dataclass` instance as an initvar,
lifecycle freezes it before storing it in `initvars`.

Rule:

- freezable mutable input -> frozen paired value in `initvars`

This gives retained initvars stable immutable semantics.

### Visibility

`initvars` is not an ordinary attribute set by user code. It is lifecycle
initialization context exposed only through supported injection points.

It is not:

- `self.current`
- `self.working`
- a lifecycle field

## Constructor Behavior

The generated constructor for `@managed_context` accepts:

- lifecycle field names where `FieldSpec.init is True`
- declared initvar names

Unknown names still fail.

Initialization order should be:

1. collect constructor args
2. separate lifecycle fields from initvars, using `FieldSpec.init` to decide
   which lifecycle fields are legal constructor kwargs
3. apply initvar defaults
4. normalize initvar values, including freezable -> frozen
5. decide whether `initvars` must be materialized
6. create `_state`
7. attach transaction manager
8. allocate current / working views
9. install explicit lifecycle field values
10. resolve field defaults

## Factory Injection

### Supported injected names

Factory runners should support:

- direct initvar names
- `initvars`

in addition to existing injected names such as:

- `self`
- `current`
- `working`
- `tx_group` where applicable

### Important semantic change

Initvars are not strictly initialization-only anymore.

If a non-initialization factory requests:

- a declared initvar name
- or `initvars`

that is allowed, and it should see the retained immutable values.

This makes initvars behave like immutable constructor context.

### If nothing requests them

If no factory or hook requests any initvar values, lifecycle should not build
the `initvars` object.

If initvars were declared anyway, raise.

## Why This Is Better Than Seed Fields

Seed fields are misleading because they:

- look like semantic state
- pollute the lifecycle field table
- blur the line between constructor context and runtime state

Initvars keep the distinction clean:

- real semantic values are lifecycle fields
- constructor context is not

## Relationship to `const`

This feature is especially useful with `const`.

Typical pattern:

- initvar carries optional constructor input
- `const(default_factory=...)` computes the canonical retained value
- result becomes true lifecycle state

That is the correct replacement for handwritten constructor plumbing.

It is also acceptable for other factories to request retained initvars when
they semantically need immutable constructor context.

## Constraints

1. Managed contexts must not define their own `__init__`.
2. Initvars must not appear in lifecycle field tables.
3. Retained initvars must be immutable.
4. Freezable mutable initvar values must be frozen before storage.
5. `__post_init__` must run only after `_state` and the transaction manager exist.
6. Declared initvars with no requestors must fail.

## Implementation Sketch

### Decorator collection

Extend `@managed_context` processing to collect:

- lifecycle fields
- initvars

Store them separately.

Lifecycle fields also retain `FieldSpec.init` so constructor generation can
distinguish:

- fields that may be seeded explicitly
- fields that are declaration-only and must not appear in `__init__`

Also compute whether any consumer requests:

- direct initvar names
- `initvars`

### Generated constructor

Update `_ManagedContextBase.__init__` to:

- accept initvar values
- accept only lifecycle field values whose `FieldSpec.init` is `True`
- apply defaults
- normalize freezable mutable inputs to frozen values
- materialize a frozen `initvars` object only when requested
- build `_state`
- resolve lifecycle fields as usual

### Factory runners

Extend factory-runner compilation so runners may bind:

- declared initvar names
- `initvars`

This should be static, like the existing runner machinery.

### Validation

Reject:

- unsupported helper options on `initvar`
- duplicate names between initvars and lifecycle fields
- names in `LIFECYCLE_RESERVED_FIELD_NAMES`
- declared initvars with no consumers
- constructor kwargs for lifecycle fields with `init=False`

## Testing

Add tests for:

1. `initvar` default and explicit value handling
2. `const(default_factory=...)` reading direct initvar names
3. `const(default_factory=...)` reading `initvars`
4. retained `initvars` object is frozen
5. mutable freezable initvar inputs are frozen before storage
6. declared initvars with no requestors fail clearly
7. names in `LIFECYCLE_RESERVED_FIELD_NAMES` fail clearly
8. initvar names conflicting with real fields fail clearly
9. non-initialization factories can request retained initvars
10. lifecycle fields with `init=False` are rejected from constructor kwargs
11. lifecycle fields with `init=True` are accepted only as keyword arguments

## Short Version

The feature is:

- declare `initvar(...)`
- allow factories to request initvars by name or via `initvars`
- retain initvars only as immutable constructor context
- freeze freezable mutable initvar inputs before retention
- fail if initvars are declared but never requested
- add `FieldSpec.init` so lifecycle controls which real fields are exposed as
  keyword-only constructor parameters

That removes the need for handwritten constructors while keeping lifecycle
field declarations focused on real state semantics.
