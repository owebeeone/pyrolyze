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

Status:

- complete

Delivered:

- `AccessorKind.DPG_CONFIG` / `DPG_VALUE` in `model.py` and handling in
  `mountable_engine.py`
- `backends/dearpygui/host.py` (`DpgRuntimeHost`, `RecordingDpgHost`, context
  helpers for host + slot id)
- `backends/dearpygui/items.py` adapter hierarchy (containers, window menu bar,
  table/plot/node/theme/registry families)
- `backends/dearpygui/specs.py` fixture `UiWidgetSpec` map for integration tests
- `tests/test_dearpygui_adapter_phases_3_5.py` (phase 3 scenarios)


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

Status:

- complete

Delivered:

- `backends/dearpygui/engine.py`: `connect_dpg_event_signal` (configure_item
  wiring), `DpgMountableEngine` (host + slot context, dispose, read shadow for
  DPG accessors)
- `generate_dearpygui_library.py`: `--list-fixture-spec-kinds`
- tests: button/input/window/node-editor event dispatch and payload policies


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

Status:

- complete

Delivered:

- Staging parent (`staging_tag=0`) and `move_item` tracking in
  `RecordingDpgHost`; `sync_*` / `place_child` / `detach_child` on
  `DpgContainerItem`
- `attach_menu_bar` on `DpgWindowItem`; table/plot/node/theme/registry mount
  shapes in `specs.py`
- Extended `learnings.py` mount metadata for `MenuBar`, `Menu`, `TableRow`,
  `Theme`, `ThemeComponent`, `FontRegistry`
- tests: window+menu+children, multi-family trees, `place_child` reorder,
  node+link under editor

Follow-ups (not required to mark phase 5 “done”, but still open vs the design
doc): node-attribute mounts, dedicated child-window shaping, and explicit
`mount(...)` selector regression tests beyond default-attach behavior.


## Phase 6. Build The DearPyGui Engine Host

**Scope (phases 3–5 vs phase 6).** Phases 3–5 already added
`DpgMountableEngine`, `connect_dpg_event_signal`, and a **recording**
`DpgRuntimeHost` in `host.py` so the generic mountable engine can be tested
without a GUI. Phase 6 is the **live** backend: a real implementation of the
same host contract (or a thin delegate) that calls into `dearpygui`, owns
viewport/context lifecycle, and uses a real staging root. Keep the recording
host for unit tests; add a separate module or clearly named class for the
production host so `engine.py` does not mix “mountable wiring” and “viewport
bootstrap” indefinitely.

Goal:

- own DearPyGui lifecycle and runtime-only mutation behind a backend interface

Files:

- `py-rolyze/src/pyrolyze/backends/dearpygui/engine.py` (already: mountable
  engine + event wiring; may import the live host)
- new module under `backends/dearpygui/` for the **live** host (viewport,
  context, staging root) — name TBD, e.g. `live_host.py`
- host/bootstrap entry points where backend roots are created (examples or
  app glue)

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

Status:

- complete

Delivered:

- `live_host.py`: `LiveDpgHost` context/viewport bootstrap, `add_stage` staging root,
  `children_order` shadow (for `place_child`), existence guards on configure/value/delete,
  `create_with_factory` fallbacks for root items (e.g. `add_window`) then reparent to staging
- Optional dependency group `dpg` (`dearpygui>=2,<3`); tests in
  `tests/test_dearpygui_live_host.py` (`pytest.importorskip` when `dearpygui` absent)
- `examples/run_dpg_host_smoke.py` manual smoke (window + button + `start_dearpygui`)


## Phase 7. Generate And Audit `DearPyGuiUiLibrary`

Goal:

- check in a real generated DearPyGui library and inspect its quality

Files:

- `py-rolyze/src/pyrolyze/backends/dearpygui/generated_library.py`
- `py-rolyze/pyrolyze_tools/generate_dearpygui_library.py` — extend beyond
  discovery/shaping/fixture listing to **emit** the checked-in library (or add
  a sibling module called from this entrypoint)

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

Status:

- complete (imperative ``UIElement`` + ``DpgMountableEngine``; not yet the
  ``@pyrolyze`` / ``load_transformed_namespace`` path used by Qt/Tk examples)

Delivered:

- ``examples/dearpygui_demo_trees.py`` — builders: window+menu, table cell grid,
  value/event widgets (input, checkbox, drag/drop button + log)
- ``examples/run_grid_app_dearpygui.py`` — interactive grid via
  ``pyrolyze_native_dearpygui`` (``create_host`` / ``reconcile_window_content``);
  ``uv run --extra dpg python examples/run_grid_app_dearpygui.py``
- ``pyrolyze/pyrolyze_native_dearpygui.py`` — Qt/Tk-style native host for
  ``RenderContext.committed_ui()``-style single-root reconciliation
- ``tests/test_dearpygui_examples_trees.py`` — structural tree tests (no GUI)
- ``tests/test_dearpygui_examples_mount.py`` — mount smoke (``importorskip``)
- ``tests/test_pyrolyze_native_dearpygui.py`` — native host reconcile (``importorskip``)

Follow-up: a **compiler-emitted** ``grid_app_dearpygui`` (``@pyrolyze`` + generated
``DearPyGui`` widget facades) is still out of scope until codegen exposes author
``C*``/``ui_interface`` for DearPyGui like PySide6.


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

Status:

- complete

Delivered (audit notes):

- **Regression:** full ``pytest`` suite run after native host + example wiring;
  DearPyGui-specific tests use ``pytest.importorskip("dearpygui")`` or
  ``uv run --extra dpg --with pytest`` when exercising live GL paths.
- **Generated library surface:** ``generated_library.py`` exports a large
  ``__all__`` (all ``M_*`` stubs) for tooling and explicit re-exports; author
  examples should prefer ``UIElement`` / ``DearPyGuiUiLibrary.WIDGET_SPECS`` /
  ``pyrolyze_native_dearpygui`` rather than importing ``M_*`` directly.
- **Learnings:** single table in ``learnings.py``; mount metadata aligned with
  hand items (Window, Table, NodeEditor, Node, FontRegistry, etc.); duplicate
  ``add_*`` / ``draw_*`` kinds use ``*DrawCmd`` UI kind suffix in the emitter.
- **Integration:** ``pyrolyze_native_dearpygui`` mirrors
  ``pyrolyze_native_pyside6`` / ``pyrolyze_native_tkinter`` (single root
  ``UIElement``, mount vs update).


## Test Strategy

Use the repository TDD workflow strictly:

1. add or update a focused failing test first
2. make the smallest change that turns it green
3. rerun the focused target
4. rerun the full suite before finalizing a phase

Repository commands:

- focused: `uv run --with pytest --with pytest-cov pytest <test-path> -q`
- full suite: `uv run --with pytest --with pytest-cov pytest -q`

Recommended test areas (existing or to add):

- `py-rolyze/tests/test_dearpygui_discovery_and_learnings.py` (phases 1–2)
- `py-rolyze/tests/test_dearpygui_adapter_phases_3_5.py` (phases 3–5)
- `py-rolyze/tests/test_dearpygui_examples_trees.py` / `test_dearpygui_examples_mount.py` (phase 8)
- `py-rolyze/tests/test_pyrolyze_native_dearpygui.py` (native host)
- `py-rolyze/tests/test_generate_dearpygui_library_tool.py` (when the tool
  grows)
- optional split later: `py-rolyze/tests/backends/dearpygui/test_*.py`
- `py-rolyze/tests/test_generated_backend_libraries.py` (when generated output
  exists)


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
| 1 | Productize DearPyGui discovery | Complete |
| 2 | Introduce DearPyGui learnings | Complete |
| 3 | Add DearPyGui adapter mountables | Complete |
| 4 | Implement event wiring | Complete |
| 5 | Implement structural mount families | Complete |
| 6 | Build the DearPyGui engine host (live viewport/context) | Complete |
| 7 | Generate and audit `DearPyGuiUiLibrary` | Complete |
| 8 | Convert representative examples | Complete |
| 9 | Run full regression and hardening | Complete |
