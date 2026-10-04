# SC2 Localized Follow-Up — CODE-AXIS REVIEW

**Review object:** Implementation diff `4d1b9b089333e99cb98381939db311c2b7ce8bde..a7bf0e92001f1c881ed81cd6e58064d8e8b4da51`; settlement diff `85ee82a8..a7bf0e9`; cumulative SC2 `1b246d47..a7bf0e9`. Controlling document: `dev-docs/PytoLifecyleIntegSC2.md` at the reviewed SHA, **DRAFT implementation checkpoint**, dated 2026-10-04.
**Baseline:** Pyrolyze `a7bf0e92001f1c881ed81cd6e58064d8e8b4da51`; yidl-lifecycle `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`; parent context only `a20f8cfb633a268925464eb27728d1934a70aea9`. Documents were read through committed `git show` views; dependency exports were byte-verified against the pinned commits.
**Date:** 2026-10-04.
**Axis:** Code: architecture, interfaces, call graphs, ownership, compatibility, and error paths. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero open P0, P1, P2, or P3 findings. Both original P2-9 counterexamples are independently verified closed on this tuple; earlier closures remain intact.

---

## Prior-finding closure table
“Verified” means the original counterexample was rerun or retraced on the corrected tuple, not inferred from aggregate counts. IDs are axis-qualified because the two P2-9 findings have independent roots.

| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| Code P2-1 | Validate parent/render ownership before initialization | Original leaf/resource cross-root constructors and reversed links reject before initialization; caught rejection aborts; caches/current membership stay empty. | Closed |
| Code P2-2 | Validate scheduler ownership and reject owned activation | Omitted, unrelated, and nested scheduler inputs reject; standalone activation of an owned legacy root rejects. | Closed |
| Code P2-3 | Gate direct component retirement before effects | Direct/disposal/ancestor paths reject before child-pointer, callback, scheduler, membership, UI, or generation changes; original direct path retraced. | Closed |
| Code P2-4 | Preflight removed component-bearing subtrees | Original committed native-leaf-contained component omission rejects and preserves its mounted child and queued boundary. | Closed |
| Code P2-5 | Published debug membership uses current | Original candidate addition stays invisible; discard stays invisible; commit/removal become visible only after completion. | Closed |
| Code P2-6 | Internal removal edits candidate membership | Original leaf/plain removal preserves staged sibling B on commit; discard restores original membership and discards B’s UI. | Closed |
| Code P2-7 | Preflight preceding candidate omissions | Original two-native-invocation omission rejects; component/nested UI remain empty, generation stays zero, and flushing executes no orphan. | Closed |
| Code P2-9 | Reject competing roots and require reciprocal ownership | Original committed/candidate competing-root constructors reject before lifecycle initialization. Stale retained first-root execution, mounting, scopes, attachment, propagation, and scheduler delivery reject without callback execution or publication. | Closed |
| State P2-1 | Retain lexical execution claims | Original native/publication early-end failures and no-op variant preserve the exact primary error, current UI, and generation; clean retry succeeds. | Verified closed |
| State P2-2 | Preflight direct/transitive retirement | Direct, disposal, ancestor, inside/outside, and caught rejection sequences preserve component and scheduler state. | Verified closed |
| State P2-3 | Check identity before no-op admission | Original real rollback/replacement sequence excludes the body; replacement participants remain empty and its explicit commit publishes nothing; old owner is quarantined. | Verified closed |
| State P2-4 | Separate published membership from reuse cache | Original activity/current contradiction is absent across candidate addition, discard, commit, and removal. | Verified closed |
| State P2-5 | Track all affected render roots | Original local-pass and publication-only discarded nested caches clear; fresh ensure does not reuse discarded leaves. Attached/detached registry removal/clear also reconciles correctly. | Verified closed |
| State P2-6 | Preserve candidate siblings during removal | Original sibling/removal sequence preserves B on commit and restores A on discard. | Verified closed |
| State P2-7 | Gate candidate-only mounted component omission | Original mounted two-local-pass sequence rejects; unpublished queue is cancelled; subsequent flush cannot advance generation. | Verified closed |
| State P2-8 | Reject constructor collisions before initialization | Original standalone/nested publication collisions reject before initialization; caught rejection poisons completion while preserving installed identity, callback, queue, UI, and generation; retry succeeds. | Verified closed |
| State P2-9 | Preflight newly unseen candidate subtrees | Original direct default-unseen component and default-unseen native leaf containing a component both reject; all candidate UI discards, generation stays zero, orphan queue clears, and retry succeeds. | Verified closed |

## Changed-range analysis
The follow-up adds 23 runtime lines across `_base.py`, `context_base.py`, `field_only_render.py`, and `render_context.py`, plus twenty narrow fault cases. Other changes are controlling/process records. Canonical success source/JSON, historical targets, dependencies, selectors, and activation defaults are unchanged.

Reciprocal checks cover constructor admission, mounting, boundary execution, lexical/direct local entry, publication scopes, and owner-UI propagation. The additional unseen-child loop applies the existing retirement preflight before filtering membership, alongside preceding/current checks. Both corrections map to RemPlan-3. No new restoration authority, resource disposal, manager API, or architectural root was identified.

## 0. Evidence base
- Verified all five HEADs at start and end: every SHA matched. Final `git diff -- src tests` was empty. Only permitted process-ledger changes appeared during review. No files, builds, bytecode, caches, or git state were written; no other current-round prompt/report was read.
- Read parent/Pyrolyze `AGENTS.md`, review-loop skill/template, SC2’s complete contract, SingleCohortPlan ownership/failure/publication/checkpoint sections, SC1-Remediation/ReviewLoop, both initial and round-1 reports, both round-2 reports, RemPlan-1/2/3, and committed SC2-ReviewLoop.
- Inspected implementation, settlement, and cumulative diffs. Principal runtime ranges: `src/pyrolyze/runtime/context_state_lcm/_base.py:79–105`, `context_base.py:106–444,462–496`, `field_only_render.py:1–333`, `render_context.py:24–311`, `component_call_slot_context.py:50–325`, `slot_context.py:11–59`, `leaf_slot_context.py:12–50`, and `render_attempt.py:38–387`.
- Traced retained facade constructors/execution at `src/pyrolyze/runtime/context_bare_refactor_lcm.py:64–210,807–1060`, scheduler behavior at `context_state_lcm/_support.py:670–731`, and generation completion at `app_context.py:107–132`.
- Read narrow tests through line 676, canonical fixture through line 419, and its authored target. Byte-verified lifecycle **17**, YIDL **45**, and Astichi **84** exported Python/YIDL files. Read pinned transaction completion and managed/core preparation, application, and discard templates; actual admitted participant metadata contains no transaction hooks or freeze/thaw converters.
- Independently ran the permitted command below: **63 passed in 4.44s**. Additional in-memory probes used real contexts/managers, ordinary runtime instrumentation, no generated-private-state writes, and no mocked manager completion. Three initial probe-script failures were harness assumptions, corrected before recording closure results.

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH="src:$snapshot/yidl-lifecycle/src:$snapshot/yidl/src:$snapshot/astichi/src" \
  "$PYTHON" -m pytest -p no:cacheprovider -q --tb=short \
  tests/test_runtime_context_state_lcm_field_only_render.py \
  tests/test_lcm_integration_characterization.py::test_common_pass_single_cohort_golden
```

## 2. Invariant analysis
The competing-root attack now stops before lifecycle initialization. A first root retained across real child installation cannot acquire execution or propagation authority: twenty stale-root entry/caught-rejection variants failed before callback, attachment, or publication. Scheduler delivery likewise rejects the stale boundary, preserves the installed child’s queued work, and advances generation only when that legitimate child subsequently executes.

Retirement preflight now covers preceding candidates, current children, and newly unseen candidates selected by the filter. Both original State P2-9 sequences discard rather than certify orphan publication. The inventory remains admission-only; lifecycle completion remains the value authority. Normal component installation/reuse, two-level nested manager sharing, canonical sticky failure, validator discard, independent roots/keys, and current-only readers held.

Seven deferred high-level routes rejected before supplied work and poisoned caught attempts. Unactivated legacy nested-manager separation, early publication, and competing-root construction remained unchanged. A fault after actual publication retained published values and observable generation uncertainty, cleared active bookkeeping, and blocked retry without fictitious undo.

## 3. Risks and next action
Full/default and broader suites were not independently rerun. Owner evidence remains focused127, full917/13 unchanged failures/20 skips/1 warning, and broader41/14 unchanged failures; none is an all-green claim or waiver. Resource adapters, broad activation, SC4 migration, asynchronous rendering, and generic manager/cross-key redesign remain uncertified.

**Next action:** File this Code GO and merge the independent State verdict at the exact reviewed tuple. Acceptance, if both verdicts are GO, remains limited to the private SC2 field-only checkpoint.
