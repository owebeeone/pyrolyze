# Comprehensive Backend And Shape Visualization

## Purpose

This document covers the newer testing tools built on top of
`pyrolyze.testing.generic_backend`:

- the generated **comprehensive backend**
- the recursive **basic shape** test helpers
- the **slot/context + render overlay** DOT/SVG visualizer

Use these when debugging rerender vs fresh-render mismatches, especially for
mount ordering, nested container placement, and retained-subtree attribution.

## Code map

- comprehensive backend generator
  - `src/pyrolyze/testing/comprehensive_backend/cb.py`
- visualizer
  - `src/pyrolyze/testing/comprehensive_backend/visualize.py`
- package exports
  - `src/pyrolyze/testing/comprehensive_backend/__init__.py`
- executable recursive shape helpers
  - `tests/basic_pyro_shapes.py`
- focused tests
  - `tests/test_comprehensive_backend.py`
  - `tests/test_comprehensive_backend_visualize.py`
  - `tests/test_basic_pyro_shapes.py`

## Comprehensive backend

The comprehensive backend is a generated backend intended to be broad enough to
exercise many structural combinations without hand-writing a large fake UI
library.

It currently generates:

- root type
  - `Node`
- base types
  - `BaseAA`, `BaseAB`, ...
- leaves
  - `LeafAA00`, `LeafAA01`, ...
- containers
  - `BinAA00`, `BinAA01`, ...
- rotating mount families
  - `MountSingleAA`
  - `MountOrderedAA`
  - `MountNestedAB`
  - `MountKeyedAB`

It also supports generated scalar fields through `ComprehensiveBackendShape`:

- `n_int`
- `n_str`

These become constructor fields like:

- `fint_a`
- `fint_b`
- `fstr_a`
- `fstr_b`

The public helpers are:

- `build_comprehensive_backend(...)`
- `comprehensive_node_specs(...)`
- `selector_family_names(...)`
- `mount_profile_names(...)`
- `allowed_child_type_names_for_mount(...)`

`allowed_child_type_names_for_mount(...)` is the main legality helper for
shape/state generation. It lets the test side ask:

- given a mount family, which generated `Leaf*` and `Bin*` node types are legal?

That keeps recursive shape generation data-driven instead of hard-coding mount
compatibility logic into tests.

## Basic recursive shapes

`tests/basic_pyro_shapes.py` is intentionally close to the scratch-style model:

- external state lives outside the transformed PyRolyze code
- slotted `use_stored(...)` reads that state through `StoreProbe`
- `CallShape.capture(...)` binds a component call into a zero-arg `ComponentRef`
- transformed shape functions interpret the stored state and recursively call
  further captured shapes

Current test-side shape dataclasses:

- `CallShape`
- `ShapeBasic`
- `ShapeRoot`

Current transformed shape functions loaded through
`load_transformed_namespace(...)`:

- `shape_basic(...)`
- `shape_root(...)`

This setup is useful because it exercises:

- real compiler lowering
- real slot/context ownership
- dynamic recursive component expansion
- external-state-driven rerenders

without generating arbitrary Python source for each fuzz case.

## Visualizer

`src/pyrolyze/testing/comprehensive_backend/visualize.py` writes a DOT graph and
optionally renders SVG with Graphviz.

Current API:

- `render_context_to_dot(...)`
- `write_render_context_graph(...)`

The visualizer overlays two things:

1. the runtime slot/context graph
2. the mounted generic-backend render graph

### Slot/context graph

The slot graph comes from:

- `pyrolyze.visitor.capture_context_graph(...)`

Slot nodes are:

- light green when active
- grey when explicitly supplied through `inactive_slot_ids`

The visible slot label is shortened to:

- `Slot(M1, 6, 19, (0,))`

where:

- `M1` is a module alias
- `6` is `slot_index`
- `19` is `line_no`
- `(0,)` is `key_path`

A module legend is emitted at the bottom of the graph, for example:

- `M1 = example.pyro_shapes.basic_test`

Important detail:

- the displayed slot label is intentionally short and may repeat
- graph identity is based on traversal path, not just the visible label

That is required because the same logical slot id can appear multiple times
under different parent contexts in recursive shapes.

### Render graph

The blue render nodes come from mounted generic-backend nodes:

- `MountedMountableNode`
- `PyroRenderHarness`
- `PyroRenderResult`

The visualizer attributes each mounted render node to the best matching slot
cluster using:

- the emitted `UIElement.slot_id`
- the last logical `SlotId` in the mounted path
- parent render ownership as a scoping rule
- traversal-order consumption when the same slot label repeats

This avoids the common mis-attribution bug where repeated leaves all collapse
into the first matching slot cluster.

### What this works with

The visualizer currently has two layers with different scope:

#### General part

The **slot/context graph capture** is general runtime tooling.

Anything with a `RenderContext` can use:

- `capture_context_graph(...)`
- `walk_context_graph(...)`
- `compare_context_graphs(...)`

So the green/grey slot graph idea is not tied to the generated backend.

#### Generated-backend-specific part

The **blue render-node overlay** is currently specific to the generated generic
backend / comprehensive backend path.

It depends on mounted generic-backend structures:

- `MountedMountableNode`
- `PyroRenderHarness`
- `PyroRenderResult`

and on the fact that those nodes retain emitted-slot identity in a way the
visualizer can read.

So today:

- slot graph only: works for any `RenderContext`
- slot graph + blue render overlay: works for the generated backend path

It is possible to generalize the render overlay later, but that would need a
backend-neutral mounted-node inspection interface.

## Output pattern

The current recursive shape test writes artifacts under:

- `pyrolyze/scratch/tests/test_basic_shape_module_render0/`

Current files:

- `basic_shape_snapshot.dot`
- `basic_shape_snapshot.svg`
- `basic_shape_context_overlay.dot`
- `basic_shape_context_overlay.svg`

The first pair is a plain mounted-graph snapshot.

The second pair is the richer slot/context + render overlay.

## When to use which artifact

Use the plain snapshot when you want:

- backend tree shape
- mount bucket shape
- host-surface placement shape

Use the overlay when you want:

- which slot/context owns which rendered node
- whether repeated recursive slots are being attributed correctly
- whether retained nested structure is ending up under the right repeated slot

## Recommended next step

The intended follow-on is to use the same shape/state setup for:

- small external-state mutations
- incremental rerender
- fresh render from the mutated state
- snapshot + overlay comparison on failure

That will turn the current static recursive-shape test into the first real
rerender-vs-fresh structural regression harness.
