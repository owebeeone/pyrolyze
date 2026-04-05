# Runtime Call Resolution And Site Metadata

## Purpose

This document describes the runtime-layer machinery used to resolve explicit
call-indirection helpers and to attach site metadata to the active slot graph.

This is not the source-level contract. For authored source semantics, see:

- [../design/Pyrolyze_Transform_And_Structural_Model.md](../design/Pyrolyze_Transform_And_Structural_Model.md)

This document is about how the runtime currently implements:

- explicit call-indirection wrappers
- intrinsic cast helpers
- nullable call targets
- site metadata capture and visitor exposure

## Main pieces

The runtime machinery currently lives in:

- `src/pyrolyze/runtime/pyro_call.py`
- `src/pyrolyze/runtime/context.py`
- `src/pyrolyze/runtime/slot_expr.py`
- `src/pyrolyze/runtime/call_site_context.py`
- `src/pyrolyze/visitor.py`

## Two kinds of indirection

### 1. Intrinsic cast helpers

The public authored helpers are:

- `component(...)`
- `slotted(...)`

These are marked with one shared intrinsic-cast marker and resolved by peeling
off the first positional callable argument.

This is the preferred source-level way to add explicit call intent.

### 2. Runtime wraps

The runtime also supports explicit wrapper objects:

- `PyrolyzeWrap`
- `PyrolyzeComponentWrap`
- `PyrolyzeSlottedWrap`

These are not the primary public source contract. They are runtime machinery
that can:

- resolve to a real callable or `None`
- adjust args / kwargs
- provide `RuntimeSiteMetadata`

They also let tests and tooling attach structured metadata without inventing
new compiler rules first.

## Resolution model

The shared runtime resolver is:

- `resolve_runtime_pyro_call(...)`

It performs resolution in this order:

1. peel intrinsic cast helpers
2. if the current callable is a `PyrolyzeWrap`, collect its metadata and call
   `resolve(...)`
3. repeat until the current callable is neither an intrinsic cast helper nor a
   wrap
4. return:
   - final callable or `None`
   - final args
   - final kwargs
   - merged metadata

Important consequences:

- nested intrinsic casts collapse naturally
- nested wraps also collapse
- wraps over cast helpers and cast helpers over wraps both normalize through the
  same resolver

## Nullable target behavior

Resolution may produce:

- a real callable target
- `None`

`None` means:

- no call target for this pass

Current consequences:

- `container_call(...)` returns `None`
- `component_call(...)` returns early
- slot-call paths currently treat “no callable target” as invalid unless that
  path is explicitly taught otherwise

This is why the new container lowering shape matters:

```python
if handle := ctx.container_call(...):
    with handle:
        ...
```

This lets one authored site become inactive without forcing the runtime to fake
an inert context manager.

## Site metadata

`RuntimeSiteMetadata` is a generic `(key, value)` pair attached to an active
site during runtime resolution.

This metadata is intended for:

- graph visitors
- fuzz tooling
- mount / advert analysis
- app-specific inspection

It is not currently interpreted by the core runtime.

## Where metadata is stored

Metadata is stored against the site that actually resolved the call.

Current storage points:

- `ComponentCallSlotContext.site_metadata`
- `ContainerSlotContext.site_metadata`
- `SlotCallSlotContext.site_metadata`
- `CallSiteContext.site_metadata` for slot-expression call sites

The slot-expression case is the subtle one:

- the metadata is conceptually about the slot-call site
- runtime reaches it through the call-site context manager
- the visitor currently exposes it as slot-context-adjacent data keyed by the
  slot-call `slot_id`

This is intentionally the simple first cut.

## Slot path attribution

Wrap-provided metadata currently receives a `SlotIdPath`.

This path is used to distinguish:

- repeated keyed-loop instances
- reused helper shapes under different parents
- container/component sites that share local slot ids but live under different
  owner chains

The first cut uses the existing slot ancestry model. If needed later, this can
  be refined further without changing the basic metadata contract.

## Visitor exposure

The visitor capture path now exposes site metadata through:

- `CapturedSiteMetadata`
- `CapturedContext.site_metadata`

This means callers can stay on the current context-graph API and still inspect:

- component site metadata
- container site metadata
- slot-call site metadata

without a separate call-site graph type.

This is deliberately a pragmatic compromise:

- the runtime may have walked call-site internals to find the metadata
- the captured graph still exposes it as data hanging off the nearest captured
  context

That is sufficient for current debugging and fuzz tooling.

## Why this is runtime machinery, not compiler machinery

The compiler only contributes two essential things here:

- source syntax still decides direct-call vs container-call lowering
- intrinsic cast helpers are visible through the existing marker-based import
  detection path

Everything else is runtime:

- peeling the actual target callable out of indirection helpers
- deciding whether the resolved target is absent
- collecting wrap-provided metadata
- storing metadata on active sites
- exposing it through the visitor graph

So this entire mechanism belongs on the runtime/contributor side, not in the
core authored-structure reference.
