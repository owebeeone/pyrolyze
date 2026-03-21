# AGENTS

## Scope
This file defines repository-specific coding instructions for `py-rolyze`.

## Design Rules
- Prefer `@dataclass` for classes that primarily hold state.
- Keep transport clients small and explicit; protocol conversion should be easy to inspect.
- Keep type annotations complete and precise so IDE inference remains strong.

## PyRolyze Source Rules
- In hand-written PyRolyze source, never write compiler-internal names such as `__pyr_*`.
- `__pyr_*` symbols are compiler-emitted implementation details only.
- Hand-written PyRolyze examples, UI libraries, and helper surfaces must use public source forms such as `@pyrolyse`, `call_native(...)`, `PyrolyzeHandler[...]`, and public function/class names.
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
- See `/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/dev-docs/ApiDesignRules.md` for generic API design rules.
- See `/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/dev-docs/SemanticUiLibraryDesignRules.md` for semantic UI library rules.
- See `/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/dev-docs/PackageStructureRules.md` for package and example layout rules.

## Development Process (TDD)
Use a strict red/green/refactor workflow for all behavior changes.

1. Red: Add or update tests first to express the expected behavior, then run the smallest relevant test target and confirm it fails.
2. Green: Implement the minimal code change required to make the failing test pass.
3. Refactor: Improve structure and readability while preserving behavior.
4. Verify targeted scope: Re-run the focused test subset.
5. Verify full regression: Run the full test suite before finalizing.

## Test Commands
- Focused tests: `uv run --with pytest --with pytest-cov pytest <test-path> -q`
- Full suite: `uv run --with pytest --with pytest-cov pytest -q`
