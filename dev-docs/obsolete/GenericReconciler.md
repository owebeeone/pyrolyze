# Generic Reconciler Plan

## Purpose

This document defines the plan for turning the current shipped reconciler into a
generic library-facing reconciler that can support multiple UI libraries
without hard-coding the semantic node set in backend adapters.

The detailed terminology and API direction in this plan have been partially
superseded by:

- [GenericReconcilerRequirements.md](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/dev-docs/GenericReconcilerRequirements.md)
- [GenericReconcilerApiProposal.md](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/dev-docs/GenericReconcilerApiProposal.md)

Those two documents should be treated as the authoritative current direction
for naming and public API shape.

The intent is not to replace the current reconciler model. The intent is to
finish the abstraction boundary that the current code already suggests.


## Current State

The current implementation is already partly generic.

### What is already generic

The normalized node layer in
[/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/runtime/ui_nodes.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/runtime/ui_nodes.py)
already has the right shape for a generic reconciler:

- `UiNodeDescriptor`
- `UiPropSpec`
- `UiEventSpec`
- `UiNodeDescriptorRegistry`
- `UiNodeSpec`
- `UiNodeId`
- `reconcile_owner(...)`
- `reconcile_children(...)`
- `mount_subtree(...)`

This means the reconciliation algorithm is already driven by:

- node identity
- kind descriptors
- prop/event diffing rules
- backend reuse decisions

That is the correct architectural direction.

### What is still fixed to the built-in node set

The shipped registry in
[/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/runtime/ui_nodes.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/runtime/ui_nodes.py)
is still a frozen built-in registry:

- `section`
- `row`
- `badge`
- `button`
- `text_field`
- `toggle`
- `select_field`

The shipped backends still hard-code binding logic by `spec.kind`:

- [pyrolyze_pyside6.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/pyrolyze_pyside6.py)
- [pyrolyze_tkinter.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/pyrolyze_tkinter.py)

That means the reconciler core is generic, but the end-to-end system is not yet
library-generic.

### Important pulled changes already in place

This plan reflects the current code after the recent pull.

Notable current details:

- `UIElement` already carries instance metadata:
  - `call_site_id`
  - `slot_id`
- `UiOwnerCommitState` now tracks `last_backend_identity`
- `normalize_ui_inputs(...)` already knows how to derive stable node ids from
  instance-side metadata and mappings

Those changes make this plan easier to implement. They do not invalidate it.


## Problem Statement

Today there are two different concerns mixed together:

1. Generic reconciliation concerns
- identity
- prop diffing
- child placement
- subtree reuse
- owner commit state

2. Built-in semantic UI library concerns
- what kinds exist
- which props/events they support
- how those kinds become widgets in PySide6 or tkinter

The generic reconciler should only own the first group.

UI libraries should own the second group.


## Design Goal

PyRolyze should support a model where a UI library can provide:

- a semantic node descriptor registry
- backend-specific binding factories
- optional helper constructors for author code
- optional normalization/validation helpers

without changing the reconciler algorithm itself.


## Non-Goals

This plan does not try to:

- remove `call_native(...)`
- redesign the AST transform
- collapse the semantic-node path and raw native path into one path
- add nested reconciler registries per subtree

Those may be revisited later, but they are outside this plan.


## Current `UIElement` Assessment

`UIElement` currently lives in
[/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/api.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/api.py)
and has:

- `kind`
- `props`
- `children`
- `call_site_id`
- `slot_id`

This is a reasonable instance-level payload.

### What metadata on `UIElement` is good for

Instance metadata is appropriate for:

- stable per-emission identity hints
- debug labels
- explicit descriptor selection override
- explicit library namespace
- explicit reconciliation key material

### What metadata on `UIElement` is not good for

Per-instance metadata should not become the place where we define:

- required props
- default props
- child policy
- event schema
- identity-affecting prop rules
- backend binding behavior

Those are kind-level semantics and belong in registries.


## Plan Of Record

The generic reconciler should be built around three public concepts.

### 1. `UIElement` remains an instance object

`UIElement` should stay small and cheap to construct.

It may grow a small metadata object, but that metadata must stay focused on
instance-level hints.

Recommended direction:

```python
@dataclass(frozen=True, slots=True)
class UiElementMeta:
    descriptor_key: str | None = None
    debug_label: str | None = None
    key_parts: tuple[object, ...] = ()


@dataclass(frozen=True, slots=True)
class UIElement:
    kind: str
    props: dict[str, Any]
    children: tuple["UIElement", ...] = ()
    call_site_id: int | str | None = None
    slot_id: Any | None = None
    meta: UiElementMeta | None = None
```

This is optional but useful. The existing `call_site_id` and `slot_id` fields
already prove that instance metadata is useful.

### 2. Kind semantics live in a library registry

The real semantic contract should remain registry-driven.

The current `UiNodeDescriptorRegistry` is the right base.

We should formalize a library-facing wrapper around it, for example:

```python
@dataclass(frozen=True, slots=True)
class UiLibrarySpec:
    library_id: str
    descriptors: UiNodeDescriptorRegistry
```

This gives each library:

- a stable id
- a known set of supported kinds
- prop and event validation rules
- child policy rules

### 3. Backend widget logic lives in a backend-side binding registry

The current backend adapters should stop switching on `spec.kind`.

Instead, each backend should register per-kind handlers, for example:

```python
class UiBackendBindingFactory(Protocol):
    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding: ...

    def can_reuse(self, current: UiNode, next_spec: UiNodeSpec) -> bool: ...
```

and then:

```python
@dataclass(slots=True)
class UiBackendBindingRegistry:
    factories: dict[str, UiBackendBindingFactory]
```

The backend adapter then becomes a small dispatcher over the binding registry,
instead of a hard-coded list of `if spec.kind == ...` branches.


## Proposed Public Shape

The system should eventually expose a library-facing assembly like:

```python
@dataclass(frozen=True, slots=True)
class UiRuntimeSpec:
    library: UiLibrarySpec
    backend_bindings: UiBackendBindingRegistry
```

The reconciler APIs should accept a runtime spec or the equivalent pair of:

- descriptor registry
- backend binding registry

The built-in v1 semantic nodes should simply become one shipped library spec.


## Required Implementation Changes

### Phase 1: Formalize current boundaries

Goal:
- no behavior change
- make the current structure explicit

Changes:
- keep `FROZEN_V1_REGISTRY` as the built-in registry
- add a public library-spec object wrapping it
- thread that library spec through normalization and reconciliation APIs
- do not change the built-in nodes yet

Expected result:
- the reconciler still behaves the same
- the built-in v1 node set is treated as a library, not as the reconciler

### Phase 2: Move backend binding logic behind registries

Goal:
- remove `if spec.kind == ...` from shipped backends

Changes:
- add a binding-factory registry for PySide6
- add a binding-factory registry for tkinter
- make `_PySideBackend.create_binding(...)` dispatch through that registry
- make `_TkBackend.create_binding(...)` dispatch through that registry
- keep backend-level `can_reuse(...)`, but allow per-kind specialization

Expected result:
- adding a new semantic kind to a backend is a registration change, not a
  backend method rewrite

### Phase 3: Add explicit library identity on UI elements

Goal:
- prevent collisions when two libraries use the same `kind` string

Changes:
- add `library_id` or `descriptor_key` support on `UIElement` metadata
- normalize using `(library_id, kind)` or `descriptor_key`
- keep a compatibility path for the current simple `kind` lookup

Expected result:
- multiple libraries can coexist without string collisions

### Phase 4: Public UI library authoring API

Goal:
- let third parties build semantic libraries intentionally

Changes:
- expose public constructors/helpers for:
  - prop specs
  - event specs
  - node descriptors
  - library specs
  - backend binding registries
- document how to assemble a minimal library

Expected result:
- third-party libraries can define new semantic kinds without editing PyRolyze


## Normalization Rules

The normalization layer should stay responsible for:

- turning `UIElement` instances into `UiNodeSpec`
- validating props and events against descriptors
- applying defaults
- deriving stable node ids

The normalization layer should not:

- instantiate widgets
- decide backend-specific reuse policy
- interpret author-level hook behavior

The current `normalize_ui_inputs(...)` function is already close to this.


## Identity Rules

The current identity model is sound and should be preserved:

- owner slot id
- region index
- optional key path

Instance metadata may contribute to identity, but only in a controlled way.

Recommended rules:

- `slot_id` and `call_site_id` remain normalization hints
- identity-affecting props are still declared by descriptors
- `key_parts` metadata may extend key path, but should not bypass descriptor
  rules


## Relationship To `call_native(...)`

This plan does not eliminate `call_native(...)`.

Current interpretation:

- `call_native(...)` remains the intrinsic escape hatch that emits `UIElement`
  instances directly from transformed code
- those `UIElement` instances are then normalized and reconciled

That means the generic reconciler still benefits from this plan even if
`call_native(...)` remains available.

Open question for later:

- should all UI libraries eventually target the semantic descriptor path first,
  with `call_native(...)` only as the final backend escape hatch?

That question is deferred.


## Testing Plan

### Phase 1 tests

- existing reconciliation tests should remain unchanged
- add tests that reconcile using an explicitly provided registry rather than
  relying on `FROZEN_V1_REGISTRY`

### Phase 2 tests

- backend tests should prove the shipped adapters no longer contain per-kind
  create logic outside the binding registry
- add a fake backend/library test with one custom kind to prove registration
  works

### Phase 3 tests

- add tests for `UIElement` metadata-driven descriptor selection
- add collision tests for two libraries with same local `kind` name

### Phase 4 tests

- add an end-to-end third-party-library fixture:
  - custom descriptor registry
  - custom backend binding registry
  - one rendered custom widget kind


## Is This Plan Still Appropriate After The Pull?

Yes.

The recent pulled changes make the plan more concrete:

- `UIElement` already has instance metadata fields
- `normalize_ui_inputs(...)` already consumes instance metadata for identity
- `UiOwnerCommitState` already tracks backend identity

Those changes support this direction.

The main thing that has not changed is the actual blocker:

- backends still hard-code supported kinds

So the plan is still appropriate, but it should now be executed against the
current richer `UIElement` shape instead of the earlier minimal one.


## Future Proposals

- per-kind backend reuse strategies beyond `can_reuse(current, next_spec)`
- descriptor-level prop coercion hooks
- descriptor-level child normalization hooks
- library namespaces baked into `UiNodeId`
- generated helper constructors from descriptor registries
- a first-party semantic UI library package separate from core runtime
