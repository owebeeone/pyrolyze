# Pyrolyze Transform And Structural Model

## Purpose

This document is the detailed reference for how authored `@pyrolyze` code is
understood by the compiler and realized by the runtime.

It is intentionally terse but explicit. The goal is not to teach beginner
authoring. The goal is to state, unambiguously, what structural forms exist,
what they mean, how they lower, and how mount / advert / app-context-override
behavior interacts with those forms.

This document describes the system as it exists today.

## One sentence model

`@pyrolyze` source is not executed as ordinary Python UI code. The compiler
rewrites specific structural forms into runtime calls that build and update a
retained context graph, and the runtime commits emitted structure upward into
the backend-facing UI tree.

## Core distinction: source form vs runtime form

At source level, authored code is expressed in a small number of meaningful
forms:

- slot expressions
- slot calls
- direct component calls
- container calls (`with ...:`)
- keyed loops
- app-context override scopes
- mount scopes

At runtime, those become context-graph operations over:

- `RenderContext`
- slot-owning runtime contexts
- retained bindings
- committed UI / directives / advertisements

The important rule is:

- source syntax determines the structural kind
- runtime state determines reuse, invalidation, mount routing, and retention

## `@pyrolyze` as a structural transform

The `@pyrolyze` decorator is not a normal runtime decorator. In transformed
code, the authored function body is rewritten into calls on a runtime context.

In current code, the public stub still raises in plain Python execution:

- `src/pyrolyze/api.py`

The compiler recognizes `@pyrolyze` functions, analyzes their body, and rewrites
the function into a runtime-facing callable that receives:

- the runtime render/context object
- dirty-state information
- the authored parameters

This is why public authored component functions do not accept runtime-only
parameters like `dirty_state`, even though the lowered runtime function does.

## Structural forms

### 1. Slot expressions

Slot expressions are expressions whose value is produced through the slot-call
machinery and whose result is retained across rerenders.

Typical examples:

- `use_grip(...)`
- `use_state(...)`
- `use_effect(...)`
- `advertise_mount(...)`
- expression trees that contain slot calls and are lowered into `slot_expr`

Current model:

- slot expressions own per-call-site retained context
- call-site state is persisted in a call-site context manager
- internal dirty / refresh behavior is tracked on the call-site context

What matters structurally:

- a slot expression is not just “a function call”
- it may retain subscriptions, effects, advertisements, or locals
- it may refresh without reinvoking the source function

### 2. Slot calls

A slot call is a call whose semantics are provided by the slot-call runtime
layer rather than by direct component/container ownership.

Examples:

- hooks
- external-store readers
- advert publishers

Slot calls are structurally terminal from the point of view of UI ownership.
They may affect runtime state, but they do not themselves create child
component/container boundaries in the way component/container calls do.

### 3. Direct component calls

A direct component call is a bare call expression in authored code where the
callee is understood as a PyRolyze component reference.

Source form:

```python
Child(title)
```

Meaning:

- this is a child component boundary
- not a plain helper call

Important current note:

- this path still exists as `component_call(...)` in runtime/compiler terms
- although the long-term architecture may continue simplifying it, this document
  describes current behavior, not only desired future cleanup

### 4. Container calls

A container call is the structural `with ...:` form.

Source form:

```python
with Row():
    ...
```

Meaning:

- open a retained structural child boundary
- emit the body inside that boundary

This is the runtime path used for:

- ordinary container components
- `mount(...)`
- any intrinsic/container-form helper that participates in container semantics

Container form matters because the body must execute while that boundary is
open. This is not equivalent to a plain direct call.

### 5. Keyed loops

Keyed loops are the structural repeated-child form.

Source form:

```python
for item in keyed(items, key=...):
    ...
```

Meaning:

- repeated structural body
- repeated child slot ownership keyed by the provided key function

Keyed loops are a first-class structural context in the runtime. They are not
just syntax sugar over Python loops.

## Mount and advert are structural, not cosmetic

Mounts and advertisements are part of structural resolution. They decide where
emitted children attach relative to the containing structural parent.

They are not backend-only presentation details.

### `mount(...)`

`mount(...)` is now a normal intrinsic `ComponentRef` in:

- `src/pyrolyze/api.py`

Source form:

```python
with mount(menu):
    Child()
```

Meaning:

- create a retained selector scope
- emit a `MountDirective`
- let parent-side flattening later resolve children under that scope

Important consequences:

- `mount(...)` is used only in container form
- it does not directly attach a child by itself
- it creates a structural scope that affects how emitted children are routed

### `advertise_mount(...)`

`advertise_mount(...)` is not a container form.

It is a slot-call-backed publication of a mount advertisement.

Meaning:

- publish a stable public mount key on the current valid container surface
- map that key to concrete selector terms
- optionally mark one published key as the default advertised mount

Important consequences:

- it is structurally tied to the nearest valid native container owner
- it participates in mount routing, but it does not itself open a container body
- it is retained per slot/call-site and participates in invalidation like other
  slot-call bindings

## Mount resolution rules

These are the current mount rules that matter for compiler/runtime reasoning.

### 1. Resolution is relative to the nearest containing structural container

Selector scopes created by `mount(...)` and advertisements published by
`advertise_mount(...)` resolve relative to the nearest containing structural
container surface.

This is enforced in the runtime, not just implied by documentation.

### 2. Explicit selectors are tried left-to-right

For explicit selector lists:

- selectors are tried in order
- the first viable selector wins
- later selectors are not consulted after a match

This applies to:

- named mount selectors
- `default`
- advertised mount-key selectors

### 3. No explicit selector means ordered default attach resolution

If no explicit selector scope applies, the parent container tries its default
attach mount points in order and takes the first compatible one.

Important precision:

- there is not always one singular “default mount point”
- a parent may have several default attach mount points
- compatibility decides which one wins

### 4. Incompatible attach is an error

If no compatible mount point exists:

- explicit selector resolution raises
- absent-selector default resolution raises
- if the child is attachable only through an explicit mount, runtime raises and
  says explicit mount is required

### 5. Advertised defaults participate before native fallback

If `default` is used in a selector list:

- runtime first checks for a default advertised provider on the current surface
- if one exists, that route wins
- otherwise resolution falls back to native/default mount behavior

## `app_context_override[...]`

`app_context_override[...]` is still a compiler-recognized special form.

It is different from `mount(...)`.

Why:

- `mount(...)` is now a real runtime intrinsic/container callable
- `app_context_override[...]` still depends on compile-time-fixed key shape

Source form:

```python
with app_context_override[THEME_KEY, LOCALE_KEY](theme, locale):
    ...
```

Meaning:

- open a retained structural provider scope
- overlay authored app-context values for the subtree
- preserve fixed structure across rerenders

Important current truth:

- key spec is intentionally compile-time-shaped
- this remains a compiler special form rather than an ordinary helper call
- the runtime treats changes in provider structure as an error

So:

- `mount(...)` is ordinary intrinsic container behavior
- `app_context_override[...]` is still a constrained compiler special form

## Current runtime ownership model

The runtime context graph distinguishes structural ownership from emitted UI.

At a high level:

- structural contexts decide child visitation, reuse, and teardown
- committed UI is propagated upward after successful commit
- retained slot/call-site bindings own subscriptions, effects, adverts, and
  other retained behavior

Important runtime concepts:

- `RenderContext`
- container slot contexts
- keyed loop contexts
- loop item contexts
- component/direct-call contexts
- slot-call / slot-expression retained state

This is why “same source shape” and “same backend tree shape” are related but
not identical debugging views. The context graph may be richer than the mounted
UI tree.

## Current backend-facing emitted structure

The runtime emits a tree containing:

- `UIElement`
- `MountDirective`
- `PyrolyzeMountAdvertisement`

Parent-side flattening and backend reconciliation then turn that into concrete
mount-state application.

This distinction matters:

- authored source does not directly “place widgets”
- it emits structural nodes
- mount resolution and backend placement happen later

## Practical reading rules

When reading authored `@pyrolyze` code, use these rules:

1. Bare component call means child component boundary.
2. `with ...:` means structural container boundary.
3. Hook-like or slot-like calls are not plain function calls; they may be
   retained slot expressions or slot calls.
4. `mount(...)` changes routing scope, not child identity.
5. `advertise_mount(...)` publishes routing metadata on the current container
   surface.
6. `app_context_override[...]` changes subtree app-context scope and is still a
   compiler-recognized special form.

## Why this document exists

This system is powerful, but it is easy to reason about it incorrectly if you
silently substitute ordinary Python function-call intuition for structural
PyRolyze forms.

The important discipline is:

- always ask what structural form the source produced
- then ask what runtime ownership and mount environment that form creates

That is the level at which compiler bugs, runtime bugs, and rerender-vs-fresh
mismatches should be diagnosed.

## Transformation mechanics

This section summarizes how the compiler actually performs the transform and
how runtime-facing symbols are wired into the lowered function.

### AST rewrite strategy

PyRolyze uses Python's `ast` module and versioned kernel rewrite logic to
analyze and lower authored functions.

Important precision:

- the implementation uses AST analysis and reconstruction over Python AST nodes
- the conceptual pattern is “visitor/rewriter”
- but the current kernel is not best described as one single public
  `ast.NodeTransformer` subclass that mechanically rewrites the whole tree

Instead, the current kernel performs:

1. parse
2. detect source forms
3. build a transform plan
4. lower that plan into a new AST
5. validate the lowered module/provenance

The relevant implementation surface is:

- `src/pyrolyze/compiler/facade.py`
- `src/pyrolyze/compiler/kernels/v3_14/kernel.py`
- `src/pyrolyze/compiler/kernels/v3_14/rewrite.py`

So if you are looking for the transform mechanics, the right mental model is:

- plan-driven AST lowering
- not simple textual replacement

### Call-site tagging

Retained runtime behavior depends on stable call-site identity.

The compiler therefore injects structural identity into lowered code.

Current important pieces are:

- module identity
  - `__pyr_module_id`
- slot ids
  - generated from `__pyr_SlotId(...)`
- call-site ids
  - monotonically allocated per lowered call site

In the current kernel:

- `_LoweringState.next_slot_id(...)` builds `SlotId` expressions with:
  - module id
  - slot index
  - source `line_no`
  - `is_top_level`
- `_LoweringState.next_call_site_id(...)` allocates integer call-site ids

Why this exists:

- retained contexts need stable ownership keys
- rerender must find the same retained slot/call-site state again
- emitted UI and mounted backend trees use this identity for normalization,
  attribution, and reuse

This is why source location and synthetic slot numbering both matter.

### Namespace injection and lowered function signature

Lowered `@pyrolyze` functions are not executed in the same calling convention as
their public authored wrapper.

The lowered runtime form receives special compiler/runtime symbols such as:

- `__pyr_ctx`
- `__pyr_module_id`
- runtime helper symbols used by the lowered AST

The lowered function signature is explicitly constructed in the kernel rewrite.
For example, the runtime context argument is injected as:

- `__pyr_ctx`

The compiler facade then executes the lowered module AST into a namespace via:

- `load_transformed_namespace(...)`
- `compile_source(...)`
- `compile_source_with_env(...)`

This matters because:

- public authored component refs remain ordinary-looking callables
- the lowered runtime function is a different callable shape stored in
  component metadata
- runtime-only helper names are injected into the transformed execution
  namespace, not written by the author

In short:

- author writes normal-looking `@pyrolyze` source
- compiler injects runtime calling convention and helper names
- runtime executes the lowered function, not the raw authored body

## Implementation notes and debugging tools

The most useful implementation-facing tools for this model are:

### 1. Compiler transformed-source tooling

Use the compiler facade and debug artifact support to inspect what the authored
 source became.

Relevant surfaces:

- `load_transformed_namespace(...)`
- `emit_transformed_source(...)`
- `build_debug_artifacts_for_source(...)`
- `write_debug_artifacts(...)`

This is the first place to look when you are not sure which structural form the
compiler recognized.

### 2. Visitor/context-graph capture

The runtime graph can be captured and compared through the visitor API in:

- `src/pyrolyze/visitor.py`

Important helpers include:

- `capture_context_graph(...)`
- `compare_context_graphs(...)`
- `walk_context_graph(...)`

Use these when the question is:

- which slot/context owns this subtree?
- which retained context survived or disappeared?
- what changed between two passes?

### 3. Live runtime inspection

`RenderContext` exposes a small set of direct debug helpers in:

- `src/pyrolyze/runtime/context.py`

Useful examples:

- `debug_children_of(...)`
- `debug_is_active(...)`
- `debug_pending_boundaries()`
- `debug_mount_advertisements()`
- `debug_ui(...)`
- `committed_ui()`

These help answer:

- which slots are active?
- what committed UI does the runtime currently believe exists?
- what advertisements are published right now?

### 4. Generic backend and backend generator

For backend-facing structure debugging, the generated generic backend is often
the easiest place to start.

Important modules:

- `src/pyrolyze/testing/generic_backend/`
- `src/pyrolyze/testing/comprehensive_backend/cb.py`

This gives you:

- generated node classes
- generated PyRolyze component refs
- generated mount families
- consistent mount compatibility metadata

This is especially useful when you want to debug:

- mount routing
- host-surface attachment
- rerender-vs-fresh structural mismatches

without a large real backend in the loop.

### 5. Comprehensive backend visual tools

The comprehensive backend visualizer overlays:

- the slot/context graph
- the mounted generic-backend render graph

Relevant code:

- `src/pyrolyze/testing/comprehensive_backend/visualize.py`
- `tests/basic_pyro_shapes.py`
- `tests/test_basic_pyro_shapes.py`

This is the best tool when you need to answer:

- which repeated slot instance owns this rendered node?
- did rerender attach the same subtree under the same structural parent?
- are mount-heavy recursive shapes producing the same graph as a fresh render?

The contributor-oriented summary of these tools is in:

- `docs/contributor/Comprehensive_Backend_And_Shape_Visualization.md`

## Practical debugging sequence

When a structural bug is unclear, the usual best order is:

1. inspect transformed source / debug artifacts
2. inspect or capture the runtime context graph
3. inspect committed UI
4. inspect generated-backend mounted snapshots
5. use the slot/render overlay visualizer for attribution problems

That sequence mirrors the actual system layers:

- authored source
- lowered structure
- runtime ownership
- emitted structure
- backend-facing mounted graph
