# Lifecycle InitVars Implementation Plan

## Preface: semantic dispatch rule

This plan follows one non-negotiable implementation rule:

- **Never implement behavior by asking `kind == LC_XXX` / `kind is SomeKind` / `issubclass(kind, SomeConcreteKind)` to decide semantics.**
- **Never add identity-style helpers such as `kind.am_i_an_initvar_kind()`.**
- **Always ask the semantic question directly and make the answer a property of the abstraction that owns that question.**

Examples:

- “Can this field appear in the generated constructor?” is a **field / kind semantic** and should be answered by a stable field property such as `FieldSpec.init` together with `LCKind.validate_field_spec()` / override rules.
- “Can this initvar appear in the generated constructor?” is an **initvar declaration semantic** and should be answered by `InitVarSpec.init`, not by identity-style declaration checks.
- “Does this callable accept explicit initvar-name injection?” is a **runner semantic** and should be answered by a runner policy / allowed-name builder, not by checking concrete kinds ad hoc.
- “Does this declaration create an instance field table entry?” is a **declaration-category semantic**. `initvar` is not a field kind at all, so it must live outside the `LCKind` / `FieldSpec` field pipeline.
- “Does this declaration retain instance state?” is answered by storage / state construction logic, not by comparing against a list of concrete kinds.

The current lifecycle restart is already mostly aligned with this style:

- `LCKind.validate_field_spec()` and `LCKind.validate_override()` centralize field semantics.
- helper parameter exposure is driven by `helper_params`, not ad hoc conditionals
- table installation is delegated through `spec.kind.install_field_tables(...)`

This plan preserves that direction.

## Scope

This plan implements the v1 design in [LifecycleInitVarsDesign.md](LifecycleInitVarsDesign.md):

- `initvar(...)`
- `InitVarSpec`
- `FieldSpec.init`
- `InitVarSpec.init`
- generalized explicit initvar-name injection
- requestor scan and dead-initvar validation
- private retained initvar storage for late consumers
- dataclass-aligned mutable `default=` rejection for instance fields

Phase **4** (`classvar`) is implemented on the same parallel-metadata path
described below; see **Rollout status**.

## Phase-boundary alignment with the design doc

This plan is aligned with [LifecycleInitVarsDesign.md](LifecycleInitVarsDesign.md)
and uses the same intended phase boundaries:

- **3A**: runner-policy and explicit-name injection groundwork
- **3B**: initvar declaration, collection, merge, constructor split, and
  dead-initvar / transitive-liveness semantics
- **3C**: retained private storage, `to_frozen()` normalization, `FieldSpec.init`,
  and mutable-default validation
- **3D**: semantic hardening and edge-case coverage
- **4**: `classvar` on its parallel metadata path

If implementation reveals that a phase boundary is wrong, update this plan and
the design doc together rather than silently widening or narrowing a phase.

## Rollout status

Phases **3A–4** are complete in `pyrolyze` `main`. Annotated tags mark phase
boundaries (use `git show <tag>` for the exact commit):

| Phase | Tag | Notes |
| --- | --- | --- |
| 3A | `lifecycle-initvars-3a-done` | Injection / validator plumbing, explicit initvar names |
| 3B + 3C | `lifecycle-initvars-3bc-done` | Initvar pipeline, retention, `FieldSpec.init`, constructor split |
| 3D | `lifecycle-initvars-3d-done` | Extra edge tests (hooks, validator, transient, inheritance, eager vs retained) |
| 4 | `lifecycle-initvars-4-done` | `classvar` collection, MRO merge, class materialization (same commit as 3D) |

There is no separate `lifecycle-initvars-3b-done` / `3c-done`: **3B and 3C**
shipped together as **`lifecycle-initvars-3bc-done`**.

## Current code map

The live implementation lives in `src/pyrolyze/lifecycle.py` and
`tests/test_api_lifecycle.py`. Central pieces include:

- `LCKind` and its validation hooks
- `FieldSpec`, `InitVarSpec`, `ClassVarSpec`
- `LifecycleField`, `InitVarField`, `ClassVarField`, `lifecycle_field`, `initvar`, `classvar`
- `_compile_injected_runner(...)`, `_compile_factory_runner(...)`
- `_collect_own_declarations(...)`, `_collect_own_field_specs(...)`
- `_merge_field_specs(...)`, `_merge_field_specs_from_mro(...)`
- `_merge_initvar_specs(...)`, `_merge_initvar_specs_from_mro(...)`
- `_merge_classvar_specs(...)`, `_merge_classvar_specs_from_mro(...)`
- requestor / liveness helpers and `_materialize_classvars_on_managed_class(...)`
- `LifecycleContextState`, `_ManagedContextBase.__init__(...)`
- `_build_hook_runner_tables(...)`, `_build_class_tables(...)`, `managed_context(...)`

## Design translation into code

### 1. Add constructor-only declaration types outside `LCKind`

Add new declaration metadata and descriptor types near `FieldSpec` / `LifecycleField`:

- `InitVarSpec`
- `InitVarField`
- `initvar(...)`

Public helper shape:

```python
def initvar(*, init: Any = MISSING, default: Any = MISSING, default_factory: Callable[..., Any] | object = MISSING) -> Any: ...
```

(`init` omitted means inherit on override; effective default is `True` for a fresh declaration.)

Spec / descriptor shape:

```python
@dataclass(slots=True)
class InitVarSpec:
    name: str
    annotation: Any
    init: bool = True
    default: Any = MISSING
    default_factory: Callable[..., Any] | object = MISSING
```

```python
class InitVarField:
    __slots__ = ("init", "default", "default_factory", "name")
```

`InitVarField` mirrors `LifecycleField` structurally:

- validates `init`
- validates `default` vs `default_factory`
- captures its name via `__set_name__`
- builds an `InitVarSpec`

This keeps initvars in the same authored style as fields, but **not** in the field-kind pipeline.

### 2. Extend field metadata with constructor semantics

Add `init: bool = True` to `FieldSpec`.

Add `init` to:

- `LifecycleField.__slots__`
- `LifecycleField.__init__(...)`
- `LifecycleField.build_spec(...)`
- `lifecycle_field(...)`

Also add `init` to:

- `_PARAM_PRESETS`
- `_LIFECYCLE_FIELD_NEUTRALS`
- helper generation where appropriate

The constructor question is semantic, so the concrete helper defaults should remain encoded by helper exposure and kind validation, not scattered checks.

### 3. Keep kind-specific decisions inside kind validation

Add the `init` compatibility and mutable-default validation at the same choke points already used for field semantics:

- `LCKind.validate_field_spec(spec)`
- `LCKind.validate_override(base, derived)`

Planned additions:

- `validate_field_spec()` should reject unsupported `init=` on helper surfaces that do not expose it
- `_reject_mutable_instance_default(spec)` should be called from the same central validation path
- `validate_override()` should require `init` compatibility according to the locked rule in the design

Do **not** add scattered checks like:

```python
if spec.kind is CommitValidatorKind:
    ...
```

If a kind has special `init` behavior, that should come from helper defaults and the kind’s own validation semantics.

## New state and metadata surfaces

### 4. Add class-level initvar metadata

`managed_context(...)` currently builds:

- `__managed_own_field_specs__`
- merged `__field_specs__`

Add parallel initvar metadata:

- `__managed_own_initvar_specs__`
- merged `__initvar_specs__`

Add to `LifecycleContextState` class attributes:

- `__initvar_specs__: dict[str, InitVarSpec] = {}`
- `__initvar_names__: tuple[str, ...] = ()`
- runner/requestor metadata described below

Add private runtime storage to `LifecycleContextState.__slots__`:

- resolved eager initvar values during construction
- retained frozen initvar values for late runners

Suggested names:

- `_construction_initvars`
- `_retained_initvars`

These remain private implementation details and are not part of the user API.

### 4B. Add class-level `classvar` metadata for Phase 4 *(implemented)*

`classvar` must remain outside the instance field pipeline.

Add parallel class metadata on the managed class itself:

- `__managed_own_classvar_specs__`
- merged `__classvar_specs__`

Suggested new metadata type:

```python
@dataclass(slots=True)
class ClassVarSpec:
    name: str
    annotation: Any
    default: Any = MISSING
    default_factory: Callable[..., Any] | object = MISSING
```

Suggested declaration helper/descriptors:

- `ClassVarField`
- `classvar(...)`

These must be collected, merged, validated, and materialized without ever
passing through `FieldSpec`, `LCKind.install_field_tables(...)`, or
`LifecycleContextState.__field_specs__`.

## Collector refactor

### 5. Split field collection from initvar collection

Replace `_collect_own_field_specs(...)` with a collector layer that can classify annotations into:

- lifecycle fields
- initvars
- ignored stdlib `InitVar` / `ClassVar`
- invalid annotated declarations

Suggested decomposition:

- `_collect_own_declarations(cls) -> tuple[dict[str, FieldSpec], dict[str, InitVarSpec], dict[str, ClassVarSpec]]`
- `_collect_own_field_specs(...)` retained as a thin wrapper over the field slice

Rules:

- `LifecycleField` instances produce `FieldSpec`
- `InitVarField` instances produce `InitVarSpec`
- stdlib `InitVar[...]` and `ClassVar[...]` are ignored without error
- any other non-underscore annotated declaration still fails as unsupported

This collector must also enforce:

- duplicate names across fields, initvars, and classvars rejected
- names in `LIFECYCLE_RESERVED_FIELD_NAMES` rejected

### 6. Merge initvar metadata across MRO

Reuse `_merge_field_specs_from_mro(...)` structurally, but not by forcing `InitVarSpec` into `FieldSpec`.

Add:

- `_merge_initvar_specs(base, derived) -> InitVarSpec`
- `_merge_initvar_specs_from_mro(...)`

Semantics:

- same first-appearance order as fields
- same-name override keeps position
- derived annotation must be narrower-or-equal
- `default` / `default_factory` replacement semantics mirror fields
- `init` merge uses the same locked agreement rule described in §18

Initvar merge validation must remain about initvar semantics, not field-kind identity.

### 6B. Merge `classvar` metadata across MRO for Phase 4 *(implemented)*

Add:

- `_merge_classvar_specs(base, derived) -> ClassVarSpec`
- `_merge_classvar_specs_from_mro(...)`

Semantics:

- first-appearance order follows the same general MRO merge discipline used for
  fields and initvars
- same-name override replaces default/default_factory while preserving position
- annotation narrowing rules mirror the field/initvar merge rules where
  appropriate

Materialization order during class decoration should follow merged classvar
order.

## Runner plan refactor

### 7. Introduce explicit runner policies

Current injection uses hardcoded frozensets:

- `_SUPPORTED_FACTORY_PARAMS`
- `_BEFORE_COMMIT_PARAMS`
- `_AFTER_COMMIT_PARAMS`
- `_AFTER_ROLLBACK_PARAMS`

This is the right abstraction point, but it now needs to become class-aware and initvar-aware.

Add a small runner-policy layer:

```python
@dataclass(frozen=True, slots=True)
class RunnerPolicy:
    allowed_builtin_params: frozenset[str]
    accepts_initvar_names: bool
    participates_in_requestor_scan: bool
    can_run_after_init: bool
```

Or equivalent helpers that answer the same semantic questions.

Policies are needed for:

- field `default_factory`
- field `working_default_factory`
- `commit_order_key` factory
- commit hooks
- `commit_validator`
- initvar `default_factory`

Important: `initvar.default_factory` is **not** a normal field runner. It needs its own policy:

- before `_state`
- allowed params = earlier initvar names plus optional `cls`
- no `self`, `current`, `working`, `previous`, `tx_group`

### 8. Generalize `_compile_injected_runner(...)`

Keep `_compile_injected_runner(...)` as the main signature validation function, but extend it to work with explicit injected values beyond the current builtins.

Planned changes:

- allow passing a resolved parameter-binding map or resolver callback
- support explicit initvar-name injection
- keep “named parameters only” validation
- keep decoration-time validation behavior

Suggested shape:

```python
def _compile_injected_runner(
    *,
    field_name: str,
    hook_name: str,
    function: Callable[..., Any],
    allowed_params: frozenset[str],
    resolve_param: Callable[[LifecycleContextState, dict[str, Any], str], Any],
) -> InjectedRunner:
    ...
```

Or precompute `parameter_names` plus a richer runtime resolver.

Do not special-case concrete field kinds inside this function. It should answer only:

- what names are allowed
- how to resolve each allowed name

### 9. Add class-aware allowed-name builders

Add helpers that build per-class allowed-name sets from:

- builtin names for that runner type
- merged `__initvar_specs__` names where that runner accepts initvar injection

Suggested helpers:

- `_allowed_params_for_factory(state_cls, spec, hook_name)`
- `_allowed_params_for_hook(state_cls, hook_name)`
- `_allowed_params_for_commit_validator(state_cls)`

Or equivalent policy-driven builders.

These are semantic questions about runner type, not kind identity checks.

## Requestor scan and liveness

### 10. Add decoration-time requestor analysis

Add a class setup pass that inspects eligible callables and determines:

- which explicit initvar names are requested by non-initvar lifecycle consumers
- which initvars are requested only transitively via other initvars
- whether any late runner needs retained storage

Suggested outputs:

- `__class_requested_initvars__ : frozenset[str]`
- `__class_retained_initvars__ : frozenset[str]`
- `__class_has_late_initvar_consumers__ : bool`

Implementation sketch:

1. Build an initvar dependency graph from `InitVarSpec.default_factory` signatures.
2. Build non-initvar consumer edges from field factories, hooks, validator, etc.
3. Compute liveness as “reachable from any non-initvar consumer.”
4. Fail if any declared initvar is not live.
5. Compute retained names as initvars reachable from any **late** consumer.

This directly implements the design’s dead-initvar rule:

- initvar-to-initvar references do not count by themselves
- they do count transitively when needed by a real lifecycle consumer

### 11. Add validator participation

`commit_validator` currently bypasses runner compilation and is invoked as `validator(self)`.

Update this path so validators use the same explicit-name injection model as other runtime callables.

Changes:

- add compiled validator runner storage to `LifecycleContextState`
- change `validate_commit()` / `validate_commit_for()` to invoke the compiled validator runner
- allow `self` plus explicit initvar names

Suggested state-class table:

- `__class_ftable_commit_validator_runner_by_group__: dict[Hashable, InjectedRunner]`

This is a runner semantic, not a kind identity special case.

## Constructor and state flow

### 12. Split constructor input processing

Current flow:

- `_ManagedContextBase.__init__(**values)` passes one dict to `LifecycleContextState`
- `LifecycleContextState.__init__` lets field kinds pop constructor values

New flow:

1. `_ManagedContextBase.__init__(**values)` separates:
   - transaction manager
   - lifecycle field kwargs
   - initvar kwargs
2. resolve initvar values before state construction
3. decide whether retained private storage is needed
4. pass only legal field constructor kwargs into `LifecycleContextState`
5. finish eager default resolution

Suggested decomposition:

- `_split_constructor_values(...)`
- `_resolve_initvar_values(...)`
- `_build_retained_initvar_storage(...)`

This is needed because initvars are not field kinds and therefore must not be consumed by `spec.kind.initialize_constructor_value(...)`.

### 13. Enforce `FieldSpec.init` and `InitVarSpec.init`

Current field constructor acceptance is effectively “all field names are accepted if present.”

Change this by filtering field kwargs before state construction:

- `init=True` field names are legal constructor kwargs
- `init=False` field names raise `TypeError` if provided

Do the same for initvars:

- `init=True` initvar names are legal constructor kwargs
- `init=False` initvar names raise `TypeError` if provided
- `init=False` initvars still participate in initvar dependency resolution and
  may behave like constructor-time locals

Do not implement this by asking whether a declaration “looks like a hook kind”
or local temporary. The legality must come from `FieldSpec.init` /
`InitVarSpec.init`.

### 14. Retained initvar storage

Add private retained storage on `LifecycleContextState` only when required by late consumers.

Planned runtime behavior:

- eager-only initvars live in local constructor resolution state and are discarded
- retained initvars are normalized with `to_frozen()` before storage
- late runner injection resolves explicit initvar names from retained private storage

Suggested helpers:

- `_normalize_retained_initvar_value(value)`
- `_get_retained_initvar(state, name)`

No public `initvars` object, no aggregate injected parameter, no public attribute.

### 14B. Hard 3B ↔ 3C invariant

The rollout must preserve this invariant:

- **No late initvar use may ship as supported behavior until retained private
  storage exists to satisfy it.**

Concretely:

- Phase 3B may classify late consumers and build the dependency/requestor model
- but Phase 3B must not be treated as a complete semantic checkpoint for any
  late-use path (`static`, `working_default_factory`, or any other post-init
  runner) unless Phase 3C retention is also present

This prevents an invalid checkpoint where decoration succeeds and signatures
appear supported, but runtime has no retained initvar data for late injection.

## Field-table and state-class build changes

### 15. Extend `_build_class_tables(...)`

Current `_build_class_tables(...)` only compiles field factories and installs field tables.

Extend it to also:

- compile field runners with per-class allowed-name sets
- compile validator runners
- record whether a runner can consume explicit initvar names

Do not collapse initvar declaration metadata into field tables. Keep the field-table pipeline only for actual fields.

### 16. Extend `_build_hook_runner_tables(...)`

Hook runner compilation must use per-class allowed names:

- builtins appropriate to the hook
- explicit initvar names

The hook tables can remain separate, but the compiler input must now be class-aware.

## Validation additions

### 17. Add mutable-default validation

Add `_reject_mutable_instance_default(spec)` and call it from the central field validation path.

This affects all collected `FieldSpec` rows and must run:

- during immediate `LifecycleField` construction validation
- after merged-field-spec creation in `_merge_field_specs(...)`

### 18. Add initvar-specific validation

Add:

- `_validate_initvar_spec(spec)`
- `_validate_initvar_override(base, derived)`

Validation includes:

- `default` vs `default_factory`
- `init` compatibility across the MRO using the same “must agree or inherit”
  rule as field `init`
- reserved names
- duplicate names vs fields
- signature rules for `InitVarSpec.default_factory`
- dependency order / cycle rules

### 18B. Add `classvar`-specific validation for Phase 4 *(implemented)*

Add:

- `_validate_classvar_spec(spec)`
- `_validate_classvar_override(base, derived)`

Validation includes:

- `default` vs `default_factory`
- reserved names
- prohibition on instance-field-only options
- `default_factory` signature rules: zero-arg or `cls` only
- mutable `default=` explicitly allowed for `classvar`

This validation remains about declaration semantics, not about comparing classvar
against instance kinds.

## Proposed implementation phases

### Phase 3A: runner and validation groundwork

Code changes:

- add runner policy / allowed-name builders
- generalize `_compile_injected_runner(...)`
- compile validator runners
- add requestor scan and liveness analysis scaffolding

Tests:

- explicit initvar-name parameter acceptance/rejection for factories, hooks, validator
- `*args` / `**kwargs` rejection
- validator parameter validation

Exit caveats:

- Do **not** mark Phase 3A complete if it only partially widens accepted
  parameter names without a coherent runner-policy model behind it.
- Do **not** expose partially implemented user-facing initvar behavior from this
  phase. Phase 3A is complete only when the plumbing is internally coherent,
  decoration-time validation is reliable, and focused tests cover acceptance and
  rejection paths.
- If 3A stalls because the runner-policy work and requestor-graph work are too
  tightly coupled, split it into two tagged substeps:
  - injection / validator plumbing
  - requestor / liveness graph
  while preserving the `14B` invariant.

### Phase 3B: initvar declaration and constructor path

Code changes:

- add `InitVarSpec`, `InitVarField`, `initvar(...)`
- add collector split and MRO merge for initvars
- add constructor split and initvar resolution
- add dead-initvar validation using transitive liveness
- add `InitVarSpec.init`

Tests:

- initvar defaults
- initvar default factories depending on earlier initvars
- transitive liveness
- dead isolated initvar chains fail
- `initvar(init=False, default_factory=...)` constructor-time local behavior

Exit caveats:

- Do **not** mark Phase 3B complete unless constructor splitting, initvar
  resolution order, and dead-initvar validation all work together.
- In particular, do **not** tag the phase complete if direct initvar usage works
  but transitive liveness through initvar-to-initvar dependencies is still
  missing or incorrect.
- Do **not** treat late initvar-use paths as complete in 3B. If any such path
  is accepted by signatures or requestor analysis but retention is not yet in
  place, the phase is still incomplete.

### Phase 3C: retained storage, `FieldSpec.init`, mutable defaults

Code changes:

- add retained private storage and `to_frozen()` normalization
- add `FieldSpec.init`
- enforce constructor filtering by `init`
- add mutable-default rejection
- add inheritance validation for `init`

Tests:

- late `static` / `working_default_factory` use retained initvars
- eager-only initvars are not retained
- `init=False` constructor rejection
- mismatched `init` across inheritance fails for both fields and initvars
- mutable `default=` rejection

Exit caveats:

- Do **not** mark Phase 3C complete if retained private storage exists but late
  runner behavior (`static`, `working_default_factory`, validator, hooks) is not
  actually covered by tests.
- Do **not** claim `FieldSpec.init` / `InitVarSpec.init` are done until
  constructor filtering, inheritance compatibility, and helper-surface
  validation all agree for both fields and initvars.

### Phase 3D: edge cases and semantic hardening

Code changes:

- tighten any remaining constructor / retention edge handling discovered during
  3A-3C rollout
- finalize semantics for initvar-as-local-temporary patterns
- add any small supporting helpers needed to keep the implementation explicit
  and stable without widening the public surface

Tests:

- coverage for `initvar(init=False, default_factory=...)` as a constructor-time
  local declaration
- additional transitive-liveness edge cases
- additional inheritance edge cases for merged initvars and fields
- regression coverage for combinations of:
  - eager-only initvars
  - retained late-use initvars
  - validator / hook / factory explicit initvar-name injection

Exit caveats:

- Do **not** close the rollout after 3C if the “init local variable” pattern is
  still ambiguous or untested.
- Phase 3D exists to prevent declaring success while the mainline feature works
  but important edge semantics remain underspecified in tests.

### Phase 4: `classvar` parallel metadata path

Code changes:

- add `ClassVarSpec`, `ClassVarField`, and `classvar(...)`
- extend declaration collection to classify classvar declarations separately
- add MRO merge for classvar metadata
- add class-decoration-time materialization onto the managed class object
- add `cls`-aware classvar `default_factory` validation and invocation
- keep classvar entirely out of:
  - `FieldSpec`
  - field-table installation
  - `LifecycleContextState.__field_specs__`
  - transaction/state machinery

Tests:

- classvar default materializes on the class at decoration time
- classvar zero-arg `default_factory` works
- classvar `default_factory(cls=...)` receives the managed class
- invalid classvar factory signatures fail decoration
- classvar mutable `default=` is allowed
- instance field mutable `default=` remains rejected
- subclass override of classvar merges deterministically
- classvar does not appear in instance field tables or constructor surface
- instance lookup sees classvar through normal class attribute lookup when not
  shadowed by instance descriptors

Exit caveats:

- Do **not** mark Phase 4 complete if classvar works only by being smuggled
  through `FieldSpec` and filtered out later.
- Do **not** accept an implementation that adds ad hoc `kind == ...` checks to
  keep classvar out of the instance pipeline. The absence of classvar from that
  pipeline must come from using a parallel declaration path from the start.
- Do **not** tag the phase complete unless tests prove classvar is absent from
  state tables, constructor acceptance, and transaction behavior.

## Concrete file-level edit plan

This section is the original target checklist; the corresponding behavior is
implemented in the tree unless an item is explicitly called out as deferred.

### `src/pyrolyze/lifecycle.py`

Add:

- `InitVarSpec`
- `InitVarField`
- `initvar(...)`
- initvar validation helpers
- runner policy helpers
- requestor/liveness helpers
- retained-initvar helpers

Modify:

- `LCKind`
- `FieldSpec`
- `LifecycleField`
- `lifecycle_field(...)`
- `_compile_injected_runner(...)`
- `_compile_factory_runner(...)`
- `LifecycleContextState`
- `_ManagedContextBase.__init__(...)`
- `_build_hook_runner_tables(...)`
- `_build_class_tables(...)`
- `_collect_own_field_specs(...)` or replacement collector
- `_merge_field_specs(...)`
- `managed_context(...)`
- validator invocation path

### `tests/test_api_lifecycle.py`

Add red/green coverage for:

- initvar declaration and constructor behavior
- `InitVarSpec.init` / `initvar(init=False, ...)` constructor filtering behavior
- initvar default factory dependency order
- explicit initvar-name injection into:
  - field factories
  - working default factories
  - hooks
  - commit validator
- dead-initvar transitive liveness rules
- retained storage and `to_frozen()`
- `FieldSpec.init`
- mutable-default rejection

### Expanded dark-spot test matrix

In addition to the core phase tests above, add explicit coverage for the
following edge scenarios.

#### Retention and late-use boundaries

- **Late/eager split in one class**
  - one initvar consumed only by eager `const(default_factory=...)`
  - one initvar consumed by lazy `static(default_factory=...)`
  - verify eager-only values are not retained while late-needed values are
    retained

- **Same initvar used by eager and late consumers**
  - one initvar requested by both eager `const` and lazy `static`
  - verify eager initialization does not consume/drop the value before the late
    path needs it

- **Late `working_default_factory` retention**
  - explicit initvar-name injection into `working_default_factory`
  - verify retention is sufficient across transaction boundaries

- **Rollback / close interactions**
  - retained initvars survive rollback when future late runners still need them
  - close-time behavior does not leak or expose retained private storage

#### Dead-initvar and dependency-graph behavior

- **Transitive liveness through initvar chain**
  - field or validator requests `c`
  - `c.default_factory` depends on `b`
  - `b.default_factory` depends on `a`
  - verify `a`, `b`, and `c` are all live

- **Dead isolated initvar chain**
  - `x.default_factory` depends on `y`
  - no non-initvar lifecycle consumer depends on either
  - decoration fails as dead declarations

- **Illegal forward dependency**
  - initvar `a.default_factory` names later initvar `b`
  - decoration fails clearly

- **Initvar default-factory exception hygiene**
  - one initvar resolves successfully
  - a later initvar factory raises
  - construction aborts without partial retained state

#### Inheritance and ordering

- **Diamond inheritance merge**
  - base declares initvar
  - intermediate classes redeclare compatibly
  - leaf class merges deterministically

- **Incompatible initvar redeclaration**
  - mismatched annotation narrowing or incompatible default/default_factory shape
  - decoration fails clearly

- **Field/initvar name collision through inheritance**
  - base field, derived initvar with same name
  - base initvar, derived field with same name
  - both fail clearly

- **Reserved-name collision through inheritance**
  - inherited or redeclared reserved names still fail deterministically

#### Injection-path coverage

- **Validator / hook / factory mixed requests**
  - the same initvar requested by `commit_validator`, a hook, and a factory
  - verify requestor scan and runtime injection all agree

- **Validator-only request**
  - `commit_validator` is the only consumer of an initvar
  - verify it counts as a requestor and receives the value correctly

- **Hook-only request**
  - hook is the only consumer
  - verify dead-initvar logic still treats it as live

- **Explicit signature edge cases**
  - positional-only parameter fails
  - bare `*args` fails
  - bare `**kwargs` fails
  - explicit keyword-only initvar param passes
  - explicit defaulted initvar param passes

#### Constructor exposure and filtering

- **Mixed bad constructor inputs**
  - constructor passes an `init=False` field and an unknown kw in the same call
  - verify the failure is deterministic and the error shape is stable

- **`FieldSpec.init` inheritance mismatch**
  - base and derived redeclarations disagree on `init`
  - decoration fails

- **`InitVarSpec.init` inheritance mismatch**
  - base and derived initvar redeclarations disagree on `init`
  - decoration fails

- **Init local variable pattern**
  - constructor-only temporary used only to compute a real lifecycle field
  - not retained after eager initialization

- **Init local variable plus late use**
  - same temporary pattern, but also needed by a late runner
  - verify retention changes appropriately

#### Retention normalization

- **`to_frozen()` selective behavior**
  - retained value with `to_frozen()`
  - retained value without `to_frozen()`
  - `to_frozen()` returns a mutable-looking object
  - `to_frozen()` raises
  - verify exact stored values and failure timing

#### Mutable-default validation

- **Override introduces mutable `default=`**
  - base uses safe `default_factory`
  - derived class overrides to `default=[]`
  - merged spec validation fails

## Non-goals

This plan does not implement:

- aggregate `initvars` injection parameter
- public retained-initvar API surface
- `__post_init__`

## Acceptance criteria

The following are **satisfied** for the shipped rollout (phases 3A–4):

- initvars are collected and merged independently of `FieldSpec`
- no field-kind identity comparisons were introduced to implement initvar semantics
- runner injection uses explicit semantic policies, not concrete-kind switches
- dead-initvar validation handles transitive liveness correctly
- late consumers get retained private initvar values by explicit name
- eager-only initvars are not retained
- validator injection works with explicit initvar names
- `FieldSpec.init` and `InitVarSpec.init` control constructor exposure for
  fields and initvars respectively
- mutable `default=` on instance fields is rejected
- `classvar` is collected and materialized on a parallel metadata path without
  entering instance field/state tables
- targeted tests pass, then full suite passes
