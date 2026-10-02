# Holder-First Integration Plan — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/PytoLifecyleIntegPlan.md` and `dev-docs/PytoLifecyleIntegHolderFirstPlan-ReviewPackage.md`, DRAFT at Pyrolyze `78e3184132eae33169ae3c329be35f3146ed338a`. Re-verdict round 1, dated 2026-10-03.
**Baseline:** Pyrolyze `78e3184132eae33169ae3c329be35f3146ed338a`; yidl-lifecycle `cdf08544deea846bca4fa7e0c468ebee8d41e138`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`; parent workspace `a20f8cfb633a268925464eb27728d1934a70aea9`, context only. Revised documents and evidence were read through committed `git show`; parent/YIDL contents were inspected exclusively through committed views.
**Date:** 2026-10-03
**Axis:** Consistency against the controlling graph, internal obligations, compatibility reference, and satisfiable evidence requirements. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero open findings. Both prior P2 findings and the prior P3 finding are closed. This is plan-only acceptance, not runtime certification or implementation authorization.

---

## Prior-Finding Closure

| Prior finding | Independent retrace and revised evidence | Disposition |
| --- | --- | --- |
| **P2-1: Bound-method identity key lost** | Plan lines 449–454 restore the reference normalization body verbatim, apart from the helper name. Distinct value-equal receivers produce different receiver IDs, so selecting B with `dirty=False` reaches assignment. Repeated methods from the same receiver/function retain the same key. The fixture at `callback_selection.py:45–79` exercises replacement and failure; expected JSON records B after success, A after failure, unpublished dispatch remaining A, and stable dispatch identity. | **Closed** |
| **P2-2: B-then-A assertion silently repairs baseline behavior** | Plan lines 469 and 505–512 now compare against `.current`; I3b at line 879 requires the same result. Starting with published A, selecting B stages B; selecting A again is skipped against published A. Success therefore publishes B; failure retains A. This independently matches both reference guards and `callback_selection.py:15–42`, with corresponding expected JSON. The alternative ending at A is explicitly deferred for separate approval. | **Closed** |
| **P3-1: Deletion map removes retained call-site manager** | Plan line 626 now deletes legacy record/manager implementation without deleting independent completion ownership. It agrees with lines 587–591, ledger lines 651 and 657, I4a lines 917–923, and U2 lines 1092–1096. `call_site_context.py:146–226` confirms the existing independent pass-manager boundary being preserved. | **Closed** |

These closures concern the document defects. They do not certify a migrated implementation.

## Changed-Range Analysis

The plan changes are localized to callback-key normalization, the published-state guard, its compatibility explanation and I3b proof, and the call-site deletion row. The review package is unchanged. Supporting additions comprise a canonical callback fixture, one structured snapshot, harness parametrization, and README documentation.

**Contract classification:** The correction changes the erroneous proposed sketch and acceptance text to conform to the already controlling reference rule. It does not change a runtime interface, completion owner, compatibility contract, or D4/D5 decision. No new architectural root cause was identified; these bounded corrections do not trigger fresh architectural review.

## 0. Evidence base

Paths below are relative to their owning repository.

- Verified all five HEADs at start and end; every SHA matched the supplied tuple. Pyrolyze status contained only the two authorized untracked reviewer prompts. Lifecycle and Astichi were clean. No current-round peer prompt/report contents were inspected.
- Read the current plan, lines 1–1405; review package, lines 1–54; merged remediation plan, lines 1–31; and my prior Consistency report, lines 1–73. Inspected the permitted `0de04bc487b3e03c9444e40ce02587046b33dcec..78e3184132eae33169ae3c329be35f3146ed338a` documentation diff.
- Rechecked applicable parent/Pyrolyze `AGENTS.md`. Independently compared committed I0 findings, inventory, and review-package contents across the two Pyrolyze revisions: unchanged. The initial controlling-graph audit also covered the historical metaprogramming/adoption documents and pinned lifecycle constructor/TM capability evidence.
- Retraced reference selection, publication, rollback, and dispatch in `context_original.py:962–967,1070–1121,2187–2211` and `context_lcm.py:958–964,2648–2654,2791–2848`. Independently compared both complete reference files across revisions: unchanged.
- Read `callback_selection.py:1–92`, `baselines/callback_selection.json:1–18`, characterization harness lines 1–54, and README lines 1–108. Independently compared all five historical snapshots across revisions: unchanged. Also compared the call-site manager and decomposed event-handler source: unchanged.
- Used inspection commands only. No tests, builds, regeneration, writes, or Git mutations occurred. The harness statically contains seven cases; the lane owner’s passing-run claim was not independently executed. Counterexamples were independently source-traced against committed fixtures and expected JSON.
- The named review-loop skill was not discoverable in the exposed skill locations; the supplied canonical reviewer contract and committed package constraints were applied.

## 2. Invariant analysis

- **Callback selection and dispatch:** Both original counterexamples now satisfy reference parity and the plan’s own I3b obligations. All four new expected observations follow from the reference guards: calls remain A during staging; successful completion selects B; failed completion retains A. Dispatch identity remains stable.
- **Evidence satisfiability:** The harness selects original or monolithic LCM before importing runtime code in fresh subprocesses and compares both against the same structured snapshot. It characterizes references, not the future decomposed implementation; the plan preserves that distinction.
- **Completion ownership:** The corrected map, ledger, I4a, U2, architecture contract, and acceptance checklist consistently retain independent cohorts through holder replacement. Removing legacy implementation no longer instructs premature manager sharing.
- **Deferrals and historical authority:** The correction leaves superseded recommendations, historical observations, and pending D4/D5 gates unchanged. The revised callback debt classification now agrees with the controlling prohibition on silently repairing baseline behavior.
- **Deletion obligations:** Lifecycle publication/discard still replaces manual callback transfer/reset methods. Retaining domain cleanup and independent completion owners does not authorize retaining a duplicate field engine.

## 3. Risks and next action

The new fixture does not validate a migrated callback holder. I3b must later exercise these same compatibility cases on the target implementation; I4a must prove retained independent completion. Existing runtime defects and pending D4/D5 decisions remain outside this GO.

**Next action:** Record plan-only GO for this exact tuple. Any implementation, beginning with I1a, still requires separate execution authority.
