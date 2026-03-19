# Versioned Test Runs

## Purpose

Explain how to run the suite across Python versions and why PyRolyze treats AST
version support as a first-class maintenance concern.

## Current implementation

The harness lives in:

- `tests/versioned_test_harness.py`

It provisions uv-managed virtual environments for selected runtimes, installs
package and test dependencies from `pyproject.toml`, and runs pytest inside the
matching interpreter.

Current policy:

- minimum runtime: Python `3.12`
- current default test matrix:
  - `3.12`
  - `3.13`
  - `3.14`
  - `3.15`
- current checked-in kernel:
  - `v3_14`

That means current multi-version runs verify that the same `v3_14` kernel still
behaves correctly across those runtimes.

## Code map

- harness
  - `tests/versioned_test_harness.py`
- runtime matrix configuration
  - `pyproject.toml`
- golden manifest and golden directories
  - `tests/data/gold_cases.toml`
  - `tests/data/gold_src/`
  - `tests/data/v3_14/goldens/`

## Primary tests

- `tests/test_versioned_test_harness.py`
- `tests/test_ast_goldens.py`
- `tests/test_ast_kernel_selection.py`

## Main commands

List kernels:

```bash
uv run python tests/versioned_test_harness.py list-versions
```

Run one version:

```bash
uv run python tests/versioned_test_harness.py run-tests --python 3.14 --pytest-args -q
```

Run all selected versions in parallel:

```bash
uv run python tests/versioned_test_harness.py run-tests-all --pytest-args -q
```

Show per-version output:

```bash
uv run python tests/versioned_test_harness.py run-tests-all --show-output --pytest-args -q
```

Regenerate checked-in goldens:

```bash
uv run python tests/versioned_test_harness.py regen-goldens
```

## Known limitations

- passing on a newer runtime does not prove the AST is permanently stable
- one kernel can legitimately serve multiple runtimes until AST behavior diverges

## Future proposals

- add new kernels only when actual AST-specific behavior breaks
