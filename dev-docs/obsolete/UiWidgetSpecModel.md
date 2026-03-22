# UiWidgetSpec Model

## Purpose

This document defines the lower-level `UiWidgetSpec` model that sits below
`UiLibrary`.

It treats widget handling as an independent problem:

- consume a `UIElement`
- combine it with runtime identity hints such as `slot_id` and optional
  `call_site_id`
- normalize that into node identity plus widget behavior
- create, update, reuse, remount, and dispose mounted backend nodes

This document is intentionally about widget specs and backend behavior. It does
not describe the author-facing `UiLibrary` API shape.

This is a phase-1 specialization, not the final fully-generic model for all
reactive native values. Deferred parameter content may later need to resolve to
things other than widgets, for example menu-like native values or other backend
objects with reactive lifecycle. When that happens, `UiWidgetSpec` should be
treated as one concrete specialization under a broader backend-mounted-value
model, not as the universal abstraction.


## Scope

`UiWidgetSpec` and related backend dataclasses are responsible for:

- which props exist for a widget kind
- which props are dynamic vs constructor-only vs readonly
- which multi-parameter methods exist
- how constructor-time and update-time application are handled
- whether a change causes update or remount
- whether a mounted node can be reused
- how children are attached, detached, and reordered

`UiWidgetSpec` is **not** responsible for:

- author-facing `@pyrolyze` callables
- `UiLibrary` class grouping
- compiler detection of public source APIs

`UiWidgetSpec` is also **not** the right long-term abstraction for every
deferred parameter result. It is the current abstraction for widget-backed
mountable values.


## Future Generalization Boundary

The current backend implementation is explicitly widget-oriented:

- mounted type resolution expects a widget class
- create/update/remount/dispose logic is written in terms of widgets
- placement and child attachment are written in terms of widget containers

That is correct for the current PySide6 and tkinter work.

However, the deferred-content design introduces a broader requirement:

- a named parameter may eventually resolve to a reactive native value that is
  not best modeled as a plain widget

Examples include:

- menus
- menu bars
- toolbars
- other backend-native attachable objects

So the intended layering is:

- current iteration:
  - `UiWidgetSpec`
  - widget-specific engines
  - widget-specific extraction/generation

- future generalization:
  - broader backend-mounted-value concept
  - widget specs remain one specialization of that model

This document still uses widget terminology because that is the concrete
implementation target for the current iteration.


## Conceptual Layers

There are three separate concerns:

### 1. Node identity

This is how the reconciler decides whether a node is "the same node".

Inputs may include:

- owner slot id
- emitted `slot_id`
- keyed path
- optional `call_site_id`

This is reconciler/runtime identity, not widget behavior.

### 2. Widget reuse semantics

This is how the backend decides whether a mounted widget can be reused for the
next node spec.

Inputs include:

- widget kind
- backend implementation identity
- props that affect identity

This is backend/widget-spec behavior.

### 3. Widget mutation semantics

This is how the backend applies changed values.

Inputs include:

- dynamic single-value props
- grouped method-backed values
- constructor-only values


## Proposed Core Types

The backend module should own the spec dataclasses.

```python
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from frozendict import frozendict


class PropMode(StrEnum):
    CREATE_ONLY = "create_only"
    CREATE_ONLY_REMOUNT = "create_only_remount"
    UPDATE_ONLY = "update_only"
    CREATE_UPDATE = "create_update"
    READONLY = "readonly"


class MethodMode(StrEnum):
    CREATE_ONLY = "create_only"
    CREATE_ONLY_REMOUNT = "create_only_remount"
    UPDATE_ONLY = "update_only"
    CREATE_UPDATE = "create_update"


class FillPolicy(StrEnum):
    RETAIN_EFFECTIVE = "retain_effective"
    TOOLKIT_DEFAULT = "toolkit_default"


class ChildPolicy(StrEnum):
    NONE = "none"
    ORDERED = "ordered"
    SINGLE = "single"


@dataclass(frozen=True, slots=True)
class TypeRef:
    expr: str
    value: object | None = None


@dataclass(frozen=True, slots=True)
class UiParamSpec:
    name: str
    annotation: TypeRef | None
    default_repr: str | None = None


@dataclass(frozen=True, slots=True)
class UiPropSpec:
    name: str
    annotation: TypeRef | None
    mode: PropMode
    constructor_name: str | None = None
    setter_name: str | None = None
    getter_name: str | None = None
    affects_identity: bool = False


@dataclass(frozen=True, slots=True)
class UiMethodSpec:
    name: str
    mode: MethodMode
    params: tuple[UiParamSpec, ...]
    source_props: tuple[str, ...]
    fill_policy: FillPolicy
    constructor_equivalent: bool = False


@dataclass(frozen=True, slots=True)
class UiWidgetSpec:
    kind: str
    mounted_type_name: str
    constructor_params: frozendict[str, UiParamSpec]
    props: frozendict[str, UiPropSpec]
    methods: frozendict[str, UiMethodSpec]
    child_policy: ChildPolicy
```

Enums are preferred here over freeform strings because:

- they make the allowed state space explicit
- they improve IDE support
- they reduce accidental spelling drift across backend modules
- they still serialize cleanly by value when needed

`annotation` should not be a raw `object`.

Use `TypeRef` instead:

- `expr`
  - stable textual form used for generation, display, and learnings overlays
- `value`
  - resolved Python annotation value when it can be imported safely

Examples:

- `TypeRef("list[str]", list[str])`
- `TypeRef("QPoint | None", QPoint | None)`
- `TypeRef("tuple[int, int] | None", tuple[int, int] | None)`

This keeps the spec:

- persistence-friendly
- codegen-friendly
- still useful to IDEs and runtime tooling


## Prop And Method Modes

The modes mean:

- `create_only`
  - only used during initial construction
  - ignored if changed after mount

- `create_only_remount`
  - only used during initial construction
  - if changed after mount, remount the widget

- `update_only`
  - only meaningful after mount
  - not part of initial constructor application

- `create_update`
  - valid both at creation time and update time

- `readonly`
  - not author-settable
  - may be observable or learnable from the backend

This distinction matters because PyRolyze exposes one declarative input surface
but backends often distinguish:

- constructor-only parameters
- single-value writable properties
- grouped method-based updates
- readonly values


## Identity And Reuse

Two different identities matter here.

### 1. Node identity

The reconciler tracks mounted nodes using a node id. The current runtime model
already does this in [ui_nodes.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/runtime/ui_nodes.py).

Conceptually a node id comes from:

- owner slot id
- region index
- key path

The current runtime may derive region index and key path from:

- `UIElement.slot_id`
- `UIElement.call_site_id`

This identity is about **which node instance in the tree** we are talking
about.

### 2. Widget equality / reuse

Once node identity says "same node id", the backend still has to decide:

- can the mounted widget be reused?
- or must it be replaced?

That depends on:

- widget kind
- backend implementation identity
- identity-affecting props

So:

- node identity is reconciler/runtime identity
- widget equality is backend reuse logic

They must remain separate concepts.


## Do We Really Care About `call_site_id`?

At the `UiWidgetSpec` layer: mostly no.

`call_site_id` is not widget behavior. It is a node-identity hint used during
normalization.

The current runtime uses it in two ways:

- to help derive `region_index`
- to contribute to `UiNodeId.key_path`

This matters only if slot-based identity alone is not enough to distinguish
siblings or alternate native emission sites.

So the rule should be:

- `UiWidgetSpec` should not depend on `call_site_id`
- the normalization layer may use `call_site_id` when building node ids

Practical recommendation:

- keep `call_site_id` outside `UiWidgetSpec`
- treat it as an optional normalization concern
- prefer `slot_id` plus keyed lineage as the primary identity source

If future runtime work proves that `slot_id` alone is always sufficient for
native emission identity, `call_site_id` can be reduced or removed later.

So from a widget-spec point of view:

- `slot_id` matters more
- `call_site_id` is secondary and should not leak into backend widget specs


## Creation And Update Semantics

The widget spec should support three application channels:

### 1. Constructor application

Inputs:

- constructor parameters
- `create_only`
- `create_only_remount`
- `create_update`

### 2. Dynamic single-value updates

Inputs:

- `create_update`
- `update_only`

Apply through:

- setter method
- generic property path
- backend-specific update hook

### 3. Grouped method updates

Inputs:

- `UiMethodSpec`

Examples:

- `setGeometry(x, y, width, height)`
- `setRange(minimum, maximum)`


## Partial Updates For Grouped Methods

Grouped method-backed state requires cached effective values on the mounted
binding.

Example:

- method: `setGeometry(x, y, width, height)`
- update changes only `x`
- backend must combine:
  - new `x`
  - previous `y`
  - previous `width`
  - previous `height`

This is what `fill_policy=FillPolicy.RETAIN_EFFECTIVE` is for.

Recommended meaning:

- `retain_effective`
  - fill missing values from the last known effective state for that logical
    method-backed value group
  - the effective state is cumulative across:
    - initial constructor-time values
    - initial setter/property application
    - later UI updates

- `toolkit_default`
  - fill missing values from declared/default toolkit values only if that
    behavior is well understood

For most multi-parameter setters, `retain_effective` should be the default.

PyRolyze should treat grouped method-backed values as cumulative declarative
state.

Example:

- first emission: `UIElement(..., props={x=1, y=2})`
- second emission: `UIElement(..., props={x=3})`
- effective method-backed state becomes `x=3, y=2`
- backend applies that as if the element now held both values

If the next emission is:

- `UIElement(..., props={y=2})`

and the effective state is already `x=3, y=2`, then this is a no-op for the
grouped method because the cumulative effective state did not change.

This means omission is not treated as reset. Omission means "leave the current
effective value unchanged" unless a specific widget/library chooses a different
fill policy.


## Constructor-To-Setter Mapping

Some backend values may appear in two forms:

- constructor input
- grouped setter update

Examples:

- geometry-like quartets
- range-like pairs

This mapping should be explicit.

```python
@dataclass(frozen=True, slots=True)
class ConstructorSetterMapping:
    constructor_params: tuple[str, ...]
    method_name: str
    method_params: tuple[str, ...]
    fill_policy: FillPolicy
```

This mapping is backend-owned and may be:

- discovered heuristically
- learned from prior runs
- manually corrected

The extractor should dump raw constructor surfaces and raw setter/method
surfaces separately first. Reconciliation into a normalized `UiWidgetSpec`
should happen in a second pass, because constructor and update APIs often use
different grouping:

- constructor `pos: QPoint`
- update `move(x, y)`

or:

- constructor `minimum`, `maximum`
- update `setRange(minimum, maximum)`

When both a constructor surface and a setter surface describe the same logical
state, the normalized generated API may prefer the setter-shaped surface and
treat construction as:

- minimal constructor invocation
- followed by initial setter/property application

This should be the default normalization strategy unless a value is truly
constructor-only.

The initial effective state for grouped updates should therefore be seeded from:

- constructor-time values that map into the grouped logical state
- followed by any explicit setter/property application performed during mount

Later updates operate against that effective state rather than against the raw
constructor argument list.


## Learnings Overlay

Auto-discovery will not be perfect. A persistent learnings overlay should
capture:

- constructor-to-setter mappings
- inferred prop modes
- verified grouped method semantics
- confidence and provenance

Suggested structure:

```python
@dataclass(frozen=True, slots=True)
class LearnedMapping:
    method_name: str
    constructor_params: tuple[str, ...]
    method_params: tuple[str, ...]
    fill_policy: str
    confidence: float
    source: Literal["discovered", "manual", "ai_suggested", "verified"]
    notes: str = ""
```

The learnings overlay should not be embedded in generated `UiLibrary` code. It
belongs with backend extraction and widget-spec generation, ideally as a
backend-local `learnings.py` module containing typed module-level constants.


## Deferred Reset Semantics

Resetting one member of a grouped logical value back to toolkit default is a
useful future feature, but it should not be part of the first implementation.

Possible future shape:

- a sentinel such as `MISSING`
- emitted explicitly by the author or generated API
- interpreted as "clear this member from effective state and recompute using
  toolkit default or remount rules"

For now:

- omission means "retain effective value"
- explicit values overwrite the effective value
- reset-to-default behavior is deferred


## Discovery Strategy

### Single-value props

Use:

- toolkit property metadata when available
- explicit setter/getter discovery

### Multi-parameter methods

Treat as a separate category.

Examples:

- PySide6:
  - many widgets expose methods like `setGeometry`, `setRange`, and
    `setContentsMargins`
- tkinter:
  - much smaller surface, but some methods like `Scrollbar.set(...)` still
    exist

These should become `UiMethodSpec`, not forced into ordinary `UiPropSpec`.


## Composite Widgets

`UiWidgetSpec` must also support composite backend-native widgets that appear as
one node.

The backend binding must be able to:

- expose a head widget for parent attachment
- update props on the composite widget
- place children into the correct internal host
- detach children
- dispose the whole composite

This remains within the current single child-region model.


## Relationship To Current Runtime

The current runtime already separates:

- normalized node identity
- backend binding creation
- binding updates
- child placement
- disposal

See:

- [ui_nodes.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/runtime/ui_nodes.py)
- [pyrolyze_pyside6.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/pyrolyze_pyside6.py)

This document proposes how to formalize the backend-owned spec layer beneath
that runtime shape.


## Future Proposals

Useful but not required immediately:

- automated extraction of setter/getter families into `UiMethodSpec`
- learnings-file round-tripping
- AI-assisted mapping suggestion workflow
- post-construction readback of effective values from readable properties
- backend-specific strict validation modes for unresolved mappings
