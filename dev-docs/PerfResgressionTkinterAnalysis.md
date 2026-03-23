# Tkinter Performance Regression Analysis

## Summary

The native/generated tkinter path is still much slower than the older generic tkinter path when the window is actually shown on screen.

What is confirmed:

- The common driver in [examples/run_grid_app.py](py-rolyze/examples/run_grid_app.py) using `--backend tkinter` remains usable for a `20x20` grid.
- The native/generated driver in [examples/run_grid_app_tkinter.py](py-rolyze/examples/run_grid_app_tkinter.py) is still pathologically slow when the window is shown.
- The slow path is specifically tied to the visible native tkinter window, not just to pure Python reconciliation.

This document records what was measured, what was fixed already, what changed, and what should be done next.

## Paths Compared

### Generic tkinter path

- Runner: [examples/run_grid_app.py](py-rolyze/examples/run_grid_app.py)
- Backend: [src/pyrolyze/pyrolyze_tkinter.py](py-rolyze/src/pyrolyze/pyrolyze_tkinter.py)
- UI source: [examples/grid_app.py](py-rolyze/examples/grid_app.py)

Important characteristics:

- Uses the older `UiNode` / `mount_reconciler` path.
- Uses a custom `_pack_child(...)` reconciler with persistent pack-order state.
- Avoids unnecessary `pack_forget()` / `pack()` churn when child ordering is already correct.

### Native/generated tkinter path

- Runner: [examples/run_grid_app_tkinter.py](py-rolyze/examples/run_grid_app_tkinter.py)
- Backend host: [src/pyrolyze/pyrolyze_native_tkinter.py](py-rolyze/src/pyrolyze/pyrolyze_native_tkinter.py)
- Engine: [src/pyrolyze/backends/tkinter/engine.py](py-rolyze/src/pyrolyze/backends/tkinter/engine.py)
- Generic mount runtime: [src/pyrolyze/backends/mountable_engine.py](py-rolyze/src/pyrolyze/backends/mountable_engine.py)
- Mount operations: [src/pyrolyze/backends/mounts.py](py-rolyze/src/pyrolyze/backends/mounts.py)
- UI source: [examples/grid_app_tkinter.py](py-rolyze/examples/grid_app_tkinter.py)

Important characteristics:

- Uses the generated `TkinterUiLibrary`.
- Uses `MountableEngine` and generic `MountState` application.
- Uses explicit `pack` and `grid` mount points.

## Artifacts And Tests Added

### Performance probe

- [scratch/tkinter_grid_perf_probe.py](py-rolyze/scratch/tkinter_grid_perf_probe.py)

Purpose:

- Compare withdrawn vs shown native tkinter host behavior.
- Measure:
  - resize to `20x20`
  - toggle to grid mode
  - toggle back to row mode
- Fail fast when shown mode gets stuck.

Representative command:

```bash
uv run python scratch/tkinter_grid_perf_probe.py --samples 1 --modes withdrawn shown --wait-timeout 5 --pump-timeout 2 --sample-timeout 20 --json
```

### Regression tests

- [tests/test_examples_grid_app_tkinter.py](py-rolyze/tests/test_examples_grid_app_tkinter.py)
  - headless example behavior checks
  - large-layout time budget check
- [tests/backends/tkinter/test_tkinter_widget_engine.py](py-rolyze/tests/backends/tkinter/test_tkinter_widget_engine.py)
  - native tkinter widget-engine behavior
- [tests/test_mount_point_runtime.py](py-rolyze/tests/test_mount_point_runtime.py)
  - synthetic mount-runtime regressions for tkinter `pack`

## What Was Confirmed

### 1. The original native pack sync was too expensive

Before the latest fixes, native tkinter `pack` sync in [mounts.py](py-rolyze/src/pyrolyze/backends/mounts.py) did this:

- query all `pack`-managed children
- `pack_forget()` all of them
- `pack()` them all again

That is substantially worse than the older `_pack_child(...)` logic in [pyrolyze_tkinter.py](py-rolyze/src/pyrolyze/pyrolyze_tkinter.py), which:

- tracks stable child order
- repositions only what actually changed
- skips work entirely when the current placement already matches the desired placement

### 2. Native tkinter children were not actually parented to their logical container

Measured directly in the native path:

- child widgets were being created with `master == root`
- then later geometry-managed into the intended parent using `in_=parent`

That is a real semantic difference from the older backend and a likely source of extra visible-window layout cost.

## Fixes Already Made

### Fix 1: incremental tkinter `pack` / `grid` sync

Changed in [mounts.py](py-rolyze/src/pyrolyze/backends/mounts.py):

- `pack` sync no longer full-rebuilds all children
- removed children are detached individually
- survivors are reordered with `pack_configure(...)` only when needed
- unchanged survivors are skipped
- `grid` sync now prefers `grid_configure(...)` for surviving children instead of clearing everything

Covered by new synthetic tests in [tests/test_mount_point_runtime.py](py-rolyze/tests/test_mount_point_runtime.py).

### Fix 2: implicit `master=parent` for tkinter geometry-mounted children

Changed in [mountable_engine.py](py-rolyze/src/pyrolyze/backends/mountable_engine.py):

- when a child is attached through tkinter geometry mounts (`pack`, `grid`, `place`)
- and the child supports a `master` constructor param
- and the author did not explicitly provide one
- the runtime now injects `master=parent`

Also added runtime support for constructor-only params that are not public props, so the implicit `master` can be passed without expanding the public authored API surface.

Covered by the updated engine test in [tests/backends/tkinter/test_tkinter_widget_engine.py](py-rolyze/tests/backends/tkinter/test_tkinter_widget_engine.py).

## What Improved

The withdrawn native probe improved materially after these fixes.

Earlier withdrawn sample:

- `resize_ms`: about `495`
- `to_grid_ms`: about `554`
- `to_row_ms`: about `751`
- `total_toggle_ms`: about `1305`

Current withdrawn sample:

- `resize_ms`: about `151`
- `to_grid_ms`: about `463`
- `to_row_ms`: about `480`
- `total_toggle_ms`: about `943`

This is a real improvement, especially in resize and row-toggle cost.

## What Is Still Broken

Shown native tkinter still times out.

Current representative probe result:

- `withdrawn`: completes in under `1s` total toggle time
- `shown`: still hits `TimeoutExpired` at `20s`

That means:

- the two confirmed native regressions were real
- fixing them was necessary
- they were not sufficient

## Current Best Hypothesis

The remaining gap is likely in actual visible Tk work, not just in Python-side reconciliation.

Evidence:

- withdrawn mode is now much better
- shown mode still becomes pathological
- the failure only appears once the real window is viewable

Most likely remaining sources:

1. real Tk layout/render cost in a very deep visible widget tree
2. repeated visible updates within a single logical interaction
3. expensive `root.update_idletasks()` / `root.update()` time after reconcile completes
4. remaining widget churn not yet visible in current runtime counters

## What We Still Do Not Know

We still do not have a clean split of time between:

- PyRolyze render/reconcile time
- mount-runtime application time
- Tk event pump / visible layout time

Without that split, `cProfile` alone is not the right first tool. If most of the time is spent in Tk’s native event loop and layout work, Python-level profiling will not answer the key question.

## Recommended Next Steps

### 1. Add explicit wall-clock trace splits

Add timings around these boundaries in the native tkinter runner/host path:

- component render
- `ctx.run_pending_invalidations()`
- `reconcile_window_content(...)`
- `root.update_idletasks()`
- `root.update()`

Goal:

- determine whether the remaining `shown` cost is mostly:
  - before Tk pump
  - or inside Tk pump

This should be done first.

### 2. Build the same probe for the generic tkinter path

Add a sibling probe for [examples/run_grid_app.py](py-rolyze/examples/run_grid_app.py) with `--backend tkinter`.

Reason:

- we need apples-to-apples timing with the same measurement harness
- current knowledge of generic performance is based on manual observation, not the same automated probe

Goal:

- compare:
  - generic reconcile time
  - generic Tk pump time
  - native reconcile time
  - native Tk pump time

### 3. Add native tkinter geometry-operation counters

The old backend already has `_TK_LAYOUT_METRICS` in [pyrolyze_tkinter.py](py-rolyze/src/pyrolyze/pyrolyze_tkinter.py).

The native path should gain similar counters for:

- `pack`
- `pack_configure`
- `pack_forget`
- `grid`
- `grid_configure`
- `grid_forget`
- widget create
- widget destroy

Goal:

- prove whether visible-mode cost still correlates with hidden widget churn
- or whether Tk is simply slow to lay out the current visible tree

### 4. Compare widget-tree size between generic and native examples

The common and native examples are similar in behavior but not necessarily identical in widget structure.

We should measure:

- total widgets
- frames per cell
- labels/buttons/entries per cell
- geometry-managed widget counts by manager

Goal:

- determine whether native is paying for a meaningfully larger visible tree

### 5. Only then decide whether to use `cProfile`

If the trace split says the time is still mostly Python-side:

- use `cProfile` on the native shown worker

If the trace split says the time is mostly inside Tk pump:

- stay focused on event-loop/layout instrumentation rather than Python call profiling

## Suggested Immediate Work Order

1. Add native shown-mode trace split around reconcile vs Tk pump
2. Add generic-path comparison probe
3. Add geometry-operation counters for native path
4. Re-run `20x20` shown comparison
5. Decide whether deeper Python profiling is still needed

## Current Repo Status

At the time of writing:

- the two native tkinter correctness/perf fixes above are in the worktree
- full suite passes:
  - `363 passed, 1 warning`

Those fixes improved withdrawn native behavior but did not resolve the shown-window regression.
