# Host Surface Placement Cookbook

## Purpose

This cookbook shows how to define the first wave of host-surface-aware generic
backend test surfaces and what each one is expected to prove.

The goal is not to mirror every backend API detail. The goal is to make the
generator-side surface precise enough that tests can distinguish:

- structural mounted-graph shape
- host-owned placement order
- mutation-policy choice


## Terms

This document uses the following layers:

- `mount style`: the low-level mount contract such as ordered replay, anchor
  before, keyed, or single attach
- `mutation policy`: how the runtime chooses between replay, sync, or other
  legal mutation strategies
- `host surface`: the parent-owned placement surface that gives concrete order
  semantics to retained children

The first unresolved blind spot is in the third layer.


## Common Example Shape

The examples below use illustrative generator-side shapes, not final API names.

```python
MountPointProfile(
    label="example_profile",
    style=MountStyleVariant(
        label="ordered_index",
        interface=MountInterfaceKind.ORDERED,
        replay_kind=MountReplayKind.INDEX,
    ),
    mutation_policy=MountMutationPolicy.REPLAY_THEN_SYNC,
    small_delta_threshold=8,
    host_surface_style=HostSurfaceStyle(
        label="ordered_slots",
        ordered=True,
    ),
    host_placement_profile=HostPlacementProfile(
        label="widget_child",
        child_kind="widget",
        stable_slot_identity=True,
        separates_structure_from_placement=True,
    ),
)
```

The names can change during implementation. The important part is the shape:

- one concrete mount-point profile
- one mount style
- one mutation policy
- one host-surface contract


## Surface 1: Plain Ordered Widget-Child Surface

### Purpose

This is the baseline ordered host surface. It proves that the generic backend
can track structural children and host placement order when every child is a
plain widget-like child.

### Generator Definition

```python
MountPointProfile(
    label="ordered_widget_children",
    style=MountStyleVariant(
        label="ordered_index",
        interface=MountInterfaceKind.ORDERED,
        replay_kind=MountReplayKind.INDEX,
    ),
    mutation_policy=MountMutationPolicy.REPLAY_THEN_SYNC,
    small_delta_threshold=8,
    host_surface_style=HostSurfaceStyle(label="ordered_slots"),
    host_placement_profile=HostPlacementProfile(
        label="widget_child",
        child_kind="widget",
    ),
)
```

### Intended Structural Snapshot

```text
Container
  top_label
  middle_label
  bottom_label
```

### Intended Host Placement Snapshot

```text
surface: layout
  [top_label, middle_label, bottom_label]
```

### Intended Operation Log

```text
surface_attach(top_label, index=0)
surface_attach(middle_label, index=1)
surface_attach(bottom_label, index=2)
surface_place_index(middle_label, index=1)
```

### Bug Family Exposed

- wrong ordered insertion index
- stale placement state after detach/reinsert
- replay-vs-sync drift on plain widget children


## Surface 2: Nested Container Child Occupying One Stable Parent Slot

### Purpose

This is the first host-surface profile that must be strong enough to represent
the current unresolved PySide6 bug class.

The parent owns an ordered host surface. One retained child is a nested
container. That nested child occupies one slot in the parent surface while also
owning its own internal child surface.

### Generator Definition

```python
MountPointProfile(
    label="ordered_nested_container_children",
    style=MountStyleVariant(
        label="ordered_index",
        interface=MountInterfaceKind.ORDERED,
        replay_kind=MountReplayKind.INDEX,
    ),
    mutation_policy=MountMutationPolicy.REPLAY_THEN_SYNC,
    small_delta_threshold=8,
    host_surface_style=HostSurfaceStyle(label="ordered_slots"),
    host_placement_profile=HostPlacementProfile(
        label="nested_container_child",
        child_kind="nested_container",
        stable_slot_identity=True,
        separates_structure_from_placement=True,
    ),
)
```

### Intended Structural Snapshot

```text
Container
  top_label
  controls_row
    decrement_button
    count_label
    increment_button
  bottom_label
```

### Intended Host Placement Snapshot

```text
surface: layout
  [top_label, controls_row, bottom_label]

surface: controls_row.layout
  [decrement_button, count_label, increment_button]
```

### Intended Operation Log

```text
surface_attach(top_label, index=0)
surface_attach(controls_row, index=1)
surface_attach(bottom_label, index=2)
surface_attach(increment_button, index=2, owner=controls_row.layout)
```

### Bug Family Exposed

- retained nested child stays in the structural graph but drifts in parent host
  order
- stale parent-slot bookkeeping after sibling churn before the nested child
- detach/reinsert bugs that only affect nested-container children


## Surface 3: Anchor-Before Ordered Surface

### Purpose

This surface models ordered placement where the placement contract is expressed
through `before` anchors rather than direct indices.

### Generator Definition

```python
MountPointProfile(
    label="anchor_before_widget_children",
    style=MountStyleVariant(
        label="anchor_before",
        interface=MountInterfaceKind.ORDERED,
        replay_kind=MountReplayKind.ANCHOR_BEFORE,
    ),
    mutation_policy=MountMutationPolicy.ANCHOR_PRESERVING,
    host_surface_style=HostSurfaceStyle(
        label="ordered_anchor_slots",
        ordered=True,
        supports_anchor_before=True,
    ),
    host_placement_profile=HostPlacementProfile(
        label="widget_child",
        child_kind="widget",
    ),
)
```

### Intended Structural Snapshot

```text
Container
  first
  second
  third
```

### Intended Host Placement Snapshot

```text
surface: layout
  [first, second, third]
```

### Intended Operation Log

```text
surface_place_before(second, anchor=third)
surface_place_before(first, anchor=second)
```

### Bug Family Exposed

- incorrect anchor preservation
- replay logic that silently falls back to index semantics
- anchor drift when surviving siblings are retained


## Surface 4: Keyed Host Surface

### Purpose

This surface models keyed placement where retained identity matters more than
relative authoring position.

### Generator Definition

```python
MountPointProfile(
    label="keyed_widget_children",
    style=MountStyleVariant(
        label="keyed",
        interface=MountInterfaceKind.KEYED,
        replay_kind=MountReplayKind.NONE,
    ),
    mutation_policy=MountMutationPolicy.SYNC_PREFERRED,
    host_surface_style=HostSurfaceStyle(
        label="keyed_slots",
        ordered=False,
        keyed=True,
    ),
    host_placement_profile=HostPlacementProfile(
        label="widget_child",
        child_kind="widget",
    ),
)
```

### Intended Structural Snapshot

```text
Container
  item[key=a]
  item[key=b]
```

### Intended Host Placement Snapshot

```text
surface: keyed_children
  {a: item_a, b: item_b}
```

### Intended Operation Log

```text
surface_attach(item_a, key=a)
surface_attach(item_b, key=b)
surface_detach(item_a, key=a)
```

### Bug Family Exposed

- duplicate-key placement leaks
- retained identity mismatch between structural node and host surface entry
- stale keyed slot state after detach


## Surface 5: Sync-Preferred Ordered Surface

### Purpose

This surface models backends such as Tkinter `pack` where ordered placement is
real, but the preferred mutation strategy is not always index replay.

### Generator Definition

```python
MountPointProfile(
    label="sync_preferred_ordered_widgets",
    style=MountStyleVariant(
        label="ordered_no_replay",
        interface=MountInterfaceKind.ORDERED,
        replay_kind=MountReplayKind.NONE,
        prefer_sync=True,
    ),
    mutation_policy=MountMutationPolicy.SYNC_PREFERRED,
    small_delta_threshold=8,
    host_surface_style=HostSurfaceStyle(label="ordered_slots"),
    host_placement_profile=HostPlacementProfile(
        label="widget_child",
        child_kind="widget",
    ),
)
```

### Intended Structural Snapshot

```text
Container
  first
  second
  third
```

### Intended Host Placement Snapshot

```text
surface: layout
  [first, second, third]
```

### Intended Operation Log

```text
surface_sync(layout, children=[first, second, third])
```

### Bug Family Exposed

- policy mismatch between generic tests and real backend contract
- stale ordered survivors after full-surface sync
- replay-only assumptions leaking into sync-preferred surfaces


## Surface 6: Combined Structural-Surface And Host-Surface Example

### Purpose

This example is the minimum shape required to show why structural correctness
alone is not enough.

### Generator Definition

```python
MountPointProfile(
    label="combined_nested_surface",
    style=MountStyleVariant(
        label="ordered_index",
        interface=MountInterfaceKind.ORDERED,
        replay_kind=MountReplayKind.INDEX,
    ),
    mutation_policy=MountMutationPolicy.REPLAY_THEN_SYNC,
    host_surface_style=HostSurfaceStyle(label="ordered_slots"),
    host_placement_profile=HostPlacementProfile(
        label="nested_container_child",
        child_kind="nested_container",
        stable_slot_identity=True,
    ),
)
```

### Intended Structural Snapshot

```text
App
  header
  controls_row
    decrement
    count
    increment
  footer
```

### Intended Host Placement Snapshot

```text
surface: app.layout
  [header, controls_row, footer]

surface: controls_row.layout
  [decrement, count, increment]
```

### Incorrect-But-Structurally-Legal Placement Snapshot

```text
surface: app.layout
  [header, footer, controls_row]

surface: controls_row.layout
  [decrement, count, increment]
```

### Bug Family Exposed

- structural graph remains correct
- nested child remains mounted
- child interior surface remains correct
- but parent host placement order is wrong

This is the exact blind spot the current host-surface work is meant to close.


## First-Wave Assertion Requirements

Every new host-surface-aware test surface should support assertions for:

1. structural mounted graph
2. host-surface placement snapshot
3. operation log
4. concrete active mount-point profile identity
5. concrete active host-surface identity

For nested-container surfaces, tests must also be able to assert:

1. parent slot order
2. nested child structural retention
3. nested child interior surface order


## Implementation Notes

The first implementation cycle does not need every possible surface family. It
does need enough precision to make the following statement testable:

> A retained nested container child can remain structurally mounted while
> drifting to the wrong parent host slot.

That statement is the minimum bar for the host-surface expansion.
