# Holder-First Lifecycle Integration Plan — SAFETY-AXIS REVIEW

**Review object:** DRAFT `dev-docs/PytoLifecyleIntegPlan.md` and `dev-docs/PytoLifecyleIntegHolderFirstPlan-ReviewPackage.md` at Pyrolyze `0de04bc487b3e03c9444e40ce02587046b33dcec`; diff from `60b955ae512daecea6d30f97408b94e77299a926`.
**Baseline:** Pyrolyze `0de04bc487b3e03c9444e40ce02587046b33dcec`; yidl-lifecycle `cdf08544deea846bca4fa7e0c468ebee8d41e138`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`; parent workspace `a20f8cfb633a268925464eb27728d1934a70aea9` (context only). Pinned documents and parent/YIDL sources were read with `git show`; clean consumer/library sources were inspected directly.
**Date:** 2026-10-03
**Axis:** Safety: degraded and mixed-version paths, completion ownership, irreversible effects, recovery, disclosure, and migration blast radius. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — two P2 findings block. I pre-commit to GO on a revision that resolves P2-1 and P2-2 as specified, with the revised tuple verified.

---

## 0. Evidence Base

Paths below are relative to their owning repository.

- Verified all five HEADs at review start and end: every value matched the exact tuple. Pyrolyze had only authorized untracked prompt noise; lifecycle and Astichi were clean. Dirty YIDL and unrelated parent changes were excluded.
- Read the controlling plan, lines 1–1390, and review package, lines 1–54; inspected the requested `dev-docs` diff.
- Read `PytoLifecyleIntegI0Findings.md`, lines 1–288; `PytoLifecyleIntegI0Inventory.md`, lines 1–234; characterization README, all three probe sources, and harness. Inspected baseline failure/recovery observations and shared-completion results.
- Traced Pyrolyze constructors/completion through `context_state_lcm/{_base,slot_context,context_base,render_context,slot_expr_slot_context,event_handler_slot_context}.py`, owner-factory references in `context_bare_refactor_lcm.py`, `call_site_context.py:60–226`, and `slot_expr.py:517–690`.
- Callback comparison evidence: `context_original.py:655–664,699–717,779–812,962–967,1071–1121`; `context_lcm.py:2791–2818`; decomposed `event_handler_slot_context.py:19–34`. Read the existing phase-3 callback tests.
- Lifecycle capability evidence: `transaction_yidl.py:71–463`; generated-constructor source in `yidl/lifecycle_core.yidl:634–659`; inheritance harvesting; `bindings.py:17–47`; regeneration command defaults. Historical adoption/metaprogramming documents were consulted only for retained behavioral goals.
- Commands were inspection-only: `pwd`, `rev-parse`, `status --short`, pinned `show`/`diff`, `rg`, `nl`, `sed`, and `cat`. No tests, builds, regeneration, writes, or git mutations occurred. Reproductions below are source-derived, not newly executed.
- The referenced review-loop skill was not found in the exposed skill locations. The supplied canonical prompt and package supplied the review procedure. No current-round peer prompt or report contents were read.

## 1. Findings

### [P2-1] I3b Requires An Unclassified Callback Behavior Change

**Location:** `dev-docs/PytoLifecyleIntegPlan.md:460–467,491–497,864`.

**Violated invariant:** Holder replacement preserves the existing runtime contract; pre-existing defects are recorded rather than silently repaired (`39–52`). The I3b target instead requires a different observable callback outcome without identifying it as a separately approved change.

**Reproduction:** Commit plain callback A. In the next active pass, select B and then A for the same handler, both with `dirty=False`, and successfully complete that pass. Repeated selection is reachable: `context_original.py:783–805` reuses the same slot without rejecting a second visit. The original guard compares both selections against committed A: B stages, the subsequent A selection skips assignment, and completion publishes B. The monolithic and decomposed guards have the same behavior. The proposed working-candidate guard overwrites B with A, exactly as the plan mandates.

**Impact:** A holder-only migration changes which application function the retained dispatch invokes after acceptance. Calling this sequence a compatibility proof conceals a baseline bug repair inside the migration.

**Required correction:** Preserve the reference outcome for holder-first acceptance, or explicitly classify the A-ending sequence as a pending behavioral correction requiring separate approval before I3b depends on it. Update both the sketch and checkpoint proof consistently; this review does not choose the preferred eventual behavior.

**Closure/regression test:** Extend canonical callback coverage with published A → pending B → pending A, successful completion, and failed completion. Record the reference’s B-after-success/A-after-failure observations separately from any subsequently approved target. Verify dispatch remains A while selections are unpublished.

### [P2-2] Raw Callback Keys Lose Bound-Receiver Identity

**Location:** `dev-docs/PytoLifecyleIntegPlan.md:459,464`; compare `src/pyrolyze/runtime/context_original.py:962–967`.

**Violated invariant:** The sketch must preserve callback-key equality semantics (`491`). The selected original/monolithic reference normalizes bound callbacks using receiver identity; the sketch uses the bound method itself.

**Reproduction:** Create distinct receivers `a` and `b` whose `__eq__` returns true, with the same handler method implementation but separate effect destinations. Their bound methods compare equal. Publish `a.handle`, then select `b.handle` with `dirty=False` and complete successfully. The reference keys contain `id(a)` versus `id(b)`, so it selects B. The sketch’s raw keys compare equal, so its guard skips the assignment and dispatch continues invoking `a.handle`.

**Impact:** Callback replacement can silently retain the wrong receiver and direct subsequent effects to the previous object. `compare="identity"` on `_callback` cannot help because the assignment is never reached.

**Required correction:** Preserve the reference’s bound-method key normalization in the runtime-only consumer sketch and implementation obligation. Do not substitute raw callable equality for receiver identity, or move this domain policy into the generic lifecycle library.

**Closure/regression test:** Add canonical replacement coverage using distinct value-equal receivers, plus repeated bound-method objects from the same receiver. Successful replacement must invoke the new receiver; failed replacement must retain the old receiver; dispatch identity must remain stable.

## 2. Invariant Analysis

Other attacks did not establish additional findings:

- **Shared-key composition:** The committed probe demonstrates premature joint publication and whole-key rollback. The plan acknowledges both, retains completion cohorts, and blocks unsupported holder-boundary mappings rather than claiming nested depth provides isolation.
- **Constructor substitution:** Injection precedes factory evaluation; both constructor branches and multiple inheritance are explicitly covered. Attachment removal waits for explicit caller coverage, limiting construction-orphan risk.
- **Fail-fast cleanup:** Mandatory retirement/delivery cannot move onto pinned hooks before approved L0 evidence. Generated-hook draining and domain-batch draining are distinguished; manager reset is not presented as completed cleanup.
- **Lifetime and reentry:** Holder/reference/referent responsibilities remain separate. Explicit cleanup, refcount compatibility, transient-batch capture, independent invalidations, and completion reentry gates are required.
- **Release and scope:** Routing requires parity/export/regression evidence and retains the original fallback. D1–D3 hardening and U1/U2 remain separate work. No production-data collection or external disclosure mechanism is proposed.

## 3. Risks And Next Action

This is a plan review, not runtime safety certification. Existing suite failures, decomposed-path parity gaps, dirty-dependency provenance, and pending D4/D5 decisions remain implementation constraints, not additional findings.

**Next action:** Revise the callback sketch and I3b acceptance wording to resolve P2-1/P2-2, then re-review the pinned revision. No implementation or runtime switch is authorized by this report.
