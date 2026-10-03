# PytoLifecyleIntegSingleCohortPlan — Consistency-AXIS REVIEW

**Review object:** `dev-docs/PytoLifecyleIntegSingleCohortPlan.md` at Pyrolyze `bad7b1c7eaae6b09eaede3803f036a1cbb9d05d7`, DRAFT dated 2026-10-03; associated precedence notices and preflight tests/JSON.
**Baseline:** Pyrolyze `bad7b1c7eaae6b09eaede3803f036a1cbb9d05d7`; yidl-lifecycle `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`; parent workspace `a20f8cfb633a268925464eb27728d1934a70aea9`, context only. Product and dependency sources were inspected through `git show` at these exact revisions.
**Date:** 2026-10-03
**Axis:** Consistency: internal coherence, controlling-document agreement, supersession exactness, source reality, and verification satisfiability. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero P0/P1/P2 findings; two nonblocking P3 documentation findings. This verdict covers the gated DRAFT design only, not implementation feasibility, I3a completion, or runtime activation.

---

## 0. Evidence base

- Ran `pwd`, and `rev-parse HEAD` plus `status --short` for all five repositories at the start and end. Every HEAD matched the requested tuple and remained unchanged. Existing excluded workspace/dependency changes remained unchanged. One authorized object-external review output appeared in Pyrolyze; its contents were not read.
- Read workspace/repository `AGENTS.md` and the canonical review-loop skill, including document-amendment review, peer blindness, severity, and acceptance rules.
- Read the amendment, lines 1–357; controlling integration-plan completion, construction, migration, I3–I6, U1/U2, D1–D5, testing, sequencing, and acceptance sections; I3a addendum, lines 1–243; historical I3a acceptance ledger, lines 1–61; I1b evidence, lines 1–146; preflight, lines 1–291.
- Inspected the object-file diff `4a2b416..bad7b1c7eaae6b09eaede3803f036a1cbb9d05d7`, including precedence notices, the preflight script, both new JSON snapshots, fixture README, and harness registration.
- Read committed Pyrolyze sources: `context_state_lcm/context_base.py`, lines 1–676; `_base.py`, lines 1–118; relevant `render_context.py` construction, boundary, completion, reader, invalidation, and delivery paths; `_support.py` scope/finish/directive/container/keyed-loop paths; `component_call_slot_context.py`, lines 1–315; owner-facade construction, pass delegation, dirty/metadata setters, and render-boundary delegation.
- Read `runtime/call_site_context.py`, lines 1–226, and `runtime/app_context.py`, lines 1–156. Read pinned yidl-lifecycle `transaction_yidl.py`, lines 1–463, and `yidl/lifecycle_core.yidl`, lines 1–670.
- Inspected the characterization harness, `characterize.py`, its decomposed historical JSON, construction fixture, and focused context-base, leaf-rerender, and slot-expression tests.
- Ran no tests, builds, writes, or git mutations. Reported historical test counts were not independently reproduced and were not treated as implementation evidence.

## 1. Findings

### [P3-1] The “Exact Supersession” table omits affected normative clauses

**Location:** Amendment lines 18–36; integration plan’s “Existing TM Limits To Respect,” lines 378–381, and “Event Callback Selection,” lines 543–547.

**Violated invariant:** An exact supersession inventory must account for each affected controlling clause, including clauses only partially replaced.

**Reproduction:** Follow the table literally. Neither named section appears in its earlier-location column. Nevertheless, lines 378–381 still describe the single outer publication-key design as deferred, while the amendment selects outer completion on `PASS_TX_KEY`. Lines 543–547 constrain event-handler deactivation against moving every retirement to outer root success, while the amendment selects eventual outer participation for render-owned actions subject to an ordering audit.

**Impact:** The chosen target remains clear from the precedence notices and amendment body, so this does not establish an unsafe execution authorization. However, a clause-by-clause audit cannot close these entries using the advertised exact table; it must infer their disposition.

**Required correction:** Add these locations explicitly. Replace the obsolete publication deferral, and distinguish the resource completion-owner shift from the still-retained deactivation, lifetime, and D5 ordering gates. Do not broadly repeal resource compatibility.

**Closure test:** Repeat the controlling-document clause audit. Each affected sentence must have an explicit replacement or retained-gate disposition, without deriving exceptions solely from the amendment’s general direction.

### [P3-2] The live-test transition inventory covers only the preflight assertion

**Location:** Amendment lines 273–282 and 353–356; `tests/test_lcm_integration_characterization.py`, lines 15–20; `tests/test_runtime_context_state_lcm_context_base.py`, lines 95–111 and 182–200; `tests/test_runtime_context_state_lcm_leaf_rerender.py`, lines 21–37.

**Violated invariant:** The verification transition must distinguish historical reproduction from current-checkout acceptance for every affected live assertion.

**Reproduction:** Implement the selected contract and perform the explicitly described preflight-assertion replacement. Other required-suite entries still demand the opposite behavior: the constructor test requires distinct nested/root managers; the scope test treats an externally activated key as local activity; the leaf helper renders under an externally begun key without a completion owner. The live decomposed I0 characterization also compares caught-child recovery against a JSON snapshot containing successful fallback publication and no boundary abort.

**Impact:** These tests are valid characterization at the reviewed revision, not current defects. Once their routes adopt the new contract, the prescribed transition leaves additional predictable failures requiring ad hoc disposition. Those failures must not be confused with the unrelated 13/14 baseline debt or resolved by rewriting historical evidence.

**Required correction:** Extend the transition ledger to name these entries and their checkpoint dispositions: migrate supported current assertions, preserve historical script/JSON reproduction at its recorded revision, and retain original-runtime observations unchanged. Specify timing for intentionally unmigrated routes.

**Closure test:** A document audit accounts for each listed entry. At implementation, the focused suite plus target fixture contains neither an obsolete live expectation nor an unexplained skip; preserved historical observations remain reproducible separately.

## 2. Invariant analysis

- **Single authority:** Attempts to find a second field engine failed. Owner storage expressly excludes copied values, child maps, dirty snapshots, and participant commit callbacks. Lifecycle remains responsible for field publication/discard.
- **Admission and local scope:** The selected mechanics separate local activity from key activity, reject unsupported external-key admission before reset/generation work, retain transaction identity, and forbid borrower completion. No-op scoped re-entry and direct duplicate entry have distinct specified behavior.
- **Failure composition:** Caught failure cannot make the owned attempt committable. Normal outer return after recorded failure raises an abort; body exceptions retain precedence. Missing/replaced tokens do not authorize rollback of a replacement token.
- **Pinned TM compatibility:** Source confirms depth-counted nested begins, whole-key rollback, sequential multi-key completion, and fail-fast completion dispatch. The amendment does not assume savepoints, atomic multi-key completion, or a phase-aware commit result.
- **Production gates:** Field-only proof requires participant auditing. Callback/resource routes cannot widen on an assumption that commit exceptions imply no publication. Incomplete cleanup blocks certified reuse; clearing an owner reference is explicitly insufficient.
- **Resource and writer retention:** The legacy call-site manager demonstrably owns separate legacy lifecycle records. Its migration is gated, not accomplished by injection. Dirty/metadata permissions and snapshot-removal conditions remain visibly unresolved; SC2/SC3 cannot falsely complete I3a.
- **Controlling history:** Notices correctly limit prior acceptance to historical revisions. I4/I5 and D5 resource sequencing remain gated, while broad D2/D3 hardening stays deferred. Historical green characterization is not promoted into target acceptance.

## 3. Risks and next action

No blocking consistency defect was established. Feasibility of complete field-only failure cleanup, subsequent bounded adapters, and dirty/metadata policies remains unproven and explicitly gated; this review does not close those implementation questions.

**Next action:** Record the two bounded documentation corrections in the amendment and transition ledger, preserving the existing implementation and activation gates.

