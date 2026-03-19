# PyRolyze

PyRolyze is the rebooted compiler/runtime package for compile-time reactive Python plus PySide6.

This repository starts by carrying forward only the reusable scaffold from the original prototype:

- import-hook shell
- compiler diagnostic types
- runtime hook-slot skeleton
- adapter and external-store skeleton

The core compiler/rendering path is being rebuilt around:

- `@pyrolyse` component markers
- `#@pyrolyze` module opt-in comments on line 1 or 2
- example-driven AST transform specifications
- generated `target/*.py` review artifacts in the examples repo

User-facing source-language documentation lives in:

- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/user/PyRolyze_Authoring_Guide.md`

## Current Status

Implemented in this repo today:

- source marker detection for `#@pyrolyze`
- `@pyrolyse` component discovery
- initial tests for the rebooted opt-in rules

Not yet implemented:

- executable init/update lowering
- direct Qt sink generation
- structural block runtime
- full external-store leak/race proof

## Local Development

Install the package in editable mode:

```bash
uv pip install -e .
```

Run focused tests:

```bash
uv run --with pytest --with pytest-cov pytest tests/test_compiler_markers.py -q
```

## Versioned AST Testing

AST transforms are more version-sensitive than most Python APIs because parser
and AST node details can shift between interpreter releases. This repo keeps the
compiler split into versioned kernels and provides a uv-based harness for
running the suite across Python versions.

The detailed workflow lives in
  [tests/README.md](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/tests/README.md).

Quick examples:

```bash
uv run python tests/versioned_test_harness.py list-versions
uv run python tests/versioned_test_harness.py regen-goldens
uv run python tests/versioned_test_harness.py run-tests --python 3.12 --pytest-args -q
uv run python tests/versioned_test_harness.py run-tests --python 3.13 --pytest-args -q
uv run python tests/versioned_test_harness.py run-tests --python 3.14 --pytest-args -q
uv run python tests/versioned_test_harness.py run-tests --python 3.15 --pytest-args -q
uv run python tests/versioned_test_harness.py run-tests-all --pytest-args -q
uv run python tests/versioned_test_harness.py run-tests-all --show-output --pytest-args -q
```

Current state:

- minimum supported runtime is Python `3.12`
- only kernel `v3_14` is checked in today
- Python `3.12`, `3.13`, `3.14`, and `3.15.0a5` have all been run successfully
  against that same `v3_14` kernel
