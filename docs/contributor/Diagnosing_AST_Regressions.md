# Diagnosing AST Regressions

## Purpose

Provide the current process for debugging compiler regressions and deciding
whether the issue belongs in shared code, runtime behavior, or a new kernel.

## Current implementation

PyRolyze already provides three useful artifacts:

- authored source fixtures in `tests/data/gold_src/`
- checked-in expected transformed output in `tests/data/<kernel>/goldens/`
- actual output per runtime/kernel in `tests/actual_test_results/`

That lets you compare:

- source intent
- expected transform output
- actual transform output

## Procedure

1. Reproduce with the versioned harness.
2. Confirm which kernel was selected.
3. Inspect the failing actual output in `tests/actual_test_results/...`.
4. Compare it with:
   - the source fixture
   - the checked-in golden
5. Decide where the failure belongs:
   - shared compiler logic
   - version-specific kernel logic
   - runtime behavior
   - backend reconciliation

## Code map

- harness
  - `tests/versioned_test_harness.py`
- golden test
  - `tests/test_ast_goldens.py`
- kernel loader
  - `src/pyrolyze/compiler/kernel_loader.py`

## Primary tests

- `tests/test_ast_goldens.py`
- `tests/test_ast_kernel_selection.py`

## Known limitations

- some regressions only appear in integrated runtime or backend tests, not in goldens alone

## Future proposals

- more automated diff summaries for failing golden runs
- more cross-linking between compiler failures and runtime graph diffs
