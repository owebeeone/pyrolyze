# Rendering Backend Bug List

Recorded: 2026-10-04.

This is a review backlog, not authorization to implement fixes. Lifecycle
integration remains a separate workstream. The visual-ordering fix stays deferred
until the agreed lifecycle integration checkpoint.

Broader API, performance, and browser-hosting discussion is captured in the
[Rendering Backend Discussion Report](RenderingBackendDiscussionReport.md).

## Scope And Evidence

There are two author-facing rendering paths:

- Generic semantic UI, with handwritten Qt 6, Tkinter, and Dear PyGui adapters.
- Toolkit-native UI, with generated libraries and the shared mountable engine.

The generic **testing** backend is a test model, not the generic semantic UI
renderer. The unified native API is a facade over native libraries, not a third
rendering engine.

Evidence below combines current source inspection, two read-only attachment
probes, and existing failure reports. Existing GUI regression tests and full
suites were not rerun for this review. Historical timings are not current
measurements.

## Backlog Summary

| Item | Classification | Evidence / status |
| --- | --- | --- |
| 1. Retained nested Qt layout loses sibling position | Correctness bug | Existing failure analysis and regression tests; user-confirmed deferred issue |
| 2. Native Tk pack sync repeatedly queries all children | Performance defect | Current source plus deterministic synthetic probe |
| 3. Toolkit generators drop mount mutation policy | Descriptor/generator gap | Current model supports policy; real generators do not carry it through |
| 4. Native child reconciliation omits edit deltas | Unnecessary attachment churn | Current call shape plus Qt attachment-layer probe |
| 5. Visible native Tk remains slow | Unresolved performance investigation | Historical report; current cause and timing need remeasurement |
| 6. Native Qt catalog initializes eagerly | Deferred startup optimization | Existing requirements; no fresh startup profile |
| 7. Child-order bookkeeping repeatedly copies/scans the list | Possible performance bug | Source-confirmed quadratic work in the semantic delta builder; runtime impact unmeasured |
| 8. Unified Dear PyGui text fields drop explicit empty updates | Suspected correctness bug | Adapter omits empty values; update engine retains absent properties; no GUI reproduction yet |

## 1. Retained Nested Qt Layout Loses Sibling Position

After an update that changes a preceding conditional sibling, a retained bare
`QHBoxLayout` moves below a trailing label. The row's contents update correctly
and its subtree remains live, but its parent-owned visual placement is wrong.
A QWidget-wrapped row does not exhibit the same recorded failure.

Expected parent order is top label, page label, controls row, trailing label.
The recorded actual order puts the controls row after the trailing label.

Evidence and existing coverage:

- [Nested layout failure analysis](mount-surface-placement/PySide6NestedLayoutFailureAnalysis.md).
- [Native Qt regression](../tests/test_pyside6_native_host.py):
  `test_native_pyside6_conditional_nested_layout_toggle_keeps_row_above_trailing_label`.
- [Testing-backend regression](../tests/test_generic_backend_host_surface_runtime.py):
  `test_buggy_reconcile_mode_keeps_retained_nested_row_above_trailing_sibling`.
- [Recorded integration baseline](history/lifecycle-integration/PytoLifecyleIntegI0Findings.md).

The existing [host-surface placement plan](mount-surface-placement/HostSurfacePlacementPlan.md)
and [design](mount-surface-placement/HostSurfacePlacementDesign.md) describe
placement modeling. They are not evidence that the real Qt defect is fixed.
Mixed widget/layout attachment surfaces are relevant, but the exact fix is not
established by this review.

Completion criterion: an incremental update must produce the same host sibling
order as a fresh render, retain the intended objects, and preserve the nested
row's internal order. Structural graph order alone is insufficient.

## 2. Native Tk Pack Sync Repeatedly Queries All Children

This is a Pyrolyze implementation issue, not a demonstrated Tk library bug.

In [mounts.py](../src/pyrolyze/backends/mounts.py),
`_sync_child_pack_mount` queries `pack_slaves()` initially, then calls
`_pack_geometry_matches` for every retained child. That helper queries the whole
list again, materializes a tuple, and searches it with `.index(child)`.
Consequently, even a one-child append incurs quadratic child-list work.

A synthetic parent/child probe using the real synchronization helper produced:

| Retained children before one append | Full-list queries | Child references returned across queries | Pack calls |
| ---: | ---: | ---: | ---: |
| 100 | 101 | 10,200 | 1 |
| 200 | 201 | 40,400 | 1 |
| 400 | 401 | 160,800 | 1 |

The probe used no real Tk window. These are operation counts, not application
timings. They do not prove this defect explains the entire visible-window
slowdown in item 5.

The handwritten [semantic Tk adapter](../src/pyrolyze/pyrolyze_tkinter.py) caches
pack order and avoids these repeated full-list round trips for small edits. It
still performs some Python list work; this is not a claim that its entire
reconciliation path is linear.

Fix direction: snapshot placement once per synchronization and maintain an
order/index view as actual moves occur. Preserve geometry changes, anchor
ordering, and removal behavior. Do not restore full forget/repack behavior.

Coverage location: [mount runtime tests](../tests/test_mount_point_runtime.py)
already provide fake pack objects and reorder/removal checks. Add a narrow
query-count regression there rather than a fragile timing assertion.

## 3. Toolkit Generators Drop Mount Mutation Policy

The API definition already describes attachment operations and runtime policy;
the missing work is carrying that policy through the real generators.

- [Backend model](../src/pyrolyze/backends/model.py): `MountPointSpec` and
  `UiMountPointLearning` include `mutation_policy` and `small_delta_threshold`.
- [Runtime planner](../src/pyrolyze/backends/mounts.py): `choose_mount_applier`
  consumes those settings, but does not consult the older `prefer_sync` flag.
- [Qt/Tk generator](../pyrolyze_tools/generate_semantic_library.py):
  `DiscoveredMountPoint`, learning application, and mount-spec emission do not
  propagate the newer policy and threshold.
- [Dear PyGui emitter](../pyrolyze_tools/dearpygui_emit_library.py) likewise does
  not propagate those settings when constructing/emitting mount specs.
- [Testing backend](../src/pyrolyze/testing/generic_backend/engine.py) does
  propagate policy, including translating legacy sync preference. Test models
  can therefore express behavior absent from real generated descriptors.

This gap does not by itself establish the cause of item 2: a sync-only Tk pack
mount still needs an efficient synchronization implementation.

Completion criterion: explicit learning policy/threshold settings survive into
generated mount descriptors and select the intended planner behavior. Decide
and document legacy `prefer_sync` compatibility rather than silently changing
defaults. Existing rationale is in [MountableSpecModel](MountableSpecModel.md)
and [ContainerStyleGeneratorDesign](mount-style-expansion/ContainerStyleGeneratorDesign.md).

## 4. Native Child Reconciliation Omits Edit Deltas

[MountableEngine._mount_children](../src/pyrolyze/backends/mountable_engine.py)
reuses matching children but supplies only old/new mount states to
`apply_mount_state`, not the ordered edit log. The
[semantic reconciler](../src/pyrolyze/runtime/mount_reconciler.py) supplies that
log. Native replay-only mounts can consequently fall back to detaching and
reattaching the complete list for a small change.

A read-only Qt attachment-layer probe appended one widget to a layout containing
100 widgets:

| Input supplied to the shared attachment helper | Removals | Insertions |
| --- | ---: | ---: |
| Old/new states only, matching the native call shape | 100 | 101 |
| Same desired state with a single ordered append edit | 0 | 1 |

Both ended with 101 widgets. This measures attachment calls, not full-render
timings or Qt-internal complexity. Reattachment is also not the same as
destroying/recreating widget objects or rebuilding their subtrees.

Fix direction: preserve an ordered edit representation through native child
reconciliation, using the existing planner. Keep replacement, prop updates, and
attachment changes distinct. Do not assume this alone fixes mixed-surface
placement in item 1.

Completion criterion: a small native append/reorder uses bounded attachment
operations when the backend supports them, while unsupported cases retain a
correct fallback. Use canonical backend reconciliation coverage for host order
and identity, with narrow helper tests for operation counts.

## 5. Visible Native Tk Slowdown Needs Remeasurement

[The existing Tk performance report](PerfResgressionTkinterAnalysis.md) records
a large gap between the native and semantic paths for a shown 20-by-20 grid.
Earlier full forget/repack churn and incorrect implicit widget parentage were
already fixed; do not list those as still-open bugs.

The historical withdrawn-window timings improved, but the shown native window
still exceeded the report's timeout. That outcome was not reproduced during
this review. Remaining time must be separated into render, reconcile/mount,
and Tk event-pump/layout work before attributing it to one mechanism.

Existing regression:
[test_examples_grid_app_tkinter.py](../tests/test_examples_grid_app_tkinter.py),
`test_native_tkinter_grid_app_large_layout_toggle_stays_within_time_budget`.
Use supported examples/tests for reproduction; exploratory scratch scripts are
not a stable prerequisite.

## 6. Eager Native Qt Catalog Startup Is Deferred

The generated native Qt module eagerly constructs a large widget catalog.
On-demand loading remains useful, but is separate from reconciliation correctness
and attachment strategy. No fresh startup numbers were collected here.

Follow [LazyLoadingOptimizationRequirements](LazyLoadingOptimizationRequirements.md).
Lazy dictionary lookup inside the same eagerly loaded/transformed large module
does not automatically eliminate module startup cost.

Agreed sequencing: retain this as a later checkpoint after reconciliation work,
before further native catalog expansion. Preserve callable signatures and stable
cached widget definitions when introducing lazy realization.

## 7. Child-Order Bookkeeping Is A Possible Performance Bug

In [mount_reconciler.py](../src/pyrolyze/runtime/mount_reconciler.py),
`_build_standard_mount_delta` calls `builder.current_objects()` for each candidate
child. In [mounts.py](../src/pyrolyze/backends/mounts.py), that method copies the
entire working list into a tuple. Processing an unchanged list of N retained
children therefore copies N-squared reference positions, even when no attachment
edits are needed. For 1,000 children, that is 1,000 temporary tuples containing
1,000,000 reference positions in total.

The same builder's `place` and `detach` methods also scan the working list;
positional insertion shifts list entries. Many edits can add further quadratic
bookkeeping. This is separate from native Tk's repeated toolkit queries in item
2 and the native path's missing edit deltas in item 4.

Classification: possible performance bug, not a measured frame-time bottleneck.
These costs apply when this delta-building routine runs; they do not establish
that it runs on every frame or explain overall UI responsiveness. No profiling
or new behavioral tests were performed for this finding.

Next evidence: measure unchanged wide lists, single appends, removals, and
reorders at increasing sizes. Separate delta-building allocations/time from
component rendering, mutation application, and toolkit layout/paint. If fixed,
avoid full-list snapshots for single-position inspection and preserve existing
identity/order/edit semantics. A Rust implementation would still need the
algorithmic improvement; changing languages alone does not remove this work.

## 8. Unified Dear PyGui Text Fields Drop Explicit Empty Updates

In [the unified Dear PyGui adapter](../src/pyrolyze/unified/dpg.py),
`text_field(text="")` omits the `value` property because its emission is guarded
by `if text`. In [MountableEngine.update](../src/pyrolyze/backends/mountable_engine.py),
effective properties start as a copy of the previous state, and only supplied
properties are updated. An omitted property therefore retains its previous
value rather than clearing it.

Expected reproduction: mount `text_field(text="hello")`, then update the same
retained node with `text_field(text="")`. The field should become empty, but
the adapter supplies no clearing request and the old effective value remains.

Classification: suspected correctness bug supported by source inspection, not
yet reproduced against a live Dear PyGui widget. Initial mounting of an empty
field does not exercise this transition. Button and toggle labels use the same
truthiness guard and should be checked for the analogous clearing problem.

Fix direction: distinguish an explicitly empty string from an omitted property
in the unified adapter. Do not change the shared engine's absent-property
retention semantics merely to compensate for the adapter.

Completion criterion: a retained populated text field can be cleared and then
repopulated through the unified API without replacing the native object. Add
update coverage in the existing [unified tests](../tests/unified/), using the
recording Dear PyGui host where sufficient, and verify related label updates.
