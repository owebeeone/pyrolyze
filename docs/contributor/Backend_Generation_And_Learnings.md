# Backend Generation And Learnings

## Purpose

Explain how the generated backend UI libraries are produced for:

- `PySide6`
- `tkinter`

what the backend `learnings.py` files do, and where the **DearPyGui** pipeline
fits (separate generator entry point from semantic-library extraction).

This is an operational maintainer document. It describes the current pipeline
as it exists in the repository today, including the parts that are still
transitional.


## Code Map

Primary files:

- generator:
  - [pyrolyze_tools/generate_semantic_library.py](../../pyrolyze_tools/generate_semantic_library.py)
- backend model types:
  - [src/pyrolyze/backends/model.py](../../src/pyrolyze/backends/model.py)
- PySide6 learnings:
  - [src/pyrolyze/backends/pyside6/learnings.py](../../src/pyrolyze/backends/pyside6/learnings.py)
- tkinter learnings:
  - [src/pyrolyze/backends/tkinter/learnings.py](../../src/pyrolyze/backends/tkinter/learnings.py)
- checked-in generated libraries:
  - [src/pyrolyze/backends/pyside6/generated_library.py](../../src/pyrolyze/backends/pyside6/generated_library.py)
  - [src/pyrolyze/backends/tkinter/generated_library.py](../../src/pyrolyze/backends/tkinter/generated_library.py)
- DearPyGui (separate toolchain; not `generate_semantic_library.py`):
  - CLI / driver: [pyrolyze_tools/generate_dearpygui_library.py](../../pyrolyze_tools/generate_dearpygui_library.py)
  - emitter implementation: [pyrolyze_tools/dearpygui_emit_library.py](../../pyrolyze_tools/dearpygui_emit_library.py)
  - learnings overlay: [src/pyrolyze/backends/dearpygui/learnings.py](../../src/pyrolyze/backends/dearpygui/learnings.py)
  - checked-in artifact: [src/pyrolyze/backends/dearpygui/generated_library.py](../../src/pyrolyze/backends/dearpygui/generated_library.py)

Primary tests:

- [tests/test_generate_semantic_library_tool.py](../../tests/test_generate_semantic_library_tool.py)
- [tests/test_generated_backend_libraries.py](../../tests/test_generated_backend_libraries.py)
- [tests/backends/pyside6/test_widget_engine.py](../../tests/backends/pyside6/test_widget_engine.py)
- [tests/test_dearpygui_generated_library.py](../../tests/test_dearpygui_generated_library.py)


## DearPyGui generation

DearPyGui uses **discovery against the installed `dearpygui` package** and a
dedicated emitter ([dearpygui_emit_library.py](../../pyrolyze_tools/dearpygui_emit_library.py)),
not the PySide6/tkinter semantic discovery pipeline above.

Typical maintainer flow:

```bash
uv run --extra dpg python pyrolyze_tools/generate_dearpygui_library.py --emit
```

Author-facing helpers for a subset of kinds live in
[src/pyrolyze/backends/dearpygui/author_ui.py](../../src/pyrolyze/backends/dearpygui/author_ui.py)
and are evolved alongside examples.


## High-Level Pipeline

The backend generation flow is:

1. Discover backend classes.
2. Extract constructor parameters.
3. Extract writable properties and multi-argument setter methods.
4. Extract mount points where supported.
5. Load backend-specific learnings.
6. Apply learnings as an overlay.
7. Generate a `UiLibrary`-style source file.
8. Commit or regenerate the checked-in generated backend library artifact.

The important design rule is:

- discovery provides the raw candidate surface
- `learnings.py` refines that surface
- the generated library is the runtime-facing artifact


## Discovery

### Entry Points

The main entry points are:

- `discover_modules(...)`
- `discover_widget_classes(...)`
- `write_generated_library(...)`

The CLI wrapper is:

```bash
uv run python pyrolyze_tools/generate_semantic_library.py PySide6 --output-dir scratch
uv run python pyrolyze_tools/generate_semantic_library.py tkinter --output-dir scratch
```

The generator chooses default base classes by package:

- `PySide6`
  - `QWidget`
  - `QLayout`
  - `QAction`
- `tkinter`
  - `tkinter.Widget`
  - `tkinter.ttk.Widget`

This logic lives in `_default_widget_base_specs(...)` in
[generate_semantic_library.py](../../pyrolyze_tools/generate_semantic_library.py).


### What Gets Extracted

For each discovered class, the generator builds a `DiscoveredWidgetClass`
containing:

- module/class identity
- public UI-library name
- constructor parameters
- writable properties
- multi-argument setter methods
- discovered mount points
- variadic-signature omission flag
- attached learnings overlay

The raw extraction helpers are:

- `_extract_parameters(...)`
- `_extract_properties(...)`
- `_extract_multiarg_setter_methods(...)`
- `_extract_mount_points(...)`


## PySide6 Extraction

PySide6 extraction is the richer path.

### Parameters

Constructor parameters come primarily from `.pyi` stubs, not only from runtime
introspection:

- `_extract_pyside6_parameters(...)`
- `_find_stub_class(...)`
- `_extract_stub_init_overloads(...)`

This matters because PySide6 runtime signatures are often incomplete or
introspection-hostile.

### Properties

Writable properties come from Qt meta-object data:

- `_extract_qt_properties(...)`

### Multi-Argument Methods

Setter-like methods are extracted from the `.pyi` stubs:

- `_extract_pyside6_multiarg_setters(...)`

### Mount Points

PySide6 currently has explicit mount-point discovery in the generator:

- `_extract_pyside6_mount_points(...)`
- `_build_pyside6_single_mount_point(...)`
- `_build_pyside6_family_mount_point(...)`

The discovery logic is driven by hardcoded families such as:

- single attach methods
- ordered attach families
- accepted-type heuristics
- ignored ordering/context parameters

This is the current bridge between raw API discovery and the newer mountable
runtime.

Important limit:

- PySide6 mount discovery is real, but still heuristic and curated
- it is not yet the exhaustive final mount scan described in the newer
  mount-point design docs


## Tkinter Extraction

Tkinter extraction is currently much simpler.

### Parameters

Constructor parameters come from runtime `inspect.signature(...)` when
available:

- `_extract_runtime_parameters(...)`

### Multi-Argument Methods

Setter-like methods are extracted from runtime functions:

- `_extract_tkinter_multiarg_setters(...)`

### Mount Points

Current state:

- `_extract_mount_points(...)` returns mount points only for `PySide6`
- `tkinter` mount-point extraction is not implemented in the generator today

So the checked-in Tkinter generated library is useful for:

- constructor params
- public prop surface
- method-learnings-driven grouped methods

but not yet for a real discovered mount-point surface.


## Tkinter: What Is Already Decided

This section is here to make handoff work easier.

For `tkinter`, the following points should be treated as current repository
truth, not open design questions:

- `TkinterUiLibrary` generation is currently breadth-first raw discovery, not a
  curated author-facing quality surface.
- The checked-in generated file may therefore include:
  - `tkinter.tix` classes
  - `_dummy*` helper classes
- That output is acceptable as a discovery artifact today.
- It is not yet evidence that those classes are endorsed as stable public
  authoring surface.

- Tkinter mount discovery is not implemented in the generator today.
- Because of that, a “full generated tkinter interface” is currently only full
  in the constructor/prop/method sense, not in the mount-point sense.

- The checked-in backend artifact workflow is still two-form:
  - raw generated source from `write_generated_library(...)`
  - lowered/runtime-ready checked-in artifact after compiler lowering
- Until that is unified, regeneration work should treat the lowering step as a
  required explicit part of refreshing a checked-in backend library.


## Tkinter: Remaining Decisions For A Real Full Interface

If the goal is only “make the generator run and emit a broad tkinter library”,
no major new design work is needed.

If the goal is “ship a high-quality full generated tkinter interface”, the
remaining decisions are these:

### 1. Event policy

Tk does not have a Qt-style signal model, so event generation must stay
explicit.

Current practical rule:

- generated tkinter event props should be driven by explicit learnings
- callback-like config parameters discovered at runtime should not
  automatically become event props

What still needs deciding in implementation terms:

- which tkinter callback/config names are promoted into generated event props
- which stay as ordinary config/callable props


### 2. Mount-point override support in learnings

The current learnings model covers:

- props
- grouped methods
- events

It does not yet provide a first-class mount-point override layer comparable to
what the mountable design now expects.

Tkinter will likely need manual shaping for:

- mount-point naming
- keyed vs non-keyed params
- default child mount selection
- default attach ordering

So for tkinter mount support, discovery alone is not enough; the learnings
model will need to grow.


### 3. Scope of `tkinter.tix`

The current checked-in library includes a large `tix`-driven surface and helper
types such as `_dummy*`.

This is the outstanding scope decision:

- if the goal is exhaustive discovered breadth, keep them
- if the goal is curated author-facing quality, trim or explicitly classify
  them as secondary/legacy surface

The current repository has not made that curation decision yet.


### 4. Reproducible checked-in regeneration

The two-step raw-then-lowered workflow is documented below, but not yet unified
behind one clean command.

For a serious tkinter refresh, do not assume:

- `write_generated_library(...)` alone reproduces
  `src/pyrolyze/backends/tkinter/generated_library.py`

It does not. The lowering step is still part of the checked-in artifact path.

So a maintainer touching tkinter generation should treat this as an explicit
workflow boundary, not an implementation detail.


## Learnings

`learnings.py` is the authoritative manual overlay for a backend.

The generator loads it with:

- `load_learnings(...)`
- `apply_learnings(...)`

The learnings model is defined in
[model.py](../../src/pyrolyze/backends/model.py):

- `UiWidgetLearning`
- `UiPropLearning`
- `UiMethodLearning`
- `UiEventLearning`

What each one does:

- `UiWidgetLearning`
  - backend-local override bucket for one class
  - may rename the public emitted callable via `public_name`
- `UiPropLearning`
  - can hide a prop from the public generated signature
  - can override signature annotation
  - can override signature default representation
- `UiMethodLearning`
  - maps a multi-argument setter to synthetic source props
  - chooses `FillPolicy`
  - chooses `MethodMode`
  - marks whether the method is constructor-equivalent
- `UiEventLearning`
  - maps public event prop name to a backend signal name
  - sets event payload policy

### What Learnings Are Not

`learnings.py` is not supposed to replace discovery.

It should:

- rename
- hide
- group
- signal-map
- fill-policy-map

It should not become the only source of truth for the backend surface.

That distinction matters even more now that the newer mount-point work expects:

- exhaustive backend discovery
- learnings as an overlay


## PySide6 Learnings State

Current PySide6 learnings are substantial.

They do a lot of real work:

- grouped setter-method mapping
- fill-policy selection
- constructor-equivalent marking
- event wiring
- selected public signature shaping

There are also helper functions in the generator for producing initial PySide6
learnings:

- `infer_pyside6_learnings(...)`
- `generate_pyside6_learnings_source(...)`

Important caveat:

- those helpers are currently helper/test utilities
- they are not the normal CLI generation path


## Tkinter Learnings State

Current Tkinter learnings are intentionally minimal:

- [src/pyrolyze/backends/tkinter/learnings.py](../../src/pyrolyze/backends/tkinter/learnings.py)

At the moment that file exports an empty `LEARNINGS` map.

That means Tkinter generation today is almost entirely raw-discovery driven,
with much less shaping than PySide6.

That emptiness should be read carefully:

- it means tkinter generation currently has almost no manual shaping
- it does not mean manual shaping is unnecessary
- for mount points and event policy, more learnings support is still expected to
  be needed


## Generated Output

The generated backend library is a class namespace with:

- `UI_INTERFACE`
- `MOUNTABLE_SPECS`
- generated `C...` author-facing callables

The relevant model types are:

- `UiWidgetSpec`
- `MountPointSpec`
- `UiInterface`

Current naming note:

- runtime code still uses some historical `UiWidget*` names
- the newer design docs refer to the same direction as `MountableSpec`


## Raw vs Lowered Generated Files

This is the most important current gotcha.

The public generator entry point:

- `write_generated_library(...)`

currently writes **raw semantic-library source** using:

- `generate_library_source(...)`

It does **not** itself lower that source through the AST compiler.

However, the checked-in backend generated libraries in `src/pyrolyze/backends/`
are currently **lowered/runtime-ready artifacts**.

So today there are effectively two forms:

1. Raw generated source
   - produced directly by `write_generated_library(...)`
2. Lowered checked-in runtime artifact
   - produced by additionally passing raw source through the compiler/lowering
     path before committing it

This is a real transitional inconsistency in the repository. Any maintainer
regenerating backend libraries needs to be aware of it.


## Practical Regeneration Workflow

If you only want to inspect raw discovery output:

```bash
uv run python pyrolyze_tools/generate_semantic_library.py PySide6 --output-dir scratch
uv run python pyrolyze_tools/generate_semantic_library.py tkinter --output-dir scratch
```

If you want to refresh the checked-in runtime-ready generated backend library,
the raw generated source must currently also be lowered through the compiler
before writing back to:

- [src/pyrolyze/backends/pyside6/generated_library.py](../../src/pyrolyze/backends/pyside6/generated_library.py)
- [src/pyrolyze/backends/tkinter/generated_library.py](../../src/pyrolyze/backends/tkinter/generated_library.py)

If you are touching this path, verify which artifact form the relevant tests
expect before committing.


## What To Change When A Backend Surface Is Wrong

If the generated backend surface is wrong, debug in this order:

1. Raw discovery wrong
   - inspect discovery helper logic first
2. Raw discovery right, public surface wrong
   - inspect `learnings.py`
3. Raw/lowered mismatch
   - inspect generation vs lowering pipeline
4. Runtime behavior wrong with correct generated metadata
   - inspect the engine/mount runtime, not the generator

This order matters. It avoids smuggling runtime fixes into `learnings.py`.


## Current Gaps

The important current gaps are:

- PySide6 mount discovery is still heuristic, not yet exhaustive
- Tkinter mount discovery is not implemented in the generator yet
- tkinter event promotion policy is not yet fully settled in generated metadata
- learnings do not yet have first-class mount-point override support
- the checked-in Tkinter generated surface is still breadth-first, not curated
- raw vs lowered generated backend artifacts are still not unified under one
  clean command
- model/runtime naming still mixes older `UiWidget*` names with newer
  `Mountable*` design terminology


## Related Docs

- [UI_Libraries_And_Backend_Adapters.md](../../docs/design/UI_Libraries_And_Backend_Adapters.md)
- [MountPointComponentDesign.md](../../dev-docs/MountPointComponentDesign.md)
- [MountableSpecModel.md](../../dev-docs/MountableSpecModel.md)
- [MountableTestingPlan.md](../../dev-docs/MountableTestingPlan.md)
