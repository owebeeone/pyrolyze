# Holder-First Lifecycle Integration Plan — SAFETY-AXIS REVIEW

**Review object:** DRAFT `pyrolyze/dev-docs/PytoLifecyleIntegPlan.md` and `pyrolyze/dev-docs/PytoLifecyleIntegHolderFirstPlan-ReviewPackage.md` at `78e3184132eae33169ae3c329be35f3146ed338a`; re-verdict round 1, 2026-10-03.
**Baseline:**
- Pyrolyze: `78e3184132eae33169ae3c329be35f3146ed338a`.
- yidl-lifecycle: `cdf08544deea846bca4fa7e0c468ebee8d41e138`.
- YIDL: `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`.
- Astichi: `387ca5e1da76204ee60922094734c13ee36383c0`.
- Parent workspace: `a20f8cfb633a268925464eb27728d1934a70aea9`, context only.

Sources were inspected through pinned `git show` and clean source reads. Parent/YIDL inspection used committed views only.
**Date:** 2026-10-03.
**Axis:** Safety: degraded paths, publication/recovery boundaries, ownership, and migration blast radius. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — both prior P2 findings independently closed; no new findings. This is plan-only approval, not runtime implementation approval.

---

## Prior-Finding Closure

| Finding | Independent retrace | Status |
| --- | --- | --- |
| P2-1: Published-versus-candidate callback guard changed baseline behavior | Revised plan lines 468–476 compare against `.current`; lines 505–512 and 879 require the historical result. Fixture `callback_selection.py:15–42` publishes A, stages B then A with `dirty=False`, and dispatches before completion. Reference source and expected JSON independently agree: successful completion ends at B; failure retains A. | Closed |
| P2-2: Raw callback equality conflated distinct bound receivers | Revised plan lines 449–454 normalize bound methods by receiver identity and function; lines 500–503 state the contract. Fixture lines 45–79 uses distinct value-equal receivers and repeated method objects. Normalized keys distinguish their receivers; successful completion dispatches B, failure dispatches A, and dispatch identity remains stable. | Closed |

Closure rests on source-derived traces and committed fixture expectations, not the lane owner's reported test results or another reviewer's verdict.

## Changed-Range Analysis

The reviewed delta is `0de04bc487b3e03c9444e40ce02587046b33dcec..78e3184132eae33169ae3c329be35f3146ed338a`.

- Plan lines 445–476, 500–512, and 879 correct callback selection requirements to conform to the existing controlling reference behavior.
- Plan line 626 removes ambiguous completion-ownership deletion language. Lines 917–923 explicitly retain independent call-site pass completion until U1/U2.
- The new callback fixture, expected JSON, selector-specific harness cases, and README observations record the two counterexamples without rewriting historical snapshots.
- No new architectural root cause was found. These corrections change neither a public interface nor the controlling ownership/compatibility contract; they restore conformance to that contract. Fresh architectural reviewers are therefore not required for this bounded remediation.

## 0. Evidence base

All paths below are relative to their owning repository.

- Ran `pwd`, all five repositories' `rev-parse HEAD` at start and end, and source-repository status inspections. Every HEAD matched the required tuple at both boundaries. Pyrolyze's observed untracked files were current-round reviewer prompts; their contents were not read.
- Read the permitted committed `dev-docs` diff, `PytoLifecyleIntegHolderFirstPlan-RemPlan-1.md:1–31`, and the complete ReviewPackage.
- Inspected revised plan ranges 429–540, 615–679, 785–853, 871–945, 1079–1100, and 1318–1405; carried forward prior-round inspection of unchanged scope and acceptance text.
- Read applicable AGENTS instructions; revisited `PytoLifecyleIntegI0Findings.md:96–143,171–246` and `PytoLifecyleIntegI0Inventory.md:27–47,83–108,145–171,199–234`.
- Read characterization `README.md:1–108`, new fixture `callback_selection.py:1–92`, its baseline JSON:1–18, and `tests/test_lcm_integration_characterization.py:1–54`.
- Retraced original runtime selection/publication/rollback through `context_original.py:655–717,737–812,962–967,1071–1121,2346–2357`; monolithic selection through `context_lcm.py:958–963,2791–2818,2836–2848`; confirmed the existing sentinel in `context_state_lcm/_support.py:315`.
- Independently compared complete committed original/monolithic callback sources, decomposed event-handler source, and `call_site_context.py` across the two Pyrolyze revisions: unchanged. Compared all five historical baseline JSON files: unchanged.
- Rechecked lifecycle capability evidence in `transaction_yidl.py:211–265` and `lifecycle_core.yidl:634–659`. No tests, builds, regeneration, writes, or git mutations were performed.

## 2. Invariant analysis

**Repeated staging preserves historical publication.** Starting from published A, both B and the subsequent A are compared against published A. B stages; A does not overwrite it. During staging, dispatch still reads A. Successful completion publishes B; rollback clears the pending selection and retains A. The revised sketch now reproduces this deliberately retained baseline debt instead of silently repairing it.

**Equal receivers cannot redirect dispatch to the wrong object.** Distinct live receivers produce different normalized keys despite their value equality. Repeated method objects for the same receiver/function produce the same key. The expected four dispatches are `A,A,A,B` after success and `A,A,A,A` after failure. Stable dispatch identity and staged invisibility are preserved.

**Holder replacement does not imply manager unification.** The revised call-site mapping agrees with I4a and the U1/U2 boundary. The independent completion owner remains; removal targets legacy storage/implementation, not independent completion itself. The scope-expansion attack therefore fails.

**Failure preconditions remain explicit.** Constructor injection remains an I1a prerequisite. D4/D5-dependent mechanisms remain gated; mandatory retirement/delivery cannot simply move onto existing fail-fast hooks. Stronger D1–D3 outcomes remain deferred, not falsely supplied by this GO.

**Disclosure scope does not expand.** Added characterization emits synthetic callback labels and dispatch-identity booleans; it introduces no runtime logging or user-data capture.

## 3. Risks and next action

The new expectations characterize reference behavior, not a completed generated-holder migration. Test execution was prohibited; the reported seven passing snapshots were not independently rerun. Existing early publication, fail-fast behavior, and broader resource-lifetime limitations remain outside this approval.

**Next action:** record plan-only Safety GO for this exact tuple. Runtime changes, default-runtime switching, API changes, and manager unification require separate authorization and implementation verification.
