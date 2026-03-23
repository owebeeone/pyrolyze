# Tkinter UI Library Implementation Plan

## Purpose

This document turns the current tkinter backend discussion into an
implementation plan.

It is intentionally phased:

- what the current generated tkinter surface is missing
- which layers need to change
- in what order they should change
- which tests should go red/green at each stage


## Scope

This plan covers the work required to make `TkinterUiLibrary` usable as a real
author-facing backend surface for applications like
[grid_app_tkinter.py](../examples/grid_app_tkinter.py).

It includes:

- tkinter config-option property discovery
- tkinter event shaping
- general container mount discovery
- `TkinterUiLibrary` regeneration
- a native/generated example conversion path

It does **not** attempt to finish:

- exhaustive curation of every `tkinter.tix` type
- a full non-widget tkinter object model
- a large redesign of the generic reconciler
- full Studio-style parity work


## Current Baseline

The current tkinter stack already has some important pieces:

- [src/pyrolyze/backends/tkinter/engine.py](../src/pyrolyze/backends/tkinter/engine.py)
  - the runtime already supports `AccessorKind.TK_CONFIG`
- [src/pyrolyze/backends/model.py](../src/pyrolyze/backends/model.py)
  - the shared model already has `TK_CONFIG`, events, and mount-point metadata
- [pyrolyze_tools/generate_semantic_library.py](../pyrolyze_tools/generate_semantic_library.py)
  - tkinter widget discovery exists
  - tkinter setter discovery exists
  - narrow tkinter mount discovery exists for:
    - `ttk.Notebook.tab`
    - `ttk.Panedwindow.pane`
    - `tkinter.PanedWindow.pane`

What is missing is the main authored surface:

- ordinary widget options like `text`, `orient`, `menu`, `show`, `values`
  are not being generated as props
- button and entry-like event surfaces are mostly absent
- ordinary container child mounting is absent
- example apps therefore still need the older wrapper path


## Root Cause

The last widening pass solved the wrong problem for tkinter.

Current generator behavior:

- for `PySide6`, property discovery comes from Qt meta-properties
- for `tkinter`, `_extract_properties(...)` returns no real widget properties
- tkinter setter discovery only looks for methods named `set...`

That works only for a narrow subset such as:

- `ttk.Combobox.set`
- `tkinter.Scale.set`
- `ttk.Scale.set`

But ordinary tkinter widgets do not expose most authored options as setter
methods.

They expose them through:

- `configure(...)`
- `config(...)`
- `cget(...)`
- `keys()`
- constructor `**kw`

So the missing surface is mostly a config-option discovery problem, not a
"find more setters" problem.


## Design Contract To Preserve

These points should not be reopened while implementing this plan:

- tkinter authored props should primarily come from config options
- tkinter `set...` methods remain secondary enrichment, not the primary surface
- callback-style config options should become events when that is the right
  authored abstraction
- mount discovery should target ordinary container authoring, not only special
  cases like notebook tabs
- learnings remain authoritative for exclusions, renames, and shaping


## Phase Breakdown

## Phase 1. Tkinter Config-Option Property Discovery

Goal:

- generate ordinary tkinter widget options as authored props

Files:

- [pyrolyze_tools/generate_semantic_library.py](../pyrolyze_tools/generate_semantic_library.py)
- [src/pyrolyze/backends/tkinter/learnings.py](../src/pyrolyze/backends/tkinter/learnings.py)

Required work:

- add a tkinter branch to `_extract_properties(...)`
- discover config options from `configure()/keys()/cget()`
- emit `UiPropSpec` with:
  - `setter_kind=AccessorKind.TK_CONFIG`
  - `getter_kind=AccessorKind.TK_CONFIG`
- infer stable public names for options
- filter obvious junk and aliases, including likely cases such as:
  - `cnf`
  - `class`
  - `container`
  - `use`

Expected result:

- `Button` gets authored props like `text`, `command`, `state`
- `Entry` gets `show`, `width`, and similar config props
- `Frame` gets layout- and style-relevant config props
- `Menu` gets normal config props

Red tests first:

- raw tkinter extraction test for config options
- generated spec tests for:
  - `Button`
  - `Entry`
  - `Frame`
  - `Menu`


## Phase 2. Shape and Curate the Public Tkinter Surface

Goal:

- turn the raw config option set into a usable author-facing API

Files:

- [src/pyrolyze/backends/tkinter/learnings.py](../src/pyrolyze/backends/tkinter/learnings.py)
- generator shaping code in
  [pyrolyze_tools/generate_semantic_library.py](../pyrolyze_tools/generate_semantic_library.py)

Required work:

- remove low-signal or duplicate options
- normalize public naming where tkinter uses awkward option names
- decide which config options should remain normal props versus event candidates

Expected result:

- generated signatures become readable
- duplicate or junk config options are suppressed
- public surface is stable enough to author examples against

Red tests first:

- learnings overlay tests for renamed/suppressed props
- generated signature tests for representative widgets


## Phase 3. Tkinter Event Policy and Event Promotion

Goal:

- expose author-meaningful events for button and entry-like widgets

Files:

- [src/pyrolyze/backends/tkinter/learnings.py](../src/pyrolyze/backends/tkinter/learnings.py)
- generator event shaping in
  [pyrolyze_tools/generate_semantic_library.py](../pyrolyze_tools/generate_semantic_library.py)
- possibly [src/pyrolyze/backends/tkinter/engine.py](../src/pyrolyze/backends/tkinter/engine.py)
  if runtime hookup needs to grow

Required work:

- decide event policy for callback-style config options
- promote high-value callback options such as:
  - `command`
- decide how entry-like change/input events are represented
  - native config callback where available
  - binding-backed event learnings where necessary

Expected result:

- button-like widgets have a usable click event surface
- entry-like widgets have a usable change/input event surface

Red tests first:

- generated event spec tests
- runtime event hookup tests on representative widgets


## Phase 4. Tkinter Setter Enrichment

Goal:

- preserve genuine setter-backed behavior as a secondary layer

Files:

- [pyrolyze_tools/generate_semantic_library.py](../pyrolyze_tools/generate_semantic_library.py)

Required work:

- keep the existing `set...` path
- merge it cleanly with config-derived props
- make sure useful methods like:
  - `Combobox.set`
  - `Scale.set`
  remain available without conflicting with config props

Expected result:

- the config-derived surface is primary
- setter-backed affordances still exist where they are genuinely useful

Red tests first:

- generated library tests for `Combobox` and `Scale`
- no duplicate/conflicting public parameter assertions


## Phase 5. General Tkinter Container Mount Discovery

Goal:

- support ordinary child/container authoring through `TkinterUiLibrary`

Files:

- [pyrolyze_tools/generate_semantic_library.py](../pyrolyze_tools/generate_semantic_library.py)
- [src/pyrolyze/backends/tkinter/learnings.py](../src/pyrolyze/backends/tkinter/learnings.py)

Required decision:

- choose the initial ordinary container geometry model

Recommended phase-1 choice:

- default ordinary child mounting through one geometry system
- defer mixing multiple geometry systems in one first pass

This likely means:

- first-class support for one of:
  - `pack`
  - `grid`
  - `place`
- keeping `Notebook.tab` and `Panedwindow.pane`

Expected result:

- `Frame`-like containers can own children through the generated mount runtime
- authored tkinter examples no longer need the old bespoke wrapper path for
  basic composition

Red tests first:

- raw mount discovery tests
- generated mount-point metadata tests
- tkinter engine mount application tests


## Phase 6. Regenerate and Audit `TkinterUiLibrary`

Goal:

- make the generated library reflect the new discovery and shaping rules

Files:

- [src/pyrolyze/backends/tkinter/generated_library.py](../src/pyrolyze/backends/tkinter/generated_library.py)

Audit targets:

- `Button`
- `Entry`
- `Frame`
- `Label`
- `Menu`
- `Canvas`
- `Scrollbar`
- `Panedwindow`
- `Notebook`
- key `ttk` equivalents

Expected result:

- the checked-in generated tkinter surface is visibly broader and usable

Red tests first:

- generated-library regression tests
- interface manifest tests


## Phase 7. Convert `grid_app_tkinter.py` to `TkinterUiLibrary`

Goal:

- prove the new generated tkinter path with a real example

Files:

- [examples/grid_app_tkinter.py](../examples/grid_app_tkinter.py)
- relevant native/generated host files if needed

Required outcome:

- the example uses `TkinterUiLibrary`
- it does not depend on the older bespoke wrapper surface for basic controls

Out of scope for this proof:

- full PySide6 feature parity
- advanced menu parity if the backend surface is not ready
- rich custom drawing behavior

Red tests first:

- example test for the generated tkinter path
- focused runtime test covering the exact controls the example uses


## Test Strategy

Use repository TDD rules strictly:

1. add or update a focused failing test first
2. make the smallest change that turns it green
3. rerun the focused target
4. rerun the full suite before finalizing a phase

Recommended focused targets by phase:

- phase 1:
  - generator extraction/spec tests
- phase 2:
  - learnings overlay tests
- phase 3:
  - tkinter runtime event tests
- phase 4:
  - generated surface tests for setter-backed widgets
- phase 5:
  - tkinter mount runtime tests
- phase 6:
  - generated backend library regression tests
- phase 7:
  - example tests for `grid_app_tkinter.py`


## Recommended Execution Order

Do the work in this order:

1. config-option props
2. public-surface shaping
3. events
4. setter enrichment
5. container mounts
6. regenerate and inspect
7. convert the example

This order is deliberate:

- props are the biggest missing surface
- events depend on knowing which config options are props versus callbacks
- mounts should not be built before ordinary widgets are authorable
- the example should be last, after the generated surface is stable enough


## Out of Scope

This plan does not require:

1. exhaustive `tix` cleanup before ordinary widgets work
2. a complete tkinter non-widget object model
3. a redesign of the generic mount runtime
4. Studio-class parity work


## Progress

| Step | Description | Status |
| --- | --- | --- |
| 1 | Add tkinter config-option property discovery | Complete |
| 2 | Shape and curate the public tkinter prop surface | Complete |
| 3 | Add tkinter event policy and event promotion | Complete |
| 4 | Merge real setter-backed enrichment cleanly | Complete |
| 5 | Add general tkinter container mount discovery | Complete |
| 6 | Regenerate and audit `TkinterUiLibrary` | Complete |
| 7 | Convert `grid_app_tkinter.py` to `TkinterUiLibrary` | Complete |
