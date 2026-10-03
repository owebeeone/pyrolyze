# SC2 Localized Follow-Up — STATE-AXIS REVIEW

**Review object:** Pyrolyze `a7bf0e92001f1c881ed81cd6e58064d8e8b4da51`; implementation diff `4d1b9b08..a7bf0e92`, settlement diff `85ee82a8..a7bf0e92`, cumulative SC2 `1b246d47..a7bf0e92`. Controlling document: `dev-docs/PytoLifecyleIntegSC2.md`, DRAFT implementation checkpoint dated 2026-10-04.
**Baseline:** yidl-lifecycle `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`; parent context only `a20f8cfb633a268925464eb27728d1934a70aea9`. Prior reviewed Pyrolyze: `4d1b9b089333e99cb98381939db311c2b7ce8bde`. Documents/dependencies were read through pinned `git show` or byte-verified committed exports.
**Date:** 2026-10-04.
**Axis:** State: publication legality, ownership, generation authority, scheduler/cache reconciliation, and recovery. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero open P0/P1/P2/P3 findings. Both prior P2-9 counterexamples close; earlier closures survive the attacks performed here.

---

## Prior-finding closure table
Verification below means original-counterexample execution or source retracing on this tuple, not acceptance of implementer claims.

| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| State P2-1 | Retain lexical execution claims | Original native/publication early-end failures, plus no-op/lexical variants, retained old UI/generation, exact primary error, and clean retry. | Closed |
| State P2-2 | Reject retirement before effects | Direct deactivation, disposal, and ancestor paths, outside and caught inside attempts, preserved identity, callback, queue, membership, UI, and generation. | Closed |
| State P2-3 | Identity admission before no-op entry | Original real token replacement excluded the body and participants; replacement survived and committed no UI; old owner remained quarantined. | Closed |
| State P2-4 | Current-only published debug readers | Original candidate/discard/commit observations and removal variants remained coherent with current membership. | Closed |
| State P2-5 | Reconcile every affected render root | Original local-pass and publication-only nested discards cleared caches; retained retry did not reuse discarded leaves. Attached/detached registry clear/remove variants also passed. | Closed |
| State P2-6 | Candidate-backed deactivation edits | Original leaf/plain staged-sibling sequences preserved B on commit and restored original membership on discard. | Closed |
| State P2-7 | Preflight preceding candidates | Original mounted two-pass and two-native-invocation sequences rejected; actual leaf-originated invalidation left no executable queue or advanced generation. | Closed |
| State P2-8 | Constructor collision admission | Original standalone/nested publication collisions, including caught rejection, preserved component state and allowed retry; initialization ordering was checked by the permitted gate. | Closed |
| State P2-9 | Preflight unseen candidates before filtering | Original direct unseen component and unseen leaf-containing-component sequences rejected while selected children remained in the candidate map; component/nested current UI discarded, generation stayed zero, queue emptied, and retry succeeded. | Closed |
| Code P2-1 | Two-sided constructor ownership | Original admitted/resource cross-root constructors and reversed links rejected; caches/current membership remained empty. Pre-initialization ordering was retraced and instrumented by the gate. | Closed |
| Code P2-2 | Scheduler ownership and activation admission | Original omitted/unrelated scheduler constructors, non-root scheduler variant, and owned standalone activation rejected; normal nested sharing remained supported. | Closed |
| Code P2-3 | Preflight direct component disposal | Original destructive route now rejects before callback, scheduler, or pointer mutation; direct/recursive variants preserved installed state. | Closed |
| Code P2-4 | Preflight component-bearing ancestors | Original native leaf → component committed omission rejected and preserved its published queued boundary. | Closed |
| Code P2-5 | Current-only debug membership | Original candidate-cache contradiction no longer reproduced; canonical slot-specific observations passed. | Closed |
| Code P2-6 | Candidate readers for removal | Original leaf/plain sibling-loss counterexamples no longer reproduced on commit or discard. | Closed |
| Code P2-7 | Cover successive local-pass omissions | Original two-native-invocation sequence rejected before orphan publication; subsequent flush could not advance generation. | Closed |
| Code P2-9 | Duplicate-root and reciprocal ownership admission | Original competing-root construction rejected before initialization; installed child/callback/UI/queue/generation survived. Candidate and caught-active variants aborted. Seven uninstalled-root entry paths excluded execution, attachment, and propagation. | Closed |

## Changed-range analysis
The localized settlement changes four runtime modules: `_base.py` adds reciprocal nearest-render admission before slot initialization; `context_base.py` guards publication scopes and preflights unseen candidates; `field_only_render.py` guards scoped/direct pass entry; `render_context.py` rejects duplicate children and guards execution/UI propagation. The narrow test adds twenty fault cases. Other settlement changes are controlling/process documents.

These changes implement RemPlan-3’s two bounded dispositions. No accepted SC1 mechanism, manager/dependency source, resource protocol, activation default, snapshot authority, or canonical/historical success target changed. No **NEW ARCHITECTURAL root cause** was identified.

## 0. Evidence base
- Verified all five HEADs at start and end: every SHA matched. Final `git diff -- src tests` was empty. The permitted process ledger changed externally during review; its committed version was used. No files, builds, bytecode, caches, or git state were written by this review. No other current-round prompt/report was read.
- Read parent/Pyrolyze `AGENTS.md`, review-loop skill/template, SC2’s complete contract, SingleCohortPlan’s ownership/failure/publication/checkpoint sections, SC1-Remediation/ReviewLoop, all initial/round-1/round-2 reports, RemPlan-1/2/3, and committed SC2-ReviewLoop.
- Inspected implementation, settlement, and relevant cumulative diffs. Principal runtime evidence: `src/pyrolyze/runtime/context_state_lcm/field_only_render.py:1–333`, `render_attempt.py:1–387`, `render_context.py:24–311`, `context_base.py:68–444,462–767`, `_base.py:79–105`, `slot_context.py:11–59`, `leaf_slot_context.py:12–50`, and `component_call_slot_context.py:50–325`. Traced facade constructors/execution at `src/pyrolyze/runtime/context_bare_refactor_lcm.py:807–1040`, scheduler operations, and generation tracking.
- Read `tests/test_runtime_context_state_lcm_field_only_render.py:1–676`, canonical fixture `tests/data/lcm_integration/common_pass_single_cohort.py:1–419`, its complete JSON target, and characterization harness. Byte-compared exported Python/YIDL sources: lifecycle **17**, YIDL **45**, Astichi **84** files; all matched pinned commits. Read real transaction completion and managed/core preparation/application/discard templates.
- Independently ran the permitted command below: **63 passed in 4.27s**. Additional write-free probes used canonical helpers loaded with `runpy.run_path("tests/data/lcm_integration/common_pass_single_cohort.py")`, real contexts/managers, and runtime-method instrumentation only. No generated-private-state writes or mocked manager completion were used.

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH="src:$snapshot/yidl-lifecycle/src:$snapshot/yidl/src:$snapshot/astichi/src" \
  "$PYTHON" -m pytest -p no:cacheprovider -q --tb=short \
  tests/test_runtime_context_state_lcm_field_only_render.py \
  tests/test_lcm_integration_characterization.py::test_common_pass_single_cohort_golden
```

One exploratory probe initially expected an exception group for an external borrower; the actual contract specifies `RenderAttemptIncomplete`. Correcting that probe expectation and rerunning confirmed discard and quarantine.

## 2. Invariant analysis
**Admission and retirement:** Both original unseen-subtree probes now fail before filtering. Duplicate owned-root construction cannot reach lifecycle initialization. Uninstalled roots cannot mount, run a queued boundary, enter scoped/direct passes, enter publication scopes, construct children, or propagate owner UI. Caught rejection remains sticky. Normal installation, repeated component reuse, and retained legitimate installed roots remain supported; reciprocal checks introduce no reachability requirement or restoration authority.

**Completion and recovery:** Early local release cannot complete an outstanding lexical body. Replacement-token admission excludes foreign writes. External same-key borrowing blocks publication/reuse certification. Leaked local scopes discard and unwind before clean retry. Caught terminal re-entry cannot double-release or restore committability. Canonical caught-child/later-sibling/parent-failure and real validation-discard observations passed.

**Ordering and reconciliation:** Lifecycle completion precedes local cleanup/cache reconciliation and generation completion. Injected faults after actual publication retained published UI, exposed the unresolved active generation, cleared execution bookkeeping, and quarantined retry; they did not fabricate rollback. Independent roots remained usable. Clean discard removed unpublished orphan scheduler work while preserving published boundaries and queues.

**Scope:** Actual root/plain/leaf/component/nested metadata contained no transaction hooks or freeze/thaw converters. Seven direct deferred constructors and seven high-level resource routes rejected before supplied work. Unactivated nested rendering retained its separate manager and historical early publication. Admission inventories remain references used for checks, never managed-value restoration.

## 3. Risks and next action
There is no new filesystem persistence to certify. Process-restart durability, asynchronous rendering, resource adapters, broad activation, SC4 migration, and cross-key atomicity remain outside this verdict. Owner full/default and broader evidence was not independently rerun; the recorded 13/14 failures remain baseline debt, neither waived nor all-green.

**Next action:** Merge this State GO with the independently produced Code verdict on the exact tuple. Accept only the privately gated SC2 scope if both are GO; this report authorizes no fourth correction or broader activation.
