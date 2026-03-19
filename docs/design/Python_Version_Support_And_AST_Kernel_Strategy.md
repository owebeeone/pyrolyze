# Python Version Support And AST Kernel Strategy

## Purpose

Explain current Python support, kernel fallback behavior, and how future AST
breaks should be handled.

## Current implementation

The package floor is Python `3.12`.

Versioned AST logic lives under:

- `src/pyrolyze/compiler/kernels/`

Kernel selection lives in:

- `src/pyrolyze/compiler/kernel_loader.py`

Selection policy:

- exact kernel match if present
- otherwise latest available kernel

Current shipped state:

- only `v3_14` exists
- Python `3.12`, `3.13`, `3.14`, and `3.15` have been run successfully against that same kernel

The versioned test harness and golden layout are already designed around this
policy.

## Code map

- kernel selection
  - `src/pyrolyze/compiler/kernel_loader.py`
- kernel protocol
  - `src/pyrolyze/compiler/kernel_api.py`
- current kernel
  - `src/pyrolyze/compiler/kernels/v3_14/`
- versioned test harness
  - `tests/versioned_test_harness.py`
- golden manifest and data
  - `tests/data/gold_cases.toml`
  - `tests/data/gold_src/`
  - `tests/data/v3_14/goldens/`

## Primary tests

- `tests/test_ast_kernel_selection.py`
- `tests/test_ast_goldens.py`
- `tests/test_versioned_test_harness.py`

## Known limitations

- only one kernel is checked in today
- passing on a newer runtime does not guarantee AST identity across all future versions

## Future proposals

- add a new kernel only when AST or lowering behavior truly diverges
- keep shared logic in non-versioned modules and isolate only the version-specific seams
