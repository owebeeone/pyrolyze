# Mount Point Component Design

## Purpose

This document proposes a cleaner model for handling PyRolyze components that
produce runtime-managed native values and attach them to specific native API
sites.

This replaces the earlier tendency to think in terms of:

- one implicit child list per mounted object
- special-case deferred parameter plumbing
- widget-only attachment semantics

Instead, the model is:

- ordinary retained props remain ordinary props
- object attachment happens through explicit mount points
- produced components declare what native value family they produce


## Raw Problem

PyRolyze already handles ordinary retained UI state well:

- component execution
- `UIElement` emission
- backend create/update/remount/dispose

The missing piece is attachment of produced native objects through specific
parent API sites such as:

- `setMenu(...)`
- `setCornerWidget(...)`
- `setCentralWidget(...)`
- `Menu.add_cascade(..., menu=...)`
- `Text.window_create(..., window=...)`
- `Notebook.add(child, ...)`

Those are not ordinary props and they are not well modeled as one implicit
child list.


## Core Idea

Backends should expose **mount points**.

A mount point is a named attachment site on a native parent API surface.

Examples:

- `QMainWindow.setCentralWidget`
- `QAbstractButton.setMenu`
- `QTabWidget.setCornerWidget`
- `tkinter.Menu.add_cascade`
- `tkinter.Text.window_create`
- `ttk.Notebook.add`

PyRolyze source selects a mount point explicitly:

```python
@pyrolyze[QMenu]
def CQMenu(*, text: str) -> None:
    ...


@pyrolyze
def panel() -> None:
    with mount(corner_widget(corner=Qt.TopLeftCorner)):
        CQMenu(text="Top Left")
```

This means:

- `CQMenu` produces a managed native `QMenu`
- the current mount scope selects the parent-relative `corner_widget` mount
  point
- `corner=...` is a mount-time parameter
- the emitted object is attached through that mount point


## Phase-1 Status

The phase-1 mount design should be treated as frozen enough to implement on top
of the mountable engine path.

Resolved for phase 1:

- source syntax uses `mount(...)`, not `mount[...]`
- selectors are runtime values
- `mount(*sels)` is valid
- selector params belong to selector terms, not to the outer `mount(...)`
- selector choice is left-to-right, first viable wins
- later selectors are not materialized if an earlier selector wins
- `default` and `no_emit` are special selector values
- `no_emit` is only valid as the sole selector term
- explicit mount scopes lower to retained `MountDirective` nodes
- parent-side flattening resolves selector scopes into concrete `MountState`
- implementation should target the mountable engine path, not the legacy
  `ui_nodes.py` path

Not yet implemented is not the same as undecided. The following are phase-1
implementation tasks, not open design questions:

- compiler lowering for `mount(...)`
- retained emitted-tree support for `MountDirective`
- parent-side selector flattening
- rerender/remount behavior when a retained mount directive changes its winning
  selector
- diagnostics around explicit selector failure paths


## Canonical Current Child Interface

The existing reconciler already has one implicit mount point:

- the ordinary ordered child list

Today that is spread across backend bindings as:

- `place_child(child, index)`
- `detach_child(child)`
- `dispose()`

Conceptually, that should be treated as one built-in ordered mount point with a
canonical interface.

Suggested conceptual shape:

```python
@dataclass(frozen=True, slots=True)
class OrderedMountOps:
    name: str

    def accepts(self, parent_binding: object) -> bool: ...
    def sync(
        self,
        parent_binding: object,
        values: Sequence[object],
    ) -> None: ...

    def place(self, parent_binding: object, child_value: object, index: int) -> None: ...
    def detach(self, parent_binding: object, child_value: object) -> None: ...
```

`sync(...)` is the preferred API.

Meaning:

- the caller provides the full desired ordered state for that mount instance
- the backend may implement `sync(...)` directly for efficiency
- otherwise PyRolyze provides a standard fallback algorithm using
  `place(...)` and `detach(...)`

For the current built-in child list, that means:

- `[child_0, child_1, ...]`

For the current generic widget-children behavior, this means:

- Qt
  - direct `sync(...)` can optimize layout ordering
  - fallback uses layout insertion/removal

- tkinter
  - direct `sync(...)` can optimize pack ordering
  - fallback uses pack ordering plus `pack_forget`

So the reconciler can think of current children as:

- one built-in mount point named something like `standard` or `base`
- cardinality `ordered`
- accepted type `widget-like`
- no mount parameters

This gives a clean bridge between:

- the existing child-list reconciler logic
- future explicit mount points

In other words, current child handling is not a separate special mechanism. It
is just the first built-in mount point.


## What Stays Ordinary

Most non-fundamental-looking APIs do **not** need a special produced-object
mechanism.

These remain ordinary retained props or grouped method-backed props:

- `QSize`, `QPoint`, `QRect`
- `QDate`, `QTime`, `QDateTime`
- `QColor`, `QBrush`, `QFont`, `QIcon`
- enums and flags
- grouped value methods such as `setRange(min, max)` or `setSortIndicator(...)`

If user code passes a new value, the normal `UIElement` retention/update path
handles it.

So the mount model is for **object attachment**, not for every rich argument
type.


## Produced Component Types

PyRolyze components need a declared produced native value type.

Working source proposal:

```python
T = TypeVar("T")


class PyrolyzeComponent(Generic[T]):
    ...
```

This should be modeled with a decorator object:

```python
T = TypeVar("T")


class WidgetResult:
    """Default produced type for bare @pyrolyze components."""


class PyrolyzeDecorator:
    def __call__(self, fn: Callable[..., Any]) -> PyrolyzeComponent[WidgetResult]:
        ...

    def __getitem__(self, produced_type: type[T]) -> Callable[[Callable[..., Any]], PyrolyzeComponent[T]]:
        ...


pyrolyze = PyrolyzeDecorator()
```

So source can be:

```python
@pyrolyze
def CButton(...) -> None:
    ...
```

Bare `@pyrolyze` means:

- default produced type is widget-like

Explicit form:

```python
@pyrolyze[QMenu]
def CQMenu(...) -> None:
    ...
```

means:

- this component produces a `QMenu`

The compiler should record that type in component metadata so both compile-time
and runtime checks can use it.

Suggested metadata addition:

```python
@dataclass(frozen=True, slots=True)
class ComponentMetadata(Generic[P]):
    name: str
    _func: Callable[..., None]
    packed_kwargs: bool = False
    packed_kwarg_param_names: tuple[str, ...] = ()
    emitted_type: TypeRef | None = None
```

Working rules:

- bare `@pyrolyze`
  - `emitted_type = TypeRef("WidgetResult", WidgetResult)`
- `@pyrolyze[QMenu]`
  - `emitted_type = TypeRef("QMenu", QMenu)`

This is likely required for the mount-point model, because mount-point
compatibility checks depend on knowing what produced type a component emits.


## Mount Source Forms

### Compile-time checked form

```python
with mount(menu, default, corner_widget(corner=Qt.TopLeftCorner)):
    CQMenu(text="Top Left")
```

Meaning:

- `mount(...)` accepts one or more selector terms
- each selector term may carry its own runtime params
- selectors are tried left-to-right for each emitted child
- the first viable selector wins
- later selectors are not materialized if an earlier selector succeeds
- selector values are ordinary runtime values, not compile-time-only names

Selector terms may be:

- parent-relative selector symbols such as `menu` or `corner_widget`
- selector factory calls such as `corner_widget(corner=Qt.TopLeftCorner)`
- special symbols such as `default` and `no_emit`
- optional discoverable/token forms such as
  `Qt.mounts.corner_widget(corner=Qt.TopLeftCorner)`
- runtime selector values held in state or variables
- splatted selector sequences via `mount(*sels)`

Phase-1 rule:

- the primary syntax is `mount(...)`, not `mount[...]`
- selector params belong to each selector term, not to the outer `mount(...)`
- multi-selector mount is supported in phase 1
- selection is lazy and first-match wins
- `no_emit` is only valid as the sole selector term

Important note:

- this is not driven by annotation string resolution
- `from __future__ import annotations` does not control `mount(...)`
- `mount(...)` is its own source form and compiler pass

Nested explicit mount scopes are valid:

```python
with mount(xyz):
    foo()
    with mount(abc):
        bar()
        with mount(xyz):
            zoo()
```

Rules:

- explicit selector scopes stack lexically
- the innermost selector scope wins for directly emitted children
- leaving an inner selector scope restores the previous selector scope
- if no explicit selector scope is active, the parent falls back to its
  generated default attach rules
- `mount(default)` resets selection to generated default attach behavior
- `mount(no_emit)` marks the subtree as non-emitting and should raise if
  anything emits within that subtree
- `mount(no_emit, menu)` is invalid

Dynamic selector values are valid:

```python
sel, set_sel = use_state(default)

with mount(sel, corner_widget(corner=Qt.TopLeftCorner)):
    foo()
```

and:

```python
with mount(*sels):
    foo()
```

Changing selector values across rerenders updates the same retained mount
directive slot. If the winning selector changes, the subtree is detached from
the old mount instance and reattached or remounted under the new one as
required.

Conceptually, source-level mount selectors should lower to retained structural
`MountDirective` nodes in the emitted tree rather than relying on pure ambient
runtime state. Parent-side flattening then resolves each emitted child against
the nearest enclosing selector scope.

Implementation direction:

- `mount(...)` should reuse slotted/plain-call mechanics for selector
  evaluation
- but it should do so through a new slot-backed scoped directive context, not
  by reusing `PlainCallRuntimeContext` directly as the `with` body owner
- this keeps slot retention, dirty tracking, and subtree capture in one
  retained unit

Deferred sugar, not phase 1:

- `mount(a).Widget(...)`
- `mount(a | b | c)`
- `mount(a) + mount(b)`

Phase-1 surface:

- `mount(selector)`
- `mount(selector_a, selector_b, selector_c)`
- `mount(*selectors)`
- `mount(default)`
- `mount(no_emit)`

Golden lowering target:

```python
with __pyr_ctx.open_directive(
    __pyr_SlotId(__pyr_module_id, 2, line_no=3, is_top_level=True),
    __pyr_validate_mount_selectors,
    sel,
    corner_widget(corner=Qt.TopLeftCorner),
) as __pyr_mount:
    foo()
```

That is the intended compiler/runtime direction for phase 1.

### Runtime-checked form

```python
with mount(*selector_terms):
    CQMenu(text="Dynamic")
```

Meaning:

- one or more selector terms are not known statically
- compatibility is checked at runtime
- this is an escape hatch, not the preferred path


## Concrete Schema Decisions

The remaining schema decisions should be settled like this.

### 1. Mount parameters need structure

We need to know:

- which mount parameters contribute to mount-instance identity
- which parameters are ordinary mount-time values
- which parameters are required

Suggested shape:

```python
@dataclass(frozen=True, slots=True)
class MountParamSpec:
    name: str
    annotation: TypeRef | None
    keyed: bool = False
    default_repr: str | None = None
```

Rule:

- `keyed=True`
  - contributes to `MountInstanceKey`
- `keyed=False`
  - stays in `MountState.values`

Examples:

- `QTabWidget.setCornerWidget(corner=...)`
  - `corner` is keyed
- built-in `standard`
  - no mount params
- `Notebook.add(child, text=..., image=...)`
  - tab configuration params are non-keyed unless proven otherwise


### 2. Mount point spec needs child limits

Suggested shape:

```python
@dataclass(frozen=True, slots=True)
class MountPointSpec:
    name: str
    accepted_produced_type: object
    mount_params: tuple[MountParamSpec, ...]
    min_children: int = 0
    max_children: int | None = None
    ops: object | None = None
```

Meaning:

- `accepted_produced_type`
  - the produced component type this mount point accepts
- `min_children`
  - lower bound for attached produced values in one mount instance
- `max_children`
  - upper bound for attached produced values in one mount instance

Examples:

- built-in `standard`
  - `min_children=0`
  - `max_children=None`
- `QAbstractButton.setMenu`
  - `min_children=0`
  - `max_children=1`
- `QTabWidget.setCornerWidget`
  - `min_children=0`
  - `max_children=1`


### 3. Mount state should package one concrete mount instance

Suggested shape:

```python
@dataclass(slots=True)
class MountState(Generic[T]):
    mount_point: MountPointSpec
    instance_key: MountInstanceKey
    values: dict[str, object]
    objects: list[T]
```

Meaning:

- `mount_point`
  - which attachment site family this state belongs to
- `instance_key`
  - which concrete keyed instance on the parent is being synchronized
- `values`
  - non-keyed mount-time values needed to apply the mount
- `objects`
  - the desired attached produced objects for that instance

Parent state then becomes:

```python
dict[MountInstanceKey, MountState[object]]
```


### 4. `apply(...)` is the primary API

Preferred canonical per-instance API:

```python
def apply(parent_binding: object, state: MountState[object]) -> None: ...
```

Meaning:

- the mount implementation receives one concrete mount instance
- this is the canonical runtime contract

Optional batch optimization:

```python
def sync(parent_binding: object, states: Sequence[MountState[object]]) -> None: ...
```

Meaning:

- a backend may provide a batch fast path for one mount point family
- PyRolyze does not require it
- if absent, the runtime calls `apply(...)` per instance

Lower-level fallback primitives remain:

- `place(...)`
- `detach(...)`

But they are implementation details, not the main reconciler abstraction.


### 5. Duplicate mount instances should be rejected

For one parent and one reconciliation pass, duplicate `MountInstanceKey`s should
be treated as an error unless the mount point explicitly opts into merging.

Phase-1 rule:

- duplicate mount instances are rejected

This avoids silent ambiguity in:

- keyed single mounts
- keyed ordered mounts
- accidental repeated corner/cell/tab positions

Failure mode:

- raise
- abort the current pass
- roll back the owning scope/boundary

TODO:

- verify with tests that the current per-component `pass_scope()` machinery
  actually rolls back mount-point side effects correctly when duplicate mount
  instances raise during reconciliation


## Mount Point Spec

The source form should compile to a backend-owned mount point spec.

Conceptually:

```python
@dataclass(frozen=True, slots=True)
class MountPointSpec:
    name: str
    accepted_produced_type: object
    mount_params: tuple[MountParamSpec, ...]
    min_children: int = 0
    max_children: int | None = None
    ops: object | None = None
```

And mount points should live in a backend-owned table keyed by the parent native
type:

```python
@dataclass(frozen=True, slots=True)
class ParentTypeMountRegistry:
    owner_type: type[object]
    mount_points: frozendict[str, MountPointSpec]
```

The backend resolves available mount points by parent type and normal MRO
lookup.

Examples:

- `QTabWidget.setCornerWidget`
  - accepted produced type: `QWidget`-like
  - mount params: `corner`
  - `max_children=1`

- `QAbstractButton.setMenu`
  - accepted produced type: `QMenu`
  - mount params: none
  - `max_children=1`

- `ttk.Notebook.add`
  - accepted produced type: child widget
  - mount params: tab options
  - `max_children=None`

- built-in `standard`
  - accepted produced type: widget-like
  - mount params: none
  - `max_children=None`


## Mount Instance Keys

There are two different identities here:

- mount point spec
  - what kind of attachment site this is
- mount instance key
  - which concrete attachment bucket on the parent is being synchronized

Conceptually:

```python
MountInstanceKey = tuple[object, ...]
```

Examples:

- built-in ordered children:
  - `("standard",)`

- corner widget by corner:
  - `("corner_widget", Qt.TopLeftCorner)`
  - `("corner_widget", Qt.TopRightCorner)`

- table cell widget by location:
  - `("cell_widget", row, column)`

So a parent mount surface can be thought of as:

```python
dict[MountInstanceKey, list[object]]
```

Where each mount instance key maps to the desired ordered or single-entry state
for that attachment site.

This is the clean way to represent:

- the default child list
- parameterized single mount points
- indexed/contextual mount sites


## Single Vs Ordered Mounts

Single mount points can still use the same `sync(...)` shape.

Examples:

- single mount point:
  - `[]`
  - or `[produced_value]`

- ordered mount point:
  - `[child_0, child_1]`

This means `sync(...)` can remain the canonical API for:

- the built-in ordered child mount
- single object attachment
- ordered attachment

Keyed identity still matters, but it belongs to reconciler/node identity, not to
the backend mount API. By the time `sync(...)` is called, the reconciler should
already have resolved which mounted values belong in which order.


## Type Safety

Type safety should exist in both the compiler and runtime.

### Compile-time

Given:

```python
with mount[QAbstractButton.setMenu]():
    CQMenu(...)
```

the compiler can verify:

- `CQMenu` is a `PyrolyzeComponent[QMenu]`
- `QAbstractButton.setMenu` accepts `QMenu`

and reject mismatches.

### Runtime

The runtime should still validate:

- actual mounted native value type
- backend compatibility
- mount parameter correctness

This is needed for dynamic mount targets and safety in transformed code.

Clarification:

- the produced component metadata carries a declared produced type
  - for example `QMenu`
- the mount point spec carries `accepted_produced_type`
  - for example `QMenu`
- the backend mount registry is keyed by the concrete parent type, for example
  `QTabWidget` or `QMenu`

Compatibility is simply:

```python
issubclass(produced_type, accepted_produced_type)
```

or the equivalent nominal compatibility rule the compiler/runtime uses.

That is what was previously meant by “how produced component type metadata plugs
into accepted type”.

For backend-native types, the actual Python class hierarchy should be used.

Example:

- `QMenu` carries its real Python MRO
- if a mount point accepts `QWidget`, a produced `QMenu` is compatible because
  `issubclass(QMenu, QWidget)` is true

So phase 1 should lean on actual native classes, not invent a separate subtype
system for backend-native produced values.


## Slotting And Identity

The current slotting model should be sufficient if mount points get their own
slot domains.

Conceptually, mount identity is:

- owner slot id
- mount point identity
- normal slot/key lineage within that mount point

This is enough for:

- one single attached object
- ordered attached objects
- remount/replacement of one mounted object


## Lifecycle

Produced mounted objects are runtime-managed.

That means:

- create when first emitted into the mount point
- update in place when supported
- replace/remount when required by the produced object’s own semantics
- detach when no longer emitted
- dispose when the owning reactive context dies

This lifecycle is owned by PyRolyze, not by user code.


## PySide6 Fit

The PySide6 scan shows that object-attachment APIs mostly fall into a few
manageable groups:

- single attachment with optional mount args
  - `setMenu`
  - `setCornerWidget`
  - `setCentralWidget`

- indexed/contextual attachment
  - `setCellWidget(row, column, widget)`
  - `setIndexWidget(index, widget)`
  - `setItemWidget(item, widget)`
  - `setTabButton(index, position, widget)`

- object/service attachment
  - delegates
  - pages
  - models and related service objects later

The full raw list is in
[pyside6_non_fundamental_api_report.md](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/scratch/pyside6_non_fundamental_api_report.md).


## tkinter Fit

The tkinter scan is smaller and fits the mount model even more directly:

- `Menu.add_cascade(..., menu=...)`
- `Text.window_create(..., window=...)`
- `Text.image_create(..., image=...)`
- `PanedWindow.add(child, **kw)`
- `ttk.Notebook.add(child, **kw)`
- `ttk.Notebook.insert(pos, child, **kw)`
- `ttk.OptionMenu.set_menu(...)`

The raw list is in
[tkinter_non_fundamental_api_report.md](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/scratch/tkinter_non_fundamental_api_report.md).


## Explicit Exclusions

Some APIs should not be treated as mount points.

Examples:

- `setParent(...)`
  - unsupported
- `setTabOrder(...)`
  - relation API, not mount API

Those belong to separate future mechanisms.


## Immediate Scope

This proposal is intended to cover:

- widget-like produced components
- `QMenu`
- object attachment APIs in PySide6 and tkinter
- compile-time checked mount sites
- runtime-checked dynamic mount sites

It does not try to solve:

- general relation APIs
- arbitrary graph constraints between mounted objects
- every future produced native object family in one step


## Remaining Open Decisions

These are the areas that still need genuine design decisions. They are much
smaller than the phase-1 mount model itself:

- there are no remaining blocker-level syntax questions for phase 1
- exhaustive backend mount discovery still needs to be executed and verified in
  code and tests
- non-phase-1 future relation APIs remain separate work


## Resolved Direction

The following points should now be treated as decided:

- phase-1 produced-type metadata remains `TypeRef`
- selector runtime values should be generated as concrete selector artifacts
  such as `SlotSelector` subclasses or singleton values
- exhaustive search of discoverable PySide6 mount-point-shaped APIs is required
- backend learnings remain an overlay to refine, exclude, or rename discovered
  candidates rather than replacing discovery entirely
- indexed mount points should support a batch `sync(...)` path in phase 1


## Current Interface Delta

To support the mount API as now designed, the backend mount interface should be
updated in these specific ways:

- keep `MountPointSpec` and `MountState` as the backend-facing core
- add explicit replay-shape metadata to `MountPointSpec`
  - index replay vs anchor-before replay
  - optional append fast path
  - batch-sync preference for indexed families
- add first-class mount-point learnings/override support
  - naming
  - enable/disable
  - keyed-param shaping
  - default child/default attach ordering
  - replay/sync preference overrides
- keep `ResolvedMountOps`, but drive it from generated mount metadata instead
  of runtime signature guessing where possible
- add a new selector/directive flattening layer above `MountState`
  - `mount(...)` lowers to retained `MountDirective`
  - parent-side flattening resolves selector scopes
  - flattening produces ordinary `MountState` payloads for the existing runtime

So the implementation change is:

- not a wholesale mount-runtime rewrite
- but a concrete expansion of the mount metadata model plus one new
  selector-to-`MountState` bridge layer
