# Mount Spec Implementation Plan

## Purpose

This document turns the current mount-point and selector design into an
implementation plan for the phase-1 `mount(...)` API.

It is intentionally execution-oriented:

- what stays from the current code
- what must change
- in what order it should be built
- which tests should go red/green at each stage


## Scope

This plan covers the phase-1 mount API:

- `with mount(...)`
- runtime selector values
- `mount(*sels)`
- `default`
- `no_emit`
- nested mount scopes
- flattening selector scopes into concrete `MountState`
- applying those mount states through the existing mount runtime

This plan does **not** attempt to finish:

- exhaustive PySide6 mount discovery
- tkinter mount discovery
- all backend curation questions
- relation APIs like `setTabOrder`
- higher-level adapter/catalog redesign beyond what mount needs


## Current Baseline

The repository already has the backend-side core:

- [src/pyrolyze/backends/model.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/model.py)
  - `MountPointSpec`
  - `MountState`
- [src/pyrolyze/backends/mounts.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/mounts.py)
  - `ResolvedMountOps`
  - `apply_mount_state(...)`
  - ordered replay / rebuild logic
- [src/pyrolyze/backends/mountable_engine.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/mountable_engine.py)
  - default attach behavior
  - compatibility checks

The main missing layer is above that runtime:

- no `mount(...)` compiler lowering
- no retained `MountDirective`
- no selector flattening into `MountState`

So phase 1 should be built as:

1. selector/directive layer
2. flattening layer
3. small mount-metadata expansion
4. runtime integration


## Design Contract To Preserve

These points are already decided and should not be reopened during
implementation:

- `mount(...)` is the source form, not `mount[...]`
- selectors are runtime values
- selector terms are tried left-to-right
- first viable selector wins
- later selectors are not materialized
- `default` is a soft reset to generated default attach behavior
- `no_emit` is a hard non-emitting barrier
- `no_emit` is valid only as the sole selector term
- explicit mount scopes are retained structural directive nodes
- selector scopes flatten into ordinary `MountState`
- `MountPointSpec` and `MountState` remain the backend-facing core


## Required Code Changes

## 1. Backend Model Expansion

Files:

- [src/pyrolyze/backends/model.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/model.py)

Required additions:

- `MountReplayKind`
- `append_method_name` on `MountPointSpec`
- `replay_kind` on `MountPointSpec`
- `prefer_sync` on `MountPointSpec`

Required learnings additions:

- `UiMountParamLearning`
- `UiMountPointLearning`
- `mount_point_learnings` on `UiWidgetLearning`

Why:

- ordered replay shape must come from generated metadata, not runtime guessing
- mount-point shaping must have the same overlay path as props/methods/events

Red tests first:

- model/default serialization tests
- generator tests for rendered mount-point metadata


## 2. Selector Runtime Artifacts

Files:

- likely [src/pyrolyze/api.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/api.py)
- likely [src/pyrolyze/runtime/context.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/runtime/context.py)
- possibly a new runtime module for directive types

Required artifacts:

- `SlotSelector`
- concrete selector values/factories
  - `default`
  - `no_emit`
  - generated mount selector artifacts such as `corner_widget(...)`
- `MountSelector`
- `MountDirective`

Rules:

- selectors are runtime values
- `mount(*sels)` is valid
- `mount(no_emit, menu)` must raise
- selectors should be cheap descriptors, not native mount instances

Red tests first:

- selector object/value tests
- validation tests for `no_emit`
- runtime equality/identity tests for selector values


## 3. Slot-Backed Scoped Directive Context

Files:

- [src/pyrolyze/runtime/context.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/runtime/context.py)
- compiler/runtime glue files as needed

Required runtime additions:

- a new directive context type
  - name still flexible
  - conceptually `DirectiveSlotContext`
- `open_directive(...)` on render/runtime context

Responsibilities:

- own a slot id
- evaluate selector tuple using slotted/plain-call semantics
- capture child emission inside the `with` block
- commit/rollback as one retained unit

This should reuse:

- slot identity
- dirty tracking
- retained plain-call evaluation

It should not reuse plain-call context as the child owner directly.

Red tests first:

- directive slot identity is stable across rerenders
- directive rollback restores prior committed state
- directive child capture is isolated to the `with` region


## 4. Compiler Lowering For `mount(...)`

Files:

- compiler detection/lowering under
  [src/pyrolyze/compiler/kernels/v3_14/](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/compiler/kernels/v3_14)

Required behavior:

- detect `with mount(...):`
- lower to `open_directive(...)`
- selector evaluation should piggyback on slotted/plain-call machinery
- preserve ordinary dirty-guard behavior for selector expressions

Phase-1 accepted forms:

- `with mount(menu):`
- `with mount(menu, default):`
- `with mount(*sels):`
- `with mount(sel, corner_widget(corner=Qt.TopLeftCorner))`

Phase-1 rejected forms:

- mixed `no_emit` selector lists
- old bracket syntax

Required golden:

- one explicit transformed example in tests matching the design doc golden

Red tests first:

- AST detection for `mount(...)`
- golden lowering test
- nested `mount(...)` lowering test
- dynamic selector/splat lowering test


## 5. Emitted-Tree Support

Files:

- runtime emitted-node handling
- likely [src/pyrolyze/api.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/api.py)
- likely [src/pyrolyze/runtime/context.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/runtime/context.py)

Required change:

- emitted tree must allow:
  - `UIElement`
  - `MountDirective`

Conceptual union:

```python
EmittedNode = UIElement | MountDirective
```

Responsibilities:

- `MountDirective` remains structural until flattening
- ordinary children emitted inside the directive belong to that directive node

Red tests first:

- emitted tree contains `MountDirective` rather than ambient mount flags
- nested directives preserve lexical structure


## 6. Parent-Side Flattening To `MountState`

Files:

- likely new runtime/backends helper module
- possibly [src/pyrolyze/backends/mountable_engine.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/mountable_engine.py)

Required function:

```python
def flatten_mount_directives(
    *,
    parent_spec,
    emitted_children,
) -> dict[MountInstanceKey, MountState]: ...
```

Responsibilities:

- walk nested `MountDirective`s
- track current selector list
- try selectors left-to-right for each child
- resolve to concrete mount point + mount params
- enforce `no_emit`
- merge contributions into one `MountState` per concrete mount instance

Rules:

- nearest directive wins
- leaving inner directive restores outer selector list
- if no explicit directive is active, use generated defaults
- if no selector is viable, raise a clear mount failure

Red tests first:

- `foo/bar/zoo` nested selector example from the design doc
- `default` reset behavior
- `no_emit` barrier behavior
- multi-selector first-viable behavior
- lexical merging into shared mount instance keys


## 7. Mount Runtime Integration

Files:

- [src/pyrolyze/backends/mounts.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/mounts.py)
- [src/pyrolyze/backends/mountable_engine.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/mountable_engine.py)

Required changes:

- prefer explicit mount metadata over runtime signature guessing
- use `replay_kind`
- use `append_method_name`
- use `prefer_sync`
- keep `ResolvedMountOps`
- keep existing apply/replay/rebuild/rollback behavior

Important implementation rule:

- do not rewrite the mount runtime from scratch
- adapt it to consume the richer metadata and flattened `MountState`s

Red tests first:

- index replay uses metadata, not introspection
- anchor-before replay uses metadata, not introspection
- indexed families prefer batch `sync(...)`


## 8. Generator And Learnings Integration

Files:

- [pyrolyze_tools/generate_semantic_library.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/pyrolyze_tools/generate_semantic_library.py)
- backend `learnings.py` files

Required changes:

- generator emits new mount-point fields
- learnings can refine mount-point metadata
- generated selector artifacts can be attached to generated UI-library classes

PySide6 work:

- use current mount discovery
- allow learnings to refine public mount selector names and keyed params

Tkinter work:

- at minimum, make learnings ready for future mount-point shaping
- full tkinter mount discovery remains separate follow-up work

Red tests first:

- generator output includes mount replay metadata
- learnings override mount-point name/keyed/default metadata


## 9. End-To-End Integration Path

First supported backend path:

- generated PySide6 library
- default attach rules
- one explicit mount family beyond `standard`

Recommended first explicit family:

- `QMainWindow.central_widget`
or
- `QToolButton.menu`
or
- `QMenuBar.corner_widget`

Do not start with a highly parameterized indexed mount.

After that:

- one keyed/indexed mount family
- then native example usage


## Suggested Phase Order

1. Expand backend model metadata and learnings model.
2. Add selector runtime artifacts.
3. Add slot-backed directive context.
4. Add compiler lowering for `mount(...)`.
5. Add retained `MountDirective` emitted-tree support.
6. Add parent-side flattening to `MountState`.
7. Integrate flattened mount states into existing mount runtime.
8. Emit new mount metadata from generator.
9. Prove one backend path end-to-end.

This order matters:

- it keeps the existing mount runtime usable
- it isolates compiler work from backend discovery work
- it gives a working path before exhaustive toolkit discovery


## TDD Gates

Each phase should follow strict red/green/refactor:

1. red
   - add focused test
   - prove failure
2. green
   - implement smallest change
3. refactor
   - clean names and boundaries
4. focused verify
   - rerun targeted tests
5. full verify
   - rerun full suite

Recommended focused suites by phase:

- compiler/lowering:
  - AST and golden tests
- directive/runtime:
  - context/runtime tests
- flattening:
  - mountable engine and mount runtime tests
- generation:
  - generator and generated-library tests
- integration:
  - native backend engine tests


## Risks

- mixing ambient runtime scope with retained directive nodes
  - avoid by building `MountDirective` first-class from the start
- growing the runtime with too many mount-only special cases
  - avoid by reusing slotted/plain-call machinery for selector evaluation
- leaking runtime signature introspection deeper into mount behavior
  - avoid by moving op shape into generated metadata
- trying to finish exhaustive backend discovery in the same change
  - avoid by freezing the phase-1 API first and treating discovery breadth as
    a follow-up track


## Definition Of Done For Phase 1

Phase 1 should be considered complete when:

- `with mount(...)` lowers and runs
- selectors are runtime-evaluated immutable values
- nested mount scopes work
- `default` and `no_emit` work as specified
- `MountDirective` is retained and rollback-safe
- selector scopes flatten into ordinary `MountState`
- the existing mount runtime applies those states correctly
- one generated backend path proves explicit mount selection end-to-end
- regression tests lock the behavior down


## Progress Table

| Step | Area | Status | Notes |
| --- | --- | --- | --- |
| 1 | Expand backend model metadata and learnings model | Done | Added replay-shape metadata, mount-point learnings, and generator support |
| 2 | Add selector runtime artifacts | Done | Added immutable selector values, named selector parameterization, and selector validation |
| 3 | Add slot-backed directive context | Done | Added `DirectiveSlotContext`, `open_directive(...)`, and directive rollback/no-emit enforcement |
| 4 | Add compiler lowering for `mount(...)` | Done | Added `mount(...)` lowering to `open_directive(...)`, including nested and splatted selectors |
| 5 | Add retained `MountDirective` emitted-tree support | Done | Emitted runtime tree now preserves `MountDirective` nodes structurally |
| 6 | Add parent-side flattening to `MountState` | Pending | Resolve selectors left-to-right into concrete mount buckets |
| 7 | Integrate flattened mount states into existing mount runtime | Pending | Consume flattened states through current apply/replay logic |
| 8 | Emit new mount metadata from generator | Pending | Replay kind, append path, prefer-sync, learnings overrides |
| 9 | Prove one backend path end-to-end | Pending | One generated backend with explicit mount selection fully working |
