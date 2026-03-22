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


## Resolved Mount Ops

`MountPointSpec` describes the declarative surface of a mount point. The
runtime still needs one resolved callable set for the concrete parent type it
is mounting on.

Proposed shape:

```python
@dataclass(frozen=True, slots=True)
class ResolvedMountOps:
    apply: Callable[[object, MountState], None] | None = None
    sync: Callable[[object, Sequence[MountState]], None] | None = None
    place: Callable[[object, object, int], None] | None = None
    detach: Callable[[object, object], None] | None = None
    capture_snapshot: Callable[[object], object] | None = None
    restore_snapshot: Callable[[object, object], None] | None = None
```

The runtime should resolve these callables once per:

- parent mounted type
- mount point name

Suggested rule:

```python
@lru_cache
def resolve_mount_ops(
    parent_type: type[object],
    mount_point: MountPointSpec,
) -> ResolvedMountOps: ...
```

This lets the backend:

- inspect class-level API only once
- cache the discovered callable set
- choose the best delta applier for that parent/mount-point pair

The important detail is that resolution happens from the class, not from each
instance, so we do not repeatedly rebuild the same function set during normal
reconciliation.


## Transaction And Rollback Contract

Mount application is imperative. Even if the reconciler keeps immutable mount
state, the live parent object may already have been mutated by the time an
exception is raised.

So the mount adapter contract must be transactional from the reconciler's point
of view:

- committed mount state is not replaced until the pass succeeds
- staged mount deltas are dropped on failure
- any live parent mutation caused by the failed mount application must be
  rolled back before the exception escapes the owning scope

The existing scope machinery already restores staged UI emission and child slot
state. The new mount adapter layer must additionally restore imperative parent
mount-point state.

### Required Rollback Paths

Every concrete mount-point adapter must support at least one of:

1. `capture_snapshot` + `restore_snapshot`
2. replay/apply of the previously committed mount state
3. explicit parent remount fallback

If none of those are available, the mount point is not valid for the generic
reconciler.

### Preferred Rollback Order

When a mount-point update fails part-way through:

1. if a snapshot was captured, restore it
2. else if the previously committed mount state can be re-applied, do that
3. else if the parent mountable/spec explicitly allows remount-on-failure,
   remount the parent
4. else re-raise as a mount adapter contract failure

This keeps rollback deterministic and makes unsupported opaque imperative APIs
fail loudly instead of corrupting committed state silently.

### Suggested Failure Boundary

The runtime should stage mount updates inside one parent-local transaction:

```python
def apply_mount_transaction(
    parent: object,
    old_mount_states: Mapping[MountInstanceKey, MountState],
    new_mount_states: Mapping[MountInstanceKey, MountState],
    resolved_ops: ResolvedMountOps,
) -> None:
    snapshot = (
        resolved_ops.capture_snapshot(parent)
        if resolved_ops.capture_snapshot is not None
        else None
    )
    try:
        apply_mount_delta(...)
    except BaseException:
        rollback_mount_delta(
            parent=parent,
            old_mount_states=old_mount_states,
            resolved_ops=resolved_ops,
            snapshot=snapshot,
        )
        raise
```

The important rule is:

- committed mount state is swapped only after `apply_mount_delta(...)`
  completes successfully

So yes: on failure, we drop the new deltas and restore the previous committed
mount state.

### Parent-Local Scope

Rollback should be parent-local.

That means:

- if one mount point on a parent fails, all mount-point mutations on that same
  parent from the current pass are rolled back
- the failure then propagates to the owning component scope
- the existing component `pass_scope()` rollback drops the higher-level staged
  UI delta as well

This mirrors the current runtime behavior for emitted `UIElement` staging, but
adds the missing imperative parent-mutation restoration.


## Immutable Ordered Mount State

Ordered mount points need a stable immutable state object that can support:

- O(1) unchanged detection by revision
- replay of simple mutations
- fallback to full ordered `sync(...)`

The intended mutation model is builder-based:

- committed state is immutable
- one reconciliation pass creates a mutable builder from committed state
- the builder applies mount deltas
- `build()` freezes the next immutable candidate state

Proposed phase-1 shape:

```python
@dataclass(frozen=True, slots=True)
class MountedRef[T]:
    node_id: object
    value: T


@dataclass(frozen=True, slots=True)
class MountOp[T]:
    kind: Literal["place", "detach", "clear"]
    index: int | None = None
    ref: MountedRef[T] | None = None


@dataclass(frozen=True, slots=True)
class ImmutableOrderedMountState[T]:
    revision: int
    objects: tuple[MountedRef[T], ...]
    ops: tuple[MountOp[T], ...] = ()


@dataclass(slots=True)
class OrderedMountStateBuilder[T]:
    _base: ImmutableOrderedMountState[T]
    _working: list[MountedRef[T]]
    _ops: list[MountOp[T]]

    def place(self, index: int, ref: MountedRef[T]) -> None: ...
    def detach(self, ref: MountedRef[T]) -> None: ...
    def clear(self) -> None: ...
    def build(self) -> ImmutableOrderedMountState[T]: ...
```

Expected lifecycle:

- a transaction begins from one committed `ImmutableOrderedMountState`
- the runtime creates an `OrderedMountStateBuilder` from that committed state
- mutations update the builder's working sequence and append a small op log
- `build()` freezes the next immutable state candidate
- commit compares old/new revisions
- if unchanged, skip
- if changed, choose an applier strategy from the resolved mount ops

Phase-1 implementation can keep this simple:

- immutable tuple of final ordered refs
- mutable builder with a working list
- small replay log
- old state retained only for the current reconciliation boundary

This does not require a tree or rope initially. A tuple plus log is enough to
validate the model.


## Delta Applier Strategies

The runtime should not hard-code one mount update algorithm. It should choose
an applier based on the resolved mount ops that exist for a concrete mount
point.

Suggested strategy families:

### 1. Direct Sync

Use when:

- `ResolvedMountOps.sync` exists
- or the delta is large enough that replay is not worthwhile

Behavior:

- build the final ordered object list from the immutable mount state
- call `sync(parent, states)` or `sync(parent, values)`

### 2. Incremental Ordered Replay

Use when:

- `ResolvedMountOps.place` and `ResolvedMountOps.detach` exist
- delta log is small/simple

Behavior:

- replay `place(...)` / `detach(...)` from the op log
- preserve O(k) work for small mutations

### 3. Per-Instance Apply

Use when:

- the mount point is single or keyed
- `ResolvedMountOps.apply` exists

Behavior:

- call `apply(parent, state)` for each changed mount instance

### 4. Full Rebuild Fallback

Use when:

- the runtime cannot safely replay incrementally
- the mount point exposes only coarse sync/apply behavior

Behavior:

- rebuild the final mount state and apply it directly


## Strategy Selection

The runtime should choose the applier from the resolved function set, not from
hard-coded parent-type branches.

Proposed rule:

```python
@dataclass(frozen=True, slots=True)
class MountApplierPlan:
    kind: Literal[
        "direct_sync",
        "incremental_ordered_replay",
        "per_instance_apply",
        "full_rebuild_fallback",
    ]
```

Selection inputs:

- mount point cardinality
- presence/absence of `sync`
- presence/absence of `place` and `detach`
- delta log size vs final object count
- duplicate mount-instance validity

### Required Decision Order

The runtime should select the strategy in this exact order:

1. validate the mount-state set
2. skip if unchanged
3. prefer per-instance apply for single/keyed non-ordered mounts
4. prefer incremental replay for ordered mounts when a small replayable delta
   exists
5. otherwise prefer direct sync when available
6. otherwise fall back to full rebuild

Illustrative rule:

```python
def choose_mount_applier(
    *,
    mount_point: MountPointSpec,
    old_state: MountState | ImmutableOrderedMountState | None,
    new_state: MountState | ImmutableOrderedMountState,
    resolved_ops: ResolvedMountOps,
) -> MountApplierPlan:
    validate_mount_state(new_state)

    if old_state is not None and old_state == new_state:
        return MountApplierPlan(kind="skip")

    is_ordered = mount_point.max_children is None or mount_point.max_children > 1
    has_replay = resolved_ops.place is not None and resolved_ops.detach is not None
    has_sync = resolved_ops.sync is not None
    has_apply = resolved_ops.apply is not None

    if not is_ordered:
        if has_apply:
            return MountApplierPlan(kind="per_instance_apply")
        if has_sync:
            return MountApplierPlan(kind="direct_sync")
        return MountApplierPlan(kind="full_rebuild_fallback")

    if has_replay and is_small_replay_delta(old_state, new_state):
        return MountApplierPlan(kind="incremental_ordered_replay")
    if has_sync:
        return MountApplierPlan(kind="direct_sync")
    if has_replay:
        return MountApplierPlan(kind="incremental_ordered_replay")
    return MountApplierPlan(kind="full_rebuild_fallback")
```

### Meaning Of "Small Replay Delta"

Phase-1 does not need a sophisticated cost model. A simple heuristic is enough:

- replay if:
  - `len(ops) <= 8`, or
  - `len(ops) <= len(objects) // 4`
- otherwise use direct sync if available

That keeps the decision:

- cheap for small insert/move/remove edits
- simple to reason about
- easy to tune later without changing the rest of the model

### Decision Table

| Mount shape | Available ops | Suggested plan |
| --- | --- | --- |
| single/keyed | `apply` | `per_instance_apply` |
| single/keyed | no `apply`, `sync` | `direct_sync` |
| single/keyed | neither | `full_rebuild_fallback` |
| ordered | `place` + `detach`, small delta | `incremental_ordered_replay` |
| ordered | `sync`, large delta | `direct_sync` |
| ordered | no `sync`, `place` + `detach` | `incremental_ordered_replay` |
| ordered | only `apply`-like coarse ops | `full_rebuild_fallback` |

### Examples

- `standard` child list on a parent with `sync_children(...)`
  - use `direct_sync` for broad reshapes
- `standard` child list on a parent with `place(...)` / `detach(...)`
  - use `incremental_ordered_replay` for small inserts/moves/removals
- `corner_widget(top_left)` with `set_corner_widget(...)`
  - use `per_instance_apply`
- `cell_widget(row, column)` with `set_cell_widget(...)`
  - use `per_instance_apply`

This makes mount updating extensible without locking the reconciler to one
toolkit-specific algorithm.


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
