# Generic Reconciler Requirements

## Purpose

This document defines the requirements for the generic reconciler effort
described in
[GenericReconciler.md](py-rolyze/dev-docs/GenericReconciler.md).

The goal is to make the reconciler and UI API surface generic enough that:

- PyRolyze core does not have to know one fixed UI element set
- a UI library can live outside the main `py-rolyze` package
- a backend-specific implementation can be published as a separate package
- rich applications can be built reactively instead of falling back to large
  imperative shells

This document is requirements-first. It is not the implementation plan.


## Current Context

The current Studio extension experiment in
[Studio/runtime_ext/studio_elements.py](py-rolyze/Studio/runtime_ext/studio_elements.py)
is useful as a pressure test, but it is not the public shape we want to ship.

It proves there is real demand for:

- more complete PySide6 support
- richer shell and model-backed controls
- generated UI-library surfaces for large toolkits
- custom composite widgets that still behave as one reconciler node

It also shows why the solution should not be a Studio-specific public API.


## Understanding Of The Goal

The goal is not "make PySide6 support better" in isolation.

The goal is:

- define a generic reconciler contract that is independent of any one toolkit
- define the minimum backend contract necessary to drive reconciliation
- define the minimum UI-library contract necessary to expose author-facing UI
  callables
- keep PyRolyze's reactive execution model central
- allow richer backends and richer UI libraries to be implemented outside core

This should support:

- the current retained-widget backends
- toolkit-specific UI libraries
- high-level portable UI libraries
- multiple render roots using different backends in one process

This explicitly does **not** require:

- mixing different UI backends inside the same `RenderContext`
- a single subtree containing both Tk and Qt widgets


## Terminology

The following names should be used consistently:

- `UiLibrary`
  - author-facing class namespace containing `@pyrolyse` UI callables
- `UiBackend`
  - backend implementation for one toolkit family
- `UiCatalog`
  - per-root flattened lookup table of installed UI element kinds
- `UiWidgetSpec`
  - backend-owned immutable description of one widget kind
- `UiPropSpec`
  - backend-owned immutable description of one prop

The older term "semantic library" is close, but `UiLibrary` is the preferred
name going forward.


## Independence Boundaries

The most important design question is: what must be independent, and what must
remain backend-specific?

### Core reconciler concerns that must be independent

The following must be backend-agnostic:

- node identity model
- prop/event diffing rules at the abstract level
- child placement semantics at the abstract level
- owner commit state
- reuse vs replace decisions at the abstract level
- subtree disposal ordering
- recovery/remount behavior on backend failure
- backend identity swap handling
- batching over one committed owner region

These are core reconciliation semantics.

### Concerns that must remain backend-specific

The following are inherently backend-specific:

- how a widget/control/native node is created
- what host object type represents the mounted node
- how child placement is performed in that backend
- how visibility, enablement, styling, and model hookup are expressed
- which props are constructor-only vs dynamically updateable
- event source wiring
- UI-thread assertions and marshalling
- toolkit-specific object lifetime rules

These should be extension points, not core logic.

### Concerns that should be library-specific

The following belong to `UiLibrary` definitions rather than the core
reconciler:

- which UI callables exist
- how those callables are grouped and documented
- which generated helper shape they use
- whether a callable is eligible for the packed-`kwds` optimization


## Primary Requirements

## 1. Core Reconciler Must Remain Toolkit-Agnostic

The generic reconciler must not hard-code:

- PySide6 classes
- tkinter widget classes
- Studio-only node kinds
- one fixed UI registry

The reconciler should only operate over normalized node specs plus backend
operations.


## 2. `UiLibrary` Must Be Replaceable

It must be possible to provide a `UiLibrary` as a separate package.

That package must be able to define:

- its own `@pyrolyse` UI callables
- its own generated or hand-written widget set
- its own backend-specific or portable API surface

without editing `py-rolyze` core.


## 3. `UiBackend` Must Be Replaceable

It must be possible to implement backend support as a separate package.

A backend package must be able to provide:

- binding creation
- binding update
- child placement
- child detachment
- disposal
- reuse decisions
- thread assertions
- UI-thread posting
- widget specs for the installed UI libraries

without editing `py-rolyze` core.


## 4. Rich Applications Must Still Be Reactive

The generic reconciler project must preserve PyRolyze's main value:

- author code stays reactive
- state/effect/grip/event flows still drive UI changes declaratively
- partial rerender stays the primary update model

New UI-provider APIs must not require the application author to reintroduce
large imperative synchronization code for ordinary UI behavior.


## 5. Multiple `UiLibrary` Classes Must Coexist Per Root

One render root must be able to install many UI libraries.

Examples:

- built-in core UI library
- generated `PySide6UiLibrary`
- generated `TkUiLibrary`
- app-specific custom UI library

Requirement:

- one backend per root
- many UI libraries per root
- duplicate `kind` names must be rejected during installation unless a future
  qualification scheme is introduced

This means per-root registration must build a flattened `UiCatalog`.


## 6. One Render Context Must Have One Backend

Each `RenderContext` or owner region must be bound to one backend identity.

Requirement:

- no mixed backend nodes in one reconciled owner tree

Allowed:

- one app process with multiple roots/windows
- different roots using different backends

This is a non-goal boundary and should remain explicit in the design.


## 7. Compatibility Must Be Checked At Registration Time

If a render root installs:

- one `UiBackend`
- many `UiLibrary` classes

the system must validate:

- each source element `kind` is unique within that root
- each installed `UiLibrary` has either:
  - an explicit backend adapter
  - or an identity mapping for direct toolkit kinds
- each source `kind` resolves to a backend-known target widget kind
- the backend can build a `UiWidgetSpec` for each resolved target widget kind

If not, installation must fail fast.

This avoids needing a separate UI-library identity field on every `UIElement`
as long as `kind` names remain unique inside the root.


## 8. Backend Adapters Must Bridge Abstract `UiLibrary` Kinds

Not every installed `UiLibrary` should be expected to expose backend-native
widget kinds directly.

Example:

- `CoreUiLibrary.button(label=..., on_press=...)`
- `PySide6Backend` may actually mount that as a normalized `QPushButton`
  widget spec using backend-native prop names like `text`

Requirement:

- a backend must be able to install an adapter for a `UiLibrary`
- the adapter must map source `kind` and source props onto a target
  backend-owned `UiWidgetSpec`
- remount/update rules come from the target `UiWidgetSpec`, not the source
  `UiLibrary`

This is required so:

- the current built-in cross-platform element API can continue to exist
- toolkit-generated UI libraries can coexist with it
- one backend can support both direct toolkit widgets and higher-level
  portable UI elements

The adapter layer should be explicit and backend-owned.


## 9. Prop Categories Must Be Explicit

The backend-owned widget spec must distinguish at least three prop categories:

- `dynamic`
  - valid at create and update time
  - update in place
- `init_only`
  - valid input for creation
  - if changed later, remount the widget
- `readonly`
  - not author-settable
  - may be observable but does not belong in the author-facing prop surface

This is essential because PyRolyze exposes one declarative prop surface to
authors and does not expose separate create/update APIs.


## 10. Constructor-Only Props Must Remount On Change

If a prop is constructor-only and the value changes, the backend must treat it
as identity-affecting and remount the node.

The default runtime behavior should be:

- remount in both debug and production

Optional diagnostics may include:

- trace or warning that an init-only prop triggered remount
- stricter testing mode that errors instead of remounting

But the semantics should not diverge between debug and production.


## 11. Widget Specs Must Be Frozen Dataclasses

Backend widget metadata must not be represented as ad hoc tuples or dicts of
tuples.

Requirement:

- backend modules define frozen dataclasses for widget and prop specs
- mapping fields should use `frozendict`
- generated UI-library code should not embed these dataclass definitions

At minimum the backend side should have:

- `UiPropSpec`
- `UiWidgetSpec`

`UiWidgetSpec` should encompass:

- kind
- mounted widget type or backend binding key
- immutable prop spec map
- child policy
- any future backend rules needed for remount/update decisions


## 12. Generated UI Libraries Must Include Constructor And Setter Inputs

For generated toolkit-backed UI libraries:

- constructor parameters should be available in the generated callable surface
- updateable setter/property values should also be available in the generated
  callable surface

The backend spec layer then decides whether each prop is:

- dynamic
- init-only
- readonly

This is necessary because `UIElement.props` is the single value surface used
for both creation and update.


## 13. Toolkit Discovery Must Use Real Toolkit Metadata

Generation should use toolkit-specific sources rather than plain
`inspect.signature()` alone.

Examples:

- PySide6:
  - `.pyi` constructor signatures
  - `QMetaObject` property metadata
- tkinter:
  - constructor/configure surface
  - widget options/configure metadata

The generated UI surface should reflect the toolkit's real capabilities as
closely as practical.


## 14. Packed-`kwds` Optimization Must Be Explicit

The optimized `__element` path is allowed, but must be explicit and narrowly
triggered.

Requirement:

- optimization is selected by the authored helper signature
- `UiLibrary` helper is `cls.__element(...)`
- if `__element` has a trailing keyword-only parameter named `kwds`, the
  compiler may lower the private `__pyr_*` runtime function to use packed
  keyword forwarding

This is an internal optimization for thin generated native wrappers.

It must not change the public author-facing callable signature.


## 14. Generated Wrapper Optimization Must Remain Debuggable

Even if packed-`kwds` lowering is implemented, the compiler must retain a
debug-friendly way to disable it for diagnosis and golden readability.

This should be a compiler/transform flag, not an environment variable.


## 15. Composite Widgets Must Appear As One Node

The design must support backend-native composite widgets that:

- expose one head/native widget to the parent/backend
- internally manage child attachment at locations that are not the head widget
- still appear to the reconciler as one node

This enables custom widgets that are compatible with a native toolkit backend
while still fitting the reconciler model.

The required backend binding contract is:

- expose the head widget used for parent attachment
- `place_child(child, index)`
- `detach_child(child)`
- `dispose()`
- `update_props(...)`

This requirement fits the current single child-region model. Multi-region child
placement is explicitly out of scope here.


## 16. The Public API Must Support Two Layers

There should be two UI-library layers:

### Portable layer

Small, curated, cross-backend kinds for general usage.

Examples:

- button
- text field
- toggle
- section
- row

### Backend-specific layer

Toolkit-specific libraries for full power.

Examples:

- `PySide6UiLibrary`
- `TkUiLibrary`
- future packages for Toga, Dear PyGui, Flet, or Textual

This is required because the full toolkit surfaces are too different to force
through one portable API.


## Contradictory Requirements

Several requirements naturally pull against each other.

### A. Minimal core vs rich toolkit access

Tension:

- core should stay small and toolkit-agnostic
- users want rich toolkit-specific capability

Resolution:

- keep core reconciler generic
- let backends own `UiWidgetSpec` and binding logic
- let toolkit-specific `UiLibrary` classes live outside core when appropriate


### B. Explicit, IDE-friendly APIs vs very large toolkit surfaces

Tension:

- explicit parameters are good for IDE support and readability
- generated toolkit APIs can become huge

Resolution:

- keep public callables explicit
- use generation to avoid hand maintenance
- allow internal packed-`kwds` lowering for thin wrappers


### C. One prop surface vs different create/update semantics

Tension:

- authors only see one declarative prop surface
- toolkits distinguish constructor-only vs updateable values

Resolution:

- backend spec layer classifies props as `dynamic`, `init_only`, or `readonly`
- init-only changes remount


### D. Coexisting libraries vs no UI-library id on `UIElement`

Tension:

- multiple libraries should coexist
- `UIElement` should stay small

Resolution:

- require globally unique `kind` names within one render root
- reject collisions at installation time
- reserve explicit qualification only if collisions become common later


## Future Proposals

Useful but not required for the first implementation:

- qualified kind names if library collisions become common
- richer generated event metadata
- optional remount diagnostics with trace tooling
- higher-level builder APIs for generated toolkit libraries
- support packages that emit frozen spec modules directly from toolkit metadata
