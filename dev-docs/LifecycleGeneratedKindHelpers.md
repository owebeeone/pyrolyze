# Lifecycle Generated Kind Helpers

## Purpose

This document specifies Phase 1B of the `LCKind` refactor: replacing handwritten
field helper functions with generated helpers whose signatures, defaults,
validation, and documentation all derive from declarative metadata on the kind
hierarchy.

Phase 1A (complete) introduced the `LCKind` class hierarchy, moved validation
and runtime dispatch onto it, and rewired the handwritten helpers to call
`lifecycle_field` with `LC_*` kind classes.  Phase 1B eliminates the handwritten
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
