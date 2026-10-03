# PytoLifecyleIntegSingleCohortPlan — Consistency-AXIS REVIEW

**Review object:** `dev-docs/PytoLifecyleIntegSingleCohortPlan.md` at Pyrolyze `3c8a8167830c3c057b91f4ad7b2a0679d13e9ba5`, gated DRAFT design dated 2026-10-03. Focused re-verdict from `bad7b1c7eaae6b09eaede3803f036a1cbb9d05d7`.
**Baseline:** Pyrolyze `3c8a8167830c3c057b91f4ad7b2a0679d13e9ba5`; yidl-lifecycle `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`; parent workspace `a20f8cfb633a268925464eb27728d1934a70aea9`, context only. Product and dependency inspection used exact committed `git show` views.
**Date:** 2026-10-03
**Axis:** Consistency: controlling-document agreement, precise supersession, verification transitions, and changed-range coherence. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — both prior P3 findings closed; zero new P0/P1/P2/P3 findings. This approves only the gated design, not runtime implementation, I3a completion, or activation. An object-external status discrepancy is recorded below.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| P3-1 | Enumerate the omitted TM-limit and event-deactivation clauses while retaining applicable gates | Amendment lines 27 and 29 explicitly identify integration-plan paragraphs 378–381 and 543–547. Selected render ownership replaces the deferral/removal-boundary restriction; atomicity, callback visibility, lifetime, cleanup, and SC3/D5 gates remain | CLOSED |
| P3-2 | Enumerate affected live tests and preserve source-pinned historical reproduction | Amendment lines 305–329 account for every named counterexample, tie migration to changed-route checkpoints, preserve historical source/JSON, and prohibit unexplained skips or misclassification as baseline debt | CLOSED |

These are documentation closures. They do not certify that future test migrations or runtime changes have been implemented.

## Changed-range analysis

The delta is a bounded clarification of the previously reviewed design, not a new architecture, interface, mutation, or compatibility boundary.

The added supersession rows make existing owner-selection consequences explicit. The transition ledger supplies missing checkpoint dispositions without changing current tests or rewriting evidence. The registration/callback example specializes the existing other-key and resource-writer audit: it requires an identified field, governing key, writer, completion owner, authorization, and removal ordering before live routing.

It neither grants two independent overlays to one field nor assumes that independently completing another key protects a stale render removal. Existing prohibitions on implicit other-key completion, new public/library APIs, and unsupported activation remain operative.

**No NEW ARCHITECTURAL root cause was identified.** The delta does not invalidate the original proof or require a fresh architectural review round.

## 0. Evidence base

- Verified all five HEADs and `status --short` listings at start and end. Every HEAD matched the revised tuple and remained unchanged; excluded workspace/dependency listings were unchanged.
- End status additionally listed untracked `dev-docs/PytoLifecyleIntegSingleCohortPlan-ReviewSafety-1.md`. This exceeds the stated prompt-only noise allowance. Its contents were not read. No committed tuple or reviewed-object movement occurred.
- Read the complete corrected amendment, lines 1–404, and its exact diff from the original reviewed revision. Read the authorized package’s “Round 1 Verdicts And Bounded Corrections,” lines 49–64; closure was independently checked rather than inferred from that disposition.
- Re-read integration-plan lines 357–381 and 513–547, including the precise old clauses underlying P3-1.
- Re-read `tests/test_runtime_context_state_lcm_context_base.py`, lines 95–223; leaf-rerender tests, lines 1–69; characterization harness, lines 1–68; `characterize.py`, lines 138–226; decomposed JSON’s caught-failure observation, lines 1–105; preflight reproduction instructions, lines 220–273.
- Compared committed outputs at both Pyrolyze revisions for 19 relevant files: eight previously inspected runtime sources, three affected test modules, two fixture scripts, three historical JSON snapshots, and three controlling documents. All comparisons were identical and untruncated.
- Re-read corrected-revision registry construction/mutation and pass/publication helpers. Re-read pinned lifecycle key permission/enlistment code, `lifecycle_core.yidl` lines 420–443, and manager key configuration/admission code, `transaction_yidl.py` lines 325–387.
- Retained the original independent source analysis, repository/workspace instructions, and canonical review-loop process. No current-round peer prompt/report contents were read. Ran no tests, builds, archives, writes, or git mutations.

## 2. Invariant analysis

**Supersession counterexample:** The previously omitted paragraphs now have explicit dispositions. The amendment does not silently turn the resource-owner shift into approval of a lifetime redesign or new retirement order.

**Live-test counterexamples:** Lines 313–315 explicitly replace the independent-manager assertion, separate genuine local activity from key activity, and remove the leaf helper’s unsupported external-begin route when SC2 changes those paths. Line 316 retires only the decomposed preflight assertion while retaining the original parameter. Line 317 accounts for the mixed I0 fixture before changed caught-failure routing, preserving unaffected and still-unmigrated observations. Lines 319–329 pin historical reproduction to the original source and require investigation of additional contrary assertions.

**Registration/removal interleaving:** An independently accepted registration followed by failed render removal cannot be treated as automatically protected by separate keys. Lines 230–238 require authorization and removal ordering before activation. Current immediate registry mutations therefore remain audited migration work, not falsely certified provisional behavior.

**Original safeguards:** Private-owner storage still excludes duplicate field authority and participant commit callbacks. Admission, sticky failure, explicit render-key ownership, current/candidate separation, field-only participant auditing, and no-fictitious-undo rules remain unchanged. Resource, dirty/metadata, L0/D5, and I3a completion gates remain intact.

## 3. Risks and next action

Runtime feasibility, adapter behavior, shared-registry ordering, and dirty/metadata policies remain unproven implementation gates. Historical reproduction and future verification were inspected structurally, not executed.

**Next action:** The lane owner should file this re-verdict and record both closures together with the unexpected object-external status delta. This GO does not certify prompt-only workspace noise or authorize runtime work.
