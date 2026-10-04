# SC2 Remediation Round 2 — CODE-AXIS REVIEW

**Review object:** `ca731d89a0086e0bff48dc426d1b5b1472aba869..4d1b9b089333e99cb98381939db311c2b7ce8bde`, within cumulative SC2 `1b246d47e934835a4871fbbfc651fae78440b913..4d1b9b089333e99cb98381939db311c2b7ce8bde`. Controlling document: `dev-docs/PytoLifecyleIntegSC2.md` at the corrected SHA, DRAFT implementation checkpoint, dated 2026-10-04.
**Baseline:** Pyrolyze `4d1b9b089333e99cb98381939db311c2b7ce8bde`; yidl-lifecycle `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`; parent context only `a20f8cfb633a268925464eb27728d1934a70aea9`. Documents were read through pinned `git show`; dependency exports were byte-verified against those commits.
**Date:** 2026-10-04.
**Axis:** Code: architecture, interfaces, call graphs, ownership, compatibility, and error paths. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one new P2 finding blocks. The original prior counterexamples close. I pre-commit to GO on a revision that resolves P2-9 as specified.

---

## Prior-finding closure table
| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| Code P2-1 | Validate parent/render ownership before initialization | Original leaf/resource cross-root constructors, including reversed links, reject; caught rejection poisons the attempt; both caches remain empty. | Closed |
| Code P2-2 | Reject omitted/conflicting scheduler ownership and owned activation | Original omitted/unrelated scheduler constructors reject; owned standalone activation rejects. Additional ownership hole identified below. | Original closed; see P2-9 |
| Code P2-3 | Gate direct component deactivation/disposal | Original outside/inside/caught disposal and ancestor sequences preserve child identity, callback, queue, UI, and generation. | Closed |
| Code P2-4 | Preflight removed component-bearing subtrees | Original committed root → native leaf → component omission rejects with its queued boundary preserved. Candidate-only variants also reject. | Closed |
| Code P2-5 | Make published debug membership current-only | Original candidate addition remains inactive/invisible; discard remains invisible; successful publication becomes visible. | Closed |
| Code P2-6 | Edit candidate membership during deactivation | Original leaf and plain-slot removal preserves the staged sibling on commit; discard restores original membership. | Closed |
| Code P2-7 | Preflight preceding candidate components | Original two-native-invocation omission rejects; no orphan publication or generation advancement; repeat-component reuse succeeds. | Closed |
| State P2-1 | Retain lexical execution claims | Original native/publication early-end failures, plus lexical/no-op variants, preserve the exact primary error and current UI/generation; retry succeeds. | Verified closed on Code axis |
| State P2-2 | Reject direct/transitive retirement before effects | Independently reran disposal, deactivation, and ancestor sequences; destructive state and scheduler changes do not occur. | Verified closed on Code axis |
| State P2-3 | Check identity before no-op re-entry | Original replacement-token body never runs; replacement participants remain empty; replacement survives; old owner is quarantined. | Verified closed on Code axis |
| State P2-4 | Separate published membership from the reuse cache | Original activity/UI contradiction no longer reproduces across candidate, discard, and commit. | Verified closed on Code axis |
| State P2-5 | Track all affected nested roots | Original local-pass and round-1 publication-only discards clear retained caches; fresh ensure does not reuse discarded leaves. Registry-only removal/clear also reconciles detached roots. | Verified closed on Code axis |
| State P2-6 | Preserve candidate siblings during leaf removal | Original successful and failed sibling/removal sequences preserve the correct candidate/current maps. | Verified closed on Code axis |
| State P2-7 | Reject candidate-only mounted component omission | Original two-local-pass mounted callback rejects; orphan queue is cancelled; subsequent flush cannot advance generation. | Verified closed on Code axis |
| State P2-8 | Reject direct colliding constructors before initialization | Original standalone/nested publication collisions reject and poison caught attempts; candidate-only, cache-only, and current-only occupancy also reject before initialization. | Verified closed on Code axis |

## Changed-range analysis
Round 2 changes five runtime modules: constructor occupancy admission; candidate deactivation reads; preceding-candidate retirement inventory; affected-root tracking; and orphan scheduler cancellation. It adds ten narrow cases and extends the canonical sibling-preservation/repeat-reuse observations. Other changes are controlling/process documents. No dependency, accepted SC1 completion mechanism, activation default, resource protocol, or historical target changed.

P2-9 is an additional omission in owned-render admission: scheduler/parent checks establish only one direction of ownership. **It is not a NEW ARCHITECTURAL root cause.** Reciprocal ownership checks fit the existing constructor/execution boundary without changing the manager API, completion architecture, or deferred resource protocols.

## 0. Evidence base
- Verified all five HEADs at start and end; every SHA matched. Final `git diff -- src tests` was empty. No files, builds, caches, bytecode, or git state were written. No other current-round prompt/report was read.
- Read parent/Pyrolyze `AGENTS.md`, the supplied review-loop skill/template, SC2’s admission/ownership/completion contracts, SingleCohortPlan’s ownership/publication/checkpoint contracts, SC1-Remediation/ReviewLoop, both initial and round-1 reports, both remediation plans, and committed SC2-ReviewLoop.
- Inspected round-2 and cumulative changes. Principal source ranges: `src/pyrolyze/runtime/context_state_lcm/field_only_render.py:1–331`, `_base.py:1–132`, `context_base.py:1–763`, `render_context.py:1–482`, `component_call_slot_context.py:1–325`, `slot_context.py:1–59`, `leaf_slot_context.py:1–50`, and `render_attempt.py:1–387`. Traced retained facade constructors, UI propagation, scheduler methods, generation completion, and visitor membership traversal.
- Read narrow tests:1–514 and canonical fixture:1–419, its target extension, and the subprocess harness. Byte-verified 17 lifecycle, 45 YIDL, and 84 Astichi Python/YIDL source files. Read real transaction completion and generated preparation/application/discard templates; inspected actual participant types and admitted-class hook/converter metadata.
- Ran the permitted two-target pytest command with pinned exports, selection variables unset, bytecode disabled, and cache provider disabled: **43 passed in 4.34s**. Independently reran original counterexamples and additional in-memory probes using real managers, without generated-private-state writes or mocked completion.

## 1. Findings
### [P2-9] Owned-render admission permits a second executable root for an occupied component
**Location and invariant:** `src/pyrolyze/runtime/context_state_lcm/render_context.py:45–57` verifies the component’s parent membership and scheduler relationship, but never checks its existing `_child_context_state_mgr`. Boundary entry at `176–185` likewise does not verify that the component actually points to this render root. UI propagation at `289–295` trusts the reverse owner pointer. An activated component’s execution/UI authority must belong to its actual child root; another constructor must not manufacture a competing authority.

**Reproduction:** Load the real helpers with `runpy.run_path("tests/data/lcm_integration/common_pass_single_cohort.py")`. Commit `_component(root, "published-child")`, retain its installed child N, then construct `ghost = runtime.RenderContext(owner_slot=component, scheduler_root=root)`. Construction succeeds although `component.child_context is N`. Mount this callback on `ghost`:

```python
def render():
    with ghost.pass_scope():
        _leaf(ghost, "wrong-owner")
    ghost._refresh_committed_ui_from_children()
```

After `ghost.mount(render)`, root and component current UI are `["wrong-owner"]`, while the actual child N still publishes `["published-child"]`; the component pointer remains N and generation advances to 2. Queueing N and `ghost` produces duplicate boundary IDs `[2, 2]`; flushing executes both and advances generation to 4. A separate failed-parent variant cancels the initially queued ghost, but requeueing that retained ghost subsequently executes successfully. These probes use constructors and runtime methods, not generated-private-state writes.

**Impact:** A constructor admitted by the private gate creates an executable root that does not own the component it can update. Published component UI can disagree with its actual child graph, and scheduler identity is no longer unique. Cache reconciliation cannot authorize this competing ownership.

**Required correction and closure:** Reject duplicate owned-root construction before lifecycle initialization when the component already has a child. Before execution or owner-UI propagation, require reciprocal ownership after construction has completed. Caught rejection must poison the active attempt. Add committed- and candidate-owner regressions inside/outside an attempt, asserting unchanged installed identity, callback, queue, current UI, and generation; no duplicate boundary execution; and continued normal nested construction/reuse. Do not dispose or replace the installed child.

## 2. Invariant analysis
The original retirement, sibling-preservation, current-reader, token-identity, and affected-cache attacks now fail. Clean discard cancels queued unpublished boundaries while preserving queued published boundaries. Repeated component invocation remains supported.

Native/publication/direct/no-op execution fencing preserves primary errors and prevents premature completion. Real validation discard, sticky caught-child failure, independent roots/keys, and clean retry pass. An injected cleanup failure after actual publication preserves published values, leaves generation uncertainty observable, and blocks retry rather than fabricating undo. An independent unactivated component probe retains its historical separate manager and early publication.

## 3. Risks and next action
Full/default and broader suites were not independently rerun. Owner evidence remains 897 passes/13 unchanged failures/20 skips/1 warning and 41 passes/14 unchanged failures, respectively; neither is an all-green claim. Deferred activation, resource adapters, SC4 migration, and excluded dependency work remain uncertified.

**Next action:** Keep SC2 unaccepted and return P2-9 for lane-owner disposition under the remediation cap. This report authorizes no additional architectural patch.
