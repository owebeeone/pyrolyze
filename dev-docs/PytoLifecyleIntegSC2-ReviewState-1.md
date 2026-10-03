# SC2 Field-Only Render Wiring Remediation Round 1 — STATE-AXIS REVIEW

**Review object:** Remediation diff `53c41674f43ab97401ac9b30a79575c19ab5dca9..ca731d89a0086e0bff48dc426d1b5b1472aba869`, within cumulative SC2 diff `1b246d47e934835a4871fbbfc651fae78440b913..ca731d89a0086e0bff48dc426d1b5b1472aba869`. Controlling document: `dev-docs/PytoLifecyleIntegSC2.md` at the corrected SHA, **DRAFT implementation checkpoint**, dated 2026-10-04.
**Baseline:** Pyrolyze `ca731d89a0086e0bff48dc426d1b5b1472aba869`; yidl-lifecycle `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`; parent context only `a20f8cfb633a268925464eb27728d1934a70aea9`. Documents and dependencies were read through pinned `git show` views or byte-verified clean exports.
**Date:** 2026-10-04
**Axis:** State: transition legality, publication ordering, failure isolation, membership integrity, cleanup, and retry certification. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — four P2 findings block: incomplete State P2-5 remediation and additional findings P2-6 through P2-8. I pre-commit to GO on a revision that resolves P2-5, P2-6, P2-7, and P2-8 as specified.

---

## Prior-finding closure table

“Original passes” means the original counterexample was rerun or retraced on the corrected tuple, not inferred from the aggregate test result.

| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| State P2-1 | Fence native, publication, and no-op lexical execution | Reran early local end followed by failure in all three modes. Current UI/generation stayed unchanged; exact primary error escaped; fresh retry succeeded. | Closed |
| State P2-2 | Preflight direct disposal/deactivation and ancestors | Reran direct deactivation, disposal, and ancestor deactivation; focused cases cover inside/outside and caught rejection. Child identity, callback, queue, membership, UI, and generation remained intact. | Original closed; other retirement bypasses below |
| State P2-3 | Check identity before no-op re-entry | Replaced the real token, caught nested admission rejection, and inspected replacement participants. Body never ran; replacement remained empty and active; old owner was quarantined. Explicit replacement commit published nothing. | Closed |
| State P2-4 | Published debug lookup traverses current membership | Reran candidate addition, discard, and commit. Activity and slot UI remained unpublished until commit; canonical addition/removal observations passed. | Closed |
| State P2-5 | Reconcile participating nested roots after discard | Original `_component` counterexample now clears retained nested membership/cache and permits fresh retry. Publication-only nested construction still leaves discarded registrations. | **Open: incomplete disposition** |
| Code P2-1 | Validate parent and nearest-render ownership before initialization | Reran mismatched leaf/resource constructors. Both rejected before attachment; both root caches remained empty. Focused allocation instrumentation passed. | Closed |
| Code P2-2 | Reject omitted/conflicting scheduler ownership and owned-root activation | Reran owner-only and conflicting-scheduler constructors; no child context was installed. Focused owned-root activation rejection passed. | Closed |
| Code P2-3 | Gate direct component retirement before effects | Same real-context retirement attacks as State P2-2; callback, child pointer, and queued work were preserved. | Original closed |
| Code P2-4 | Preflight component descendants of removed ancestors | Reran committed root → leaf → component omission with a queued nested boundary. Empty root pass rejected and preserved the graph/queue. Candidate-only omission remains admitted. | Original closed; new variant P2-7 |
| Code P2-5 | Published debug membership is current-only | Original candidate-cache activity counterexample no longer reproduces; canonical slot-specific reads passed. | Closed |

## Changed-range analysis

The remediation changes seven runtime modules, adds seventeen narrow closure cases, extends canonical published-membership observations, and adds review/process documentation. Constructor ownership checks, direct/transitive retirement guards, lexical execution depth, identity-checked no-op entry, current-backed debug lookup, and participating-root reconciliation all correspond to merged dispositions. No unrelated product change was identified.

The original execution-fencing correction survives the attacks performed here. The remaining defects concern incomplete coverage of existing invariants:

- P2-5 retains the original cache-reconciliation omission for affected roots without a local pass.
- P2-6 is an internal membership writer still using a newly current-only reader.
- P2-7 checks committed membership but misses previously staged component membership.
- P2-8 omits replacement admission on direct constructor attachment.

**Architectural classification:** None is a **NEW ARCHITECTURAL root cause**. These are bounded reader/writer, retirement-admission, and affected-root bookkeeping omissions within the existing field-only design. Their correction does not require changing the accepted SC1 kernel, manager API, resource protocol, or activation scope. Remediation count remains one implemented, zero accepted; this review does not trigger the architectural stop rule.

## 0. Evidence base

- Verified all five HEADs at start and end; every SHA matched. Final `git diff -- src tests` was empty. A working-tree update to the process ledger appeared during review; its committed version was read through `git show`. No source/test or HEAD movement occurred.
- Read parent/Pyrolyze `AGENTS.md`, the supplied review-loop skill and canonical template, the controlling SC2 document, SingleCohortPlan ownership/failure/publication/checkpoint contracts, SC1-Remediation and SC1-ReviewLoop, both **prior** SC2 reports, RemPlan-1, and committed SC2-ReviewLoop. No other current-round prompt/report was read.
- Inspected the remediation diff and relevant cumulative changes. Runtime evidence includes `src/pyrolyze/runtime/context_state_lcm/field_only_render.py:1–304`, `context_base.py:68–758`, `render_context.py:24–471`, `render_attempt.py:1–387`, `component_call_slot_context.py:50–325`, `_base.py:79–108`, `slot_context.py:11–58`, and native execution/facade/scheduler/generation paths.
- Read `tests/test_runtime_context_state_lcm_field_only_render.py:1–356`, `tests/data/lcm_integration/common_pass_single_cohort.py:1–382`, the canonical membership JSON extension, and the characterization subprocess harness.
- Byte-compared exported `.py`/`.yidl` sources against pinned commits: lifecycle **17 files**, YIDL **45**, Astichi **84**; all matched. Read pinned transaction completion and generated managed/core preparation, application, and discard templates. Actual admitted-class metadata had no transaction hooks or freeze/thaw converters.
- Independently ran the permitted two-target command with Python **3.12.12**, both context-selection variables unset, bytecode disabled, and pytest cache disabled: **33 passed in 4.18s**.

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH="src:$snapshot/yidl-lifecycle/src:$snapshot/yidl/src:$snapshot/astichi/src" \
  "$PYTHON" -m pytest -p no:cacheprovider -q --tb=short \
  tests/test_runtime_context_state_lcm_field_only_render.py \
  tests/test_lcm_integration_characterization.py::test_common_pass_single_cohort_golden
```

Additional probes ran in memory under that same source/environment envelope, using real managers and contexts. Reproductions below use `_root`, `_slot_id`, `_emit`, `_leaf`, `_component`, `_ui`, `_tracker`, and `runtime` loaded through:

```python
import runpy
f = runpy.run_path("tests/data/lcm_integration/common_pass_single_cohort.py")
```

No generated-private-state writes or mocked manager completion were used. One fault probe temporarily replaced a local cleanup method in memory, restoring it afterward.

## 1. Findings

### [P2-5] Reconciliation still misses publication-only discarded nested roots

**Location and invariant:** `src/pyrolyze/runtime/context_state_lcm/field_only_render.py:180–183,301–304`. Affected-root discovery depends on `_enter_context`, so it covers local-pass participants rather than every render root whose registry changed. The SC2 clean-discard contract requires affected caches to agree with current membership, including newly unreachable nested roots.

**Reproduction:** On a fresh activated root, enter `root.pass_scope()`, ensure a component, and invoke a resource-free callback that does **not** enter a local pass:

```python
def render(context):
    with context._state_mgr.publish_write_scope():
        child = runtime.LeafSlotContext(
            context, context, _slot_id(9), seen_in_pass=True
        )
        retained.extend((context, child))
```

Then raise from the parent pass. The actual completion participant list contains only the root local context. After certified discard:

- Root current membership and registry are empty.
- Retained nested current membership is empty.
- Nested registry still contains the discarded leaf.
- `last.reuse_ready` is `True`.

Entering a fresh retained nested pass and ensuring slot 9 returns that same discarded leaf. Published debug activity correctly returns false, but the internal reuse cache remains contaminated.

**Impact:** Clean discard certifies reuse while retaining registrations outside current membership. The original local-pass reproduction is fixed; the required invariant is not.

**Required correction and closure:** Discover affected render roots when construction/registration or publication-only writes affect them, not exclusively on local-pass entry. Preserve the no-second-value-authority boundary. Add this publication-only variant alongside the original regression, asserting empty retained current membership/cache, no reuse of the discarded object, and unaffected independent roots/keys.

### [P2-6] Leaf deactivation replaces candidate membership with the published map

**Location and invariant:** `src/pyrolyze/runtime/context_state_lcm/slot_context.py:55–58`, together with current-only `ContextBaseStateMgr.children_by_slot_id()` at `context_base.py:111–112`. An internal membership writer must edit the candidate map; published readers must remain current-only.

**Reproduction:** Commit leaf A at slot 1. In the next activated root pass, revisit A, create/invoke leaf B at slot 3 with `"keep"`, then call `A.deactivate()`.

Immediately before deactivation, candidate children are `[1, 3]`. Deactivation copies the parent’s **current** map, removes A, and assigns the resulting empty map over the candidate map. Normal outer completion publishes empty membership/UI, although B’s own current UI becomes `["keep"]`.

The same sequence on the unactivated historical route retains slot 3 and root UI `["keep"]`.

**Impact:** An admitted field-only retirement silently drops unrelated work and reports successful completion. This is a reproducible activated-route parity regression, not deferred component retirement or baseline debt.

**Required correction and closure:** Use working/candidate membership for internal removal, retaining current-only public readers. Extend canonical membership observations with staged sibling plus leaf retirement, covering commit and discard: candidate B must survive removing A; current must remain old until publication; discard must restore A.

### [P2-7] Repeated local passes can omit a candidate-only mounted component

**Location and invariant:** `src/pyrolyze/runtime/context_state_lcm/context_base.py:331–354`. Reset clears previous candidate membership, while retirement preflight examines only `current.children_state`. Component removal must remain gated even when the component was introduced earlier in the same still-open attempt.

**Reproduction:** Use a real mounted root callback containing two sequential root local passes:

1. First pass invokes `_component(root, "candidate-only")`; retain its nested render.
2. Queue that nested boundary through the real scheduler.
3. Second pass is empty.

The mounted boundary retains one outer attempt across both passes. The second pass clears the first pass’s candidate map; current membership is still empty, so retirement preflight examines nothing. Outer completion succeeds with empty root membership/UI, while the component and nested UI publish `"candidate-only"` and the nested callback remains mounted and queued.

Observed committed generation is **1** after mount. `root.run_pending_invalidations()` successfully executes the orphan boundary and advances generation to **2**.

**Impact:** A supposedly gated component-removal route publishes an unreachable mounted component and permits successful orphan execution. The committed-ancestor regression does not cover this candidate-only transition.

**Required correction and closure:** Preflight omission of previously staged component-bearing subtrees within the same attempt, not merely omission from committed membership. Do not implement deferred retirement. Add the two-local-pass mounted-boundary regression, requiring rejection, no successful orphan publication/execution, and unchanged committed generation. Re-visiting the same component in the second pass must remain supported.

### [P2-8] Direct constructor attachment bypasses component replacement admission

**Location and invariant:** `src/pyrolyze/runtime/context_state_lcm/_base.py:79–108`, `slot_context.py:18–20`, and `context_base.py:228–231`. Replacement rejection exists in `ensure_resolved_slot()` at `context_base.py:423–425`, but direct constructor attachment overwrites registration and membership without that check. SC2 must reject deferred component replacement before allocation/attachment effects.

**Reproduction:** Commit `_component(root, "old")`, retain its nested render, and queue it. Then:

```python
with root._state_mgr.publish_write_scope():
    replacement = runtime.LeafSlotContext(
        root, root, _slot_id(2), seen_in_pass=True
    )
```

Parent/render ownership matches and the new class is admitted. Construction overwrites slot 2’s cache and membership. No local pass exits, so the retirement check never runs.

After successful completion, current membership contains the replacement leaf, while the old component’s nested callback remains mounted and queued. Generation advances from **1** to **2**. Flushing executes the orphan component and advances generation to **3**.

**Impact:** An ordinary admitted constructor can detach a committed component through the supported publication-scope path without retirement authorization.

**Required correction and closure:** Check existing slot occupancy/replacement admission before direct constructor initialization and attachment; reject the deferred replacement and poison an active attempt when rejection is caught. Add direct colliding-constructor tests under standalone and nested publication scopes, asserting no allocation/registration/membership mutation, preserved component identity/callback/queue/UI/generation, and clean subsequent retry.

## 2. Invariant analysis

The following attacks failed to refute the corrected implementation:

- Native, publication, and no-op lexical bodies retained execution ownership after explicit local end. Later failures preserved their exact primary exception, discarded candidates, preserved committed generation, and allowed clean retry.
- Replacement-token no-op admission rejected before body execution/enlistment. Cleanup preserved the replacement and quarantined the old owner.
- Direct component disposal/deactivation, recursive ancestor deactivation, and omission of a **committed** component-bearing ancestor rejected while preserving scheduler and component state.
- Published addition/removal/activity/slot-specific UI observations remained current-only through rendering and discard.
- Canonical caught-child poison, successful later sibling non-recovery, parent failure after child success, manager sharing, independent roots/keys, and real validation discard passed.
- A cleanup failure injected **after actual manager publication** retained published current UI, left generation uncertainty observable, cleared active local bookkeeping, and blocked retry. No fictitious rollback was performed.

The failures above arise where those protections do not cover all supported membership and publication-only transitions. Passing the focused suite therefore does not establish a closed recovery grammar.

## 3. Risks and next action

This checkpoint adds no filesystem persistence; the reviewed ordering is in-memory lifecycle publication, cache reconciliation, and generation completion. Process-restart durability and asynchronous/parallel rendering are not certified. Deferred resource adapters, broader activation, SC4 migration, and generic manager/cross-key redesign remain outside this verdict.

The owner’s broader results were not independently rerun: 97 focused passes; full default 887 passes/13 unchanged failures/20 skips; broader unactivated 41 passes/14 unchanged failures. They are not an all-green claim or waiver.

**Next action:** Keep SC2 unaccepted and prepare one bounded second remediation addressing P2-5 through P2-8, retaining the verified original closure cases. Settle a new tuple and return these exact counterexamples for reviewer verification.
