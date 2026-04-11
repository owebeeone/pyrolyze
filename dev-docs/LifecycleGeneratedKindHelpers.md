# Lifecycle Generated Kind Helpers

## Purpose

This document specifies Phase 1B of the `LCKind` refactor: replacing handwritten
field helper functions with generated helpers whose signatures, defaults,
validation, and documentation all derive from declarative metadata on the kind
hierarchy.

Phase 1A (complete) introduced the `LCKind` class hierarchy, moved validation
and runtime dispatch onto it, and rewired the handwritten helpers to call
`lifecycle_field` with `LC_*` kind classes.  An archived Phase 1A narrative and
large illustrative hierarchy sketch (pre-initvars doc) lives in the
[appendix](#appendix-phase-1a-prerequisite-design-archived) below.  Phase 1B eliminates the handwritten
helpers and the 16 `Allows*Kind`/`Forbids*Kind` validation mixin classes,
replacing both with a single param-descriptor system that serves as the source
of truth for:

- field-spec validation
- public helper function generation
- helper documentation

## Prerequisites

- Phase 1A is green (all tests pass except the two known-unrelated failures).
- The `LCKind` hierarchy, `LC_*` exports, `FieldSpec`, `lifecycle_field`, and
  `@managed_context` all work as shipped after Phase 1A.

## Design overview

### Single source of truth: `helper_params`

Each kind class in the hierarchy can declare a `helper_params` attribute built
with a chained `HelperParams` builder.  A resolver walks the MRO once per
terminal kind and merges the per-class contributions by param name, most-derived
wins.  Any `lifecycle_field` kwarg absent from the resolved dict is forbidden.

This replaces:

- the 14 `AllowsDefaultKind`, `ForbidsDefaultKind`, `AllowsDefaultFactoryKind`,
  `ForbidsDefaultFactoryKind`, `AllowsWorkingDefaultFactoryKind`,
  `ForbidsWorkingDefaultFactoryKind`, `AllowsInitialWorkingKind`,
  `ForbidsInitialWorkingKind`, `AllowsStateFactoryKind`,
  `ForbidsStateFactoryKind`, `AllowsStateCopyKind`, `ForbidsStateCopyKind`,
  `AllowsTxGroupKind`, `ForbidsCustomTxGroupKind` mixin classes
- the 2 `ValueCompareKind`, `ValueOrIdentityCompareKind` mixin classes
- all individual `validate_compare`, `validate_default`, etc. methods
- the per-kind handwritten helper functions (`const`, `managed`, etc.)

### Param descriptor types

```python
@dataclass(frozen=True, slots=True)
class ExposedParam:
    """Appears in the generated helper's keyword-only signature."""
    annotation_src: str
    default_src: str
    doc: str = ""
    allowed_values: frozenset | None = None

@dataclass(frozen=True, slots=True)
class FixedParam:
    """Passed to lifecycle_field with a fixed value; not in the signature."""
    value_src: str

SCRUB_PARAM = type('SCRUB_PARAM', (), {'__repr__': lambda s: 'SCRUB_PARAM'})()
```

- `ExposedParam` — the param appears in the helper signature with the given
  annotation, default, and optional allowed-value constraint.
- `FixedParam` — the param is always passed to `lifecycle_field` with the
  declared fixed value; the user never sees it.
- `SCRUB_PARAM` — removes an inherited param.  Scrubbing a param that is not
  inherited is a no-op.  Validation rejects non-neutral values for scrubbed
  params.

### Builder

```python
class HelperParams:
    """Chained builder for helper_params declarations."""

    def __init__(self):
        self._params: dict[str, ExposedParam | FixedParam | _ScrubType] = {}

    def param(self, name, doc=""):
        """Add a standard lifecycle_field param by name (preset lookup)."""
        preset = _PARAM_PRESETS[name]
        self._params[name] = ExposedParam(
            preset.annotation_src, preset.default_src, doc, preset.allowed_values,
        )
        return self

    def fixed(self, name, value_src):
        """Add a param that is always passed with a fixed value."""
        self._params[name] = FixedParam(value_src)
        return self

    def scrub(self, name):
        """Remove an inherited param (no-op if not inherited)."""
        self._params[name] = SCRUB_PARAM
        return self
```

Module-level entry points for concise chaining:

```python
def _param(name, doc=""):
    return HelperParams().param(name, doc)

def _fixed(name, value_src):
    return HelperParams().fixed(name, value_src)

def _scrub(name):
    return HelperParams().scrub(name)
```

### Presets

Each `lifecycle_field` kwarg has exactly one standard annotation and default,
drawn from the `lifecycle_field` signature itself:

```python
_PARAM_PRESETS = {
    "compare":                 ExposedParam("str",                            '"value"',              allowed_values=frozenset({"value", "identity"})),
    "tx_group":                ExposedParam("Hashable",                       "DEFAULT_TRANSACTION"),
    "default":                 ExposedParam("Any",                            "MISSING"),
    "default_factory":         ExposedParam("Callable[[], Any] | object",     "MISSING"),
    "working_default_factory": ExposedParam("Callable[[], Any] | object",     "MISSING"),
    "initial_working":         ExposedParam("Any",                            "MISSING"),
    "freeze":                  ExposedParam("Callable[[Any], Any] | None",    "None"),
    "thaw":                    ExposedParam("Callable[[Any], Any] | None",    "None"),
    "state_factory":           ExposedParam("Callable[[], Any] | None",       "None"),
    "state_copy":              ExposedParam("StateCopyHelper | None",         "None"),
}
```

### Resolver

The resolver walks the MRO in base-first order, collecting `helper_params`
from each class's own `__dict__`, and merges per param name:

```python
def _resolve_helper_params(cls):
    merged = {}
    for base in reversed(cls.__mro__):
        if 'helper_params' in base.__dict__:
            hp = base.__dict__['helper_params']
            for name, entry in hp._params.items():
                if isinstance(entry, _ScrubType):
                    merged.pop(name, None)
                else:
                    merged[name] = entry
    return merged
```

The resolved dict is cached on every `LCKind` subclass, not just terminals.
`LCKind.__init_subclass__` (or equivalent) calls the resolver and stores the
result as `cls._resolved_params` at class-creation time.  This means:

- intermediate kinds have a cached resolved dict too, available for
  introspection and debugging
- terminal kinds read the already-cached dict during validation and helper
  generation — no MRO walk at runtime
- the cost is one dict merge per class in the hierarchy, paid once at
  import time

### Merge semantics

- **Inheritance**: a param declared on an ancestor is inherited by all
  descendants unless overridden or voided.
- **Override**: a descendant redeclares the same param name; the descendant's
  entry wins.  This can change a param from exposed to fixed, fixed to exposed,
  or any other transition.
- **Scrub**: `SCRUB_PARAM` removes a param entirely.  Scrubbing a param that
  is not inherited is a no-op.  Validation rejects non-neutral values for
  scrubbed params.
- **No augmentation**: if the resolved result is wrong for a terminal kind, the
  kind declares an override or scrub.  There is no partial-merge or
  contradiction-detection layer.

### Generic validator

The generic validator replaces `validate_field_spec` and all per-dimension
`validate_*` methods:

```python
_LIFECYCLE_FIELD_NEUTRALS = {
    "compare":                 "value",
    "tx_group":                DEFAULT_TRANSACTION,
    "default":                 MISSING,
    "default_factory":         MISSING,
    "working_default_factory": MISSING,
    "initial_working":         MISSING,
    "freeze":                  None,
    "thaw":                    None,
    "state_factory":           None,
    "state_copy":              None,
}

@classmethod
def validate_field_spec(cls, spec):
    resolved = cls._resolved_helper_params()
    for kwarg, neutral in _LIFECYCLE_FIELD_NEUTRALS.items():
        actual = getattr(spec, kwarg)
        param = resolved.get(kwarg)
        if param is None:
            # Absent: forbidden
            if actual is not neutral and actual != neutral:
                raise TypeError(
                    f"{cls.name!r} fields cannot define {kwarg}"
                )
        elif isinstance(param, ExposedParam) and param.allowed_values is not None:
            if actual not in param.allowed_values:
                raise TypeError(
                    f"{cls.name!r} fields require {kwarg} in "
                    f"{param.allowed_values}"
                )
    cls.validate_spec(spec)
```

`validate_spec` remains as a per-kind hook for custom multi-field validation
(e.g. `NonStoredHookKind` checking that `default` is callable).

## Intermediate kind declarations

After the refactor, intermediate kinds declare `helper_params` instead of
inheriting Allows/Forbids mixin classes.  The operational and storage mixins
are unchanged.

```python
class DefaultStoredKind(StoredKind, OverlayOperationalKind):
    helper_params = (
        _param("compare").param("tx_group")
        .param("default").param("default_factory")
        .param("initial_working")
        .param("freeze").param("thaw")
        .param("state_factory").param("state_copy")
    )


class SimpleStoredKind(StoredKind, OverlayOperationalKind):
    helper_params = (
        _param("compare").param("tx_group")
        .param("default").param("default_factory")
    )


class ImmutableConfigKind(StoredKind):
    helper_params = (
        _fixed("compare", '"value"')
        .param("default").param("default_factory")
    )


class HookKind(NonStoredHookKind, HookOperationalKind):
    helper_params = (
        _fixed("compare", '"identity"')
        .param("tx_group").param("default")
    )


class StoredMetadataKind(StoredKind, StoredDeclarationOperationalKind):
    helper_params = (
        _param("compare").param("tx_group").param("default")
    )


class LocalLikeKind(StoredKind):
    helper_params = (
        _fixed("compare", '"value"')
        .param("default").param("default_factory")
    )


class TxScopedScratchKind(TransientOperationalKind, LocalLikeKind):
    helper_params = (
        _param("working_default_factory").param("tx_group")
    )


class NonTransactionalHelperKind(LocalLikeKind):
    pass


class NonTransactionalLocalKind(
    LocalStoreOperationalKind, LocalStoreStorageKind, NonTransactionalHelperKind,
):
    pass


class DerivedHelperKind(
    DerivedOperationalKind, DerivedStoreStorageKind, NonTransactionalHelperKind,
):
    pass
```

## Terminal kind declarations

Each terminal kind declares `name`, `helper_doc`, and optionally
`helper_params` overrides.

```python
@define_kind
class ManagedKind(DefaultStoredKind):
    name = "managed"
    helper_doc = "Managed transactional field with overlay, commit, and rollback."


@define_kind
class ConstKind(StoredNeverKind, ImmutableConfigKind):
    name = "const"
    helper_doc = "Immutable per-instance configuration, set at construction."


@define_kind
class StaticKind(StoredOnceKind, ImmutableConfigKind):
    name = "static"
    helper_doc = "Class-level shared value, written at most once."


@define_kind
class BindingKind(ResourceKind):
    name = "binding"
    helper_doc = "Identity-compared retained resource binding."
    helper_params = _fixed("compare", '"identity"')


@define_kind
class OwnedKind(ResourceKind):
    name = "owned"
    helper_doc = "Identity-compared owned child resource."
    helper_params = _fixed("compare", '"identity"')


@define_kind
class TransientKind(TxScopedScratchKind):
    name = "transient"
    helper_doc = "Transaction-scoped scratch that exists only while a group is open."


@define_kind
class LocalStoreKind(NonTransactionalLocalKind):
    name = "local_store"
    helper_doc = "Non-transactional local storage, cleared on close."


@define_kind
class DerivedKind(DerivedHelperKind):
    name = "derived"
    helper_doc = "Cached derived value, reset on commit/rollback/close."


@define_kind
class CommitOrderKeyKind(StoredMetadataKind):
    name = "commit_order_key"
    helper_doc = "Sortable key controlling commit ordering within a group."
    helper_params = _fixed("compare", '"value"')


@define_kind
class CommitValidatorKind(StoredMetadataKind):
    name = "commit_validator"
    helper_doc = "Callable that validates state before commit is finalized."
    helper_params = _fixed("compare", '"identity"')


@define_kind
class OnBeforeCommitKind(HookDeclarationKind):
    name = "on_before_commit"
    helper_doc = "Hook invoked before a transaction group commits."


@define_kind
class OnAfterCommitKind(HookDeclarationKind):
    name = "on_after_commit"
    helper_doc = "Hook invoked after a transaction group commits."


@define_kind
class OnAfterRollbackKind(HookDeclarationKind):
    name = "on_after_rollback"
    helper_doc = "Hook invoked after a transaction group rolls back."
```

Note: `BindingKind` and `OwnedKind` inherit `compare` as an exposed param from
`SimpleStoredKind` (via `ResourceKind`) and override it to
`FixedParam('"identity"')`.  All other terminal kinds inherit their complete
param surface from their intermediate base and add nothing.

## `@define_kind` decorator

The decorator is applied to every terminal kind class.  It:

1. validates that the class has a unique `name` not equal to `"<unset>"`
2. reads `cls._resolved_params` (already cached by `__init_subclass__`)
3. generates a real Python helper function via `exec()` (dataclasses technique)
4. installs the helper on the lifecycle module under `cls.name`
5. installs the `LC_` constant (`LC_{name.upper()} = cls`) on the module
6. appends both names to `__all__`
7. registers the kind in a module-level `_TERMINAL_KINDS` list
8. attaches the generated docstring back onto the class

### Helper generation technique

The generated function body is real Python source, not a `**kwargs` wrapper:

```python
# Generated source for const():
def const(*, default=_dflt_default, default_factory=_dflt_default_factory) -> Any:
    return lifecycle_field(
        kind=_kind_cls,
        default=default,
        default_factory=default_factory,
    )
```

The `exec()` namespace binds:

- `_kind_cls` — the terminal kind class
- `_dflt_<name>` — the real default-value object for each exposed param
- `lifecycle_field` — the function reference
- annotation objects (`Any`, `Callable`, `Hashable`, `StateCopyHelper`, etc.)

For fixed params, the fixed value is inlined in the `lifecycle_field(...)` call
and the corresponding default-value object is bound in the namespace.

The generated function gets:

- `__name__` and `__qualname__` set to the helper name
- `__module__` set to `"pyrolyze.lifecycle"`
- `__doc__` set to the kind's `helper_doc`
- `__annotations__` populated from the `annotation_src` strings evaluated in
  the exec namespace

This matches the stdlib `dataclasses` pattern for generating `__init__` methods
with exact signatures.

## `commit_order_key` and `default_factory`

`CommitOrderKeyKind.default_value` explicitly handles `default_factory`, so
`CommitOrderKeyKind` overrides its inherited `helper_params` to add
`default_factory` back (it is not present on `StoredMetadataKind`).  The
Phase 1A hierarchy had `ForbidsDefaultFactoryKind` on `StoredMetadataKind`,
which was correct for `CommitValidatorKind` but too restrictive for
`CommitOrderKeyKind`.

## What Phase 1B preserves

- helper names stay the same
- helper signatures stay semantically the same (the `commit_order_key` fix
  removes a dead parameter, which is a correctness improvement)
- helper defaults stay the same
- helper error behavior stays the same where practical
- `LC_*` exports stay the same
- `__all__` stays the same
- `FieldSpec`, `lifecycle_field`, and `@managed_context` are unchanged

## What Phase 1B removes

- 16 Allows/Forbids/Compare mixin classes
- all individual `validate_compare`, `validate_default`, `validate_default_factory`,
  `validate_working_default_factory`, `validate_initial_working`,
  `validate_state_factory`, `validate_state_copy`, `validate_tx_group` methods
- 13 handwritten helper functions
- 13 handwritten `LC_*` constant assignments
- handwritten `__all__` entries for helpers and `LC_*` constants

## What Phase 1B adds

- `ExposedParam`, `FixedParam`, `SCRUB_PARAM` types
- `HelperParams` builder with `_param()`, `_fixed()`, and `_scrub()` entry points
- `_PARAM_PRESETS` registry
- `_resolve_helper_params()` resolver
- generic `validate_field_spec` on `LCKind`
- `@define_kind` decorator
- `_TERMINAL_KINDS` registry
- `helper_params` declarations on intermediate kinds
- `helper_doc` declarations on terminal kinds

## Acceptance criteria

- no behavior regression relative to Phase 1A
- public helper functions are generated, not handwritten
- helper signatures, defaults, and docs come from `helper_params` metadata
- `Allows*Kind` and `Forbids*Kind` mixin classes are removed
- validation is driven by the resolved `helper_params`
- all existing tests pass (same result set as Phase 1A)

---

## Appendix: Phase 1A prerequisite design (archived)

The following material was moved from [LifecycleInitVarsDesign.md](LifecycleInitVarsDesign.md)
so that document can stay focused on **initvars** and the **`InitVarSpec`** type.

It records the original Phase 1A narrative and a large illustrative `LCKind`
hierarchy sketch (including the Allows/Forbids mixin era and `LC_*` exports).
**Phase 1B** in the sections above supersedes the handwritten-helper and mixin
validation parts of this sketch; treat the code blocks as design history and
intent, not necessarily a line-for-line match to current `lifecycle.py`.

## Prerequisite: `LCKind`

Before implementing initvars, lifecycle should introduce first-class field-kind
objects.

We are not using dataclasses for this. The kind system should be class-based.

Target shape:

```python
class LCKind:
    name: str

    @classmethod
    def validate_spec(cls, spec: FieldSpec) -> None: ...

    @classmethod
    def supports_compare(cls, compare: str) -> bool: ...
```

Each concrete lifecycle kind should be a class, and shared behavior should come
from inherited facets / mixins.

Illustrative shape:

```python
class AllowsDefault:
    @classmethod
    def validate_default(cls, spec: FieldSpec) -> None: ...


class AllowsDefaultFactory:
    @classmethod
    def validate_default_factory(cls, spec: FieldSpec) -> None: ...


class NonStoredHookKind:
    @classmethod
    def validate_spec(cls, spec: FieldSpec) -> None: ...


class ManagedKind(AllowsDefault, AllowsDefaultFactory, LCKind):
    name = "managed"


class OnBeforeCommitKind(NonStoredHookKind, LCKind):
    name = "on_before_commit"
```

The exact class layout may change, but the important rules are:

- each lifecycle kind is defined once
- its capabilities and restrictions live on that class
- validation reads those capabilities instead of checking membership in
  repeated sets of string literals

Examples of the current bad pattern:

- repeated `"managed"`, `"const"`, `"transient"`, etc
- repeated special-case sets for hook kinds
- repeated negative checks such as "these kinds cannot define X"

Those rules are currently distributed throughout the implementation. That is
the wrong shape for a system we intend to extend.

### Why this is required first

Initvars add more constructor-time semantics and more validation paths.

If lifecycle kinds remain stringly-typed, every new feature will continue to:

- add more string literals
- add more repeated membership checks
- spread validation logic wider

So the first step in this lifecycle iteration should be:

1. introduce `LCKind`
2. convert existing field kinds to canonical `LCKind` classes / singletons
3. move kind capability checks onto `LCKind`
4. only then add initvars and `FieldSpec.init`

### Validation model

Target style:

```python
if not isinstance(kind, LCKind):
    raise TypeError(f"unsupported lifecycle field kind {kind!r}")
kind.validate_compare(compare)
kind.validate_default(spec)
kind.validate_default_factory(spec)
kind.validate_working_default_factory(spec)
kind.validate_initial_working(spec)
kind.validate_state_factory(spec)
kind.validate_spec(spec)
```

The point is not the exact field names. The point is:

- no more distributed string lists
- no more hidden semantics in ad hoc set membership
- one canonical object per field kind

### Representation rule

Use classes plus inherited facets, not dataclasses.

Reason:

- validation behavior is part of the type, not passive metadata
- shared semantics can be inherited cleanly
- extension means composing behavior, not copying flags into more records

The immediate requirement is:

- one first-class kind class per semantic kind
- one place to describe capabilities
- shared validators through inheritance / facets

### Proposed class hierarchy

The cleanest model is:

- `FieldSpec.kind` stores a kind class, not a string
- exported lifecycle kind names are classes
- no singleton machinery is needed initially

One reviewable near-copy-paste candidate for `lifecycle.py` is:

```python
# Root protocol for all lifecycle field kinds.
# FieldSpec.kind should hold one of these classes, not a string. The kind owns
# both validation semantics and ftable builder selection.
class LCKind:
    name: str = "<unset>"

    # Validation protocol.
    @classmethod
    def validate_compare(cls, compare: str) -> None:
        raise NotImplementedError

    @classmethod
    def validate_default(cls, spec: FieldSpec) -> None:
        return None

    @classmethod
    def validate_default_factory(cls, spec: FieldSpec) -> None:
        return None

    @classmethod
    def validate_working_default_factory(cls, spec: FieldSpec) -> None:
        return None

    @classmethod
    def validate_initial_working(cls, spec: FieldSpec) -> None:
        return None

    @classmethod
    def validate_state_factory(cls, spec: FieldSpec) -> None:
        return None

    @classmethod
    def validate_state_copy(cls, spec: FieldSpec) -> None:
        return None

    @classmethod
    def validate_tx_group(cls, spec: FieldSpec) -> None:
        return None

    # Catch-all validation for rules that do not fit a smaller capability facet.
    @classmethod
    def validate_spec(cls, spec: FieldSpec) -> None:
        return None

    # Kinds must also own any special default-value semantics. This is required
    # to eliminate the remaining kind-specific branches for:
    # - static -> uninitialized sentinel
    # - commit_order_key -> ()
    # - commit_validator -> None
    @classmethod
    def default_value(cls, spec: FieldSpec) -> Any:
        if spec.default is not MISSING:
            return spec.default
        if spec.default_factory is not MISSING:
            return spec.default_factory()
        raise TypeError(f"missing required lifecycle field {spec.name!r}")

    # Constructor/default-store protocol. This is required to remove the
    # remaining storage-routing branches for:
    # - current_record-backed fields
    # - local_store-backed fields
    # - derived-backed fields
    # - declaration-only hook fields
    @classmethod
    def initialize_constructor_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
        values: dict[str, Any],
    ) -> None:
        if name in values:
            state.current_record.values[name] = values.pop(name)

    @classmethod
    def default_store_contains(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> bool:
        return name in state.current_record.values

    @classmethod
    def get_default_store_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> Any:
        return state.current_record.values[name]

    @classmethod
    def set_default_store_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
        value: Any,
    ) -> Any:
        state.current_record.values[name] = value
        return value

    @classmethod
    def reset_default_store(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> None:
        state.current_record.values.pop(name, None)

    # Registration protocol for the few remaining non-ftable dispatch points.
    # These must also move onto kinds so the runtime does not retain any
    # external kind-switch logic.
    @classmethod
    def register_hook_runner(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        hook_tables: HookRunnerTables,
    ) -> None:
        return None

    @classmethod
    def register_special_field(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        special_tables: SpecialFieldTables,
    ) -> None:
        return None

    # Operational protocol for field-table generation.
    # This is the important missing piece in the current stringly-typed design:
    # kinds must also own the getter/setter/hook table behavior.
    @classmethod
    def build_default_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        raise NotImplementedError

    @classmethod
    def build_current_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        raise NotImplementedError

    @classmethod
    def build_working_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        raise NotImplementedError

    @classmethod
    def build_default_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        raise NotImplementedError

    @classmethod
    def build_working_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        raise NotImplementedError

    @classmethod
    def build_commit_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        raise NotImplementedError

    @classmethod
    def build_rollback_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        raise NotImplementedError

    @classmethod
    def build_close_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        raise NotImplementedError

    @classmethod
    def build_state_factory(cls, spec: FieldSpec) -> FieldStateFactory | None:
        raise NotImplementedError

    @classmethod
    def build_state_copy(cls, spec: FieldSpec) -> StateCopyHelper | None:
        raise NotImplementedError


# Compare traits.
class ValueCompareKind(LCKind):
    @classmethod
    def validate_compare(cls, compare: str) -> None:
        if compare != "value":
            raise TypeError(f"{cls.name!r} fields require compare='value'")


class ValueOrIdentityCompareKind(LCKind):
    @classmethod
    def validate_compare(cls, compare: str) -> None:
        if compare not in {"value", "identity"}:
            raise TypeError(
                f"{cls.name!r} fields require compare in {{'value', 'identity'}}"
            )


# Operational traits. These choose the ftable entries for whole families of
# field kinds. The point of the intermediate bases is to bundle behavior that
# is operationally identical, then let concrete kinds override only the real
# semantic delta.
class NoStateHelpersOperationalKind(LCKind):
    # Most non-overlay kinds do not allocate per-field helper state or copy
    # helpers.
    @classmethod
    def build_state_factory(cls, spec: FieldSpec) -> FieldStateFactory | None:
        return None

    @classmethod
    def build_state_copy(cls, spec: FieldSpec) -> StateCopyHelper | None:
        return None


class NoLifecycleHooksOperationalKind(NoStateHelpersOperationalKind):
    # Most non-resource kinds share no-op commit / rollback / close hooks.
    @classmethod
    def build_commit_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _close_noop

    @classmethod
    def build_rollback_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _close_noop

    @classmethod
    def build_close_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _close_noop


class SameGetterEverywhereOperationalKind(LCKind):
    # Kinds like const, static, local_store, derived, and hooks expose one
    # conceptual value regardless of default/current/working view.
    @classmethod
    def build_shared_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        raise NotImplementedError

    @classmethod
    def build_default_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return cls.build_shared_getter(tx_index=tx_index, spec=spec)

    @classmethod
    def build_current_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return cls.build_shared_getter(tx_index=tx_index, spec=spec)

    @classmethod
    def build_working_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return cls.build_shared_getter(tx_index=tx_index, spec=spec)


class SameSetterEverywhereOperationalKind(LCKind):
    # Many non-overlay kinds also use the same setter in default/current/working
    # contexts.
    @classmethod
    def build_shared_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        raise NotImplementedError

    @classmethod
    def build_default_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return cls.build_shared_setter(tx_index=tx_index, spec=spec)

    @classmethod
    def build_working_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return cls.build_shared_setter(tx_index=tx_index, spec=spec)


class OverlayOperationalKind(LCKind):
    # Managed-style overlay semantics.
    @classmethod
    def build_default_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        if spec.thaw is not None:
            return _build_managed_thawed_getter(tx_index)
        if spec.initial_working is not MISSING:
            return _build_managed_initial_working_getter(tx_index)
        return _build_default_overlay_getter(tx_index)

    @classmethod
    def build_current_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_current_field

    @classmethod
    def build_working_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        if spec.thaw is not None:
            return _build_managed_thawed_getter(tx_index)
        if spec.initial_working is not MISSING:
            return _build_managed_initial_working_getter(tx_index)
        return _build_working_overlay_getter(tx_index)

    @classmethod
    def build_default_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        if spec.compare == "identity":
            return _build_default_identity_setter(tx_index)
        return _build_default_value_setter(tx_index)

    @classmethod
    def build_working_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        if spec.compare == "identity":
            return _build_working_identity_setter(tx_index)
        return _build_working_value_setter(tx_index)

    @classmethod
    def build_commit_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _build_overlay_commit_hook(tx_index)

    @classmethod
    def build_rollback_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _rollback_overlay_field

    @classmethod
    def build_close_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _close_noop

    @classmethod
    def build_state_factory(cls, spec: FieldSpec) -> FieldStateFactory | None:
        return spec.state_factory

    @classmethod
    def build_state_copy(cls, spec: FieldSpec) -> StateCopyHelper | None:
        return spec.state_copy


class ImmutableOperationalKind(
    SameGetterEverywhereOperationalKind,
    SameSetterEverywhereOperationalKind,
    NoLifecycleHooksOperationalKind,
):
    # Base for immutable non-transactional stored fields. Const and static are
    # identical except for the shared getter and shared setter they choose.
    pass


class ConstOperationalKind(ImmutableOperationalKind):
    # Constructor-fixed immutable value. Never writable after initialization.
    @classmethod
    def build_shared_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_current_field

    @classmethod
    def build_shared_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return _set_const_field


class StaticOperationalKind(ImmutableOperationalKind):
    # Write-once lazy state. This is the important semantic difference from
    # const: static may be initialized later exactly once.
    @classmethod
    def build_shared_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_static_field

    @classmethod
    def build_shared_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return _set_static_field


class StoredDeclarationOperationalKind(ConstOperationalKind):
    # Stored declarations such as commit_order_key / commit_validator behave
    # like const operationally: current-only reads, read-only setters, and no
    # commit-time publication.
    pass


class RetainedResourceOperationalKind(NoStateHelpersOperationalKind):
    # Binding and owned fields share the same table-building shape. Their
    # semantic distinction is ownership intent, not the ftable family.
    @classmethod
    def _is_mapping_field(cls, spec: FieldSpec) -> bool:
        return typing.get_origin(spec.annotation) in {dict, typing.Dict}

    @classmethod
    def build_default_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _build_default_overlay_getter(tx_index)

    @classmethod
    def build_current_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_current_field

    @classmethod
    def build_working_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _build_working_overlay_getter(tx_index)

    @classmethod
    def build_default_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        if cls._is_mapping_field(spec):
            return _build_default_binding_map_setter(tx_index)
        return _build_default_binding_setter(tx_index)

    @classmethod
    def build_working_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        if cls._is_mapping_field(spec):
            return _build_working_binding_map_setter(tx_index)
        return _build_working_binding_setter(tx_index)

    @classmethod
    def build_commit_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        if cls._is_mapping_field(spec):
            return _build_binding_map_commit_hook(tx_index)
        return _build_binding_commit_hook(tx_index)

    @classmethod
    def build_rollback_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        if cls._is_mapping_field(spec):
            return _build_binding_map_rollback_hook(tx_index)
        return _build_binding_rollback_hook(tx_index)

    @classmethod
    def build_close_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        if cls._is_mapping_field(spec):
            return _close_binding_map_field
        return _close_binding_field


class TransientOperationalKind(NoLifecycleHooksOperationalKind):
    # Tx-group scratch behavior.
    @classmethod
    def build_default_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        if spec.working_default_factory is not MISSING:
            return _build_transient_working_default_getter(tx_index)
        return _build_default_overlay_getter(tx_index)

    @classmethod
    def build_current_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_current_field

    @classmethod
    def build_working_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        if spec.working_default_factory is not MISSING:
            return _build_transient_working_default_getter(tx_index)
        return _build_working_overlay_getter(tx_index)

    @classmethod
    def build_default_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return _build_default_value_setter(tx_index)

    @classmethod
    def build_working_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return _build_working_value_setter(tx_index)


class LocalStoreOperationalKind(
    SameGetterEverywhereOperationalKind,
    SameSetterEverywhereOperationalKind,
    NoStateHelpersOperationalKind,
):
    # Non-authoritative helper store behavior.
    @classmethod
    def build_shared_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_local_store_field

    @classmethod
    def build_shared_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return _set_local_store_field

    @classmethod
    def build_commit_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _close_noop

    @classmethod
    def build_rollback_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _close_noop

    @classmethod
    def build_close_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _close_local_store_field


class DerivedOperationalKind(
    SameGetterEverywhereOperationalKind,
    SameSetterEverywhereOperationalKind,
    NoStateHelpersOperationalKind,
):
    # Derived declarative field behavior.
    @classmethod
    def build_shared_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_derived_field

    @classmethod
    def build_shared_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return _set_derived_field

    @classmethod
    def build_commit_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _reset_derived_field

    @classmethod
    def build_rollback_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _reset_derived_field

    @classmethod
    def build_close_hook(cls, *, tx_index: int, spec: FieldSpec) -> FieldHook:
        return _reset_derived_field


class HookOperationalKind(
    SameGetterEverywhereOperationalKind,
    SameSetterEverywhereOperationalKind,
    NoLifecycleHooksOperationalKind,
):
    # Non-stored hook declaration behavior.
    @classmethod
    def build_shared_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_hook_declaration_field

    @classmethod
    def build_shared_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return _set_hook_declaration_field


# Default / factory traits.
class AllowsDefaultKind(LCKind):
    @classmethod
    def validate_default(cls, spec: FieldSpec) -> None:
        return None


class ForbidsDefaultKind(LCKind):
    @classmethod
    def validate_default(cls, spec: FieldSpec) -> None:
        if spec.default is not MISSING:
            raise TypeError(f"{cls.name!r} fields cannot define default")


class AllowsDefaultFactoryKind(LCKind):
    @classmethod
    def validate_default_factory(cls, spec: FieldSpec) -> None:
        return None


class ForbidsDefaultFactoryKind(LCKind):
    @classmethod
    def validate_default_factory(cls, spec: FieldSpec) -> None:
        if spec.default_factory is not MISSING:
            raise TypeError(f"{cls.name!r} fields cannot define default_factory")


class AllowsWorkingDefaultFactoryKind(LCKind):
    @classmethod
    def validate_working_default_factory(cls, spec: FieldSpec) -> None:
        return None


class ForbidsWorkingDefaultFactoryKind(LCKind):
    @classmethod
    def validate_working_default_factory(cls, spec: FieldSpec) -> None:
        if spec.working_default_factory is not MISSING:
            raise TypeError(
                f"{cls.name!r} fields cannot define working_default_factory"
            )


class AllowsInitialWorkingKind(LCKind):
    @classmethod
    def validate_initial_working(cls, spec: FieldSpec) -> None:
        return None


class ForbidsInitialWorkingKind(LCKind):
    @classmethod
    def validate_initial_working(cls, spec: FieldSpec) -> None:
        if spec.initial_working is not MISSING:
            raise TypeError(f"{cls.name!r} fields cannot define initial_working")


# State helper traits.
class AllowsStateFactoryKind(LCKind):
    @classmethod
    def validate_state_factory(cls, spec: FieldSpec) -> None:
        return None


class ForbidsStateFactoryKind(LCKind):
    @classmethod
    def validate_state_factory(cls, spec: FieldSpec) -> None:
        if spec.state_factory is not None:
            raise TypeError(f"{cls.name!r} fields cannot define state_factory")


class AllowsStateCopyKind(LCKind):
    @classmethod
    def validate_state_copy(cls, spec: FieldSpec) -> None:
        return None


class ForbidsStateCopyKind(LCKind):
    @classmethod
    def validate_state_copy(cls, spec: FieldSpec) -> None:
        if spec.state_copy is not None:
            raise TypeError(f"{cls.name!r} fields cannot define state_copy")


# Transaction-group traits.
class AllowsTxGroupKind(LCKind):
    @classmethod
    def validate_tx_group(cls, spec: FieldSpec) -> None:
        return None


class ForbidsCustomTxGroupKind(LCKind):
    @classmethod
    def validate_tx_group(cls, spec: FieldSpec) -> None:
        if spec.tx_group != DEFAULT_TRANSACTION:
            raise TypeError(f"{cls.name!r} fields cannot override tx_group")


# Registration/state-routing helpers.
class HookRunnerTables:
    before_commit: dict[Hashable, list[InjectedRunner]]
    after_commit: dict[Hashable, list[InjectedRunner]]
    after_rollback: dict[Hashable, list[InjectedRunner]]


class SpecialFieldTables:
    commit_order_key_by_group: dict[Hashable, str]
    commit_validator_by_group: dict[Hashable, str]


class CurrentRecordStorageKind(LCKind):
    # Most stored fields live in current_record plus optional working overlays.
    pass


class LocalStoreStorageKind(LCKind):
    @classmethod
    def initialize_constructor_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
        values: dict[str, Any],
    ) -> None:
        if name in values:
            state.local_store_values[name] = values.pop(name)

    @classmethod
    def default_store_contains(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> bool:
        return name in state.local_store_values

    @classmethod
    def get_default_store_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> Any:
        return state.local_store_values[name]

    @classmethod
    def set_default_store_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
        value: Any,
    ) -> Any:
        state.local_store_values[name] = value
        return value

    @classmethod
    def reset_default_store(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> None:
        state.local_store_values.pop(name, None)


class DerivedStoreStorageKind(LCKind):
    @classmethod
    def initialize_constructor_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
        values: dict[str, Any],
    ) -> None:
        if name in values:
            state.derived_values[name] = values.pop(name)

    @classmethod
    def default_store_contains(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> bool:
        return name in state.derived_values

    @classmethod
    def get_default_store_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> Any:
        return state.derived_values[name]

    @classmethod
    def set_default_store_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
        value: Any,
    ) -> Any:
        state.derived_values[name] = value
        return value

    @classmethod
    def reset_default_store(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
    ) -> None:
        state.derived_values.pop(name, None)


class DeclarationStorageKind(LCKind):
    # Hook declaration fields are not readable stored values and should consume
    # any constructor kwarg without publishing it into runtime field state.
    @classmethod
    def initialize_constructor_value(
        cls,
        *,
        state: LifecycleContextState,
        name: str,
        values: dict[str, Any],
    ) -> None:
        del state
        values.pop(name, None)


# Family traits.
class StoredKind(CurrentRecordStorageKind, LCKind):
    @classmethod
    def validate_spec(cls, spec: FieldSpec) -> None:
        return None


class NonStoredHookKind(DeclarationStorageKind, LCKind):
    @classmethod
    def validate_spec(cls, spec: FieldSpec) -> None:
        # Hook declarations are not stored runtime fields. They require a
        # callable default and disallow the normal stored-field machinery.
        if spec.default is MISSING:
            raise TypeError(f"{cls.name!r} fields require default=callable")
        if spec.default_factory is not MISSING:
            raise TypeError(f"{cls.name!r} fields cannot define default_factory")
        if spec.working_default_factory is not MISSING:
            raise TypeError(
                f"{cls.name!r} fields cannot define working_default_factory"
            )
        if spec.initial_working is not MISSING:
            raise TypeError(f"{cls.name!r} fields cannot define initial_working")
        if spec.state_factory is not None:
            raise TypeError(f"{cls.name!r} fields cannot define state_factory")
        if spec.state_copy is not None:
            raise TypeError(f"{cls.name!r} fields cannot define state_copy")


# Composed family bases to reduce repetition in the concrete kinds.
class DefaultStoredKind(
    StoredKind,
    ValueOrIdentityCompareKind,
    OverlayOperationalKind,
    AllowsDefaultKind,
    AllowsDefaultFactoryKind,
    ForbidsWorkingDefaultFactoryKind,
    AllowsInitialWorkingKind,
    AllowsStateFactoryKind,
    AllowsStateCopyKind,
    AllowsTxGroupKind,
):
    pass


class SimpleStoredKind(
    StoredKind,
    ValueOrIdentityCompareKind,
    OverlayOperationalKind,
    AllowsDefaultKind,
    AllowsDefaultFactoryKind,
    ForbidsWorkingDefaultFactoryKind,
    ForbidsInitialWorkingKind,
    ForbidsStateFactoryKind,
    ForbidsStateCopyKind,
    AllowsTxGroupKind,
):
    pass


class HookKind(
    NonStoredHookKind,
    ValueOrIdentityCompareKind,
    HookOperationalKind,
    AllowsDefaultKind,
    ForbidsDefaultFactoryKind,
    ForbidsWorkingDefaultFactoryKind,
    ForbidsInitialWorkingKind,
    ForbidsStateFactoryKind,
    ForbidsStateCopyKind,
    AllowsTxGroupKind,
):
    # Phase 1A must preserve the current public helper surface. The existing
    # hook helpers currently pass compare="identity", so hook kinds must accept
    # both compare modes even though the compare value is operationally inert
    # for non-stored hook declarations.
    @classmethod
    def register_hook_runner(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        hook_tables: HookRunnerTables,
    ) -> None:
        raise NotImplementedError


# Intermediate descriptor classes for recurring semantic bundles.
class ImmutableConfigKind(
    StoredKind,
    ValueCompareKind,
    AllowsDefaultKind,
    AllowsDefaultFactoryKind,
    ForbidsWorkingDefaultFactoryKind,
    ForbidsInitialWorkingKind,
    ForbidsStateFactoryKind,
    ForbidsStateCopyKind,
    ForbidsCustomTxGroupKind,
):
    # Immutable-style configuration restrictions shared by const and static.
    # This class describes validation policy only; the write/read operational
    # rule is supplied by a more specific base.
    pass


class StoredNeverKind(ConstOperationalKind):
    # Read like current everywhere, and reject all assignment after
    # initialization.
    pass


class StoredOnceKind(StaticOperationalKind):
    # Read like static everywhere, and allow exactly one assignment while unset.
    pass


class ResourceKind(RetainedResourceOperationalKind, SimpleStoredKind):
    # Stored retained-resource kinds with plain stored semantics and no special
    # state-factory or working-default behavior.
    pass


class StoredMetadataKind(
    StoredKind,
    ValueOrIdentityCompareKind,
    StoredDeclarationOperationalKind,
    AllowsDefaultKind,
    ForbidsDefaultFactoryKind,
    ForbidsWorkingDefaultFactoryKind,
    ForbidsInitialWorkingKind,
    ForbidsStateFactoryKind,
    ForbidsStateCopyKind,
    AllowsTxGroupKind,
):
    # Stored metadata declarations such as commit order keys and validators.
    # Phase 1A must preserve the current public helper surface. The existing
    # commit_validator helper currently passes compare="identity", so metadata
    # kinds must accept both compare modes during the refactor.
    pass


class HookDeclarationKind(HookKind):
    # Non-stored callable hook declarations.
    pass


class LocalLikeKind(
    StoredKind,
    ValueCompareKind,
    AllowsDefaultKind,
    AllowsDefaultFactoryKind,
    ForbidsInitialWorkingKind,
    ForbidsStateFactoryKind,
    ForbidsStateCopyKind,
):
    # Non-authoritative helper-like fields. The two main variants are:
    # - transient: tx-scoped scratch with working-default support
    # - local_store: non-transactional helper cache
    pass


class TxScopedScratchKind(
    TransientOperationalKind,
    AllowsWorkingDefaultFactoryKind,
    AllowsTxGroupKind,
    LocalLikeKind,
):
    # Scratch scoped to an open transaction group.
    pass


class NonTransactionalHelperKind(
    ForbidsWorkingDefaultFactoryKind,
    ForbidsCustomTxGroupKind,
    LocalLikeKind,
):
    # Helper-like fields outside commit / rollback semantics.
    pass


class NonTransactionalLocalKind(
    LocalStoreOperationalKind,
    LocalStoreStorageKind,
    NonTransactionalHelperKind,
):
    # Helper cache outside commit / rollback semantics.
    pass


class DerivedHelperKind(
    DerivedOperationalKind,
    DerivedStoreStorageKind,
    NonTransactionalHelperKind,
):
    # Declarative non-transactional helper value.
    pass


# Concrete stored lifecycle kinds.
class ManagedKind(DefaultStoredKind):
    # Authoritative current/working state with overlay commit / rollback.
    name = "managed"


class ConstKind(StoredNeverKind, ImmutableConfigKind):
    # Immutable per-instance configuration copied or derived at construction.
    name = "const"


class StaticKind(
    StoredOnceKind,
    ImmutableConfigKind,
):
    # Shared or lazily resolved non-transactional state.
    name = "static"

    @classmethod
    def default_value(cls, spec: FieldSpec) -> Any:
        if spec.default is MISSING and spec.default_factory is MISSING:
            return _SENTINEL
        return super().default_value(spec)


class BindingKind(ResourceKind):
    # Retained borrowed resource with commit / rollback binding semantics.
    name = "binding"


class OwnedKind(ResourceKind):
    # Retained owned resource with ownership-oriented lifecycle semantics.
    name = "owned"


class TransientKind(TxScopedScratchKind):
    # Pass-local scratch that exists only while a transaction group is open.
    name = "transient"


class LocalStoreKind(NonTransactionalLocalKind):
    # Non-authoritative helper cache that does not participate in commit/rollback.
    name = "local_store"


class DerivedKind(DerivedHelperKind):
    # Declarative derived value, not directly authoritative mutable state.
    name = "derived"


# Special stored metadata kinds.
class CommitOrderKeyKind(StoredMetadataKind):
    # Stored declaration used only to order commits within a tx group.
    name = "commit_order_key"

    @classmethod
    def default_value(cls, spec: FieldSpec) -> Any:
        if spec.default is not MISSING:
            return spec.default
        if spec.default_factory is not MISSING:
            return spec.default_factory()
        return ()

    @classmethod
    def register_special_field(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        special_tables: SpecialFieldTables,
    ) -> None:
        if spec.tx_group in special_tables.commit_order_key_by_group:
            raise TypeError(
                f"at most one commit_order_key field is allowed for group {spec.tx_group!r}"
            )
        special_tables.commit_order_key_by_group[spec.tx_group] = name


class CommitValidatorKind(StoredMetadataKind):
    # Stored declaration used only to validate commit eligibility.
    name = "commit_validator"

    @classmethod
    def default_value(cls, spec: FieldSpec) -> Any:
        if spec.default is not MISSING:
            return spec.default
        return None

    @classmethod
    def register_special_field(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        special_tables: SpecialFieldTables,
    ) -> None:
        if spec.tx_group in special_tables.commit_validator_by_group:
            raise TypeError(
                f"at most one commit_validator field is allowed for group {spec.tx_group!r}"
            )
        special_tables.commit_validator_by_group[spec.tx_group] = name


# Hook kinds.
class OnBeforeCommitKind(HookDeclarationKind):
    name = "on_before_commit"

    @classmethod
    def register_hook_runner(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        hook_tables: HookRunnerTables,
    ) -> None:
        hook_tables.before_commit.setdefault(spec.tx_group, []).append(
            _compile_hook_runner(
                field_name=name,
                hook_name="on_before_commit",
                hook=typing.cast(Callable[..., Any], spec.default),
                allowed_params=_BEFORE_COMMIT_PARAMS,
            )
        )


class OnAfterCommitKind(HookDeclarationKind):
    name = "on_after_commit"

    @classmethod
    def register_hook_runner(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        hook_tables: HookRunnerTables,
    ) -> None:
        hook_tables.after_commit.setdefault(spec.tx_group, []).append(
            _compile_hook_runner(
                field_name=name,
                hook_name="on_after_commit",
                hook=typing.cast(Callable[..., Any], spec.default),
                allowed_params=_AFTER_COMMIT_PARAMS,
            )
        )


class OnAfterRollbackKind(HookDeclarationKind):
    name = "on_after_rollback"

    @classmethod
    def register_hook_runner(
        cls,
        *,
        name: str,
        spec: FieldSpec,
        hook_tables: HookRunnerTables,
    ) -> None:
        hook_tables.after_rollback.setdefault(spec.tx_group, []).append(
            _compile_hook_runner(
                field_name=name,
                hook_name="on_after_rollback",
                hook=typing.cast(Callable[..., Any], spec.default),
                allowed_params=_AFTER_ROLLBACK_PARAMS,
            )
        )


# Exported canonical names.
# These are classes today. If we ever need singleton instances later, these
# names can change behind the same exported API surface.
LC_MANAGED = ManagedKind
LC_CONST = ConstKind
LC_STATIC = StaticKind
LC_BINDING = BindingKind
LC_OWNED = OwnedKind
LC_TRANSIENT = TransientKind
LC_LOCAL_STORE = LocalStoreKind
LC_DERIVED = DerivedKind
LC_COMMIT_ORDER_KEY = CommitOrderKeyKind
LC_COMMIT_VALIDATOR = CommitValidatorKind
LC_ON_BEFORE_COMMIT = OnBeforeCommitKind
LC_ON_AFTER_COMMIT = OnAfterCommitKind
LC_ON_AFTER_ROLLBACK = OnAfterRollbackKind
```

### `FieldSpec.kind` type

The preferred type is:

```python
kind: type[LCKind]
```

Not:

- `str`
- `Enum`
- ad hoc union of names

### Responsibility split

The hierarchy should divide responsibility like this:

- root `LCKind`
  - defines validation, default-value, storage-routing, and registration protocol
- facets / mixins
  - define capability-level validators
- family bases
  - define shared semantics for stored kinds, hook kinds, helper-store kinds, etc.
- concrete kinds
  - name the kind and add only truly kind-specific rules

That keeps extension disciplined:

- add a new capability -> add a facet
- add a new kind family -> add a family base
- add a new lifecycle kind -> compose existing traits plus minimal custom logic

### Canonical exported values

Lifecycle should export canonical kind objects such as:

```python
LC_MANAGED
LC_CONST
LC_STATIC
LC_BINDING
LC_OWNED
LC_TRANSIENT
LC_LOCAL_STORE
LC_DERIVED
LC_COMMIT_ORDER_KEY
LC_COMMIT_VALIDATOR
LC_ON_BEFORE_COMMIT
LC_ON_AFTER_COMMIT
LC_ON_AFTER_ROLLBACK
```

Whether these are singleton instances of kind classes or the classes
themselves is an implementation choice. The important rule is:

- `FieldSpec.kind` should store an `LCKind`, not a raw string

### Constraints

1. No lifecycle validation logic should depend on repeated string literal sets.
2. `FieldSpec.kind` should be typed as `LCKind`.
3. All kind-specific capability checks should come from `LCKind` class
   behavior.
4. New lifecycle features must extend `LCKind`, not add new scattered
   string-switch logic.
5. No runtime path may retain `kind == ...` or `kind in {...}` dispatch once
   the `LCKind` refactor is complete.
6. Constructor-value routing, default-store routing, hook registration, and
   special-field registration must dispatch through `LCKind` methods too, not
   helper-side special cases.

### Phase split

This lifecycle iteration is intentionally split into two separate phases.

#### Phase 1A: `LCKind` integration only

Phase 1A is the structural refactor that replaces stringly-typed lifecycle
kinds with class-based `LCKind` behavior.

What Phase 1A changes:

- introduce the `LCKind` hierarchy and `LC_*` exports
- change `FieldSpec.kind` and `LifecycleField.kind` to store an `LCKind`
  class, not a raw string
- move validation onto `LCKind`
- move constructor-value routing onto `LCKind`
- move default-store routing onto `LCKind`
- move special-field registration onto `LCKind`
- move hook-runner registration onto `LCKind`
- move ftable installation onto `LCKind`
- keep the existing handwritten public helper functions (`const`,
  `managed`, `transient`, etc), but make them call `lifecycle_field` with the
  new `LC_*` kind classes

What Phase 1A explicitly does not change:

- no generated helper functions
- no `@define_kind`
- no helper signature generation
- no initvars
- no constructor-generation redesign
- no intended public behavior changes

Phase 1A acceptance criteria:

- the lifecycle API surface behaves the same as before
- existing helper names stay the same
- existing helper defaults stay the same
- transaction behavior stays the same
- tests should pass with the same result set as the pre-refactor baseline

In short: Phase 1A changes the implementation model, not the public helper
surface.

#### Phase 1B: generated helper substitution

Phase 1B is specified in a separate document:
[LifecycleGeneratedKindHelpers.md](LifecycleGeneratedKindHelpers.md).

The two phases have different goals:

- Phase 1A removes string dispatch and centralizes runtime semantics
- Phase 1B removes handwritten helper duplication, the Allows/Forbids mixin
  explosion, and centralizes both validation and helper API declarations into
  a single param-descriptor system
