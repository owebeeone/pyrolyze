# SC2 Field-Only Render Wiring Remediation Round 2 — STATE-AXIS REVIEW

**Review object:** Remediation diff `ca731d89a0086e0bff48dc426d1b5b1472aba869..4d1b9b089333e99cb98381939db311c2b7ce8bde`, within cumulative SC2 from `1b246d47e934835a4871fbbfc651fae78440b913`. Controlling document: `dev-docs/PytoLifecyleIntegSC2.md` at the corrected revision, **DRAFT implementation checkpoint**, dated 2026-10-04.  
**Baseline:** Pyrolyze `4d1b9b089333e99cb98381939db311c2b7ce8bde`; yidl-lifecycle `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`; parent context only `a20f8cfb633a268925464eb27728d1934a70aea9`. Documents/dependencies were read through pinned `git show` views or byte-verified committed exports; inspected Pyrolyze source/tests remained unchanged.
**Date:** 2026-10-04.
**Axis:** State: publication legality, sticky failure, ownership, generation, cache/scheduler reconciliation, and recovery certification. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one P2 finding blocks; no P0, P1, or P3 findings. I pre-commit to GO on a revision that resolves P2-9 as specified while preserving the verified closures.

---

## Prior-finding closure table

“Verified” below means the original counterexample was rerun or retraced on this tuple, not inferred solely from aggregate test counts.

| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| State P2-1 | Fence native, publication, and no-op lexical execution | Reran all three early-end/later-error sequences. Current UI/generation stayed old; exact primary error escaped; retry succeeded. | Closed |
| State P2-2 | Preflight direct disposal/deactivation and ancestors | Direct, disposal, ancestor, inside/outside, and caught rejection cases preserved child identity, callback, queue, membership, UI, and generation. | Closed |
| State P2-3 | Check identity before no-op admission | Reran real token replacement with caught nested rejection. Body never ran; replacement participants stayed empty; replacement survived; old owner was quarantined. | Closed |
| State P2-4 | Published debug lookup uses current membership | Candidate additions/removals, slot-specific observations, discard, and commit remained current-only. | Closed |
| State P2-5 | Track every affected render root | Reran original local-pass and publication-only nested discards, plus attached/detached registry remove/clear without local entry. Caches reconciled; discarded leaf was not reused; independent root/key survived. | Closed |
| State P2-6 | Deactivation edits candidate membership | Leaf and plain-slot removal preserved staged sibling B. Discard restored old membership/UI without publishing B. | Closed |
| State P2-7 | Preflight preceding candidate omissions | Both original two-native-invocation and two-mounted-root-pass sequences rejected. Component/nested UI stayed unpublished; orphan queue was empty; generation stayed zero after flush. | Original closed; retirement coverage gap remains as P2-9 |
| State P2-8 | Reject constructor collisions before initialization | Standalone/nested publication collisions, including caught rejection, preserved published component identity, callback, queue, UI, and generation; retry succeeded. Allocation instrumentation passed. | Closed |
| Code P2-1 | Validate both parent and nearest-render ownership | Original cross-root admitted/resource constructors and reversed links rejected before attachment; initialization ordering retraced. | Closed |
| Code P2-2 | Reject omitted/conflicting scheduler ownership and owned-root activation | Omitted, unrelated, and non-root scheduler inputs rejected. Owned standalone activation rejection passed; normal sharing remained canonical. | Closed |
| Code P2-3 | Gate direct component retirement before effects | Original destructive disposal sequence and direct/recursive variants preserved component and scheduler state. | Closed |
| Code P2-4 | Preflight removed component-bearing subtrees | Original committed leaf-contained component omission rejected and preserved its queued boundary. Newly introduced unseen subtree variant remains below. | Original closed; broader invariant incomplete |
| Code P2-5 | Published debug membership is current-only | Original candidate-cache contradiction no longer reproduced; canonical slot-specific reads passed. | Closed |
| Code P2-6 | Internal removal uses candidate readers | Original leaf/plain staged-sibling loss no longer reproduced on commit or discard. | Closed |
| Code P2-7 | Cover component removal across successive local passes | Original candidate-only repeat omission rejected and discarded all publication/queued work. | Original closed; retirement coverage gap remains as P2-9 |

## Changed-range analysis

Round 2 changes five runtime modules: constructor collision admission, preceding-candidate retirement references, affected-render-root tracking, publication/registry bookkeeping, orphan scheduler cancellation, and candidate-backed deactivation. It adds ten narrow cases and canonical sibling-preservation/repeat-component observations. Remaining changes are controlling/process documents.

These changes map to RemPlan-2’s dispositions. No dependency, activation, resource protocol, lifecycle kernel, or snapshot-removal widening was identified.

P2-9 is a **localized, non-architectural retirement-admission omission**, not a **NEW ARCHITECTURAL root cause**. The new inventory covers preceding candidates and current membership, but the retained filter still removes newly introduced unseen candidates without preflight. Correcting that selection boundary needs neither manager redesign nor resource disposal. The original SC2 execution-ownership root remains recorded; this review identifies no additional architectural root.

## 0. Evidence base

- Verified all five HEADs at review start and end; every SHA matched. Final `git diff -- src tests` was empty. Only the permitted process ledger changed during review. No files were written, builds run, or git state mutated. No other current-round prompt/report was read.
- Read parent/Pyrolyze `AGENTS.md`, the review-loop skill/template, all controlling SC2/SingleCohortPlan contracts, SC1-Remediation/ReviewLoop, both initial and round-1 reports, both remediation plans, and committed SC2-ReviewLoop.
- Inspected round-2 and relevant cumulative diffs. Principal runtime ranges: `src/pyrolyze/runtime/context_state_lcm/field_only_render.py:1–331`, `context_base.py:68–763`, `render_context.py:24–482`, `_base.py:79–104`, `slot_context.py:11–59`, `component_call_slot_context.py:50–325`, `leaf_slot_context.py:12–50`, and `render_attempt.py:38–387`. Also read facade constructors and scheduler/generation paths.
- Read the narrow tests through line 514, canonical fixture through line 419, its authored JSON, and characterization harness. Byte-compared exported Python/YIDL sources with pinned commits: lifecycle **17**, YIDL **45**, Astichi **84** files; all matched.
- Read pinned transaction completion and managed/core prepare/apply/discard templates. Actual root, plain slot, leaf, component, and nested-render metadata contained no transaction hooks or freeze/thaw converters.
- Independently ran the permitted gate below: **43 passed in 4.12s**. Ran additional write-free in-memory probes using real contexts/managers, without generated-private-state writes or mocked manager completion.

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH="src:$snapshot/yidl-lifecycle/src:$snapshot/yidl/src:$snapshot/astichi/src" \
  "$PYTHON" -m pytest -p no:cacheprovider -q --tb=short \
  tests/test_runtime_context_state_lcm_field_only_render.py \
  tests/test_lcm_integration_characterization.py::test_common_pass_single_cohort_golden
```

## 1. Findings

### [P2-9] Newly introduced unseen component subtrees bypass retirement preflight

**Location:** `src/pyrolyze/runtime/context_state_lcm/context_base.py:353–361`. Admission examines preceding candidate/current children, then separately filters all unseen candidate children. Direct constructors retain `seen_in_pass=False` by default at `src/pyrolyze/runtime/context_bare_refactor_lcm.py:811–819,880–888`.

**Violated invariant:** SC2.md:26–32 and 73–74 admit these exact constructors but gate component retirement and require subtree-removal preflight before membership edits. Cache reconciliation cannot authorize retirement.

**Reproduction:** Load the canonical helpers through `runpy.run_path("tests/data/lcm_integration/common_pass_single_cohort.py")`, then execute:

```python
root = _root()
with root.pass_scope():
    component = runtime.ComponentCallSlotContext(root, root, _slot_id(2))
    component.invoke(_nested, ("unseen-new",), {})
    nested = component.child_context
    root._state_mgr._scheduler.request(nested)
```

No explicit visitation mutation is involved: the constructor’s documented default leaves the new component unseen. Neither preceding candidate nor current membership contains it, so preflight examines nothing. The filter removes it and outer completion succeeds.

Observed after completion:

- Root current membership and UI are empty.
- Component and nested current UI both contain `"unseen-new"`.
- Committed generation is **1**, and the owner certifies reuse.
- The nested mounted callback remains installed. Reconciliation cancels its queue, but only after successful orphan publication.

A second reproduction constructs a new native leaf with its default unseen status, then invokes it to ensure/invoke a component descendant. Root exit silently filters that leaf and likewise publishes the unreachable component/nested UI with generation **1**.

**Impact:** An admitted first-pass construction silently takes the deferred retirement outcome and reports successful publication. The new scheduler cancellation prevents queued execution in these probes; it does not prevent the illegal completion or generation advancement.

**Required correction:** Before filtering candidate membership, preflight every candidate subtree selected for removal, including newly introduced unseen children. Keep preceding/current checks, current-only readers, and lookup-cache reconciliation; do not add disposal or snapshot restoration.

**Closure/regression test:** Add both direct-component and native-leaf-containing-component default-constructor cases. Require retirement rejection, discarded component/nested current UI, unchanged committed generation, no executable queued orphan, and clean subsequent retry. Retain canonical successful same-component repeat reuse and all prior closure cases.

## 2. Invariant analysis

- Execution claims held through early local release in native, publication, and no-op scopes. Later failure retained its primary exception and discarded rather than publishing.
- Sticky caught-child failure, later-sibling non-recovery, parent-after-child failure, real validation discard, manager sharing, independent roots/keys, and sequential queued-boundary generation held in the canonical proof.
- Replaced-token admission excluded foreign writes and preserved the replacement. An external same-key borrower prevented publication and reuse certification.
- Publication-only affected-root tracking restored attached/detached registry removal/clear without local entry. Previously published callback/identity/queue state survived caught constructor rejection.
- Preceding-candidate references are admission-only: they are not used to restore managed membership. Affected-root references likewise hold no copied value authority. Clean discard restores fields through lifecycle completion.
- Injected adapter failure after actual publication retained published UI and observable generation uncertainty, cleared active execution bookkeeping, and blocked retry. It did not fabricate rollback. Cleanup/terminal reentry guards were traced.
- Seven deferred direct constructors and seven high-level resource entry points rejected before supplied work. No activated fallback to legacy local completion was found. These protections do not cover P2-9’s newly filtered candidates.

## 3. Risks and next action

This checkpoint introduces no filesystem persistence. The reviewed ordering is in-memory lifecycle publication, cleanup/reconciliation, then generation completion; process-restart durability and asynchronous rendering are not certified.

The owner’s focused107/full897/broader41 results were not independently rerun. Their unchanged 13/14 failures remain baseline debt, not an all-green claim or waiver. Broad activation, SC3 adapters, SC4 migration, and generic manager/cross-key redesign remain excluded.

**Next action:** Keep SC2 unaccepted and return P2-9 to the lane owner for operator disposition under the final bounded-remediation authorization. This report does not authorize an automatic third patch or lower the acceptance bar.
