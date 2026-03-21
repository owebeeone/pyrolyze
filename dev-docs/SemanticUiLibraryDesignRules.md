# Semantic UI Library Design Rules

## Purpose

These rules apply specifically to semantic UI library design in `py-rolyze`.

This is the narrower category that covers semantic element libraries,
registration/manifests, and the relationship between author-facing reactive
callables and backend/runtime support.


## Rules

### No compiler internals in hand-written source

Never write compiler-emitted names such as `__pyr_*` in:

- examples
- semantic libraries
- author-facing design examples

### One semantic element, one public callable form

Do not introduce multiple public callable surfaces for the same semantic
element unless there is a strong explicit reason.

### Keep semantic identity separate from backend identity

Do not make a semantic element point directly at a backend singleton or backend
implementation object.

Keep separate:

- semantic library identity
- backend family / implementation identity
- runtime compatibility checks

### Keep authoring, registration, and runtime helpers separate

For every semantic-library proposal, identify:

1. the author-facing callable surface
2. the registration/manifest surface
3. the runtime-only helper surface

If one proposal mixes those layers, rewrite it before presenting it.

### Preserve semantic normalization at source boundaries

When semantic UI helper code intentionally normalizes values, preserve those
conversions.

Examples:

- `bool(visible)`
- `int(current_index)`
- `tuple(options)`

Removing them can materially change semantics.

### Use explicit registration

Semantic libraries may use:

- modules
- classes
- decorators
- generated manifests

But backend/runtime support should consume explicit registration data rather
than depend on fragile implicit reflection.


## Review Checklist

Before accepting a semantic UI library proposal, check:

1. What is the one public callable form per semantic element?
2. What identifies the semantic library?
3. What registration object does the backend/runtime consume?
4. Are semantic coercions preserved?
5. Is backend compatibility kept separate from semantic identity?
