# Testing And Goldens

## Purpose

Explain the current test layers and how golden-source testing is organized.

## Current implementation

PyRolyze uses several test layers:

- compiler/golden tests
- runtime context-graph tests
- backend wrapper/reconciliation tests
- example-host tests
- integrated source-backed graph tests

The golden layout is:

- shared source fixtures
  - `tests/data/gold_src/`
- case manifest
  - `tests/data/gold_cases.toml`
- checked-in expected output by kernel
  - `tests/data/v3_14/goldens/`
- untracked actual output by runtime and kernel
  - `tests/actual_test_results/<runtime>/<kernel>/`

## Code map

- versioned harness
  - `tests/versioned_test_harness.py`
- golden comparison test
  - `tests/test_ast_goldens.py`
- kernel selection tests
  - `tests/test_ast_kernel_selection.py`

## Primary tests

- `tests/test_ast_goldens.py`
- `tests/test_versioned_test_harness.py`
- `tests/test_ast_kernel_selection.py`

## Known limitations

- only one checked-in kernel-specific golden directory exists today

## Future proposals

- more kernel-specific golden directories as AST behavior diverges
- richer automatic diff tooling for actual vs expected output
