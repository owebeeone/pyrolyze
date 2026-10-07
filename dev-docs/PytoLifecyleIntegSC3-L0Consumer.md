# SC3-L0 Private Completion-Evidence Adoption

Status: implementation candidate, 2026-10-08; independent Code/State acceptance
pending. This checkpoint consumes the accepted L0 library, not resource-route
activation. Contract: `PytoLifecyleIntegSC3-L0Plan.md`, Consumer Contract and
SC3-L0 Consumer sections. No contract amendments are proposed here.

## Boundary

The only runtime changes are in
`src/pyrolyze/runtime/context_state_lcm/render_attempt.py` and
`field_only_render.py`. The original SC2 private, exact-class field-only gate
remains in place. Production callback/binding/effect/override routes remain
legacy; no resource adapters, holder migration, new markers, manager/compiler
changes, activation switches, or arbitrary snapshot deletion are included.

The owner captures the original token's key/ID before callbacks, retains that
token, and validates its terminal `TransactionCompletion` after either a
normal return or an exception. It rejects missing, structurally incoherent,
wrong-key/ID, nonfinalized, ownership-lost, or replacement-active evidence.
Earlier ownership loss cannot be repaired by a later apparently clean record.

`published` is a private observation, not a second transaction state machine:
True means authoritative full publication; False means authoritative
nonpublication (not necessarily completed discard); None means partial or
uncertified application. It is never inferred from `first_failure` or readiness.

| Evidence | Generation | Reuse |
| --- | --- | --- |
| Full publication, complete after actions | Commit once | Allowed if local cleanup also succeeded |
| Full publication, after-action failure | Commit once; preserve error | Quarantined in this private checkpoint |
| No application, complete discard/actions | Roll back once; preserve original error | Allowed if local cleanup also succeeded |
| No application, incomplete discard/actions | Roll back once; preserve all errors | Quarantined |
| Partial application or rejected authority | No publication/rollback certificate | Quarantined |

Generation completion precedes local scratch/cache cleanup, so cleanup failure
cannot erase already published values' generation. Cleanup errors separately
fence graph reuse. No resource-hook visibility/retirement ordering is chosen;
that is the next D5/category-adapter design gate. Partial/uncertified outcomes
leave the tracker pending rather than fabricate commit or rollback; the graph
cannot start another attempt automatically.

Local scope admission, poison-on-caught-failure, recursive-completion fencing,
original-token identity, other-key isolation, and exactly-once owner completion
remain required. A commit exception is not followed by a guessed second
rollback: the manager's record reports the actual pending discard/application.

## Historical Transition

`tests/data/lcm_integration/baselines/transaction_failures.json` is unchanged.
It reproduces exactly with yidl-lifecycle
`371dfa530a975c27f7a6c09a7648f7f00532ab29`; the fixture README records the
trusted-source reproduction command without changing a checkout.

The current-library target is separately named
`transaction_completion_outcomes.py` and its JSON, including structured grouped
errors. The old unclassified-commit unit expectation is replaced by an explicit
prepare/apply/after outcome test. These are the two previously recorded
adoption mismatches, not unrelated debt and not silently regenerated history.

The canonical `common_pass_single_cohort.py` adds a completion-evidence section
with real generated fields/context paths, protocol fault participants, and
observed generation calls. It covers the empty commit/rollback/abort matrix,
validation/prepare failure, incomplete discard/after cleanup, partial apply,
and fully published values with an after failure. Its previous seven JSON
sections are unchanged. Narrow tests cover missing/incoherent evidence,
replacement after finalization, preserved primary errors, exactly-once finish,
and published generation despite local scratch cleanup failure.

## Verification

Baseline Pyrolyze: `dc9e4ccd21715bf8c639d07a2ec4d46af936b2c2`.
Unchanged dependency tuple:

- yidl-lifecycle `05554397d1837ecbeafa36e4685477dd5ff30fc6` (accepted runtime
  `4b86eec179942d96012aa4a1d92752a34cae87ef`; HEAD adds acceptance docs only).
- YIDL `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`.
- Astichi `1c47f781d3804130fdd61cbee07a3b2e4529158a`.

Python 3.12.12, local source exports, bytecode/cache writes disabled:

- Baseline seven-file native run: 125 passed, the exact two adoption failures.
- Red: 11 failures/1 pass in new outcome/evidence units; canonical fixture
  fails its explicit prepare-outcome assertion before snapshot comparison.
- Green seven-file native run: **138 passed**.
- Owner/field-only/characterization Python-backend run: **119 passed**.
- Full default native: **928 passed, 13 failed, 20 skipped, 1 warning**.
- Broader decomposed, unactivated native: **41 passed, 14 failed**.
- Historical-manager output equals the preserved JSON; no historical golden
  changed. Black and `git diff --check` pass.

The full-default failure identities remain the prior eleven visitor/visualizer
cases plus the two host-order cases. The broader failure identities remain
the nine app-context override cases, one mount advertisement case, one
generation relocation case, and three event-handler cases. See
`history/lifecycle-integration/PytoLifecyleIntegI0Findings.md` and the SC2 ledger.
These are not waived and no fully green integration is claimed.

From this repository root:

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM \
  PYTHONDONTWRITEBYTECODE=1 ASTICHI_LOWER_ENGINE=native \
  PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=short \
  tests/test_runtime_context_state_lcm_render_attempt.py \
  tests/test_runtime_context_state_lcm_field_only_render.py \
  tests/test_runtime_context_state_lcm_construction.py \
  tests/test_runtime_context_state_lcm_context_base.py \
  tests/test_runtime_context_state_lcm_slot_expr.py \
  tests/test_runtime_context_state_lcm_leaf_rerender.py \
  tests/test_lcm_integration_characterization.py
```

Omit test paths for full default. The broader eight paths and runtime selector
are in the I0 findings' Reproduction section. The Python-backend check uses
`ASTICHI_LOWER_ENGINE=python` and only the owner, field-only, and characterization
paths above. No duplicate pytest-plugin registration is necessary.

## Next Gate

The initial candidate at `223d04aa322df32e2adc5f5cd45b27111b111f4b`
received Code/State NO-GO verdicts. The verbatim reports and combined remediation
plan are in `history/lifecycle-integration/`, named
`PytoLifecyleIntegSC3-L0Consumer-ReviewCode.md`, `-ReviewState.md`, and
`-RemPlan-1.md`. Three distinct P2s concern exception truthiness, mutable token
metadata at admission, and unreachable completion-record combinations.

One bounded remediation patch addresses them without widening the contract.
Nine counterexamples were red before correction. Native focused verification
now passes **147 tests**, and the Python-backend subset passes **128 tests**.
Full default native is **937 passed, the same 13 failures, 20 skipped, 1
warning**; broader unactivated is **41 passed, the same 14 failures**. No
goldens changed. Black and diff checks pass. The original observations above
are retained as initial-candidate evidence, not the latest test counts.

Commit this combined correction and request focused re-verdicts from the same
Code and State reviewers. Remediation rounds used: 1/2. Acceptance is still
pending those verdicts. No pushes/tags/parent-pointer updates are part of this step.
After acceptance, design the concrete D5/category adapter timeline before
admitting any resource-bearing route. Do not skip directly to event-handler
holder replacement or general activation.
