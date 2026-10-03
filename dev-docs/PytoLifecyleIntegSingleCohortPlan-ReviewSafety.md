# PytoLifecyleIntegSingleCohortPlan — Safety-AXIS REVIEW

**Review object:** `dev-docs/PytoLifecyleIntegSingleCohortPlan.md` at Pyrolyze `bad7b1c7eaae6b09eaede3803f036a1cbb9d05d7`, including the specified precedence notices and preflight additions. DRAFT DESIGN, dated 2026-10-03; not runtime implementation acceptance.

**Baseline:**
- Pyrolyze: `bad7b1c7eaae6b09eaede3803f036a1cbb9d05d7`
- yidl-lifecycle: `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4`
- YIDL: `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`
- Astichi: `387ca5e1da76204ee60922094734c13ee36383c0`
- Parent workspace, context only: `a20f8cfb633a268925464eb27728d1934a70aea9`

Product and dependency source inspection used `git show <exact-sha>:<path>`, never dirty dependency source files.

**Date:** 2026-10-03

**Axis:** Safety: attack text-authorized ownership, publication, recovery, isolation, and rollout failures. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — Zero P0, P1, P2, or P3 findings. This approves only the gated draft design, not implementation feasibility, I3a completion, or activation.

---

## 0. Evidence base

- Ran `pwd`, and `rev-parse HEAD` plus `status --short` for all five repositories at both start and end. Every SHA matched the requested tuple; all status listings remained unchanged. Astichi was clean. Dirty dependency/workspace changes and untracked review artifacts were excluded.
- Read workspace and Pyrolyze `AGENTS.md`. The canonical `review-loop` skill was not discoverable in the configured skill locations; no independent certification of its additional process requirements is claimed.
- Read the amendment, lines 1–357; integration-plan authority and affected construction, completion, resource, checkpoint, test, acceptance, and decision clauses; `PytoLifecyleIntegI3aPlan.md`, lines 1–243; `PytoLifecyleIntegI3aPlan-ReviewLoop.md`, lines 1–61; `PytoLifecyleIntegI1bEvidence.md`, lines 1–146; and `PytoLifecyleIntegI3aPreflight.md`, lines 1–291. Historical acceptance was not inherited.
- Inspected the specified object-file diff for `4a2b416..bad7b1c7eaae6b09eaede3803f036a1cbb9d05d7`, including the preflight script, both JSON baselines, README additions, and harness entry. Read `tests/test_lcm_integration_characterization.py`, lines 1–68, and historical `transaction_failures.py`, lines 1–152.
- Read Pyrolyze `context_state_lcm/context_base.py`, lines 1–676; `render_context.py`, lines 1–409; `_base.py`, lines 1–118; relevant `_support.py` pass, directive, container, scheduler, and keyed-loop paths, lines 396–785; `component_call_slot_context.py`, lines 1–315; and targeted owner-facade construction, setter, scope, leaf, and render delegation paths.
- Also read `runtime/call_site_context.py`, lines 1–226; `app_context.py` generation implementation, lines 106–138; `slot_context.py`, lines 1–53; `leaf_slot_context.py`, lines 1–43; and the lifecycle adapter.
- Read pinned yidl-lifecycle `transaction_yidl.py`, lines 1–463, and `lifecycle_core.yidl` transaction, token, facade, and hook templates, especially lines 292–593.
- Ran no tests, builds, exports, or mutation commands. Historical test counts are provenance only. No current-round peer prompt or report was read.

## 2. Invariant analysis

**Caught failure cannot become success through later work.** The attempted sequence was: child stages UI, raises, parent catches, sibling succeeds, parent returns normally. Amendment lines 148–169 explicitly make failure sticky, prohibit publication, and require an abort chained from the first cause. The preflight’s eventual failed-candidate publication is identified as historical debt, not an accepted target.

**Local scope and completion ownership are separate.** Lines 107–124 and 136–146 require actual local reset despite an already-active owned key, prohibit borrower TM begins, retain no-op same-context re-entry, diagnose duplicate direct entry, and block publication with leaked borrowers. The listed caller migration prevents treating a predicate-only patch as completion.

**Foreign or corrupted ownership does not authorize destructive cleanup.** An externally active render key is rejected before reset, generation start, or rendering. Later token/manager mismatch poisons the owned attempt; missing or replaced identity is reported rather than used to roll back a replacement transaction. External publication is expressly not represented as undone (lines 107–117, 170–179).

**Publication-phase uncertainty cannot unlock wider routes.** The pinned TM can partially apply or finish applying before throwing, while clearing key activity. Therefore inactive-key observation cannot prove rollback safety. Lines 195–210 acknowledge this exact limitation, require an audited field-only proof, and block callback/resource-bearing routes pending separately approved prerequisites. They prohibit fictitious generation undo after partial publication.

**Generation and rerender boundaries remain bounded.** Lines 74–86, 125–128, 189–193, and 267–287 route scheduled and standalone ownership through one path, make nested completion provisional, and prevent synchronous completion callbacks from attaching to a finishing attempt. A scheduler flush is not silently widened into a batch transaction.

**Other keys and roots are not collateral completion targets.** The owner must pass `PASS_TX_KEY` explicitly; unrelated active keys survive render failure. Independent roots retain separate managers. No multi-key atomicity is claimed (lines 72–82, 212–217, 331–332).

**Membership discard is not resource cleanup.** Pinned source shows eager registry changes, component disposal, legacy call-site acceptance, and local notification delivery. The amendment does not certify these from manager sharing: lines 219–245 and SC2–SC4 retain their authority, require audits/adapters, block mixed-owner activation, and preserve dirty/metadata permissions and snapshots until their replacement gates pass.

**Partial success cannot become false migration acceptance.** SC1 accepts private mechanics only; SC2 accepts a field-only proof only; SC3 stops routes retaining separate publication or unclassified throwing callbacks; SC4 still requires writer policies and the deletion ledger. Historical fixtures remain distinguishable from target observations. No unconditional “never worse than status quo” guarantee is made.

## 3. Risks and next action

The remaining risks are implementation obligations, not demonstrated text-authorized defects: proving complete field-only discard against the actual manager, preserving failure causes when cleanup raises, enforcing reuse-readiness after incomplete cleanup, and accounting for component replacement, registries, resource retirement, and invalidations during a pass. A green proof must not bypass these gates.

The next action is for the lane owner to file this report and evaluate the independent dual-review acceptance gate. No runtime implementation or activation follows from this verdict alone.

