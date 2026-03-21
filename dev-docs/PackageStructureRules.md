# Package Structure Rules

## Purpose

These rules define what belongs in the `py-rolyze` package repository and what
should live in separate packages or repositories.


## Core Principle

`py-rolyze` should contain:

- the reusable core runtime
- the compiler and import machinery
- the supported backend integrations that are part of the core distribution
- tests, examples, and working documentation for those reusable pieces

`py-rolyze` should not become the long-term home of one large application.


## Rules

### Keep the core package focused

The main package should primarily contain reusable framework code:

- `src/pyrolyze/`
- runtime
- compiler
- backend adapters
- public API helpers
- test support

Large application implementations should not be added under the top-level repo
unless they are explicitly temporary experiments.

### Example applications are working documentation

The `examples/` directory is for:

- concise end-to-end examples
- working documentation
- demonstration of supported patterns
- small applications that explain a technique or architecture

Examples should stay:

- readable
- contained
- instructional

They may use multiple files if the technique being demonstrated genuinely
requires multiple files, but the purpose must remain documentation and
demonstration.

### Full applications should live in separate packages

A substantial application with its own:

- architecture
- services
- host shell
- persistence
- domain model
- large UI surface
- dedicated roadmap

should be split into a separate package or repository.

That includes applications like Studio once they grow beyond example or design
exploration scope.

### Avoid product code in the core repo when it distorts package design

If application-specific code starts to force:

- special-case runtime hooks
- large app-specific directories
- app-specific public APIs
- product-specific semantic libraries

into the core repo, that is a sign it should move out.

### Semantic UI libraries may be separate packages

Semantic UI libraries are good candidates for separate packages when they are:

- backend-specific
- application-specific
- large enough to warrant their own versioning/release cadence

Examples:

- a Studio-specific semantic UI library
- a richer PySide6 semantic library
- a Textual-specific semantic library

### Backend integrations may be split when they are optional or heavy

If a backend integration becomes:

- large
- optional
- version-sensitive
- independently releasable

it may be better as a separate package than as part of core.


## Specific Guidance For `Studio/`

The current `Studio/` tree is a warning sign.

It contains:

- app code
- host code
- runtime extensions
- services
- tests
- docs

That is application/package structure, not example structure.

Recommended direction:

- do not expand `Studio/` as the long-term packaged application inside
  `py-rolyze`
- treat it as temporary exploration/prototyping material
- move it into a separate package/repo when the API and packaging boundaries are
  ready


## Allowed Exceptions

Exceptions are acceptable when the goal is clearly one of:

- proving a framework technique
- capturing a temporary parity exploration
- creating working documentation for a recommended structure
- shipping a small demonstrator app

In those cases:

- keep the scope intentionally bounded
- document why it lives here
- avoid letting it silently become permanent product code


## Review Checklist

Before adding a new top-level directory or significant subtree, check:

1. Is this reusable framework code or application code?
2. Is this here to demonstrate a technique, or to ship a product?
3. Would this be cleaner as a separate package?
4. Will this distort the public API or package layout of core?
5. Does it belong in `examples/` instead?
6. If it is multi-file example code, is the multi-file structure essential to
   the teaching goal?


## Future Proposals

- add a formal policy for incubating experimental applications before they move
  to separate packages
- add a separate examples-style guide for what counts as "working
  documentation"
- define when a semantic UI library should stay in core vs move out
