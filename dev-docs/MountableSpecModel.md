# MountableSpec Model

## Purpose

This document defines the lower-level backend model that sits below
`UiLibrary`, `UiCatalog`, and source-level `UIElement` emission.

It is the runtime-side contract for:

- what a produced mountable is
- what props and grouped methods it supports
- what mount points it exposes
- how keyed mount instances are represented
- how create, update, remount, and dispose decisions are driven


## Scope

`MountableSpec` is responsible for:

- describing one mountable kind
- describing its author-settable prop and method surface
- describing its available mount points
- describing mount-point parameter roles
- describing single vs ordered attachment limits
- describing remount-triggering rules

`MountableSpec` is not responsible for:

- source-level `UiLibrary` grouping
- backend installation or catalog building
- reconciler slot identity
- source syntax like `mount[...]`


## Core Types

The backend-owned model should converge on these concepts:

```python
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
class MountParamSpec:
    name: str
    annotation: TypeRef | None
    keyed: bool = False
    default_repr: str | None = None


@dataclass(frozen=True, slots=True)
class MountPointSpec:
    name: str
    accepted_produced_type: TypeRef
    params: tuple[MountParamSpec, ...]
    min_children: int = 0
    max_children: int | None = None


MountInstanceKey = tuple[object, ...]


@dataclass(slots=True)
class MountState:
    mount_point: MountPointSpec
    instance_key: MountInstanceKey
    values: dict[str, object]
    objects: tuple[object, ...]


@dataclass(frozen=True, slots=True)
class MountableSpec:
    kind: str
    mounted_type_name: str
    props: frozendict[str, UiPropSpec]
    methods: frozendict[str, UiMethodSpec]
    mount_points: frozendict[str, MountPointSpec]
```


## Prop And Method Rules

Ordinary value-like state remains part of `UIElement.props` and is governed by:

- `UiPropSpec`
- `UiMethodSpec`

This includes:

- scalars
- enums and flags
- rich value objects like `QPoint`, `QSize`, `QColor`
- grouped method-backed value updates like `setRange(min, max)`

These are not mount points.

Remount behavior comes from prop/method mode:

- `CREATE_ONLY`
  - used at creation
  - ignored later
- `CREATE_ONLY_REMOUNT`
  - used at creation
  - remount if changed later
- `CREATE_UPDATE`
  - apply at creation and update
- `UPDATE_ONLY`
  - only meaningful after creation


## Mount Points

Mount points are for attached produced objects, not value-like props.

Examples:

- `QMainWindow.setCentralWidget`
- `QAbstractButton.setMenu`
- `QTabWidget.setCornerWidget`
- `tkinter.Text.window_create`
- `ttk.Notebook.add`

Each mount point describes:

- what produced type it accepts
- which params are keyed
- which params are non-keyed mount-time values
- how many attached objects may exist in one mount instance


## Mount Instance Keys

`MountPointSpec` defines the abstract attachment site.

`MountInstanceKey` identifies one concrete keyed instance of that site.

Examples:

- `("standard",)`
- `("corner_widget", Qt.TopLeftCorner)`
- `("cell_widget", row, column)`

Rules:

- keyed mount params contribute to `instance_key`
- non-keyed params remain in `MountState.values`
- duplicate mount instances for the same key are invalid and should fail the
  reconciliation pass


## MountState

`MountState` is the reconciler-to-backend payload for one concrete mount
instance.

It contains:

- which mount point is being applied
- which concrete keyed bucket is targeted
- which non-keyed mount args are active
- the desired ordered produced objects for that mount instance

Conceptually, the parent-side mounted state is:

```python
dict[MountInstanceKey, MountState]
```


## Standard Mount Point

The current generic ordered child list should be treated as the built-in
`standard` mount point.

That means the existing child mechanism is not special. It is just the first
ordered mount point:

- `name = "standard"`
- no extra mount params
- `max_children = None`
- accepted produced type is the default mountable/widget-like type


## Apply And Sync

The canonical runtime API is per mount instance:

```python
def apply(parent: object, state: MountState) -> None: ...
```

Backends may optionally provide:

```python
def sync(parent: object, states: Sequence[MountState]) -> None: ...
```

Rules:

- `apply(...)` is the required behavior contract
- `sync(...)` is an optional batch optimization
- lower-level `place(...)` / `detach(...)` operations remain backend
  implementation details or fallback primitives


## Produced Type Compatibility

Compatibility is checked between:

- the produced type declared by the emitting component
- the `accepted_produced_type` on the `MountPointSpec`

For backend-native types, the compatibility rule should follow the real Python
class hierarchy and `issubclass(...)`.

Examples:

- `QMenu` is compatible with a mount point that accepts `QWidget`
- a mount point that accepts `QMenu` should reject a plain `QWidget`


## Composite Mountables

Composite mountables remain first-class.

They must still appear as one node to the reconciler while internally managing
their own child attachment.

Required binding surface:

- expose one head/native value for parent attachment
- `update_props(...)`
- `place_child(...)`
- `detach_child(...)`
- `dispose()`


## Relationship To Source-Level Design

This model is the lower-level runtime companion to:

- [GenericReconcilerRequirements.md](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/dev-docs/GenericReconcilerRequirements.md)
- [GenericReconcilerApiProposal.md](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/dev-docs/GenericReconcilerApiProposal.md)
- [MountPointComponentDesign.md](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/dev-docs/MountPointComponentDesign.md)

Those documents define:

- source-level `UiLibrary` and `mount[...]` direction
- catalog/adapter/backend installation
- migration from the current widget-only implementation

This document defines the backend-facing model that those higher-level designs
assume.
