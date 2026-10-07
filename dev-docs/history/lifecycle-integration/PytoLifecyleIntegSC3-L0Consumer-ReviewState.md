# SC3-L0 Private Consumer — State-AXIS REVIEW

**Review object:** SC3-L0 private completion-evidence consumer, fixtures, and verification document at Pyrolyze `223d04aa322df32e2adc5f5cd45b27111b111f4b`, diff `dc9e4ccd21715bf8c639d07a2ec4d46af936b2c2..223d04aa322df32e2adc5f5cd45b27111b111f4b`. Controlling document: `dev-docs/PytoLifecyleIntegSC3-L0Plan.md`, Consumer Contract and consumer checkpoint; implementation candidate `dev-docs/PytoLifecyleIntegSC3-L0Consumer.md`, acceptance pending, 2026-10-08.
**Baseline:** Pyrolyze `223d04aa322df32e2adc5f5cd45b27111b111f4b`; yidl-lifecycle `05554397d1837ecbeafa36e4685477dd5ff30fc6`; YIDL `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`; Astichi `1c47f781d3804130fdd61cbee07a3b2e4529158a`. Documents and historical source were read through `git show`; runtime inspection used unchanged tracked files.
**Date:** 2026-10-08.
**Axis:** State: completion authority, publication/generation ordering, failure retention, quarantine, and recovery legality. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — two P2 findings block; no P0, P1, or P3 findings. I pre-commit to GO on a revision that resolves P2-1 and P2-2 as specified while preserving the verified closures.

---

## 0. Evidence base
- Verified all four exact HEADs and statuses at start and end: unchanged. Dependencies were clean; Pyrolyze had only the two excluded untracked rendering documents, neither read. No files, builds, caches, bytecode, or Git state were written. The reviewed diff passed `git diff --check`.
- Read workspace/Pyrolyze `AGENTS.md` and the supplied review-loop skill. Read `dev-docs/README.md`, the L0 plan’s observation/algorithm/consumer/checkpoint sections, the complete consumer checkpoint, SingleCohortPlan’s ownership/failure/publication rules, SC3’s writer/prerequisite/gate sections, and yidl-lifecycle `dev-docs/L0CompletionVerification.md`.
- Inspected both changed runtime files completely: `src/pyrolyze/runtime/context_state_lcm/render_attempt.py:1–464` and `field_only_render.py:1–335`. Retraced supporting local-pass, published-reader, generation, cache, and owned-render admission paths without reviewing deferred resource implementation.
- Read retained owner tests `tests/test_runtime_context_state_lcm_render_attempt.py:1–875`, field-only tests `tests/test_runtime_context_state_lcm_field_only_render.py:1–704`, characterization harness `tests/test_lcm_integration_characterization.py:1–80`, canonical fixture `tests/data/lcm_integration/common_pass_single_cohort.py:1–553`, transaction traces, relevant JSON, and fixture README. Read prior SC1 State reports and SC2 State round-2/final reports and acceptance ledger; no current-round peer report was accessed.
- Ran the permitted three-file pytest command with selectors unset, bytecode/cache disabled, and local-source exports: **native 119 passed in 4.55s; Python backend 119 passed in 10.79s**. These runs included the retained SC1/SC2 regressions and current canonical completion matrix.
- Independently loaded pre-L0 manager `371dfa530a975c27f7a6c09a7648f7f00532ab29:src/yidl_lifecycle/transaction_yidl.py` into a registered ephemeral module. Historical output exactly matched `baselines/transaction_failures.json`; current output exactly matched `baselines/transaction_completion_outcomes.json`. Partial-apply current values were historical `[1,0,0]`, current `[1,0,1]`. All seven prior SC2 JSON sections were unchanged.
- Additional in-memory probes reproduced both findings. Separate probes verified release failure before/after removal, cache failure, generation failure before/after mutation, and late callback token relabeling. The latter probes retained actual publication/errors and denied retry as described below. One initial exploratory probe referenced an uncreated leaf after admission failed; corrected probes completed.

## 1. Findings
### [P2-1] Local admission does not fence mutations of the retained token’s identity
**Location:** Pyrolyze `src/pyrolyze/runtime/context_state_lcm/render_attempt.py:113–123`; terminal metadata comparison at `234–238`.

**Violated invariant:** The consumer captures the original key/ID before callbacks and must preserve original completion authority. Earlier identity loss cannot become authoritative merely because metadata later looks normal. Admission must reject compromised identity before local reset or execution.

**Reproduction:** Load the field-only test helpers with `runpy.run_path("tests/test_runtime_context_state_lcm_field_only_render.py")`. Create `_root()` and enter its private `completion.attempt_scope()`. Obtain the active `PASS_TX_KEY` token, save `token.tx_key`, assign `token.tx_key = object()`, then enter `root.pass_scope()` and call `_emit(root, "candidate")`. Restore the original key in `finally`, before outer completion. No manager mocking or record replacement is involved.

Observed: the local body entered; no exception escaped; current UI contained `"candidate"`; generation advanced to **1**; `published=True`, uncertainty false, and reuse certified. `_require_identity` compares only the transaction object, so it misses the relabeling at the admission boundary. Changing `tx_id` to `999` similarly admitted the body; after restoration, generated preparation rejected the stale token, but the consumer certified a reusable nonpublication outcome instead of quarantining the earlier identity loss.

A terminal variant also passed: immediately after real manager finalization, assigning `token.tx_id = True` for original ID `1` was accepted because the consumer uses loose numeric equality there. Generation advanced and retry entered.

**Impact:** Unsupported identity changes can escape quarantine and become successful publication or reusable failure. The accepted library’s checks during completion do not replace the consumer’s admission checks.

**Required correction:** Use the captured original metadata consistently at local admission and terminal observation: original transaction object, exact integer ID type/value, and original key identity. Record observed loss irreversibly; restoration must not rehabilitate authority. Keep replacements untouched and preserve actual published values.

**Closure test:** Parameterize key/ID mutation before scoped and no-op admission, restoring metadata before outer exit. Require rejection before local reset/body, sticky uncertainty, no generation certificate, and blocked retry. Add the post-finalization boolean-ID case; retain clean admission, replacement preservation, and other-key isolation.

### [P2-2] Completion validation accepts unreachable phase/failure combinations
**Location:** Pyrolyze `src/pyrolyze/runtime/context_state_lcm/render_attempt.py:217–254`; generation consumption in `field_only_render.py:269–279`.

**Violated invariant:** Missing or incoherent evidence must be rejected before publication classification, generation completion, or reuse certification. Recovery evidence must follow the accepted phase grammar, not merely contain well-typed flags.

**Reproduction:** Patch `TransactionManager.commit_only` in memory to call the real method first, then replace the original token’s immutable record using `dataclasses.replace`. Render `"published"` through the real private graph. Two independently tested replacements were:
- `publication_started=False`, `after_actions_complete=False`, `failures=(ValueError("retained record failure"),)`, leaving `publication_complete=True`.
- Only `failures=(ValueError("retained record failure"),)`, leaving full publication and after-action completion true.

Both are unreachable under the accepted algorithm. Full publication without an invoked application callback is the successful empty-commit case, which cannot have a failing eligible after action. Likewise, fully successful preparation/application/after completion cannot carry a manager completion failure while ownership remains preserved.

Observed: both records were accepted and **generation committed to 1**. The second also certified `reuse_ready=True`; a subsequent real pass entered and committed generation **2**, despite the outward retained error. Neither produced an incoherent-evidence diagnostic. These are consumer fault-injection results, not a claim that the accepted library emits these records.

**Impact:** Malformed evidence can authorize generation and, in one demonstrated case, graph reuse. Current corruption tests cover types and simultaneous publication/discard, but not these semantic contradictions.

**Required correction:** Enforce the reachable phase/failure combinations before installing `_completion`. Reject contradictions as incomplete authority, retain supplied exception objects, leave generation uncertified, and quarantine. Preserve legitimate empty commits, clean aborts, partial application, and incomplete cleanup.

**Closure test:** Extend the narrow evidence-corruption matrix with both combinations and exercise the real field-only consumer. Require `published=None`, uncertainty, retained failures, no tracker commit/rollback certificate, no second completion, and rejection of subsequent pass/publication-write entry.

## 2. Invariant analysis
The original counterexamples remained closed within the exercised scope:

| Prior closure | Independent evidence on this tuple |
| --- | --- |
| SC1 exceptional validation ownership loss | Retained commit/discard/replacement cases preserved original errors and actual values, quarantined loss, and preserved replacements. |
| SC1 recursive terminal/release failures | Recursive finish/abort/finish-during-abort regressions passed. Additional release faults before/after removal discarded unpublished values, retained cleanup errors, and blocked reuse. |
| SC1 external borrowing/stale completion | Retained external-borrower and replacement tests passed; stale exceptional-exit fencing was source-retraced. |
| SC2 execution, retirement, cache, and ghost-owner closures | Retained early-end/reentry, direct/ancestor/unseen retirement, candidate-sibling, constructor collision, nested cache, duplicate/uninstalled-root, and current-only debug cases passed under both backends. |

The canonical matrix independently distinguishes empty commit/rollback/abort, preparation/validation abort, incomplete discard/after cleanup, partial application, and publication followed by action failure. Generation follows accepted publication facts, not readiness or `first_failure`; partial outcomes leave generation pending and block retry. Commit exceptions do not cause guessed second rollback or fabricated field undo.

Late cache failure and generation failure after mutation retained published UI and generation **1**. Generation failure before mutation retained published UI with generation pending, without fabricated rollback. In all three probes, the original after-action error and injected cleanup error remained outwardly reachable, and later pass/publication-write entry was rejected. Late token relabeling during an after callback rejected authority, preserved published UI, and issued no generation certificate.

Historical/current traces remained separate. Explicit restaging was not treated as repaired cleanup. Independent keys remained covered by retained tests and canonical observations. No resource activation was inferred.

## 3. Risks and next action
This checkpoint is synchronous and in-memory: it adds no filesystem persistence or restart protocol. Process-kill durability, parallel rendering, and resource adapters are not certified. Full default/broader suites were not repeated; their recorded 13/14 failures remain unverified here and outside this bounded review.

**Next action:** Return P2-1 and P2-2 for one bounded consumer correction and focused re-review at a newly settled tuple. Keep resource admission and broader activation blocked.
