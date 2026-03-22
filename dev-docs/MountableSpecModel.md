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
- source syntax like `mount(...)`


## Phase-1 Status

The lower-level phase-1 mount model should be considered decided enough to
implement.

Resolved design points:

- explicit mount selection is represented by retained `MountDirective` nodes
- selectors are runtime values
- phase-1 produced-type metadata remains `TypeRef`
- a mount directive holds one or more selector terms
- selector terms are tried left-to-right
- first viable selector wins
- later selectors are not materialized if they are not selected
- `default` is a soft reset to generated default attach behavior
- `no_emit` is a hard non-emitting barrier
- `no_emit` is only valid as the sole selector term
- selector changes across rerenders update the same retained mount-directive
  slot and may trigger detach/reattach or remount

Still to implement, but not still to design:

- source/compiler lowering of `mount(...)`
- emitted-tree support for `MountDirective`
- selector flattening into `MountState`
- rerender handling for winning-selector changes
- end-to-end tests on the new mountable path

Still worth naming explicitly before implementation:

- the exact runtime class names for the new slot-backed scoped directive
  context types


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


## Unspecified Mount Rules

When authored source does not use an explicit `mount(...)` form, the runtime
uses generated default mount metadata instead of trying to infer the mount site
from live toolkit APIs.

There are two separate defaults:

- `default_child_mount_point_name`
  - the mount point a mountable opens for its own nested children when source
    enters `with SomeMountable(...):`
- `default_attach_mount_point_names`
  - the ordered parent-side candidate list used when a child is attached
    without an explicit `mount(...)`

Rules:

1. Entering a mountable scope opens `default_child_mount_point_name`.
2. If nested children are emitted and `default_child_mount_point_name` is
   `None`, that is a fatal error.
3. An explicit `mount(...)` scope overrides parent-side default attach
   selection for directly emitted children.
4. When no explicit `mount(...)` scope is active, the parent scans
   `default_attach_mount_point_names` in order.
5. The first candidate that:
   - accepts the child's produced type
   - requires no keyed mount params
   - has defaults for any optional non-keyed mount params
   is selected.
6. If no candidate matches, that is a fatal error.
7. Explicit `mount(...)` always overrides the generated defaults.

This keeps unspecified behavior deterministic and generator-owned.


## Explicit Mount Scope Rules

Explicit mount scopes are parent-relative attachment selector lists.

They are authored as lexical scopes, but they should not be modeled as naked
ambient runtime state. The emitted tree should retain them as structural
directive nodes until parent-side flattening resolves effective mount
assignments for concrete children.

Example:

```python
with mount(xyz):
    foo()
    with mount(abc):
        bar()
        with mount(xyz):
            zoo()
```

Rules:

1. Entering `mount(...)` creates a new explicit mount selector scope.
2. The explicit selector list applies only to directly emitted children inside
   block.
3. Nested `mount(...)` blocks are allowed; the innermost selector list wins.
4. Leaving an inner selector scope restores the previous selector scope.
5. Leaving the outermost explicit selector scope restores ordinary generated
   default attach behavior.
6. Explicit mount selectors do not change the current parent mountable. They
   only change which mount point on that parent receives directly emitted
   children.
7. Selector terms are tried left-to-right for each emitted child.
8. The first viable selector wins.
9. Unused later selectors are not materialized.
10. If no selector in the list is viable for an emitted child, that is a fatal
    error.
11. `no_emit` is only valid as the sole selector term in a `mount(...)`
    directive.
12. `mount(no_emit, menu)` and any similar mixed form are invalid.

Example:

```python
with mount(menu, default, corner(Qt.TopLeftCorner)):
    emit()
```

means:

1. try `menu`
2. if `menu` is incompatible for that child, try `default`
3. if `default` is also not viable, try `corner(Qt.TopLeftCorner)`
4. the first viable selector wins

This selection should be lazy:

- selector descriptor objects may still be constructed eagerly by normal Python
  argument evaluation rules
- do not create or materialize mount instances for later selectors unless they
  are actually selected
- an incompatible selector is simply skipped
- a selector that is never reached is never materialized
- only the winning selector contributes to `MountState`


## Runtime Selector Values

Selectors are runtime values, not compile-time-only names.

That means these are valid:

```python
sel, set_sel = use_state(default)

with mount(sel):
    foo()

set_sel(menu)
```

```python
sels = (sel, corner(Qt.TopLeftCorner))

with mount(*sels):
    foo()
```

Model:

- `menu`, `default`, and `no_emit` are selector values
- `corner(...)` is a selector factory that returns a selector value
- `mount(...)` accepts selector values at runtime
- `mount(*sels)` is valid and should be treated as runtime-only from the
  compiler's point of view
- static checking is strongest for literal/direct selector terms and weaker for
  splatted dynamic selector collections

Invalid:

```python
with mount(no_emit, menu):
    foo()
```

because `no_emit` is a hard barrier, not a fallback selector

Suggested runtime selector shape:

```python
class SlotSelector:
    pass


@dataclass(slots=True, frozen=True)
class add_corner(SlotSelector):
    corner: object
```

Rules:

- there should be one generated selector value/class per selector family
- selector classes do not need to be owner-class-specific if the selector
  semantics are the same across multiple parent types
- selector artifacts can be attached to the local generated UI-interface class
  alongside the other generated class metadata
- these selector values are what `mount(...)` consumes at runtime

Special selector forms:

1. `mount(default)`
   - resets selection to the parent's generated default attach behavior
   - nested explicit mount selectors may override it
2. `mount(no_emit)`
   - declares a hard non-emitting barrier
   - if anything emits anywhere inside that subtree, that is a fatal error
   - nested named/default mount selectors inside it are invalid because the
     subtree is explicitly non-emitting

Recommended source forms:

- `mount(corner_widget)`
- `mount(widget)`
- `mount(corner_widget(corner=Qt.TopLeftCorner))`
- `mount(menu, default)`

Optional discoverable/token form:

- `mount(Qt.mounts.corner_widget)`
- `mount(Qt.mounts.corner_widget(corner=Qt.TopLeftCorner), default)`

Both resolve to the same parent-relative selector semantics.


## Deferred Mount Syntax Sugar

The following source forms are worth remembering as plausible sugar, but they
should be treated as explicitly deferred or rejected for phase 1.

Nice but no, for now:

1. `mount(a).Widget(...)`
   - plausible sugar for:
     ```python
     with mount(a):
         with Widget(...):
             ...
     ```
   - rejected for phase 1 because it conflates selector choice with mountable
     construction and complicates lowering

2. `mount(a | b | c)`
   - syntactically attractive alternative to comma-separated selector lists
   - deferred because plain Python argument lists already cover the behavior
     and the extra operator form adds parser/compiler surface area

3. `mount[pos](x, y).mount(menu)`
   - rejected because chained selector composition is harder to reason about
     than one selector scope at a time

4. `mount(a) + mount(b)`
   - rejected because operator composition is less readable than an explicit
     selector form

Phase-1 recommendation remains:

- `mount(selector)`
- `mount(selector_a, selector_b, selector_c)`
- `mount(default)`
- `mount(no_emit)`

All other sugar should wait until the plain selector model is implemented and
validated.


## Retained Mount Directives

At emission time, explicit mount selectors should remain in the emitted tree as
structural directive nodes. They should not immediately mutate child
`UIElement`s or rely on ambient mutable runtime flags.

Conceptually:

```python
class SlotSelector:
    pass


@dataclass(frozen=True, slots=True)
class MountSelector:
    kind: Literal["named", "default", "no_emit"]
    name: str | None
    values: frozendict[str, object]


@dataclass(frozen=True, slots=True)
class MountDirective:
    slot_id: object
    selectors: tuple[SlotSelector | MountSelector, ...]
    children: tuple[EmittedNode, ...]
```

Where:

- `MountSelector(kind="no_emit", name=None, values={})`
  - means the hard non-emitting barrier form `mount(no_emit)`
- `MountSelector(kind="default", name="default", values={})`
  - means reset to parent generated default attach behavior
- `MountSelector(kind="named", name="corner_widget", values={...})`
  - means explicit selection of that parent-relative mount point

Each `MountDirective` may hold one or more selectors. Selectors are attempted
left-to-right for each emitted child, and the first viable selector wins.

In generated code, those selector terms should typically be concrete
`SlotSelector` subclasses or singleton selector values, not ad hoc tuples or
magic strings.

`MountDirective` is a retained reactive node with its own slot identity.
On rerender:

- selector values are re-evaluated
- the same mount-directive slot is updated in place
- the winning selector may change across renders
- if the winning selector changes to a different mount instance, the directive
  detaches its children from the old mount instance and reattaches or remounts
  them under the new one
- if the winning selector remains the same concrete mount instance, ordinary
  child reuse rules apply
- if the selector becomes `no_emit`, the subtree must emit nothing
- if the selector changes from `no_emit` to something else, the same directive
  slot now permits emission and attaches through the newly selected mount


## Slot-Backed Scoped Directive Runtime

`mount(...)` should not be implemented as pure ambient mutable state and should
not be modeled as a one-off special case either.

The recommended runtime shape is a new slot-backed scoped directive context.

Conceptually:

```python
@dataclass(slots=True)
class DirectiveSlotContext(ContextBase):
    slot_id: SlotId
    directive_binding: PlainCallBinding


@dataclass(frozen=True, slots=True)
class DirectiveRuntimeContext:
    slot: DirectiveSlotContext
```

And on `RenderContext`:

```python
def open_directive(
    self,
    slot_id: SlotId,
    evaluator: Callable[..., tuple[SlotSelector, ...]],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    *,
    result_shape: object | None = None,
) -> AbstractContextManager[DirectiveRuntimeContext]: ...
```

Meaning:

- `DirectiveSlotContext` owns a normal slot identity
- selector evaluation reuses the same retained plain-call/value semantics as
  `call_plain(...)`
- the directive also owns a child-emission region like a container context
- commit/rollback happens on the directive as one retained unit

This should be viewed as:

- reusing slotted/plain-call machinery for selector evaluation
- while adding scoped child capture and commit/rollback behavior

It should **not** be viewed as:

- forcing plain-call runtime context itself to become the child-emission owner
- or introducing a mount-only bespoke runtime path that cannot generalize to
  other future scoped directives


## Golden Lowering Example

Source:

```python
sel, set_sel = use_state(default)

with mount(sel, corner_widget(corner=Qt.TopLeftCorner)):
    foo()
```

Conceptual transformed shape:

```python
(__pyr_sel_dirty, __pyr_set_sel_dirty), (sel, set_sel) = __pyr_ctx.call_plain(
    __pyr_SlotId(__pyr_module_id, 1, line_no=1, is_top_level=True),
    use_state,
    default,
    result_shape=("tuple", 2),
)

with __pyr_ctx.open_directive(
    __pyr_SlotId(__pyr_module_id, 2, line_no=3, is_top_level=True),
    __pyr_validate_mount_selectors,
    sel,
    corner_widget(corner=Qt.TopLeftCorner),
) as __pyr_mount:
    foo()
```

and `open_directive(...)` is responsible for:

1. retaining the directive slot
2. evaluating and retaining the validated selector tuple
3. capturing emitted child nodes within the `with` block
4. producing a retained `MountDirective`
5. committing or rolling back the directive subtree as one unit

The important point is that mount lowering becomes:

- a slot-backed scoped directive
- not a raw ambient scope flag
- and not merely a plain-call helper with no child region

`EmittedNode` is conceptually:

```python
UIElement | MountDirective
```

This keeps mount selection:

- lexical in source
- structural in the retained emitted tree
- safe under rollback when a pass raises before commit


## Effective Mount Resolution Walkthrough

Given:

```python
with mount(xyz(x=1)):
    foo()
    with mount(abc(a=2)):
        bar()
        with mount(xyz(x=3)):
            zoo()
```

The emitted tree is conceptually:

```python
MountDirective((MountSelector("named", "xyz", {"x": 1}),), children=[
    UIElement("foo"),
    MountDirective((MountSelector("named", "abc", {"a": 2}),), children=[
        UIElement("bar"),
        MountDirective((MountSelector("named", "xyz", {"x": 3}),), children=[
            UIElement("zoo"),
        ]),
    ]),
])
```

During parent-side flattening:

1. Start with current selector = generated default attach behavior.
2. Enter outer `MountDirective` containing selector `xyz(x=1)`.
3. `foo()` resolves to effective mount assignment `xyz(x=1)`.
4. Enter `MountDirective` containing selector `abc(a=2)`.
5. `bar()` resolves to effective mount assignment `abc(a=2)`.
6. Enter inner `MountDirective` containing selector `xyz(x=3)`.
7. `zoo()` resolves to effective mount assignment `xyz(x=3)`.
8. Exit inner `xyz`, restoring selector `abc(a=2)`.
9. Exit `abc`, restoring selector `xyz(x=1)`.
10. Exit outer `xyz`, restoring generated default attach behavior.

So for the specific `zoo()` case:

- `zoo()` itself emits a plain `UIElement`
- the nearest enclosing `MountDirective` contains the selector `xyz(x=3)`
- parent-side flattening resolves that directive against the current parent's
  mount table
- the resulting child is added to the concrete `MountState` for `xyz(x=3)`

The mount therefore lives in two places by phase:

1. before flattening: on the nearest enclosing `MountDirective`
2. after flattening: in the effective `MountState` / mount assignment for that
   child


## Selector Change Across Rerenders

Example:

```python
sel, set_sel = use_state(no_emit)

with mount(sel):
    helper_only()

set_sel(default)
```

Rules:

1. The `MountDirective` slot remains the same across rerenders.
2. Its selector list is re-evaluated on each pass.
3. If the winning selector changes, the directive updates the subtree's
   effective mount assignment.
4. This may require detaching and reattaching or remounting child state,
   depending on compatibility and backend requirements.
5. If the active selector is `no_emit`, any emitted child is a fatal error.
6. If a later rerender switches from `no_emit` to a viable selector such as
   `default`, the subtree may begin emitting normally under that same
   directive slot.


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
- lower-level placement operations remain backend implementation details or
  fallback primitives


## Required Change Against Current Code

The current repository already has:

- `MountPointSpec`
- `MountState`
- `ResolvedMountOps`
- `apply/sync/place/detach` runtime behavior

Those are close enough to keep, but not quite sufficient for the selector-based
phase-1 mount design.

The required change is **not** to replace the mount-point interface wholesale.
It is to tighten it in three places:

1. generated mount-point metadata
2. mount-point learnings/overrides
3. selector/directive flattening above the existing `MountState` apply path


### 1. `MountPointSpec` Needs Explicit Op-Shape Metadata

Today the runtime still infers some ordered mount behavior from method names and
`inspect.signature(...)`.

That is no longer the right long-term interface.

The generated mount-point metadata should carry the shape explicitly.

Conceptually:

```python
class MountReplayKind(StrEnum):
    NONE = "none"
    INDEX = "index"
    ANCHOR_BEFORE = "anchor_before"


@dataclass(frozen=True, slots=True)
class MountPointSpec:
    name: str
    accepted_produced_type: TypeRef
    params: tuple[MountParamSpec, ...] = ()
    min_children: int = 0
    max_children: int | None = None
    apply_method_name: str | None = None
    sync_method_name: str | None = None
    place_method_name: str | None = None
    append_method_name: str | None = None
    detach_method_name: str | None = None
    replay_kind: MountReplayKind = MountReplayKind.NONE
    prefer_sync: bool = False
```

Meaning:

- `replay_kind=NONE`
  - no ordered replay contract is promised
- `replay_kind=INDEX`
  - ordered replay uses `place(index, value)`
- `replay_kind=ANCHOR_BEFORE`
  - ordered replay uses `place_before(value, before)`
- `append_method_name`
  - append fast path for anchor-based APIs when there is no `before` anchor
- `prefer_sync`
  - batch `sync(parent, states)` should be preferred over per-instance replay
  - especially important for indexed/keyed mount families

This change lets the runtime stop guessing ordered API shape from live methods.


### 2. Learnings Need First-Class Mount-Point Overrides

The current learnings model only shapes:

- props
- grouped methods
- events

To support the mount design cleanly, it also needs explicit mount-point
learnings.

Conceptually:

```python
@dataclass(frozen=True, slots=True)
class UiMountParamLearning:
    keyed: bool | None = None
    annotation: TypeRef | None = None
    default_repr: str | None = None


@dataclass(frozen=True, slots=True)
class UiMountPointLearning:
    public_name: str | None = None
    enabled: bool | None = None
    accepted_produced_type: TypeRef | None = None
    param_learnings: frozendict[str, UiMountParamLearning] = frozendict()
    default_child: bool | None = None
    default_attach_rank: int | None = None
    replay_kind: MountReplayKind | None = None
    append_method_name: str | None = None
    prefer_sync: bool | None = None


@dataclass(frozen=True, slots=True)
class UiWidgetLearning:
    ...
    mount_point_learnings: frozendict[str, UiMountPointLearning] = frozendict()
```

This is needed for:

- excluding bad discovered mount points
- renaming mount points to stable public selector names
- deciding keyed vs non-keyed params
- declaring default child mount points
- ordering default attach fallback
- refining replay/sync strategy

Tkinter almost certainly needs this. PySide6 will benefit from it too once the
mount-point scan becomes exhaustive.


### 3. Insert A Flattening Layer Above `MountState`

The selector design does **not** replace `MountState`.

Instead, it adds one retained structural layer above it:

- emitted tree contains `MountDirective`
- parent-side flattening resolves selector scopes
- flattening produces the existing `dict[MountInstanceKey, MountState]`
- the current mount runtime then applies those mount states

Conceptually:

```python
def flatten_mount_directives(
    *,
    parent_spec: MountableSpec,
    emitted_children: tuple[UIElement | MountDirective, ...],
) -> dict[MountInstanceKey, MountState]: ...
```

Responsibilities:

- walk nested `MountDirective` nodes
- track nearest explicit selector list
- resolve selectors left-to-right
- reject `no_emit` violations
- merge lexical contributions into concrete mount buckets
- produce one `MountState` per concrete mount instance

This is the missing bridge between:

- source/compiler `mount(...)`
- and runtime/backend `apply_mount_state(...)`


### 4. `ResolvedMountOps` Stays, But Should Become Metadata-Driven

`ResolvedMountOps` is still the right runtime shape:

```python
@dataclass(frozen=True, slots=True)
class ResolvedMountOps:
    apply: Callable[[object, MountState], None] | None = None
    sync: Callable[[object, Sequence[MountState]], None] | None = None
    place: Callable[[object, object, int], None] | None = None
    place_before: Callable[[object, object, object | None], None] | None = None
    detach: Callable[[object, object], None] | None = None
    capture_snapshot: Callable[[object], object] | None = None
    restore_snapshot: Callable[[object, object], None] | None = None
```

But resolution should primarily consume generated metadata from `MountPointSpec`
instead of discovering call shape dynamically from runtime signatures.

That means:

- keep `ResolvedMountOps`
- keep `apply/sync/place_before/detach`
- remove the need for runtime signature guessing as mount specs improve


### 5. Indexed Mounts Need Batch `sync(...)` Preference

The design already decided this, but it should be treated as an interface
constraint now.

Indexed mount families such as:

- `cell_widget(row, column)`
- `widget(row, role)`

often appear as many keyed single-child mount instances on one parent.

Applying them one-by-one is correct but not ideal. So the mount interface
should explicitly support:

- `sync(parent, states)`
- `prefer_sync=True` on those families

The runtime may still fall back to per-instance `apply(...)`, but batch sync is
the intended contract for that family.


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
    place_before: Callable[[object, object, object | None], None] | None = None
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
- O(n) diffing against a new ordered sequence when needed
- replay of simple mutations
- fallback to full ordered `sync(...)`
- lowering to either index-based or anchor-based placement APIs

The intended mutation model is builder-based:

- committed state is immutable
- one reconciliation pass creates a mutable builder from committed state
- the builder applies mount deltas
- `build()` freezes the next immutable candidate state

The key identity for ordered mount deltas should be `slot_id`, not position.
That is what lets the runtime distinguish:

- reused objects
- inserted objects
- removed objects
- moved objects

without conflating them with the current index.

Proposed shape:

```python
@dataclass(frozen=True, slots=True)
class MountedRef[T]:
    slot_id: object
    value: T
    attachment_handle: object | None = None


@dataclass(frozen=True, slots=True)
class MountOp[T]:
    kind: Literal[
        "append",
        "insert_before",
        "move_before",
        "detach",
        "clear",
    ]
    ref: MountedRef[T] | None = None
    anchor_slot_id: object | None = None


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

    def append(self, ref: MountedRef[T]) -> None: ...
    def insert_before(self, ref: MountedRef[T], anchor_slot_id: object | None) -> None: ...
    def move_before(self, slot_id: object, anchor_slot_id: object | None) -> None: ...
    def detach(self, slot_id: object) -> None: ...
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

This does not require a tree or rope initially. A tuple plus builder is enough
to validate the model.

### Complexity

The runtime should not aim for true `O(log n)` detection of arbitrary sequence
changes. That is not realistic. If a new ordered sequence is presented, the
runtime has to inspect it, which gives an `O(n)` lower bound for general diff.

The practical targets are:

- `O(1)` no-op detection when the revision or generation is unchanged
- `O(n)` sequence diff by `slot_id`
- `O(k)` replay for small known delta logs
- optionally `O(n log n)` move minimization later, for example via LIS on the
  retained old-index stream

Phase-1 implementation can keep this simple:

- immutable tuple of final ordered refs
- mutable builder with a working list
- small semantic op log
- old state retained only for the current reconciliation boundary

The important point is that the op log should be expressed in semantic
slot/anchor terms, not raw integer indices.


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

- `ResolvedMountOps` can consume fine-grained placement ops
- delta log is small/simple

Behavior:

- replay semantic ordered ops from the op log
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


## Low-Level Ordered Mount Interface

The ordered-mount runtime should expose a small semantic delta interface, then
lower that interface to the concrete backend API shape.

Recommended internal op surface:

```python
@dataclass(frozen=True, slots=True)
class OrderedMountDelta[T]:
    ops: tuple[MountOp[T], ...]
    next_state: ImmutableOrderedMountState[T]


@dataclass(frozen=True, slots=True)
class MountOp[T]:
    kind: Literal[
        "append",
        "insert_before",
        "move_before",
        "detach",
        "clear",
    ]
    ref: MountedRef[T] | None = None
    anchor_slot_id: object | None = None
```

The important rule is:

- deltas are expressed in semantic slot/anchor terms
- adapters are free to lower them to:
  - `place(index, value)`
  - `place_before(value, anchor)`
  - `insertAction(before, action)`
  - full `sync(...)`

### Resolved Ordered Ops

For ordered mounts, the adapter-facing callable set should conceptually be:

```python
@dataclass(frozen=True, slots=True)
class ResolvedMountOps:
    sync: Callable[[object, Sequence[MountState]], None] | None = None
    place: Callable[[object, object, int], None] | None = None
    place_before: Callable[[object, object, object | None], None] | None = None
    detach: Callable[[object, object], None] | None = None
```

Where:

- `place(...)` is for index-addressable parents
- `place_before(...)` is for anchor-addressable parents
- `sync(...)` is the batch fast path
- `detach(...)` removes one currently mounted child/object

### Rebuild Behavior

When incremental replay is rejected, the runtime should stop trying to be
clever.

Preferred rebuild order:

1. if `sync(...)` exists, build the final ordered state and call `sync(...)`
2. otherwise, detach everything currently mounted in that mount instance
3. then append/reinsert everything in final order using the best available
   primitive

This is deliberately blunt. The goal is to avoid a long series of widget-side
move operations that each do hidden `O(n)` work.


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
- presence/absence of index-based placement
- presence/absence of anchor-based placement
- delta log size vs final object count
- replay operation count cap
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
    has_index_replay = (
        resolved_ops.place is not None and resolved_ops.detach is not None
    )
    has_anchor_replay = (
        resolved_ops.place_before is not None and resolved_ops.detach is not None
    )
    has_sync = resolved_ops.sync is not None
    has_apply = resolved_ops.apply is not None

    if not is_ordered:
        if has_apply:
            return MountApplierPlan(kind="per_instance_apply")
        if has_sync:
            return MountApplierPlan(kind="direct_sync")
        return MountApplierPlan(kind="full_rebuild_fallback")

    if (has_anchor_replay or has_index_replay) and is_small_replay_delta(old_state, new_state):
        return MountApplierPlan(kind="incremental_ordered_replay")
    if has_sync:
        return MountApplierPlan(kind="direct_sync")
    if has_anchor_replay or has_index_replay:
        return MountApplierPlan(kind="incremental_ordered_replay")
    return MountApplierPlan(kind="full_rebuild_fallback")
```

### Meaning Of "Small Replay Delta"

Phase-1 should use a hard replay cap to avoid accidental quadratic widget-side
costs.

Recommended rule:

- replay only if all are true:
  - `len(ops) <= 8`
  - the adapter exposes replay primitives (`place_before(...)` or `place(...)`)
- otherwise rebuild

This is intentionally conservative.

Why:

- even if PyRolyze computes the delta in `O(n)`
- replaying many moves may still cost `O(n)` each inside the toolkit
- so a long replay can become effectively quadratic at the widget layer

The design goal is therefore:

- no accidental `O(n^2)` or worse in common ordered-mount updates
- accept `O(n)` or `O(n log n)` diff computation
- cap replay aggressively
- rebuild once the mutation count stops being small

### Decision Table

| Mount shape | Available ops | Suggested plan |
| --- | --- | --- |
| single/keyed | `apply` | `per_instance_apply` |
| single/keyed | no `apply`, `sync` | `direct_sync` |
| single/keyed | neither | `full_rebuild_fallback` |
| ordered | `place_before` or `place` + `detach`, small delta | `incremental_ordered_replay` |
| ordered | `sync`, large delta | `direct_sync` |
| ordered | no `sync`, replay ops only, small delta | `incremental_ordered_replay` |
| ordered | no `sync`, replay ops only, large delta | `full_rebuild_fallback` |
| ordered | only `apply`-like coarse ops | `full_rebuild_fallback` |

### Examples

- `standard` child list on a parent with `sync_children(...)`
  - use `direct_sync` for broad reshapes
- `standard` child list on a parent with `place(...)` / `detach(...)`
  - use `incremental_ordered_replay` for small inserts/moves/removals
  - use full rebuild once replay exceeds the cap
- `menu` or `toolbar` mount with `insertAction(before, action)`
  - use anchor-based replay rather than index-based replay
  - use rebuild once the anchor-based op count exceeds the cap
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
