# AGENTS

## Scope
This file defines repository-specific coding instructions for `py-rolyze`.

## Design Rules
- Prefer `@dataclass` for classes that primarily hold state.
- Keep transport clients small and explicit; protocol conversion should be easy to inspect.
- Keep type annotations complete and precise so IDE inference remains strong.

## Paths in version control
- Do not store absolute filesystem paths in any committed file; use paths relative to this repository (the `pyrolyze` submodule root). If a path would cross into a parent monorepo checkout, truncate to the closest submodule root instead of embedding machine-specific prefixes.
- Do not treat `scratch/` as a stable dependency location for committed code, tests, or docs. Use it only for exploratory or generated work that is intentionally not part of the supported checked-in surface.
- If a checked-in test can optionally use a scratch asset, it must skip cleanly when that asset is absent rather than failing the suite.

## PyRolyze Source Rules
- In hand-written PyRolyze source, never write compiler-internal names such as `__pyr_*`.
- `__pyr_*` symbols are compiler-emitted implementation details only.
- Hand-written PyRolyze examples, UI libraries, and helper surfaces must use public source forms such as `@pyrolyze`, `call_native(...)`, `PyrolyzeHandler[...]`, and public function/class names.
- If a source example or proposed library API requires `__pyr_*` names, rewrite it into author-facing PyRolyze source form instead of showing lowered code.
- Preserve the distinction between:
  - author-facing reactive callables
  - registration/manifests/descriptors
  - internal runtime/helper utilities
- Do not introduce a second public callable surface for the same semantic element unless explicitly requested.
- Before proposing a PyRolyze API shape, identify:
  1. the author-facing callable surface
  2. the registration/manifest surface
  3. the runtime-only helper surface
- If one proposal mixes those layers, rewrite it before presenting it.
- Preserve explicit semantic coercions at API boundaries. Do not remove conversions such as `bool(...)`, `int(...)`, or `tuple(...)` when they are part of the intended source/runtime contract.
- See `dev-docs/ApiDesignRules.md` for generic API design rules.
- See `dev-docs/SemanticUiLibraryDesignRules.md` for semantic UI library rules.
- See `dev-docs/PackageStructureRules.md` for package and example layout rules.

## Development Process (TDD)
Use a strict red/green/refactor workflow for all behavior changes.

1. Red: Add or update tests first to express the expected behavior, then run the smallest relevant test target and confirm it fails.
2. Green: Implement the minimal code change required to make the failing test pass.
3. Refactor: Improve structure and readability while preserving behavior.
4. Verify targeted scope: Re-run the focused test subset.
5. Verify full regression: Run the full test suite before finalizing.

## Roll-Build Method
- When the user asks for a phased rollout using the roll-build method, start from a clean git tree and tag that point before implementation begins.
- Use the requested start tag name when one is given. If none is given, ask or use a clearly scoped phase-start tag name.
- Implement one phase at a time.
- After a phase is complete, only commit and tag it if:
  - the phase goal is actually met
  - focused verification passes
  - the remaining ambiguities are minor and non-blocking
- Tag completed phases using the naming scheme the user requested. If a phase is only partially complete, use an explicit partial tag name rather than pretending the phase is done.
- If there are no more phases, or if confidence drops because of material ambiguity or instability, stop and wait instead of forcing the next phase.
- If work starts cycling on the same persistent bug or bug family, stop, report the cycle clearly, and ask for direction.

## When To Push Back On Roll-Build
- Push back when the next phase has too many unresolved ambiguities to produce a trustworthy checkpoint.
- Push back when the requested phase is too large or too coupled to complete safely as one checkpoint.
- Push back when implementation reveals facts that materially break the current design or plan assumptions.
- Push back when the resulting checkpoint would be misleadingly partial, unstable, or hard to recover from.

## Test Framework Selection
- For new end-to-end PyRolyze tests that exercise authored component code, dynamic mount behavior, advert routing, or rerender graph changes, prefer the generic backend framework in `pyrolyze.testing.generic_backend` when it keeps the test clearer than ad hoc scaffolding.
- Keep narrow compiler golden tests and tiny runtime unit tests on simpler direct scaffolding when that remains clearer.

## Test Commands
- Focused tests: `uv run --with pytest --with pytest-cov pytest <test-path> -q`
- Full suite: `uv run --with pytest --with pytest-cov pytest -q`
