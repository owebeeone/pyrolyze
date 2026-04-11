# Lifecycle InitVars Design

## Purpose

This document proposes `InitVar` support for `pyrolyze.lifecycle`.

This design also depends on a prerequisite lifecycle refactor:

- lifecycle field kinds must stop being modeled as scattered string literals
- field-kind behavior must be defined in one place through first-class metadata
  objects

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
    NoLifecycleHooksOperationalKind,
):
    # Derived declarative field behavior.
    @classmethod
    def build_shared_getter(cls, *, tx_index: int, spec: FieldSpec) -> FieldGetter:
        return _get_derived_field

    @classmethod
    def build_shared_setter(cls, *, tx_index: int, spec: FieldSpec) -> FieldSetter:
        return _set_derived_field


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


# Family traits.
class StoredKind(LCKind):
    @classmethod
    def validate_spec(cls, spec: FieldSpec) -> None:
        return None


class NonStoredHookKind(LCKind):
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
    ValueCompareKind,
    HookOperationalKind,
    AllowsDefaultKind,
    ForbidsDefaultFactoryKind,
    ForbidsWorkingDefaultFactoryKind,
    ForbidsInitialWorkingKind,
    ForbidsStateFactoryKind,
    ForbidsStateCopyKind,
    AllowsTxGroupKind,
):
    pass


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


class ResourceKind(SimpleStoredKind):
    # Stored retained-resource kinds with plain stored semantics and no special
    # state-factory or working-default behavior.
    pass


class StoredMetadataKind(
    StoredKind,
    ValueCompareKind,
    OverlayOperationalKind,
    AllowsDefaultKind,
    ForbidsDefaultFactoryKind,
    ForbidsWorkingDefaultFactoryKind,
    ForbidsInitialWorkingKind,
    ForbidsStateFactoryKind,
    ForbidsStateCopyKind,
    AllowsTxGroupKind,
):
    # Stored metadata declarations such as commit order keys and validators.
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
    NonTransactionalHelperKind,
):
    # Helper cache outside commit / rollback semantics.
    pass


class DerivedHelperKind(
    DerivedOperationalKind,
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


class CommitValidatorKind(StoredMetadataKind):
    # Stored declaration used only to validate commit eligibility.
    name = "commit_validator"


# Hook kinds.
class OnBeforeCommitKind(HookDeclarationKind):
    name = "on_before_commit"


class OnAfterCommitKind(HookDeclarationKind):
    name = "on_after_commit"


class OnAfterRollbackKind(HookDeclarationKind):
    name = "on_after_rollback"


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
  - defines validation protocol
- facets / mixins
  - define capability-level validators
- family bases
  - define shared semantics for stored kinds, hook kinds, etc.
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

### Generated field helpers

The `LCKind` model should go one step further: it should become the single
source of truth for the public field helper functions too.

Today we effectively maintain the same semantics in three places:

- validation logic
- field-table generation logic
- handwritten helper functions such as `const()`, `managed()`, `transient()`

That duplication is unnecessary. Once kinds are class-based, each terminal kind
can declare the constructor surface it supports and lifecycle can generate the
helper function from that declaration.

Target shape:

- each terminal kind declares which keyword parameters it accepts
- each terminal kind declares the defaults and annotations for those parameters
- lifecycle uses that to:
  - validate `FieldSpec`
  - build the ftable entries
  - generate the public helper function
  - generate human-readable documentation for that helper

This is the intended single-source-of-truth endpoint.

### Kind-declared helper signatures

Each terminal kind should declare the helper signature it wants exposed.

Near-copy-paste candidate shape:

```python
class KindParam:
    # Declarative description of one helper-function parameter.
    name: str
    annotation_src: str
    default_expr_src: str
    doc: str


class LCKind:
    name: str = "<unset>"

    @classmethod
    def field_helper_name(cls) -> str:
        # Most kinds use their lifecycle name directly.
        return cls.name

    @classmethod
    def field_helper_params(cls) -> tuple[KindParam, ...]:
        # Terminal kinds override this.
        raise NotImplementedError

    @classmethod
    def field_helper_doc(cls) -> str:
        # Terminal kinds override this with a short semantic summary.
        raise NotImplementedError

    @classmethod
    def field_helper_call_kwargs(cls) -> tuple[str, ...]:
        # Names forwarded into lifecycle_field(...).
        return tuple(param.name for param in cls.field_helper_params())
```

Then a terminal kind can say exactly what its public helper surface is:

```python
class ConstKind(StoredNeverKind, ImmutableConfigKind):
    name = "const"

    @classmethod
    def field_helper_doc(cls) -> str:
        return "Immutable per-instance configuration copied or derived at construction."

    @classmethod
    def field_helper_params(cls) -> tuple[KindParam, ...]:
        return (
            KindParam(
                name="default",
                annotation_src="Any",
                default_expr_src="MISSING",
                doc="Literal default value.",
            ),
            KindParam(
                name="default_factory",
                annotation_src="Callable[[], Any] | object",
                default_expr_src="MISSING",
                doc="Factory used when no explicit default is supplied.",
            ),
        )
```

And:

```python
class TransientKind(TxScopedScratchKind):
    name = "transient"

    @classmethod
    def field_helper_doc(cls) -> str:
        return "Pass-local scratch that exists only while a transaction group is open."

    @classmethod
    def field_helper_params(cls) -> tuple[KindParam, ...]:
        return (
            KindParam(
                name="tx_group",
                annotation_src="Hashable",
                default_expr_src="DEFAULT_TRANSACTION",
                doc="Transaction group that owns this scratch field.",
            ),
            KindParam(
                name="default",
                annotation_src="Any",
                default_expr_src="MISSING",
                doc="Default scratch value before first write.",
            ),
            KindParam(
                name="default_factory",
                annotation_src="Callable[[], Any] | object",
                default_expr_src="MISSING",
                doc="Factory for the default scratch value.",
            ),
            KindParam(
                name="working_default_factory",
                annotation_src="Callable[[], Any] | object",
                default_expr_src="MISSING",
                doc="Factory used to materialize the working scratch value lazily.",
            ),
        )
```

### Generated helper functions

The helper functions such as `const()` and `transient()` should be generated
from terminal kind declarations rather than handwritten.

The generated function body should be real source, not a generic `**kwargs`
wrapper, so:

- the Python signature is exact
- editors and `help()` show the real callable surface
- generated docs can quote the same signature

Target generated shape:

```python
def const(
    *,
    default: Any = MISSING,
    default_factory: Callable[[], Any] | object = MISSING,
) -> Any:
    return lifecycle_field(
        kind=LC_CONST,
        default=default,
        default_factory=default_factory,
    )
```

And:

```python
def transient(
    *,
    tx_group: Hashable = DEFAULT_TRANSACTION,
    default: Any = MISSING,
    default_factory: Callable[[], Any] | object = MISSING,
    working_default_factory: Callable[[], Any] | object = MISSING,
) -> Any:
    return lifecycle_field(
        kind=LC_TRANSIENT,
        tx_group=tx_group,
        default=default,
        default_factory=default_factory,
        working_default_factory=working_default_factory,
    )
```

Important constraint:

- helper generation uses declared metadata only
- helper generation must not reverse-engineer signatures from implementation
- kinds remain the canonical declaration point

Implementation technique:

- use the same source-generation pattern as stdlib `dataclasses`
- render real Python source for the helper function
- `exec(...)` that source in a controlled namespace
- bind real default values and annotation objects through generated locals
- do not use a generic `**kwargs` wrapper plus `__signature__` patching as the
  primary implementation

Reason:

- real Python call signatures produce the right error messages
- `help()` and editor introspection reflect the actual callable surface
- generated docs can reuse the same rendered signature
- this is a proven standard-library technique for exact generated APIs

### `@define_kind`

The cleanest way to keep terminal kinds declarative is to use a class decorator
that validates the declaration and generates the public helper function.

Target shape:

```python
@define_kind
class ConstKind(StoredNeverKind, ImmutableConfigKind):
    name = "const"
    helper_doc = "Immutable per-instance configuration copied or derived at construction."
    helper_params = (
        KindParam("default", "Any", "MISSING", "Literal default value."),
        KindParam(
            "default_factory",
            "Callable[[], Any] | object",
            "MISSING",
            "Factory used when no explicit default is supplied.",
        ),
    )
```

The decorator should:

- validate that the class is terminal and has a unique `name`
- validate that `helper_params` are legal for the kind
- validate that helper param names do not collide with reserved names
- generate the helper function source
- install it on the lifecycle module under `field_helper_name()`
- attach helper documentation and signature metadata back onto the kind

This keeps all declarative knowledge in one place:

- validation policy
- operational policy
- public helper signature
- public helper docs

### Auto-generated docs

Once helper signatures are declarative, lifecycle can also generate docs for
each field kind automatically.

At minimum, lifecycle should be able to produce for every terminal kind:

- helper name
- exact keyword-only signature
- one-paragraph semantic summary
- parameter table with defaults and per-parameter docs
- validation notes inferred from the kind hierarchy

That can drive:

- `help(pyrolyze.lifecycle.const)`
- markdown API docs
- debug dumps for `managed_context`
- future schema export if needed

The point is the same as the `LCKind` refactor itself:

- no handwritten duplicate lists
- no repeated helper signatures drifting out of sync
- no docstrings that silently lie
- one canonical declaration for behavior and API surface

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
