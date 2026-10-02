# LCM Integration Characterization

These are I0 observations for `dev-docs/PytoLifecyleIntegPlan.md`, not the
acceptance contract for the eventual lifecycle migration. They deliberately
record differences and incomplete failure handling in the current runtimes.
Never regenerate a baseline merely to hide an unapproved semantic change.

## Contents

- `characterize.py`: authored nested component execution through the generic
  backend, parent failure after child success, caught child failure, unchanged
  rerenders, and recovery. Root UI and per-child published UI are recorded
  separately because they can disagree after failure.
- `transaction_failures.py`: three minimal protocol participants exercise the
  extracted manager's prepare/apply/after-commit/rollback/after-rollback delivery.
  This probes callback mechanics, not generated lifecycle field correctness or
  external resource ownership. Recovery explicitly restages every participant;
  it does not imply skipped cleanup repaired itself.
- `baselines/*.json`: structured historical snapshots, compared as JSON rather
  than by whitespace. Runtime selection takes place in fresh subprocesses.

The compiler does not lower authored `try` statements. The caught-child case
therefore catches the authored child's exception in an ordinary runtime
boundary callback; it does not introduce an unsupported author-facing form.

## Run

From the Pyrolyze repository root, using the existing workspace environment:

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q \
  tests/test_lcm_integration_characterization.py
```

The Pyrolyze pytest plugin is discovered automatically from the source package
metadata in this environment. Do not also pass
`-p pyrolyze.compiler.pytest_plugin`: that registers it twice. The fixture itself
uses `load_transformed_namespace` for dynamic authored source.

Inspect a single runtime without changing an expected file:

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
PYROLYZE_CONTEXT_IMPL=bare_refactor_lcm \
  ../.venv/bin/python tests/data/lcm_integration/characterize.py
```

## Explicit Regeneration

Regenerate only after reviewing the observed change and recording any semantic
decision in the integration plan/findings. These commands write snapshots, not
runtime code:

```sh
for implementation in original lcm bare_refactor_lcm; do
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  PYROLYZE_CONTEXT_IMPL="$implementation" \
    ../.venv/bin/python tests/data/lcm_integration/characterize.py \
    --output "tests/data/lcm_integration/baselines/$implementation.json"
done

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python tests/data/lcm_integration/transaction_failures.py \
  --output tests/data/lcm_integration/baselines/transaction_failures.json
```

Normal pytest execution never rewrites expected files. External-store, effect,
async-effect, mount, and call-site retirement coverage remains in its existing
canonical tests; this fixture does not duplicate those success assertions.
