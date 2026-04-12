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

## Scope

This document defines lifecycle semantics for:

- `initvar(...)`
- `InitVarSpec`
- `FieldSpec.init`
- `InitVarSpec.init`
- generalized explicit initvar-name injection
- dead-initvar / transitive-liveness rules
- private retained initvar storage for late consumers
- dataclass-aligned mutable `default=` validation for instance fields

`classvar` is implemented on a **parallel metadata path** (see
[`classvar` (parallel path)](#classvar-parallel-path--not-fieldspec--not-state-ftables));
it is not part of the instance `FieldSpec` pipeline.

## Stdlib `InitVar` and `ClassVar` (typing)

`@managed_context` **does not** use the stdlib/dataclass meaning of:

- **`typing.InitVar`** / **`dataclasses.InitVar`** — lifecycle **does not** use
  them for managed-context semantics. They must be **ignored** during class
  body scan (no error): treat like an exempt annotation, not a missing
  `lifecycle_field(...)`.

- **`typing.ClassVar[...]`** — lifecycle **ignores** it for **instance** field
  collection (no error when the default value is a `classvar(...)` marker or
  plain class attribute; `classvar` itself is defined below as a separate
  semantic path).

**Required collector redesign:** Today `_collect_own_field_specs` raises if an
annotated name is not a `LifecycleField` (unless `_`-prefixed). Initvars require
recognizing **`initvar(...)`** markers and **skipping** stdlib **`InitVar` /
`ClassVar` annotations** without treating them as lifecycle fields. That is a
**first-class change** to collection, not a small extension.

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
| Constructor kw | when `init=True` | when `init=True` |
| Consumed by factories / hooks | via injection | via injection (direct names only) |

**Fields on `InitVarSpec` (proposed):**

- `name: str` — attribute name on the managed context class
- `annotation: Any` — resolved type hint (same spirit as `FieldSpec.annotation`)
- `init: bool = True` — whether this initvar is accepted as a constructor kw
- `default: Any` — optional; mutually exclusive with `default_factory` where the same `MISSING` conventions apply
- `default_factory: Callable[..., Any] | object` — optional; see contract below

### `InitVarSpec.default_factory` contract

Runs during **constructor / setup before `_state` exists** (see [Constructor Behavior](#constructor-behavior)), so **`self`**, **`current`**, and **`working`**
are **not** available and **must not** appear in the signature.

**Allowed parameter names (named-only; same spirit as `_compile_injected_runner`):**

- **Earlier initvars** — parameters whose names match initvars **already
  resolved** in **merged declaration order** (see [Field order](#field-order-and-mro-merge)).
- Optionally **`cls`** — the managed context **class** (same reserved name used
  by `classvar` factories).

**Ordering:** Resolve initvar values in merged order; each `default_factory` may
only depend on initvars **earlier** in that order. **Cycle detection:** if
statically detectable, **fail at class decoration time**; otherwise fail at
construction with an error in the same style as existing factory-cycle reporting.

**Not allowed:** `self`, `current`, `working`, `previous`, `tx_group`, bare
`*args` / `**kwargs` as the sole way to receive lifecycle-provided values.

**Collection and validation:**

- `@managed_context` collects `InitVarSpec` entries into **`__initvar_specs__`**
  (or equivalent), **merged across the MRO** with the same **first-appearance key
  order** as merged `FieldSpec` dicts (see [Field order](#field-order-and-mro-merge)).
- duplicate names between initvars and lifecycle fields are rejected
- names in `LIFECYCLE_RESERVED_FIELD_NAMES` are rejected for initvars as well as fields
- static **requestor** scan (decoration time): see [Requestor scan](#requestor-scan-decorator-time); **declared initvars with no requestors fail at decoration time** (see [Dead declarations are errors](#dead-declarations-are-errors))

The public `initvar()` helper returns a **namespace descriptor** in the same
spirit as `LifecycleField`: it implements **`__set_name__`**, binds the attribute
name, and holds (or materializes) an **`InitVarSpec`** that `@managed_context`
collects from the class body. **v1 uses this single mechanism** — no parallel
sentinel-based recognition path.

**Why not a subclass of `LCKind`:** initvars are not stored, not transactional, and must never be installed into field ftables. Keeping a dedicated type avoids overloading `FieldSpec.kind` or stretching `LCKind` to cover non-fields.

## Field order and MRO merge

Aligned with current `managed_context` behavior (`_merge_field_specs_from_mro`):

- Iterate **`reversed(cls.__mro__)`** (bases before subclass in the walk).
- **First time** a field or initvar **name** appears, it gets a stable position in
  the merged dict; **same-name override** updates the spec **without moving** the
  key’s iteration slot.
- **Net effect:** merged **`__field_specs__`** / **`__initvar_specs__`** iteration
  order is **base declarations first** (each class in body order), then **new
  names** from subclasses; overrides replace values but **not** order.

For **initvar `default_factory`**, use this merged order as the **dependency
order**; tie-break or secondary ordering is only needed if explicit topological
sort is added later.

## `classvar` (parallel path — **not** `FieldSpec` / **not** state ftables)

**Implemented:** `classvar(...)` / `ClassVarField` / `ClassVarSpec` live outside the
instance field pipeline:

- Collected as **`__managed_own_classvar_specs__`**, merged to **`__classvar_specs__`**
  on the managed class, and materialized as **plain class attributes** on the
  wrapped type at decoration time.
- **Never** wrapped in `FieldSpec`, **never** passed to `_build_class_tables`,
  **never** listed in `LifecycleContextState.__field_specs__` or instance
  getter/setter ftables.

**Semantics:**

- `default` / `default_factory` materialize at **class decoration** time.
- **`default_factory`** injection: **`cls` only** (or zero-arg), same
  named-parameter-only rule as other lifecycle callables.
- **Mutable `default`** (`list` / `dict` / `set`) **allowed** on classvar;
  **`_reject_mutable_instance_default`** applies only to **`FieldSpec`** rows.
- **Instance access:** Attributes live on the managed class object; instances
  resolve them via normal Python class attribute lookup unless shadowed.

**Distinction from `static`:** `static` is per-instance lifecycle state;
**`classvar`** is per-class data outside the state record.

## Mutable `default` on instance field kinds (dataclass-aligned)

**Problem:** Allowing `default=[]` (or `{}` / `set()`) on **per-instance** lifecycle
fields causes shared mutable state across instances — the same bug dataclasses
guards against.

**Rule:** For every `FieldSpec` whose kind is an **instance** field kind, when
`spec.default is not MISSING`, apply the **same rule as CPython `dataclasses`**
for ordinary (`_FIELD`) fields:

- If `isinstance(spec.default, (list, dict, set))`, raise **`ValueError`** with
  a message parallel to:
  `mutable default <type> for field <name> is not allowed: use default_factory`

**Scope:**

- Applies to the **`default=`** parameter value only — **not** to objects
  **returned** from `default_factory` (those are intentionally fresh per call).
- Applies to **const** as well as other instance kinds: the concern is shared
  mutable **defaults**, not whether the committed value is later mutated by user
  code.
- **Callable** defaults (e.g. hook callables) are not `list`/`dict`/`set` as
  types — unchanged.

**Exemption:** **`classvar`** metadata **skips** this check (mutable class-level
defaults allowed). The check applies only to collected **`FieldSpec`** rows.

**Merge / inheritance:** After `_merge_field_specs` produces the effective spec,
**re-run** this validation so a derived class cannot override with a mutable
`default` without using `default_factory`.

**Implementation:** Implement a small helper (e.g.
`_reject_mutable_instance_default(spec: FieldSpec) -> None`) invoked from
`validate_field_spec` (or one choke point). **Do not** import private
`dataclasses` internals; **mirror** the condition and message from the **minimum
CPython version** pyrolyze supports (re-check current `dataclasses.py` when
bumping that floor — e.g. whether `bytearray` or other types are included).

**Recommendation:** For shared class-level mutables, use **`classvar`**; avoid
mutable shared `default=` on instance **`FieldSpec`** rows.

## Initvar retention (single rule)

**Problem:** `const` `default_factory` runs while building state (initvars in
hand). **`static`** `default_factory` can run on **first read**, after `__init__`.

**Rule:** If **any** lifecycle runner that can run **after** the constructor
finishes (e.g. lazy **`static`**, **`working_default_factory`**, or any other
non-eager path) **requests** an initvar name, lifecycle **retains** a
**private** frozen snapshot for the **lifetime** of the context instance.
Otherwise initvar values need only survive through eager initialization (steps
before / while resolving non-late field defaults).

User-facing access remains **injection only**; the snapshot is not a public
attribute.

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
- may be retained in private lifecycle-only storage when requested by late runners

Constructor-only parameters are expressed only via **`initvar(...)`**, not via
stdlib `InitVar` annotations (which lifecycle ignores).

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

If any late consumer requests initvar values by explicit name, lifecycle
retains them in private lifecycle-only storage.

That retained storage:

- is private / non-public
- is frozen / immutable where retained
- is not a lifecycle field
- is not assignable
- is not exposed as an aggregate API object

If no late consumer requests initvar values, no retained storage is created.

### Dead declarations are errors

If a class declares initvars and nothing requests them, **fail at class
decoration time** (static requestor scan), not on first instance construction.

Reason:

- declared initvars should represent real initialization dependencies
- silent dead initvars are design mistakes
- decoration-time failure matches other lifecycle class-setup errors

**Liveness rule:**

- **Initvar-to-initvar references do not count as requestors by themselves.**
  They matter for construction ordering and dependency validation, not for
  proving that an initvar is semantically used.
- An initvar is **live** when it is requested by at least one **non-initvar
  lifecycle consumer** (for example a field `default_factory`,
  `working_default_factory`, hook, or `commit_validator`), either:
  - **directly** by name, or
  - **transitively** because it is required by another initvar whose value is
    ultimately requested by such a consumer.
- A chain of initvars that only reference each other, with no downstream
  non-initvar lifecycle consumer, is still **dead** and must fail decoration.

## Proposed API

### Declaration helper

```python
def initvar(*, init=True, default=MISSING, default_factory=MISSING) -> Any: ...
```

Rules:

- not a lifecycle field kind
- constructor metadata only
- supports `init`
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
    "cls",
    "current",
    "working",
    "previous",
    "tx_group",
)
```

This tuple should be used to reject:

- lifecycle field names
- initvar names

(`cls` is reserved as an **injection** parameter name for **initvar**
`default_factory` and future **`classvar` `default_factory`**; **declared**
field and initvar **names** must not collide with this tuple.)

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

### `FieldSpec.init` and `InitVarSpec.init`

Both `FieldSpec` and `InitVarSpec` need:

```python
init: bool = True
```

Meaning:

- `init=True`: the generated managed-context constructor accepts this lifecycle
  field or initvar as a keyword-only parameter
- `init=False`: the field or initvar is not accepted as a constructor parameter
  and must come from declaration-time defaults or other initialization logic

Rules:

- all lifecycle field constructor parameters are keyword-only
- no lifecycle field constructor parameters are positional
- initvars are also keyword-only
- `initvar(init=False, default_factory=...)` is in scope and acts like a
  constructor-time local declaration: it can participate in initvar dependency
  resolution and later factory injection semantics, but it is not a legal user
  constructor kw

**Default `init` per kind (v1 proposal):**

| Kind | Default `init` |
| --- | --- |
| `managed`, `const`, `static`, `binding`, `owned`, `transient`, `local_store`, `derived` | `True` |
| `commit_order_key` | `True` (per-instance ordering key is constructor-driven) |
| `commit_validator` | `False` |
| `on_before_commit`, `on_after_commit`, `on_after_rollback` | `False` |

**Merge / inheritance (v1 — locked policy):**

- **`init` is not independently overridable.** For a given field name, every
  `FieldSpec` contribution along the MRO that sets `init` **must agree** on the
  value. **Decoration fails** on mismatch (same spirit as forbidding incompatible
  `kind` / `compare` / `tx_group` changes).
- If a subclass redeclares the name only to adjust other attributes, it may
  **omit** `init` to inherit the merged value from bases, or **repeat** the same
  value explicitly. **Specifying a different `init` than the merged parent value
  fails decoration.**

The same agreement rule applies to merged initvars:

- `_merge_initvar_specs` / initvar override validation must enforce that
  `InitVarSpec.init` contributions along the MRO either agree or omit `init` to
  inherit the merged value; a mismatched explicit `init` fails decoration.

`_merge_field_specs` must enforce **`init`** compatibility with the same clarity as
existing `default` / `compare` / `tx_group` checks.

### Example

```python
@managed_context
class ContextBaseStateMgr(StateMgrBase):
    render_context_state_mgr: Any | None = initvar(default=None)
    render_context: Any | None = initvar(default=None)

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

## Retained Initvar Storage

When needed, lifecycle stores retained initvar values in a **private**
lifecycle-only structure on the instance state. This storage is an
implementation detail, not a public class or parameter surface.

### Normalization for retention (no `pyrolyze.freezable` dependency)

The restarted lifecycle core does **not** depend on **`pyrolyze.freezable`**
(`lifecycle.py` module doc). Retained initvars must still be **immutable** where
required.

**Protocol rule (duck typing):**

- When storing a value in the retained initvar snapshot, if the value has a
  callable **`to_frozen()`**, call it and store the **return value**.
- Otherwise store the value **as-is**.
- If `to_frozen()` raises, **abort construction** without leaving a partially
  built retained-initvar structure.

This preserves decoupling while allowing opt-in freezing for types that implement
the method.

### Visibility

Retained initvar storage is not an ordinary attribute set by user code. It is
lifecycle initialization context exposed only through supported injection points.

It is not:

- `self.current`
- `self.working`
- a lifecycle field

## Constructor Behavior

The generated constructor for `@managed_context` accepts:

- lifecycle field names where `FieldSpec.init is True`
- declared initvar names where `InitVarSpec.init is True`

Unknown names still fail.

Initialization order should be:

1. collect constructor args
2. separate lifecycle fields from initvars, using `FieldSpec.init` and
   `InitVarSpec.init` to decide which names are legal constructor kwargs
3. apply initvar **`default=`** values and resolve **`default_factory`** in merged
   initvar order (each factory sees only **earlier** initvars + optional **`cls`**)
4. **Retained snapshot only:** if the class was marked at **decoration time** as
   needing private retained initvar storage (requestor scan found any eligible
   late runner that names an initvar), materialize that storage now: for each
   retained initvar, apply the **`to_frozen()`** protocol when storing. If no
   retained storage is needed, do **not** call **`to_frozen()`** for retention
   and drop initvar values after eager initialization finishes.
5. create `_state`
6. attach transaction manager
7. allocate current / working views
8. install explicit lifecycle field values
9. resolve field defaults

## Factory Injection

### Requestor scan (decorator time)

The scan walks every **injection-eligible** user callable on the merged class
that lifecycle validates and invokes with lifecycle-managed arguments, including
at least:

- `default_factory` and `working_default_factory` on **instance** `FieldSpec`s
- **`commit_order_key`** `default_factory` (compiled like other field factories)
- **`commit_validator`** callables
- **`on_before_commit`**, **`on_after_commit`**, **`on_after_rollback`** hook
  callables

If any such callable’s **inspectable signature** names a declared **initvar**,
that counts as a **requestor**. **Bare `*args` / `**kwargs`** without explicit
named parameters for lifecycle injection do **not** count as requesting initvars.

Use the same **named-parameter-only** rules as `_compile_injected_runner` when
classifying parameters.

### `commit_validator`

`commit_validator` participates in the generalized injection model for explicit
initvar-name access.

**v1 policy (locked):**

- A `commit_validator` may request **`self`** and explicit declared initvar
  names.
- A validator that names an initvar counts as an initvar requestor for
  decoration-time validation and retention policy.
- Unsupported parameter names fail at decoration.

### Keyword-only injection: explicit names, no bare `*args` / `**kwargs`

Lifecycle **never** passes injected values positionally or into anonymous
catch-alls. When invoking a user `default_factory`, `working_default_factory`,
hook, validator, or similar eligible callable, the implementation builds a
**keyword call** `name=value` only for **explicit** parameter names that are part
of the supported injection contract (`self`, `current`, `working`, declared
initvar names, etc.).

Rules:

- Every lifecycle-supplied argument is tied to a **declared** parameter name on
  the callee.
- A callable that uses **only** `*args` or **only** `**kwargs` (with no
  explicit named parameters for the values lifecycle should inject) cannot
  receive those injections and is **invalid** for that role (same spirit as
  today’s “named parameters only” check in `_compile_injected_runner`).
- A callable may still declare explicit keyword-only parameters **and** reserve
  additional names for its own use; lifecycle only fills names it knows about.

**Initvar constructor inputs (no separate “omission” addendum):**

- Every **declared** initvar must receive a value from the constructor **or**
  (when `InitVarSpec.init is True`)
  from its **`InitVarSpec.default`** / **`default_factory`** (same `MISSING`
  conventions as fields). If still missing after that, **`TypeError`** at
  instance construction (mirror missing required field kwargs).
- Before **`_state`** exists, **lifecycle factories** (initvar `default_factory`,
  etc.) never see “omitted” initvars: **earlier** initvars in merged order are
  **fully resolved** before **later** factories run.
- After **`_state`** exists, **injected runners** receive only the keyword names
  the callee declares and lifecycle supports; there is **no** second channel for
  “optional initvar omission” beyond normal Python defaults on the user’s callable.

### Supported injected names

Factory runners should support:

- direct initvar names

in addition to existing injected names such as:

- `self`
- `current`
- `working`
- `tx_group` where applicable

**`classvar` `default_factory`** uses **`cls`** only (see
[`classvar` (parallel path)](#classvar-parallel-path--not-fieldspec--not-state-ftables));
it is outside the initvar requestor / retention work described here.

### Important semantic change

Initvars are not strictly initialization-only anymore.

If a non-initialization factory requests:

- a declared initvar name

that is allowed, and it should see the retained immutable values.

This makes initvars behave like immutable constructor context.

### If nothing requests them

If no factory, hook, validator, or other eligible runner requests any initvar
values, lifecycle should not build retained initvar storage.

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
4. Initvar values intended for retention use the **`to_frozen()`** protocol when
   present; no hard dependency on `pyrolyze.freezable`.
5. `__post_init__` is **not** part of the lifecycle managed-context model.
6. Declared initvars with no requestors must fail **at decoration time**.

## Implementation Sketch

### Decorator collection

Extend `@managed_context` processing to collect:

- lifecycle fields (existing `FieldSpec` path)
- initvars (`__initvar_specs__`, **not** `FieldSpec`)

`classvar` uses a **separate** parallel collector and is not part of the
instance `FieldSpec` path described here.

Store initvars separately from merged `__field_specs__`.

Lifecycle fields also retain `FieldSpec.init` so constructor generation can
distinguish:

- fields that may be seeded explicitly
- fields that are declaration-only and must not appear in `__init__`

Initvars retain `InitVarSpec.init` so constructor generation can distinguish:

- initvars that may be provided explicitly
- initvars that are constructor-time local declarations only

Also compute whether any consumer requests direct initvar names.

### Generated constructor

Update `_ManagedContextBase.__init__` to:

- accept initvar values
- accept only lifecycle field values whose `FieldSpec.init` is `True`
- accept only initvar values whose `InitVarSpec.init` is `True`
- apply defaults
- materialize retained private initvar storage only when requested by late runners
- build `_state`
- resolve lifecycle fields as usual

### Factory runners

Replace **fixed** `_SUPPORTED_FACTORY_PARAMS`-only binding with **per-runner
allowed-name sets**: existing builtins per hook/factory kind **plus** all
declared **initvar** names where applicable. Compile and
validate at class decoration time; runtime uses the same keyword-only call
shape as today.

### Validation

Reject:

- unsupported helper options on `initvar`
- duplicate names between initvars and lifecycle fields
- names in `LIFECYCLE_RESERVED_FIELD_NAMES`
- declared initvars with no consumers
- constructor kwargs for lifecycle fields with `init=False`
- **mutable `default`** on instance field kinds: `list` / `dict` / `set` (dataclass
  rule); `classvar` metadata is exempt on its separate path
- re-validate merged specs after inheritance merge for mutable `default`

### Mutable-default helper

Call `_reject_mutable_instance_default` (or equivalent) from the central field-spec
validator for all **`FieldSpec`** rows. `classvar` metadata uses its own
parallel validation path.

## Testing

Add tests for:

1. `initvar` default and explicit value handling
2. `const(default_factory=...)` reading direct initvar names
3. late factories can read retained initvars by explicit name
4. retained private initvar storage uses **`to_frozen()`** when present; failure leaves no partial snapshot
5. declared initvars with no requestors fail clearly
6. names in `LIFECYCLE_RESERVED_FIELD_NAMES` fail clearly
7. initvar names conflicting with real fields fail clearly
8. non-initialization factories can request retained initvars
9. **`commit_validator`** can request explicit initvar names and is counted as
    an initvar requestor
10. lifecycle fields with `init=False` are rejected from constructor kwargs
11. initvars with `init=False` are rejected from constructor kwargs but remain
    usable through initvar dependency resolution
12. lifecycle fields with `init=True` are accepted only as keyword arguments
13. subclass redeclaration with mismatched `init` vs merged parent fails at
    decoration
14. `managed(default=[])` (and `dict` / `set`) raises
15. merged derived spec cannot introduce mutable `default` without
    `default_factory`
16. **`classvar`** mutable `default` and `default_factory(cls=...)` on the parallel path

## Short Version

**v1** delivers:

- `initvar(...)` / `InitVarSpec` with explicit **`default_factory`** contract
  (earlier initvars + optional **`cls`** only; before `_state`)
- merged **`__initvar_specs__`**; **dead initvars** fail at **decoration** time
- **Requestor scan** over factories, **`working_default_factory`**, **`commit_order_key`**
  factories, **`commit_validator`**, and commit hooks
- **Per-runner** allowed injection names; **keyword-only** lifecycle calls
- **`FieldSpec.init`** with per-kind defaults and explicit **merge** rules
- **Mutable-`default` ban** for all **`FieldSpec`** instance fields (dataclass
  rule)
- **Retention:** private snapshot when **any late runner** requests explicit
  initvar names; **`to_frozen()`** protocol for normalization (**no**
  `freezable` import)
- **Collector** redesign: skip stdlib **`InitVar` / `ClassVar`** without error;
  recognize **`initvar`** and **`classvar`**
- **`classvar`**: parallel path (**not** `FieldSpec` / not state ftables); mutable
  `default` allowed there

That removes the need for handwritten constructors while keeping lifecycle
field declarations focused on real state semantics.
