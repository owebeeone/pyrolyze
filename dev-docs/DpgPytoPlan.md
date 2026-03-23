# DearPyGui / Pyrolyze Implementation Plan

## Purpose

This document turns the DearPyGui design into an implementation plan.

It is intentionally phased:

- establish the scratch and discovery baseline
- build the DearPyGui-specific generator path
- add the adapter/runtime layer needed to fit the generic mountable engine
- validate the generated library on representative DearPyGui families


## Scope

This plan covers:

- the DearPyGui dump workflow
- DearPyGui-specific discovery and learnings shaping
- a generated `DearPyGuiUiLibrary`
- a DearPyGui backend adapter/runtime layer
- structural mount support for the major DearPyGui families

It does not require:

- phase-1 support for every query helper
- full popup semantics
- every debug/demo/tool helper DearPyGui ships
- docking or advanced viewport features beyond the standard host lifecycle


## Current Baseline

Existing assets now live under `py-rolyze/scratch/dpg`:

- `generate_dearpygui_api_dump.py`
- `dearpygui_api_dump.py`
- `dpg_grid-example.py`
- `dpg_grid-example2.py`

The dump already tells us the shape of the problem:

- the public surface is mostly function-based rather than class-based
- there are many valid semantic item factories
- a large imperative/runtime layer must stay backend-owned
- mount structure cannot be derived from raw signatures alone


## Design Contract To Preserve

These points should not be reopened while implementing the plan:

- DearPyGui uses a dump-driven generator, not direct class discovery
- one semantic element gets one public callable surface
- context-manager aliases collapse into canonical factory-backed semantic kinds
- `parent`, `before`, `tag`, `source`, and raw lifecycle helpers are not normal
  authored props
- learnings remain authoritative for structural mount rules, renames, and
  exclusions
- DearPyGui integrates through Hydo-style adapter mountables, not through
  brittle direct function pass-through


## Phase 0. Establish The DPG Scratch Workspace

Goal:

- keep DearPyGui exploration assets together in one dedicated scratch area

Files:

- `py-rolyze/scratch/dpg/generate_dearpygui_api_dump.py`
- `py-rolyze/scratch/dpg/dearpygui_api_dump.py`
- `py-rolyze/scratch/dpg/dpg_grid-example.py`
- `py-rolyze/scratch/dpg/dpg_grid-example2.py`

Required work:

- keep the dump script and dump output co-located
- keep exploratory DPG examples in the same scratch area
- make sure embedded path references in the dump output point at the new
  location

Expected result:

- the DearPyGui exploration baseline is easy to inspect and rerun

Status:

- complete


## Phase 1. Productize DearPyGui Discovery

Goal:

- turn the exploratory dump shape into stable generator input

Files:

- `py-rolyze/pyrolyze_tools/generate_dearpygui_library.py`
- `py-rolyze/scratch/dpg/generate_dearpygui_api_dump.py`

Required work:

- define a DearPyGui-specific discovered-item model
- load either the checked-in dump or a freshly inspected runtime surface
- preserve classification, alias mapping, parameter metadata, and doc summaries
- normalize raw `add_*` factories into canonical semantic kind candidates

Expected result:

- generation no longer depends on ad hoc scratch inspection
- the DearPyGui generator has deterministic structured input

Red tests first:

- dump-loader tests
- classification-preservation tests
- alias-collapse tests
- kind-naming tests

Status:

- complete

Delivered:

- `src/pyrolyze/backends/dearpygui/discovery.py` loads the checked-in
  `scratch/dpg/dearpygui_api_dump.py`, exposes `DpgLoadedDump`,
  `DpgCanonicalMountable`, `iter_canonical_mountables`, and kind naming for
  `add_*` and `draw_*` factories
- `pyrolyze_tools/generate_dearpygui_library.py` CLI for `--print-summary` and
  `--list-shaped`
- `tests/test_dearpygui_discovery_and_learnings.py` covers load, classification,
  alias collapse, and kind naming


## Phase 2. Introduce DearPyGui Learnings

Goal:

- shape the raw discovered DearPyGui surface into a usable author-facing API

Files:

- `py-rolyze/src/pyrolyze/backends/dearpygui/learnings.py`
- `py-rolyze/pyrolyze_tools/generate_dearpygui_library.py`

Required work:

- define public kind renames where the raw factory name is too low-level
- suppress runtime-owned params such as `tag`, `parent`, `before`, `source`,
  `user_data`, and `kwargs`
- normalize `default_value` to authored `value` where appropriate
- choose semantic event names for callback-bearing item families
- define produced-family and mount-point learnings

Expected result:

- the generated DearPyGui signatures become readable and intentional
- structural and event semantics are explicit rather than guessed

Red tests first:

- learnings overlay tests
- generated signature tests for representative widgets
- prop suppression/rename regression tests

Status:

- complete

Delivered:

- `src/pyrolyze/backends/dearpygui/learnings.py` with `LEARNINGS`,
  `RUNTIME_OWNED_PARAM_NAMES`, `KINDS_DEFAULT_VALUE_AS_VALUE`, and initial mount
  metadata for `Window`, `Table`, `Plot`, and `NodeEditor`
- `src/pyrolyze/backends/dearpygui/author_shape.py` with
  `shape_canonical_mountable` (runtime param suppression, `default_value` →
  `value` where configured, callback renaming for representative kinds, mount
  point ordering)
- tests in `tests/test_dearpygui_discovery_and_learnings.py` for Button,
  InputText, Window, and NodeEditor shaping


## Phase 3. Add DearPyGui Adapter Mountables

Goal:

- create the runtime object model that lets DearPyGui fit the generic
  mountable engine

Files:

- `py-rolyze/src/pyrolyze/backends/dearpygui/items.py`
- `py-rolyze/src/pyrolyze/backends/model.py`
- possibly `py-rolyze/src/pyrolyze/backends/mountable_engine.py`

Required work:

- define DearPyGui base adapter classes
- define stable tag ownership on those adapter objects
- support configuration updates, value updates, disposal, and staging
- add explicit DearPyGui accessor behavior for config and value channels

Expected result:

- the backend can mount generated DearPyGui items as real Python objects
- DearPyGui no longer needs to be treated as a special non-mountable exception

Red tests first:

- adapter creation/disposal tests
- accessor-kind tests for config vs value updates
- tag-allocation stability tests


## Phase 4. Implement Event Wiring

Goal:

- turn DearPyGui callback parameters into real `UiEventSpec` behavior

Files:

- `py-rolyze/src/pyrolyze/backends/dearpygui/engine.py`
- `py-rolyze/src/pyrolyze/backends/dearpygui/learnings.py`
- `py-rolyze/pyrolyze_tools/generate_dearpygui_library.py`

Required work:

- map callback slots to `UiEventSpec.signal_name`
- install stable dispatchers through `configure_item(...)`
- apply payload policies per event family
- support event prop updates without recreating items

Expected result:

- author-facing handlers work through generated event parameters
- event routing is backend-owned and inspectable

Red tests first:

- button/menu activation event tests
- input/change event tests
- drag/drop event tests
- window close and node-editor delink event tests


## Phase 5. Implement Structural Mount Families

Goal:

- support ordinary and specialized DearPyGui composition through mount points

Files:

- `py-rolyze/src/pyrolyze/backends/dearpygui/items.py`
- `py-rolyze/src/pyrolyze/backends/dearpygui/learnings.py`
- `py-rolyze/pyrolyze_tools/generate_dearpygui_library.py`

Required work:

- add ordered child replay support through DearPyGui `before`/reparenting
- implement hidden staging for unattached items
- define default child and default attach ranking per family
- support the initial structural families:
  - windows and child windows
  - menus and menu bars
  - tables
  - plots and plot axes
  - node editor, nodes, and node attributes
  - theme/component entries
  - registry/resource families

Expected result:

- nested DearPyGui authoring is possible without raw `parent`/`before`
- structural constraints are generator-owned and testable

Red tests first:

- default attach ranking tests
- explicit `mount(...)` selector tests
- ordered reparent/reorder tests
- singular mount tests for menu bars and similar one-off sites


## Phase 6. Build The DearPyGui Engine Host

Goal:

- own DearPyGui lifecycle and runtime-only mutation behind a backend interface

Files:

- `py-rolyze/src/pyrolyze/backends/dearpygui/engine.py`
- host/bootstrap code where backend roots are created

Required work:

- create/destroy context
- create/setup/show viewport
- own the staging root
- route config/value/query helpers through the backend
- ensure disposal order and existence checks are safe

Expected result:

- the generated library stays author-facing only
- all DearPyGui lifecycle and imperative mutation lives in the backend host

Red tests first:

- engine lifecycle tests
- staging attach/detach tests
- dispose ordering tests
- existence-guard regression tests


## Phase 7. Generate And Audit `DearPyGuiUiLibrary`

Goal:

- check in a real generated DearPyGui library and inspect its quality

Files:

- `py-rolyze/src/pyrolyze/backends/dearpygui/generated_library.py`

Audit targets:

- `Button`
- `InputText`
- `Window`
- `MenuBar`
- `MenuItem`
- `Table`
- `TableRow`
- `Plot`
- `PlotAxis`
- `ThemeComponent`
- `NodeEditor`

Expected result:

- the generated library is broad enough to author serious examples against
- the checked-in source is readable and consistent with the existing generated
  backend libraries

Red tests first:

- generated-library regression tests
- interface manifest tests
- representative spec snapshot tests


## Phase 8. Convert Representative Examples

Goal:

- prove the generated DearPyGui path with real authored examples

Files:

- new or converted examples under `py-rolyze/examples`
- existing scratch examples under `py-rolyze/scratch/dpg` as parity references

Required work:

- author at least one ordinary window/menu example
- author at least one table or grid composition example
- author at least one value/event-heavy example

Expected result:

- DearPyGui support is validated by authored Pyrolyze code, not just metadata

Red tests first:

- focused example tests
- smoke tests that render representative example trees through the backend


## Phase 9. Full Regression And Hardening

Goal:

- finish the implementation with the repo's normal quality bar

Required work:

- rerun the focused test targets after each phase
- rerun the full suite before finalizing
- audit the generated library for noisy or accidental public surface
- audit learnings for duplicated or contradictory rules

Expected result:

- the DearPyGui backend is integrated without weakening existing backend paths


## Test Strategy

Use the repository TDD workflow strictly:

1. add or update a focused failing test first
2. make the smallest change that turns it green
3. rerun the focused target
4. rerun the full suite before finalizing a phase

Repository commands:

- focused: `uv run --with pytest --with pytest-cov pytest <test-path> -q`
- full suite: `uv run --with pytest --with pytest-cov pytest -q`

Recommended new test areas:

- `py-rolyze/tests/test_generate_dearpygui_library_tool.py`
- `py-rolyze/tests/backends/dearpygui/test_items.py`
- `py-rolyze/tests/backends/dearpygui/test_engine.py`
- `py-rolyze/tests/test_generated_backend_libraries.py`


## Recommended Execution Order

Do the work in this order:

1. productize discovery
2. add learnings
3. add adapter mountables and accessor semantics
4. add event wiring
5. add structural mount families
6. build the backend host
7. generate and audit the library
8. convert examples
9. run full regression

This order is deliberate:

- the dump shape must be stable before generation
- learnings must exist before the public API can be trusted
- the adapter/runtime layer is the main DearPyGui-specific architectural step
- events and mounts depend on the adapter layer existing
- example conversion should happen only after the generated surface stabilizes


## Out Of Scope

This plan does not require:

1. phase-1 support for all query hooks
2. raw `source` registry binding on every value widget
3. an automatically inferred popup model
4. every DearPyGui debug or tool window helper
5. advanced viewport/docking work before ordinary authoring works


## Progress

| Step | Description | Status |
| --- | --- | --- |
| 0 | Establish dedicated DPG scratch workspace | Complete |
| 1 | Productize DearPyGui discovery | Pending |
| 2 | Introduce DearPyGui learnings | Pending |
| 3 | Add DearPyGui adapter mountables | Pending |
| 4 | Implement event wiring | Pending |
| 5 | Implement structural mount families | Pending |
| 6 | Build the DearPyGui engine host | Pending |
| 7 | Generate and audit `DearPyGuiUiLibrary` | Pending |
| 8 | Convert representative examples | Pending |
| 9 | Run full regression and hardening | Pending |
