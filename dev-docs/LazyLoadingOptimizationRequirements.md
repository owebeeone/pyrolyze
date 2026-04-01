# Lazy Loading Optimization Requirements

## Purpose

Define requirements for reducing the startup, memory, and generated-surface cost
of large native UI libraries in PyRolyze.

This document focuses on two related problems:

- lazy loading of native class and member definitions
- reduction of generated surface noise caused by repeated parameter-name sets

The immediate motivating backend is PySide6, but the requirements should be
usable by future backends such as UIKit.

## Problem Statement

PyRolyze currently pays a large static cost when a generated backend exposes a
wide native API surface.

The most visible symptoms are:

- large import-time metadata payloads
- eager materialization of many widget definitions that most apps never use
- repeated storage of near-identical parameter-name sets across related widgets
- generated files whose size and readability are dominated by field-name
  proliferation rather than distinct semantics

The PySide6 generated library shows this clearly:

- inherited widget families repeat large common property sets
- constructor, prop, and method parameter names recur across many widgets
- the generated Python source contains a large amount of repeated text that does
  not correspond to equally large semantic variation

This is now a design constraint, not just a code-generation style issue.

## Goals

- Reduce import-time and startup overhead for large generated UI libraries.
- Reduce memory footprint of metadata and wrapper definitions.
- Preserve PyRolyze's explicit author-facing API semantics.
- Preserve complete registration and runtime semantics for supported widgets.
- Allow backends to expose large libraries without requiring eager realization
  of all classes, selectors, properties, methods, and constants.
- Dramatically reduce repeated parameter-name expansion in generated surfaces.
- Keep the design compatible with curated semantic libraries and future lazy
  native bridges such as UIKit.

## Non-Goals

- This is not a proposal to collapse public author-facing semantics into an
  untyped `**kwargs` API.
- This is not a proposal to remove explicit widget/property registration.
- This is not a proposal to rely purely on live reflection for all metadata.
- This is not a requirement that every backend expose the full native toolkit.
- This is not primarily a formatting cleanup effort; the target is runtime and
  package-surface efficiency.

## Terminology

### Lazy Definition Loading

Lazy definition loading means PyRolyze knows how to find native classes and
their metadata without eagerly materializing all Python-side wrapper and
descriptor objects at import time.

Examples:

- a backend may know that `QLabel` exists without eagerly building every Python
  wrapper object related to it
- a backend may materialize `QLabel` metadata only when a PyRolyze surface first
  references that widget
- method and property metadata may be loaded member-by-member rather than all at
  once for the whole toolkit

### Surface Compaction

Surface compaction means representing repeated parameter-name and metadata sets
once, then reusing them across widget definitions instead of spelling them out
fully in each generated entry.

This does not mean hiding semantics from authored code. It means reducing
redundant representation inside generated registration artifacts and internal
surfaces.

## Design Constraints

The following existing PyRolyze rules still apply:

- author-facing APIs, registration metadata, and runtime-only helpers must stay
  distinct
- explicit semantic coercions at API boundaries must remain visible where they
  matter
- supported surfaces should remain inspectable and testable
- optimization for neatness must not erase semantic differences

These constraints rule out a simplistic "replace everything with generic
keyword bags" approach.

## Requirements

## 1. Lazy Loading Architecture

### R1.1 Metadata Must Be Indexable Without Full Realization

The generated backend must support a lightweight index that can answer:

- which widgets are available
- where their metadata lives
- whether a widget belongs to a shared family or template
- which members exist for that widget

This index must be materially cheaper to load than the current fully expanded
generated module.

### R1.2 Widget Definitions Must Load On Demand

The backend must be able to defer realization of widget definitions until first
use.

At minimum, first use should include:

- first authored reference to a widget surface
- first mount of that widget kind
- first explicit introspection request for that widget's metadata

Loading one widget definition must not force eager realization of the entire
backend surface.

### R1.3 Member Definitions Must Support Lazy Realization

Within one widget definition, large property and method sets should support
member-level laziness where practical.

Required cases:

- properties
- methods
- events
- mount definitions where a family is large

This requirement does not mandate maximal fine-grained laziness if a coarser
family-level cache is more practical, but the system must not require eager
construction of every member descriptor in the toolkit.

### R1.4 Loading Must Be Cached And Stable

Once a definition is realized, the backend must reuse the existing realized
objects rather than rebuilding them repeatedly.

The cache must be:

- identity-stable for the lifetime of the process unless explicitly invalidated
- safe for repeated lookups
- inspectable in tests

### R1.5 Failure Modes Must Be Explicit

If a requested widget or member cannot be loaded, the failure should be
deterministic and attributable.

At minimum, diagnostics should distinguish:

- unknown widget kind
- known widget with unavailable member
- malformed generated metadata
- backend version mismatch

## 2. Generated Surface Compaction

### R2.1 Repeated Parameter Sets Must Be Factored

The generator must support extracting common constructor/property/method
parameter-name sets so they are defined once and reused across related widgets.

This applies especially to inherited families such as:

- widget base properties
- geometry and size properties
- text/control properties
- common method parameter groups such as margins, sizes, positions, ranges, and
  alignment-like sets

### R2.2 Factoring Must Preserve Explicit Semantics

Factoring common sets must not erase per-widget differences.

The compaction model must still allow:

- additions
- exclusions
- overrides
- mode changes
- annotation changes
- remount/identity differences

The internal reuse mechanism should be compositional rather than all-or-nothing.

### R2.3 Parameter Names Must Have Canonical Shared Identities

Repeated field names such as `parent`, `enabled`, `visible`, `objectName`,
`minimumWidth`, `maximumWidth`, `left`, `top`, `right`, and `bottom` should not
be represented as unrelated repeated string payloads throughout the generated
surface.

The system should introduce canonical shared identities for common names or name
groups.

Acceptable techniques include:

- interned field-name tables
- shared parameter-group declarations
- reusable metadata fragments
- family templates with patch layers

The chosen mechanism must remain inspectable and deterministic.

### R2.4 Compaction Must Operate Below The Author Surface

The primary compaction target is generated registration and runtime metadata,
not necessarily the authored callable signature.

PyRolyze may still choose to present explicit public parameters for curated
semantic libraries where that is the right authoring experience.

This requirement exists to avoid conflating:

- storage optimization
- runtime loading behavior
- user-facing signature design

### R2.5 The Backend Must Support Shared Family Definitions

The generator should support declaring common families such as:

- base widget props
- control props
- scrollable props
- layout container props
- text input props

One widget definition should be able to say, in effect:

- include family A
- include family B
- override these three fields
- exclude these two read-only members

This requirement is central to reducing the PySide6 surface explosion.

## 3. Runtime Semantics

### R3.1 Resolution Must Produce Ordinary Runtime Specs

Even if metadata is stored compactly and loaded lazily, the runtime must still
be able to resolve a widget into ordinary `UiWidgetSpec`-like runtime data for
mounting, validation, and reconciliation.

The mount engine and backend adapters should not have to know whether a spec was
stored eagerly or realized lazily.

### R3.2 Resolution Cost Must Be Front-Loaded Per Widget, Not Per Update

Lazy loading is acceptable on first access. It is not acceptable if normal
rerender/update paths repeatedly pay metadata-resolution cost.

Once a widget family is warm:

- repeated mounts should reuse cached descriptors
- repeated prop updates should not re-expand shared parameter groups
- normal event/update traffic should remain on resolved runtime structures

### R3.3 Surface Compaction Must Not Change Public Semantics

Compaction must be representation-only unless the user explicitly opts into a
different authored API design.

That means:

- no silent change from explicit parameters to free-form keyword bags
- no silent loss of annotation precision
- no silent removal of coercion semantics
- no silent merging of distinct members that happen to share a name

## 4. Introspection And Tooling

### R4.1 Introspection Must Remain Available

Developers and tests must still be able to inspect:

- what widgets are available
- what props/events/methods a widget exposes
- which metadata families a widget inherits from
- whether a definition is loaded or still deferred

### R4.2 Generated Docs Must Not Require Full Expansion

Documentation generation should be able to read the compact metadata format and
produce full docs without requiring the shipping runtime module to embed a fully
expanded copy of every widget definition.

### R4.3 Test Surfaces Must Cover Cold And Warm Paths

The test plan for this optimization must explicitly cover:

- cold lookup of one widget
- repeated lookup of the same widget
- loading several related widgets sharing one family definition
- loading one widget without forcing unrelated families
- correct override and exclusion behavior after compaction

## 5. UIKit Readiness Requirements

These optimizations should be designed so that a future UIKit backend can use
them directly.

That implies:

- the metadata model must not assume Qt-only concepts
- family/group factoring must work for property-heavy native frameworks in
  general
- lazy definition loading must support native bridges where runtime lookup and
  ABI metadata are more expensive than pure Python import

The UIKit backend should be able to reuse the same high-level pattern:

- lightweight index at startup
- load widget/class definitions on first use
- load member metadata on demand where practical
- share common property families across control hierarchies

## Recommended Technical Direction

This document does not lock in one implementation, but the following direction
appears most consistent with the requirements.

### A. Split The Current Generated Module

Instead of one large fully expanded Python source file, split the surface into:

- a lightweight registry index
- compact metadata fragments and family declarations
- a resolver that realizes full runtime specs on demand
- optional generated author-facing wrappers kept separate from the storage layer

### B. Introduce Family / Fragment Tables

Represent common metadata once:

- field-name atoms
- shared prop groups
- shared method parameter groups
- inherited widget family fragments

Then let widget definitions reference those fragments plus local patches.

### C. Use Patch-Based Realization

Resolve one widget definition by:

1. loading referenced family fragments
2. merging them in deterministic order
3. applying widget-local additions/exclusions/overrides
4. materializing the final runtime spec
5. caching the result

This keeps explicit semantics while removing most repeated text.

### D. Keep Curated Author Surfaces Optional

For large raw native libraries, the optimized storage model should not force
equally large hand-authored-like public signatures.

PyRolyze should remain free to expose:

- a compact internal/generated native surface
- a smaller curated semantic author surface
- or both, depending on backend goals

## Acceptance Criteria

The optimization should be considered successful only if all of the following
are true.

### Cold-Start Criteria

- Importing a generated large backend no longer requires eager construction of
  all widget specs.
- Loading one small widget subset does not materialize the full toolkit.

### Representation Criteria

- Common parameter-name sets are stored once and reused.
- Related widgets visibly share family metadata rather than repeating it in full.

### Semantic Criteria

- Runtime mounting behavior is unchanged for supported widgets.
- Public authored semantics are unchanged unless intentionally redesigned.
- Per-widget overrides and remount/identity semantics remain correct.

### Tooling Criteria

- Tests can assert whether a widget definition is cold or realized.
- Docs/introspection can still enumerate the supported surface.

## Open Design Questions

- How much of the current public generated callable surface should remain fully
  explicit for giant native libraries?
- Should author-facing explicit signatures be generated only for curated or
  commonly used widgets, with the wider native surface exposed through a
  different layer?
- Should field-name interning be implemented as Python constants, numeric atoms,
  or compact table indexes?
- Should member-level laziness stop at the widget boundary, or should very large
  widgets support property/method family loading separately?
- How should compact metadata be serialized for code generation, docs, and
  tests so the same source of truth is reused?

## Immediate Next Step

Before implementation, produce a follow-on design doc that proposes:

- the compact metadata model
- the family/fragment merge rules
- cache and invalidation behavior
- generated-code layout changes
- how PySide6 can migrate without changing runtime semantics
