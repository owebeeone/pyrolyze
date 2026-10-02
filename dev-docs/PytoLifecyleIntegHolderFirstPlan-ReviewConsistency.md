# Holder-First Integration Plan — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/PytoLifecyleIntegPlan.md` and `dev-docs/PytoLifecyleIntegHolderFirstPlan-ReviewPackage.md`, DRAFT at Pyrolyze `0de04bc487b3e03c9444e40ce02587046b33dcec`, dated 2026-10-03.
**Baseline:** Pyrolyze `0de04bc487b3e03c9444e40ce02587046b33dcec`; yidl-lifecycle `cdf08544deea846bca4fa7e0c468ebee8d41e138`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`; parent workspace `a20f8cfb633a268925464eb27728d1934a70aea9`, context only. Parent/YIDL contents were inspected exclusively through committed `git show`; clean Pyrolyze/lifecycle sources were also read directly.
**Date:** 2026-10-03
**Axis:** Consistency against the controlling graph, internal obligations, reference behavior, and satisfiable evidence requirements. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — two P2 findings block; one additional P3 finding remains. I pre-commit to GO on a revision that resolves P2-1, P2-2, and P3-1 as specified.

---

## 0. Evidence base

Paths below are relative to their owning repository.

- Verified all five HEADs at the start and end; every SHA matched the supplied tuple. Pyrolyze status contained only the two authorized untracked reviewer prompts; lifecycle and Astichi were clean. Neither prompt’s contents nor any current-round peer material was inspected.
- Read the plan, lines 1–1390, and review package, lines 1–54; inspected the requested `60b955ae512daecea6d30f97408b94e77299a926..0de04bc487b3e03c9444e40ce02587046b33dcec` documentation diff.
- Read applicable parent/Pyrolyze/lifecycle `AGENTS.md`; I0 findings, lines 1–260; inventory, lines 1–234; historical metaprogramming plan, lines 1–824; adoption patterns, lines 1–493.
- Read characterization README, lines 1–88; harness, lines 1–46; `characterize.py`, lines 1–244; `shared_completion.py`, lines 1–88; `transaction_failures.py`, lines 1–152; both manager snapshots; runtime snapshots’ caught-failure and parent-failure sections.
- Traced construction/completion through `context_bare_refactor_lcm.py`, `_base.py`, `context_base.py`, `slot_context.py`, `render_context.py`, `event_handler_slot_context.py`, `slot_expr_slot_context.py`, and `call_site_context.py`. Checked reference callback selection in `context_original.py:655–727,779–805,962–967,1070–1108` and `context_lcm.py:2767–2834`.
- Checked lifecycle marker defaults, generated constructor injection and write enforcement, `transaction_yidl.py:71–335`, and Phase F-1’s manager contract at lines 632–760.
- Commands were inspection-only: `pwd`, `rev-parse`, `status --short`, the permitted diff, `git show`, `rg`, `nl`, `sed`, and `cat`. No tests, builds, regeneration, writes, or Git mutations occurred. Reproductions below are source-traced sequences, not executed tests. The named review-loop skill was not discoverable in the exposed skill locations; the supplied prompt/package process constraints were applied.

## 1. Findings

### [P2-1] Callback sketch drops the reference’s bound-method identity key

**Location:** Plan lines 459–467 and 491–502; I3b at line 864 requires implementing this shape. Reference: `context_original.py:962–967,1085–1088`; monolithic LCM: `context_lcm.py:2797–2802`.

**Violated invariant:** Callback-key selection must preserve the selected reference’s behavior. The reference normalizes bound methods to a tuple containing receiver identity and function; the sketch instead uses `callback_key = callback`.

**Reproduction and impact:** Publish `a.handler`. Let distinct receivers `a` and `b` compare equal, share the same handler function, but produce distinguishable effects. In the next pass select `b.handler` with `dirty=False`. Their bound methods compare equal, so the sketch skips assignment and dispatch continues targeting `a`. The reference’s receiver IDs differ, so it selects `b`. `compare="identity"` on `_callback` cannot help because the staging guard prevents reaching the assignment.

**Required correction:** Preserve the reference’s bound-method key normalization in the proposed shape, or explicitly gate a separately approved change. Do not substitute blanket identity comparison for the established key policy.

**Closure/regression test:** Extend canonical callback coverage with equal-but-distinct receivers and `dirty=False`; verify stable dispatch identity, old-receiver visibility during staging/rollback, and new-receiver selection after acceptance.

### [P2-2] The B-then-A acceptance assertion silently repairs reference behavior

**Location:** Plan lines 491–497 and I3b’s proof at line 864. Conflicting scope: plan lines 39–52 and 1217–1220; review package lines 52–53.

**Violated invariant:** Holder compatibility must not make baseline bug repair an unconditional acceptance requirement. Changed reference outcomes require a separately approved target.

**Reproduction and impact:** Publish callback A. Within one subsequent pass, select B and then A for the same slot, both with `dirty=False`, and complete successfully. The reference compares both selections against committed A: B is staged, the second A is skipped, and completion publishes B (`context_original.py:1085–1097`). Reusing that slot is permitted by lines 779–805. The monolithic guard has the same behavior. The plan instead requires final A and describes that result as preservation. Consequently, reference parity and I3b’s mandatory assertion cannot both pass without a behavioral change outside the package’s accepted scope.

**Required correction:** Record the existing B result as baseline debt. Either preserve it for holder-only acceptance or make the proposed A result conditional on a separately recorded semantic/bug-fix approval, with distinct historical and target expectations.

**Closure/regression test:** Characterize the public same-slot B-then-A sequence under original and monolithic runtimes. Require the migrated compatibility target to match that observation unless the separate change is approved; then retain both the baseline evidence and explicitly approved A target.

### [P3-1] Migration map still instructs removal of the retained call-site manager

**Location:** Plan line 611, “Remove” column: “Legacy call-site record access and private pass TM.” Contradicting obligations: lines 572–576, 642, 887–908, and 1077–1080.

**Violated invariant:** The deletion map must distinguish replacing the legacy manager implementation from removing independent completion ownership. Independent call-site completion is retained through holder integration; allocation removal belongs to U2.

**Reproduction and impact:** Use the migration map to prepare I4a’s deletion checklist. It requires deleting the private pass TM, whereas I4a and its ledger require retaining an independent pass TM. Following the deletion wording can drive premature render-manager sharing, which the shared-completion fixture demonstrates cannot isolate same-key completion.

**Required correction:** Amend the row to remove legacy record access and the legacy manager implementation while retaining an explicit lifecycle-owned independent pass manager/cohort until U2.

**Closure/regression test:** Cross-check every manager-removal instruction against I4a/U2. The later standalone/integrated call-site fixture must verify independent completion without publishing or discarding pending render work.

## 2. Invariant analysis

- **Deferral consistency otherwise held:** The revised architecture, sequence, decision register, and acceptance checklist generally place U1/U2 after holder replacement and do not require deferred outer atomicity, savepoints, or universal lifetime hardening. Historical recommendations were not treated as current authority.
- **Capability claims held:** Source and snapshots support the stated nested-depth, whole-key commit/rollback, fail-fast dispatch, and manager-teardown limitations. Phase F-1 supports the proposed drain/report direction; the plan does not falsely claim that capability is already implemented.
- **Construction prerequisite held:** Generated initialization installs the supplied manager before field initialization. The plan explicitly covers both ordinary-slot construction branches, decorated derived construction, and separate attachment.
- **Evidence boundaries held:** Historical test counts have provenance; baseline failures are disclosed. Runtime selectors are isolated by the characterization harness, and the plan warns that direct imports are not rerouted by environment selection. Historical snapshots and future approved targets are distinguished, except for P2-2.

## 3. Risks and next action

This is a document verdict, not runtime certification. D4/D5 remain pending, existing failures remain debt, and future checkpoints still require concrete key/ownership mappings and execution evidence.

**Next action:** Revise the callback specification and contradictory deletion row, then re-review the revised exact tuple. Do not treat this revision as plan-only GO or implementation authorization.
