# Backend Generation And Learnings

## Purpose

Explain how the generated backend UI libraries are produced for:

- `PySide6`
- `tkinter`

and what the backend `learnings.py` files actually do.

This is an operational maintainer document. It describes the current pipeline
as it exists in the repository today, including the parts that are still
transitional.


## Code Map

Primary files:

- generator:
  - [pyrolyze_tools/generate_semantic_library.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/pyrolyze_tools/generate_semantic_library.py)
- backend model types:
  - [src/pyrolyze/backends/model.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/model.py)
- PySide6 learnings:
  - [src/pyrolyze/backends/pyside6/learnings.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/pyside6/learnings.py)
- tkinter learnings:
  - [src/pyrolyze/backends/tkinter/learnings.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/tkinter/learnings.py)
- checked-in generated libraries:
  - [src/pyrolyze/backends/pyside6/generated_library.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/pyside6/generated_library.py)
  - [src/pyrolyze/backends/tkinter/generated_library.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/tkinter/generated_library.py)

Primary tests:

- [tests/test_generate_semantic_library_tool.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/tests/test_generate_semantic_library_tool.py)
- [tests/test_generated_backend_libraries.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/tests/test_generated_backend_libraries.py)
- [tests/backends/pyside6/test_widget_engine.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/tests/backends/pyside6/test_widget_engine.py)


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
[generate_semantic_library.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/pyrolyze_tools/generate_semantic_library.py).


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


## Learnings

`learnings.py` is the authoritative manual overlay for a backend.

The generator loads it with:

- `load_learnings(...)`
- `apply_learnings(...)`

The learnings model is defined in
[model.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/model.py):

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

- [src/pyrolyze/backends/tkinter/learnings.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/tkinter/learnings.py)

At the moment that file exports an empty `LEARNINGS` map.

That means Tkinter generation today is almost entirely raw-discovery driven,
with much less shaping than PySide6.


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

- [src/pyrolyze/backends/pyside6/generated_library.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/pyside6/generated_library.py)
- [src/pyrolyze/backends/tkinter/generated_library.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/tkinter/generated_library.py)

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
- raw vs lowered generated backend artifacts are still not unified under one
  clean command
- model/runtime naming still mixes older `UiWidget*` names with newer
  `Mountable*` design terminology


## Related Docs

- [UI_Libraries_And_Backend_Adapters.md](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/docs/design/UI_Libraries_And_Backend_Adapters.md)
- [MountPointComponentDesign.md](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/dev-docs/MountPointComponentDesign.md)
- [MountableSpecModel.md](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/dev-docs/MountableSpecModel.md)
- [MountableTestingPlan.md](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/dev-docs/MountableTestingPlan.md)
