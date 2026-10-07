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
- `transaction_completion_outcomes.py`: the separately named L0 target trace
  for the same participants. Independent callbacks drain after failures, failed
  applications receive pending discard (not undo of applied current values),
  and grouped errors retain both preparation and cleanup failures. Its JSON is
  the current-library test; `baselines/transaction_failures.json` stays historical.
- `shared_completion.py`: two instances of a generated lifecycle class share
  one TM and one key. It observes nested commit, direct child-facade commit,
  and caught-child rollback. The snapshot demonstrates that the current API
  does not provide independent parent/child completion on that shared key;
  it is a capability observation, not approval of the resulting behavior.
- `callback_selection.py`: original/monolithic callback behavior through runtime
  pass scopes. It records receiver-identity replacement, stable dispatch,
  unpublished selection, and A then pending B/A (B after success, A after
  failure). The latter is known debt, not permission to fix it during holder
  replacement. Both references share one JSON snapshot; prior snapshots remain
  unchanged.
- `baselines/*.json`: structured historical snapshots, compared as JSON rather
  than by whitespace. Runtime selection takes place in fresh subprocesses.

The compiler does not lower authored `try` statements. The caught-child case
therefore catches the authored child's exception in an ordinary runtime
boundary callback; it does not introduce an unsupported author-facing form.

## Construction Golden

`slot_construction.py` is I1b coverage for ordinary, decorated, and
multiple-inheritance slots. It pins the single inherited common field set,
injected manager identity, completed initialization before root/parent
registration, and detached direct constructors. This is new migration coverage,
not a regeneration of the historical runtime observations.

Inspect it using the same environment:

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python tests/data/lcm_integration/slot_construction.py
```

The expected JSON is authored against the accepted construction contract.
Review a proposed change before updating `baselines/slot_construction.json`;
the script prints observations and does not rewrite the golden.

## I3a Preflight Observations

`common_pass_preflight.py` and its two `common_pass_preflight_*.json` baselines
record the original reference and decomposed path before I3a implementation.
They are **characterization, not approval of the observed failures**. The
decomposed path publishes a failed leaf candidate after its parent catches the
exception and succeeds; the original retains the leaf's previous UI. Separate
observations show skipped local entry on a borrowed transaction and the existing
out-of-pass dirty/metadata writes that a plain managed-marker conversion would
reject. No runtime changes or historical baseline rewrites accompany these
observations. The intended I3a acceptance fixture remains `common_pass.py`, to
be written only after the permission/isolation decisions are resolved.
The later single-cohort decision is described in
`dev-docs/PytoLifecyleIntegSingleCohortPlan.md`; its target fixture will be
`common_pass_single_cohort.py`. These old observations are history, not the
chosen target for nested completion.

Run only these observations through the existing harness:

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q \
  tests/test_lcm_integration_characterization.py -k common_pass_preflight
```

Inspect without rewriting a baseline by running `common_pass_preflight.py`
with `PYROLYZE_CONTEXT_IMPL=original` or `bare_refactor_lcm`. It prints JSON
only; it has no regeneration option. Committed-dependency reproduction and the
writer/completion-owner audit are in
`dev-docs/history/lifecycle-integration/PytoLifecyleIntegI3aPreflight.md`.

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

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python tests/data/lcm_integration/shared_completion.py
```

## Explicit Regeneration

Regenerate only after reviewing the observed change and recording any semantic
decision in the integration plan/findings. These commands write snapshots, not
runtime code:

Inspect the callback reference separately with the same environment and
`PYROLYZE_CONTEXT_IMPL=original` or `lcm`:

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
PYROLYZE_CONTEXT_IMPL=original \
  ../.venv/bin/python tests/data/lcm_integration/callback_selection.py
```

Its snapshot was added explicitly after inspecting both reference outputs.
Change it only with a recorded semantic decision, not automatic regeneration.
The earlier snapshots can be regenerated as follows:

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

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python tests/data/lcm_integration/shared_completion.py \
  --output tests/data/lcm_integration/baselines/shared_completion.json
```

Normal pytest execution never rewrites expected files. External-store, effect,
async-effect, mount, and call-site retirement coverage remains in its existing
canonical tests; this fixture does not duplicate those success assertions.

## Completion-Evidence Adoption

`common_pass_single_cohort.py` now extends the accepted SC2 fixture with the
SC3-L0 consumer matrix: empty commit, empty rollback/abort, validation/prepare
abort, full publication with after-action failure, incomplete discard/after
cleanup, and partial application. Generation follows authoritative publication
evidence, independently of exception shape and reuse readiness. These protocol
faults are test participants, not admission of production resource routes.
The previous seven sections of the SC2 JSON are unchanged.

The old failure trace is preserved against yidl-lifecycle
`371dfa530a975c27f7a6c09a7648f7f00532ab29`. Reproduce it without changing a
checkout or overwriting a baseline (bash/zsh process substitution):

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python tests/data/lcm_integration/transaction_failures.py \
  --historical-manager-source <(git -C ../yidl-lifecycle show \
    371dfa530a975c27f7a6c09a7648f7f00532ab29:src/yidl_lifecycle/transaction_yidl.py)
```

This option executes trusted local Python source; do not supply untrusted files.
Compare its JSON with `baselines/transaction_failures.json`. To inspect the
current target, run `transaction_completion_outcomes.py` with the same exports.
The historical `--output transaction_failures.json` command above is only for
that pinned pre-L0 manager, never for blessing current behavior into history.
