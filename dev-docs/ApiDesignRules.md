# API Design Rules

## Purpose

These are generic API design rules for `py-rolyze`. They apply beyond PyRolyze
source syntax and beyond semantic UI libraries.


## Rules

### Prefer explicit signatures

Prefer explicit named parameters over `*args` and `**kwargs` when the supported
shape is known.

Reason:

- better IDE support
- better type inference
- clearer docs
- fewer ambiguous call forms

### Keep annotations complete and precise

Public API examples and proposals should carry full type annotations when
practical.

Reason:

- IDE guidance
- easier review
- fewer hidden assumptions

### Preserve semantic boundary coercions

If an API boundary intentionally normalizes values, preserve that normalization
in examples and proposals.

Examples:

- `bool(visible)`
- `int(current_index)`
- `tuple(options)`

Do not remove those conversions casually. They are often part of the semantic
contract, not just style noise.

### Do not optimize for neatness at the cost of semantics

A shorter or less repetitive API shape is not better if it changes the meaning,
blurs ownership, or hides important constraints.

### Keep one concept in one place

Do not duplicate the same concept across multiple public entry points unless
there is a strong explicit reason.

### Prefer explicit registration over implicit discovery

When a system has to know what is installed or supported, favor explicit
registration objects and explicit installation calls over broad reflective
discovery.

### Separate authoring surface from metadata and runtime internals

Keep distinct:

- author-facing APIs
- registration/manifest metadata
- runtime-only helpers

Mixing them makes APIs harder to reason about and easier to misuse.


## Review Checklist

Before accepting an API proposal, check:

1. Is the callable surface explicit?
2. Are the types precise enough for IDEs?
3. Are any coercions being removed that actually matter semantically?
4. Is the proposal cleaner without changing meaning?
5. Is registration explicit enough to inspect and test?
