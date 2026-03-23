# Versioned Test Runs

## Why This Exists

PyRolyze does AST transformation work, and Python's AST shape is not as stable as
the rest of the language and standard-library surface. Small interpreter
changes can alter:

- AST node classes
- node fields
- parser output shape
- unparse formatting behavior
- location propagation behavior

That means an AST transformer can appear correct on one Python version and then
quietly regress on another. The versioned test harness exists to make those
regressions visible early and to keep the compiler organized around explicit
kernel boundaries.

## Current Policy

- The package floor is Python `3.12`, declared in
  [pyproject.toml](../pyproject.toml).
- The only checked-in AST kernel today is
  [src/pyrolyze/compiler/kernels/v3_14/](../src/pyrolyze/compiler/kernels/v3_14/__init__.py).
- `kernel_loader` prefers an exact kernel match for the running interpreter and
  otherwise falls back to the latest available kernel.
- Because only `v3_14` exists today, all currently tested runtimes use that same
  kernel.

As of March 19, 2026, the full suite has been run successfully against:

- Python `3.12.12` using kernel `v3_14`
- Python `3.13.12` using kernel `v3_14`
- Python `3.14.3` using kernel `v3_14`
- Python `3.15.0a5` using kernel `v3_14`

That does not mean the AST is version-agnostic. It means the current compiler
surface still behaves correctly on those runtimes when routed through the
existing `v3_14` kernel.

## Test Data Layout

- Shared source fixtures live in
  [tests/data/gold_src/](data/gold_src).
- The source-to-module mapping lives in
  [tests/data/gold_cases.toml](data/gold_cases.toml).
- Checked-in expected transformed output is versioned by kernel:
  - [tests/data/v3_14/goldens/](data/v3_14/goldens)
- Untracked actual outputs from local runs go to:
  - `tests/actual_test_results/<runtime>/<kernel>/goldens/`
  - `tests/actual_test_results/<runtime>/<kernel>/pytest.xml`
  - `tests/actual_test_results/<runtime>/<kernel>/pytest.stdout.txt`
  - `tests/actual_test_results/<runtime>/<kernel>/pytest.stderr.txt`

This split is intentional:

- `gold_src` is the canonical authored source corpus
- `vX_Y/goldens` is the expected transform output for a specific AST kernel
- `actual_test_results` is disposable run output for debugging diffs and
  failures

## Prerequisites

You need [uv](https://docs.astral.sh/uv/) installed. The harness uses:

- `uv venv --python ...` to create interpreter-specific virtual environments
- `uv pip install ...` to install package and test dependencies
- `uv` interpreter downloads when a requested Python is not already present

The harness reads dependency installation requirements from
  [pyproject.toml](../pyproject.toml),
including the `test` optional dependency group.

The default runtime matrix for multi-version runs also lives there under:

- `[tool.pyrolyze.test-matrix]`

## Main Commands

List available AST kernels:

```bash
uv run python tests/versioned_test_harness.py list-versions
```

Regenerate checked-in goldens for every available kernel:

```bash
uv run python tests/versioned_test_harness.py regen-goldens
```

Regenerate checked-in goldens for a single kernel:

```bash
uv run python tests/versioned_test_harness.py regen-goldens --versions v3_14
```

Run the full suite on one Python version:

```bash
uv run python tests/versioned_test_harness.py run-tests --python 3.12 --pytest-args -q
uv run python tests/versioned_test_harness.py run-tests --python 3.13 --pytest-args -q
uv run python tests/versioned_test_harness.py run-tests --python 3.14 --pytest-args -q
uv run python tests/versioned_test_harness.py run-tests --python 3.15 --pytest-args -q
```

Run the suite for all configured runtime versions in parallel:

```bash
uv run python tests/versioned_test_harness.py run-tests-all --pytest-args -q
```

Run the suite for selected runtime versions in parallel:

```bash
uv run python tests/versioned_test_harness.py run-tests-all --python 3.12 3.14 3.15 --pytest-args -q
```

Show per-version output even for passing runs:

```bash
uv run python tests/versioned_test_harness.py run-tests-all --show-output --pytest-args -q
```

If only one version is selected and `--show-output` is set, the child `run-tests`
output is streamed directly to stdout/stderr. If multiple versions are selected,
the harness captures each run separately and replays the outputs serially so they
do not overlap.

Run only a focused subset on one Python version:

```bash
uv run python tests/versioned_test_harness.py run-tests --python 3.14 --pytest-args tests/test_ast_goldens.py -q
```

Recreate the versioned environment before running:

```bash
uv run python tests/versioned_test_harness.py run-tests --python 3.14 --recreate --pytest-args -q
```

## How Version Selection Works

The harness uses the requested interpreter version to create a uv-managed
environment under:

- `tests/.uv-venvs/py3_12`
- `tests/.uv-venvs/py3_13`
- `tests/.uv-venvs/py3_14`
- `tests/.uv-venvs/py3_15`

Inside that environment, the package is installed in editable mode and tests are
run using that interpreter. The AST kernel is then selected by
  [src/pyrolyze/compiler/kernel_loader.py](../src/pyrolyze/compiler/kernel_loader.py):

- exact `v<major>_<minor>` match if present
- otherwise latest available kernel

Examples today:

- Python `3.14` -> kernel `v3_14`
- Python `3.15` -> falls back to kernel `v3_14`
- Python `3.12` -> falls back to kernel `v3_14`

For `run-tests-all`, the default runtime list comes from
  [pyproject.toml](../pyproject.toml)
under `[tool.pyrolyze.test-matrix]`. Each selected runtime is launched as a
separate harness subprocess, so the runs proceed in parallel and each child run
still writes its own versioned artifacts under `tests/actual_test_results/`.

## Golden Testing Behavior

The active golden test is
  [tests/test_ast_goldens.py](test_ast_goldens.py).

It does the following:

1. Determine the selected kernel for the running interpreter.
2. Load shared source fixtures from `tests/data/gold_src/`.
3. Load the expected transformed output from `tests/data/<kernel>/goldens/`.
4. Emit transformed source using the current compiler/kernel.
5. Compare emitted output to the checked-in expected file.
6. Write actual output to `tests/actual_test_results/<runtime>/<kernel>/goldens/`.

This makes it easy to diff:

- authored input
- checked-in expected output
- actual output from a failing runtime/kernel combination

## Adding A New Kernel

When a future Python version needs AST-specific logic, add a new kernel
directory rather than branching all over the shared compiler code.

Minimum steps:

1. Add a new kernel directory such as
   [src/pyrolyze/compiler/kernels/v3_15/](../src/pyrolyze/compiler/kernels).
2. Implement the same module surface currently exposed by `v3_14`:
   - `kernel.py`
   - `eligibility.py`
   - `detect.py`
   - `plan.py`
   - `rewrite.py`
   - `validate.py`
   - `emit.py`
   - helper modules such as `builders.py`
3. Copy only the pieces that actually need to diverge from the previous kernel.
   Keep shared logic in the non-versioned compiler modules where possible.
4. Add a new expected output directory:
   - `tests/data/v3_15/goldens/`
5. Regenerate those goldens with the matching interpreter:

```bash
uv run python tests/versioned_test_harness.py regen-goldens --versions v3_15
```

6. Run the suite on that interpreter:

```bash
uv run python tests/versioned_test_harness.py run-tests --python 3.15 --pytest-args -q
```

## How To Diagnose Future AST Regressions

When a new Python version starts failing:

1. Run the full suite for that runtime with the harness.
2. Check which kernel was selected.
3. Inspect `tests/actual_test_results/<runtime>/<kernel>/goldens/` for transform
   diffs.
4. Compare those outputs with:
   - `tests/data/gold_src/`
   - `tests/data/<kernel>/goldens/`
5. Decide whether the regression belongs in:
   - shared compiler logic
   - runtime behavior
   - a new kernel version

If the failure is truly AST-shape-specific, prefer creating a new kernel version
over making shared logic increasingly conditional on interpreter checks.

## Practical Guidance

- If a runtime newer than `3.14` still passes against `v3_14`, do not create a
  new kernel just because the runtime is newer.
- Create a new kernel only when the AST or compiler behavior actually diverges.
- Keep the shared source corpus stable. Prefer adding a new checked-in golden
  directory before duplicating source fixtures.
- Use the manifest in
  [tests/data/gold_cases.toml](data/gold_cases.toml)
  to add or remove canonical golden cases.
