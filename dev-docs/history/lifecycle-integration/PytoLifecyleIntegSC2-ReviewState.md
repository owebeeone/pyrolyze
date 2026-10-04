# SC2 Private Field-Only Render Wiring — STATE-AXIS REVIEW

**Review object:** SC2 implementation diff `1b246d47e934835a4871fbbfc651fae78440b913..53c41674f43ab97401ac9b30a79575c19ab5dca9`, controlled by `dev-docs/PytoLifecyleIntegSC2.md`, DRAFT implementation checkpoint dated 2026-10-04.
**Baseline:** Pyrolyze `53c41674f43ab97401ac9b30a79575c19ab5dca9`; yidl-lifecycle `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`; parent context only `a20f8cfb633a268925464eb27728d1934a70aea9`. Documents/dependency code were read through pinned `git show` views or verified clean exports; Pyrolyze source had no tracked working-tree changes.
**Date:** 2026-10-04
**Axis:** State: transition legality, publication ordering, failure isolation, cleanup, and retry certification. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — five P2 findings block. I pre-commit to GO on a revision that resolves P2-1 through P2-5 as specified.

---

## 0. Evidence base

- Verified all five HEADs against the exact tuple at review start and end. All matched. The final Pyrolyze tracked diff remained empty. No files were written, builds run, or git state mutated.
- Read parent/Pyrolyze `AGENTS.md`, the supplied review-loop skill and canonical template, all sections of `PytoLifecyleIntegSC2.md`, `PytoLifecyleIntegSingleCohortPlan.md`, `PytoLifecyleIntegSC1-Remediation.md`, and `PytoLifecyleIntegSC1-ReviewLoop.md`. No current-round peer prompt/report was read.
- Inspected the entire 13-file SC2 diff. Source locations below use `context_state_lcm/` to mean `src/pyrolyze/runtime/context_state_lcm/`. Read `_base.py:79-99`, `context_base.py:68-760`, `field_only_render.py:1-257`, `render_context.py:24-449`, `render_attempt.py:1-387`, `component_call_slot_context.py:50-319`, and `leaf_slot_context.py:1-43`, plus related facade, slot attachment/deactivation, support, and generation-tracker paths.
- Read `tests/data/lcm_integration/common_pass_single_cohort.py:1-337`, its complete authored JSON target, `tests/test_runtime_context_state_lcm_field_only_render.py:1-148`, and the characterization harness. Inspected pinned lifecycle transaction completion and generated managed-field preparation/application/discard code. Byte-compared all exported `.py`/`.yidl` sources against their pinned commits: lifecycle 17 files, YIDL 45, Astichi 84; all matched.
- Independently ran the permitted two-target pytest command with Python 3.12.12, clean dependency exports, both context-selection variables unset, bytecode disabled, and pytest cache disabled: **16 passed in 4.33s**. The owner's broader results were not independently rerun and are not an all-green claim.
- Ran write-free, in-memory probes against real managers and contexts. Reproductions below use the fixture helpers `_root`, `_slot_id`, `_emit`, `_leaf`, `_component`, `_ui`, and `_tracker` at fixture lines 21-60, loadable with `runpy.run_path("tests/data/lcm_integration/common_pass_single_cohort.py")`. Findings required no generated-private-state writes or mocked manager completion.

## 1. Findings

### [P2-1] Direct terminal completion can outlive neither a native callback nor an open publication scope
**Location and invariant:** `context_state_lcm/field_only_render.py:99-118,151-197` and `leaf_slot_context.py:30-42`. Completion must wait for the enclosing render execution to finish; an escaping callback failure must poison the attempt before publication.

**Reproduction and impact:** Seed a leaf with `"old"` in a successful root pass. Invoke it standalone with a callback that calls `_emit(context, "published-before-error")`, then `context.end_pass()`, then raises `ValueError("original callback failure")`. At `end_pass()`, leaf current UI changes and committed generation advances from 1 to 2 while the callback is still running. The later failure escapes as `RuntimeError("local render scope is not active")` because `invoke_native` tries to roll back the already-released handle. The failed callback's UI remains published. Separately, `root.begin_pass()` followed by an open `publish_write_scope()`, emission, `root.end_pass()`, and a later body exception publishes before that scope exits; the saved owner remains `reuse_ready=True`, and retry succeeds.

**Required correction and closure:** Retain an execution claim around the entire native invocation and fence direct completion while lexical publication claims remain open. Early local release must not complete the cohort or cause cleanup to replace the callback's primary failure. Add regressions for both sequences asserting unchanged current UI/generation until lexical exit, discard on failure, the original primary error, and clean subsequent retry.

### [P2-2] Direct component deactivation performs deferred retirement before the gate rejects it
**Location and invariant:** The retirement check at `context_state_lcm/context_base.py:350-356` occurs after the reachable disposal path in `component_call_slot_context.py:228-231,306-319`. Deferred component retirement must be rejected before side effects, not repaired through field rollback.

**Reproduction and impact:** Seed `_component(root, "old")` and retain its child context. In the next root pass, ensure the same component and call its public `deactivate()`. The call removes scheduler ownership, clears the child's mounted callback, and sets the component child pointer to `None`. Normal parent exit subsequently raises `"component retirement is not admitted by SC2"`. Lifecycle rollback restores current membership and old UI, but not the child pointer or callback. Raising a parent exception after deactivation produces the same mixed state. Cleanup nevertheless certifies reuse.

**Required correction and closure:** Reject activated component deactivation before entering disposal, including recursive ancestor-deactivation paths. Do not implement deferred retirement here. Test direct deactivation inside and outside a pass, caught rejection, and recursive deactivation; original child identity, mounted callback, scheduler state, membership, UI, and generation must remain intact.

### [P2-3] No-op scoped re-entry bypasses transaction identity admission
**Location and invariant:** `context_state_lcm/field_only_render.py:121-127`. Re-entry may omit reset and another begin, but must still verify the owned transaction identity before admitting the body. It must never adopt a replacement token.

**Reproduction and impact:** Inside `root.pass_scope()`, call the real manager's `rollback(PASS_TX_KEY)` and then `replacement = begin(PASS_TX_KEY)`. Enter another `root.pass_scope()` and emit `"foreign candidate"`. The active-local-scope shortcut admits the body and enlists its writes into `replacement`. Only outer exit detects `"owned render transaction is missing or replaced"`. The replacement is preserved but contaminated: a subsequent explicit manager commit publishes `"foreign candidate"` while committed render generation remains 0.

**Required correction and closure:** Apply the owner's open/identity admission checks before the active-scope shortcut yields. Add a replacement-token re-entry regression proving the nested body never runs, replacement participants/values remain untouched, the old owner is quarantined, and cleanup never completes the replacement.

### [P2-4] Published debug membership reads the candidate lookup cache
**Location and invariant:** `context_state_lcm/render_context.py:87-100,224-251`, particularly `debug_is_active` at lines 234-235. The SC2 contract makes published debug/membership readers current-only; registration is explicitly a lookup cache, not publication.

**Reproduction and impact:** On a fresh activated root, create and invoke a new leaf inside `root.pass_scope()`. Before outer exit, `root.debug_is_active(slot_id)` returns `True`, although `root.debug_children_of()` returns `()` and current membership is empty. Raise to discard the pass; activity then becomes `False`. The reader therefore reports unaccepted membership as active. Slot-specific debug readers also select objects through this working cache rather than current membership.

**Required correction and closure:** Resolve published debug activity and slot-specific observations from current graph membership, keeping the working lookup cache separate for internal construction. Extend canonical observations for candidate additions and removals: published readers must retain old membership throughout the pass, reflect success only after commit, and remain unchanged after discard.

### [P2-5] Registry reconciliation misses newly discarded nested render roots
**Location and invariant:** `context_state_lcm/field_only_render.py:239-257`. After certified discard, every affected render-root lookup cache must agree with its current membership, including nested roots created during the discarded attempt.

**Reproduction and impact:** On a fresh activated root, create `_component(root, "nested-candidate")`, retain `component.child_context`, then raise from the parent pass. After clean discard, root membership/cache are empty and the retained nested root's current membership is empty. However, its `_slots_by_id` still contains the candidate leaf, and `nested.debug_is_active(_slot_id(1))` returns `True`. Reconciliation starts exclusively from the scheduler root's current graph, so this newly unreachable nested root is never cleared. The purportedly clean retry state retains discarded registrations.

**Required correction and closure:** Reconcile affected nested render caches even when their owning component disappears from current membership. Existing participating-context bookkeeping can identify them; no resource deactivation or second value authority is needed. Add a discarded-new-component regression retaining the nested reference and asserting empty current membership and registry, then verify fresh retry and unrelated roots/keys remain unaffected.

## 2. Invariant analysis

- Canonical clean passes held manager sharing, provisional child success, current/candidate UI separation, repeated-pass order, independent roots, and independent queued boundary completion.
- Additional real-context probes held sticky caught-child poison, later-sibling non-recovery, other-key preservation during render discard, leaked-scope rejection, clean retry after local assembly failure, and caught recursive local completion remaining unpublished.
- High-level slot-expression, container, directive, keyed-loop, event-handler, event-binding, and app-context-override entry points rejected before supplied callback work; catching rejection did not restore committability. This does not excuse the component-retirement bypass.
- An injected adapter failure after actual publication retained published UI, left generation uncertainty observable, cleared active execution bookkeeping, and blocked retry rather than fabricating undo. Ordinary validation failure used the real manager and discarded without advancing committed generation.
- Architectural classification: **P2-1 is a newly exposed SC2 execution-ownership root**. P2-2 through P2-5 are localized gate, admission, reader, and reconciliation omissions. The remedies do not require changing the accepted SC1 manager API or undertaking generic manager redesign.

## 3. Risks and next action

The diff introduces no filesystem persistence; reviewed failure boundaries are in-memory lifecycle publication, local cleanup, registry reconciliation, and generation completion. Asynchronous rendering, resource adapters, broad activation, and cross-key atomicity remain unaccepted and outside this verdict. Recorded default/decomposed baseline failures remain visible and unwaived.

**Next action:** Keep SC2 unaccepted, prepare one bounded remediation mapping all five IDs to corrections and closure tests, settle a revised tuple, and return these original counterexamples for verification.
