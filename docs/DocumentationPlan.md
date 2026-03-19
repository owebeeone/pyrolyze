# PyRolyze Docs Plan

## Purpose

Create a first-class `docs/` tree inside `py-rolyze/` that explains the
current package as implemented, not the redesign history that lives in the
parent repo. In fact the pyrolyze history is not relevant so avoid mentioning
previous versions.

This plan is based on:

- active parent docs in `/Users/owebeeone/limbo/py-rolyze-dev2/docs/` the relevant plan is in "new_design" and that with the docs/user/PyRolyze_Authoring_Guide.md should be the plan of record but the actual implementation is the target of this documentation (future sections of course can reflect the intentions not yet implemented)
- the current package source in
  `/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/`
- the current examples and tests in
  `/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/examples/` and
  `/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/tests/`

The goal is to make the nested repo self-explanatory for:

- users authoring `@pyrolyse` code
- maintainers debugging compiler/runtime behavior
- humans or AI agents adding new Python AST kernel support
- backend/library authors building on top of the reconciler

## Scope

The new `py-rolyze/docs/` should contain only active documentation derived from
the current implementation and the current non-historical parent docs.

Do not copy historical materials such as:

- `docs/sdd/`
- `docs/reference/`
- legacy plan documents
- superseded prototype notes

Use those only as background when needed.

## Source Of Truth Inputs

### Parent docs worth extracting from

- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/NoCompValueApiDesign.md`
- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/new_design/App_Context_Framework.md`
- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/new_design/PyrolyzeContextManagement_V2.md`
- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/new_design/UI_Reconcilliation_Mechanism.md`
- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/new_design/UI_Node_Bindings_Proposal.md`
- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/new_design/ast/`
- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/new_design/ast/INTEGRATED_TEST_ENV.md`
- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/user/PyRolyze_Authoring_Guide.md`
- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/AdvancedTestingPlan.md`
- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/Python Library Documentation Tone Guide - Short.md`
- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/Python Library Documentation Tone Guide.md`
- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/whitepaper/PyRolyze_Transformed_Runtime_White_Paper.md`

### Current code seams that docs must reflect

- public source API:
  - `src/pyrolyze/api.py`
  - `src/pyrolyze/hooks.py`
- import/loader path:
  - `src/pyrolyze/import_hook.py`
  - `src/pyrolyze/importer.py`
- compiler facade and versioned kernels:
  - `src/pyrolyze/compiler/facade.py`
  - `src/pyrolyze/compiler/kernel_loader.py`
  - `src/pyrolyze/compiler/kernel_api.py`
  - `src/pyrolyze/compiler/artifacts.py`
  - `src/pyrolyze/compiler/debug.py`
  - `src/pyrolyze/compiler/diagnostics.py`
  - `src/pyrolyze/compiler/kernels/v3_14/`
- runtime:
  - `src/pyrolyze/runtime/context.py`
  - `src/pyrolyze/runtime/app_context.py`
  - `src/pyrolyze/runtime/trace.py`
  - `src/pyrolyze/runtime/ui_nodes.py`
  - `src/pyrolyze/visitor.py`
- backend UI libraries:
  - `src/pyrolyze/pyrolyze_pyside6.py`
  - `src/pyrolyze/pyrolyze_tkinter.py`
- examples:
  - `examples/grid_app.py`
  - `examples/run_grid_app.py`
- testing and version runner:
  - `tests/README.md`
  - `tests/versioned_test_harness.py`
  - `tests/data/gold_cases.toml`
  - `tests/test_ast_goldens.py`
  - `tests/test_visitor_context_graph_integrated.py`

## Proposed Docs Tree

```text
py-rolyze/docs/
  README.md
  overview/
    What_Is_PyRolyze.md
    Why_PyRolyze.md
    System_Map.md
  design/
    Architecture.md
    Loader_And_Import_Hook.md
    Compiler_And_Kernels.md
    Runtime_Context_Graph.md
    Event_Management_And_Scheduler.md
    UI_Libraries_And_Backend_Adapters.md
    Reconciler_And_UI_Node_Model.md
    App_Context_Framework.md
    Integrated_Test_Environment.md
    Python_Version_Support_And_AST_Kernel_Strategy.md
  user/
    README.md
    Authoring_Overview.md
    Decorators_And_Annotations.md
    Components_Containers_And_Function_Semantics.md
    Hooks_And_State.md
    Native_UI_And_UIElement.md
    Building_A_UI_Library.md
    Testing_Pyrolyze_Code.md
    Examples.md
  contributor/
    README.md
    Testing_And_Goldens.md
    Versioned_Test_Runs.md
    Adding_A_New_AST_Kernel.md
    Diagnosing_AST_Regressions.md
    Tracing_And_Debugging.md
  reference/
    Glossary.md
    Public_API_Surface.md
```

## Tone Strategy

This section should be read together with:

- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/Python Library Documentation Tone Guide - Short.md`
- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/Python Library Documentation Tone Guide.md`

The short guide is the operational writing guide. The longer guide is
background rationale. The rules below adapt both to the specific
`py-rolyze/docs/` structure.

The nested repo docs should use different tones for different readers instead
of forcing every document into the same voice.

Recommended tone families:

- `overview/`
  - clear, confident, motivating
  - explain why PyRolyze matters without sounding like marketing copy
- `design/`
  - technical, grounded, implementation-first
  - optimized for accuracy and current behavior
- `user/`
  - practical, concise, lightly aspirational
  - should communicate the value of the model without becoming wordy
- `contributor/`
  - procedural, explicit, low-ambiguity
  - written for maintainers and AI agents changing code
- `reference/`
  - matter-of-fact, professional, and to the point
  - optimized for fast lookup rather than narrative

Writing rules:

- `overview/` can be the most visionary section, but it should still stay
  compact and concrete.
- `design/` must always describe current implementation before future ideas.
- `user/` should balance authoring guidance with a modest sense of what the
  model enables.
- `contributor/` should prefer checklists, procedures, and explicit decision
  rules.
- `reference/` should avoid scene-setting and minimize explanatory prose.

## Folder Intent

### `overview/`

Short, motivating entry docs.

Tone guidance:

- concise, high-signal, slightly aspirational
- enough energy to explain the purpose of PyRolyze
- avoid hype, repetition, and long preambles
- prefer diagrams and short sections over long essays

- `What_Is_PyRolyze.md`
  - what the package does today
  - what it does not do yet
  - where to start
- `Why_PyRolyze.md`
  - aspirational document
  - why compile-time reactive Python is useful
  - why AST transforms are worth the complexity
- `System_Map.md`
  - one graphic with components and boundaries
  - should use Mermaid
  - should link down into `design/`, `user/`, and `contributor/`

### `design/`

Implementation-facing docs that explain the actual package structure and
behavior.

Tone guidance:

- precise, direct, implementation-oriented
- default to concrete module names, runtime objects, and tests
- separate “implemented now” from “future proposals” very clearly
- avoid aspirational language outside explicit future-looking sections

Every design doc should have the same sections:

1. Purpose
2. Current implementation
3. Code map
4. Main tests
5. Known limitations
6. Future proposals

Required design docs:

- `Architecture.md`
  - top-level package architecture
  - relationship between API, compiler, runtime, backend wrappers, examples, tests
- `Loader_And_Import_Hook.md`
  - `#@pyrolyze`
  - import hook
  - importer cache/fingerprint behavior
- `Compiler_And_Kernels.md`
  - facade
  - kernel loader
  - current `v3_14` kernel structure
  - emitted helper source and goldens
- `Runtime_Context_Graph.md`
  - `RenderContext`
  - slot contexts
  - structural owner vs render owner
  - committed UI behavior
- `Event_Management_And_Scheduler.md`
  - event handlers
  - invalidation queue
  - rerun boundaries
  - post-flush behavior
- `UI_Libraries_And_Backend_Adapters.md`
  - PySide6 adapter
  - Tkinter adapter
  - example host flow
- `Reconciler_And_UI_Node_Model.md`
  - `UIElement`
  - `UiNodeSpec`
  - reconciliation and identity
- `App_Context_Framework.md`
  - app context store
  - generation tracking
  - current optional usage model
- `Integrated_Test_Environment.md`
  - visitor/capture model
  - graph diffs
  - integrated source-backed graph tests
- `Python_Version_Support_And_AST_Kernel_Strategy.md`
  - current support policy
  - fallback behavior
  - how to introduce a new kernel when AST breaks
  - what has already been verified: 3.12, 3.13, 3.14, 3.15 all against `v3_14`

### `user/`

Authoring docs for people writing PyRolyze source.

Tone guidance:

- practical and directive, but not dry
- lightly aspirational rather than purely mechanical
- focus on helping authors make correct choices quickly
- explain constraints clearly instead of apologizing for them

- `README.md`
  - user-doc table of contents
- `Authoring_Overview.md`
  - simplest mental model
  - file opt-in and entry flow
- `Decorators_And_Annotations.md`
  - `@pyrolyse`
  - `@pyrolyze_slotted`
  - `ComponentRef[...]`
  - `SlotCallable[...]`
  - `PyrolyteHandler[...]`
  - `Callable[...]`
  - when annotations are required
- `Components_Containers_And_Function_Semantics.md`
  - difference between plain functions, slotted helpers, components
  - `with helper(...):`
  - `with expr(...) as value:`
  - passing functions while preserving semantics
  - explain clearly that `call_native(...)` is a compiler intrinsic, not a function kind
- `Hooks_And_State.md`
  - `use_state`
  - `use_effect`
  - `use_mount`
  - `use_unmount`
  - `use_grip`
  - behavior and testing expectations
- `Native_UI_And_UIElement.md`
  - `UIElement` semantics
  - `call_native(...)`
  - what native helpers may return
- `Building_A_UI_Library.md`
  - how to define UIElement kinds
  - how to bridge a backend to the reconciler
  - how to structure bindings
- `Testing_Pyrolyze_Code.md`
  - source-backed tests
  - integrated graph tests
  - host tests vs compiler/runtime tests
- `Examples.md`
  - small complete examples
  - include real code drawn from examples and test fixtures

### `contributor/`

This is the main missing section. It should exist because versioned AST
maintenance and golden management are neither user docs nor architecture docs.

Tone guidance:

- crisp, procedural, and unambiguous
- assume the reader may be debugging a failure or adding version support
- make steps and decision points easy to scan
- optimize for correctness and maintainability over elegance

- `README.md`
  - contributor-doc entry point
- `Testing_And_Goldens.md`
  - gold source corpus
  - checked-in goldens
  - actual test results
- `Versioned_Test_Runs.md`
  - direct lift/adaptation of `tests/README.md`
- `Adding_A_New_AST_Kernel.md`
  - how to create `v3_15`, `v3_16`, and so on
  - how to keep shared vs versioned logic separated
- `Diagnosing_AST_Regressions.md`
  - compare source, expected, actual
  - decide runtime vs compiler vs kernel break
- `Tracing_And_Debugging.md`
  - runtime trace channels
  - graph capture
  - examples and failure workflows

### `reference/`

Small, stable lookup docs.

Tone guidance:

- matter-of-fact, professional, and to the point
- minimal narrative, minimal framing
- definitions and signatures first
- examples only where they prevent ambiguity

- `Glossary.md`
  - boundary
  - slot
  - render owner
  - structural owner
  - component ref
  - slotted helper
  - call native
  - committed UI
  - keyed loop item
- `Public_API_Surface.md`
  - summarize current exported API from `api.py`, `hooks.py`, and key runtime/compiler entrypoints

## Additional Sections Worth Adding

These are the sections missing from the initial request that should be included.

### Contributor / maintainer docs

This is the biggest gap. The nested repo already contains a real operational
story for:

- goldens
- versioned uv test runs
- kernel fallback
- multi-version verification

That deserves a dedicated folder instead of being split across `design/` and
`user/`.

### Glossary / reference docs

PyRolyze has a specialized vocabulary. A glossary will reduce repetition and
make the design and user docs more consistent.

### Status / limitations notes

Each major design doc should explicitly record what is implemented versus still
aspirational. This repo currently contains both shipped behavior and planned
behavior, so that distinction must stay visible.

## Migration Strategy From Parent Docs

Do not copy parent docs verbatim.

For each new doc:

1. start from the relevant parent design doc
2. verify each claim against the current `py-rolyze` code
3. verify behavior against tests where possible
4. rewrite the material to describe the nested repo as it exists now
5. place older or not-yet-implemented ideas under `Future proposals`

Rules:

- if current code contradicts the parent doc, the nested repo doc must describe
  current code first
- if a proposal is still valuable but not implemented, keep it in `Future proposals`
- if a parent doc is mostly historical, do not import it into the nested repo

## Writing Conventions

Use the same conventions across all new docs:

- every design doc must include `Future proposals`
- every design and contributor doc must include `Code map`
- every design and contributor doc should include `Primary tests`
- examples should come from current code:
  - `examples/grid_app.py`
  - `tests/data/gold_src/`
  - integrated source-backed graph tests
- diagrams should use Mermaid
- keep “implemented now” and “possible later” clearly separated

## Suggested Delivery Order

### Phase 1: skeleton and entry docs

1. create `py-rolyze/docs/`
2. create top-level `README.md`
3. create `overview/What_Is_PyRolyze.md`
4. create `overview/System_Map.md`
5. create `contributor/Versioned_Test_Runs.md`

### Phase 2: architecture docs

1. `design/Architecture.md`
2. `design/Compiler_And_Kernels.md`
3. `design/Runtime_Context_Graph.md`
4. `design/Reconciler_And_UI_Node_Model.md`
5. `design/Loader_And_Import_Hook.md`

### Phase 3: backend and event docs

1. `design/Event_Management_And_Scheduler.md`
2. `design/UI_Libraries_And_Backend_Adapters.md`
3. `design/App_Context_Framework.md`
4. `design/Integrated_Test_Environment.md`

### Phase 4: user docs

1. `user/README.md`
2. `user/Authoring_Overview.md`
3. `user/Decorators_And_Annotations.md`
4. `user/Components_Containers_And_Function_Semantics.md`
5. `user/Hooks_And_State.md`
6. `user/Native_UI_And_UIElement.md`
7. `user/Examples.md`

### Phase 5: maintainer docs

1. `contributor/Testing_And_Goldens.md`
2. `contributor/Adding_A_New_AST_Kernel.md`
3. `contributor/Diagnosing_AST_Regressions.md`
4. `contributor/Tracing_And_Debugging.md`
5. `design/Python_Version_Support_And_AST_Kernel_Strategy.md`

### Phase 6: polish

1. add `reference/Glossary.md`
2. add `reference/Public_API_Surface.md`
3. cross-link everything
4. update `py-rolyze/README.md` to point at the new nested docs tree

## Acceptance Criteria

The plan is complete when:

- `py-rolyze/docs/` stands on its own without requiring a reader to start in the
  parent repo
- current package behavior is documented from current code and tests
- user docs explain authoring rules clearly enough to avoid function-kind and
  annotation mistakes
- maintainer docs explain how to keep AST support working across Python versions
- every design doc clearly marks future ideas instead of mixing them into the
  current behavior description
