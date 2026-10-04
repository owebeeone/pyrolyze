# Lifecycle Integration Completion Plan — Consistency-AXIS REVIEW

**Review object:** Pyrolyze dev-docs/PytoLifecyleIntegPlan.md at 723460d6c1dce75b70f03e355daf20c248bde8ad; DRAFT plan; 2026-10-03  
**Baseline:** Committed views read with `git -C <repo> show <exact-sha>:<path>`.
| Repository | SHA |
| --- | --- |
| Pyrolyze | `723460d6c1dce75b70f03e355daf20c248bde8ad` |
| yidl-lifecycle | `cdf08544deea846bca4fa7e0c468ebee8d41e138` |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` |
| Parent, context only | `a20f8cfb633a268925464eb27728d1934a70aea9` |

**Date:** 2026-10-03  
**Axis:** Consistency: internal coherence, controlling-document agreement, supersession, and satisfiability of checkpoint evidence. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one P2 finding blocks; no P0, P1, or P3 findings. I pre-commit to GO on a revision that resolves P2-1 as specified.

---

## 0. Evidence base

- Verified all five HEADs at start and end. All matched the tuple throughout. Pyrolyze had only permitted untracked review documents; an untracked review-loop ledger appeared during review. yidl-lifecycle and Astichi remained clean. YIDL's excluded dirty changes were unchanged and were not read as authority.
- Read operator authority `review-loop/SKILL.md` and `review-loop/references/review-prompt-template.md`; committed parent and submodule `AGENTS.md` files.
- Pyrolyze controlling documents: `dev-docs/PytoLifecyleIntegPlan.md:1-1213`, `dev-docs/ContextLifecyleMetaprogrammingPlan.md:1-824`, `dev-docs/LifecyleAdoptionPatterns.md:1-493`, `dev-docs/PytoLifecyleIntegI0Findings.md:1-205`, `dev-docs/PytoLifecyleIntegI0Inventory.md:1-234`, and `tests/data/lcm_integration/README.md:1-74`.
- I0 evidence: `tests/test_lcm_integration_characterization.py:1-42`, `tests/data/lcm_integration/characterize.py:1-244`, `tests/data/lcm_integration/transaction_failures.py:1-152`; original/decomposed snapshot boundary observations at `baselines/original.json:1-270` and `baselines/bare_refactor_lcm.json:1-270`, plus monolithic parent-failure observations at `baselines/lcm.json:106-167`. These baseline paths are relative to `tests/data/lcm_integration/`.
- Pyrolyze capability/call-site evidence: `src/pyrolyze/runtime/context_state_lcm/_base.py:1-41`, `slot_context.py:1-76`, `event_handler_slot_context.py:1-57`, `context_base.py:1-470,689-710`, `component_call_slot_context.py:1-310`, and `render_context.py:1-255`; filenames after the first share its directory. Also inspected `src/pyrolyze/runtime/call_site_context.py:1-226`, relevant construction/event facades in `context_bare_refactor_lcm.py:286-464`, and original callback behavior in `context_original.py:962-967,1070-1121`.
- Additional contracts/coverage inspected: `dev-docs/ContextOriginalPublicApi.md:1-245`, `dev-docs/CallSiteContextDesign.md:1-210`, `tests/test_context_graph_no_comp_value_api.py:110-203`, and `tests/test_runtime_context_lcm_phase4.py:1-220`. A committed-view diff confirmed Pyrolyze `src` and `tests` unchanged before live `rg` searches there.
- yidl-lifecycle evidence: `src/yidl_lifecycle/transaction_yidl.py:1-463`; selected harvesting/factory/inheritance sections of `lifecycle_harvester.py:85-255,298-435,460-725`; `lifecycle.py:1-288`; generated constructor/facade templates in `yidl/lifecycle_core.yidl:400-450,540-660` and managed accessors in `yidl/lifecycle_managed.yidl:233-303`. Materialized inherited output was checked at `tests/data/goldens/materialized/yidl_transactional_phase_b_decorator/generated_inherited_output_prettier.py:348-479`.
- Checked lifecycle Phase B constructor/inheritance constraints, Phase G transient lifetimes, Phase H ownership/reference semantics, and Phase F-1 terminology and failure requirements, especially `dev-docs/YidlTransactionalYidlPhaseF-1Plan.md:950-980`. Inspected binding implementation, regeneration command defaults, and existing transaction/harvester test locations. YIDL's committed compatibility shim was read at `src/yidl/runtime/lifecycle.py:1-11`.
- Inspection only: no tests, imports, builds, regeneration, writes, or git mutations. The operator-reported four characterization passes were not independently rerun.

## 1. Findings

### [P2-1] Callback staging compares against published state instead of the surviving candidate

**Location:** Pyrolyze `dev-docs/PytoLifecyleIntegPlan.md:409-416`, reinforced by the guard-preservation instruction at `:440-444` and I3b's instruction to implement this shape at `:795`.

**Violated invariant:** The plan permits multiple local passes inside one outer transaction (`:203-207`) and forbids local publication (`:213-216`). A later successful local pass must update the surviving candidate, while dispatch continues reading published `.current`. The sketch instead uses `.current` for both dispatch visibility and staging-elision decisions.

**Reproduction, statically traced against the committed generated accessors:**
1. Publish callback/key `A`, and retain its stable dispatch handle. Choose ordinary unequal callables `A` and `B`.
2. Begin an outer publication transaction. In the first local pass, call `stage_callback(callback=B, dirty=False)`. Since published key `A != B`, the sketch stages `B`.
3. Finish that local pass without publishing, as required. Published callback/key remain `A`; working callback/key are `B`.
4. In a second successful local pass, call `stage_callback(callback=A, dirty=False)`. Every guard condition is false: published callback exists and published key equals `A`. No assignment occurs, leaving candidate `B`.
5. Publish the outer transaction. The retained dispatch now invokes `B`, although the final successful pass selected `A`.

The existing consumer forwards the caller's `dirty` value unchanged (`src/pyrolyze/runtime/context_state_lcm/context_base.py:689-702`). Managed getters retain the working overlay until completion; `.current` deliberately ignores it (`yidl-lifecycle`, `src/yidl_lifecycle/yidl/lifecycle_managed.yidl:241-278`). No hypothetical savepoint facility is involved.

**Impact:** The prescribed I3b shape publishes a stale intermediate callback. Existing per-pass callback publication advanced the comparison baseline between completed passes; preserving that guard verbatim is incompatible with the proposed longer publication lifetime.

**Required correction:** Compare the staging guard against the effective working/default candidate selection, not `.current`. Keep stable dispatch reading `.current`, retain the approved callback-key equality semantics and dirty-forced identity replacement, and amend the guard-preservation wording accordingly.

**Closure/regression test:** For this draft gate, re-trace the corrected sketch and add this explicit case to I3b's canonical proof. At implementation, exercise two completed local passes under one outer transaction selecting `B` then `A`, with `dirty=False`: dispatch identity stays stable, calls during staging still invoke published `A`, and final publication selects `A`. Retain rollback and distinct-but-equal dirty-forced replacement coverage.

**Root-cause classification:** Bounded facade-selection defect in the prescribed shape, not a new architectural root cause.

## 2. Invariant analysis

- **Containment:** Attempts to derive blanket abort or automatic caught-exception recovery failed. `PytoLifecyleIntegPlan.md:243-290,764-770` requires whole-attempt containment, preservation of entry working state, and persistent boundary invalidation for uncertain attempts.
- **Supersession:** The historical blanket-abort recommendation is explicitly superseded at `:629-632`; I0 observations remain intact. D1/D2 explicitly identify proposed departures from original behavior rather than claim unchanged parity.
- **Construction:** The plan correctly rejects automatic harvesting/chaining of ordinary subclass initializers. Its shared-TM injection and inherited-field prerequisite agree with committed harvesting and generated constructor behavior. Both slot construction branches are explicitly covered.
- **Ownership:** The distinction between nontransactional `binding()`, transactional holder replacement, referent participation, and deterministic domain retirement agrees with Phase H. The plan does not falsely promise immediate resource closure from reference dropping.
- **L0 and ordering:** The pinned manager really is fail-fast in the identified phases. The plan treats drain/report behavior as a prerequisite, not an existing capability, and gates dependent coordinator/hook work on it. D4/D5 retain partial-apply and completion-order decisions.
- **Checkpoint/routing evidence:** I1 requires local-scope safety alongside live sharing; I7 addresses direct imports, exports, and monolithic removal. Historical snapshots are distinguished from approved target expectations. Passing focused tests are not represented as integration readiness.

## 3. Risks and next action

D1-D5, concrete containment facilities where needed, resource timelines, dependency reproducibility, and broader baseline failures remain execution gates, not defects merely because they are pending. Future L0 verification should include generated hook composition as well as minimal protocol participants.

**Next action:** Revise the callback staging sketch and I3b evidence obligation to resolve P2-1, then request the focused consistency re-verdict on the revised committed tuple. No runtime implementation or activation is authorized by this review.
